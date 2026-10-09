// Test-only persistent SQLite adapter; caller supplies a new isolated temporary database.
import { DatabaseSync } from 'node:sqlite';
import { readFileSync } from 'node:fs';
import { AdStore } from '../../src/ad-commerce-store.js';
export function openTestStore(path,{initialize=false,clock=()=>new Date()}={}) {
  if(typeof path!=='string'||!path.endsWith('.ad-sandbox.sqlite')) throw new Error('An explicit sandbox fixture path is required');
  const native=new DatabaseSync(path); native.exec('PRAGMA foreign_keys=ON; PRAGMA busy_timeout=5000;');
  const tables=native.prepare("SELECT count(*) n FROM sqlite_master WHERE type='table'").get().n;
  if(initialize&&tables!==0){native.close();throw new Error('Refusing to initialize a nonempty database');}
  if(initialize) {
    native.exec('BEGIN IMMEDIATE');
    try {
      for(const file of ['0004_sponsorship_sales.sql','0005_image_ad_fulfilment.sql']) native.exec(readFileSync(new URL('../../migrations/'+file,import.meta.url),'utf8'));
      native.exec('PRAGMA application_id=1129272147; COMMIT;');
    }catch(error){native.exec('ROLLBACK');native.close();throw error;}
  }
  if(native.prepare('PRAGMA application_id').get().application_id!==1129272147){native.close();throw new Error('Not an advertising sandbox fixture database');}
  const prepare=sql=>({bind(...values){const s=native.prepare(sql);return {
    async first(){return s.get(...values)??null;}, async all(){return {results:s.all(...values)};},
    run(){return {success:true,meta:{changes:Number(s.run(...values).changes)}};}
  };}});
  const db={prepare,async batch(statements){native.exec('BEGIN IMMEDIATE');try{const results=statements.map(s=>s.run());native.exec('COMMIT');return results;}catch(error){native.exec('ROLLBACK');throw error;}}};
  return {native,db,store:new AdStore(db,{environment:'sandbox',clock}),close(){native.close();}};
}
