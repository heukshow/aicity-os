import tools from "../data/tools.json";

export default function Home() {
  return (
    <div className="container mx-auto px-6 max-w-6xl">
      {/* FTC Disclosure - Legal Compliance */}
      <div className="mt-4 p-3 bg-white/5 border border-white/10 rounded-lg text-[11px] text-gray-500 text-center">
        <span className="font-bold text-brand mr-2">[법적 고지]</span> 
        본 사이트는 기업용 AI 도구의 객관적인 정보를 제공하며, 추천 링크를 통한 서비스 가입 시 파트너사로부터 소정의 수수료를 지급받을 수 있습니다. 
        이는 이용자의 결제 금액에 영향을 미치지 않으며, 모든 서비스 계약 및 책임은 해당 솔루션 제공업체와 이용자 간의 계약에 따릅니다.
      </div>

      {/* Hero: B2B Focus */}
      <section className="py-24 text-center">
        <div className="inline-block px-4 py-1.5 mb-6 rounded-full bg-brand/10 border border-brand/20 text-brand text-xs font-bold tracking-widest uppercase">
          Enterprise Efficiency Suite 2026
        </div>
        <h1 className="text-6xl md:text-7xl font-black mb-8 leading-[1.1]">
          AI로 귀사의 <br /><span className="gradient-text">운영 비용을 절감하십시오.</span>
        </h1>
        <p className="text-xl md:text-2xl text-gray-400 max-w-3xl mx-auto font-light leading-relaxed mb-12">
          검증된 데이터와 법적 가이드라인을 바탕으로 <br />
          최적의 <strong>AI 에이전트 도입</strong>을 지원합니다.
        </p>
      </section>

      {/* Consultation Form with Legal Consent */}
      <section className="py-16 glass rounded-[40px] p-10 mb-20">
        <h2 className="text-3xl font-bold mb-8 text-center">AI 도입 무료 진단 신청</h2>
        <form className="max-w-2xl mx-auto space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <input type="text" placeholder="성함/담당자명" className="bg-white/5 border border-white/10 rounded-xl p-4 outline-none focus:border-brand transition" required />
            <input type="email" placeholder="회사 이메일 (@coshuma.com 추천)" className="bg-white/5 border border-white/10 rounded-xl p-4 outline-none focus:border-brand transition" required />
          </div>
          <textarea placeholder="현재 고민 중인 업무 자동화 영역을 적어주세요." className="w-full bg-white/5 border border-white/10 rounded-xl p-4 h-32 outline-none focus:border-brand transition" required></textarea>
          
          {/* Legal Consent Checkboxes - PIPA Compliance */}
          <div className="bg-black/20 p-6 rounded-2xl border border-white/5 space-y-4">
            <label className="flex items-start space-x-3 cursor-pointer">
              <input type="checkbox" className="mt-1 accent-brand" required />
              <span className="text-xs text-gray-400 leading-relaxed">
                [필수] 개인정보 수집 및 이용 동의: 이름, 연락처, 이메일 주소를 상담 목적 및 서비스 안내를 위해 수집하며, 목적 달성 후 지체 없이 파기합니다.
              </span>
            </label>
            <label className="flex items-start space-x-3 cursor-pointer">
              <input type="checkbox" className="mt-1 accent-brand" required />
              <span className="text-xs text-gray-400 leading-relaxed">
                [필수] 개인정보 제3자 제공 동의: 효율적인 AI 솔루션 매칭 및 상담 진행을 위해 수집된 정보를 협력 파트너사(AI 구축 전문업체)에 제공하는 것에 동의합니다.
              </span>
            </label>
          </div>

          <button className="w-full py-5 rounded-2xl bg-brand text-black font-black text-xl hover:scale-[1.02] transition-transform">
            무료 진단 리포트 신청하기
          </button>
        </form>
      </section>

      {/* Profitability Index (B2B Specialized Tools) */}
      <section className="py-16">
        <h2 className="text-4xl font-bold mb-16 text-center">검증된 <span className="text-brand">AI 에이전트</span> 리스트</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
          {tools.map((tool) => (
            <div key={tool.id} className="group relative glass p-10 rounded-[40px] hover:border-brand/30 transition-all">
              <div className="flex justify-between items-start mb-8">
                <div>
                  <h3 className="text-3xl font-black mb-2">{tool.name}</h3>
                  <div className="flex flex-wrap gap-2">
                    {tool.tags.map(tag => (
                      <span key={tag} className="text-[10px] font-bold text-brand uppercase tracking-tighter">#{tag}</span>
                    ))}
                  </div>
                </div>
              </div>
              <p className="text-gray-400 text-sm mb-8 leading-relaxed">{tool.korean_desc}</p>
              <a 
                href={tool.url}
                target="_blank"
                className="flex items-center justify-center space-x-3 w-full py-5 rounded-3xl bg-white text-black font-black hover:bg-brand transition-colors text-lg"
              >
                <span>솔루션 상세 보기</span>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg>
              </a>
            </div>
          ))}
        </div>
      </section>

      {/* Legal Footer */}
      <footer className="py-20 border-t border-white/10 mt-20 text-center">
        <div className="flex flex-wrap justify-center gap-8 mb-8 text-xs font-bold text-gray-500">
          <a href="#" className="hover:text-white transition">이용약관</a>
          <a href="#" className="text-white hover:text-brand transition">개인정보처리방침</a>
          <a href="#" className="hover:text-white transition">제휴문의</a>
        </div>
        <p className="text-[10px] text-gray-600">
          &copy; 2026 COSUMA Market. All Rights Reserved. <br />
          본 사이트는 지식 서비스 제공을 목적으로 하며, 특정 AI 솔루션의 직접적인 판매 주체가 아닙니다.
        </p>
      </footer>
    </div>
  );
}
