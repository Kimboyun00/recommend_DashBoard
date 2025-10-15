# app.py (웰니스 투어 추천 시스템 - 로그인 전용)

import streamlit as st
import sqlite3
import hashlib
from utils import apply_global_styles

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

# 전역 스타일 적용
apply_global_styles()

# --- 로그인 UI 스타일 ---
def auth_css():
    st.markdown("""
    <style>
        /* Streamlit 기본 UI 숨기기 */
        [data-testid="stHeader"], [data-testid="stSidebar"], footer { display: none; }
        
        /* 앱 배경 그라데이션 */
        [data-testid="stAppViewContainer"] > .main {
            background-image: linear-gradient(to top right, #0a192f, #1e3a5f, #4a6da7);
            background-size: cover;
        }

        /* st.columns를 포함하는 메인 블록을 Flexbox로 만들어 수직 중앙 정렬 */
        .main .block-container {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            width: 100%;
            padding: 0 !important;
        }

        /* 로그인 폼 컨테이너 (st.columns의 중앙 컬럼을 타겟팅) */
        div[data-testid="stHorizontalBlock"] > div:nth-child(2) > div[data-testid="stVerticalBlock"] {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 40px;
            border-radius: 15px;
            width: 100%;
            text-align: center;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }
        
        h1 { font-size: 2.2em; color: #ffffff; font-weight: 600; margin-bottom: 25px; letter-spacing: 2px; }
        
        /* 로그인/회원가입 선택 라디오 버튼 스타일 */
        div[data-testid="stRadio"] {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 25px;
            width: 100%;
        }

        /* 🔹 전체 라벨(제목)은 숨김 처리 */
        div[data-testid="stRadio"] > label {
            display: none !important;
        }
        /* 🔹 옵션 라벨 버튼 스타일 */
        div[data-testid="stRadio"] > div[role="radiogroup"] {
            display: flex;
            justify-content: center;
            gap: 10px; /* 🔹 버튼 간격 */
        }
        /* 🔹 옵션 라벨만 버튼처럼 스타일 적용 */
        div[data-testid="stRadio"] > div[role="radiogroup"] > label {
            padding: 8px 20px;
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            margin: 0 5px;
            transition: all 0.3s;
            background-color: transparent;
            color: rgba(255,255,255,0.7);
        }

        /* 🔹 선택된 옵션 스타일 */
        div[data-testid="stRadio"] > div[role="radiogroup"] > label[aria-checked="true"] {
            background-color: rgba(0, 198, 255, 0.3);
            color: black !important;
            border-color: #00c6ff;
        }

        div[data-testid="stTextInput"] input {
            background-color: rgba(255, 255, 255, 0.1); 
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px; 
            color: #000000 !important; /* 검정색으로 유지 */
            padding: 12px; 
            transition: all 0.3s;
        }
        
        div[data-testid="stButton"] > button {
            width: 100% !important;
            padding: 12px 40px;
            background: linear-gradient(45deg, #4CAF50, #8BC34A);
                border: none;
                border-radius: 10px;
                color: white;
            font-weight: bold;
            transition: all 0.3s;
            margin-top: 10px;
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
        st.markdown("""
        <style>
        .wellness-title {
            font-size: 34px !important;
            font-weight: bold;
        }
        </style>
        <h1 class="wellness-title">🌿 WELLNESS TOUR</h1>
        """, unsafe_allow_html=True)
        st.markdown('<p style="color: rgba(76,175,80,0.8); font-size: 1.2em; margin-bottom: 30px;">당신만의 맞춤형 힐링 여행을 찾아보세요</p>', unsafe_allow_html=True)
        
        choice = st.radio("choice", ["로그인", "회원가입"], horizontal=True, label_visibility="collapsed")
        
        if 'choice_radio' in st.session_state and st.session_state.choice_radio == "로그인":
            choice = "로그인"
            del st.session_state.choice_radio

        if choice == "로그인":
            st.markdown("<h2>🔐 로그인</h2>", unsafe_allow_html=True)
            username = st.text_input("아이디", key="login_user", placeholder="아이디를 입력하세요")
            password = st.text_input("비밀번호", type="password", key="login_pass", placeholder="비밀번호를 입력하세요")
            
            # 테스트 계정 정보 스타일 적용하여 표시
            st.markdown("""
            <div style="
                margin: 20px 0;
                padding: 15px;
                background: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(0, 0, 0, 0.3);
                border-radius: 10px;
                backdrop-filter: blur(10px);">
                <p style="
                    color: #000000;
                    font-size: 0.9em;
                    font-weight: 500;
                    margin: 0;
                    text-align: left;">
                    🔑 테스트 계정 정보<br>
                    ㆍ아이디: <span style="color: #2E7D32; font-weight: 600;">wellness</span><br>
                    ㆍ비밀번호: <span style="color: #2E7D32; font-weight: 600;">1234</span>
                </p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("로그인", key="login_btn"):
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

        elif choice == "회원가입":
            st.markdown("<h2>📝 회원가입</h2>", unsafe_allow_html=True)
            new_username = st.text_input("사용할 아이디", key="signup_user", placeholder="아이디를 입력하세요")
            new_password = st.text_input("사용할 비밀번호", type="password", key="signup_pass", placeholder="비밀번호를 입력하세요")
            confirm_password = st.text_input("비밀번호 확인", type="password", key="signup_confirm", placeholder="비밀번호를 다시 입력하세요")

            
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