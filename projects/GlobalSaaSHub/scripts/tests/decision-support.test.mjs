import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const source = fs.readFileSync(new URL('../../public/presentation-test-brief.js', import.meta.url), 'utf8');
function fixture({clipboardFails = false, analyticsFails = false} = {}) {
  const calls = [], observers = [];
  const element = (extra = {}) => ({listeners:{}, addEventListener(n,f){this.listeners[n]=f;}, ...extra});
  const nodes = {
    'presentation-scenario': element({value:'pitch'}),
    'presentation-brief': element({value:'PRIVATE NOTE NEVER SEND', focus(){}, select(){}}),
    'copy-presentation-brief': element({hidden:true}),
    'presentation-copy-status': element({textContent:''}),
    'test-heading': element(),
  };
  const link = {dataset:{ctaSource:'gamma_vs_canva_hero'}};
  class Observer {
    constructor(callback){this.callback=callback;this.targets=new Set();observers.push(this);}
    observe(node){this.targets.add(node);}
    unobserve(node){this.targets.delete(node);}
    disconnect(){this.targets.clear();}
    show(node, ratio){if(this.targets.has(node))this.callback([{target:node,isIntersecting:ratio>0,intersectionRatio:ratio}]);}
  }
  vm.runInNewContext(source, {
    window:{location:{href:'https://coshuma.com/compare/gamma-vs-canva.html',pathname:'/compare/gamma-vs-canva.html'},gtag(...args){if(analyticsFails)throw Error('blocked');calls.push(args);}},
    document:{getElementById:id=>nodes[id],querySelectorAll:()=>[link]},
    navigator:{clipboard:{async writeText(){if(clipboardFails)throw Error('denied');}}},
    IntersectionObserver:Observer,
  });
  return {nodes,link,observers,calls};
}
test('visible CTA and tool heading are counted once, not before exposure',()=>{
  const f=fixture(); const [cta,tool]=f.observers;
  cta.show(f.link,0.3); assert.equal(f.calls.length,0);
  cta.show(f.link,0.6); cta.show(f.link,0.9);
  tool.show(f.nodes['test-heading'],0.7); tool.show(f.nodes['test-heading'],1);
  assert.deepEqual(f.calls.map(x=>x[1]),['affiliate_cta_view','decision_tool_view']);
});
test('copy success is measured without sending brief or notes',async()=>{
  const f=fixture(); await f.nodes['copy-presentation-brief'].listeners.click();
  assert.equal(f.calls[0][1],'decision_brief_copy');
  assert.ok(!JSON.stringify(f.calls).includes('PRIVATE NOTE'));
  assert.match(f.nodes['presentation-copy-status'].textContent,/Copied/);
});
test('clipboard failure stays usable and does not claim a copy',async()=>{
  const f=fixture({clipboardFails:true}); await f.nodes['copy-presentation-brief'].listeners.click();
  assert.equal(f.calls.length,0); assert.match(f.nodes['presentation-copy-status'].textContent,/selected/);
});
test('analytics failure cannot block scenario selection or copying',async()=>{
  const f=fixture({analyticsFails:true}); f.nodes['presentation-scenario'].value='report';
  f.nodes['presentation-scenario'].listeners.change();
  assert.match(f.nodes['presentation-brief'].value,/monthly business update/);
  await f.nodes['copy-presentation-brief'].listeners.click();
  assert.match(f.nodes['presentation-copy-status'].textContent,/Copied/);
});
