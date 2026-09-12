const fileInput = document.getElementById('fileInput');
const chooseBtn = document.getElementById('chooseBtn');
const dropzone = document.getElementById('dropzone');
const statusBox = document.getElementById('status');
const results = document.getElementById('results');
let currentFile = null;

chooseBtn.addEventListener('click', e => { e.stopPropagation(); fileInput.click(); });
dropzone.addEventListener('click', () => fileInput.click());
dropzone.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') fileInput.click(); });
fileInput.addEventListener('change', () => { if (fileInput.files[0]) analyze(fileInput.files[0]); });
['dragenter','dragover'].forEach(evt => dropzone.addEventListener(evt, e => { e.preventDefault(); dropzone.classList.add('drag'); }));
['dragleave','drop'].forEach(evt => dropzone.addEventListener(evt, e => { e.preventDefault(); dropzone.classList.remove('drag'); }));
dropzone.addEventListener('drop', e => { const f=e.dataTransfer.files[0]; if(f) analyze(f); });
document.getElementById('againBtn').addEventListener('click', () => { results.classList.add('hidden'); fileInput.value=''; currentFile=null; window.scrollTo({top:0,behavior:'smooth'}); });
document.getElementById('csvBtn').addEventListener('click', () => downloadReport('csv'));
document.getElementById('jsonBtn').addEventListener('click', () => downloadReport('json'));

function esc(v){return String(v??'').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));}

async function analyze(file){
  currentFile=file;
  statusBox.classList.remove('hidden'); statusBox.textContent='파일을 분석하고 있습니다…';
  results.classList.add('hidden');
  const fd=new FormData(); fd.append('file',file);
  try{
    const res=await fetch('/api/analyze',{method:'POST',body:fd});
    const data=await res.json();
    if(!res.ok) throw new Error(data.detail || '분석 실패');
    render(data);
    statusBox.classList.add('hidden');
  }catch(err){ statusBox.textContent='오류: '+err.message; }
}

async function downloadReport(format){
  if(!currentFile) return;
  statusBox.classList.remove('hidden'); statusBox.textContent='전체 리포트를 만들고 있습니다…';
  const fd=new FormData(); fd.append('file',currentFile);
  try{
    const res=await fetch(`/api/report/${format}`,{method:'POST',body:fd});
    if(!res.ok){
      const data=await res.json().catch(()=>({}));
      throw new Error(data.detail || '리포트 생성 실패');
    }
    const blob=await res.blob();
    const cd=res.headers.get('content-disposition')||'';
    const m=cd.match(/filename="?([^";]+)"?/i);
    const fallback=`sheetproof_report.${format}`;
    const name=m ? m[1] : fallback;
    const url=URL.createObjectURL(blob);
    const a=document.createElement('a'); a.href=url; a.download=name; document.body.appendChild(a); a.click(); a.remove();
    URL.revokeObjectURL(url);
    statusBox.classList.add('hidden');
  }catch(err){ statusBox.textContent='오류: '+err.message; }
}

function render(d){
  document.getElementById('filename').textContent=d.filename;
  document.getElementById('sheets').textContent=(d.sheets??1).toLocaleString();
  document.getElementById('rows').textContent=d.rows.toLocaleString();
  document.getElementById('total').textContent=d.issues_total.toLocaleString();
  document.getElementById('high').textContent=d.high;
  document.getElementById('medium').textContent=d.medium;
  document.getElementById('low').textContent=d.low;
  const list=document.getElementById('issueList'); list.innerHTML='';
  if(d.preview.length===0){
    list.innerHTML='<div class="issue"><div class="check">검사 범위에서 뚜렷한 오류를 찾지 못했습니다.</div><div class="message">현재 6가지 규칙 기준 결과입니다. 실제 업무 규칙은 추가할 수 있습니다.</div></div>';
  } else {
    d.preview.forEach(i=>{
      const meta=[i.sheet?`시트 ${esc(i.sheet)}`:'', i.row?`행 ${i.row}`:'', i.column?`열 ${esc(i.column)}`:''].filter(Boolean).join(' · ');
      const el=document.createElement('div'); el.className='issue';
      el.innerHTML=`<div class="issue-top"><div class="check">${esc(i.check)}</div><div class="meta">${meta}</div></div><div class="message">${esc(i.message)}</div>${i.value?`<div class="meta">값: ${esc(i.value)}</div>`:''}${i.suggestion?`<div class="suggestion">수정 제안: ${esc(i.suggestion)}</div>`:''}`;
      list.appendChild(el);
    });
  }
  const reportBox=document.getElementById('reportBox');
  if(d.locked_count>0){document.getElementById('lockedCount').textContent=d.locked_count;reportBox.classList.remove('hidden');} else reportBox.classList.add('hidden');
  results.classList.remove('hidden'); results.scrollIntoView({behavior:'smooth'});
}
