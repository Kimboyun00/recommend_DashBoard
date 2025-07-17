# pages/06_statistics.py (웰니스 통계 페이지)

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from utils import check_access_permissions

# 로그인 체크
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("app.py")

# 페이지 설정
st.set_page_config(
    page_title="웰니스 투어 통계",
    page_icon="📈",
    layout="wide"
)

# 접근 권한 확인 (통계 페이지는 설문 완료 없이도 볼 수 있도록 'home' 타입으로 설정)
check_access_permissions('home')

# 웰니스 관광지 데이터
wellness_destinations = {
    "온천/스파": [
        {
            "name": "부산 해운대 스파랜드",
            "rating": 4.5,
            "price_range": "20,000-40,000원",
            "distance_from_incheon": 325,
            "travel_cost_car": "60,000원",
            "travel_cost_train": "45,000원"
        },
        {
            "name": "충남 아산 온양온천",
            "rating": 4.2,
            "price_range": "15,000-30,000원",
            "distance_from_incheon": 120,
            "travel_cost_car": "25,000원",
            "travel_cost_train": "18,000원"
        }
    ],
    "자연치유": [
        {
            "name": "제주 한라산 국립공원",
            "rating": 4.7,
            "price_range": "무료",
            "distance_from_incheon": 460,
            "travel_cost_car": "120,000원 (항공료 포함)",
            "travel_cost_train": "120,000원 (항공료 포함)"
        },
        {
            "name": "강원 설악산 국립공원",
            "rating": 4.6,
            "price_range": "3,500원",
            "distance_from_incheon": 200,
            "travel_cost_car": "40,000원",
            "travel_cost_train": "35,000원"
        }
    ],
    "요가/명상": [
        {
            "name": "경주 불국사",
            "rating": 4.8,
            "price_range": "50,000-100,000원 (템플스테이)",
            "distance_from_incheon": 370,
            "travel_cost_car": "70,000원",
            "travel_cost_train": "50,000원"
        },
        {
            "name": "전남 순천만 국가정원",
            "rating": 4.4,
            "price_range": "8,000원",
            "distance_from_incheon": 350,
            "travel_cost_car": "65,000원",
            "travel_cost_train": "42,000원"
        }
    ],
    "웰니스 리조트": [
        {
            "name": "강원 평창 알펜시아 리조트",
            "rating": 4.3,
            "price_range": "150,000-300,000원",
            "distance_from_incheon": 180,
            "travel_cost_car": "35,000원",
            "travel_cost_train": "28,000원"
        },
        {
            "name": "경기 용인 에버랜드 스파",
            "rating": 4.1,
            "price_range": "30,000-60,000원",
            "distance_from_incheon": 60,
            "travel_cost_car": "15,000원",
            "travel_cost_train": "12,000원"
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
    
    /* 제목 스타일 */
    .page-title {
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
    
    /* 범례/설정 카드 */
    .legend-card, .setting-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 18px;
        padding: 25px;
        margin: 20px 0;
        transition: all 0.3s ease;
    }
    
    .legend-card:hover, .setting-card:hover {
        border-color: #4CAF50;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.2);
        transform: translateY(-2px);
    }
    
    /* 통계 카드 */
    .stats-card, .metric-card {
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
    
    .stats-card:hover, .metric-card:hover {
        border-color: #4CAF50;
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.25);
        transform: translateY(-3px);
        background: rgba(255, 255, 255, 1);
    }
    
    .stats-number, .metric-number {
        font-size: 2.8em;
        font-weight: 800;
        color: #2E7D32;
        margin-bottom: 8px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    .stats-label, .metric-label {
        color: #2E7D32;
        font-size: 1.2em;
        font-weight: 600;
        letter-spacing: 0.5px;
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
    
    /* 인사이트 카드 */
    .insight-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 15px;
        padding: 20px 25px;
        margin: 15px 0;
        transition: all 0.3s ease;
    }
    
    .insight-card:hover {
        border-color: #4CAF50;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.2);
        transform: translateY(-2px);
    }
    
    .insight-card h4 {
        color: #2E7D32;
        margin-bottom: 10px;
        font-weight: 700;
    }
    
    .insight-card p {
        color: #2E7D32;
        font-weight: 600;
        margin: 0;
    }
    
    /* 버튼 스타일 */
    div[data-testid="stButton"] > button {
        background: linear-gradient(45deg, #4CAF50, #66BB6A) !important;
        border: none !important;
        border-radius: 15px !important;
        color: white !important;
        font-weight: 700 !important;
        padding: 12px 25px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3) !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        width: 100% !important;
    }
    
    div[data-testid="stButton"] > button:hover {
        background: linear-gradient(45deg, #388E3C, #4CAF50) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.4) !important;
    }
    
    /* 메뉴 제목 */
    .menu-title {
        color: #2E7D32;
        text-align: center;
        margin-bottom: 20px;
        font-weight: 700;
        font-size: 1.3em;
    }
    
    /* 사용자 정보 표시 */
    .user-info {
        color: #2E7D32;
        font-weight: 600;
        line-height: 1.6;
    }
    
    /* 상태 메시지 */
    .status-message {
        color: #2E7D32;
        font-size: 1.1em;
        font-weight: 600;
        margin: 20px 0;
        padding: 15px 20px;
        background: rgba(76, 175, 80, 0.1);
        border-radius: 12px;
        border-left: 5px solid #4CAF50;
        box-shadow: 0 3px 12px rgba(76, 175, 80, 0.15);
    }
    
    /* 진행률 컨테이너 */
    .progress-container {
        background: rgba(76, 175, 80, 0.15);
        border-radius: 15px;
        padding: 8px;
        margin: 25px 0;
        box-shadow: inset 0 2px 8px rgba(76, 175, 80, 0.2);
    }
    
    /* 진행률 텍스트 */
    .progress-text {
        text-align: center;
        color: #2E7D32;
        font-weight: 700;
        font-size: 1.1em;
        margin: 12px 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    /* 경고 및 정보 메시지 */
    div[data-testid="stAlert"] {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid #FF8A65 !important;
        border-radius: 12px !important;
        color: #2E7D32 !important;
        font-weight: 600 !important;
    }
    
    /* 성공 메시지 */
    div[data-testid="stAlert"][data-baseweb="notification"] {
        border-color: #4CAF50 !important;
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(129, 199, 132, 0.05)) !important;
    }
    
    /* 데이터프레임 스타일 */
    .dataframe {
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: 12px !important;
        border: 2px solid rgba(76, 175, 80, 0.2) !important;
    }
    
    /* 사이드바 메뉴 */
    .sidebar-menu {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(15px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
    }
    
    /* 관광지 목록 카드 */
    .destination-list-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        transition: all 0.3s ease;
    }
    
    .destination-list-card:hover {
        border-color: #4CAF50;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.2);
        transform: translateY(-2px);
    }
    
    .destination-list-card h4 {
        color: #2E7D32;
        margin: 0;
        font-weight: 700;
    }
    
    .destination-list-card p {
        color: #2E7D32;
        margin: 5px 0;
        font-size: 0.9em;
        font-weight: 600;
    }
    
    /* 통계 페이지 관련 추가 스타일 */
    .statistics-grid {
        display: grid;
        gap: 20px;
        margin: 20px 0;
    }

    .trend-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 18px;
        padding: 25px;
        transition: all 0.3s ease;
    }

    .trend-card:hover {
        border-color: #4CAF50;
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.2);
        transform: translateY(-3px);
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
        
        .page-title {
            font-size: 2.2em !important;
            padding: 20px 25px !important;
        }
        
        .stats-number, .metric-number {
            font-size: 2.4em;
        }
        
        .section-title {
            font-size: 1.6em;
            padding: 12px 20px;
        }
        
        .legend-card, .setting-card, .insight-card {
            padding: 15px 20px;
        }
    }
</style>
""", unsafe_allow_html=True)

# 사이드바 메뉴
def sidebar_menu():
    st.markdown("### 🧭 메뉴")
    
    menu_col1, menu_col2, menu_col3, menu_col4, menu_col5 = st.columns(5)
    
    with menu_col1:
        if st.button("🏠 홈", key="home_btn"):
            st.switch_page("pages/03_home.py")
    
    with menu_col2:
        if st.button("📝 설문조사", key="survey_btn"):
            st.switch_page("pages/01_questionnaire.py")
    
    with menu_col3:
        if st.button("📊 추천 결과", key="results_btn"):
            if 'survey_completed' in st.session_state and st.session_state.survey_completed:
                st.switch_page("pages/04_recommendations.py")
            else:
                st.warning("설문을 먼저 완료해주세요!")
    
    with menu_col4:
        if st.button("🗺️ 지도 보기", key="map_btn"):
            if 'survey_completed' in st.session_state and st.session_state.survey_completed:
                st.switch_page("pages/05_map_view.py")
            else:
                st.warning("설문을 먼저 완료해주세요!")
    
    with menu_col5:
        if st.button("🚪 로그아웃", key="logout_btn"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.switch_page("app.py")
    
    st.markdown("---")
    
    # 통계 설정
    st.markdown("### ⚙️ 통계 설정")
    
    # 분석 기간 (가상)
    analysis_period = st.selectbox(
        "분석 기간",
        ["전체", "최근 1년", "최근 6개월", "최근 3개월"],
        key="analysis_period"
    )
    
    # 비교 기준
    comparison_metric = st.selectbox(
        "비교 기준",
        ["평점", "거리", "비용", "인기도"],
        key="comparison_metric"
    )
    
    # 지역별 분석
    region_analysis = st.checkbox(
        "지역별 분석 포함",
        value=True,
        key="region_analysis"
    )
    
    st.markdown("---")
    st.markdown(f"### 👤 {st.session_state.username}")
    
    return analysis_period, comparison_metric, region_analysis

# 데이터 처리 함수들
def get_all_places_data():
    """모든 관광지 데이터를 하나의 리스트로 반환"""
    all_places = []
    for category, places in wellness_destinations.items():
        for place in places:
            place['type'] = category
            all_places.append(place)
    return all_places

def extract_cost(cost_str):
    """비용 문자열에서 숫자만 추출"""
    cost_str = cost_str.replace(',', '').replace('원', '')
    if '(' in cost_str:
        cost_str = cost_str.split('(')[0]
    if '-' in cost_str:
        # 범위인 경우 평균값 사용
        parts = cost_str.split('-')
        try:
            return (int(parts[0]) + int(parts[1])) / 2
        except:
            return 0
    try:
        return int(cost_str)
    except:
        return 0

def create_category_analysis():
    """카테고리별 분석 데이터 생성"""
    category_stats = {}
    
    for category, places in wellness_destinations.items():
        ratings = [place['rating'] for place in places]
        distances = [place['distance_from_incheon'] for place in places]
        car_costs = [extract_cost(place['travel_cost_car']) for place in places]
        train_costs = [extract_cost(place['travel_cost_train']) for place in places]
        
        category_stats[category] = {
            '관광지 수': len(places),
            '평균 평점': np.mean(ratings),
            '평균 거리(km)': np.mean(distances),
            '평균 자가용 비용(원)': np.mean(car_costs),
            '평균 대중교통 비용(원)': np.mean(train_costs),
            '최고 평점': np.max(ratings),
            '최저 평점': np.min(ratings)
        }
    
    return category_stats

# 메인 통계 페이지
def statistics_page():
    analysis_period, comparison_metric, region_analysis = sidebar_menu()
    
    # 제목
    st.markdown('<h1 class="stats-title">📈 웰니스 투어 통계 분석</h1>', unsafe_allow_html=True)
    
    # 전체 데이터 준비
    all_places = get_all_places_data()
    total_destinations = len(all_places)
    
    # 기본 통계
    avg_rating = np.mean([place['rating'] for place in all_places])
    avg_distance = np.mean([place['distance_from_incheon'] for place in all_places])
    categories_count = len(wellness_destinations)
    
    # 가격 범위 분석
    car_costs = [extract_cost(place['travel_cost_car']) for place in all_places]
    avg_car_cost = np.mean([cost for cost in car_costs if cost > 0])
    
    # 상단 KPI 카드들
    st.markdown('<h2 class="section-title">🎯 핵심 지표</h2>', unsafe_allow_html=True)
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{total_destinations}</div>
            <div class="metric-label">총 관광지</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{avg_rating:.1f}</div>
            <div class="metric-label">평균 평점</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{avg_distance:.0f}km</div>
            <div class="metric-label">평균 거리</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{avg_car_cost:,.0f}원</div>
            <div class="metric-label">평균 교통비</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 카테고리별 분석
    st.markdown('<h2 class="section-title">🏷️ 카테고리별 분석</h2>', unsafe_allow_html=True)
    
    # 카테고리별 관광지 수 파이 차트
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        categories = list(wellness_destinations.keys())
        counts = [len(places) for places in wellness_destinations.values()]
        
        fig_pie = px.pie(
            values=counts,
            names=categories,
            title="카테고리별 관광지 분포",
            color_discrete_sequence=['#4CAF50', '#81C784', '#66BB6A', '#A5D6A7']
        )
        fig_pie.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#2E7D32',
            title_font_size=16
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with chart_col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        # 카테고리별 평균 평점
        category_ratings = {}
        for category, places in wellness_destinations.items():
            category_ratings[category] = np.mean([place['rating'] for place in places])
        
        fig_bar = px.bar(
            x=list(category_ratings.keys()),
            y=list(category_ratings.values()),
            title="카테고리별 평균 평점",
            color=list(category_ratings.values()),
            color_continuous_scale=['#A5D6A7', '#4CAF50']
        )
        fig_bar.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#2E7D32',
            title_font_size=16,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 거리 vs 비용 분석
    st.markdown('<h2 class="section-title">📍 거리 및 비용 분석</h2>', unsafe_allow_html=True)
    
    distance_cost_col1, distance_cost_col2 = st.columns(2)
    
    with distance_cost_col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        # 거리별 분포 히스토그램
        distances = [place['distance_from_incheon'] for place in all_places]
        
        fig_hist = px.histogram(
            x=distances,
            nbins=6,
            title="인천공항으로부터 거리 분포",
            labels={'x': '거리 (km)', 'y': '관광지 수'},
            color_discrete_sequence=['#4CAF50']
        )
        fig_hist.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#2E7D32',
            title_font_size=16
        )
        st.plotly_chart(fig_hist, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with distance_cost_col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        # 거리 vs 자가용 비용 산점도
        distances = [place['distance_from_incheon'] for place in all_places]
        car_costs = [extract_cost(place['travel_cost_car']) for place in all_places]
        names = [place['name'] for place in all_places]
        categories = [place['type'] for place in all_places]
        
        fig_scatter = px.scatter(
            x=distances,
            y=car_costs,
            hover_name=names,
            color=categories,
            title="거리 vs 자가용 비용",
            labels={'x': '거리 (km)', 'y': '비용 (원)'},
            color_discrete_sequence=['#4CAF50', '#81C784', '#66BB6A', '#A5D6A7']
        )
        fig_scatter.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#2E7D32',
            title_font_size=16
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 교통수단별 비용 비교
    st.markdown('<h2 class="section-title">🚗 교통수단별 비교</h2>', unsafe_allow_html=True)
    
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    transport_data = []
    for place in all_places:
        car_cost = extract_cost(place['travel_cost_car'])
        train_cost = extract_cost(place['travel_cost_train'])
        
        if car_cost > 0 and train_cost > 0:  # 유효한 데이터만
            transport_data.append({
                '관광지': place['name'],
                '자가용': car_cost,
                '대중교통': train_cost,
                '카테고리': place['type']
            })
    
    if transport_data:
        transport_df = pd.DataFrame(transport_data)
        
        fig_transport = px.bar(
            transport_df,
            x='관광지',
            y=['자가용', '대중교통'],
            title="교통수단별 비용 비교",
            labels={'value': '비용 (원)', 'variable': '교통수단'},
            color_discrete_sequence=['#4CAF50', '#81C784']
        )
        fig_transport.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#2E7D32',
            title_font_size=16,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_transport, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 상세 통계 테이블
    st.markdown('<h2 class="section-title">📊 상세 통계표</h2>', unsafe_allow_html=True)
    
    category_stats = create_category_analysis()
    stats_df = pd.DataFrame(category_stats).T
    
    # 숫자 형식 정리
    stats_df = stats_df.round(1)
    
    st.dataframe(stats_df, use_container_width=True)
    
    # 평점 분포 박스플롯
    st.markdown('<h2 class="section-title">⭐ 평점 분포 분석</h2>', unsafe_allow_html=True)
    
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    rating_data = []
    for category, places in wellness_destinations.items():
        for place in places:
            rating_data.append({
                'category': category,
                'rating': place['rating'],
                'name': place['name']
            })
    
    rating_df = pd.DataFrame(rating_data)
    
    fig_box = px.box(
        rating_df,
        x='category',
        y='rating',
        title="카테고리별 평점 분포",
        labels={'category': '카테고리', 'rating': '평점'},
        color='category',
        color_discrete_sequence=['#4CAF50', '#81C784', '#66BB6A', '#A5D6A7']
    )
    fig_box.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#2E7D32',
        title_font_size=16,
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig_box, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 추가 인사이트
    st.markdown('<h2 class="section-title">💡 주요 인사이트</h2>', unsafe_allow_html=True)
    
    insight_col1, insight_col2 = st.columns(2)
    
    with insight_col1:
        # 최고 평점 관광지
        best_rated = max(all_places, key=lambda x: x['rating'])
        st.markdown(f"""
        <div class="insight-card">
            <h4 style="color: #2E7D32; margin-bottom: 10px;">🏆 최고 평점 관광지</h4>
            <p style="color: #2E7D32; font-weight: 600; margin: 0;">
                {best_rated['name']} ({best_rated['rating']}/5)
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 가장 가까운 관광지
        closest = min(all_places, key=lambda x: x['distance_from_incheon'])
        st.markdown(f"""
        <div class="insight-card">
            <h4 style="color: #2E7D32; margin-bottom: 10px;">📍 가장 가까운 관광지</h4>
            <p style="color: #2E7D32; font-weight: 600; margin: 0;">
                {closest['name']} ({closest['distance_from_incheon']}km)
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with insight_col2:
        # 가장 경제적인 관광지
        cheapest_costs = [(place, extract_cost(place['travel_cost_car'])) for place in all_places]
        cheapest = min([x for x in cheapest_costs if x[1] > 0], key=lambda x: x[1])
        st.markdown(f"""
        <div class="insight-card">
            <h4 style="color: #2E7D32; margin-bottom: 10px;">💰 가장 경제적인 관광지</h4>
            <p style="color: #2E7D32; font-weight: 600; margin: 0;">
                {cheapest[0]['name']} ({cheapest[1]:,.0f}원)
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 평균 이상 평점 비율
        above_avg_count = len([p for p in all_places if p['rating'] > avg_rating])
        above_avg_ratio = (above_avg_count / total_destinations) * 100
        st.markdown(f"""
        <div class="insight-card">
            <h4 style="color: #2E7D32; margin-bottom: 10px;">⭐ 평균 이상 평점 비율</h4>
            <p style="color: #2E7D32; font-weight: 600; margin: 0;">
                {above_avg_ratio:.1f}% ({above_avg_count}/{total_destinations})
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # 사용자 맞춤 분석 (설문 완료 시)
    if 'survey_completed' in st.session_state and st.session_state.survey_completed:
        st.markdown('<h2 class="section-title">👤 나의 선호도 분석</h2>', unsafe_allow_html=True)
        
        user_prefs = st.session_state.survey_results
        
        pref_col1, pref_col2, pref_col3 = st.columns(3)
        
        with pref_col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">⭐</div>
                <div class="metric-label">웰니스 관심도<br>높음</div>
            </div>
            """, unsafe_allow_html=True)
        
        with pref_col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">🌿</div>
                <div class="metric-label">자연 친화적<br>성향</div>
            </div>
            """, unsafe_allow_html=True)
        
        with pref_col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">💚</div>
                <div class="metric-label">힐링 추구<br>여행객</div>
            </div>
            """, unsafe_allow_html=True)

# 메인 실행
if __name__ == "__main__":
    statistics_page()
else:
    statistics_page()