// Sandbox customer-return page; signed redirects never authorize money by themselves.
const escape = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c]);
export function sandboxReturnScript(view) {
  const config = JSON.stringify({ id: view.orderId, nextAction: view.nextAction }).replace(/</g, '\\u003c');
  return `(() => {
    'use strict';
    const config=${config};
    const message=document.getElementById('return-status');
    const retry=document.getElementById('check-order');
    let busy=false;
    function access(){try{return sessionStorage.getItem('coshuma-sandbox-order:'+config.id);}catch{return null;}}
    async function run(action){
      if(busy)return;const token=access();
      if(!token||!/^[a-f0-9]{64}$/.test(token)){message.textContent='Return to your saved order to check its status. This page cannot charge without your order access.';return;}
      busy=true;retry.disabled=true;
      try{
        const response=await fetch('/sandbox/orders/'+encodeURIComponent(config.id)+'/'+action,{
          method:'POST',headers:{'Content-Type':'application/json','Authorization':'Bearer '+token},body:'{}',
          credentials:'omit',cache:'no-store',redirect:'error'});
        const data=await response.json();
        if(!response.ok)throw new Error('not-confirmed');
        message.textContent=['active','ended'].includes(data.order?.state)
          ? 'Sandbox payment verified. Advertising status: '+data.order.state+'.'
          : 'Payment is not yet confirmed. Do not create another order or pay again.';
      }catch{message.textContent='Payment confirmation is incomplete. Keep this order and check its status; do not pay again.';}
      finally{busy=false;retry.disabled=false;}
    }
    retry.addEventListener('click',()=>run('reconcile'));
    if(config.nextAction==='confirm_with_authenticated_post')run('capture');
  })();`;
}
export function renderSandboxReturn(view) {
  const nonce=crypto.randomUUID().replaceAll('-','');
  const text=view.paymentVerified
    ? 'The stored sandbox payment is verified. This redirect did not create a payment.'
    : view.browserOutcome==='cancelled'
      ? 'PayPal approval was cancelled. This return page will not charge or release your reservation.'
      : view.reservationExpired
        ? 'The checkout reservation expired. Check your existing order before trying again.'
        : 'Checking the approved sandbox payment against your saved order.';
  const html='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'+
    '<meta name="robots" content="noindex,nofollow"><title>COSHUMA sandbox order status</title>'+
    '<body><main><h1>COSHUMA sandbox order status</h1><p id="return-status" role="status" aria-live="polite">'+escape(text)+'</p>'+
    '<button type="button" id="check-order">Check this order without charging again</button><p>This is a test environment, not a receipt for a live payment.</p></main>'+
    '<script nonce="'+nonce+'">'+sandboxReturnScript(view)+'</script></body></html>';
  return new Response(html,{headers:{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-store','Referrer-Policy':'no-referrer',
    'X-Content-Type-Options':'nosniff','X-Frame-Options':'DENY','X-Robots-Tag':'noindex,nofollow',
    'Content-Security-Policy':"default-src 'none'; script-src 'nonce-"+nonce+"'; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"}});
}
