# pages/05_map_view.py (키 충돌 해결된 버전)

import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.express as px
import pandas as pd
import numpy as np
import time
from utils import (check_access_permissions, determine_cluster, get_cluster_info, 
                  classify_wellness_type)

# 페이지 고유 ID 생성 (세션별 고유 키 보장)
if 'page_instance_id' not in st.session_state:
    st.session_state.page_instance_id = int(time.time() * 1000)

PAGE_ID = st.session_state.page_instance_id

# 로그인 체크
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("app.py")

# 설문 완료 체크
if 'survey_completed' not in st.session_state or not st.session_state.survey_completed:
    st.warning("⚠️ 설문조사를 먼저 완료해주세요.")
    if st.button("📝 설문조사 하러 가기", key=f"survey_btn_{PAGE_ID}"):
        st.switch_page("pages/01_questionnaire.py")
    st.stop()

# 페이지 설정
st.set_page_config(
    page_title="웰니스 투어 지도",
    page_icon="🗺️",
    layout="wide"
)

# 접근 권한 확인
check_access_permissions()

# =============================================================================
# 데이터 정의 (기존과 동일)
# =============================================================================

wellness_destinations = {
    "한류/쇼핑": [
        {
            "name": "명동 쇼핑거리",
            "lat": 37.5636,
            "lon": 126.9826,
            "type": "한류/쇼핑",
            "description": "한류 스타 굿즈와 최신 뷰티 제품을 만날 수 있는 핫플레이스",
            "website": "https://www.visitseoul.net",
            "rating": 4.3,
            "price_range": "10,000-50,000원",
            "distance_from_incheon": 45,
            "travel_time_car": "1시간",
            "travel_time_train": "1시간 10분",
            "travel_cost_car": "15,000원",
            "travel_cost_train": "2,150원",
            "image_url": "🛍️"
        },
        {
            "name": "강남 K-STAR ROAD",
            "lat": 37.5175,
            "lon": 127.0473,
            "type": "한류/쇼핑",
            "description": "K-POP 스타들의 손도장과 포토존이 있는 한류 성지",
            "website": "https://www.gangnam.go.kr",
            "rating": 4.5,
            "price_range": "무료-30,000원",
            "distance_from_incheon": 50,
            "travel_time_car": "1시간 20분",
            "travel_time_train": "1시간 30분",
            "travel_cost_car": "18,000원",
            "travel_cost_train": "2,150원",
            "image_url": "🌟"
        }
    ],
    "전통문화": [
        {
            "name": "경복궁",
            "lat": 37.5796,
            "lon": 126.9770,
            "type": "전통문화",
            "description": "조선왕조의 정궁으로 전통 문화와 역사를 체험할 수 있는 곳",
            "website": "https://www.royalpalace.go.kr",
            "rating": 4.6,
            "price_range": "3,000원",
            "distance_from_incheon": 42,
            "travel_time_car": "1시간",
            "travel_time_train": "1시간 15분",
            "travel_cost_car": "15,000원",
            "travel_cost_train": "2,150원",
            "image_url": "🏛️"
        },
        {
            "name": "인사동 문화거리",
            "lat": 37.5744,
            "lon": 126.9851,
            "type": "전통문화",
            "description": "전통 찻집과 갤러리, 전통 공예품을 만날 수 있는 문화의 거리",
            "website": "https://www.insa-dong.net",
            "rating": 4.4,
            "price_range": "5,000-30,000원",
            "distance_from_incheon": 43,
            "travel_time_car": "1시간",
            "travel_time_train": "1시간 10분",
            "travel_cost_car": "15,000원",
            "travel_cost_train": "2,150원",
            "image_url": "🎨"
        }
    ],
    "자연/힐링": [
        {
            "name": "제주 한라산",
            "lat": 33.3617,
            "lon": 126.5292,
            "type": "자연/힐링",
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
            "name": "남한산성",
            "lat": 37.4741,
            "lon": 127.1838,
            "type": "자연/힐링",
            "description": "유네스코 세계문화유산으로 등재된 산성과 아름다운 자연경관",
            "website": "https://www.gg.go.kr/namhansansung",
            "rating": 4.3,
            "price_range": "무료",
            "distance_from_incheon": 75,
            "travel_time_car": "1시간 30분",
            "travel_time_train": "2시간",
            "travel_cost_car": "25,000원",
            "travel_cost_train": "3,200원",
            "image_url": "🌿"
        }
    ],
    "음식/체험": [
        {
            "name": "광장시장",
            "lat": 37.5700,
            "lon": 126.9996,
            "type": "음식/체험",
            "description": "전통 한식과 길거리 음식을 맛볼 수 있는 대표 전통시장",
            "website": "https://www.kwangjangmarket.co.kr",
            "rating": 4.4,
            "price_range": "3,000-15,000원",
            "distance_from_incheon": 45,
            "travel_time_car": "1시간 10분",
            "travel_time_train": "1시간 20분",
            "travel_cost_car": "18,000원",
            "travel_cost_train": "2,150원",
            "image_url": "🍜"
        },
        {
            "name": "홍대 맛집거리",
            "lat": 37.5563,
            "lon": 126.9244,
            "type": "음식/체험",
            "description": "트렌디한 카페와 레스토랑이 모인 젊은이들의 거리",
            "website": "https://www.visitseoul.net",
            "rating": 4.2,
            "price_range": "8,000-25,000원",
            "distance_from_incheon": 35,
            "travel_time_car": "50분",
            "travel_time_train": "1시간",
            "travel_cost_car": "12,000원",
            "travel_cost_train": "1,950원",
            "image_url": "🍽️"
        }
    ]
}

# =============================================================================
# 추천 알고리즘 (캐시 키 개선)
# =============================================================================

@st.cache_data(show_spinner=False)
def calculate_recommendations_with_cluster(survey_answers, cache_key=None):
    """실제 클러스터 분석 결과 기반 추천 계산 - 개선된 캐시"""
    recommendations = []
    
    # 클러스터 결정
    cluster_result = determine_cluster(survey_answers)
    cluster_id = cluster_result['cluster']
    
    # 실제 클러스터 분석 결과 기반 추천 로직
    cluster_preferences = {
        0: ["한류/쇼핑", "음식/체험"],          # 한류 트렌디형
        1: ["한류/쇼핑", "음식/체험", "전통문화"],  # 종합형 실속파
        2: ["자연/힐링"],                      # 수동형 관광객
        3: ["음식/체험", "한류/쇼핑"],          # 체험중심 실용형
        4: ["전통문화", "한류/쇼핑"],          # 고소득 전통형
        5: ["전통문화"],                      # 행사 관심형
        6: ["자연/힐링", "전통문화"],          # 자연 힐링형
        7: ["자연/힐링"]                      # 소외형 여행객
    }
    
    preferred_categories = cluster_preferences.get(cluster_id, ["음식/체험"])
    
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

# =============================================================================
# 지도 생성 함수 (기존과 동일, 키 수정)
# =============================================================================

def create_enhanced_wellness_map(places_to_show, center_lat=37.5, center_lon=127.0, zoom=7):
    """개선된 인터랙티브 지도 생성"""
    
    # 지도 생성
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles='CartoDB positron',
        attr='CartoDB'
    )
    
    # 인천공항 마커
    incheon_airport = [37.4602, 126.4407]
    folium.Marker(
        incheon_airport,
        popup="✈️ 인천국제공항 (출발지)",
        tooltip="✈️ 인천국제공항",
        icon=folium.Icon(color='red', icon='plane', prefix='fa')
    ).add_to(m)
    
    # 카테고리별 색상 매핑
    color_map = {
        "한류/쇼핑": "#FF6B6B",
        "전통문화": "#4ECDC4",
        "자연/힐링": "#45B7D1",
        "음식/체험": "#FFA726"
    }
    
    # 관광지 마커들 생성
    for i, place in enumerate(places_to_show):
        popup_html = f"""
        <div style="width: 300px;">
            <h4>{place['name']}</h4>
            <p><b>유형:</b> {place['type']}</p>
            <p><b>평점:</b> {place['rating']}/5</p>
            <p><b>거리:</b> {place['distance_from_incheon']}km</p>
            <p><b>가격:</b> {place['price_range']}</p>
            <p>{place['description']}</p>
        </div>
        """
        
        folium.Marker(
            [place['lat'], place['lon']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"#{i+1} {place['name']}",
            icon=folium.Icon(color=color_map.get(place['type'], '#4CAF50'))
        ).add_to(m)
    
    return m

# =============================================================================
# CSS 스타일 (기존과 동일)
# =============================================================================

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] > .main {
        background: linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 50%, #A5D6A7 100%);
        min-height: 100vh;
    }
    
    .main .block-container {
        padding: 2rem 3rem !important;
        max-width: 1400px;
        margin: 0 auto;
    }
    
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
    }
    
    .filter-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 18px;
        padding: 25px 30px;
        margin: 25px 0;
        transition: all 0.3s ease;
    }
    
    .stats-card {
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
    
    .stats-number {
        font-size: 2.8em;
        font-weight: 800;
        color: #2E7D32;
        margin-bottom: 8px;
    }
    
    .stats-label {
        color: #2E7D32;
        font-size: 1.2em;
        font-weight: 600;
    }
    
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
    }
    
    div[data-testid="stButton"] > button {
        background: linear-gradient(45deg, #4CAF50, #66BB6A) !important;
        border: none !important;
        border-radius: 15px !important;
        color: white !important;
        font-weight: 700 !important;
        padding: 12px 25px !important;
        width: 100% !important;
    }
    
    [data-testid="stHeader"] { display: none; }
    [data-testid="stSidebarNav"] { display: none; }
    [data-testid="stSidebar"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }
    footer { display: none; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# 지도 설정 함수 (키 충돌 해결)
# =============================================================================

def render_map_settings():
    """지도 설정 렌더링 - 고유한 키로 중복 오류 해결"""
    
    st.markdown('<h2 class="section-title">🗺️ 지도로 관광지 보기</h2>', unsafe_allow_html=True)
    
    with st.expander("🛠️ 지도 설정", expanded=True):
        settings_col1, settings_col2 = st.columns(2)
        
        with settings_col1:
            st.markdown("#### 📊 표시 옵션")
            
            # 고유한 키 사용
            num_places = st.slider(
                "표시할 추천지 수",
                min_value=1,
                max_value=8,
                value=6,
                key=f"map_places_slider_{PAGE_ID}"  # 페이지별 고유 키
            )
            
            map_center = st.selectbox(
                "지도 중심점",
                ["전체 보기", "인천공항", "서울 중심", "부산 중심", "제주 중심"],
                key=f"map_center_select_{PAGE_ID}"  # 페이지별 고유 키
            )
        
        with settings_col2:
            st.markdown("#### 🎨 카테고리 필터")
            
            show_categories = {}
            for i, category in enumerate(wellness_destinations.keys()):
                show_categories[category] = st.checkbox(
                    category,
                    value=True,
                    key=f"show_category_{i}_{PAGE_ID}"  # 인덱스와 페이지 ID로 고유 키 생성
                )
    
    return num_places, map_center, show_categories

def render_user_cluster_analysis():
    """사용자 클러스터 분석 결과 표시"""
    if 'answers' not in st.session_state or not st.session_state.answers:
        return None
        
    cluster_result = determine_cluster(st.session_state.answers)
    cluster_id = cluster_result['cluster']
    cluster_info = get_cluster_info()
    
    if cluster_id not in cluster_info:
        return None
        
    cluster_data = cluster_info[cluster_id]
    
    st.markdown('<h2 class="section-title">🎭 당신의 여행 성향 분석</h2>', unsafe_allow_html=True)
    
    analysis_col1, analysis_col2 = st.columns([1, 2])
    
    with analysis_col1:
        st.markdown(f"""
        <div class="filter-card" style="border-color: {cluster_data['color']}; text-align: center;">
            <h3 style="color: {cluster_data['color']};">🏆 {cluster_data['name']}</h3>
            <div style="background: linear-gradient(45deg, #4CAF50, #66BB6A); color: white; 
                        padding: 10px 20px; border-radius: 10px; margin: 15px 0;">
                매칭 점수: {cluster_result['score']}/20
            </div>
            <p style="color: #2E7D32; font-weight: 600;">
                신뢰도: {cluster_result['confidence']:.1%}
            </p>
        </div>
        """, unsafe_allow_html=True)

    with analysis_col2:
        st.markdown(f"""
        <div class="filter-card">
            <h4 style="color: #2E7D32;">🎨 지도 범례</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div style="text-align: center; padding: 10px; background: #f8f9fa; border-radius: 10px;">
                    <div style="font-size: 1.5em;">🔴</div>
                    <div style="font-weight: 600; color: #2E7D32;">인천공항</div>
                </div>
                <div style="text-align: center; padding: 10px; background: #f8f9fa; border-radius: 10px;">
                    <div style="font-size: 1.5em;">🔵</div>
                    <div style="font-weight: 600; color: #2E7D32;">한류/쇼핑</div>
                </div>
                <div style="text-align: center; padding: 10px; background: #f8f9fa; border-radius: 10px;">
                    <div style="font-size: 1.5em;">🟢</div>
                    <div style="font-weight: 600; color: #2E7D32;">전통문화</div>
                </div>
                <div style="text-align: center; padding: 10px; background: #f8f9fa; border-radius: 10px;">
                    <div style="font-size: 1.5em;">🟣</div>
                    <div style="font-weight: 600; color: #2E7D32;">자연/힐링</div>
                </div>
            </div>
            <div style="text-align: center; padding: 10px; background: #f8f9fa; border-radius: 10px; margin-top: 15px;">
                <div style="font-size: 1.5em;">🟠</div>
                <div style="font-weight: 600; color: #2E7D32;">음식/체험</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    return cluster_result

# =============================================================================
# 메인 페이지 함수 (키 충돌 해결)
# =============================================================================

def enhanced_map_view_page():
    """개선된 지도 뷰 페이지"""
    
    # 헤더
    st.title('🌿 웰커밍 투어 추천 시스템')
    st.markdown("---")
    
    # 지도 설정 렌더링
    num_places, map_center, show_categories = render_map_settings()
    
    # 사용자 클러스터 분석 표시
    cluster_result = render_user_cluster_analysis()
    
    # 제목
    st.markdown("---")
    st.markdown('<h1 class="page-title">🗺️ 맞춤형 웰니스 여행지 지도</h1>', unsafe_allow_html=True)
    
    # 추천 결과 가져오기 (캐시 키 개선)
    if 'answers' in st.session_state and st.session_state.answers:
        # 답변 해시를 캐시 키로 사용
        cache_key = str(hash(str(sorted(st.session_state.answers.items()))))
        recommended_places = calculate_recommendations_with_cluster(
            st.session_state.answers, 
            cache_key=cache_key
        )
    else:
        st.error("❌ 설문 데이터가 없습니다. 설문을 먼저 완료해주세요.")
        if st.button("📝 설문하러 가기", key=f"survey_redirect_{PAGE_ID}"):
            st.switch_page("pages/01_questionnaire.py")
        return
    
    # 카테고리 필터링
    filtered_places = []
    for place in recommended_places:
        if show_categories.get(place['type'], True):
            filtered_places.append(place)
    
    # 표시할 관광지 수 제한
    places_to_show = filtered_places[:num_places]
    
    if not places_to_show:
        st.warning("⚠️ 표시할 관광지가 없습니다. 카테고리 필터를 확인해주세요.")
        return
    
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
    st.markdown('<h2 class="section-title">🌍 인터랙티브 관광지 지도</h2>', unsafe_allow_html=True)
    
    try:
        wellness_map = create_enhanced_wellness_map(places_to_show, center_lat, center_lon, zoom)
        
        # 지도 표시 (고유한 키 사용)
        map_data = st_folium(
            wellness_map, 
            width=1200, 
            height=600, 
            returned_objects=["last_object_clicked"],
            key=f"wellness_map_{PAGE_ID}"  # 페이지별 고유 키
        )
        
    except Exception as e:
        st.error(f"❌ 지도 로딩 중 오류가 발생했습니다: {str(e)}")
        st.info("💡 페이지를 새로고침하거나 설정을 다시 조정해보세요.")
    
    # 통계 정보 표시
    st.markdown('<h2 class="section-title">📊 추천 관광지 통계</h2>', unsafe_allow_html=True)
    
    if places_to_show:
        avg_distance = np.mean([place['distance_from_incheon'] for place in places_to_show])
        avg_rating = np.mean([place['rating'] for place in places_to_show])
        
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        
        with stat_col1:
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number">{len(places_to_show)}</div>
                <div class="stats-label">표시 관광지</div>
            </div>
            """, unsafe_allow_html=True)
        
        with stat_col2:
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number">{avg_distance:.0f}km</div>
                <div class="stats-label">평균 거리</div>
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
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number">{len(wellness_destinations)}</div>
                <div class="stats-label">총 카테고리</div>
            </div>
            """, unsafe_allow_html=True)
    
    # 액션 버튼
    st.markdown("---")
    st.markdown('<h2 class="section-title">🎯 다음 단계</h2>', unsafe_allow_html=True)
    
    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        if st.button("📝 설문 다시하기", key=f"restart_survey_{PAGE_ID}"):
            # 세션 상태 클리어
            for key in ['survey_completed', 'answers', 'score_breakdown']:
                if key in st.session_state:
                    del st.session_state[key]
            st.switch_page("pages/01_questionnaire.py")
    
    with action_col2:
        if st.button("📊 상세 추천 결과", key=f"view_results_{PAGE_ID}"):
            st.switch_page("pages/04_recommendations.py")
    
    with action_col3:
        if st.button("📈 통계 분석 보기", key=f"view_stats_{PAGE_ID}"):
            st.switch_page("pages/06_statistics.py")

# =============================================================================
# 메인 실행
# =============================================================================

def main():
    """메인 실행 함수"""
    try:
        enhanced_map_view_page()
    except Exception as e:
        st.error("❌ 페이지 로딩 중 오류가 발생했습니다.")
        st.exception(e)
        
        if st.button("🔄 페이지 새로고침", key=f"refresh_{PAGE_ID}"):
            st.rerun()
        
        if st.button("🏠 홈으로 돌아가기", key=f"home_{PAGE_ID}"):
            st.switch_page("pages/03_home.py")

if __name__ == "__main__":
    main()
else:
    main()