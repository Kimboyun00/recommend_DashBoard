# pages/05_map_view.py (웰니스 지도 보기 페이지)

import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.express as px
import pandas as pd
from utils import (check_access_permissions, determine_cluster, get_cluster_info, 
                  classify_wellness_type)

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
    page_title="웰니스 투어 지도",
    page_icon="🗺️",
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

# 클러스터 기반 추천 알고리즘
def calculate_recommendations_with_cluster(survey_answers):
    """클러스터 기반 추천 계산"""
    recommendations = []
    
    # 클러스터 결정
    cluster_result = determine_cluster(survey_answers)
    cluster_id = cluster_result['cluster']
    
    # 클러스터별 추천 로직
    cluster_preferences = {
        0: ["온천/스파", "자연치유"],  # 안전추구 모험가형
        1: ["온천/스파", "웰니스 리조트"],  # 안전우선 편의형  
        2: ["요가/명상", "자연치유"],  # 문화체험 힐링형
        3: ["웰니스 리조트", "온천/스파"],  # 쇼핑마니아 사교형
        4: ["웰니스 리조트", "자연치유"],  # 프리미엄 모험형
        5: ["요가/명상", "자연치유"],  # 탐험형 문화애호가
        6: ["요가/명상", "온천/스파"],  # 문화미식 여성형
        7: ["자연치유", "요가/명상", "온천/스파"]  # 종합체험 활동형
    }
    
    preferred_categories = cluster_preferences.get(cluster_id, ["온천/스파"])
    
    # 모든 관광지에 대해 점수 계산
    for category, places in wellness_destinations.items():
        for place in places:
            score = 0
            
            # 클러스터 선호 카테고리 보너스
            if category in preferred_categories:
                bonus_index = preferred_categories.index(category)
                score += (10 - bonus_index * 2)
            
            # 기본 평점 반영
            score += place["rating"] * 2
            
            # 클러스터 점수 반영
            score += cluster_result['score'] * 0.1
            
            place_with_score = place.copy()
            place_with_score["recommendation_score"] = score
            place_with_score["cluster_id"] = cluster_id
            recommendations.append(place_with_score)
    
    # 점수 순으로 정렬
    recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)
    
    return recommendations

# 지도 생성 함수
def create_wellness_map(places_to_show, center_lat=36.5, center_lon=127.8, zoom=7):
    """웰니스 관광지를 표시하는 인터랙티브 지도 생성"""
    
    # 지도 생성
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles='OpenStreetMap'
    )
    
    # 인천공항 마커 (출발지)
    incheon_airport = [37.4602, 126.4407]
    folium.Marker(
        incheon_airport,
        popup=folium.Popup("""
        <div style="width: 200px;">
            <h4>✈️ 인천국제공항</h4>
            <p><strong>출발지</strong></p>
            <p>모든 여행의 시작점</p>
        </div>
        """, max_width=200),
        tooltip="인천국제공항 (출발지)",
        icon=folium.Icon(color='red', icon='plane', prefix='fa')
    ).add_to(m)
    
    # 웰니스 관광지 마커들
    color_map = {
        "온천/스파": "blue",
        "자연치유": "green", 
        "요가/명상": "purple",
        "웰니스 리조트": "orange"
    }
    
    icon_map = {
        "온천/스파": "tint",
        "자연치유": "tree",
        "요가/명상": "heart",
        "웰니스 리조트": "home"
    }
    
    for i, place in enumerate(places_to_show):
        # 추천 순위에 따른 마커 크기
        if i < 2:
            tooltip_prefix = "🥇"
        elif i < 4:
            tooltip_prefix = "🥈"
        else:
            tooltip_prefix = "🥉"
        
        popup_html = f"""
        <div style="width: 350px; font-family: Arial, sans-serif;">
            <div style="text-align: center; padding: 10px; background: linear-gradient(45deg, #4CAF50, #81C784); color: white; border-radius: 10px 10px 0 0; margin: -10px -10px 10px -10px;">
                <h3 style="margin: 0; font-size: 18px;">{place['image_url']} {place['name']}</h3>
                <div style="font-size: 14px; margin-top: 5px;">#{i+1} 추천 관광지</div>
            </div>
            
            <div style="padding: 0 5px;">
                <p><strong>🏷️ 유형:</strong> {place['type']}</p>
                <p><strong>📍 설명:</strong> {place['description']}</p>
                <p><strong>⭐ 평점:</strong> {place['rating']}/5.0</p>
                <p><strong>💰 가격:</strong> {place['price_range']}</p>
                <p><strong>📏 거리:</strong> {place['distance_from_incheon']}km (인천공항 기준)</p>
                
                <div style="background: #f8f9fa; padding: 10px; border-radius: 8px; margin: 10px 0;">
                    <div style="margin-bottom: 8px;"><strong>🚗 자가용:</strong></div>
                    <div style="margin-left: 15px; font-size: 13px;">
                        ⏰ {place['travel_time_car']}<br>
                        💵 {place['travel_cost_car']}
                    </div>
                    
                    <div style="margin: 8px 0 8px 0;"><strong>🚊 대중교통:</strong></div>
                    <div style="margin-left: 15px; font-size: 13px;">
                        ⏰ {place['travel_time_train']}<br>
                        💵 {place['travel_cost_train']}
                    </div>
                </div>
                
                {'<div style="text-align: center; margin: 10px 0;"><div style="background: linear-gradient(45deg, #4CAF50, #81C784); color: white; padding: 8px 15px; border-radius: 20px; display: inline-block; font-weight: bold;">추천점수: ' + str(place.get('recommendation_score', 0))[:4] + '/20</div></div>' if 'recommendation_score' in place else ''}
                
                <div style="text-align: center; margin-top: 15px;">
                    <a href="{place['website']}" target="_blank" style="background: linear-gradient(45deg, #4CAF50, #81C784); color: white; padding: 8px 20px; text-decoration: none; border-radius: 15px; font-weight: bold;">🌐 공식 사이트 방문</a>
                </div>
            </div>
        </div>
        """
        
        # 경로선 그리기 (인천공항에서 관광지까지)
        folium.PolyLine(
            locations=[incheon_airport, [place['lat'], place['lon']]],
            color=color_map.get(place['type'], 'gray'),
            weight=3,
            opacity=0.6,
            dash_array='5, 10'
        ).add_to(m)
        
        folium.Marker(
            [place['lat'], place['lon']],
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=f"{tooltip_prefix} {place['name']} (추천순위: {i+1}위)",
            icon=folium.Icon(
                color=color_map.get(place['type'], 'gray'),
                icon=icon_map.get(place['type'], 'info-sign'),
                prefix='fa'
            )
        ).add_to(m)
    
    return m

# 웰니스 테마 CSS (동일한 스타일 유지)
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
        
        .legend-card, .setting-card {
            padding: 15px 20px;
        }
    }
</style>
""", unsafe_allow_html=True)

# 사이드바 메뉴
def sidebar_menu():

    # 제목
    st.title('🌿 웰커밍 투어추천 시스템')
    st.markdown("---")

    # 메인 제목
    st.markdown('<h2 class="section-title">🗺️ 지도로 관광지 보기</h2>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 지도 설정
    st.markdown("### 🗺️ 지도 설정")
    
    # 표시할 관광지 수
    num_places = st.slider(
        "표시할 추천지 수",
        min_value=1,
        max_value=8,
        value=6,
        key="num_places_slider"
    )
    
    # 지도 중심점 설정
    map_center = st.selectbox(
        "지도 중심점",
        ["전체 보기", "인천공항", "서울 중심", "부산 중심", "제주 중심"],
        key="map_center_select"
    )
    
    # 카테고리 표시 설정
    st.markdown("### 🎨 카테고리 표시")
    show_categories = {}
    for category in wellness_destinations.keys():
        show_categories[category] = st.checkbox(
            category,
            value=True,
            key=f"show_{category}"
        )
    
    st.markdown("---")
    
    # 클러스터 분석 결과 표시
    if 'answers' in st.session_state and st.session_state.answers:
        cluster_result = determine_cluster(st.session_state.answers)
        cluster_id = cluster_result['cluster']
        cluster_info = get_cluster_info()
        
        if cluster_id in cluster_info:
            cluster_data = cluster_info[cluster_id]
            wellness_type, wellness_color = classify_wellness_type(cluster_result['score'], cluster_id)
            
            st.markdown('<h2 class="section-title">🎭 당신의 여행 성향</h2>', unsafe_allow_html=True)
            
            analysis_col1, analysis_col2 = st.columns([1, 2])
            
            with analysis_col1:
                st.markdown(f"""
                <div class="cluster-result-card" style="border-color: {cluster_data['color']};">
                    <h3 style="color: {cluster_data['color']}; margin-bottom: 15px;">
                        🏆 {cluster_data['name']}
                    </h3>
                    <div class="score-display">
                        매칭 점수: {cluster_result['score']}/20
                    </div>
                    <p style="color: #2E7D32; font-weight: 600; margin-top: 15px; font-size: 0.9em;">
                        신뢰도: {cluster_result['confidence']:.1%}
                    </p>
                </div>
                """, unsafe_allow_html=True)

            with analysis_col2:
                # 범례
                st.markdown("### 🎨 지도 범례")
                
                legend_data = [
                    ("🔴", "인천공항 (출발지)"),
                    ("🔵", "온천/스파"),
                    ("🟢", "자연치유"),
                    ("🟣", "요가/명상"),
                    ("🟠", "웰니스 리조트")
                ]
                
                for color, label in legend_data:
                    st.markdown(f"{color} {label}")
    
    return num_places, map_center, show_categories

# 메인 지도 페이지
def map_view_page():
    num_places, map_center, show_categories = sidebar_menu()
    
    # 제목
    st.markdown('<h1 class="page-title">🗺️ 맞춤형 여행지 지도</h1>', unsafe_allow_html=True)
    
    # 추천 결과 가져오기 (클러스터 기반)
    if 'recommended_places' not in st.session_state:
        if 'answers' in st.session_state and st.session_state.answers:
            st.session_state.recommended_places = calculate_recommendations_with_cluster(st.session_state.answers)
        else:
            st.error("설문 데이터가 없습니다.")
            return
    
    recommended_places = st.session_state.recommended_places
    
    # 필터링 (카테고리별)
    filtered_places = []
    for place in recommended_places:
        if show_categories.get(place['type'], True):
            filtered_places.append(place)
    
    # 표시할 관광지 수 제한
    places_to_show = filtered_places[:num_places]
    
    if not places_to_show:
        st.warning("⚠️ 표시할 관광지가 없습니다. 카테고리를 선택해주세요.")
        return
    
    # 클러스터 분석 결과 요약 표시
    if 'answers' in st.session_state and st.session_state.answers:
        cluster_result = determine_cluster(st.session_state.answers)
        cluster_info = get_cluster_info()
        
        if cluster_result['cluster'] in cluster_info:
            cluster_data = cluster_info[cluster_result['cluster']]
            
            st.markdown('<h3 class="section-title">🎯 개인 맞춤 분석 결과</h3>', unsafe_allow_html=True)
            
            summary_col1, summary_col2, summary_col3 = st.columns(3)
            
            with summary_col1:
                st.markdown(f"""
                <div class="stats-card" style="border-color: {cluster_data['color']};">
                    <div class="stats-number" style="color: {cluster_data['color']};">🎭</div>
                    <div class="stats-label">{cluster_data['name']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with summary_col2:
                st.markdown(f"""
                <div class="stats-card">
                    <div class="stats-number">{cluster_result['score']}</div>
                    <div class="stats-label">클러스터 점수</div>
                </div>
                """, unsafe_allow_html=True)
            
            with summary_col3:
                confidence_pct = int(cluster_result['confidence'] * 100)
                st.markdown(f"""
                <div class="stats-card">
                    <div class="stats-number">{confidence_pct}%</div>
                    <div class="stats-label">매칭 신뢰도</div>
                </div>
                """, unsafe_allow_html=True)
    
    # 지도 중심점 설정
    center_coords = {
        "전체 보기": (36.5, 127.8, 7),
        "인천공항": (37.4602, 126.4407, 9),
        "서울 중심": (37.5665, 126.9780, 10),
        "부산 중심": (35.1796, 129.0756, 11),
        "제주 중심": (33.4996, 126.5312, 11)
    }
    
    center_lat, center_lon, zoom = center_coords[map_center]
    
    # 지도 생성 및 표시
    st.markdown('<h3 class="section-title">🌍 추천 관광지 위치</h3>', unsafe_allow_html=True)
    
    wellness_map = create_wellness_map(places_to_show, center_lat, center_lon, zoom)
    
    # 지도 표시
    map_data = st_folium(wellness_map, width=1200, height=600, returned_objects=["last_object_clicked"])
    
    # 클릭된 마커 정보 표시
    if map_data['last_object_clicked']:
        clicked_data = map_data['last_object_clicked']
        if clicked_data and 'lat' in clicked_data and 'lng' in clicked_data:
            # 클릭된 위치와 가장 가까운 관광지 찾기
            clicked_lat, clicked_lng = clicked_data['lat'], clicked_data['lng']
            min_distance = float('inf')
            selected_place = None
            
            for place in places_to_show:
                distance = ((place['lat'] - clicked_lat) ** 2 + (place['lon'] - clicked_lng) ** 2) ** 0.5
                if distance < min_distance:
                    min_distance = distance
                    selected_place = place
            
            if selected_place and min_distance < 0.1:  # 충분히 가까운 경우
                st.markdown(f'<h3 class="section-title">📍 선택된 관광지: {selected_place["name"]}</h3>', unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown(f"""
                    <div class="stats-card">
                        <div style="font-size: 3em; margin-bottom: 10px;">{selected_place['image_url']}</div>
                        <div class="stats-number">{selected_place['rating']}</div>
                        <div class="stats-label">평점</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    **🏷️ 유형**: {selected_place['type']}  
                    **📍 설명**: {selected_place['description']}  
                    **💰 가격**: {selected_place['price_range']}  
                    **📏 거리**: {selected_place['distance_from_incheon']}km  
                    **🚗 자가용**: {selected_place['travel_time_car']} ({selected_place['travel_cost_car']})  
                    **🚊 대중교통**: {selected_place['travel_time_train']} ({selected_place['travel_cost_train']})
                    """)
                    
                    if 'recommendation_score' in selected_place:
                        st.markdown(f"**🎯 추천 점수**: {selected_place['recommendation_score']:.1f}/20")
                    
                    st.markdown(f"🌐 [공식 웹사이트 방문]({selected_place['website']})")
    
    # 추천 관광지 목록
    st.markdown('<h3 class="section-title">📋 추천 관광지 목록</h3>', unsafe_allow_html=True)
    
    # 간단한 카드 형태로 표시
    cols = st.columns(2)
    for i, place in enumerate(places_to_show):
        col_idx = i % 2
        
        with cols[col_idx]:
            rank_emoji = "🥇" if i < 2 else "🥈" if i < 4 else "🥉"
            
            st.markdown(f"""
            <div class="legend-card">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <span style="font-size: 2em; margin-right: 15px;">{place['image_url']}</span>
                    <div>
                        <h4 style="color: #2E7D32; margin: 0;">{rank_emoji} {place['name']}</h4>
                        <p style="color: #2E7D32; margin: 5px 0; font-size: 0.9em; font-weight: 600;">{place['type']}</p>
                    </div>
                </div>
                <div style="color: #2E7D32; font-size: 0.85em; font-weight: 600;">
                    ⭐ {place['rating']}/5 | 💰 {place['price_range']} | 📍 {place['distance_from_incheon']}km
                    {f' | 🎯 {place["recommendation_score"]:.1f}점' if 'recommendation_score' in place else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # 여행 통계
    st.markdown('<h3 class="section-title">📊 여행 통계</h3>', unsafe_allow_html=True)
    
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
    # 평균 거리
    avg_distance = sum(place['distance_from_incheon'] for place in places_to_show) / len(places_to_show)
    
    # 평균 자가용 비용 (숫자만 추출)
    car_costs = []
    for place in places_to_show:
        cost_str = place['travel_cost_car'].replace(',', '').replace('원', '')
        # 괄호 안의 내용 제거 (항공료 포함 등)
        if '(' in cost_str:
            cost_str = cost_str.split('(')[0]
        try:
            car_costs.append(int(cost_str))
        except:
            car_costs.append(0)
    
    avg_car_cost = sum(car_costs) / len(car_costs) if car_costs else 0
    
    # 평균 평점
    avg_rating = sum(place['rating'] for place in places_to_show) / len(places_to_show)
    
    # 평균 추천 점수
    avg_rec_score = 0
    if places_to_show and 'recommendation_score' in places_to_show[0]:
        avg_rec_score = sum(place['recommendation_score'] for place in places_to_show) / len(places_to_show)
    
    with stat_col1:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{avg_distance:.0f}km</div>
            <div class="stats-label">평균 거리</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_col2:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{avg_car_cost:,.0f}원</div>
            <div class="stats-label">평균 자가용 비용</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_col3:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{avg_rating:.1f}</div>
            <div class="stats-label">평균 평점</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_col4:
        if avg_rec_score > 0:
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number">{avg_rec_score:.1f}</div>
                <div class="stats-label">평균 추천 점수</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number">{len(places_to_show)}</div>
                <div class="stats-label">추천 관광지</div>
            </div>
            """, unsafe_allow_html=True)

# 메인 실행
if __name__ == "__main__":
    map_view_page()
else:
    map_view_page()