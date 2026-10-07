import { AD_ASSET_SPECS } from './ad-asset-specs.js';
export const CATALOG_VERSION = '2026-10-07.1';
// USD totals for the owner-authorized image advertising service. No automatic renewal.
const rows = [
 ['tool-primary','F1','Pipedrive introduction','/tool/pipedrive.html',1,[19,49,129]],
 ['buyer-intent-top','F2','Claap guide introduction','/best/claap-sales-follow-up-ai.html',1,[39,99,269]],
 ['compare-decision-premium','F3','Semrush / Frase, before sources','/compare/semrush-vs-frase.html',1,[59,149,399]],
 ['buyer-hub-fixed','F4','Buyer-guide directory','/best/index.html',1,[24,59,159]],
 ['comparison-hub-fixed','F5','Comparison directory','/compare/',1,[24,59,159]],
 ['tool-rotation','R1','Pipedrive shared rotation','/tool/pipedrive.html',3,[16,39,105]],
 ['guide-rotation','R2','Claap shared rotation','/best/claap-sales-follow-up-ai.html',3,[16,39,105]],
 ['compare-rotation','R3','Semrush / Frase shared rotation','/compare/semrush-vs-frase.html',3,[16,39,105]]
];
export const IMAGE_SLOTS = Object.freeze(rows.map(([id,code,name,path,capacity,prices]) => ({id,code,name,path,capacity,mode:capacity===1?'fixed':'rotating',...AD_ASSET_SPECS[id],prices:Object.fromEntries([7,30,90].map((days,i)=>[days,prices[i]]))})));
export const IMAGE_BUNDLES = Object.freeze([
 {id:'P1',name:'Discovery Mix',price:79,slots:['buyer-hub-fixed'],choices:['tool-rotation','guide-rotation','compare-rotation']},
 {id:'P2',name:'Sales & CRM Duo',price:129,slots:['tool-primary','buyer-intent-top'],choices:[]},
 {id:'P3',name:'SEO & Content Duo',price:179,slots:['compare-decision-premium','comparison-hub-fixed'],choices:[]}
]);
