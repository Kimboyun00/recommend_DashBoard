import streamlit as st
import sqlite3
import hashlib
import time
import os

# 페이지 기본 설정 (가장 먼저 실행되어야 함)
st.set_page_config(
    page_title="웰커밍 투어 성향 테스트",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Streamlit 기본 UI 숨기기 및 전체 스타일 적용
st.markdown("""
<style>
    /* Streamlit 기본 UI 완전히 숨기기 */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    .stDecoration {display: none;}
    [data-testid="stHeader"] {display: none;}
    [data-testid="stToolbar"] {display: none;}
    [data-testid="stSidebar"] {display: none;}
    [data-testid="collapsedControl"] {display: none;}
    
    /* 전체 앱 컨테이너 스타일 */
    .stApp {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #334155 100%);
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem 1rem;
    }
    
    /* 메인 컨테이너 */
    .main .block-container {
        padding: 3rem 2.5rem !important;
        max-width: 500px !important;
        width: 90% !important;
        margin: 0 auto !important;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: stretch;
        min-height: auto !important;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
        position: relative;
        overflow: hidden;
        transform: translateY(10vh);
    }
    
    /* 상단 그라데이션 라인 */
    .main .block-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #10B981, #6366F1, #8B5CF6);
        border-radius: 20px 20px 0 0;
    }
    
    /* 제목 스타일 */
    .main h1 {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #10B981, #6366F1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.02em;
    }
    
    /* 부제목 스타일 */
    .main p {
        text-align: center;
        color: rgba(255, 255, 255, 0.8);
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 400;
        line-height: 1.6;
    }
    
    /* 탭 버튼 스타일 */
    .stButton > button {
        width: 100% !important;
        padding: 0.75rem 0 !important;
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        color: rgba(255, 255, 255, 0.8) !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        backdrop-filter: blur(10px) !important;
        margin: 0.5rem 0 !important;
    }
    
    .stButton > button:hover {
        background: rgba(255, 255, 255, 0.2) !important;
        border-color: #10B981 !important;
        color: white !important;
        transform: translateY(-2px) !important;
    }
    
    /* 로그인 버튼 (폼 제출용)은 다른 스타일 */
    .stForm .stButton > button {
        background: linear-gradient(135deg, #10B981, #6366F1) !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        box-shadow: 0 10px 25px rgba(16, 185, 129, 0.3) !important;
        margin: 1.5rem 0 1rem 0 !important;
        padding: 0.875rem 0 !important;
    }
    
    .stForm .stButton > button:hover {
        background: linear-gradient(135deg, #047857, #10B981) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 15px 35px rgba(16, 185, 129, 0.4) !important;
    }
    
    /* 입력 필드 스타일 */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        color: white !important;
        padding: 0.875rem 1rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #10B981 !important;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2) !important;
        outline: none !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.5) !important;
    }
    
    .stTextInput label {
        color: white !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        margin-bottom: 0.5rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    
    /* 라디오 버튼 숨기기 */
    .stRadio {
        display: none !important;
    }
    
    /* 알림 메시지 스타일 */
    .stAlert {
        border-radius: 12px !important;
        backdrop-filter: blur(10px) !important;
        border: none !important;
        margin: 1rem 0 !important;
    }
    
    /* 성공 메시지 */
    .stSuccess {
        background: rgba(16, 185, 129, 0.2) !important;
        color: white !important;
        border: 1px solid rgba(16, 185, 129, 0.4) !important;
    }
    
    /* 에러 메시지 */
    .stError {
        background: rgba(239, 68, 68, 0.2) !important;
        color: white !important;
        border: 1px solid rgba(239, 68, 68, 0.4) !important;
    }
    
    /* 경고 메시지 */
    .stWarning {
        background: rgba(245, 158, 11, 0.2) !important;
        color: white !important;
        border: 1px solid rgba(245, 158, 11, 0.4) !important;
    }
    
    /* 정보 메시지 */
    .stInfo {
        background: rgba(59, 130, 246, 0.2) !important;
        color: white !important;
        border: 1px solid rgba(59, 130, 246, 0.4) !important;
    }
    
    /* 정보 카드 */
    .info-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(16, 185, 129, 0.2));
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        color: white;
        backdrop-filter: blur(10px);
    }
    
    .info-card h4 {
        color: #6366F1;
        margin-bottom: 1rem;
        font-size: 1.125rem;
        font-weight: 700;
    }
    
    .demo-credentials {
        background: rgba(0, 0, 0, 0.3);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        font-family: 'Courier New', monospace;
        border-left: 3px solid #6366F1;
        color: #E5E7EB;
    }
    
    /* 시스템 정보 */
    .system-features {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 2rem 0;
        backdrop-filter: blur(10px);
        width: 100%;
    }
    
    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .feature-item {
        text-align: center;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    .feature-item:hover {
        background: rgba(255, 255, 255, 0.1);
        transform: translateY(-2px);
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
        display: block;
    }
    
    .feature-title {
        font-weight: 700;
        color: white;
        margin-bottom: 0.25rem;
        font-size: 0.875rem;
    }
    
    .feature-desc {
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.75rem;
        line-height: 1.4;
    }
    
    /* 반응형 디자인 */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 2rem 1.5rem !important;
            margin: 1rem auto !important;
            max-width: 95% !important;
            transform: translateY(5vh);
        }
        
        .main h1 {
            font-size: 2rem;
        }
        
        .features-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    
    @media (max-width: 480px) {
        .main .block-container {
            padding: 1.5rem 1rem !important;
            transform: translateY(2vh);
        }
        
        .main h1 {
            font-size: 1.75rem;
        }
        
        .features-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)

# 데이터베이스 설정
@st.cache_resource
def setup_database():
    """데이터베이스 초기화"""
    try:
        conn = sqlite3.connect('wellness_users.db', check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users 
                     (username TEXT PRIMARY KEY, password TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"데이터베이스 초기화 오류: {e}")
        return False

def hash_password(password):
    """비밀번호를 SHA256 해시로 변환"""
    return hashlib.sha256(str.encode(password)).hexdigest()

def verify_user_credentials(username, password):
    """사용자 인증 확인"""
    try:
        # 데모 계정 우선 확인
        if username == "wellness" and password == "1234":
            return True
            
        # 데이터베이스 계정 확인
        conn = sqlite3.connect('wellness_users.db')
        c = conn.cursor()
        c.execute('SELECT password FROM users WHERE username = ?', (username,))
        result = c.fetchone()
        conn.close()
        
        if result and result[0] == hash_password(password):
            return True
            
        return False
    except Exception as e:
        st.error(f"인증 확인 중 오류: {e}")
        return False

def create_user_account(username, password):
    """새 사용자 계정 생성"""
    try:
        conn = sqlite3.connect('wellness_users.db')
        c = conn.cursor()
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                 (username, hash_password(password)))
        conn.commit()
        conn.close()
        return True, "회원가입이 완료되었습니다!"
    except sqlite3.IntegrityError:
        return False, "이미 존재하는 아이디입니다."
    except Exception as e:
        return False, f"회원가입 중 오류가 발생했습니다: {e}"

def render_login_form():
    """로그인 폼 렌더링"""
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input(
            "아이디", 
            placeholder="아이디를 입력하세요",
            key="login_username"
        )
        password = st.text_input(
            "비밀번호", 
            type="password", 
            placeholder="비밀번호를 입력하세요",
            key="login_password"
        )
        
        submitted = st.form_submit_button("🚀 로그인")
        
        if submitted:
            if not username or not password:
                st.error("❌ 아이디와 비밀번호를 모두 입력해주세요.")
            else:
                with st.spinner("인증 확인 중..."):
                    time.sleep(0.8)
                    
                    if verify_user_credentials(username, password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.reset_survey_flag = True
                        
                        st.success("✅ 로그인 성공! 웰니스 여행 추천을 시작합니다.")
                        st.balloons()
                        
                        time.sleep(2)
                        st.switch_page("pages/03_home.py")
                    else:
                        st.error("❌ 아이디 또는 비밀번호가 잘못되었습니다.")

def render_signup_form():
    """회원가입 폼 렌더링"""
    with st.form("signup_form", clear_on_submit=True):
        new_username = st.text_input(
            "사용할 아이디", 
            placeholder="영문, 숫자 조합 (4자 이상)",
            key="signup_username"
        )
        new_password = st.text_input(
            "사용할 비밀번호", 
            type="password", 
            placeholder="안전한 비밀번호 (4자 이상)",
            key="signup_password"
        )
        confirm_password = st.text_input(
            "비밀번호 확인", 
            type="password", 
            placeholder="비밀번호를 다시 입력하세요",
            key="signup_confirm"
        )
        
        submitted = st.form_submit_button("✨ 가입하기")
        
        if submitted:
            if not new_username or not new_password or not confirm_password:
                st.error("❌ 모든 필드를 입력해주세요.")
            elif len(new_username) < 4:
                st.warning("⚠️ 아이디는 4자 이상이어야 합니다.")
            elif len(new_password) < 4:
                st.warning("🔒 비밀번호는 4자 이상이어야 합니다.")
            elif new_password != confirm_password:
                st.error("❌ 비밀번호가 일치하지 않습니다.")
            else:
                with st.spinner("계정 생성 중..."):
                    time.sleep(0.8)
                    
                    success, message = create_user_account(new_username, new_password)
                    
                    if success:
                        st.success(f"🎉 {message}")
                        st.info("이제 로그인할 수 있습니다!")
                        
                        st.session_state.auth_tab = "로그인"
                        time.sleep(2.5)
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")

def auth_page():
    """로그인/회원가입 페이지"""
    
    # 데이터베이스 초기화
    if not setup_database():
        st.error("시스템 초기화에 실패했습니다. 잠시 후 다시 시도해주세요.")
        if st.button("🔄 다시 시도"):
            st.rerun()
        return

    # 탭 상태 초기화
    if 'auth_tab' not in st.session_state:
        st.session_state.auth_tab = "로그인"

    # 제목 표시
    st.markdown("# 🌿 웰커밍 투어")
    st.markdown("AI 기반 12개 요인 분석으로 당신만의 맞춤형 힐링 여행을 찾아보세요")
    
    # 커스텀 탭 버튼
    tab_col1, tab_col2 = st.columns(2)
    
    with tab_col1:
        if st.button("로그인", key="login_tab", use_container_width=True):
            st.session_state.auth_tab = "로그인"
    
    with tab_col2:
        if st.button("회원가입", key="signup_tab", use_container_width=True):
            st.session_state.auth_tab = "회원가입"
    
    # 선택된 탭에 따라 폼 표시
    if st.session_state.auth_tab == "로그인":
        render_login_form()
        
        # 데모 계정 안내
        st.markdown("""
        <div class="info-card">
            <h4>🎯 체험용 데모 계정</h4>
            <div class="demo-credentials">
                <strong>아이디:</strong> wellness<br>
                <strong>비밀번호:</strong> 1234
            </div>
            <p style="margin: 0; font-size: 0.875rem; opacity: 0.8;">
                💡 즉시 체험해보고 싶다면 위 데모 계정을 사용하세요!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    else:  # 회원가입
        render_signup_form()
    
    # 시스템 정보
    st.markdown("""
    <div class="system-features">
        <h4 style="color: white; text-align: center; margin-bottom: 1rem; font-size: 1.25rem; font-weight: 700;">🚀 시스템 특징</h4>
        <div class="features-grid">
            <div class="feature-item">
                <span class="feature-icon">🔬</span>
                <div class="feature-title">과학적 분석</div>
                <div class="feature-desc">2,591명 데이터 요인분석</div>
            </div>
            <div class="feature-item">
                <span class="feature-icon">🎯</span>
                <div class="feature-title">정밀 분류</div>
                <div class="feature-desc">12개 요인 8개 클러스터</div>
            </div>
            <div class="feature-item">
                <span class="feature-icon">🤖</span>
                <div class="feature-title">AI 추천</div>
                <div class="feature-desc">95% 정확도</div>
            </div>
            <div class="feature-item">
                <span class="feature-icon">⚡</span>
                <div class="feature-title">실시간</div>
                <div class="feature-desc">1.2초 응답</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    """메인 실행 함수"""
    # 세션 상태 초기화
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # 로그인 상태 확인
    if st.session_state.logged_in:
        try:
            st.switch_page("pages/03_home.py")
        except Exception as e:
            st.error(f"페이지 이동 중 오류: {e}")
            st.session_state.logged_in = False
            st.rerun()
    else:
        try:
            auth_page()
        except Exception as e:
            st.error("❌ 시스템 오류가 발생했습니다.")
            st.exception(e)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 페이지 새로고침"):
                    st.rerun()
            with col2:
                if st.button("🔧 세션 초기화"):
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()

# 앱 실행
if __name__ == "__main__":
    main()
else:
    main()