// Restore a backup only into a runner-created disposable MySQL server, never
// into the user's local service or the cloud database.
import fs from 'node:fs/promises';
import mysql from 'mysql2/promise';
import {withTestDatabase} from './lib/test-database.mjs';
import {applySchema} from './import-mysql.mjs';
import {exportMysql} from './migrate-neon.mjs';
const input=process.argv[2],output=process.argv[3];
if(!input||!output?.startsWith('.env.'))throw new Error('Usage: node scripts/prepare-neon-backup.mjs backup.sql .env.snapshot.json');
await withTestDatabase(async(c,env)=>{
 if(env.DB_HOST!=='127.0.0.1'||Number(env.DB_PORT)===3306||!env.HNAG_ISOLATED_TEST_DIR)throw new Error('Refusing non-disposable restore target.');
 const sql=await fs.readFile(input,'utf8');
 if(/^\s*(?:USE\s|CREATE\s+DATABASE)/mi.test(sql))throw new Error('Backup selects another database; review before restoring.');
 const restore=await mysql.createConnection({host:env.DB_HOST,port:Number(env.DB_PORT),user:env.DB_USER,password:env.DB_PASSWORD,database:env.DB_NAME,multipleStatements:true,timezone:'Z'});
 try{await restore.query(sql);}finally{await restore.end();}
 await applySchema(c);
 Object.assign(process.env,env);process.env.DB_PROVIDER='mysql';
 const report=await exportMysql(output);console.log(JSON.stringify({restoredOnlyInDisposableServer:true,...report}));
});
