import test from 'node:test';
import assert from 'node:assert/strict';
import {postgresQuery,postgresConfig} from '../server/config/postgres.js';

test('PostgreSQL parameters preserve literals, identifiers and comments',()=>{
 const sql="SELECT '?' AS literal, \"?\" FROM dishes WHERE id=? AND name=? -- ?\n/* ? */";
 const result=postgresQuery(sql,['pho-bo','Phở bò']);
 assert.equal(result.text,"SELECT '?' AS literal, \"?\" FROM dishes WHERE id=$1 AND name=$2 -- ?\n/* ? */");
 assert.deepEqual(result.values,['pho-bo','Phở bò']);
 assert.throws(()=>postgresQuery('SELECT ?',[1,2]),/count mismatch/);
 assert.equal(postgresQuery("SELECT 'it''s ?' WHERE id=?",[1]).text,"SELECT 'it''s ?' WHERE id=$1");
});
test('PostgreSQL translations cover the app-specific MySQL operations',()=>{
 assert.equal(postgresQuery('INSERT IGNORE INTO admin_catalog_versions(kind,entity_key) VALUES (?,?)',['recipes','x']).text,'INSERT INTO admin_catalog_versions(kind,entity_key) VALUES ($1,$2) ON CONFLICT (kind,entity_key) DO NOTHING');
 assert.match(postgresQuery("INSERT INTO admin_catalog_versions(kind,entity_key,revision) VALUES ('reviews',?,2) ON DUPLICATE KEY UPDATE revision=revision+1,last_request_id=NULL",['x']).text,/ON CONFLICT \(kind,entity_key\) DO UPDATE SET revision=admin_catalog_versions.revision\+1/);
 assert.equal(postgresQuery("SELECT before_data WHERE JSON_CONTAINS_PATH(before_data,'one','$.source_record')").text,"SELECT before_data WHERE (before_data -> 'source_record') IS NOT NULL");
 assert.equal(postgresQuery('UPDATE dishes SET updated_at=UTC_TIMESTAMP(3)').text,'UPDATE dishes SET updated_at=CURRENT_TIMESTAMP(3)');
});
test('Remote PostgreSQL uses verified TLS and finite connection/query timeouts',()=>{
 const config=postgresConfig({DATABASE_URL:'postgresql://user:private@example.neon.tech/neondb?sslmode=require&channel_binding=require'});
 assert.deepEqual(config.ssl,{rejectUnauthorized:true});
 assert.equal(new URL(config.connectionString).searchParams.has('sslmode'),false);
 assert.equal(config.max,2);assert.ok(config.connectionTimeoutMillis>0);assert.ok(config.query_timeout>0);
 assert.throws(()=>postgresConfig({DATABASE_URL:'postgresql://user:private@example.neon.tech/neondb'}),/TLS/);
 assert.throws(()=>postgresConfig({DATABASE_URL:'mysql://user:private@localhost/db'}));
 assert.equal(postgresConfig({DATABASE_URL:'postgresql://user@127.0.0.1/db'}).ssl,false);
});
