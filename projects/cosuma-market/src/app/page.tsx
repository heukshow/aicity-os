import SheetProofUploader from "./SheetProofUploader";

const features = [
  ["누락값 검사", "필수값으로 보이는 컬럼에서 비어 있는 셀을 찾아 검토 대상으로 표시합니다."],
  ["중복값 검사", "주문번호·품목코드처럼 식별자로 추정되는 컬럼의 중복을 찾아냅니다."],
  ["형식 불일치", "같은 컬럼 안에서 숫자·문자·날짜 형식이 어긋난 값을 찾아냅니다."],
  ["계산 불일치", "수량·단가·금액 관계를 추정해 계산이 맞지 않는 행을 확인합니다."],
  ["멀티시트 분석", "여러 시트를 한 번에 검사하고 시트·행·열 위치를 함께 보여줍니다."],
  ["리포트 확장", "현재 엔진은 CSV·JSON 전체 리포트를 생성할 수 있도록 준비되어 있습니다."],
];

export default function Home() {
  return (
    <div className="container mx-auto px-5 md:px-6 max-w-6xl">
      <section className="relative py-20 md:py-28 text-center">
        <div className="absolute inset-x-0 top-10 -z-10 mx-auto h-64 max-w-3xl rounded-full bg-brand/10 blur-3xl" />
        <div className="inline-flex items-center gap-2 px-4 py-2 mb-7 rounded-full bg-brand/10 border border-brand/20 text-brand text-xs font-bold tracking-[.18em] uppercase">
          <span className="h-1.5 w-1.5 rounded-full bg-brand" /> Spreadsheet quality check
        </div>
        <h1 className="text-5xl md:text-7xl font-black mb-7 leading-[1.02] tracking-tight">
          중요한 스프레드시트,<br /><span className="gradient-text">업로드 전에 한 번 더 증명하세요.</span>
        </h1>
        <p className="text-base md:text-xl text-gray-400 max-w-2xl mx-auto font-light leading-relaxed mb-10">
          SheetProof는 XLSX · XLSM · CSV에서 누락, 중복, 형식과 계산의 이상 징후를 찾아 검토할 위치까지 정리합니다.
        </p>
        <div className="flex flex-col sm:flex-row justify-center gap-3 mb-10">
          <a href="#analyze" className="inline-flex items-center justify-center px-7 py-4 rounded-2xl bg-brand text-black font-black hover:brightness-110 transition">무료로 파일 검사하기 <span className="ml-2">↓</span></a>
          <a href="#features" className="inline-flex items-center justify-center px-7 py-4 rounded-2xl border border-white/15 text-white font-bold hover:bg-white/5 transition">무엇을 검사하나요?</a>
        </div>
        <div className="flex flex-wrap justify-center gap-2 text-xs text-gray-500">
          {["XLSX · XLSM · CSV", "최대 10MB", "시트·행·열 위치", "서버 영구 저장 없음"].map((item) => <span key={item} className="rounded-full border border-white/10 bg-white/[.03] px-3 py-1.5">{item}</span>)}
        </div>
      </section>

      <SheetProofUploader />

      <section id="features" className="py-24">
        <div className="text-center mb-14">
          <p className="text-xs font-bold tracking-[0.25em] text-brand uppercase mb-3">What it checks</p>
          <h2 className="text-4xl font-black">지금 SheetProof가 확인하는 것</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {features.map(([title, description]) => (
            <div key={title} className="glass rounded-3xl p-7 border border-white/10">
              <h3 className="text-xl font-black mb-3">{title}</h3>
              <p className="text-sm text-gray-400 leading-relaxed">{description}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="how" className="py-10 pb-24">
        <div className="glass rounded-[36px] p-8 md:p-12 border border-white/10">
          <h2 className="text-3xl md:text-4xl font-black mb-8 text-center">사용 방법은 세 단계입니다</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              ["01", "파일 업로드", "검사할 XLSX, XLSM 또는 CSV 파일을 선택합니다."],
              ["02", "자동 분석", "SheetProof가 여러 검사 규칙을 적용해 문제 후보를 찾습니다."],
              ["03", "위치 확인", "시트·행·열 위치를 보고 원본 파일에서 바로 확인합니다."],
            ].map(([number, title, description]) => (
              <div key={number} className="rounded-3xl bg-black/15 p-6 border border-white/5">
                <div className="text-brand font-black text-sm mb-4">{number}</div>
                <h3 className="font-black text-xl mb-2">{title}</h3>
                <p className="text-sm text-gray-400 leading-relaxed">{description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="limits" className="py-10 pb-24">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="glass rounded-3xl p-8 border border-white/10">
            <h2 className="text-2xl font-black mb-4">파일 처리 안내</h2>
            <div className="space-y-3 text-sm text-gray-400 leading-relaxed">
              <p>업로드 파일은 분석을 위해 서버에서 처리됩니다.</p>
              <p>현재 SheetProof 애플리케이션은 업로드 파일을 별도의 사용자 저장소나 데이터베이스에 영구 보관하도록 설계되어 있지 않습니다.</p>
              <p>비밀번호, 주민등록번호, 금융·의료정보 등 민감한 개인정보가 포함된 파일은 업로드하지 않는 것을 권장합니다.</p>
            </div>
          </div>
          <div className="glass rounded-3xl p-8 border border-white/10">
            <h2 className="text-2xl font-black mb-4">분석 결과의 한계</h2>
            <div className="space-y-3 text-sm text-gray-400 leading-relaxed">
              <p>SheetProof는 자동 규칙과 휴리스틱으로 잠재적인 데이터 문제를 찾는 검토 보조 도구입니다.</p>
              <p>제목행, 복잡한 헤더, 세금·할인·배송비가 포함된 계산식, 회사별 업무 규칙 등에서는 오탐이나 미탐이 발생할 수 있습니다.</p>
              <p>문제가 발견되지 않았다는 결과가 파일에 오류가 전혀 없다는 의미는 아닙니다.</p>
            </div>
          </div>
        </div>
      </section>

      <section id="pricing" className="pb-24">
        <div className="glass rounded-[36px] p-8 md:p-12 border border-white/10 text-center">
          <p className="text-xs font-bold tracking-[0.25em] text-brand uppercase mb-3">Pricing direction</p>
          <h2 className="text-3xl md:text-4xl font-black mb-4">기본 검사는 무료로 시작합니다</h2>
          <p className="text-gray-400 max-w-2xl mx-auto leading-relaxed">
            현재 공개 단계에서는 사용성과 검사 정확도를 먼저 검증합니다. 이후 전체 상세 리포트, 자동 수정, 업종별 검사팩을 유료 기능으로 확장할 예정입니다.
          </p>
        </div>
      </section>
    </div>
  );
}
