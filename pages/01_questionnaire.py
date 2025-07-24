import streamlit as st
import time
from utils import (questions, calculate_factor_scores, determine_cluster_from_factors, 
                  validate_answers, show_footer, reset_survey_state, check_access_permissions)

# 페이지 설정
st.set_page_config(
    page_title="웰니스 관광 성향 설문",
    page_icon="🌿",
    layout="wide"
)

# 접근 권한 확인
check_access_permissions('questionnaire')

# 로그인 확인
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("⚠️ 로그인 후 이용해주세요.")
    if st.button("🏠 로그인 페이지로 돌아가기", key="login_redirect"):
        st.switch_page("app.py")
    st.stop()

if st.session_state.get('reset_survey_flag', False):
    reset_survey_state()

# 고급 CSS 스타일링 (TailwindCSS 스타일 적용)
st.markdown("""
<style>
    /* 기본 배경 그라데이션 */
    [data-testid="stAppViewContainer"] > .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #4CAF50 100%);
        min-height: 100vh;
    }
    
    /* 메인 컨테이너 */
    .main .block-container {
        max-width: 1000px;
        margin: 0 auto;
        padding: 2rem 1rem !important;
    }
    
    /* 프로그레스 컨테이너 */
    .progress-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(15px);
        border: 2px solid rgba(76, 175, 80, 0.3);
        border-radius: 20px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    /* 질문 카드 스타일 */
    .question-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(15px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 20px;
        padding: 30px;
        margin: 25px 0;
        transition: all 0.3s ease;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .question-card:hover {
        transform: translateY(-2px);
        border-color: #4CAF50;
        box-shadow: 0 12px 40px rgba(76, 175, 80, 0.2);
    }
    
    .question-card.error {
        border-color: #FF5722;
        background: linear-gradient(135deg, rgba(255, 87, 34, 0.1), rgba(255, 255, 255, 0.95));
        animation: shake 0.6s ease-in-out;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    /* 질문 제목 */
    .question-title {
        color: #2E7D32;
        font-size: 1.4em;
        font-weight: 700;
        margin-bottom: 20px;
        line-height: 1.4;
    }
    
    .question-title.error {
        color: #FF5722;
    }
    
    /* 요인 태그 */
    .factor-tag {
        display: inline-block;
        background: linear-gradient(45deg, #4CAF50, #81C784);
        color: white;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 0.8em;
        font-weight: 600;
        margin-bottom: 15px;
        box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
    }
    
    /* 라디오 버튼 스타일 */
    div[data-testid="stRadio"] {
        margin: 15px 0;
    }
    
    div[data-testid="stRadio"] > div {
        gap: 12px !important;
    }
    
    div[data-testid="stRadio"] label {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 2px solid rgba(76, 175, 80, 0.3) !important;
        border-radius: 15px !important;
        padding: 15px 20px !important;
        margin: 0 !important;
        transition: all 0.3s ease !important;
        backdrop-filter: blur(10px) !important;
        cursor: pointer !important;
        min-height: 60px !important;
        display: flex !important;
        align-items: center !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
    }
    
    div[data-testid="stRadio"] label:hover {
        transform: translateY(-2px) !important;
        border-color: #4CAF50 !important;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.2) !important;
    }
    
    div[data-testid="stRadio"] input:checked + div {
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.2), rgba(129, 199, 132, 0.1)) !important;
        border-color: #4CAF50 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.3) !important;
    }
    
    div[data-testid="stRadio"] label span {
        font-size: 1.1em !important;
        color: #2E7D32 !important;
        font-weight: 600 !important;
        line-height: 1.5 !important;
    }
    
    /* 메인 제목 */
    .main-title {
        color: #2E7D32 !important;
        text-align: center;
        font-size: 2.8em !important;
        font-weight: 800 !important;
        margin-bottom: 30px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        background: rgba(255, 255, 255, 0.95);
        padding: 25px;
        border-radius: 20px;
        border: 3px solid #4CAF50;
    }
    
    /* 인트로 카드 */
    .intro-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(15px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 20px;
        padding: 25px;
        margin: 20px 0;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    /* 진행률 바 커스터마이징 */
    div[data-testid="stProgress"] > div > div {
        background: linear-gradient(45deg, #4CAF50, #81C784) !important;
        border-radius: 10px !important;
        height: 12px !important;
    }
    
    div[data-testid="stProgress"] > div {
        background: rgba(76, 175, 80, 0.2) !important;
        border-radius: 10px !important;
        height: 12px !important;
    }
    
    /* 진행률 텍스트 */
    .progress-text {
        font-size: 1.3em;
        font-weight: 700;
        color: #2E7D32;
        text-align: center;
        margin: 15px 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    /* 완료 버튼 */
    div[data-testid="stButton"] > button {
        background: linear-gradient(45deg, #4CAF50, #66BB6A) !important;
        border: none !important;
        border-radius: 15px !important;
        color: white !important;
        font-weight: 700 !important;
        padding: 15px 30px !important;
        font-size: 18px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4) !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        width: 100% !important;
        min-height: 60px !important;
    }
    
    div[data-testid="stButton"] > button:hover {
        background: linear-gradient(45deg, #388E3C, #4CAF50) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 30px rgba(76, 175, 80, 0.5) !important;
    }
    
    /* 에러 메시지 */
    div[data-testid="stAlert"] {
        border-radius: 15px !important;
        border: 2px solid #FF5722 !important;
        background: linear-gradient(135deg, rgba(255, 87, 34, 0.1), rgba(255, 255, 255, 0.95)) !important;
        color: #FF5722 !important;
        font-weight: 600 !important;
        font-size: 1.1em !important;
    }
    
    /* 사이드바 커스터마이징 */
    section[data-testid="stSidebar"] > div {
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(129, 199, 132, 0.05));
        backdrop-filter: blur(15px);
    }
    
    /* 기본 UI 숨김 */
    [data-testid="stHeader"] { display: none; }
    [data-testid="stSidebarNav"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }
    footer { display: none; }
    
    /* 반응형 디자인 */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem 0.5rem !important;
        }
        
        .main-title {
            font-size: 2.2em !important;
            padding: 20px 15px !important;
        }
        
        .question-card {
            padding: 20px 15px;
            margin: 15px 0;
        }
        
        div[data-testid="stRadio"] label {
            padding: 12px 15px !important;
            min-height: 50px !important;
        }
        
        div[data-testid="stRadio"] label span {
            font-size: 1em !important;
        }
    }
</style>
""", unsafe_allow_html=True)

def get_factor_description(factor_key):
    """요인별 설명 반환"""
    descriptions = {
        "요인1": "계획적 정보 추구형",
        "요인2": "쇼핑 중심형", 
        "요인3": "한국 여행 경험축",
        "요인4": "실용적 현지 탐색형",
        "요인5": "편의 인프라 중시형",
        "요인6": "전통문화 안전 추구형",
        "요인7": "패션 쇼핑형",
        "요인8": "프리미엄 사회적 여행형",
        "요인9": "성별 기반 쇼핑 선호형",
        "요인10": "디지털 미디어 개인형",
        "요인11": "절차 중시 자연 관광형",
        "요인12": "교통 편의 미식형"
    }
    return descriptions.get(factor_key, "미정의 요인")

def questionnaire_page():
    # 사이드바에 사용자 정보 및 진행 상황
    with st.sidebar:
        st.success(f"🌿 **{st.session_state.username}**님 환영합니다!")
        
        # 간단한 설명
        st.markdown("""
        ### 📋 12개 요인 분석 시스템
        
        **🎯 새로운 분석 방식**
        - 12개 핵심 요인으로 성향 분석
        - 8개 클러스터로 정확한 분류
        - 2,591명 데이터 기반 검증
        
        **⏱️ 소요 시간**: 약 5분
        **📊 정확도**: 95% 이상
        """)
        
        if st.button("🚪 로그아웃", use_container_width=True, key="sidebar_logout"):
            st.session_state.clear()
            st.session_state.logged_in = False
            st.switch_page("app.py")

    # 세션 상태 초기화
    if 'answers' not in st.session_state:
        st.session_state.answers = {}
    if 'survey_completed' not in st.session_state:
        st.session_state.survey_completed = False
    if 'validation_errors' not in st.session_state:
        st.session_state.validation_errors = set()

    def update_answers():
        """답변 업데이트 함수"""
        for q_key in questions.keys():
            radio_key = f"radio_{q_key}"
            if radio_key in st.session_state:
                st.session_state.answers[q_key] = st.session_state[radio_key]

    # 메인 제목
    st.markdown('<h1 class="main-title">🌿 한국 관광 성향 진단 시스템</h1>', unsafe_allow_html=True)
    
    # 소개 메시지
    st.markdown("""
    <div class="intro-card">
        <h3 style="color: #2E7D32; margin-bottom: 15px;">🎯 12개 요인 기반 정밀 분석</h3>
        <p style="color: #2E7D32; font-size: 1.1em; margin: 0; font-weight: 600; line-height: 1.6;">
            실제 2,591명의 외국인 관광객 데이터를 분석하여 개발된 과학적 성향 진단 시스템입니다.<br>
            각 질문은 특정 요인을 측정하여 당신만의 여행 패턴을 정확히 파악합니다.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 진행률 표시를 위한 플레이스홀더
    progress_placeholder = st.empty()
    
    st.markdown("---")

    # 설문 문항 표시
    for q_key, question in questions.items():
        is_error = q_key in st.session_state.validation_errors
        current_answer = st.session_state.answers.get(q_key)
        
        # 질문 카드 생성
        card_class = "question-card error" if is_error else "question-card"
        title_class = "question-title error" if is_error else "question-title"
        
        st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
        
        # 요인 태그
        factor_desc = get_factor_description(question['factor'])
        st.markdown(f'<div class="factor-tag">{question["factor"]}: {factor_desc}</div>', unsafe_allow_html=True)
        
        # 질문 제목
        title_text = f"**{question['title']}**"
        if is_error:
            title_text += " ⚠️ **필수 문항**"
        
        st.markdown(f'<div class="{title_class}">{title_text}</div>', unsafe_allow_html=True)
        
        # 라디오 버튼 옵션 - 접근성 경고 해결
        index_to_pass = current_answer if current_answer is not None else None
        
        # 각 질문마다 고유한 라벨 생성
        question_number = q_key.replace('q', '')
        radio_label = f"질문 {question_number}번 응답 선택"
        
        st.radio(
            radio_label,  # 접근성을 위한 명확한 라벨
            options=list(range(len(question['options']))),
            format_func=lambda x, opts=question['options']: f"{x+1}. {opts[x]}",
            key=f"radio_{q_key}",
            on_change=update_answers,
            index=index_to_pass,
            label_visibility="hidden"  # 라벨은 숨기지만 스크린 리더를 위해 제공
        )
        
        st.markdown('</div>', unsafe_allow_html=True)

    # 진행률 계산 및 표시
    answered_count = len([q for q in questions.keys() if st.session_state.answers.get(q) is not None])
    progress_value = answered_count / len(questions)
    
    with progress_placeholder:
        st.markdown('<div class="progress-container">', unsafe_allow_html=True)
        st.progress(progress_value)
        st.markdown(f"""
        <div class="progress-text">
            🌿 진행률: {answered_count} / {len(questions)} ({progress_value:.0%}) 
            {' 🎉 완료!' if progress_value == 1 else ''}
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # 완료 버튼
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎯 12개 요인 분석 시작하기", type="primary", use_container_width=True, key="complete_survey"):
            if validate_answers():
                try:
                    # 요인 점수 계산
                    factor_scores = calculate_factor_scores(st.session_state.answers)
                    st.session_state.factor_scores = factor_scores
                    
                    # 클러스터 결정
                    cluster_result = determine_cluster_from_factors(factor_scores)
                    st.session_state.cluster_result = cluster_result
                    st.session_state.survey_completed = True
                    
                    # 성공 메시지와 함께 분석 페이지로 이동
                    st.success("✅ 설문이 완료되었습니다! 분석을 시작합니다...")
                    st.balloons()
                    time.sleep(1.5)
                    st.switch_page("pages/02_analyzing.py")
                    
                except Exception as e:
                    st.error(f"❌ 분석 중 오류가 발생했습니다: {str(e)}")
                    st.info("잠시 후 다시 시도해주세요.")
            else:
                error_count = len(st.session_state.validation_errors)
                st.error(f"⚠️ {error_count}개의 문항에 답변이 필요합니다!")
                
                # 오류가 있는 문항들 표시
                missing_questions = []
                for q_key in st.session_state.validation_errors:
                    if q_key in questions:
                        q_num = q_key.replace('q', '')
                        missing_questions.append(f"Q{q_num}")
                
                if missing_questions:
                    st.warning(f"미완료 문항: {', '.join(missing_questions)}")
                
                st.rerun()

    # 푸터
    show_footer()

# 실행부 - 에러 처리 추가
if __name__ == '__main__':
    try:
        questionnaire_page()
    except Exception as e:
        st.error("❌ 페이지 로딩 중 오류가 발생했습니다.")
        st.exception(e)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 페이지 새로고침", key="refresh_page"):
                st.rerun()
        
        with col2:
            if st.button("🏠 홈으로 돌아가기", key="home_redirect"):
                st.switch_page("pages/03_home.py")
else:
    questionnaire_page()