# pages/03_home.py (웰니스 홈 페이지)

import streamlit as st
import plotly.express as px
import pandas as pd
from utils import check_access_permissions, get_cluster_info, classify_wellness_type

# 로그인 체크
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("app.py")

# 페이지 설정
st.set_page_config(
    page_title="웰니스 투어 홈",
    page_icon="🌿",
    layout="wide"
)

# 접근 권한 확인 (홈페이지이므로 'home' 타입)
check_access_permissions('home')

# 웰니스 관광지 데이터
wellness_destinations = {
    "온천/스파": [
        {
            "name": "부산 해운대 스파랜드",
            "lat": 35.1584,
            "lon": 129.1604,
            "type": "온천/스파",
            "description": "천연 온천수와 다양한 스파 시설을 갖춘 복합 웰니스 센터",
            "website": "https://www.spaland.co.kr",
            "rating": 4.5,
            "price_range": "20,000-40,000원"
        },
        {
            "name": "충남 아산 온양온천",
            "lat": 36.7894,
            "lon": 127.0042,
            "type": "온천/스파",
            "description": "600년 역사의 전통 온천으로 유명한 천연 온천지",
            "website": "https://www.onyanghotspring.or.kr",
            "rating": 4.2,
            "price_range": "15,000-30,000원"
        }
    ],
    "자연치유": [
        {
            "name": "제주 한라산 국립공원",
            "lat": 33.3617,
            "lon": 126.5292,
            "type": "자연치유",
            "description": "한국 최고봉으로 산림욕과 트레킹이 가능한 자연 치유 공간",
            "website": "https://www.hallasan.go.kr",
            "rating": 4.7,
            "price_range": "무료"
        },
        {
            "name": "강원 설악산 국립공원",
            "lat": 38.1197,
            "lon": 128.4655,
            "type": "자연치유",
            "description": "아름다운 자연경관과 맑은 공기로 유명한 산악 치유 공간",
            "website": "https://www.knps.or.kr",
            "rating": 4.6,
            "price_range": "3,500원"
        }
    ],
    "요가/명상": [
        {
            "name": "경주 불국사",
            "lat": 35.7904,
            "lon": 129.3320,
            "type": "요가/명상",
            "description": "천년 고찰에서 체험하는 명상과 템플스테이 프로그램",
            "website": "https://www.bulguksa.or.kr",
            "rating": 4.8,
            "price_range": "50,000-100,000원 (템플스테이)"
        },
        {
            "name": "전남 순천만 국가정원",
            "lat": 34.8853,
            "lon": 127.5086,
            "type": "요가/명상",
            "description": "자연과 함께하는 힐링 요가 프로그램과 명상 공간",
            "website": "https://www.suncheonbay.go.kr",
            "rating": 4.4,
            "price_range": "8,000원"
        }
    ],
    "웰니스 리조트": [
        {
            "name": "강원 평창 알펜시아 리조트",
            "lat": 37.6565,
            "lon": 128.6719,
            "type": "웰니스 리조트",
            "description": "산악 경관과 함께하는 프리미엄 스파 & 웰니스 리조트",
            "website": "https://www.alpensia.com",
            "rating": 4.3,
            "price_range": "150,000-300,000원"
        },
        {
            "name": "경기 용인 에버랜드 스파",
            "lat": 37.2946,
            "lon": 127.2018,
            "type": "웰니스 리조트",
            "description": "테마파크와 연계된 대형 스파 & 웰니스 시설",
            "website": "https://www.everland.com",
            "rating": 4.1,
            "price_range": "30,000-60,000원"
        }
    ]
}

# 웰니스 테마 CSS
st.markdown("""
<style>
    /* 웰니스 테마 배경 그라데이션 */
    [data-testid="stAppViewContainer"] > .main {
        background: linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 50%, #A5D6A7 100%);
        min-height: 100vh;
    }
    
    /* 메인 컨테이너 */
    .main .block-container {
        padding: 2rem 3rem !important;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    /* 웰컴 카드 스타일 */
    .welcome-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(25px);
        border: 2px solid #4CAF50;
        border-radius: 25px;
        padding: 40px;
        margin: 20px 0;
        text-align: center;
        box-shadow: 0 12px 40px rgba(76, 175, 80, 0.2);
        transition: all 0.3s ease;
    }
    
    .welcome-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 16px 50px rgba(76, 175, 80, 0.25);
    }
    
    /* 기능 카드 스타일 */
    .feature-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 20px;
        padding: 35px 25px;
        margin: 15px 0;
        text-align: center;
        transition: all 0.4s ease;
        height: 280px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(76, 175, 80, 0.1), transparent);
        transition: all 0.6s ease;
    }
    
    .feature-card:hover::before {
        left: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 60px rgba(76, 175, 80, 0.3);
        background: rgba(255, 255, 255, 1);
        border-color: #4CAF50;
    }
    
    /* 제목 스타일 */
    .home-title {
        color: #2E7D32 !important;
        text-align: center;
        background: rgba(255, 255, 255, 0.95);
        padding: 25px 30px;
        border-radius: 20px;
        font-size: 2.8em !important;
        margin-bottom: 40px;
        font-weight: 800 !important;
        border: 3px solid #4CAF50;
        box-shadow: 0 10px 30px rgba(76, 175, 80, 0.2);
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        letter-spacing: 1px;
    }
    
    /* 통계 카드 */
    .stat-card {
        background: rgba(255, 255, 255, 0.95);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 18px;
        padding: 25px 20px;
        text-align: center;
        margin: 15px 0;
        transition: all 0.3s ease;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .stat-card:hover {
        border-color: #4CAF50;
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.25);
        transform: translateY(-3px);
        background: rgba(255, 255, 255, 1);
    }
    
    .stat-number {
        font-size: 2.8em;
        font-weight: 800;
        color: #2E7D32;
        margin-bottom: 8px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    .stat-label {
        color: #2E7D32;
        font-size: 1.2em;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    /* 클러스터 타입 카드 */
    .cluster-type-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 18px;
        padding: 25px;
        margin: 15px 0;
        transition: all 0.3s ease;
        text-align: center;
    }
    
    .cluster-type-card:hover {
        border-color: #4CAF50;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.2);
        transform: translateY(-2px);
    }
    
    /* 버튼 스타일 */
    div[data-testid="stButton"] > button {
        background: linear-gradient(45deg, #4CAF50, #66BB6A) !important;
        border: none !important;
        border-radius: 15px !important;
        color: white !important;
        font-weight: 700 !important;
        padding: 15px 30px !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3) !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    div[data-testid="stButton"] > button:hover {
        background: linear-gradient(45deg, #388E3C, #4CAF50) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.4) !important;
    }
    
    /* 섹션 제목 */
    .section-title {
        color: #2E7D32 !important;
        font-size: 2em;
        font-weight: 700;
        margin: 40px 0 25px 0;
        text-align: center;
        background: rgba(255, 255, 255, 0.9);
        padding: 15px 25px;
        border-radius: 15px;
        border-left: 5px solid #4CAF50;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.15);
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    /* 웰컴 메시지 텍스트 */
    .welcome-text {
        color: #2E7D32;
        font-size: 1.3em;
        line-height: 1.7;
        font-weight: 600;
        margin: 0;
    }
    
    .welcome-subtitle {
        color: #2E7D32;
        margin-bottom: 20px;
        font-size: 1.1em;
        font-weight: 600;
    }
    
    /* 사용자 정보 카드 */
    .user-info-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 18px;
        padding: 25px;
        margin: 15px 0;
        transition: all 0.3s ease;
        text-align: center;
    }
    
    .user-info-card:hover {
        border-color: #4CAF50;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.2);
        transform: translateY(-2px);
    }
    
    .user-name {
        color: #2E7D32;
        font-size: 1.3em;
        font-weight: 700;
        margin: 0;
    }
    
    .status-text {
        font-size: 1.2em;
        font-weight: 700;
        margin: 0;
    }
    
    /* 경고 메시지 스타일 */
    div[data-testid="stAlert"] {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid #FF8A65 !important;
        border-radius: 12px !important;
        color: #2E7D32 !important;
        font-weight: 600 !important;
    }
    
    /* 성공 메시지 스타일 */
    div[data-testid="stAlert"][data-baseweb="notification"] {
        border-color: #4CAF50 !important;
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(129, 199, 132, 0.05)) !important;
    }
    
    /* 차트 컨테이너 */
    .chart-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 20px;
        padding: 25px;
        margin: 20px 0;
        transition: all 0.3s ease;
    }
    
    .chart-container:hover {
        border-color: #4CAF50;
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.2);
    }
    
    /* 기본 UI 숨김 */
    [data-testid="stHeader"] { display: none; }
    [data-testid="stSidebarNav"] { display: none; }
    [data-testid="stSidebar"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }
    footer { display: none; }
    
    /* 반응형 디자인 */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem 1.5rem !important;
        }
        
        .home-title {
            font-size: 2.2em !important;
            padding: 20px 25px !important;
        }
        
        .feature-card {
            height: 240px;
            padding: 25px 20px;
        }
        
        .stat-number {
            font-size: 2.4em;
        }
        
        .section-title {
            font-size: 1.6em;
            padding: 12px 20px;
        }
    }
</style>
""", unsafe_allow_html=True)

# 상단 메뉴
def top_menu():
    st.markdown('<h3 style="color: #2E7D32; text-align: center; margin-bottom: 20px;">🧭 빠른 메뉴</h3>', unsafe_allow_html=True)
    
    menu_col1, menu_col2, menu_col3, menu_col4, menu_col5 = st.columns(5)
    
    with menu_col1:
        if st.button("📝 설문조사", key="survey_btn"):
            st.switch_page("pages/01_questionnaire.py")
    
    with menu_col2:
        if st.button("📊 추천 결과", key="results_btn"):
            if 'survey_completed' in st.session_state and st.session_state.survey_completed:
                st.switch_page("pages/04_recommendations.py")
            else:
                st.warning("설문을 먼저 완료해주세요!")
    
    with menu_col3:
        if st.button("🗺️ 지도 보기", key="map_btn"):
            if 'survey_completed' in st.session_state and st.session_state.survey_completed:
                st.switch_page("pages/05_map_view.py")
            else:
                st.warning("설문을 먼저 완료해주세요!")
    
    with menu_col4:
        if st.button("📈 통계 정보", key="stats_btn"):
            st.switch_page("pages/06_statistics.py")
    
    with menu_col5:
        if st.button("🚪 로그아웃", key="logout_btn"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.switch_page("app.py")

# 메인 홈 페이지
def home_page():
    top_menu()
    
    # 메인 제목
    st.markdown('<h1 class="home-title">🌿 웰니스 관광 성향 진단 시스템</h1>', unsafe_allow_html=True)
    
    # 웰컴 메시지
    st.markdown(f"""
    <div class="welcome-card">
        <h2 class="welcome-subtitle">안녕하세요, {st.session_state.username}님! 👋</h2>
        <p class="welcome-text">
            8가지 질문으로 당신의 여행 성향을 정확하게 분석하고<br>
            개인 맞춤형 한국 관광지를 추천해드립니다.<br><br>
            AI 클러스터 분석을 통해 당신만의 완벽한 여행을 찾아보세요.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 사용자 정보 및 설문 결과 표시
    st.markdown("---")
    user_col1, user_col2 = st.columns(2)
    
    with user_col1:
        st.markdown(f"""
        <div class="user-info-card">
            <h3 style="color: #2E7D32; margin-bottom: 10px;">👤 사용자 정보</h3>
            <p class="user-name">{st.session_state.username}님 환영합니다!</p>
        </div>
        """, unsafe_allow_html=True)
    
    with user_col2:
        if 'survey_completed' in st.session_state and st.session_state.survey_completed:
            status_color = "#4CAF50"
            status_text = "✅ 설문 완료"
            
            # 클러스터 결과가 있다면 표시
            if 'score_breakdown' in st.session_state and 'cluster_id' in st.session_state.score_breakdown:
                cluster_id = st.session_state.score_breakdown['cluster_id']
                cluster_info = get_cluster_info()
                if cluster_id in cluster_info:
                    cluster_name = cluster_info[cluster_id]['name']
                    status_text += f"<br><small>🎯 {cluster_name}</small>"
        else:
            status_color = "#FF8A65"
            status_text = "⏳ 설문 대기 중"
        
        st.markdown(f"""
        <div class="user-info-card">
            <h3 style="color: #2E7D32; margin-bottom: 10px;">📋 진행 상태</h3>
            <p class="status-text" style="color: {status_color};">{status_text}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 클러스터 유형 소개 (설문 완료된 경우)
    if 'survey_completed' in st.session_state and st.session_state.survey_completed:
        if 'score_breakdown' in st.session_state and 'cluster_id' in st.session_state.score_breakdown:
            cluster_id = st.session_state.score_breakdown['cluster_id']
            cluster_info = get_cluster_info()
            
            if cluster_id in cluster_info:
                cluster_data = cluster_info[cluster_id]
                st.markdown('<h2 class="section-title">🎯 당신의 여행 성향</h2>', unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="cluster-type-card" style="border-color: {cluster_data['color']};">
                    <h3 style="color: {cluster_data['color']}; margin-bottom: 15px;">
                        🏆 {cluster_data['name']}
                    </h3>
                    <p style="color: #2E7D32; font-weight: 600; margin-bottom: 20px;">
                        {cluster_data['description']}
                    </p>
                    <div style="margin: 15px 0;">
                        <strong style="color: #2E7D32;">주요 특성:</strong><br>
                        {' | '.join(cluster_data['characteristics'])}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # 통계 정보
    st.markdown('<h2 class="section-title">📊 웰니스 관광지 현황</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    # 전체 관광지 수 계산
    total_destinations = sum(len(places) for places in wellness_destinations.values())
    avg_rating = sum(place['rating'] for places in wellness_destinations.values() for place in places) / total_destinations
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{total_destinations}</div>
            <div class="stat-label">총 관광지</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">8</div>
            <div class="stat-label">클러스터 유형</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{avg_rating:.1f}</div>
            <div class="stat-label">평균 평점</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">98%</div>
            <div class="stat-label">추천 정확도</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 8개 클러스터 유형 소개
    st.markdown('<h2 class="section-title">🎭 8가지 여행 성향 유형</h2>', unsafe_allow_html=True)
    
    cluster_info = get_cluster_info()
    cluster_cols = st.columns(2)
    
    for i, (cluster_id, info) in enumerate(cluster_info.items()):
        col_idx = i % 2
        
        with cluster_cols[col_idx]:
            st.markdown(f"""
            <div class="cluster-type-card" style="height: 180px; border-color: {info['color']};">
                <h4 style="color: {info['color']}; margin-bottom: 10px; font-size: 1.1em;">
                    {info['name']}
                </h4>
                <p style="color: #2E7D32; font-size: 0.9em; margin: 0; line-height: 1.4;">
                    {info['description']}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # 카테고리별 분포 차트
    st.markdown('<h2 class="section-title">📈 카테고리별 관광지 분포</h2>', unsafe_allow_html=True)
    
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    categories = list(wellness_destinations.keys())
    counts = [len(places) for places in wellness_destinations.values()]
    
    fig = px.pie(
        values=counts,
        names=categories,
        title="",
        color_discrete_sequence=['#4CAF50', '#66BB6A', '#81C784', '#A5D6A7']
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#2E7D32',
        title_font_size=20,
        font_size=14
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 주요 기능 소개
    st.markdown('<h2 class="section-title">🎯 주요 기능</h2>', unsafe_allow_html=True)
    
    feature_col1, feature_col2, feature_col3 = st.columns(3)
    
    with feature_col1:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 3.5em; margin-bottom: 20px; color: #2E7D32;">📝</div>
            <h3 style="color: #2E7D32; margin-bottom: 15px; font-size: 1.4em;">8문항 성향 진단</h3>
            <p style="color: #2E7D32; font-weight: 600; line-height: 1.6;">
                간단한 8개 질문으로<br>
                정확한 여행 성향을<br>
                클러스터 분석합니다
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_col2:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 3.5em; margin-bottom: 20px; color: #2E7D32;">🤖</div>
            <h3 style="color: #2E7D32; margin-bottom: 15px; font-size: 1.4em;">AI 클러스터 매칭</h3>
            <p style="color: #2E7D32; font-weight: 600; line-height: 1.6;">
                머신러닝 기반<br>
                8개 클러스터 중<br>
                최적 유형을 찾아드립니다
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_col3:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 3.5em; margin-bottom: 20px; color: #2E7D32;">🎯</div>
            <h3 style="color: #2E7D32; margin-bottom: 15px; font-size: 1.4em;">맞춤형 추천</h3>
            <p style="color: #2E7D32; font-weight: 600; line-height: 1.6;">
                개인 성향에 맞는<br>
                한국 관광지를<br>
                정확하게 추천합니다
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # 시작하기 버튼
    st.markdown('<h2 class="section-title">🚀 지금 시작하기</h2>', unsafe_allow_html=True)
    
    start_col1, start_col2, start_col3 = st.columns([1, 2, 1])
    with start_col2:
        if 'survey_completed' not in st.session_state or not st.session_state.survey_completed:
            if st.button("📝 설문조사 시작하기", key="start_survey", type="primary"):
                st.switch_page("pages/01_questionnaire.py")
        else:
            if st.button("📊 내 추천 결과 보기", key="view_results", type="primary"):
                st.switch_page("pages/04_recommendations.py")

# 메인 실행
if __name__ == "__main__":
    home_page()
else:
    home_page()