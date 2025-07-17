# pages/04_recommendations.py (웰니스 추천 결과 페이지)

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sqlite3
import json
from utils import check_access_permissions, questions

# 로그인 체크
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("app.py")

# 설문 완료 체크
if 'survey_completed' not in st.session_state or not st.session_state.survey_completed:
    st.warning("⚠️ 설문조사를 먼저 완료해주세요.")
    if st.button("📝 설문조사 하러 가기"):
        st.switch_page("pages/01_questionnaire.py")
    st.stop()

# 페이지 설정
st.set_page_config(
    page_title="웰니스 투어 추천 결과",
    page_icon="🎯",
    layout="wide"
)

# 접근 권한 확인 (기본값: 로그인 + 설문 완료 둘 다 확인)
check_access_permissions()

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
            "price_range": "20,000-40,000원",
            "distance_from_incheon": 325,
            "travel_time_car": "3시간 30분",
            "travel_time_train": "2시간 50분",
            "travel_cost_car": "60,000원",
            "travel_cost_train": "45,000원",
            "image_url": "🏖️"
        },
        {
            "name": "충남 아산 온양온천",
            "lat": 36.7894,
            "lon": 127.0042,
            "type": "온천/스파",
            "description": "600년 역사의 전통 온천으로 유명한 천연 온천지",
            "website": "https://www.onyanghotspring.or.kr",
            "rating": 4.2,
            "price_range": "15,000-30,000원",
            "distance_from_incheon": 120,
            "travel_time_car": "1시간 30분",
            "travel_time_train": "1시간 20분",
            "travel_cost_car": "25,000원",
            "travel_cost_train": "18,000원",
            "image_url": "♨️"
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
            "price_range": "무료",
            "distance_from_incheon": 460,
            "travel_time_car": "항공 1시간 + 차량 1시간",
            "travel_time_train": "항공 이용 필수",
            "travel_cost_car": "120,000원 (항공료 포함)",
            "travel_cost_train": "120,000원 (항공료 포함)",
            "image_url": "🏔️"
        },
        {
            "name": "강원 설악산 국립공원",
            "lat": 38.1197,
            "lon": 128.4655,
            "type": "자연치유",
            "description": "아름다운 자연경관과 맑은 공기로 유명한 산악 치유 공간",
            "website": "https://www.knps.or.kr",
            "rating": 4.6,
            "price_range": "3,500원",
            "distance_from_incheon": 200,
            "travel_time_car": "2시간 30분",
            "travel_time_train": "3시간",
            "travel_cost_car": "40,000원",
            "travel_cost_train": "35,000원",
            "image_url": "🏞️"
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
            "price_range": "50,000-100,000원 (템플스테이)",
            "distance_from_incheon": 370,
            "travel_time_car": "4시간",
            "travel_time_train": "3시간 30분",
            "travel_cost_car": "70,000원",
            "travel_cost_train": "50,000원",
            "image_url": "🏛️"
        },
        {
            "name": "전남 순천만 국가정원",
            "lat": 34.8853,
            "lon": 127.5086,
            "type": "요가/명상",
            "description": "자연과 함께하는 힐링 요가 프로그램과 명상 공간",
            "website": "https://www.suncheonbay.go.kr",
            "rating": 4.4,
            "price_range": "8,000원",
            "distance_from_incheon": 350,
            "travel_time_car": "3시간 50분",
            "travel_time_train": "3시간 20분",
            "travel_cost_car": "65,000원",
            "travel_cost_train": "42,000원",
            "image_url": "🌿"
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
            "price_range": "150,000-300,000원",
            "distance_from_incheon": 180,
            "travel_time_car": "2시간 20분",
            "travel_time_train": "1시간 30분 (KTX)",
            "travel_cost_car": "35,000원",
            "travel_cost_train": "28,000원",
            "image_url": "🏔️"
        },
        {
            "name": "경기 용인 에버랜드 스파",
            "lat": 37.2946,
            "lon": 127.2018,
            "type": "웰니스 리조트",
            "description": "테마파크와 연계된 대형 스파 & 웰니스 시설",
            "website": "https://www.everland.com",
            "rating": 4.1,
            "price_range": "30,000-60,000원",
            "distance_from_incheon": 60,
            "travel_time_car": "1시간",
            "travel_time_train": "1시간 30분",
            "travel_cost_car": "15,000원",
            "travel_cost_train": "12,000원",
            "image_url": "🎢"
        }
    ]
}

# 추천 알고리즘
def calculate_recommendations(survey_answers):
    """설문 결과를 바탕으로 추천 관광지 계산"""
    recommendations = []
    
    # answers에서 preferred_activities 추출
    preferred_activities_indices = survey_answers.get("preferred_activities", [])
    
    # 선호 활동에 따른 카테고리 매핑
    activity_to_category = {
        0: "온천/스파",        # 스파/온천 체험
        1: "요가/명상",        # 요가/명상 프로그램
        2: "자연치유",         # 트레킹/하이킹
        3: "웰니스 리조트",    # 건강한 식단 체험
        4: "온천/스파"         # 마사지/아로마테라피
    }
    
    # 선호 카테고리 결정
    preferred_categories = []
    if isinstance(preferred_activities_indices, list):
        for idx in preferred_activities_indices:
            if idx in activity_to_category:
                preferred_categories.append(activity_to_category[idx])
    
    # 기본값 설정
    if not preferred_categories:
        preferred_categories = ["온천/스파"]
    
    # 모든 관광지에 대해 점수 계산
    for category, places in wellness_destinations.items():
        for place in places:
            score = 0
            
            # 카테고리 일치 보너스
            if category in preferred_categories:
                score += 10
            
            # 기본 평점 반영
            score += place["rating"]
            
            # 웰니스 관심도에 따른 추가 점수
            wellness_interest = survey_answers.get("wellness_interest", 2)
            if wellness_interest is not None:
                score += wellness_interest * 0.5
            
            place_with_score = place.copy()
            place_with_score["recommendation_score"] = score
            recommendations.append(place_with_score)
    
    # 점수 순으로 정렬
    recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)
    
    return recommendations[:6]  # 상위 6개 추천

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
    
    /* 추천 카드 스타일 */
    .recommendation-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(25px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 25px;
        padding: 30px;
        margin: 20px 0;
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
    }
    
    .recommendation-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 60px rgba(76, 175, 80, 0.25);
        background: rgba(255, 255, 255, 1);
        border-color: #4CAF50;
    }
    
    .recommendation-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 6px;
        background: linear-gradient(45deg, #4CAF50, #66BB6A);
        border-radius: 25px 25px 0 0;
    }
    
    /* 랭킹 배지 */
    .ranking-badge {
        position: absolute;
        top: -15px;
        right: 25px;
        background: linear-gradient(45deg, #4CAF50, #66BB6A);
        color: white;
        padding: 10px 18px;
        border-radius: 25px;
        font-weight: 800;
        font-size: 16px;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.3);
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    
    /* 제목 스타일 */
    .recommendations-title {
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
    
    /* 설문 요약 카드 */
    .survey-summary {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 18px;
        padding: 25px 30px;
        margin: 25px 0;
        border-left: 6px solid #4CAF50;
    }
    
    /* 점수 표시 */
    .score-display {
        background: linear-gradient(45deg, #4CAF50, #66BB6A);
        color: white;
        padding: 10px 20px;
        border-radius: 30px;
        font-weight: 700;
        display: inline-block;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    
    /* 정보 태그 */
    .info-tag {
        background: rgba(76, 175, 80, 0.15);
        border: 2px solid rgba(76, 175, 80, 0.3);
        border-radius: 12px;
        padding: 8px 15px;
        margin: 5px 3px;
        display: inline-block;
        color: #2E7D32;
        font-size: 0.95em;
        font-weight: 700;
        transition: all 0.3s ease;
    }
    
    .info-tag:hover {
        background: rgba(76, 175, 80, 0.25);
        border-color: #4CAF50;
        transform: translateY(-1px);
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
    
    /* 필터 카드 */
    .filter-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 18px;
        padding: 25px 30px;
        margin: 25px 0;
        transition: all 0.3s ease;
    }
    
    .filter-card:hover {
        border-color: #4CAF50;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.2);
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
    }
    
    div[data-testid="stButton"] > button:hover {
        background: linear-gradient(45deg, #388E3C, #4CAF50) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.4) !important;
    }
    
    /* 차트 스타일 */
    .chart-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 20px;
        padding: 25px;
        margin: 20px 0;
    }
    
    /* 관광지 카드 내용 스타일 */
    .place-name {
        color: #2E7D32;
        font-size: 1.6em;
        font-weight: 800;
        margin-bottom: 15px;
        margin-top: 10px;
    }
    
    .place-description {
        color: #2E7D32;
        margin-bottom: 20px;
        font-weight: 600;
        line-height: 1.6;
    }
    
    .place-details {
        margin: 20px 0;
        color: #2E7D32;
        font-weight: 600;
        line-height: 1.8;
    }
    
    /* 사용자 정보 표시 */
    .user-info {
        color: #2E7D32;
        font-weight: 600;
        line-height: 1.6;
    }
    
    /* 메뉴 제목 */
    .menu-title {
        color: #2E7D32;
        text-align: center;
        margin-bottom: 20px;
        font-weight: 700;
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
        
        .recommendations-title {
            font-size: 2.2em !important;
            padding: 20px 25px !important;
        }
        
        .recommendation-card {
            padding: 20px;
            margin: 15px 0;
        }
        
        .place-name {
            font-size: 1.4em;
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
    st.markdown('<h3 class="menu-title">🧭 빠른 메뉴</h3>', unsafe_allow_html=True)
    
    menu_col1, menu_col2, menu_col3, menu_col4, menu_col5 = st.columns(5)
    
    with menu_col1:
        if st.button("🏠 홈", key="home_btn"):
            st.switch_page("pages/03_home.py")
    
    with menu_col2:
        if st.button("📝 설문조사", key="survey_btn"):
            st.switch_page("pages/01_questionnaire.py")
    
    with menu_col3:
        if st.button("🗺️ 지도 보기", key="map_btn"):
            st.switch_page("pages/05_map_view.py")
    
    with menu_col4:
        if st.button("📈 통계 정보", key="stats_btn"):
            st.switch_page("pages/06_statistics.py")
    
    with menu_col5:
        if st.button("🚪 로그아웃", key="logout_btn"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.switch_page("app.py")

# 메인 추천 결과 페이지
def recommendations_page():
    top_menu()
    
    # 제목
    st.markdown('<h1 class="recommendations-title">🎯 맞춤형 웰니스 여행지 추천</h1>', unsafe_allow_html=True)
    
    # 필터 섹션
    st.markdown('<h2 class="section-title">🎛️ 필터 설정</h2>', unsafe_allow_html=True)
    
    st.markdown('<div class="filter-card">', unsafe_allow_html=True)
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    # 세션 상태 초기화
    if 'category_filter' not in st.session_state:
        st.session_state.category_filter = list(wellness_destinations.keys())
    if 'distance_filter' not in st.session_state:
        st.session_state.distance_filter = 500
    
    with filter_col1:
        # 카테고리 필터
        selected_categories = st.multiselect(
            "카테고리 선택",
            list(wellness_destinations.keys()),
            default=st.session_state.category_filter,
            key="category_filter_new"
        )
        st.session_state.category_filter = selected_categories
    
    with filter_col2:
        # 거리 필터
        distance_max = st.slider(
            "최대 거리 (km)",
            min_value=50,
            max_value=500,
            value=st.session_state.distance_filter,
            step=50,
            key="distance_filter_new"
        )
        st.session_state.distance_filter = distance_max
    
    with filter_col3:
        # 사용자 정보
        st.markdown(f"""
        <div class="user-info">
            <strong>👤 사용자:</strong> {st.session_state.username}<br>
            <strong>📊 필터된 카테고리:</strong> {len(selected_categories)}개<br>
            <strong>📏 최대 거리:</strong> {distance_max}km
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # 설문 결과 요약
    with st.expander("📋 설문 결과 요약", expanded=False):
        st.markdown('<div class="survey-summary">', unsafe_allow_html=True)
        
        # survey_results 대신 answers 사용하고 적절한 형태로 변환
        if 'answers' in st.session_state and st.session_state.answers:
            from utils import questions
            
            for key, answer in st.session_state.answers.items():
                if key in questions:
                    question_title = questions[key]['title']
                    
                    # 다중 선택 문항 처리
                    if key in ["travel_purpose", "preferred_activities"]:
                        if isinstance(answer, list) and answer:
                            selected_options = [questions[key]['options'][i] for i in answer]
                            answer_text = ", ".join(selected_options)
                        else:
                            answer_text = "선택 안함"
                    # 단일 선택 문항 처리
                    else:
                        if answer is not None and answer < len(questions[key]['options']):
                            answer_text = questions[key]['options'][answer]
                        else:
                            answer_text = "답변 없음"
                    
                    st.markdown(f"**{question_title}**: {answer_text}")
        else:
            st.markdown("설문 답변 데이터가 없습니다.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 추천 결과 계산
    recommended_places = calculate_recommendations(st.session_state.answers)
    
    # 필터 적용
    filtered_places = []
    for place in recommended_places:
        # 카테고리 필터
        if place['type'] not in st.session_state.category_filter:
            continue
        
        # 거리 필터
        if place['distance_from_incheon'] > st.session_state.distance_filter:
            continue
        
        filtered_places.append(place)
    
    # 추천 결과 표시
    st.markdown(f'<h2 class="section-title">🏆 추천 관광지 TOP {len(filtered_places)}</h2>', unsafe_allow_html=True)
    
    if len(filtered_places) == 0:
        st.warning("⚠️ 필터 조건에 맞는 관광지가 없습니다. 필터를 조정해주세요.")
        return
    
    # 추천 점수 차트
    st.markdown('<h3 class="section-title">📊 추천 점수 비교</h3>', unsafe_allow_html=True)
    
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    names = [place['name'] for place in filtered_places[:6]]
    scores = [place['recommendation_score'] for place in filtered_places[:6]]
    
    fig = px.bar(
        x=names,
        y=scores,
        title="",
        labels={'x': '관광지', 'y': '추천 점수'},
        color=scores,
        color_continuous_scale=['#A5D6A7', '#4CAF50']
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#2E7D32',
        xaxis_tickangle=-45,
        font_size=12
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 상세 추천 결과
    st.markdown('<h3 class="section-title">🌿 상세 추천 정보</h3>', unsafe_allow_html=True)
    
    for i, place in enumerate(filtered_places):
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown(f"""
            <div style="text-align: center; font-size: 4.5em; margin: 25px 0; filter: drop-shadow(0 4px 8px rgba(76, 175, 80, 0.3));">
                {place['image_url']}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="recommendation-card">
                <div class="ranking-badge">#{i+1}</div>
                <h3 class="place-name">{place['name']}</h3>
                <p class="place-description">{place['description']}</p>
                
                <div class="score-display">추천 점수: {place['recommendation_score']:.1f}/10</div>
                
                <div style="margin: 20px 0;">
                    <span class="info-tag">⭐ {place['rating']}/5</span>
                    <span class="info-tag">💰 {place['price_range']}</span>
                    <span class="info-tag">📍 {place['distance_from_incheon']}km</span>
                    <span class="info-tag">🏷️ {place['type']}</span>
                </div>
                
                <div class="place-details">
                    <strong>🚗 자가용:</strong> {place['travel_time_car']} ({place['travel_cost_car']})<br>
                    <strong>🚊 대중교통:</strong> {place['travel_time_train']} ({place['travel_cost_train']})
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 버튼들
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            with col_btn1:
                st.markdown(f'<a href="{place["website"]}" target="_blank" style="text-decoration: none;"><button style="background: linear-gradient(45deg, #4CAF50, #66BB6A); border: none; border-radius: 12px; color: white; padding: 10px 18px; font-weight: 700; cursor: pointer; transition: all 0.3s ease; text-transform: uppercase;">🌐 공식 사이트</button></a>', unsafe_allow_html=True)
            with col_btn2:
                if st.button(f"🗺️ 지도에서 보기", key=f"map_{i}"):
                    st.session_state.selected_place = place
                    st.switch_page("pages/05_map_view.py")
            with col_btn3:
                if st.button(f"💾 저장", key=f"save_{i}"):
                    st.success(f"✅ {place['name']} 저장됨!")
        
        st.markdown("---")
    
    # 액션 버튼
    st.markdown('<h2 class="section-title">🚀 다음 단계</h2>', unsafe_allow_html=True)
    
    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        if st.button("🗺️ 지도에서 모든 추천지 보기", type="primary"):
            st.session_state.recommended_places = filtered_places
            st.switch_page("pages/05_map_view.py")
    
    with action_col2:
        if st.button("📝 설문 다시하기"):
            st.session_state.survey_completed = False
            st.session_state.survey_results = {}
            st.switch_page("pages/01_questionnaire.py")
    
    with action_col3:
        if st.button("📊 다른 통계 보기"):
            st.switch_page("pages/06_statistics.py")

# 메인 실행
if __name__ == "__main__":
    recommendations_page()
else:
    recommendations_page()