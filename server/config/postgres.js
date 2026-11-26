import pg from 'pg';
import {attachDatabasePool} from '@vercel/functions';

// Application queries use positional ? parameters; PostgreSQL uses $1, $2...
// Only replace placeholders outside quoted literals/identifiers and comments.
export function postgresQuery(input,params=[]) {
 let sql=input.replace(/UTC_TIMESTAMP\(3\)/g,'CURRENT_TIMESTAMP(3)')
  .replace(/JSON_CONTAINS_PATH\(before_data,'one','\$\.source_record'\)/g,"(before_data -> 'source_record') IS NOT NULL");
 if(/^INSERT IGNORE INTO admin_catalog_versions\b/.test(sql))sql=sql.replace('INSERT IGNORE','INSERT')+' ON CONFLICT (kind,entity_key) DO NOTHING';
 sql=sql.replace(/ON DUPLICATE KEY UPDATE revision=revision\+1,last_request_id=NULL$/, 'ON CONFLICT (kind,entity_key) DO UPDATE SET revision=admin_catalog_versions.revision+1,last_request_id=NULL');
 let output='',index=0,quote=null,line=false,block=false;
 for(let i=0;i<sql.length;i++){
  const ch=sql[i],next=sql[i+1];
  if(line){output+=ch;if(ch==='\n')line=false;continue;}
  if(block){output+=ch;if(ch==='*'&&next==='/'){output+=next;i++;block=false;}continue;}
  if(quote){output+=ch;if(ch===quote){if(next===quote){output+=next;i++;}else quote=null;}continue;}
  if(ch==='-'&&next==='-'){output+='--';i++;line=true;continue;}
  if(ch==='/'&&next==='*'){output+='/*';i++;block=true;continue;}
  if(ch==="'"||ch==='"'){quote=ch;output+=ch;continue;}
  if(ch==='?'){output+='$'+(++index);continue;}
  output+=ch;
 }
 if(index!==params.length)throw new Error('SQL parameter count mismatch.');
 return {text:output,values:params};
}
export function postgresConfig(env=process.env){
 const url=new URL(env.DATABASE_URL||'');
 if(!['postgres:','postgresql:'].includes(url.protocol)||!url.username||!url.hostname)throw new Error('Set a private PostgreSQL DATABASE_URL.');
 const local=['127.0.0.1','localhost','[::1]'].includes(url.hostname);
 if(!local&&!['require','verify-full','verify-ca'].includes(url.searchParams.get('sslmode')))throw new Error('Remote PostgreSQL requires TLS.');
 // Explicit TLS certificate verification. Do not let sslmode=require downgrade it.
 for(const key of ['sslmode','channel_binding','sslcert','sslkey','sslrootcert'])url.searchParams.delete(key);
 const schema=env.PG_SCHEMA;
 if(schema&&!/^[a-z][a-z0-9_]{0,62}$/.test(schema))throw new Error('Invalid PostgreSQL schema.');
 return {connectionString:url.href,ssl:local?false:{rejectUnauthorized:true},...(schema?{options:'-c search_path='+schema}:{}),max:2,min:0,idleTimeoutMillis:1000,connectionTimeoutMillis:15000,statement_timeout:30000,query_timeout:35000,application_name:'hom-nay-an-gi',types:{getTypeParser(oid,format){
  if(oid===20)return value=>{const n=Number(value);return Number.isSafeInteger(n)?n:value;};
  return pg.types.getTypeParser(oid,format);
 }}};
}
function applicationClient(client,release){
 return {
  async execute(sql,params=[]){const r=await client.query(postgresQuery(sql,params));return [r.rows,r.fields];},
  async query(sql,params=[]){return this.execute(sql,params);},
  beginTransaction:()=>client.query('BEGIN'),commit:()=>client.query('COMMIT'),rollback:()=>client.query('ROLLBACK'),release,
 };
}
export function createPostgresPool(env=process.env){
 const native=new pg.Pool(postgresConfig(env));
 native.on('error',()=>console.error('Idle PostgreSQL connection failed.'));
 if(env.VERCEL==='1')attachDatabasePool(native);
 return {...applicationClient(native,undefined),native,
  async getConnection(){const c=await native.connect();return applicationClient(c,()=>c.release());},
  end:()=>native.end(),
 };
}
