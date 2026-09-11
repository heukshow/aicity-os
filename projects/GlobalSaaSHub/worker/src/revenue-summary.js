import inventory from './revenue-inventory.json' with { type: 'json' };
import observations from './revenue-observations.json' with { type: 'json' };
import { fetchPartnerStackMetrics } from './partnerstack.js';

const valid = n => typeof n === 'number' && Number.isFinite(n) && n >= 0;
const moneyKeys = ['commission_earned','commission_pending','reward_paid','available','withdrawn','declined','payout_paid'];
export function summarizeRevenue(programs, liveAccounts, now = new Date().toISOString()) {
  const accounts = [...new Set(programs.map(p=>p.account_id))].map(id => {
    const members=programs.filter(p=>p.account_id===id), live=liveAccounts.find(a=>a.account_id===id);
    const evidence=members.flatMap(p=>p.evidence || []).sort((a,b)=>Date.parse(b.checked_at)-Date.parse(a.checked_at));
    return {account_id:id,name:id==='partnerstack-account'?'PartnerStack':members.map(p=>p.name).join(' / '),network:members[0].network,
      programs:members.map(p=>p.name),portal_url:members.find(p=>p.portal_url)?.portal_url || null,
      connection:'not_connected',complete:false,checked_at:null,currency:null,metrics:{},
      action:'기존 제휴 포털에서 수익 보고서 확인',...live,evidence:[...(live?.evidence||[]),...evidence]};
  });
  const totals={};
  for(const key of moneyKeys){
    const included=accounts.filter(a=>['connected','verified_snapshot'].includes(a.connection) && a.complete && a.period==='lifetime' && valid(a.metrics?.[key]) && /^[A-Z]{3}$/.test(a.currency) && Date.parse(a.checked_at)<=Date.parse(now) && Date.parse(now)-Date.parse(a.checked_at)<=86400000);
    const byCurrency={};
    for(const a of included) byCurrency[a.currency]=(byCurrency[a.currency]||0)+Math.round(a.metrics[key]*100);
    totals[key]={by_currency:Object.fromEntries(Object.entries(byCurrency).map(([k,v])=>[k,v/100])),account_ids:included.map(a=>a.account_id),checked_accounts:included.length,total_accounts:accounts.length,complete:included.length===accounts.length && accounts.length>0};
  }
  const rank=a=>a.connection==='connected'?0:a.connection==='verified_snapshot'?1:a.connection==='blocked'?2:a.evidence.length?3:4;
  accounts.sort((a,b)=>rank(a)-rank(b)||a.name.localeCompare(b.name));
  return {generated_at:now,scope:inventory.scope,program_count:programs.length,account_count:accounts.length,
    connected_accounts:accounts.filter(a=>a.connection==='connected').length,totals,accounts,
    snapshot_accounts:accounts.filter(a=>a.connection==='verified_snapshot').length,
    blocked_accounts:accounts.filter(a=>a.connection==='blocked').length,
    definitions:{commission_earned:'수익으로 기록된 커미션. 미지급 보상을 포함하며 매출/출금액과 더하지 않습니다.',reward_paid:'네트워크가 보상에 표시한 paid 상태. 은행 입금과 별개입니다.',withdrawn:'네트워크의 출금 처리 상태. 은행 입금 대조 결과가 아닙니다.',payout_paid:'지급 보고서가 명시한 지급액. 보상 paid에서 추정하지 않습니다.',totals:'24시간 내 확인한 누적·전체 조회 계정만 통화별 소계에 포함. 기간 보고서·과거 기록은 근거 표에 별도 표시.'}};
}

export async function getRevenueSummary(env) {
  const now=new Date().toISOString();
  let partner;
  try { partner=await fetchPartnerStackMetrics(env); } catch { partner={connected:false,reason:'PartnerStack API 조회 실패'}; }
  const safe=partner.connected && partner.coverage?.rewardsComplete===true && partner.invalidAmountCount===0 && !partner.mixedCurrency && !(partner.rewardStatusCounts?.other>0);
  const ps={account_id:'partnerstack-account',connection:partner.connected?'connected':'error',complete:Boolean(safe),checked_at:partner.checkedAt||now,
    source:'PartnerStack API',period:'lifetime',currency:partner.currency||null,coverage:partner.coverage||null,reward_count:partner.rewardCount??null,
    action:partner.connected?(safe?'페이지를 새로고침하면 자동 조회':'통화·조회 범위·보상 상태 점검'):partner.reason||'기존 API 연결 확인',
    metrics:Object.fromEntries(moneyKeys.map(k=>[k,null]))};
  if(safe) Object.assign(ps.metrics,{commission_earned:partner.total,commission_pending:partner.pending,reward_paid:partner.paid,available:partner.available,withdrawn:partner.withdrawn,declined:partner.declined});
  ps.evidence=observations.accounts.find(a=>a.account_id==='partnerstack-account')?.evidence || [];
  // No payouts means zero payouts only when that independent endpoint was fully read.
  if(partner.coverage?.payouts?.connected && partner.coverage.payouts.complete && partner.coverage.payouts.count===0) ps.metrics.payout_paid=0;
  const summary=summarizeRevenue(inventory.programs,[ps,...observations.accounts.filter(a=>a.account_id!=='partnerstack-account')],now);
  summary.partnerstack_currency_breakdown=partner.amountsByCurrency || {};
  summary.direct_sales={connection:'error',checked_at:now,currency_totals:[],note:'COSHUMA 결제 장부 기준 · 제휴 커미션과 별도 · 결제사 잔액/은행 입금 아님'};
  try {
    const r=await env.ORDERS.prepare("SELECT currency, COUNT(*) AS orders, SUM(CASE WHEN status = 'paid' THEN 1 ELSE 0 END) AS paid_orders, SUM(CASE WHEN status = 'paid' THEN CAST(amount AS REAL) ELSE 0 END) AS paid_amount, SUM(CASE WHEN status = 'refunded' THEN CAST(amount AS REAL) ELSE 0 END) AS refunded_amount FROM orders GROUP BY currency").all();
    if(r.success===false || !Array.isArray(r.results)) throw new Error('unavailable');
    summary.direct_sales.connection='connected';summary.direct_sales.currency_totals=r.results.map(x=>({currency:x.currency,orders:x.orders,paid_orders:x.paid_orders,paid_amount:x.paid_amount,refunded_amount:x.refunded_amount}));
    summary.direct_sales.empty=r.results.length===0;
  } catch { summary.direct_sales.error='기존 결제 장부 조회 실패'; }
  return summary;
}
