
// Payment System Variables
window.currentPaymentToolId = null;
window.currentPaymentToolName = null;
window.currentPaymentPriceKRW = null;
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('fortune-form');
    const loader = document.getElementById('loader');
    const resultArea = document.getElementById('result-text');
    const upsellBtn = document.getElementById('btn-upsell');
    const particlesContainer = document.getElementById('particles');

    // Generate floating particles for background ambiance
    function createParticles() {
        for (let i = 0; i < 20; i++) {
            let particle = document.createElement('div');
            particle.classList.add('particle');

            // Randomize position, size, and animation duration
            let size = Math.random() * 5 + 2;
            let startPosX = Math.random() * window.innerWidth;
            let duration = Math.random() * 10 + 10;
            let delay = Math.random() * 5;

            particle.style.width = size + 'px';
            particle.style.height = size + 'px';
            particle.style.left = startPosX + 'px';
            particle.style.bottom = '-10px';
            particle.style.animationDuration = duration + 's';
            particle.style.animationDelay = delay + 's';

            particlesContainer.appendChild(particle);
        }
    }

    createParticles();

    // Oracle-specific tiered tools  { id, icon, title{ko,en}, desc{ko,en}, price }
    const oracleTools = {
        saju: [
            {
                id: 'saju_karma', icon: '🌀', price: '₩6,900', best: true,
                title: { ko: '전생과 현생의 카르마 분석', en: 'Past Life & Current Karma' },
                desc: { ko: '오행을 통해 짚어보는 나의 전생 스토리와 현생의 업보', en: 'Your past life story and current karma based on elements' }
            },
            {
                id: 'saju_crisis', icon: '🚨', price: '₩4,900', best: true,
                title: { ko: '향후 3년 내 인생 최대 위기 경보', en: '3-Year Biggest Crisis Warning' },
                desc: { ko: '블랙스완 분석: 가장 피해야 할 최악의 시기와 사건', en: 'Black Swan Analysis: The absolute worst timing and events to avoid' }
            },
            {
                id: 'saju_brutal_wealth', icon: '💰', price: '₩4,900',
                title: { ko: '뼈때리는 팩트폭행: 나의 숨겨진 재물 그릇', en: 'Brutal Truth: Your Hidden Wealth Capacity' },
                desc: { ko: '내가 부자가 되지 못하는 사주적 이유 (초극딜 분석)', en: 'Ruthless investor analysis on why you lack money' }
            },
            {
                id: 'saju_custom', icon: '🗣️', price: '₩900', best: true,
                title: { ko: '1:1 맞춤형 질문 (자유질문)', en: 'Custom 1:1 Question' },
                desc: { ko: '사주를 바탕으로 원하시는 구체적인 질문 1가지에 대해 명확한 해답을 드립니다.', en: 'One specific, custom question answered using your Saju chart.' }
            },
            {
                id: 'saju_daily', icon: '📅', price: '₩500',
                title: { ko: '오늘의 상세 사주 운세', en: 'Today\'s Detailed Saju' },
                desc: { ko: '시간별 기운 흐름과 유의할 시각', en: 'Hourly energy flow & caution times' }
            },
            {
                id: 'saju_yearly', icon: '🗓️', price: '₩1,900',
                title: { ko: '연간 대운 & 세운 분석', en: 'Yearly Fortune & Major Cycle' },
                desc: { ko: '올해 전반의 재물·건강·관계 흐름', en: 'Wealth, health, relationship flow this year' }
            },
            {
                id: 'saju_lifetime', icon: '🌌', price: '₩900', best: true,
                title: { ko: '종합 대운 & 용신 분석', en: 'Full 10-Year Cycle & Core Element' },
                desc: { ko: '10년 대운 + 용신·기신 + 인생 최강 시기 판정', en: '10-yr cycle, favorable element & peak life period' }
            },
            {
                id: 'saju_modern', icon: '🏙️', price: '₩900', best: true,
                title: { ko: '현대적 심층 사주 프로파일링', en: 'Modern Saju Profiling' },
                desc: { ko: '현재 나이와 현대 사회에 맞춘 직업, 적성, 상황 예측', en: 'Modern career & life prediction based on your current age' }
            },
            {
                id: 'saju_past', icon: '⏪', price: '₩900',
                title: { ko: '과거 대운 확인', en: 'Past Luck Cycle Verification' },
                desc: { ko: '특정 나이대의 사주 흐름으로 과거 사건 확인', en: 'Reveal what your chart says happened at a past age' }
            },
        ],
        tarot: [
            {
                id: 'tarot_custom', icon: '🗣️', price: '₩900', best: true,
                title: { ko: '1:1 맞춤형 질문 (자유질문)', en: 'Custom 1:1 Question' },
                desc: { ko: '원하시는 구체적인 질문 1가지에 대해 타로카드를 뽑아 심층 답변해 드립니다.', en: 'One specific, custom question answered via Tarot draw.' }
            },
            {
                id: 'tarot_3card', icon: '🃏', price: '₩900',
                title: { ko: '3카드 스프레드', en: '3-Card Spread' },
                desc: { ko: '과거·현재·미래 카드 집중 해석', en: 'Past / Present / Future card reading' }
            },
            {
                id: 'tarot_celtic', icon: '🔯', price: '₩1,900',
                title: { ko: '켈틱 크로스 10장', en: 'Celtic Cross (10 Cards)' },
                desc: { ko: '상황·장애·환경·결과 10개 위치 심층 해석', en: '10-position deep spread: situation, obstacles, outcome' }
            },
            {
                id: 'tarot_love', icon: '💖', price: '₩3,900', best: true,
                title: { ko: '심층 연애 타로', en: 'Deep Love Tarot' },
                desc: { ko: '소울메이트·관계 전망·이별/재회 가능성 전격 분석', en: 'Soulmate, relationship outlook & reunion chances' }
            },
        ],
        astrology: [
            {
                id: 'astro_crosscheck', icon: '⚖️', price: '₩9,900', best: true,
                title: { ko: '동서양 사주·별자리 크로스체크', en: 'Saju x Astrology Cross-Check' },
                desc: { ko: '절대 피할 수 없는, 동서양 명리학이 공통으로 가리키는 나의 치명적 약점', en: 'The one fatal flaw both Eastern and Western astrology warn you about' }
            },
            {
                id: 'astro_custom', icon: '🗣️', price: '₩900', best: true,
                title: { ko: '1:1 맞춤형 질문 (자유질문)', en: 'Custom 1:1 Question' },
                desc: { ko: '출생 차트를 바탕으로 원하시는 고민이나 질문 1가지에 대해 심층 답변해 드립니다.', en: 'One specific, custom question answered using your Astrological chart.' }
            },
            {
                id: 'astro_sun', icon: '☀️', price: '₩900',
                title: { ko: '태양궁 & 성격 분석', en: 'Sun Sign & Personality' },
                desc: { ko: '태양궁 심층 성격 + 강점/약점', en: 'Deep sun sign personality, strengths & weaknesses' }
            },
            {
                id: 'astro_rising', icon: '🌅', price: '₩1,900',
                title: { ko: '달궁·상승궁 분석', en: 'Moon & Rising Sign Analysis' },
                desc: { ko: '감정패턴(달) + 타인에게 비치는 첫인상(상승)', en: 'Emotional patterns (Moon) + first impression (Rising)' }
            },
            {
                id: 'astro_transit', icon: '🔭', price: '₩1,900',
                title: { ko: '행성 트랜짓 분석', en: 'Planetary Transit Analysis' },
                desc: { ko: '현재 행성 배치가 나의 하우스에 미치는 실질적 영향', en: 'Current planetary positions & house impact' }
            },
            {
                id: 'astro_full', icon: '🌟', price: '₩3,900', best: true,
                title: { ko: '전생·운명·영혼 분석', en: 'Past Life, Destiny & Soul Chart' },
                desc: { ko: '출생 차트 전체 해석 + 전생 카르마 + 영혼 목적 분석', en: 'Full birth chart + past-life karma + soul purpose' }
            },
            {
                id: 'astro_past', icon: '⏪', price: '₩900',
                title: { ko: '과거 행성 이벤트 맞추기', en: 'Past Planetary Event Verification' },
                desc: { ko: '특정 나이대의 행성 트랜짓으로 과거 사건 맞추기', en: 'What transits reveal about your past period' }
            },
        ],
        palmistry: [
            {
                id: 'palm_lines', icon: '✋', price: '₩900',
                title: { ko: '생명선·두뇌선 분석', en: 'Life & Head Line Analysis' },
                desc: { ko: '생명력·체력 + 사고방식·결단력 해석', en: 'Vitality, health + thinking style & decisiveness' }
            },
            {
                id: 'palm_heart', icon: '❤️', price: '₩1,900',
                title: { ko: '감정선·운명선 분석', en: 'Heart & Fate Line Analysis' },
                desc: { ko: '감정 패턴·연애운 + 사회적 성취와 운명의 전환점', en: 'Emotional patterns + career turning points' }
            },
            {
                id: 'palm_full', icon: '🖐️', price: '₩3,900', best: true,
                title: { ko: '전체 손 종합 분석', en: 'Full Palm Reading' },
                desc: { ko: '5개 주요선 + 손 형태 + 재물궁·결혼선 전격 분석', en: '5 major lines + hand shape + marriage & wealth mounts' }
            },
        ],
        physiognomy: [
            {
                id: 'physio_montage', icon: '👤', price: '₩3,900', best: true,
                title: { ko: '나의 천적 & 귀인 관상 얼굴 묘사', en: 'Nemesis & Benefactor Montage' },
                desc: { ko: '내가 반드시 피해야 할 얼굴과 곁에 둬야 할 얼굴 상세 묘사', en: 'Detailed facial traits of who will ruin you and who will save you' }
            },
            {
                id: 'physio_eyes', icon: '👁️', price: '₩900',
                title: { ko: '눈·코 관상 분석', en: 'Eyes & Nose Reading' },
                desc: { ko: '눈빛(의지력) + 코(재물운) 세부 해석', en: 'Eye energy (will) + nose (wealth luck)' }
            },
            {
                id: 'physio_face', icon: '🧑', price: '₩1,900',
                title: { ko: '오행 관상 분석', en: '5-Elements Face Analysis' },
                desc: { ko: '얼굴형 오행 + 이마·턱·볼 재물·명예 해석', en: 'Face shape element + forehead, jaw, cheek fortune' }
            },
            {
                id: 'physio_full', icon: '🪞', price: '₩3,900', best: true,
                title: { ko: '종합 관상 + 재물궁', en: 'Full Physiognomy + Wealth Gates' },
                desc: { ko: '전면 이목구비 + 재물·귀인·수명궁 종합 판정', en: 'Full facial reading + wealth, benefactor & longevity gates' }
            },
        ],
        vedic: [
            {
                id: 'vedic_nakshatra', icon: '⭐', price: '₩900',
                title: { ko: '나크샤트라(별자리) 분석', en: 'Nakshatra Analysis' },
                desc: { ko: '탄생 별자리 성격·직업 적성·숨겨진 재능', en: 'Birth star personality, vocation & hidden talents' }
            },
            {
                id: 'vedic_dasha', icon: '🔄', price: '₩1,900',
                title: { ko: '마하다샤 주기 분석', en: 'Mahadasha Cycle Analysis' },
                desc: { ko: '현재 대주기 + 다음 전환점의 흐름 예측', en: 'Current major period + next transition prediction' }
            },
            {
                id: 'vedic_full', icon: '🕉️', price: '₩900', best: true,
                title: { ko: '종합 라시 차트 분석', en: 'Full Rashi Chart Reading' },
                desc: { ko: '12궁 행성 배치 + 요가(길격) + 인생 최대 전환점', en: '12-house placements, Yogas & life turning points' }
            },
            {
                id: 'vedic_past', icon: '⏪', price: '₩900',
                title: { ko: '과거 다샤 주기 확인', en: 'Past Dasha Cycle Verification' },
                desc: { ko: '특정 나이대의 다샤 주기로 과거 사건 확인', en: 'What your Dasha cycle reveals about a past period' }
            },
        ],
        bazi: [
            {
                id: 'bazi_daymaster', icon: '🀄', price: '₩900',
                title: { ko: '일주(日柱) 분석', en: 'Day Master Analysis' },
                desc: { ko: '일간 오행 + 성격·직업 적성·대인관계', en: 'Day stem element + personality & career aptitude' }
            },
            {
                id: 'bazi_luck', icon: '🎰', price: '₩1,900',
                title: { ko: '대운 흐름 분석', en: 'Luck Cycle Analysis' },
                desc: { ko: '현재 대운 + 재물 기회가 오는 시기 판정', en: 'Current luck cycle + when wealth opportunities arrive' }
            },
            {
                id: 'bazi_full', icon: '☯️', price: '₩900', best: true,
                title: { ko: '오행 균형 & 용신 분석', en: 'Full 5-Element & Yongshen Analysis' },
                desc: { ko: '사주 팔자 전체 오행 균형 + 용신 특정 + 인생 전략', en: 'Full chart element balance + favorable element + life strategy' }
            },
            {
                id: 'bazi_past', icon: '⏪', price: '₩900',
                title: { ko: '과거 대운 확인', en: 'Past Luck Pillar Verification' },
                desc: { ko: '특정 나이대의 중국식사주 대운으로 과거 사건 확인', en: 'What your Bazi luck pillar reveals about a past period' }
            },
        ],
        iching: [
            {
                id: 'iching_basic', icon: '☰', price: '₩900',
                title: { ko: '기본 괘 해석', en: 'Basic Hexagram Reading' },
                desc: { ko: '질문에 답하는 주괘 + 핵심 메시지', en: 'Primary hexagram & core message for your question' }
            },
            {
                id: 'iching_lines', icon: '☲', price: '₩1,900',
                title: { ko: '변효(變爻) 심층 분석', en: 'Changing Lines Deep Analysis' },
                desc: { ko: '변화하는 효 해석 + 지괘 전환의 의미', en: 'Changing lines + resulting hexagram transformation' }
            },
            {
                id: 'iching_full', icon: '📜', price: '₩3,900', best: true,
                title: { ko: '종합 운명 판단', en: 'Full Destiny Judgment' },
                desc: { ko: '상·하괘 + 변효 + 체용 + 현실적 행동 전략 제안', en: 'Upper/lower + changing lines + practical action strategy' }
            },
        ],
        numerology: [
            {
                id: 'num_lifepath', icon: '🔢', price: '₩900',
                title: { ko: '생명수 분석', en: 'Life Path Number' },
                desc: { ko: '핵심 생명수 + 타고난 목적과 재능', en: 'Core life path number, purpose & innate talents' }
            },
            {
                id: 'num_expression', icon: '🔤', price: '₩1,900',
                title: { ko: '표현수 & 영혼수', en: 'Expression & Soul Urge Numbers' },
                desc: { ko: '이름 표현수(외부 모습) + 영혼수(내면의 갈망)', en: 'How you appear to others (Expression) + inner desire (Soul)' }
            },
            {
                id: 'num_personal', icon: '📊', price: '₩3,900', best: true,
                title: { ko: '개인년도 & 핵심 주기 분석', en: 'Personal Year & Core Cycle' },
                desc: { ko: '올해 개인년도 + 9년 주기 + 최적 행동 타이밍', en: 'This year\'s personal year + 9-year cycle + optimal action timing' }
            },
        ],
        runes: [
            {
                id: 'runes_3', icon: '᚛', price: '₩900',
                title: { ko: '3룬 배열', en: '3-Rune Cast' },
                desc: { ko: '과거·현재·미래 3룬 집중 해석', en: 'Past / Present / Future 3-rune interpretation' }
            },
            {
                id: 'runes_5', icon: '✦', price: '₩1,900',
                title: { ko: '5룬 십자 배열', en: '5-Rune Cross Spread' },
                desc: { ko: '중심·장애·조언·결과 5위치 심층 해석', en: 'Center, obstacle, advice, outcome — 5-position reading' }
            },
            {
                id: 'runes_full', icon: '🗿', price: '₩3,900', best: true,
                title: { ko: '종합 운명 룬 배열', en: 'Full Destiny Rune Spread' },
                desc: { ko: 'Aett별 9룬 + 숨겨진 운명의 전체 메시지', en: '9-rune Aett spread + full hidden destiny message' }
            },
        ],
        name: [
            {
                id: 'name_hanja_analysis', icon: '🀄', price: '₩900',
                title: { ko: '획수 심층분석', en: 'Hanja Stroke Analysis' },
                desc: { ko: '한자 획수 + 81수리 길흉 판정', en: 'Hanja stroke count + 81 numerology fortune' }
            },
            {
                id: 'name_saju_harmony', icon: '☯️', price: '₩1,900',
                title: { ko: '이름과 사주 조화 분석', en: 'Name-Saju Harmony' },
                desc: { ko: '생년월일 오행 vs 이름 오행 충·합 분석', en: 'Birth element vs name element compatibility' }
            },
            {
                id: 'name_change', icon: '💎', price: '₩900', best: true,
                title: { ko: '개명 전문 상담', en: 'Name Change Consultation' },
                desc: { ko: '현재 이름 진단 + 개명 후보안 3가지 + 운 예측', en: 'Name diagnosis + 3 alternative names + fortune forecast' }
            },
        ],
    };

    // ── Auth helpers ─────────────────────────────────────────────────────────
    window.currentUser = null;

    window.switchAuthTab = function (tab) {
        const isLogin = tab === 'login';
        document.getElementById('form-login').style.display = isLogin ? 'block' : 'none';
        document.getElementById('form-register').style.display = isLogin ? 'none' : 'block';
        document.getElementById('tab-login').style.background = isLogin ? 'rgba(255,215,0,0.2)' : 'transparent';
        document.getElementById('tab-register').style.background = isLogin ? 'transparent' : 'rgba(255,215,0,0.2)';
        document.getElementById('tab-login').style.color = isLogin ? 'var(--accent-gold,#d4af37)' : '#999';
        document.getElementById('tab-register').style.color = isLogin ? '#999' : 'var(--accent-gold,#d4af37)';
    };

    function applyUserProfile(user) {
        if (!user) return;
        window.currentUser = user;
        // Auto-fill main oracle form fields
        const setVal = (id, val) => { const el = document.getElementById(id); if (el && val) el.value = val; };
        setVal('user-name', user.name);
        setVal('birth-year', user.birthYear);
        setVal('birth-month', user.birthMonth);
        setVal('birth-day', user.birthDay);
        setVal('birth-ampm', user.birthTimeAmpm);
        setVal('birth-hour', user.birthTimeHour);
        setVal('birth-minute', user.birthTimeMinute);
        setVal('birth-calendar', user.calendar);
        setVal('gender', user.gender);
        // Also pre-fill name oracle inputs
        setVal('name-korean', user.name);
        setVal('intention-name', user.name);
        // Update header button
        document.getElementById('auth-btn-icon').textContent = '🔓';
        document.getElementById('auth-btn-label').textContent = '로그아웃 (' + (user.name || user.email) + ')';
        // Show history button
        const histBtn = document.getElementById('history-btn');
        if (histBtn) histBtn.style.display = 'flex';
        document.getElementById('auth-toggle-btn').onclick = () => {
            document.getElementById('profile-modal').style.display = 'flex';
            setVal('prof-name', user.name);
            setVal('prof-year', user.birthYear);
            setVal('prof-month', user.birthMonth);
            setVal('prof-day', user.birthDay);
            setVal('prof-calendar', user.calendar);
            setVal('prof-gender', user.gender);
            setVal('prof-time-ampm', user.birthTimeAmpm);
            setVal('prof-time-hour', user.birthTimeHour);
            setVal('prof-time-min', user.birthTimeMinute);
            document.getElementById('prof-err').style.display = 'none';
            document.getElementById('prof-succ').style.display = 'none';
        };
    }

    // Default handler for non-logged in users
    document.getElementById('auth-toggle-btn').onclick = () => {
        document.getElementById('auth-modal').style.display = 'flex';
    };

    // Check existing session on load
    fetch('/api/auth/me', { credentials: 'include' })
        .then(r => r.json())
        .then(d => { if (d.user) applyUserProfile(d.user); })
        .catch(() => { });

    // Login handler
    document.getElementById('do-login-btn').addEventListener('click', async () => {
        const email = document.getElementById('login-email').value.trim();
        const pw = document.getElementById('login-pw').value;
        const errEl = document.getElementById('login-err');
        errEl.style.display = 'none';
        try {
            const res = await fetch('/api/auth/login', {
                method: 'POST', credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password: pw })
            });
            const d = await res.json();
            if (!res.ok) { errEl.textContent = d.error; errEl.style.display = 'block'; return; }
            applyUserProfile(d.user);
            if (window.loadPurchases) window.loadPurchases();
            document.getElementById('auth-modal').style.display = 'none';
        } catch { errEl.textContent = '서버 연결 오류'; errEl.style.display = 'block'; }
    });

    // Handle Enter key for login
    document.getElementById('form-login').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            document.getElementById('do-login-btn').click();
        }
    });

    // Register handler
    document.getElementById('do-register-btn').addEventListener('click', async () => {
        const errEl = document.getElementById('reg-err');
        errEl.style.display = 'none';
        const body = {
            email: document.getElementById('reg-email').value.trim(),
            password: document.getElementById('reg-pw').value,
            name: document.getElementById('reg-name').value.trim(),
            birthYear: document.getElementById('reg-year').value,
            birthMonth: document.getElementById('reg-month').value,
            birthDay: document.getElementById('reg-day').value,
            birthTimeAmpm: document.getElementById('reg-time-ampm').value,
            birthTimeHour: document.getElementById('reg-time-hour').value,
            birthTimeMinute: document.getElementById('reg-time-min').value,
            calendar: document.getElementById('reg-calendar').value,
            gender: document.getElementById('reg-gender').value,
            language: window.currentLanguage || 'ko'
        };
        try {
            const res = await fetch('/api/auth/register', {
                method: 'POST', credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            const d = await res.json();
            if (!res.ok) { errEl.textContent = d.error; errEl.style.display = 'block'; return; }
            applyUserProfile(d.user);
            if (window.loadPurchases) window.loadPurchases();
            document.getElementById('auth-modal').style.display = 'none';
        } catch { errEl.textContent = '서버 연결 오류'; errEl.style.display = 'block'; }
    });

    // Handle Enter key for register
    document.getElementById('form-register').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            document.getElementById('do-register-btn').click();
        }
    });

    document.getElementById('do-update-profile-btn').addEventListener('click', async () => {
        const errEl = document.getElementById('prof-err');
        const succEl = document.getElementById('prof-succ');
        errEl.style.display = 'none';
        succEl.style.display = 'none';

        const body = {
            name: document.getElementById('prof-name').value.trim(),
            birthYear: document.getElementById('prof-year').value,
            birthMonth: document.getElementById('prof-month').value,
            birthDay: document.getElementById('prof-day').value,
            birthTimeAmpm: document.getElementById('prof-time-ampm').value,
            birthTimeHour: document.getElementById('prof-time-hour').value,
            birthTimeMinute: document.getElementById('prof-time-min').value,
            calendar: document.getElementById('prof-calendar').value,
            gender: document.getElementById('prof-gender').value
        };
        try {
            const res = await fetch('/api/auth/profile', {
                method: 'PUT', credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            const d = await res.json();
            if (!res.ok) { errEl.textContent = d.error || '수정 실패'; errEl.style.display = 'block'; return; }

            succEl.style.display = 'block';
            applyUserProfile(d.user);

            setTimeout(() => {
                document.getElementById('profile-modal').style.display = 'none';
            }, 1500);
        } catch { errEl.textContent = '서버 연결 오류'; errEl.style.display = 'block'; }
    });

    // ── End Auth ──────────────────────────────────────────────────────────────

    // ── Reading History ────────────────────────────────────────────────────────
    const ORACLE_ICONS = {
        saju: '✨', tarot: '☀️', astrology: '⭐', palmistry: '✨',
        physiognomy: '✨', vedic: '✨', bazi: '✨', iching: '☰',
        numerology: '✨', runes: '✨', name: '✨'
    };

    async function saveReading(oracle, title, fortune) {
        if (!window.currentUser) return;
        fetch('/api/user/readings', {
            method: 'POST', credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ oracle, title, fortune })
        }).catch(() => { });
    }

    window.openHistoryModal = async function () {
        const modal = document.getElementById('history-modal');
        const list = document.getElementById('history-list');
        modal.style.display = 'flex';
        list.innerHTML = '<p style="color:#666;text-align:center;padding:30px;">불러오는 중...</p>';
        try {
            const res = await fetch('/api/user/readings', { credentials: 'include' });
            const data = await res.json();
            const readings = data.readings || [];
            if (readings.length === 0) {
                list.innerHTML = '<p style="color:#666;text-align:center;padding:30px;">아직 저장된 운세 기록이 없습니다.<br><span style="font-size:0.8rem;">운세를 받으면 자동으로 저장됩니다.</span></p>';
                return;
            }
            list.innerHTML = '';
            readings.forEach(r => {
                const icon = ORACLE_ICONS[r.oracle] || '🔮';
                const date = new Date(r.created_at).toLocaleString('ko-KR', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
                const preview = r.fortune.length > 120 ? r.fortune.slice(0, 120) + '...' : r.fortune;
                const cardId = 'hist-' + r.id;
                const card = document.createElement('div');
                card.style.cssText = 'background:rgba(255,255,255,0.04);border:1px solid rgba(255,215,0,0.15);border-radius:14px;padding:18px;position:relative;';
                card.innerHTML = `
                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
                        <span style="font-size:1.3rem;">${icon}</span>
                        <div>
                            <div style="color:var(--accent-gold,#d4af37);font-weight:700;font-size:0.95rem;">${r.title}</div>
                            <div style="color:#777;font-size:0.72rem;">${date}</div>
                        </div>
                        <button onclick="deleteReading(${r.id}, this)"
                            style="position:absolute;top:14px;right:14px;background:none;border:none;color:#555;font-size:1.1rem;cursor:pointer;" title="삭제">🗑</button>
                    </div>
                    <div id="${cardId}-preview" style="color:#ccc;font-size:0.85rem;line-height:1.7;white-space:pre-wrap;">${preview}</div>
                    ${r.fortune.length > 120 ? `
                    <button onclick="toggleFull('${cardId}', ${JSON.stringify(r.fortune).replace(/'/g, '&apos;')})"
                        id="${cardId}-btn"
                        style="margin-top:10px;background:none;border:1px solid rgba(255,215,0,0.3);border-radius:20px;padding:4px 14px;color:#d4af37;font-size:0.75rem;cursor:pointer;">
                        전체 보기
                    </button>` : ''}
                `;
                list.appendChild(card);
            });
        } catch {
            list.innerHTML = '<p style="color:#f66;text-align:center;padding:30px;">불러오기 실패. 다시 시도해 주세요.</p>';
        }
    };

    window.deleteReading = async function (id, btn) {
        if (!confirm('이 기록을 삭제하시겠습니까?')) return;
        await fetch('/api/user/readings/' + id, { method: 'DELETE', credentials: 'include' });
        btn.closest('div[style]').remove();
    };

    window.toggleFull = function (cardId, fullText) {
        const preview = document.getElementById(cardId + '-preview');
        const btn = document.getElementById(cardId + '-btn');
        if (btn.textContent.trim() === '전체 보기') {
            preview.textContent = fullText;
            btn.textContent = '접기';
        } else {
            preview.textContent = fullText.slice(0, 120) + '...';
            btn.textContent = '전체 보기';
        }
    };
    // ── End Reading History ────────────────────────────────────────────────────

    // ── Past Oracle Handlers ───────────────────────────────────────────────────
    let _selectedAgeRange = '';

    window.setAgeRange = function (range) {
        _selectedAgeRange = range;
        document.querySelectorAll('#age-range-modal .age-quick-btn').forEach(b => {
            b.classList.toggle('selected', b.textContent === range);
        });
        // Auto-clear manual inputs
        document.getElementById('age-from').value = '';
        document.getElementById('age-to').value = '';
    };

    window.setPastAge = function (range) {
        _selectedAgeRange = range;
        document.querySelectorAll('#past-quick-btns .age-quick-btn').forEach(b => {
            b.classList.toggle('selected', b.textContent === range);
        });
        document.getElementById('past-age-from').value = '';
        document.getElementById('past-age-to').value = '';
    };

    // Age-range modal confirm → go to payment modal
    const ageConfirmBtn = document.getElementById('age-range-confirm-btn');
    if (ageConfirmBtn) {
        ageConfirmBtn.addEventListener('click', () => {
            if (!_selectedAgeRange) { alert('분석할 시기를 선택해 주세요.'); return; }
            document.getElementById('age-range-modal').style.display = 'none';
            const lang = window.currentLanguage || 'ko';
            const tool = window._pendingPastTool;
            if (!tool) return;
            // Check if already owned
            if (purchasedTools.has(tool.id)) {
                runPastAnalysis(tool.id, _selectedAgeRange);
            } else {
                document.getElementById('modal-tool-name').textContent = (tool.title[lang] || tool.title['en']) + ' — ' + _selectedAgeRange;
                premiumModal.style.display = 'flex';
            }
        });
    }

    // Standalone past panel submit
    const pastSubmitBtn = document.getElementById('past-submit-btn');
    if (pastSubmitBtn) {
        pastSubmitBtn.addEventListener('click', async () => {
            if (!_selectedAgeRange) { alert('분석할 시기를 선택해 주세요.'); return; }
            // Simulate payment
            paymentLoader.style.display = 'flex';
            await new Promise(r => setTimeout(r, 2000));
            paymentLoader.style.display = 'none';
            if (window.currentUser) {
                await fetch('/api/user/purchase', {
                    method: 'POST', credentials: 'include',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ oracle: window.currentOracle, tool_id: 'past_universal' })
                }).catch(() => { });
            }
            runPastAnalysis('past_universal', _selectedAgeRange);
        });
    }

    async function runPastAnalysis(toolId, ageRange) {
        const name = document.getElementById('user-name')?.value || '';
        const year = document.getElementById('birth-year')?.value || '';
        const month = document.getElementById('birth-month')?.value || '';
        const day = document.getElementById('birth-day')?.value || '';
        const calendar = document.getElementById('birth-calendar')?.value || 'solar';
        const gender = document.getElementById('gender')?.value || '';
        const ampm = document.getElementById('birth-ampm')?.value || '';
        const hour = document.getElementById('birth-hour')?.value || '';
        const minute = document.getElementById('birth-minute')?.value || '';
        const birthDate = `${year}-${month}-${day}`;
        let birthTimeInfo = 'Unknown time';
        if (hour) birthTimeInfo = `${hour}:${minute || '00'} ${ampm}`;
        const fullBirthInfo = `${birthDate} (Time: ${birthTimeInfo})`;

        loader.style.display = 'flex';
        try {
            const response = await fetch('/api/fortune/tool', {
                method: 'POST', credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name, birthDate: fullBirthInfo, calendar, gender,
                    tool_id: toolId, oracle: window.currentOracle,
                    language: window.currentLanguage || 'ko',
                    ageRange
                })
            });
            const data = await response.json();
            loader.style.display = 'none';
            resultArea.innerHTML += `
                <div style="margin-top:40px;padding-top:30px;border-top:1px dashed rgba(192,132,252,0.3);">
                    <h2 style="color:#c084fc;margin-bottom:16px;font-size:1.5rem;text-align:center;">⏪ ${data.title}</h2>
                    <div style="color:#eee;font-size:1.05rem;line-height:1.8;text-align:left;white-space:pre-wrap;background:rgba(192,132,252,0.05);padding:20px;border-radius:10px;border:1px solid rgba(192,132,252,0.2);">${data.fortune}</div>
                </div>
            `;
            saveReading(window.currentOracle || 'saju', `⏪ ${ageRange} 과거 맞추기`, data.fortune);
        } catch {
            loader.style.display = 'none';
        }
    }
    // ── End Past Oracle ────────────────────────────────────────────────────────

    // Populate Date Dropdowns
    const yearList = document.getElementById('year-list');
    const monthList = document.getElementById('month-list');
    const dayList = document.getElementById('day-list');

    const currentYear = new Date().getFullYear();
    for (let i = currentYear; i >= 1930; i--) {
        let option = document.createElement('option');
        option.value = i;
        yearList.appendChild(option);
    }
    for (let i = 1; i <= 12; i++) {
        let option = document.createElement('option');
        let val = i < 10 ? '0' + i : i;
        option.value = val;
        monthList.appendChild(option);
    }
    for (let i = 1; i <= 31; i++) {
        let option = document.createElement('option');
        let val = i < 10 ? '0' + i : i;
        option.value = val;
        dayList.appendChild(option);
    }

    // Populate Minute Dropdown (00 to 59)
    const minuteList = document.getElementById('minute-list');
    for (let i = 0; i <= 59; i++) {
        let option = document.createElement('option');
        let val = i < 10 ? '0' + i : i;
        option.value = val;
        minuteList.appendChild(option);
    }

    // Oracle Selection Logic
    window.currentOracle = 'saju';
    window.uploadedImageBase64 = null;

    // Group oracles by input type
    const oracleGroups = {
        date: ['saju', 'bazi', 'vedic', 'astrology', 'iching'],
        intention: ['tarot', 'runes', 'numerology'],
        image: ['palmistry', 'physiognomy'],
        name: ['name']
    };

    const extraPanel = document.getElementById('oracle-extra-input');
    const panelImage = document.getElementById('panel-image');
    const panelIntention = document.getElementById('panel-intention');
    const panelName = document.getElementById('panel-name');
    const mainForm = document.getElementById('fortune-form');

    function updateOraclePanel(oracle) {
        // Determine group
        let group = 'date';
        if (oracleGroups.intention.includes(oracle)) group = 'intention';
        if (oracleGroups.image.includes(oracle)) group = 'image';
        if (oracleGroups.name.includes(oracle)) group = 'name';

        // Reset all panels
        panelImage.style.display = 'none';
        panelIntention.style.display = 'none';
        if (panelName) panelName.style.display = 'none';
        const tarotArea = document.getElementById('tarot-display-area');
        if (tarotArea) tarotArea.style.display = 'none';

        // Hide main form for oracles that have their own dedicated submit panel
        if (mainForm) mainForm.style.display = (group === 'name' || group === 'intention') ? 'none' : 'block';

        if (group === 'date') {
            extraPanel.style.display = 'none';
        } else {
            extraPanel.style.display = 'block';
            if (group === 'image') {
                panelImage.style.display = 'block';
                const palmSelector = document.getElementById('palm-hand-selector');
                if (palmSelector) {
                    palmSelector.style.display = (oracle === 'palmistry') ? 'block' : 'none';
                }
            }
            if (group === 'intention') panelIntention.style.display = 'block';
            if (group === 'name') { if (panelName) panelName.style.display = 'block'; }
        }

        // Update upload label based on oracle using i18n
        const uploadLabel = document.getElementById('upload-label');
        if (uploadLabel) {
            const lang = window.currentLanguage || 'en';
            const t = translations[lang] || translations['en'];
            uploadLabel.textContent = oracle === 'palmistry' ? t.uploadLabelPalm : t.uploadLabelFace;
        }
    }

    const oracleCards = document.querySelectorAll('.oracle-card');
    oracleCards.forEach(card => {
        card.addEventListener('click', () => {
            oracleCards.forEach(c => c.classList.remove('active'));
            card.classList.add('active');
            window.currentOracle = card.getAttribute('data-oracle');
            window.uploadedImageBase64 = null; // reset on oracle change

            const preview = document.getElementById('upload-preview');
            const placeholder = document.getElementById('upload-placeholder');
            const retakeText = document.getElementById('upload-retake-text');
            if (preview && placeholder) {
                preview.style.display = 'none';
                preview.src = '';
                if (retakeText) retakeText.style.display = 'none';
                placeholder.style.display = 'block';
            }

            updateOraclePanel(window.currentOracle);
        });
    });

    // Image upload preview and base64 encode
    const imageUploadInput = document.getElementById('oracle-image-upload');
    if (imageUploadInput) {
        imageUploadInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = (ev) => {
                window.uploadedImageBase64 = ev.target.result.split(',')[1]; // base64 only
                const preview = document.getElementById('upload-preview');
                const placeholder = document.getElementById('upload-placeholder');
                const retakeText = document.getElementById('upload-retake-text');
                preview.src = ev.target.result;
                preview.style.display = 'block';
                if (retakeText) retakeText.style.display = 'block';
                placeholder.style.display = 'none';
            };
            reader.readAsDataURL(file);
        });
    }

    // Intention-based oracle submit button (Tarot, Runes, Numerology)
    const intentionSubmitBtn = document.getElementById('intention-submit-btn');
    if (intentionSubmitBtn) {
        intentionSubmitBtn.addEventListener('click', async () => {
            const intentionName = document.getElementById('intention-name').value.trim();
            const intention = document.getElementById('oracle-intention').value.trim();
            if (!intentionName) {
                alert('이름을 입력해 주세요.');
                return;
            }

            document.getElementById('oracle-extra-input').style.display = 'none';
            const oracleLabels = { tarot: '타로', runes: '룬 문자', numerology: '수비학' };
            const oracleLabel = oracleLabels[window.currentOracle] || window.currentOracle;

            let drawnCardsParam = null;
            if (window.currentOracle === 'tarot') {
                drawnCardsParam = await drawTarotCards(1);
            }

            if (window.currentOracle !== 'tarot') {
                loader.style.display = 'flex';
            }

            try {
                const response = await fetch('/api/fortune/free', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        name: intentionName,
                        birthDate: 'Unknown',
                        calendar: 'solar',
                        gender: 'unknown',
                        oracle: window.currentOracle,
                        intention,
                        drawn_cards: drawnCardsParam,
                        language: window.currentLanguage || 'en'
                    })
                });
                const data = await response.json();
                loader.style.display = 'none';
                resultArea.style.display = 'block';
                resultArea.innerHTML = `
                    <h3 style="color:var(--accent-gold);margin-bottom:20px;font-size:1.8rem;">${data.title || intentionName + ' · ' + oracleLabel}</h3>
                    <div style="color:#eee;font-size:1.05rem;line-height:1.9;text-align:left;white-space:pre-wrap;margin-bottom:30px;">${data.fortune}</div>
                `;

                // Dynamically Add Premium Consultation Tiers for ALL Oracles
                const tiers = oracleTools[window.currentOracle] || [];
                if (tiers.length > 0) {
                    const lang = window.currentLanguage || 'ko';
                    const secTitle = lang === 'ko' ? '🔮 심층 분석 서비스' : '🔮 Deep Analysis Services';
                    let html = `
                            <div style="border-top:1px dashed rgba(255,215,0,0.3);padding-top:28px;margin-top:10px;">
                                <p style="color:var(--accent-gold);font-size:1.05rem;font-weight:700;margin-bottom:18px;text-align:center;">${secTitle}</p>
                                <div style="display:flex;flex-direction:column;gap:14px;">
                        `;

                    tiers.forEach(tool => {
                        const isBest = tool.best ? `<div style="position:absolute;top:0;right:0;background:var(--accent-gold);color:#111;font-size:0.7rem;font-weight:900;padding:3px 10px;border-radius:0 14px 0 10px;">BEST</div>` : '';
                        const bg = tool.best ? 'linear-gradient(135deg,rgba(255,215,0,0.12),rgba(255,150,0,0.08))' : 'rgba(255,215,0,0.06)';
                        const border = tool.best ? '2px solid var(--accent-gold)' : '1px solid rgba(255,215,0,0.4)';
                        html += `
                                    <div class="dynamic-tier-card" data-tool="${tool.id}" data-toolname="${tool.title[lang]}" style="background:${bg};border:${border};border-radius:14px;padding:18px 20px;cursor:pointer;transition:all 0.3s;position:relative;overflow:hidden;">
                                        ${isBest}
                                        <div style="display:flex;justify-content:space-between;align-items:center;">
                                            <div>
                                                <div style="color:${tool.best ? 'var(--accent-gold)' : '#fff'};font-weight:700;font-size:1rem;margin-bottom:4px;">${tool.icon} ${tool.title[lang]}</div>
                                                <div style="color:#bbb;font-size:0.85rem;">${tool.desc[lang]}</div>
                                            </div>
                                            <div style="color:var(--accent-gold);font-weight:800;font-size:1.1rem;white-space:nowrap;">${tool.price}</div>
                                        </div>
                                    </div>
                            `;
                    });
                    html += `</div></div>`;
                    resultArea.innerHTML += html;

                    // Wire up universal clicks
                    resultArea.querySelectorAll('.dynamic-tier-card').forEach(card => {
                        card.addEventListener('mouseenter', () => card.style.transform = 'translateY(-2px)');
                        card.addEventListener('mouseleave', () => card.style.transform = '');
                        card.addEventListener('click', async () => {
                            const toolId = card.getAttribute('data-tool');
                            const toolName = card.getAttribute('data-toolname');

                            const isMaster = window.currentUser && window.currentUser.email === 'oskyoo@naver.com';
                            if (isMaster || (typeof window.purchasedTools !== 'undefined' && window.purchasedTools.has(toolId))) {
                                let q = "General deep analysis please.";
                                if (toolId && toolId.endsWith('_custom')) {
                                    const userQ = prompt(`[${toolName}]\n상담하실 구체적인 질문 내용을 작성해 주세요:\n(분석이 시작됩니다.)`);
                                    if (!userQ) return;
                                    q = userQ;
                                }
                                document.getElementById('premium-modal').style.display = 'none';
                                executePremiumAnalysis(toolId, toolName, q);
                                return;
                            }

                            // Extract price as integer
                            const priceStr = tool.price.replace(/[^0-9]/g, '');
                            window.currentPaymentPriceKRW = parseInt(priceStr, 10);
                            window.currentPaymentToolId = toolId;
                            window.currentPaymentToolName = toolName;

                            // Show Modal UI depending on Language
                            document.getElementById('modal-tool-name').innerText = toolName;
                            const premiumModal = document.getElementById('premium-modal');
                            const krPanel = document.getElementById('payment-options-kr');
                            const globalPanel = document.getElementById('payment-options-global');

                            const lang = window.currentLanguage || 'ko';
                            if (lang === 'ko') {
                                krPanel.style.display = 'flex';
                                globalPanel.style.display = 'none';
                            } else {
                                krPanel.style.display = 'none';
                                globalPanel.style.display = 'flex';
                                renderPayPalButton(); // Refresh PayPal button
                            }

                            premiumModal.style.display = 'flex';
                        });
                    });
                }

            } catch (err) {
                loader.style.display = 'none';
                resultArea.style.display = 'block';
                resultArea.innerHTML = "<p style='color:red;'>연결에 실패했습니다. 다시 시도해 주세요.</p>";
            }
        });
    }

    // Name Reading dedicated submit button
    const nameSubmitBtn = document.getElementById('name-submit-btn');
    if (nameSubmitBtn) {
        nameSubmitBtn.addEventListener('click', async () => {
            const nameKorean = document.getElementById('name-korean').value.trim();
            if (!nameKorean) {
                alert('한글 이름을 입력해 주세요.');
                return;
            }
            const nameHanja = document.getElementById('name-hanja').value || '';
            const nameBirthdate = document.getElementById('name-birthdate').value || '';

            // Hide extra input area, show loader
            document.getElementById('oracle-extra-input').style.display = 'none';
            loader.style.display = 'flex';

            try {
                const response = await fetch('/api/fortune/free', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        name: nameKorean,
                        birthDate: nameBirthdate || 'Unknown',
                        calendar: 'solar',
                        gender: 'unknown',
                        oracle: 'name',
                        nameKorean,
                        nameHanja,
                        nameBirthdate,
                        language: window.currentLanguage || 'en'
                    })
                });
                const data = await response.json();
                loader.style.display = 'none';
                resultArea.style.display = 'block';
                resultArea.innerHTML = `
                    <h3 style="color:var(--accent-gold);margin-bottom:20px;font-size:1.8rem;">${data.title || nameKorean + ' 이름풀이'}</h3>
                    <div style="color:#eee;font-size:1.05rem;line-height:1.9;text-align:left;white-space:pre-wrap;margin-bottom:30px;">${data.fortune}</div>
                    <div style="border-top:1px dashed rgba(255,215,0,0.3);padding-top:28px;margin-top:10px;">
                        <p style="color:var(--accent-gold);font-size:1.05rem;font-weight:700;margin-bottom:18px;text-align:center;">🔮 심층 이름풀이 서비스</p>
                        <div style="display:flex;flex-direction:column;gap:14px;">
                            <div class="name-tier-card" data-tool="name_hanja_analysis" style="background:rgba(255,215,0,0.06);border:1px solid rgba(255,215,0,0.35);border-radius:14px;padding:18px 20px;cursor:pointer;transition:all 0.3s;">
                                <div style="display:flex;justify-content:space-between;align-items:center;">
                                    <div>
                                        <div style="color:#fff;font-weight:700;font-size:1rem;margin-bottom:4px;">🀄 획수 심층분석</div>
                                        <div style="color:#bbb;font-size:0.85rem;">한자 획수 + 81수리 길흉 판정</div>
                                    </div>
                                    <div style="color:var(--accent-gold);font-weight:800;font-size:1.1rem;white-space:nowrap;">₩2,900</div>
                                </div>
                            </div>
                            <div class="name-tier-card" data-tool="name_saju_harmony" style="background:rgba(255,215,0,0.06);border:1px solid rgba(255,215,0,0.5);border-radius:14px;padding:18px 20px;cursor:pointer;transition:all 0.3s;">
                                <div style="display:flex;justify-content:space-between;align-items:center;">
                                    <div>
                                        <div style="color:#fff;font-weight:700;font-size:1rem;margin-bottom:4px;">☯️ 이름과 사주 조화 분석</div>
                                        <div style="color:#bbb;font-size:0.85rem;">생년월일 오행 vs 이름 오행 충·합 분석</div>
                                    </div>
                                    <div style="color:var(--accent-gold);font-weight:800;font-size:1.1rem;white-space:nowrap;">₩6,900</div>
                                </div>
                            </div>
                            <div class="name-tier-card" data-tool="name_change" style="background:linear-gradient(135deg,rgba(255,215,0,0.12),rgba(255,150,0,0.08));border:2px solid var(--accent-gold);border-radius:14px;padding:18px 20px;cursor:pointer;transition:all 0.3s;position:relative;overflow:hidden;">
                                <div style="position:absolute;top:0;right:0;background:var(--accent-gold);color:#111;font-size:0.7rem;font-weight:900;padding:3px 10px;border-radius:0 14px 0 10px;">BEST</div>
                                <div style="display:flex;justify-content:space-between;align-items:center;">
                                    <div>
                                        <div style="color:var(--accent-gold);font-weight:700;font-size:1rem;margin-bottom:4px;">💎 개명 전문 상담</div>
                                        <div style="color:#bbb;font-size:0.85rem;">현재 이름 진단 + 개명 후보안 3가지 + 운 예측</div>
                                    </div>
                                    <div style="color:var(--accent-gold);font-weight:800;font-size:1.1rem;white-space:nowrap;">₩14,900</div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;

                // Wire up tier card clicks
                resultArea.querySelectorAll('.name-tier-card').forEach(card => {
                    card.addEventListener('mouseenter', () => card.style.transform = 'translateY(-2px)');
                    card.addEventListener('mouseleave', () => card.style.transform = '');
                    card.addEventListener('click', async () => {
                        const toolId = card.getAttribute('data-tool');
                        const toolName = card.getAttribute('data-toolname');

                        const isMaster = window.currentUser && window.currentUser.email === 'oskyoo@naver.com';
                        if (isMaster || (typeof window.purchasedTools !== 'undefined' && window.purchasedTools.has(toolId))) {
                            let q = "General deep analysis please.";
                            if (toolId && toolId.endsWith('_custom')) {
                                const userQ = prompt(`[${toolName}]\n상담하실 구체적인 질문 내용을 작성해 주세요:\n(분석이 시작됩니다.)`);
                                if (!userQ) return;
                                q = userQ;
                            }
                            document.getElementById('premium-modal').style.display = 'none';
                            executePremiumAnalysis(toolId, toolName, q);
                            return;
                        }

                        // Extract price as integer
                        const priceStr = tool.price.replace(/[^0-9]/g, '');
                        window.currentPaymentPriceKRW = parseInt(priceStr, 10);
                        window.currentPaymentToolId = toolId;
                        window.currentPaymentToolName = toolName;

                        // Show Modal UI depending on Language
                        document.getElementById('modal-tool-name').innerText = toolName;
                        const premiumModal = document.getElementById('premium-modal');
                        const krPanel = document.getElementById('payment-options-kr');
                        const globalPanel = document.getElementById('payment-options-global');

                        const lang = window.currentLanguage || 'ko';
                        if (lang === 'ko') {
                            krPanel.style.display = 'flex';
                            globalPanel.style.display = 'none';
                        } else {
                            krPanel.style.display = 'none';
                            globalPanel.style.display = 'flex';
                            renderPayPalButton(); // Refresh PayPal button
                        }

                        premiumModal.style.display = 'flex';
                    });
                });
            } catch (error) {
                console.error("Cosmic interference:", error);
                loader.style.display = 'none';
                resultArea.style.display = 'block';
                resultArea.innerHTML = "<p style='color: red;'>The cosmic connection was interrupted. Please try again.</p>";
            }
        });
    }



    // Main Form Submit (Restored)
    const submitBtn = document.getElementById('btn-submit');
    if (submitBtn) {
        submitBtn.addEventListener('click', async (e) => {
            e.preventDefault();

            // Validate form
            const name = document.getElementById('user-name').value.trim();
            if (!name) {
                alert('이름을 입력해 주세요.');
                return;
            }

            const year = document.getElementById('birth-year').value;
            const month = document.getElementById('birth-month').value;
            const day = document.getElementById('birth-day').value;
            const calendar = document.getElementById('birth-calendar').value;
            const gender = document.getElementById('gender').value;
            const ampm = document.getElementById('birth-ampm').value;
            const hour = document.getElementById('birth-hour').value;
            const minute = document.getElementById('birth-minute').value;

            const birthDate = `${year}-${month}-${day}`;

            let birthTimeInfo = "Unknown time";
            if (hour) {
                let minuteStr = minute ? minute : "00";
                birthTimeInfo = `${hour}:${minuteStr} ${ampm}`;
            }

            const fullBirthInfo = `${birthDate} (Time: ${birthTimeInfo})`;

            let palmHand = null;
            if (window.currentOracle === 'palmistry') {
                const handChecked = document.querySelector('input[name="palm_hand"]:checked');
                if (handChecked) palmHand = handChecked.value;
            }

            document.getElementById('oracle-extra-input').style.display = 'none';
            if (document.getElementById('fortune-form')) {
                document.getElementById('fortune-form').style.display = 'none';
            }
            const loader = document.getElementById('loader');
            const resultArea = document.getElementById('result-text');
            loader.style.display = 'flex';

            try {
                const response = await fetch('/api/fortune/free', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        name,
                        birthDate: fullBirthInfo,
                        calendar,
                        gender,
                        oracle: window.currentOracle,
                        imageData: window.uploadedImageBase64 || null,
                        palmHand: palmHand,
                        language: window.currentLanguage || 'en'
                    })
                });

                const data = await response.json();
                loader.style.display = 'none';
                resultArea.style.display = 'block';

                let parsedFortune = data.fortune
                    .replace(/^### (.*$)/gim, '<h3 style="color:var(--accent-gold);margin-top:20px;margin-bottom:10px;">$1</h3>')
                    .replace(/^## (.*$)/gim, '<h2 style="color:var(--accent-gold);margin-top:20px;margin-bottom:10px;">$1</h2>')
                    .replace(/^# (.*$)/gim, '<h1 style="color:var(--accent-gold);margin-top:20px;margin-bottom:10px;">$1</h1>')
                    .replace(/\*\*(.*?)\*\*/g, '<strong style="color:var(--accent-gold);">$1</strong>')
                    .replace(/\*(.*?)\*/g, '<em>$1</em>')
                    .replace(/^\* (.*$)/gim, '<li style="margin-left:20px;margin-bottom:8px;">$1</li>')
                    .replace(/^- (.*$)/gim, '<li style="margin-left:20px;margin-bottom:8px;">$1</li>');

                parsedFortune = parsedFortune.replace(/(<li.*?>.*<\/li>)/g, '<ul style="margin-bottom:20px;">$1</ul>').replace(/<\/ul>\n<ul style="margin-bottom:20px;">/g, '\n');

                resultArea.innerHTML = `
                    <h3 style="color: var(--accent-gold); margin-bottom: 20px; font-size: 1.8rem;">${data.title}</h3>
                    <div style="color: #eee; font-size: 1.1rem; line-height: 1.8; text-align: left; white-space: pre-wrap; margin-bottom: 30px;">${parsedFortune}</div>
                `;

                if (typeof saveReading === 'function') {
                    saveReading(window.currentOracle || 'saju', data.title, data.fortune);
                }

                setTimeout(() => {
                    resultArea.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 100);

                const tiers = typeof oracleTools !== 'undefined' ? (oracleTools[window.currentOracle] || []) : [];
                if (tiers.length > 0) {
                    const lang = window.currentLanguage || 'ko';
                    const secTitle = lang === 'ko' ? '🔮 심층 분석 서비스' : '🔮 Deep Analysis Services';
                    let html = `
                        <div style="border-top:1px dashed rgba(255,215,0,0.3);padding-top:28px;margin-top:10px;">
                            <p style="color:var(--accent-gold);font-size:1.05rem;font-weight:700;margin-bottom:18px;text-align:center;">${secTitle}</p>
                            <div style="display:flex;flex-direction:column;gap:14px;">
                    `;

                    tiers.forEach(tool => {
                        const isBest = tool.best ? `<div style="position:absolute;top:0;right:0;background:var(--accent-gold);color:#111;font-size:0.7rem;font-weight:900;padding:3px 10px;border-radius:0 14px 0 10px;">BEST</div>` : '';
                        const bg = tool.best ? 'linear-gradient(135deg,rgba(255,215,0,0.12),rgba(255,150,0,0.08))' : 'rgba(255,215,0,0.06)';
                        const border = tool.best ? '2px solid var(--accent-gold)' : '1px solid rgba(255,215,0,0.4)';
                        html += `
                                <div class="dynamic-tier-card" data-tool="${tool.id}" data-toolname="${tool.title[lang]}" style="background:${bg};border:${border};border-radius:14px;padding:18px 20px;cursor:pointer;transition:all 0.3s;position:relative;overflow:hidden;">
                                    ${isBest}
                                    <div style="display:flex;justify-content:space-between;align-items:center;">
                                        <div>
                                            <div style="color:${tool.best ? 'var(--accent-gold)' : '#fff'};font-weight:700;font-size:1rem;margin-bottom:4px;">${tool.icon} ${tool.title[lang]}</div>
                                            <div style="color:#bbb;font-size:0.85rem;">${tool.desc[lang]}</div>
                                        </div>
                                        <div style="color:var(--accent-gold);font-weight:800;font-size:1.1rem;white-space:nowrap;">${tool.price}</div>
                                    </div>
                                </div>
                        `;
                    });
                    html += `</div></div>`;
                    resultArea.innerHTML += html;

                    resultArea.querySelectorAll('.dynamic-tier-card').forEach(card => {
                        card.addEventListener('mouseenter', () => card.style.transform = 'translateY(-2px)');
                        card.addEventListener('mouseleave', () => card.style.transform = '');
                        card.addEventListener('click', () => {
                            const toolId = card.getAttribute('data-tool');
                            const toolName = card.getAttribute('data-toolname');

                            const isMaster = window.currentUser && window.currentUser.email === 'oskyoo@naver.com';
                            if (isMaster || (typeof window.purchasedTools !== 'undefined' && window.purchasedTools.has(toolId))) {
                                let q = "General deep analysis please.";
                                if (toolId && toolId.endsWith('_custom')) {
                                    const userQ = prompt(`[${toolName}]\n상담하실 구체적인 질문 내용을 작성해 주세요:\n(분석이 시작됩니다.)`);
                                    if (!userQ) return;
                                    q = userQ;
                                }
                                document.getElementById('premium-modal').style.display = 'none';
                                executePremiumAnalysis(toolId, toolName, q);
                                return;
                            }

                            const priceStr = card.querySelector('div[style*="font-size:1.1rem"]').innerText.replace(/[^0-9]/g, '');
                            window.currentPaymentPriceKRW = parseInt(priceStr, 10);
                            window.currentPaymentToolId = toolId;
                            window.currentPaymentToolName = toolName;

                            document.getElementById('modal-tool-name').innerText = toolName;
                            const premiumModal = document.getElementById('premium-modal');
                            const krPanel = document.getElementById('payment-options-kr');
                            const globalPanel = document.getElementById('payment-options-global');

                            const localeLang = window.currentLanguage || 'ko';
                            if (localeLang === 'ko') {
                                krPanel.style.display = 'flex';
                                globalPanel.style.display = 'none';
                            } else {
                                krPanel.style.display = 'none';
                                globalPanel.style.display = 'flex';
                                if (typeof renderPayPalButton === 'function') renderPayPalButton();
                            }

                            premiumModal.style.display = 'flex';
                        });
                    });
                }

            } catch (error) {
                console.error("Cosmic interference:", error);
                loader.style.display = 'none';
                resultArea.style.display = 'block';
                resultArea.innerHTML = "<p style='color: red;'>The cosmic connection was interrupted. Please try again.</p>";
            }
        });
    }

    // Tool Library Logic
    const premiumModal = document.getElementById('premium-modal');
    const closeModalBtn = document.getElementById('close-modal');
    const paymentLoader = document.getElementById('payment-loader');
    const toolGrid = document.querySelector('.tool-grid');
    let selectedToolId = null;


    // Track which tool IDs the user has purchased
    window.purchasedTools = new Set();

    window.loadPurchases = async function () {
        try {
            const res = await fetch('/api/user/purchases', { credentials: 'include' });
            const d = await res.json();
            window.purchasedTools = new Set(d.purchased || []);
            renderToolGrid(); // Refresh UI after loading purchases
        } catch { window.purchasedTools = new Set(); }
    };

    // FETCH PURCHASES ON LOAD
    window.loadPurchases();

    function renderToolGrid() {
        if (!toolGrid) return;
        toolGrid.innerHTML = '';
        const lang = window.currentLanguage || 'ko';
        const oracle = window.currentOracle || 'saju';
        const tiers = oracleTools[oracle] || oracleTools['saju'];
        const isLoggedIn = !!window.currentUser;

        // Compute non-member price (2x member price, rounded to nice X,900 number)
        function guestPrice(memberPriceStr) {
            const num = parseInt(memberPriceStr.replace(/[₩,]/g, ''));
            const raw = num * 2;
            const rounded = Math.ceil(raw / 1000) * 1000 - 100;
            return '₩' + rounded.toLocaleString();
        }

        tiers.forEach(tool => {
            const isMaster = window.currentUser && window.currentUser.email === 'oskyoo@naver.com';
            const owned = isMaster || window.purchasedTools.has(tool.id);
            const mPrice = tool.price;        // member price
            const gPrice = guestPrice(mPrice); // guest price (~2x)
            const card = document.createElement('div');
            card.className = 'tool-card' + (owned ? ' unlocked' : '');
            card.style.cssText = 'position:relative;overflow:hidden;';

            // Top-right badge
            if (owned) {
                card.innerHTML = `<div style="position:absolute;top:0;right:0;background:#27ae60;color:#fff;font-size:0.65rem;font-weight:900;padding:2px 8px;border-radius:0 10px 0 8px;">✓ 보유</div>`;
            } else if (isLoggedIn) {
                card.innerHTML = `<div style="position:absolute;top:0;right:0;background:linear-gradient(135deg,#27ae60,#1e8449);color:#fff;font-size:0.65rem;font-weight:900;padding:2px 8px;border-radius:0 10px 0 8px;">회원 할인가</div>`;
            } else if (tool.best) {
                card.innerHTML = `<div style="position:absolute;top:0;right:0;background:var(--accent-gold);color:#111;font-size:0.65rem;font-weight:900;padding:2px 8px;border-radius:0 10px 0 8px;">BEST</div>`;
            }

            // Price display block
            let priceHTML;
            if (owned) {
                priceHTML = `<div class="tool-lock">🔓 구매 완료</div>`;
            } else if (isLoggedIn) {
                // Member: show member price + crossed-out guest price
                priceHTML = `
                    <div style="display:flex;align-items:center;justify-content:center;gap:8px;flex-wrap:wrap;">
                        <span style="font-size:0.8rem;color:#999;text-decoration:line-through;">${gPrice}</span>
                        <span class="tool-lock" style="background:rgba(39,174,96,0.15);border-color:#27ae60;color:#4caf50;">🔓 ${mPrice}</span>
                    </div>`;
            } else {
                // Guest: show full guest price + savings nudge
                priceHTML = `
                    <div style="display:flex;flex-direction:column;align-items:center;gap:4px;">
                        <div class="tool-lock">🔒 ${gPrice}</div>
                        <div style="font-size:0.7rem;color:#d4af37;font-weight:600;background:rgba(212,175,55,0.12);padding:2px 8px;border-radius:20px;border:1px solid rgba(212,175,55,0.25);">
                            ✨ 회원 가입시 ${mPrice} (50% 절약)
                        </div>
                    </div>`;
            }

            card.innerHTML += `
                <div class="tool-icon">${tool.icon}</div>
                <div class="tool-title">${tool.title[lang] || tool.title['en']}</div>
                <div style="font-size:0.75rem;color:#aaa;margin:3px 0 8px;">${tool.desc[lang] || tool.desc['en']}</div>
                ${priceHTML}
            `;

            card.addEventListener('click', () => {
                selectedToolId = tool.id;
                const displayPrice = isLoggedIn ? mPrice : gPrice;
                const purchaseBtn = document.getElementById('btn-purchase-tool');
                if (purchaseBtn) purchaseBtn.textContent = `${displayPrice}에 잠금 해제`;

                if (owned) {
                    premiumModal.style.display = 'none';
                    runToolAnalysis(tool.id);
                } else if (tool.isPast) {
                    // Show age-range picker first
                    document.getElementById('age-range-modal').style.display = 'flex';
                    document.getElementById('age-range-tool-id').value = tool.id;
                    document.getElementById('age-range-title').textContent = tool.title[lang] || tool.title['en'];
                    window._pendingPastTool = tool;
                } else {
                    document.getElementById('modal-tool-name').textContent = tool.title[lang] || tool.title['en'];
                    premiumModal.style.display = 'flex';
                }
            });
            toolGrid.appendChild(card);
        });
    }

    async function runToolAnalysis(toolId) {
        const name = document.getElementById('user-name')?.value || '';
        const year = document.getElementById('birth-year')?.value || '';
        const month = document.getElementById('birth-month')?.value || '';
        const day = document.getElementById('birth-day')?.value || '';
        const calendar = document.getElementById('birth-calendar')?.value || 'solar';
        const gender = document.getElementById('gender')?.value || '';
        const ampm = document.getElementById('birth-ampm')?.value || '';
        const hour = document.getElementById('birth-hour')?.value || '';
        const minute = document.getElementById('birth-minute')?.value || '';
        const birthDate = `${year}-${month}-${day}`;
        let birthTimeInfo = 'Unknown time';
        if (hour) birthTimeInfo = `${hour}:${minute || '00'} ${ampm}`;
        const fullBirthInfo = `${birthDate} (Time: ${birthTimeInfo})`;

        let drawnCardsParam = null;

        if (window.currentOracle === 'tarot') {
            let numCards = toolId === 'tarot_3card' ? 3 : (toolId === 'tarot_celtic' ? 10 : 5);
            drawnCardsParam = await drawTarotCards(numCards);
        } else {
            document.getElementById('tarot-display-area').style.display = 'none';
        }

        if (window.currentOracle !== 'tarot') {
            loader.style.display = 'flex';
        }

        loader.style.display = 'flex';
        try {
            const response = await fetch('/api/fortune/tool', {
                method: 'POST', credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify((() => {
                    const payload = {
                        name, birthDate: fullBirthInfo, calendar, gender,
                        tool_id: toolId, oracle: window.currentOracle,
                        language: window.currentLanguage || 'en',
                        drawn_cards: drawnCardsParam
                    };
                    if (window._pendingCustomQ) {
                        payload.intention = window._pendingCustomQ;
                        window._pendingCustomQ = null;
                    }
                    return payload;
                })())
            });
            const data = await response.json();
            loader.style.display = 'none';

            // Simple Markdown Parser
            let parsedFortune = data.fortune
                .replace(/^### (.*$)/gim, '<h3 style="color:var(--accent-gold);margin-top:20px;margin-bottom:10px;">$1</h3>')
                .replace(/^## (.*$)/gim, '<h2 style="color:var(--accent-gold);margin-top:25px;margin-bottom:15px;">$1</h2>')
                .replace(/^# (.*$)/gim, '<h1 style="color:var(--accent-gold);margin-top:30px;margin-bottom:20px;">$1</h1>')
                .replace(/\*\*(.*?)\*\*/g, '<strong style="color:var(--accent-gold);">$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/^\* (.*$)/gim, '<li style="margin-left:20px;margin-bottom:8px;">$1</li>')
                .replace(/^- (.*$)/gim, '<li style="margin-left:20px;margin-bottom:8px;">$1</li>');

            // Wrap lists in <ul> if needed (simplified approach)
            parsedFortune = parsedFortune.replace(/(<li.*?>.*<\/li>)/g, '<ul>$1</ul>').replace(/<\/ul>\n<ul>/g, '\n');

            resultArea.innerHTML = `
                <div style="padding-top:10px;">
                    <h2 style="color:var(--accent-gold);margin-bottom:20px;font-size:1.6rem;text-align:center;">${data.title}</h2>
                    <div style="color:#fff;font-size:1.05rem;line-height:1.8;text-align:left;white-space:pre-wrap;background:rgba(0,0,0,0.3);padding:20px;border-radius:10px;border:1px solid rgba(212,175,55,0.2);">${parsedFortune}</div>
                </div>
            `;

            // Auto-scroll to result
            setTimeout(() => {
                resultArea.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 100);
        } catch {
            loader.style.display = 'none';
        }
    }

    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', () => {
            premiumModal.style.display = 'none';
        });
    }

    if (premiumModal) {
        premiumModal.addEventListener('click', (e) => {
            if (e.target === premiumModal) {
                premiumModal.style.display = 'none';
            }
        });
    }

    const btnPurchase = document.getElementById('btn-purchase-tool');
    if (btnPurchase) {
        btnPurchase.addEventListener('click', async () => {
            if (!selectedToolId) return;

            premiumModal.style.display = 'none';
            paymentLoader.style.display = 'flex';

            // Simulate payment gateway delay
            await new Promise(resolve => setTimeout(resolve, 2000));
            paymentLoader.style.display = 'none';

            // Record purchase if user is logged in
            if (window.currentUser) {
                await fetch('/api/user/purchase', {
                    method: 'POST', credentials: 'include',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ oracle: window.currentOracle, tool_id: selectedToolId })
                }).catch(() => { });
                window.purchasedTools.add(selectedToolId);
                renderToolGrid(); // re-render to show 🔓
            }

            // Run the tool analysis
            await runToolAnalysis(selectedToolId);
        });
    }

    async function drawTarotCards(numCards) {
        const TAROT_DECK = [
            { id: 0, name: "The Fool", nameKo: "바보 (0. The Fool)", icon: "🃏" }, { id: 1, name: "The Magician", nameKo: "마법사 (I. The Magician)", icon: "🪄" },
            { id: 2, name: "The High Priestess", nameKo: "여사제 (II. The High Priestess)", icon: "📜" }, { id: 3, name: "The Empress", nameKo: "여황제 (III. The Empress)", icon: "👑" },
            { id: 4, name: "The Emperor", nameKo: "황제 (IV. The Emperor)", icon: "🪑" }, { id: 5, name: "The Hierophant", nameKo: "교황 (V. The Hierophant)", icon: "🕍" },
            { id: 6, name: "The Lovers", nameKo: "연인 (VI. The Lovers)", icon: "💑" }, { id: 7, name: "The Chariot", nameKo: "전차 (VII. The Chariot)", icon: "🛷" },
            { id: 8, name: "Strength", nameKo: "힘 (VIII. Strength)", icon: "🦁" }, { id: 9, name: "The Hermit", nameKo: "은둔자 (IX. The Hermit)", icon: "🕯️" },
            { id: 10, name: "Wheel of Fortune", nameKo: "운명의 수레바퀴 (X. Wheel of Fortune)", icon: "🎡" }, { id: 11, name: "Justice", nameKo: "정의 (XI. Justice)", icon: "⚖️" },
            { id: 12, name: "The Hanged Man", nameKo: "매달린 사람 (XII. The Hanged Man)", icon: "🧗" }, { id: 13, name: "Death", nameKo: "죽음 (XIII. Death)", icon: "💀" },
            { id: 14, name: "Temperance", nameKo: "절제 (XIV. Temperance)", icon: "🍷" }, { id: 15, name: "The Devil", nameKo: "악마 (XV. The Devil)", icon: "👿" },
            { id: 16, name: "The Tower", nameKo: "탑 (XVI. The Tower)", icon: "🌩️" }, { id: 17, name: "The Star", nameKo: "별 (XVII. The Star)", icon: "⭐" },
            { id: 18, name: "The Moon", nameKo: "달 (XVIII. The Moon)", icon: "🌙" }, { id: 19, name: "The Sun", nameKo: "태양 (XIX. The Sun)", icon: "☀️" },
            { id: 20, name: "Judgement", nameKo: "심판 (XX. Judgement)", icon: "📯" }, { id: 21, name: "The World", nameKo: "세계 (XXI. The World)", icon: "🌍" }
        ];

        const lang = window.currentLanguage || 'en';
        const tarotArea = document.getElementById('tarot-display-area');
        const tarotContainer = document.getElementById('tarot-cards-container');
        const tarotTitle = document.getElementById('tarot-draw-title');

        tarotTitle.textContent = lang === 'ko' ? `운명의 카드를 섞었습니다. ${numCards}장을 직접 선택해주세요.` : `Please manually select ${numCards} cards.`;
        tarotContainer.innerHTML = '';
        tarotArea.style.display = 'block';

        tarotArea.scrollIntoView({ behavior: 'smooth', block: 'center' });

        return new Promise((resolve) => {
            let drawn = [];
            let pickedCount = 0;
            let deckCopy = [...TAROT_DECK];

            // Render all 22 cards face-down
            for (let i = 0; i < 22; i++) {
                const cardEl = document.createElement('div');
                cardEl.className = 'tarot-card appear';
                cardEl.style.animationDelay = `${(i % 5) * 0.05}s`;
                cardEl.style.cursor = 'pointer';
                cardEl.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
                cardEl.style.transform = 'scale(0.85)'; // Slightly smaller to fit 22 cards
                cardEl.style.margin = '4px';

                const inner = document.createElement('div');
                inner.className = 'tarot-card-inner';

                const back = document.createElement('div');
                back.className = 'tarot-card-back';
                back.style.backgroundImage = "url('/static/images/tarot/card_back.png')";
                back.style.backgroundSize = 'cover';
                back.style.backgroundPosition = 'center';
                back.style.border = '1px solid rgba(255,215,0,0.3)';

                const front = document.createElement('div');
                front.className = 'tarot-card-front';
                front.style.border = '1px solid rgba(255,215,0,0.6)';

                inner.appendChild(back);
                inner.appendChild(front);
                cardEl.appendChild(inner);
                tarotContainer.appendChild(cardEl);

                // Attach click listener for manual picking
                cardEl.addEventListener('click', function onClick() {
                    // Ignore if already flipped or we reached the required amount
                    if (cardEl.classList.contains('flipped') || pickedCount >= numCards) return;

                    // Assign random card properties
                    let randIdx = Math.floor(Math.random() * deckCopy.length);
                    let card = deckCopy.splice(randIdx, 1)[0];
                    let isReversed = Math.random() > 0.7; // 30% chance reversed
                    let drawnCard = { ...card, isReversed };
                    drawn.push(drawnCard);

                    // Populate the front UI with image
                    front.style.backgroundImage = `url('/static/images/tarot/tarot_${drawnCard.id}.jpg')`;
                    front.style.backgroundSize = 'cover';
                    front.style.backgroundPosition = 'center';

                    front.innerHTML = `
                        <div style="position:absolute;bottom:0;left:0;right:0;background:rgba(0,0,0,0.85);backdrop-filter:blur(6px);padding:8px 4px;text-align:center;border-top:1px solid rgba(255,215,0,0.4);">
                            <div style="color:var(--accent-gold);font-weight:700;font-size:0.75rem;">${lang === 'ko' ? drawnCard.nameKo : drawnCard.name}</div>
                            ${drawnCard.isReversed ? `<div style="font-size:0.65rem; color:#ff6b6b; margin-top:2px;">REVERSED (역방향)</div>` : `<div style="font-size:0.65rem; color:#4caf50; margin-top:2px;">UPRIGHT (정방향)</div>`}
                        </div>
                    `;

                    // Flip animation
                    cardEl.style.pointerEvents = 'none'; // Prevent further clicks
                    cardEl.style.transform = 'scale(1)'; // Enlarge picked card back to normal
                    if (isReversed) {
                        cardEl.classList.add('flipped', 'reversed');
                    } else {
                        cardEl.classList.add('flipped');
                    }

                    pickedCount++;

                    // Update Title Text
                    if (pickedCount < numCards) {
                        tarotTitle.textContent = lang === 'ko' ? `남은 선택: ${numCards - pickedCount}장` : `Remaining: ${numCards - pickedCount}`;
                    } else {
                        tarotTitle.textContent = lang === 'ko' ? "우주의 뜻을 읽어내는 중입니다..." : "Interpreting the cards...";

                        // Hide unpicked cards
                        const unpickedCards = tarotContainer.querySelectorAll('.tarot-card:not(.flipped)');
                        unpickedCards.forEach(c => c.style.opacity = '0');

                        setTimeout(() => {
                            unpickedCards.forEach(c => c.style.display = 'none');
                        }, 500);

                        // Give user time to see their final drawn card before resolving
                        setTimeout(() => {
                            resolve(drawn.map(c => `${c.name} (${c.isReversed ? 'Reversed' : 'Upright'})`).join(', '));
                        }, 1200);
                    }
                }, { once: true });
            }
        });
    }

});


// ======================================
// HYBRID PAYMENT GATEWAY INTEGRATION
// ======================================

// [Phase 2] PortOne KRW Payment (Credit, Kakao, Mobile)
async function requestPortOnePayment(method) {
    if (!window.currentPaymentToolId || !window.currentPaymentPriceKRW) return;

    // The user will insert their actual PortOne Store ID here
    const STORE_ID = 'STORE-ID-PLACEHOLDER';
    const paymentId = `order_${new Date().getTime()}`;

    // Show User Question Prompt first ONLY if it's a custom question tool
    let question = "Please provide a general deep analysis.";
    if (window.currentPaymentToolId && window.currentPaymentToolId.endsWith('_custom')) {
        const userQ = prompt(`[${window.currentPaymentToolName}]\n상담하실 구체적인 질문 내용을 작성해 주세요:\n(결제가 완료되면 바로 분석이 시작됩니다.)`);
        if (!userQ) return;
        question = userQ;
    }

    try {
        const response = await PortOne.requestPayment({
            storeId: STORE_ID,
            channelKey: 'CHANNEL-KEY-PLACEHOLDER',
            paymentId: paymentId,
            orderName: window.currentPaymentToolName,
            totalAmount: window.currentPaymentPriceKRW,
            currency: 'CURRENCY_KRW',
            payMethod: method, // 'CARD', 'EASY_PAY', or 'MOBILE'
        });

        if (response.code != null) {
            // Error handling
            alert(`결제 실패: ${response.message}`);
            return;
        }

        // 🟢 PAYMENT SUCCESS
        document.getElementById('premium-modal').style.display = 'none';
        executePremiumAnalysis(window.currentPaymentToolId, window.currentPaymentToolName, question);

    } catch (error) {
        console.error("PortOne SDK Error:", error);
        alert("결제 모듈 로드 중 오류가 발생했습니다.");
    }
}

// [Phase 3] PayPal Global USD Payment
function renderPayPalButton() {
    const container = document.getElementById('paypal-button-container');
    container.innerHTML = ''; // Clear previous button

    // Roughly convert KRW to USD (Assume 1,300 KRW = 1 USD)
    const usdPrice = (window.currentPaymentPriceKRW / 1300).toFixed(2);

    if (typeof paypal !== 'undefined') {
        paypal.Buttons({
            createOrder: function (data, actions) {
                return actions.order.create({
                    purchase_units: [{
                        description: window.currentPaymentToolName,
                        amount: { value: usdPrice }
                    }]
                });
            },
            onApprove: function (data, actions) {
                return actions.order.capture().then(function (details) {
                    // 🟢 PAYMENT SUCCESS
                    let question = "General deep analysis please.";
                    if (window.currentPaymentToolId && window.currentPaymentToolId.endsWith('_custom')) {
                        question = prompt(`[${window.currentPaymentToolName}]\nPlease write your specific question for the AI:\n(Analysis starts immediately)`) || question;
                    }
                    document.getElementById('premium-modal').style.display = 'none';
                    executePremiumAnalysis(window.currentPaymentToolId, window.currentPaymentToolName, question);
                });
            },
            onError: function (err) {
                alert('PayPal Transaction failed. Please try again.');
            }
        }).render('#paypal-button-container');
    } else {
        container.innerHTML = '<p style="color:red;font-size:0.8rem;">PayPal SDK not loaded yet.</p>';
    }
}

// Commmon Execution Function for after payment
async function executePremiumAnalysis(toolId, toolName, question) {
    const resultArea = document.getElementById('result-area');
    const loader = document.getElementById('payment-loader');

    resultArea.style.display = 'none';
    loader.style.display = 'flex';

    // Fetch existing user info
    const name = document.getElementById('user-name').value;
    const year = document.getElementById('birth-year').value;
    const month = document.getElementById('birth-month').value;
    const day = document.getElementById('birth-day').value;
    const calendar = document.getElementById('birth-calendar').value;
    const gender = document.getElementById('gender').value;
    const fullBirthInfo = `${year}-${month}-${day}`;

    try {
        const toolRes = await fetch('/api/fortune/tool', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name,
                birthDate: fullBirthInfo,
                calendar,
                gender,
                oracle: window.currentOracle,
                tool_id: toolId,
                intention: question,
                language: window.currentLanguage || 'en'
            })
        });
        const toolData = await toolRes.json();
        loader.style.display = 'none';
        resultArea.style.display = 'block';

        // Append the deep analysis result
        resultArea.innerHTML += `
            <div style="margin-top:30px;padding-top:24px;border-top:1px dashed rgba(255,215,0,0.3);">
                <h3 style="color:var(--accent-gold);margin-bottom:16px;font-size:1.5rem;">${toolData.title || toolName}</h3>
                <div style="color:#eee;font-size:1.05rem;line-height:1.9;white-space:pre-wrap;background:rgba(0,0,0,0.3);padding:20px;border-radius:12px;border:1px solid rgba(212,175,55,0.2);">${toolData.fortune}</div>
            </div>
        `;

        setTimeout(() => {
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
        }, 100);

    } catch (e) {
        loader.style.display = 'none';
        resultArea.style.display = 'block';
        alert('Payment succeeded, but analysis failed. Please contact support.');
    }
}

document.getElementById('close-modal').addEventListener('click', () => {
    document.getElementById('premium-modal').style.display = 'none';
});
