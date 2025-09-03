# app.py - 개선된 밝은 테마 메인 앱
import streamlit as st
import sqlite3
import hashlib
import time
import os

# 페이지 기본 설정
st.set_page_config(
    page_title="웰커밍 투어 성향 테스트",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 데이터베이스 설정
@st.cache_resource
def setup_database():
    """데이터베이스 초기화 (캐시 적용으로 성능 향상)"""
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

# 밝은 테마 로그인 UI 스타일
def auth_css():
    st.markdown("""
    <style>
        /* 전역 변수 - 밝은 테마 */
        :root {
            --primary: #3498DB;
            --primary-dark: #2980B9;
            --primary-light: #5DADE2;
            --secondary: #2ECC71;
            --accent: #E67E22;
            --glass-bg: rgba(255, 255, 255, 0.95);
            --glass-border: rgba(52, 152, 219, 0.2);
            --text-primary: #2C3E50;
            --text-secondary: #34495E;
        }
        
        /* Streamlit 기본 UI 숨기기 */
        [data-testid="stHeader"], 
        [data-testid="stSidebar"], 
        footer,
        [data-testid="stToolbar"] { 
            display: none !important; 
        }
        
        /* 메인 배경 - 밝은 그라데이션 */
        [data-testid="stAppViewContainer"] > .main {
            background: linear-gradient(135deg, #F8F9FA 0%, #E8F4FD 35%, #D6EAF8 100%);
            background-size: 400% 400%;
            animation: gradient-shift 20s ease infinite;
            min-height: 100vh;
        }
        
        @keyframes gradient-shift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        /* 메인 컨테이너 중앙 정렬 */
        .main .block-container {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            width: 100%;
            padding: 20px !important;
        }

        /* 로그인 폼 컨테이너 */
        .auth-container {
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            border: 2px solid var(--glass-border);
            border-radius: 24px;
            padding: 48px 40px;
            width: 100%;
            max-width: 480px;
            text-align: center;
            box-shadow: 0 16px 48px rgba(0, 0, 0, 0.1);
            position: relative;
            overflow: hidden;
        }
        
        .auth-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            border-radius: 24px 24px 0 0;
        }
        
        /* 제목 스타일 */
        .auth-title {
            font-size: 2.4em !important;
            font-weight: 800 !important;
            margin-bottom: 12px !important;
            letter-spacing: 1px !important;
            background: linear-gradient(135deg, var(--primary-dark), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .auth-subtitle {
            color: var(--text-secondary) !important;
            font-size: 1.1em !important;
            margin-bottom: 32px !important;
            font-weight: 500 !important;
            line-height: 1.5 !important;
        }

        /* 탭 스타일 */
        div[data-testid="stRadio"] {
            display: flex !important;
            justify-content: center !important;
            margin-bottom: 28px !important;
            gap: 8px !important;
        }
        
        div[data-testid="stRadio"] > div {
            display: flex !important;
            gap: 8px !important;
        }
        
        div[data-testid="stRadio"] label {
            background: rgba(255, 255, 255, 0.8) !important;
            border: 2px solid var(--glass-border) !important;
            border-radius: 12px !important;
            padding: 12px 24px !important;
            margin: 0 !important;
            transition: all 0.3s ease !important;
            color: var(--text-secondary) !important;
            font-weight: 600 !important;
            cursor: pointer !important;
            backdrop-filter: blur(10px) !important;
        }
        
        div[data-testid="stRadio"] label:hover {
            background: rgba(255, 255, 255, 1) !important;
            border-color: var(--primary) !important;
            color: var(--text-primary) !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(52, 152, 219, 0.15) !important;
        }
        
        div[data-testid="stRadio"] input:checked + div {
            background: linear-gradient(135deg, var(--primary), var(--primary-light)) !important;
            color: white !important;
            border-color: var(--primary) !important;
            box-shadow: 0 4px 16px rgba(52, 152, 219, 0.3) !important;
            transform: translateY(-1px) !important;
        }

        /* 입력 필드 스타일 */
        div[data-testid="stTextInput"] > div > div > input {
            background: rgba(255, 255, 255, 0.9) !important;
            border: 2px solid var(--glass-border) !important;
            border-radius: 12px !important;
            color: var(--text-primary) !important;
            padding: 14px 16px !important;
            font-size: 1em !important;
            transition: all 0.3s ease !important;
            backdrop-filter: blur(10px) !important;
        }
        
        div[data-testid="stTextInput"] > div > div > input:focus {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1) !important;
            outline: none !important;
            background: rgba(255, 255, 255, 1) !important;
        }
        
        div[data-testid="stTextInput"] > div > div > input::placeholder {
            color: rgba(45, 62, 80, 0.5) !important;
        }
        
        /* 라벨 스타일 */
        div[data-testid="stTextInput"] label {
            color: var(--text-primary) !important;
            font-weight: 600 !important;
            font-size: 1em !important;
            margin-bottom: 6px !important;
        }
        
        /* 버튼 스타일 */
        div[data-testid="stButton"] > button {
            width: 100% !important;
            padding: 14px 0 !important;
            background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
            border: none !important;
            border-radius: 12px !important;
            color: white !important;
            font-weight: 700 !important;
            font-size: 1em !important;
            transition: all 0.3s ease !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
            box-shadow: 0 4px 16px rgba(52, 152, 219, 0.3) !important;
        }
        
        div[data-testid="stButton"] > button:hover {
            background: linear-gradient(135deg, var(--primary-dark), var(--primary)) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4) !important;
        }
        
        /* 성공/오류 메시지 스타일 */
        div[data-testid="stAlert"] {
            border-radius: 12px !important;
            backdrop-filter: blur(10px) !important;
            border: none !important;
            margin: 16px 0 !important;
        }
        
        .stSuccess {
            background: rgba(46, 204, 113, 0.1) !important;
            color: #27AE60 !important;
            border: 2px solid rgba(46, 204, 113, 0.3) !important;
        }
        
        .stError {
            background: rgba(231, 76, 60, 0.1) !important;
            color: #E74C3C !important;
            border: 2px solid rgba(231, 76, 60, 0.3) !important;
        }
        
        .stWarning {
            background: rgba(243, 156, 18, 0.1) !important;
            color: #F39C12 !important;
            border: 2px solid rgba(243, 156, 18, 0.3) !important;
        }
        
        .stInfo {
            background: rgba(52, 152, 219, 0.1) !important;
            color: var(--primary) !important;
            border: 2px solid rgba(52, 152, 219, 0.3) !important;
        }
        
        /* 데모 계정 안내 */
        .demo-info {
            background: linear-gradient(135deg, rgba(52, 152, 219, 0.1), rgba(46, 204, 113, 0.1));
            border: 2px solid rgba(52, 152, 219, 0.2);
            border-radius: 12px;
            padding: 16px;
            margin: 20px 0;
            color: var(--text-primary);
            font-weight: 500;
            backdrop-filter: blur(10px);
        }
        
        .demo-info h4 {
            color: var(--primary) !important;
            margin-bottom: 8px !important;
            font-size: 1em !important;
        }
        
        /* 시스템 정보 */
        .system-info {
            background: rgba(255, 255, 255, 0.8);
            border: 2px solid var(--glass-border);
            border-radius: 12px;
            padding: 16px;
            margin: 24px 0;
            text-align: center;
            backdrop-filter: blur(10px);
        }
        
        .system-info h4 {
            color: var(--text-primary) !important;
            margin-bottom: 12px !important;
            font-size: 1.1em !important;
        }
        
        .system-stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-top: 12px;
        }
        
        .stat-item {
            text-align: center;
            padding: 8px;
            background: rgba(255, 255, 255, 0.6);
            border-radius: 8px;
            border: 1px solid rgba(52, 152, 219, 0.1);
        }
        
        .stat-number {
            font-size: 1.3em;
            font-weight: 800;
            color: var(--primary);
            display: block;
        }
        
        .stat-label {
            font-size: 0.8em;
            color: var(--text-secondary);
            margin-top: 2px;
        }
        
        /* 로딩 애니메이션 */
        .loading-spinner {
            border: 3px solid rgba(52, 152, 219, 0.3);
            border-radius: 50%;
            border-top: 3px solid var(--primary);
            width: 24px;
            height: 24px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* 반응형 디자인 */
        @media (max-width: 768px) {
            .auth-container {
                padding: 32px 24px;
                margin: 16px;
            }
            
            .auth-title {
                font-size: 2em !important;
            }
            
            .system-stats {
                grid-template-columns: 1fr;
            }
        }
        
        @media (max-width: 480px) {
            .auth-container {
                padding: 24px 20px;
            }
            
            .auth-title {
                font-size: 1.8em !important;
            }
            
            div[data-testid="stRadio"] {
                flex-direction: column !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)

def auth_page():
    """로그인/회원가입 페이지"""
    
    # 데이터베이스 초기화
    if not setup_database():
        st.error("시스템 초기화에 실패했습니다. 잠시 후 다시 시도해주세요.")
        if st.button("🔄 다시 시도"):
            st.rerun()
        return
    
    # CSS 스타일 적용
    auth_css()

    # 통합된 메인 컨테이너 (제목 + 폼을 하나로)
    st.markdown("""
    <div class="auth-container">
        <h1 class="auth-title">🌿 웰커밍 투어 시스템</h1>
        <p class="auth-subtitle">당신만의 맞춤형 힐링 여행을 찾아보세요</p>
    """, unsafe_allow_html=True)

    # 로그인/회원가입 선택 (컨테이너 내부에서)
    choice = st.radio(
        "선택", 
        ["로그인", "회원가입"], 
        horizontal=True, 
        label_visibility="collapsed",
        key="auth_choice"
    )

    # 강제 로그인 모드 처리 (세션에서 설정된 경우)
    if 'choice_radio' in st.session_state and st.session_state.choice_radio == "로그인":
        choice = "로그인"
        del st.session_state.choice_radio

    if choice == "로그인":
        st.markdown("<h2 style='color: #2C3E50; text-align: center; margin: 24px 0 16px 0; font-weight: 700;'>🔐 로그인</h2>", unsafe_allow_html=True)
        
        # 로그인 폼
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
            
            submitted = st.form_submit_button("🚀 로그인", use_container_width=True)
            
            if submitted:
                if not username or not password:
                    st.error("❌ 아이디와 비밀번호를 모두 입력해주세요.")
                else:
                    # 로딩 표시
                    with st.spinner("인증 확인 중..."):
                        time.sleep(0.5)  # 사용자 경험을 위한 지연
                        
                        if verify_user_credentials(username, password):
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.session_state.reset_survey_flag = True
                            
                            st.success("✅ 로그인 성공! 웰니스 여행 추천을 시작합니다.")
                            st.balloons()
                            
                            # 잠시 후 홈으로 이동
                            time.sleep(1.5)
                            st.switch_page("pages/03_home.py")
                        else:
                            st.error("❌ 아이디 또는 비밀번호가 잘못되었습니다.")
        
        # 데모 계정 안내
        st.markdown("""
        <div class="demo-info">
            <h4>🎯 체험용 데모 계정</h4>
            <p style="margin: 6px 0;">
                <strong>아이디:</strong> wellness<br>
                <strong>비밀번호:</strong> 1234
            </p>
            <p style="margin: 6px 0 0 0; font-size: 0.9em; opacity: 0.8;">
                💡 즉시 체험해보고 싶다면 위 데모 계정을 사용하세요!
            </p>
        </div>
        """, unsafe_allow_html=True)

    elif choice == "회원가입":
        st.markdown("<h2 style='color: #2C3E50; text-align: center; margin: 24px 0 16px 0; font-weight: 700;'>📝 회원가입</h2>", unsafe_allow_html=True)
        
        # 회원가입 폼
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
            
            submitted = st.form_submit_button("✨ 가입하기", use_container_width=True)
            
            if submitted:
                # 입력 검증
                if not new_username or not new_password or not confirm_password:
                    st.error("❌ 모든 필드를 입력해주세요.")
                elif len(new_username) < 4:
                    st.warning("⚠️ 아이디는 4자 이상이어야 합니다.")
                elif len(new_password) < 4:
                    st.warning("🔒 비밀번호는 4자 이상이어야 합니다.")
                elif new_password != confirm_password:
                    st.error("❌ 비밀번호가 일치하지 않습니다.")
                else:
                    # 계정 생성 시도
                    with st.spinner("계정 생성 중..."):
                        time.sleep(0.5)
                        
                        success, message = create_user_account(new_username, new_password)
                        
                        if success:
                            st.success(f"🎉 {message}")
                            st.info("이제 로그인할 수 있습니다!")
                            
                            # 로그인 모드로 전환
                            st.session_state.choice_radio = "로그인"
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")

    # 컨테이너 닫기 태그
    st.markdown("</div>", unsafe_allow_html=True)
    # 시스템 소개
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.8); border-radius: 12px; padding: 20px; margin: 20px 0; text-align: center; backdrop-filter: blur(10px); border: 2px solid rgba(52, 152, 219, 0.2);">
        <h4 style="color: #2C3E50; margin-bottom: 12px; font-size: 1.2em;">🌟 새로운 2.0 시스템</h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-top: 16px;">
            <div style="text-align: center;">
                <div style="font-size: 1.8em; margin-bottom: 6px;">🔬</div>
                <div style="color: #2C3E50; font-size: 0.85em; line-height: 1.4;">
                    <strong>과학적 근거</strong><br>
                    실제 데이터 기반<br>
                    요인분석 적용
                </div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 1.8em; margin-bottom: 6px;">🎯</div>
                <div style="color: #2C3E50; font-size: 0.85em; line-height: 1.4;">
                    <strong>정밀 분류</strong><br>
                    12개 요인<br>
                    8개 클러스터
                </div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 1.8em; margin-bottom: 6px;">🚀</div>
                <div style="color: #2C3E50; font-size: 0.85em; line-height: 1.4;">
                    <strong>맞춤 추천</strong><br>
                    개인화된<br>
                    관광지 추천
                </div>
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
        # 이미 로그인된 경우 홈으로 리다이렉트
        try:
            st.switch_page("pages/03_home.py")
        except Exception as e:
            st.error(f"페이지 이동 중 오류: {e}")
            # 폴백: 로그인 상태 초기화 후 다시 시작
            st.session_state.logged_in = False
            st.rerun()
    else:
        # 로그인 페이지 표시
        try:
            auth_page()
        except Exception as e:
            st.error("❌ 시스템 오류가 발생했습니다.")
            st.exception(e)
            
            # 복구 옵션
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