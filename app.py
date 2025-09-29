# app.py — Login-only entry (hardened, sidebar untouched)
import streamlit as st
import sqlite3, os, secrets, hashlib
from utils import apply_global_styles

# ===== Security helpers =====
ITER = 130_000  # PBKDF2 iterations

def make_salt() -> str:
    return secrets.token_hex(16)

def hash_pw(password: str, salt: str) -> str:
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt), ITER)
    return dk.hex()

def verify_pw(password: str, salt: str, pw_hash: str) -> bool:
    return hash_pw(password, salt) == pw_hash

# ===== Database =====
DB_PATH = 'wellness_users.db'

def setup_database():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # New schema (salted): username, pw_hash, salt
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        pw_hash  TEXT NOT NULL,
        salt     TEXT NOT NULL
    )''')
    # Backward-compat migration
    try:
        c.execute("SELECT username, password FROM users LIMIT 1")
        row = c.fetchone()
        if row is not None:
            c.execute("PRAGMA table_info(users)")
            cols = [r[1] for r in c.fetchall()]
            if 'pw_hash' not in cols:
                c.execute("ALTER TABLE users ADD COLUMN pw_hash TEXT")
            if 'salt' not in cols:
                c.execute("ALTER TABLE users ADD COLUMN salt TEXT")
    except sqlite3.OperationalError:
        pass
    conn.commit(); conn.close()

# ===== Page config & styles =====
st.set_page_config(
    page_title='웰커밍 투어성향 테스트 - 로그인',
    page_icon='🌿',
    layout='wide',
    initial_sidebar_state='collapsed'  # keep sidebar hidden
)
apply_global_styles()

# ===== Auth CSS (sidebar remains hidden) =====
def auth_css():
    st.markdown('''
    <style>
      [data-testid="stHeader"], [data-testid="stSidebar"], footer { display:none; }
      [data-testid="stAppViewContainer"] > .main { background-image:linear-gradient(45deg,#0a192f,#1e3a5f,#4a6da7); }
      .main .block-container { display:flex; min-height:100vh; align-items:center; }
      div[data-testid="stHorizontalBlock"] > div:nth-child(2) > div[data-testid="stVerticalBlock"]{
        background:rgba(255,255,255,.05); backdrop-filter:blur(10px);
        border:1px solid rgba(255,255,255,.1); padding:40px; border-radius:16px;
        width:100%; text-align:center; box-shadow:0 8px 32px rgba(0,0,0,.37);
      }
      h1 { font-size:2.2rem; color:#fff; font-weight:700; margin-bottom:18px; }
      .muted { color:rgba(255,255,255,.8); font-size:.95rem; margin-bottom:8px; }
      div[data-testid="stRadio"]{ display:flex; justify-content:center; gap:8px; margin:10px 0 24px; }
      .stTextInput input, .stPassword input { background:rgba(255,255,255,.1); color:#fff; border-radius:10px; }
      .stButton>button { background:#6aa6ff; color:#0b1020; font-weight:800; border-radius:12px; }
    </style>
    ''', unsafe_allow_html=True)

# ===== Simple lockout =====
def too_many_attempts() -> bool:
    n = st.session_state.get('fail_count', 0)
    return n >= 7

# ===== Auth Page =====
def auth_page():
    setup_database(); auth_css()
    left, mid, right = st.columns((1.2, 1.2, 1.2))
    with mid:
        st.markdown('<h1>🌿 웰니스 여행 대시보드</h1>', unsafe_allow_html=True)
        st.markdown('<div class="muted">로그인 후 맞춤 추천을 시작합니다</div>', unsafe_allow_html=True)

        choice = st.radio("", ["로그인", "회원가입"], horizontal=True, label_visibility='collapsed', key='choice_radio')

        if choice == '로그인':
            with st.form('login_form'):
                user = st.text_input('아이디', key='login_user')
                pw = st.text_input('비밀번호', type='password', key='login_pass')
                submitted = st.form_submit_button('로그인 🚀', use_container_width=True)

            if submitted:
                if too_many_attempts():
                    st.error('잠시 후 다시 시도하세요.')
                    return
                conn = sqlite3.connect(DB_PATH); c = conn.cursor()
                c.execute('SELECT pw_hash, salt FROM users WHERE username=?', (user,))
                row = c.fetchone()
                if row and verify_pw(pw, row[1], row[0]):
                    st.session_state.logged_in = True
                    st.session_state.fail_count = 0
                    st.success('✅ 로그인 성공!')
                    st.switch_page('pages/01_questionnaire.py')
                else:
                    st.session_state.fail_count = st.session_state.get('fail_count', 0) + 1
                    st.error('❌ 아이디 또는 비밀번호가 잘못되었습니다.')
                conn.close()

        elif choice == '회원가입':
            with st.form('signup_form'):
                new_user = st.text_input('아이디', key='signup_user')
                new_pw = st.text_input('비밀번호', type='password', key='signup_pass')
                new_pw2 = st.text_input('비밀번호 확인', type='password', key='signup_confirm')
                submitted = st.form_submit_button('가입하기 ✨', use_container_width=True)
            if submitted and new_pw == new_pw2 and len(new_pw) >= 8:
                conn = sqlite3.connect(DB_PATH); c = conn.cursor()
                try:
                    salt = make_salt(); pw_hash = hash_pw(new_pw, salt)
                    c.execute('INSERT INTO users (username, pw_hash, salt) VALUES (?,?,?)', (new_user, pw_hash, salt))
                    conn.commit()
                    st.success('🎉 회원가입 성공! 로그인해 주세요.')
                except sqlite3.IntegrityError:
                    st.error('이미 존재하는 아이디입니다.')
                finally:
                    conn.close()

# ===== Router =====
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    st.switch_page('pages/01_questionnaire.py')
else:
    auth_page()