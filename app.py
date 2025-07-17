# app.py (웰니스 투어 추천 시스템 - 로그인 전용) - 개선된 버전

import streamlit as st
import sqlite3
import hashlib

# --- 데이터베이스 설정 ---
def setup_database():
    conn = sqlite3.connect('wellness_users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT)''')
    conn.commit()
    conn.close()

def hash_password(password):
    """비밀번호를 SHA256 해시로 변환합니다."""
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="웰커밍 투어성향 테스트 - 로그인",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 로그인 UI 스타일 (개선된 버전) ---
def auth_css():
    st.markdown("""
    <style>
        /* Streamlit 기본 UI 숨기기 */
        [data-testid="stHeader"], 
        [data-testid="stSidebar"], 
        [data-testid="stSidebarNav"],
        [data-testid="collapsedControl"],
        footer { 
            display: none !important; 
        }
        
        /* 앱 배경 그라데이션 */
        [data-testid="stAppViewContainer"] > .main {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #4CAF50 100%);
            background-size: cover;
            position: relative;
            min-height: 100vh;
        }

        /* 메인 컨테이너를 Flexbox로 중앙 정렬 */
        .main .block-container {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            width: 100%;
            padding: 0 !important;
            margin: 0 !important;
        }

        /* 로그인 폼 컨테이너 */
        div[data-testid="stHorizontalBlock"] > div:nth-child(2) > div[data-testid="stVerticalBlock"] {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border: 2px solid rgba(255, 255, 255, 0.2);
            padding: 50px 40px;
            border-radius: 20px;
            width: 100%;
            max-width: 400px;
            text-align: center;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
        }
        
        div[data-testid="stHorizontalBlock"] > div:nth-child(2) > div[data-testid="stVerticalBlock"]:hover {
            transform: translateY(-5px);
            box-shadow: 0 35px 70px rgba(0, 0, 0, 0.3);
        }
        
        /* 제목 스타일 */
        h1 { 
            font-size: 2.5em; 
            color: #ffffff; 
            font-weight: 700; 
            margin-bottom: 30px; 
            letter-spacing: 2px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        /* 로그인/회원가입 선택 라디오 버튼 스타일 */
        div[data-testid="stRadio"] {
            display: flex; 
            justify-content: center; 
            margin-bottom: 30px;
        }
        
        div[data-testid="stRadio"] > div {
            display: flex;
            gap: 10px;
        }
        
        div[data-testid="stRadio"] label {
            padding: 12px 25px; 
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 25px; 
            margin: 0 8px; 
            transition: all 0.3s ease;
            background-color: rgba(255,255,255,0.1); 
            color: rgba(255,255,255,0.8);
            font-weight: 600;
            cursor: pointer;
            backdrop-filter: blur(10px);
        }
        
        div[data-testid="stRadio"] label:hover {
            background-color: rgba(255,255,255,0.2);
            border-color: rgba(255,255,255,0.5);
            transform: translateY(-2px);
        }
        
        div[data-testid="stRadio"] input:checked + div {
            background: linear-gradient(45deg, #4CAF50, #66BB6A) !important;
            color: white !important; 
            border-color: #4CAF50 !important;
            box-shadow: 0 8px 25px rgba(76, 175, 80, 0.3);
        }

        /* 입력 필드 스타일 */
        div[data-testid="stTextInput"] input {
            background: rgba(255, 255, 255, 0.15) !important; 
            border: 2px solid rgba(255, 255, 255, 0.3) !important;
            border-radius: 15px !important; 
            color: #ffffff !important;
            padding: 15px 20px !important; 
            transition: all 0.3s ease !important;
            font-size: 16px !important;
            backdrop-filter: blur(10px) !important;
        }
        
        div[data-testid="stTextInput"] input:focus {
            border-color: #4CAF50 !important;
            box-shadow: 0 0 20px rgba(76, 175, 80, 0.4) !important;
            background: rgba(255, 255, 255, 0.2) !important;
        }
        
        div[data-testid="stTextInput"] input::placeholder {
            color: rgba(255, 255, 255, 0.6) !important;
        }
        
        /* 버튼 스타일 - 박스 완전 제거 */
        div[data-testid="stButton"] > button {
            width: 100% !important; 
            padding: 15px 0 !important; 
            background: linear-gradient(45deg, #4CAF50, #66BB6A) !important;
            border: none !important;
            outline: none !important;
            border-radius: 15px !important; 
            color: white !important; 
            font-weight: 700 !important; 
            font-size: 18px !important;
            transition: all 0.3s ease !important;
            cursor: pointer !important;
            box-shadow: 0 8px 25px rgba(76, 175, 80, 0.3) !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            margin: 10px 0 !important;
        }
        
        div[data-testid="stButton"] > button:hover {
            background: linear-gradient(45deg, #388E3C, #4CAF50) !important;
            transform: translateY(-3px) !important;
            box-shadow: 0 12px 35px rgba(76, 175, 80, 0.4) !important;
        }
        
        div[data-testid="stButton"] > button:active {
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 20px rgba(76, 175, 80, 0.3) !important;
        }
        
        div[data-testid="stButton"] > button:focus {
            outline: none !important;
            border: none !important;
            box-shadow: 0 8px 25px rgba(76, 175, 80, 0.3), 0 0 0 3px rgba(76, 175, 80, 0.2) !important;
        }
        
        /* 부제목 스타일 */
        h2 {
            color: #ffffff;
            font-size: 1.8em;
            font-weight: 600;
            margin-bottom: 25px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }
        
        /* 설명 텍스트 스타일 */
        p {
            color: rgba(255,255,255,0.9);
            font-size: 1.1em;
            line-height: 1.6;
            margin-bottom: 20px;
        }
        
        /* 데모 계정 안내 스타일 */
        div[data-testid="stAlert"] {
            background: rgba(255, 255, 255, 0.1) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 12px !important;
            color: rgba(255,255,255,0.9) !important;
            backdrop-filter: blur(10px) !important;
        }
        
        /* 성공/에러 메시지 스타일 */
        .stSuccess, .stError {
            border-radius: 12px !important;
            backdrop-filter: blur(10px) !important;
        }
        
        /* 반응형 디자인 */
        @media (max-width: 768px) {
            div[data-testid="stHorizontalBlock"] > div:nth-child(2) > div[data-testid="stVerticalBlock"] {
                padding: 30px 25px;
                margin: 20px;
            }
            
            h1 {
                font-size: 2em;
            }
            
            div[data-testid="stButton"] > button {
                padding: 12px 0 !important;
                font-size: 16px !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)

# --- 로그인/회원가입 페이지 함수 ---
def auth_page():
    setup_database()
    auth_css() 

    left_space, form_col, right_space = st.columns((1.2, 1.2, 1.2))

    with form_col:
        # 웰니스 투어 로고 및 제목
        st.markdown('<h1 class="wellness-title">🌿 웰커밍 투어추천</h1>', unsafe_allow_html=True)
        st.markdown('<p style="color: rgba(255,255,255,0.8); font-size: 1.2em; margin-bottom: 30px;">당신만의 맞춤형 힐링 여행을 찾아보세요</p>', unsafe_allow_html=True)
        
        choice = st.radio("choice", ["로그인", "회원가입"], horizontal=True, label_visibility="collapsed")
        
        if 'choice_radio' in st.session_state and st.session_state.choice_radio == "로그인":
            choice = "로그인"
            del st.session_state.choice_radio

        if choice == "로그인":
            st.markdown("<h2>🔐 로그인</h2>", unsafe_allow_html=True)
            username = st.text_input("아이디", key="login_user", placeholder="아이디를 입력하세요")
            password = st.text_input("비밀번호", type="password", key="login_pass", placeholder="비밀번호를 입력하세요")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("로그인 🚀", key="login_btn"):
                    is_authenticated = False
                    if username == "wellness" and password == "1234":
                        is_authenticated = True
                    else:
                        conn = sqlite3.connect('wellness_users.db')
                        c = conn.cursor()
                        c.execute('SELECT password FROM users WHERE username = ?', (username,))
                        db_password_hash = c.fetchone()
                        conn.close()

                        if db_password_hash and db_password_hash[0] == hash_password(password):
                            is_authenticated = True
                    
                    if is_authenticated:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.reset_survey_flag = True
                        st.success("✅ 로그인 성공! 웰니스 여행 추천을 시작합니다.")
                        st.balloons()
                        st.switch_page("pages/01_questionnaire.py")
                    else:
                        st.error("❌ 아이디 또는 비밀번호가 잘못되었습니다.")
            
            # 데모 계정 안내
            st.markdown("---")
            st.info("🎯 **데모 계정**: 아이디 `wellness`, 비밀번호 `1234`")

        elif choice == "회원가입":
            st.markdown("<h2>📝 회원가입</h2>", unsafe_allow_html=True)
            new_username = st.text_input("사용할 아이디", key="signup_user", placeholder="아이디를 입력하세요")
            new_password = st.text_input("사용할 비밀번호", type="password", key="signup_pass", placeholder="비밀번호를 입력하세요")
            confirm_password = st.text_input("비밀번호 확인", type="password", key="signup_confirm", placeholder="비밀번호를 다시 입력하세요")

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("가입하기 ✨", key="signup_btn"):
                    if new_password == confirm_password:
                        if len(new_password) >= 4:
                            try:
                                conn = sqlite3.connect('wellness_users.db')
                                c = conn.cursor()
                                c.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                                         (new_username, hash_password(new_password)))
                                conn.commit()
                                st.success("🎉 회원가입 성공! 이제 로그인해주세요.")
                                st.session_state.choice_radio = "로그인" 
                                st.rerun()
                            except sqlite3.IntegrityError:
                                st.error("⚠️ 이미 존재하는 아이디입니다.")
                            finally:
                                conn.close()
                        else:
                            st.warning("🔒 비밀번호는 4자 이상이어야 합니다.")
                    else:
                        st.error("❌ 비밀번호가 일치하지 않습니다.")

# --- 메인 라우터 ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    st.switch_page("pages/01_questionnaire.py")
else:
    auth_page()