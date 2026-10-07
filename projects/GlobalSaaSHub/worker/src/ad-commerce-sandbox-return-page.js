// Sandbox customer return. GET renders only; authenticated browser POST may verify an approved checkout.
const escape = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c]);
export function sandboxReturnScript(view) {
  const config = JSON.stringify({ id: view.orderId, nextAction: view.nextAction,
    browserOutcome: view.browserOutcome, reservationExpired: view.reservationExpired }).replace(/</g, '\\u003c');
  return `(() => {
    'use strict';
    const config=${config};
    const message=document.getElementById('return-status'), detail=document.getElementById('order-detail');
    const retry=document.getElementById('check-order'); let busy=false;
    function access(){try{return sessionStorage.getItem('coshuma-sandbox-order:'+config.id);}catch{return null;}}
    function verified(order){return ['active','ended'].includes(order?.state)&&order.payment_environment==='sandbox'&&
      !!order.capture_id&&Number.isFinite(Date.parse(order.payment_verified_at))&&
      Number.isFinite(Date.parse(order.starts_at))&&Number.isFinite(Date.parse(order.ends_at));}
    function display(order){
      detail.textContent='서버 주문: '+order.id+' · 상태: '+order.state+' · 광고 시작: '+(order.starts_at||'확인되지 않음')+
        ' · 광고 종료: '+(order.ends_at||'확인되지 않음');
      message.textContent=verified(order)?'Sandbox 결제를 서버에서 확인했습니다. 광고 상태: '+order.state+'.':
        config.browserOutcome==='cancelled'?'구매자 승인이 취소되어 결제를 요청하지 않았습니다. 현재 서버 상태: '+order.state+'.':
        config.reservationExpired&&order.state==='checkout'?'예약 기한이 만료되어 결제를 요청하지 않았습니다. 기존 주문을 확인하세요.':
        '결제 완료가 확인되지 않았습니다. 기존 주문을 유지하고 다시 결제하지 마세요.';
    }
    async function request(action,token){
      const response=await fetch('/sandbox/orders/'+encodeURIComponent(config.id)+(action?'/'+action:''),{
        method:action?'POST':'GET',headers:{...(action?{'Content-Type':'application/json'}:{}),'Authorization':'Bearer '+token},
        ...(action?{body:'{}'}:{}),credentials:'omit',cache:'no-store',redirect:'error'});
      const data=await response.json();
      if(!response.ok||!data.order||data.order.id!==config.id)throw new Error('not-confirmed');
      display(data.order); return data.order;
    }
    async function run(initial){
      if(busy)return;
      const token=access();
      if(!token||!/^[a-f0-9]{64}$/.test(token)){message.textContent='주문 접근키가 유실되었습니다. 주문 시작 화면에서 기존 접근키를 복구하세요. 이 화면은 결제를 요청할 수 없습니다.';return;}
      busy=true;retry.disabled=true;
      try{
        const order=await request('',token);
        if(verified(order)||config.browserOutcome==='cancelled'||!['checkout','capturing'].includes(order.state))return;
        const mark='coshuma-sandbox-capture:'+config.id+':'+order.provider_order;
        if(order.state==='capturing'||!initial||sessionStorage.getItem(mark)){
          await request('reconcile',token);return;
        }
        if(config.nextAction!=='confirm_with_authenticated_post'||config.reservationExpired)return;
        // Persist before a capture may be sent. Refreshes and lost responses only reconcile.
        sessionStorage.setItem(mark,'attempted');
        if(sessionStorage.getItem(mark)!=='attempted')throw new Error('storage-unavailable');
        await request('capture',token);
      }catch{message.textContent='결제 확인 결과가 불명확합니다. 기존 주문을 유지하고 상태를 재조회하세요. 다시 결제하지 마세요.';}
      finally{busy=false;retry.disabled=false;}
    }
    retry.addEventListener('click',()=>run(false));
    run(true);
  })();`;
}
export function renderSandboxReturn(view) {
  const nonce=crypto.randomUUID().replaceAll('-','');
  const text=view.paymentVerified?'저장된 Sandbox 결제가 확인되었습니다. 서버 주문 상태를 조회합니다.':
    view.browserOutcome==='cancelled'?'구매자 승인이 취소되었습니다. 결제를 요청하지 않고 기존 주문을 조회합니다.':
    view.reservationExpired?'예약 기한이 만료되었습니다. 기존 주문을 조회합니다.':'승인 복귀를 받았습니다. 서버에서 주문과 결제를 확인합니다.';
  const html='<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'+
    '<meta name="robots" content="noindex,nofollow"><title>COSHUMA sandbox order status</title>'+
    '<body><main><h1>COSHUMA Sandbox 주문 상태</h1><p>격리 시험 환경 · 실제 고객 결제가 아닙니다.</p>'+
    '<p id="return-status" role="status" aria-live="polite">'+escape(text)+'</p><pre id="order-detail"></pre>'+
    '<button type="button" id="check-order">새 결제 없이 기존 주문 상태 재조회</button>'+
    '<p><a href="/sandbox/purchase">주문 시작 화면으로 돌아가기</a></p></main>'+
    '<script nonce="'+nonce+'">'+sandboxReturnScript(view)+'</script></body></html>';
  return new Response(html,{headers:{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-store','Referrer-Policy':'no-referrer',
    'X-Content-Type-Options':'nosniff','X-Frame-Options':'DENY','X-Robots-Tag':'noindex,nofollow',
    'Content-Security-Policy':"default-src 'none'; script-src 'nonce-"+nonce+"'; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"}});
}
