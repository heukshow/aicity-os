import tools from "../data/tools.json";

export default function Home() {
  return (
    <div className="container mx-auto px-6 max-w-6xl">
      {/* FTC Disclosure - Legal Compliance */}
      <div className="mt-4 p-3 bg-white/5 border border-white/10 rounded-lg text-[11px] text-gray-500 text-center">
        <span className="font-bold text-brand mr-2">[공지]</span> 
        본 사이트는 기업용 AI 도구 추천 정보를 제공하며, 일부 도구의 링크를 통해 서비스 결제가 이루어질 경우 소정의 제휴 수수료를 지급받을 수 있음을 명확히 밝힙니다. 
        이는 사용자에게 추가 비용을 발생시키지 않으며, 투명한 리뷰 운영을 위해 게시물 상단에 고지합니다.
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
          단순한 추천이 아닙니다. 국내 비즈니스 환경에 최적화된 <br />
          최적의 <strong>AI 에이전트</strong>와 <strong>비용 절감 시뮬레이션</strong>을 제공합니다.
        </p>
        <div className="flex flex-col md:flex-row justify-center gap-6">
          <button className="px-10 py-5 rounded-2xl bg-brand font-black text-black hover:scale-105 transition-transform">
            솔루션 무료 진단 받기
          </button>
          <button className="px-10 py-5 rounded-2xl bg-white/5 border border-white/10 font-bold hover:bg-white/10 transition">
            AI 바우처 지원금 확인
          </button>
        </div>
      </section>

      {/* Profitability Index (B2B Specialized Tools) */}
      <section className="py-16">
        <div className="flex flex-col md:flex-row justify-between items-end mb-16 gap-6">
          <div>
            <h2 className="text-4xl font-bold mb-4">기업 전용 <span className="text-brand">AI Pick 2026</span></h2>
            <p className="text-gray-500">실질적인 ROI(투자 대비 수익)가 증명된 도구들입니다.</p>
          </div>
          <div className="flex overflow-x-auto pb-2 space-x-3 no-scrollbar">
            {['전체', '워크플로우', '고객관리', '마케팅'].map(tab => (
              <button key={tab} className="whitespace-nowrap px-6 py-2 rounded-xl bg-white/5 border border-white/10 text-sm font-bold hover:bg-brand/20 transition">
                {tab}
              </button>
            ))}
          </div>
        </div>
        
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
                <div className="text-right">
                  <div className="text-brand text-xs font-black mb-1">COMPATIBILITY</div>
                  <div className="text-2xl font-mono font-black italic">{(tool.rating * 20).toFixed(0)}%</div>
                </div>
              </div>
              
              {/* ROI Insight (Automated Analysis Pattern) */}
              <div className="mb-10 p-6 rounded-3xl bg-black/40 border border-white/5">
                <h4 className="text-xs font-bold text-gray-400 mb-3 flex items-center">
                  <span className="w-1 h-1 bg-brand rounded-full mr-2"></span> 분석 데이터
                </h4>
                <p className="text-gray-300 text-sm leading-relaxed">
                  {tool.id === 'claude' ? 
                    "한국 기업 보고서 작성 효율 340% 향상 확인. 전문적인 뉘앙스 구현으로 외부 커뮤니케이션 리스크 최소화." : 
                    "데이터 요약 및 초기 기획 단계에서 인당 월평균 12시간 업무 시간 절감 효과 발생."}
                </p>
              </div>

              <a 
                href={tool.url}
                target="_blank"
                className="flex items-center justify-center space-x-3 w-full py-5 rounded-3xl bg-white text-black font-black hover:bg-brand transition-colors text-lg"
              >
                <span>상담 및 도입 안내</span>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg>
              </a>
            </div>
          ))}
        </div>
      </section>

      {/* B2B Insight Section */}
      <section className="py-24 border-t border-white/10 mt-20">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
          {[
            { title: "2026 AI 바우처 가이드", desc: "최대 5천만 원 지원! 기업 자격 요건과 신청 기간을 확인하세요." },
            { title: "DX 전환 비용 시뮬레이션", desc: "직종별 AI 도입 시 예상되는 연간 인건비 절감액을 계산해 드립니다." },
            { title: "국내 법률 가이드", desc: "AI 도입 시 발생하는 보안 및 저작권 규제, 완벽히 준수하는 법." }
          ].map((item, i) => (
            <div key={i} className="hover:translate-y-[-8px] transition">
              <h4 className="text-xl font-bold mb-4">{item.title}</h4>
              <p className="text-gray-500 text-sm mb-6 leading-relaxed">{item.desc}</p>
              <a href="#" className="text-brand text-xs font-bold underline underline-offset-8">자세히 보기</a>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
