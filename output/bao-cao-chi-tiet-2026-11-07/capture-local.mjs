import {withTestDatabase} from '../../scripts/lib/test-database.mjs';
import {applySchema,importSeed} from '../../scripts/import-mysql.mjs';
import {loadSeed} from '../../scripts/mysql-seed-data.mjs';
import {randomBytes} from 'node:crypto';
import {writeFile,access} from 'node:fs/promises';
import {setTimeout as sleep} from 'node:timers/promises';
const out=new URL('./',import.meta.url);
await withTestDatabase(async(c,env)=>{
 Object.assign(process.env,env);process.env.NODE_ENV='development';
 await applySchema(c);await importSeed(c,await loadSeed());
 const [columns]=await c.query('SELECT TABLE_NAME,COLUMN_NAME,COLUMN_TYPE,IS_NULLABLE,COLUMN_DEFAULT,COLUMN_KEY,EXTRA FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() ORDER BY TABLE_NAME,ORDINAL_POSITION');
 const [foreignKeys]=await c.query('SELECT TABLE_NAME,COLUMN_NAME,REFERENCED_TABLE_NAME,REFERENCED_COLUMN_NAME,CONSTRAINT_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA=DATABASE() AND REFERENCED_TABLE_NAME IS NOT NULL ORDER BY TABLE_NAME,CONSTRAINT_NAME,ORDINAL_POSITION');
 await writeFile(new URL('schema-current.json',out),JSON.stringify({columns,foreignKeys},null,2));
 const {server}=await import('../../server/app.js');
 const {provisionAdmin}=await import('../../server/services/provision-admin.js');
 const {closeDatabase}=await import('../../server/config/database.js');
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const base='http://127.0.0.1:'+server.address().port;process.env.BETTER_AUTH_URL=base;
 const password=randomBytes(24).toString('base64url');const email='report-admin@example.invalid';await provisionAdmin({email,password});
 await writeFile(new URL('.env.capture-session',out),JSON.stringify({base,email,password}));console.log('Isolated report server ready: '+base);
 try{for(let n=0;n<1800;n++){try{await access(new URL('STOP',out));break;}catch{}await sleep(1000);}}
 finally{await new Promise(r=>server.close(r));await closeDatabase();}
});
