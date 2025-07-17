# pages/02_analyzing.py (웰니스 분석 중 페이지)

import streamlit as st
import time
import base64
from pathlib import Path
from utils import check_access_permissions

# --- 페이지 설정 ---
st.set_page_config(
    page_title="분석 중...",
    page_icon="🔬",
    layout="wide"
)

# 접근 권한 확인 (기본값: 로그인 + 설문 완료 둘 다 확인)
check_access_permissions()

# --- 모든 페이지 공통 UI 숨김 CSS 및 분석 페이지 스타일 ---
st.markdown("""
    <style>
        /* 웰니스 테마 배경 그라데이션 */
        [data-testid="stAppViewContainer"] > .main {
            background: linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 50%, #A5D6A7 100%);
            min-height: 100vh;
        }
        
        /* 모든 페이지 공통: 헤더, 사이드바 내비게이션, 사이드바 컨트롤 버튼, 푸터 숨기기 */
        [data-testid="stHeader"] { display: none; }
        [data-testid="stSidebarNav"] { display: none; } 
        [data-testid="stSidebar"] { display: none; } 
        [data-testid="collapsedControl"] { display: none; } 
        footer { display: none; } 

        /* 중앙 정렬을 위한 메인 컨테이너 */
        .main .block-container {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            width: 100%;
            padding: 30px 10px !important;
        }
        
        /* 분석 카드 스타일 */
        .analyzing-card {
            background: rgba(100, 255, 71, 0.2);
            backdrop-filter: blur(25px);
            border: 3px solid #4CAF50;
            border-radius: 30px;
            padding: 40px 30px;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
            max-width: 600px;
            width: 90%;
            margin: 0 auto;
            position: relative;
            overflow: hidden;
        }
        
        @keyframes borderGlow {
            0% { opacity: 0.3; transform: scale(1); }
            100% { opacity: 0.6; transform: scale(1.01); }
        }
        
        /* 아이콘 회전 애니메이션 */
        @keyframes spin {
            0% { transform: rotate(0deg) scale(1); }
            25% { transform: rotate(90deg) scale(1.1); }
            50% { transform: rotate(180deg) scale(1); }
            75% { transform: rotate(270deg) scale(1.1); }
            100% { transform: rotate(360deg) scale(1); }
        }
        
        .spinning-brain {
            animation: spin 4s linear infinite;
            font-size: 70px;
            display: inline-block;
            margin-bottom: 15px;
            filter: drop-shadow(0 4px 8px rgba(76, 175, 80, 0.3));
        }

        /* 텍스트 점(.) 애니메이션 */
        @keyframes ellipsis {
            0% { content: "."; }
            33% { content: ".."; }
            66% { content: "..."; }
            100% { content: "."; }
        }
        
        .analyzing-text::after {
            content: ".";
            animation: ellipsis 1.5s infinite;
            display: inline-block;
            width: 2em;
            text-align: left;
        }

        /* 제목 스타일 */
        .analyzing-title {
            text-align: center;
            color: #2E7D32;
            font-size: 2.4em;
            font-weight: 800;
            margin-top: 20px;
            margin-bottom: 35px;
        }
        
        /* 설명 텍스트 */
        .analyzing-description {
            color: #333;
            font-size: 1.05em;
            font-weight: 600;
            margin-top: 20px;
            margin-bottom: 35px;
            line-height: 1.7;
            opacity: 0.9;
        }
            
        /* 진행률 바 외부 컨테이너가 analyzing-card와 같은 폭을 갖도록 설정 */
        .progress-wrapper {
            max-width: 600px;
            width: 90%;
            margin: 0 auto;  /* 중앙 정렬 */
        }
            
        /* 진행률 컨테이너 */
        .progress-container {
            background: rgba(76, 175, 80, 0.15);
            border-radius: 15px;
            padding: 0px;
            margin: 0 0;
            box-shadow: inset 0 2px 8px rgba(76, 175, 80, 0.2);
        }
        
        /* 진행률 바 */
        .progress-bar {
            background: linear-gradient(45deg, #4CAF50, #66BB6A);
            height: 12px;
            border-radius: 8px;
            transition: all 0.5s ease;
            box-shadow: 0 2px 8px rgba(76, 175, 80, 0.4);
            position: relative;
            overflow: hidden;
        }
        
        @keyframes progressShine {
            0% { left: -100%; }
            50% { left: 100%; }
            100% { left: 100%; }
        }
        
        /* 진행률 텍스트 */
        .progress-text {
            text-align: left;
            color: #2E7D32;
            font-weight: 700;
            font-size: 1.1em;
            margin-top: 20px;
            margin: 12px 0;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }
        
        .status-wrapper {
            max-width: 600px;
            width: 90%;
            margin: 0 auto;  /* 중앙 정렬 */
        }
        
        /* 상태 메시지 */
        .status-message {
            color: #2E7D32;
            font-size: 1.0em;
            font-weight: 600;
            margin: 20px 0;
            padding: 15px 20px;
            background: rgba(76, 175, 80, 0.1);
            border-radius: 12px;
            border-left: 5px solid #4CAF50;
            box-shadow: 0 3px 12px rgba(76, 175, 80, 0.15);
            transition: all 0.3s ease;
        }
        
        /* 완료 상태 메시지 */
        .status-message.completed {
            background: linear-gradient(135deg, rgba(76, 175, 80, 0.2), rgba(129, 199, 132, 0.15));
            border-left-color: #4CAF50;
            box-shadow: 0 4px 16px rgba(76, 175, 80, 0.25);
            transform: translateY(-2px);
        }
        
        
        
        /* 반응형 디자인 */
        @media (max-width: 768px) {
            .analyzing-card {
                padding: 40px 30px;
                max-width: 95%;
            }
            
            .analyzing-title {
                font-size: 2em;
            }
            
            .spinning-brain {
                font-size: 70px;
            }
            
            .analyzing-description {
                font-size: 1.1em;
            }
        }
        
        /* 작은 화면 대응 */
        @media (max-width: 480px) {
            .analyzing-card {
                padding: 30px 20px;
            }
            
            .analyzing-title {
                font-size: 1.8em;
            }
            
            .spinning-brain {
                font-size: 60px;
            }
        }
    </style>
    """, unsafe_allow_html=True)

# --- 직접 접근 방지 로직 (로그인 여부 및 설문 완료 여부 확인) ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("⚠️ 로그인 후 이용해주세요.")
    st.page_link("app.py", label="로그인 페이지로 돌아가기", icon="🏠")
    st.stop()

if 'survey_completed' not in st.session_state or not st.session_state.survey_completed:
    st.error("⚠️ 설문을 먼저 완료해주세요.")
    st.page_link("pages/01_questionnaire.py", label="설문 페이지로 돌아가기", icon="🏠")
    st.stop()

# --- 메인 로직 ---
def analyzing_page():
    # 분석 중 화면 구성 (완전 중앙 정렬)
    st.markdown("""
    <div class="analyzing-card">
        <div class="spinning-brain">🧠</div>
        <h1 class="analyzing-title">
            <span class="analyzing-text">맟춤 웰니스 성향 분석중</span>
        </h1>
        <p class="analyzing-description">
            답변해 주신 내용을 바탕으로<br>
            당신만의 맞춤형 웰니스 여행지를 찾고 있습니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 진행률 바와 상태 메시지를 위한 플레이스홀더
    progress_placeholder = st.empty()
    status_placeholder = st.empty()

    # 분석 단계들
    analysis_steps = [
        ("🎯 연령대 및 여행 빈도 분석", 15),
        ("🌟 여행 목적 및 선호도 평가", 35),
        ("💚 웰니스 관심도 측정", 55),
        ("🏃‍♀️ 활동 성향 및 여행 스타일 확인", 75),
        ("💰 예산 범위 및 최적 매칭", 90),
        ("✨ 최종 웰니스 성향 분류", 100),
    ]

    # 분석 시뮬레이션
    for step_text, percentage in analysis_steps:
        with progress_placeholder.container():
            st.markdown(f"""
            <div class="progress-wrapper">
                <p class="progress-text">
                    <br>분석 진행률: {percentage}% 🌿
                </p>
                <div class="progress-container">
                    <div class="progress-bar" style="width: {percentage}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with status_placeholder.container():
            st.markdown(f"""
            <div class="status-wrapper">
                <div class="status-message">
                    <strong>진행 단계:</strong> {step_text}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        time.sleep(1.2)  # 각 단계별 대기 시간

    # 분석 완료
    with status_placeholder.container():
        st.markdown("""
        <div class="status-wrapper">
            <div class="status-message completed">
                ✅ <strong>분석이 완료되었습니다!</strong> 잠시 후 결과 페이지로 이동합니다.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with progress_placeholder.container():
        st.markdown("""
        <div class="progress-wrapper">
            <p class="progress-text">
                <br>분석 완료! 100% 🎉
            </p>
            <div class="progress-container">
                <div class="progress-bar" style="width: 100%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    time.sleep(1.5)

    # 결과 페이지로 이동
    st.switch_page("pages/04_recommendations.py")

if __name__ == "__main__":
    analyzing_page()
else:
    analyzing_page()