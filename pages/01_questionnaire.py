import streamlit as st
import json
import sqlite3
from utils import questions, calculate_wellness_score, validate_wellness_answers, show_footer, reset_wellness_survey_state, check_access_permissions, convert_answers_to_survey_results

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="웰니스 관광 성향 설문",
    page_icon="🌿",
    layout="wide"
)

# 접근 권한 확인 (설문 페이지이므로 'questionnaire' 타입)
check_access_permissions('questionnaire')

# --- 로그인 확인 및 설문 상태 초기화 ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("⚠️ 로그인 후 이용해주세요.")
    st.page_link("app.py", label="로그인 페이지로 돌아가기", icon="🏠")
    st.stop()

if st.session_state.get('reset_survey_flag', False):
    reset_wellness_survey_state()

# --- 웰니스 테마 CSS ---
st.markdown("""
<style>
    /* 웰니스 테마 배경 그라데이션 */
    [data-testid="stAppViewContainer"] > .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #4CAF50 100%);
    }
    
    /* 설문 옵션(라디오/체크박스) 글자 크게 및 웰니스 스타일 */
    div[data-testid="stRadio"] label span ,
    div[data-testid="stCheckbox"] label span {
        font-size: 1.25em !important;
        line-height: 1.7;
        color: #2E7D32 !important;
        font-weight: 600 !important;
    }
    
    /* 라디오 버튼과 체크박스 공통 스타일 - 완전 동일하게 */
    div[data-testid="stRadio"],
    div[data-testid="stCheckbox"] {
        margin: 0 0 10px 0 !important;
        padding: 0 !important;
    }
    
    /* 라디오버튼 그룹 전체 간격 조정 */
    div[data-testid="stRadio"] > div {
        gap: 10px !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* 체크박스 그룹 전체 간격 조정 */
    div[data-testid="stCheckbox"] > div {
        margin: 0 0 10px 0 !important;
        padding: 0 !important;
    }

    /* 라디오 버튼 웰니스 스타일 */
    div[data-testid="stRadio"] label {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 2px solid rgba(76, 175, 80, 0.5) !important;
        border-radius: 10px !important;
        padding: 8px 12px !important;
        margin: 0 0 0 0 !important;
        transition: all 0.3s ease !important;
        backdrop-filter: blur(10px) !important;
        width: 100% !important;
        box-sizing: border-box !important;
        display: flex !important;
        align-items: center !important;
        min-height: 40px !important;
        line-height: 1.3 !important;
    }
    
    /* 체크박스 웰니스 스타일 */
    div[data-testid="stCheckbox"] label {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 2px solid rgba(76, 175, 80, 0.5) !important;
        border-radius: 10px !important;
        padding: 8px 12px !important;
        margin: 0 0 0 0 !important;
        transition: all 0.3s ease !important;
        backdrop-filter: blur(10px) !important;
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
        box-sizing: border-box !important;
        min-height: 40px !important;
        line-height: 1.3 !important;
    }
    
    div[data-testid="stRadio"] input:checked + div,
    div[data-testid="stCheckbox"] input:checked + div {
        background-color: rgba(76, 175, 80, 0.3) !important;
        border-color: #4CAF50 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4) !important;
    }
    
    /* 문항 제목 웰니스 스타일 */
    h3 {
        font-size: 1.5em;
        margin-bottom: 0.5em;
        color: #2E7D32 !important;
    }
    
    /* 메인 제목 */
    h1 {
        color: #2E7D32 !important;
        text-align: left;
        padding: 20px;
        font-size: 2.5em !important;
        margin-bottom: 30px;
        font-weight: 800 !important;
    }
    
    /* 진행률 바 */
    div[data-testid="stProgress"] > div > div {
        background: linear-gradient(45deg, #4CAF50, #81C784) !important;
    }
    
    /* 버튼 스타일 */
    div[data-testid="stButton"] > button {
        background: linear-gradient(45deg, #4CAF50, #81C784) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 12px 30px !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
    }
    
    div[data-testid="stButton"] > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4) !important;
    }
    
    /* 에러/경고 메시지 */
    div[data-testid="stAlert"] {
        font-size: 1.2em;
        font-weight: bold;
        color: #d32f2f !important;
    }
    
    /* 복수응답 안내 메시지 스타일 - 박스 제거 */
    .multiple-choice-info {
        background: none;
        border: none;
        border-radius: 0;
        padding: 5px 0;
        margin: 5px 0 15px 0;
        color: #2E7D32;
        font-weight: 600;
        font-size: 0.95em;
    }
    
    /* 기본 UI 숨김 */
    [data-testid="stHeader"] { display: none; }
    [data-testid="stSidebarNav"] { display: none; }
    [data-testid="stSidebar"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }
    footer { display: none; }
    
    /* 메인 컨테이너 */
    .main .block-container {
        display: block;
        align-items: initial;
        justify-content: initial;
        min-height: auto;
        padding-top: 2rem !important;
    }
</style>
""", unsafe_allow_html=True)

def wellness_questionnaire_page():
    # 사이드바에 웰니스 테마 환영 메시지
    with st.sidebar:
        st.success(f"🌿 **{st.session_state.username}**님, 환영합니다! 웰니스 여행을 위한 설문에 참여해주세요!")
        if st.button("🚪 로그아웃", use_container_width=True):
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
        """답변 업데이트 함수 - 복수응답 지원"""
        for key, question_data in questions.items():
            # 복수응답 문항 처리
            if question_data.get('multiple', False):
                selected_indices = [j for j, _ in enumerate(question_data['options']) 
                                 if st.session_state.get(f"checkbox_{key}_{j}", False)]
                st.session_state.answers[key] = selected_indices
            # 단일 선택 문항 처리
            elif f"radio_{key}" in st.session_state:
                st.session_state.answers[key] = st.session_state[f"radio_{key}"]

    # 메인 제목
    st.title("🌿 웰니스 관광 성향 설문조사")
    
    # 소개 메시지
    st.markdown("""
    <div style="
        backdrop-filter: blur(10px);
        padding: 15px;
        margin: 15px 0;
        text-align: center;
    ">
        <p style="color: #2E7D32; text-align: left; font-size: 1.1em; margin: 0; font-weight: 600;">
            💚 당신만의 맞춤형 웰니스 여행지를 추천하기 위해 몇 가지 질문에 답해주세요 💚
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    progress_placeholder = st.container()
    st.markdown("---")

    # utils.py의 questions 딕셔너리를 사용하여 설문 표시
    for key, question in questions.items():
        is_error = key in st.session_state.validation_errors
        current_answer = st.session_state.answers.get(key)
        container = st.container()

        # 에러가 있는 문항은 강조 표시
        if is_error:
            container.markdown(
                f"<h3 style='color: #ff4444;'>**{question['title']}** ⚠️ 필수 문항</h3>", 
                unsafe_allow_html=True
            )
        else:
            container.subheader(f"**{question['title']}**")

        # 복수 선택 문항 처리
        if question.get('multiple', False):
            container.markdown("""
            <div class="multiple-choice-info">
                ✅ <strong>복수 선택 가능:</strong> 해당하는 모든 항목을 선택해주세요
            </div>
            """, unsafe_allow_html=True)
            
            for j, option in enumerate(question['options']):
                is_checked = isinstance(current_answer, list) and j in current_answer
                container.checkbox(
                    f"{j+1}. {option}", 
                    key=f"checkbox_{key}_{j}", 
                    on_change=update_answers, 
                    value=is_checked
                )
        # 단일 선택 문항
        else:
            index_to_pass = current_answer if current_answer is not None else None
            container.radio(
                "",
                options=list(range(len(question['options']))),
                format_func=lambda x, opts=question['options']: f"{x+1}. {opts[x]}",
                key=f"radio_{key}",
                on_change=update_answers,
                index=index_to_pass,
                label_visibility="hidden"
            )
        
        st.markdown("---")

    # 진행률 계산 및 표시 (복수응답 지원)
    answered_count = 0
    for key, question_data in questions.items():
        if key in st.session_state.answers:
            answer = st.session_state.answers[key]
            # 복수응답 문항: 빈 리스트가 아닌지 확인
            if question_data.get('multiple', False):
                if isinstance(answer, list) and len(answer) > 0:
                    answered_count += 1
            # 단일응답 문항: None이 아닌지 확인
            else:
                if answer is not None:
                    answered_count += 1
    
    progress_value = answered_count / len(questions) if questions else 0
    
    with progress_placeholder:
        st.progress(progress_value)
        st.markdown(
            f"<div style='font-size:1.3em; font-weight:bold; margin-top:0.5em;'>"
            f"🌿 진행률: {answered_count} / {len(questions)} ({progress_value:.0%}) 🌿</div>",
            unsafe_allow_html=True
        )

    # 완료 버튼
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🎯 웰니스 성향 분석하기", type="primary", use_container_width=True):
            if validate_wellness_answers():
                st.session_state.survey_completed = True
                
                # 웰니스 점수 계산 및 저장
                total_score, score_breakdown = calculate_wellness_score(st.session_state.answers)
                st.session_state.total_score = total_score
                st.session_state.score_breakdown = score_breakdown
                
                # survey_results 생성 (추천 페이지에서 사용)
                from utils import convert_answers_to_survey_results
                st.session_state.survey_results = convert_answers_to_survey_results(st.session_state.answers)
                
                st.switch_page("pages/02_analyzing.py")
            else:
                st.error(f"⚠️ {len(st.session_state.validation_errors)}개의 문항에 답변이 필요합니다!")
                st.rerun()

    show_footer()

if __name__ == '__main__':
    wellness_questionnaire_page()
else:
    wellness_questionnaire_page()