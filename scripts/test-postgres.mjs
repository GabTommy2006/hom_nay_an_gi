import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {randomUUID} from 'node:crypto';
import pg from 'pg';
import {postgresConfig} from '../server/config/postgres.js';
import {importPostgres} from './migrate-neon.mjs';

// Explicitly opt in: private snapshot and Neon URI stay outside version control.
const snapshotFile=process.argv[2];
if(!snapshotFile?.startsWith('.env.'))throw new Error('Pass a private .env.* MySQL snapshot.');
const url=(await fs.readFile('.env.neon-uri','utf8')).trim().replace('-pooler.','.');
const schema='hnag_test_'+randomUUID().replaceAll('-','');
const control=new pg.Client(postgresConfig({DATABASE_URL:url}));await control.connect();
let server,closeDatabase,resetAuth;
try{
 await control.query('CREATE SCHEMA '+schema);
 await importPostgres(JSON.parse(await fs.readFile(snapshotFile,'utf8')),url,{schema});
 process.env.DB_PROVIDER='postgres';process.env.DATABASE_URL=url;process.env.PG_SCHEMA=schema;process.env.NODE_ENV='test';
 ({server}=await import('../server/app.js'));
 ({closeDatabase}=await import('../server/config/database.js'));
 ({resetAuth}=await import('../server/config/auth.js'));
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const base='http://127.0.0.1:'+server.address().port;process.env.BETTER_AUTH_URL=base;resetAuth();
 const call=(path,{body,cookie,method=body?'POST':'GET'}={})=>fetch(base+path,{method,redirect:'manual',headers:{...(body?{'content-type':'application/json',origin:base}:{}),...(cookie?{cookie}:{})},...(body?{body:JSON.stringify(body)}:{})});
 for(const path of ['/api/dishes','/api/restaurants','/js/data.js','/js/recipes.js'])assert.equal((await call(path)).status,200,path);
 assert.equal((await call('/api/admin/me')).status,401);
 const {provisionAdmin}=await import('../server/services/provision-admin.js');
 const email='postgres-test@example.com',password=randomUUID()+'Aa1!';await provisionAdmin({email,password});
 const login=await call('/api/auth/sign-in/email',{body:{email,password}});assert.equal(login.status,200);
 const cookie=login.headers.getSetCookie().map(value=>value.split(';')[0]).join('; ');
 assert.equal((await call('/api/admin/me',{cookie})).status,200);
 for(const kind of ['dishes','restaurants','links','recipes','reviews','users'])assert.equal((await call('/api/admin/'+kind,{cookie})).status,200,kind);
 const write=async(kind,values,record)=>{
  const result=await call('/api/admin/'+kind+(record?'/'+encodeURIComponent(record.id):''),{cookie,method:record?'PUT':'POST',body:{...values,requestId:randomUUID(),...(record?{revision:record.revision}:{})}});
  assert.ok([200,201].includes(result.status),kind+': '+await result.clone().text());return (await result.json()).record;
 };
 let dish=await write('dishes',{name:'Món kiểm thử',cuisine:'viet',desc:'Dữ liệu thử',imageUrl:'',meals:['sang'],isVisible:true});
 dish=await write('dishes',{name:'Món đã sửa',cuisine:'viet',desc:'Dữ liệu thử',imageUrl:'',meals:['toi'],isVisible:false},dish);
 assert.equal((await call('/api/dishes/'+dish.id)).status,404);
 const link={dishId:'pho-bo',restaurantId:'dn-001',type:'related',offering:'Món cùng nhóm',price:null,sourceUrl:'https://example.com/menu',note:'Kiểm thử riêng',enabled:true};
 let linked=await write('links',link);linked=await write('links',{...link,enabled:false},linked);await write('links',link,linked);
 const recipe={dishId:'banh-mi',servings:2,prep:'10 phút',cook:'5 phút',soak:'',tip:'Thử riêng',source:{label:'Nguồn kiểm thử',url:'https://example.com/recipe'},ingredients:[{name:'Bánh mì',amount:2,unit:'ổ'},{name:'Muối',text:'Một ít'}],steps:[['Chuẩn bị','Sơ chế'],['Hoàn thành','Trình bày']],enabled:true};
 const recipes=(await (await call('/api/admin/recipes',{cookie})).json()).items;
 let recipeRecord=await write('recipes',recipe,recipes.find(r=>r.id==='banh-mi'));
 const reviews=(await (await call('/api/admin/reviews',{cookie})).json()).items;
 const evidence={dishId:'banh-mi',confirmed:true,vegetarianReview:{status:'reviewed',scope:'Phiên bản thử không thịt cá',ingredients:['bánh mì','rau'],source:'https://example.com/ingredients',reviewedAt:'2026-11-26'},nutritionProfile:null,nutritionKeys:[]};
 await write('reviews',evidence,reviews.find(r=>r.id==='banh-mi'));
 recipeRecord=await write('recipes',{...recipe,tip:'Thay đổi công thức để thu hồi căn cứ'},recipeRecord);
 assert.equal((await (await call('/api/dishes/banh-mi')).json()).vegetarianReview,undefined);
 recipeRecord=await write('recipes',{...recipe,enabled:false},recipeRecord);await write('recipes',recipe,recipeRecord);
 const values={name:'Quán kiểm thử PostgreSQL',address:'Địa chỉ kiểm thử',area:'Khu vực thử nghiệm',category:'Món chính',priceLabel:'',priceTier:'',website:'',phone:'',hours:'',imageUrl:'',grabFoodUrl:'',shopeeFoodUrl:'',partnership:'',note:'',meals:['sang'],isVisible:false,requestId:randomUUID()};
 let response=await call('/api/admin/restaurants',{cookie,body:values});assert.equal(response.status,201,await response.clone().text());
 const {record}=await response.json();
 assert.equal((await call('/api/restaurants/'+record.id)).status,404);
 const update={...values,name:'Quán đã sửa',isVisible:true,meals:['toi'],revision:record.revision};
 response=await call('/api/admin/restaurants/'+record.id,{cookie,method:'PUT',body:update});assert.equal(response.status,200,await response.clone().text());
 assert.equal((await call('/api/restaurants/'+record.id)).status,200);
 assert.equal((await call('/api/admin/restaurants/'+record.id,{cookie,method:'PUT',body:update})).status,409);
 assert.equal((await call('/api/auth/sign-out',{cookie,body:{}})).status,200);
 assert.equal((await call('/api/admin/me',{cookie})).status,401);
 console.log('PostgreSQL integration passed: public APIs, authentication, authorization, dish/restaurant writes, links, recipes, evidence withdrawal, visibility, revision conflict and logout.');
}finally{
 if(server?.listening)await new Promise(resolve=>server.close(resolve));
 await closeDatabase?.();resetAuth?.();
 // Only the unique schema created by this run is removed; public is untouched.
 await control.query('DROP SCHEMA '+schema+' CASCADE');await control.end();
}
