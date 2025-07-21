# pages/05_map_view.py (웰니스 지도 보기 페이지 - 개선된 버전)

import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.express as px
import pandas as pd
import numpy as np
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

# 접근 권한 확인
check_access_permissions()

# =============================================================================
# 데이터 정의
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
# 추천 알고리즘
# =============================================================================

@st.cache_data
def calculate_recommendations_with_cluster(survey_answers):
    """실제 클러스터 분석 결과 기반 추천 계산 - 캐시 적용으로 성능 최적화"""
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
# 지도 생성 함수
# =============================================================================

def create_enhanced_wellness_map(places_to_show, center_lat=37.5, center_lon=127.0, zoom=7):
    """개선된 인터랙티브 지도 생성"""
    
    # 지도 생성 - 더 나은 타일 사용
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles='CartoDB positron',  # 더 깔끔한 타일
        attr='CartoDB'
    )
    
    # 추가 타일 레이어 옵션
    folium.TileLayer(
        'CartoDB dark_matter',
        attr='CartoDB',
        name='Dark Mode'
    ).add_to(m)
    
    folium.TileLayer(
        'OpenStreetMap',
        attr='OpenStreetMap',
        name='Street View'
    ).add_to(m)
    
    # 인천공항 마커 (출발지) - 개선된 스타일
    incheon_airport = [37.4602, 126.4407]
    folium.Marker(
        incheon_airport,
        popup=folium.Popup("""
        <div style="width: 250px; font-family: 'Inter', sans-serif;">
            <div style="background: linear-gradient(135deg, #4CAF50, #81C784); color: white; padding: 15px; margin: -10px -10px 15px -10px; border-radius: 12px 12px 0 0; text-align: center;">
                <h3 style="margin: 0; font-size: 18px;">✈️ 인천국제공항</h3>
                <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;">여행의 시작점</p>
            </div>
            <div style="padding: 5px;">
                <p style="margin: 0; font-weight: 600; color: #2E7D32;">🌏 모든 한국 여행의 게이트웨이</p>
                <p style="margin: 5px 0 0 0; font-size: 13px; color: #666;">이곳에서 당신의 웰니스 여행이 시작됩니다</p>
            </div>
        </div>
        """, max_width=250),
        tooltip="✈️ 인천국제공항 (출발지)",
        icon=folium.Icon(
            color='red', 
            icon='plane', 
            prefix='fa',
            icon_size=(20, 20)
        )
    ).add_to(m)
    
    # 카테고리별 색상 및 아이콘 매핑 개선
    color_map = {
        "한류/쇼핑": "#FF6B6B",     # 더 생생한 빨강
        "전통문화": "#4ECDC4",      # 청록색
        "자연/힐링": "#45B7D1",     # 하늘색
        "음식/체험": "#FFA726"      # 주황색
    }
    
    icon_map = {
        "한류/쇼핑": "shopping-bag",
        "전통문화": "landmark",
        "자연/힐링": "tree",
        "음식/체험": "utensils"
    }
    
    # 관광지 마커들 생성
    for i, place in enumerate(places_to_show):
        # 순위 배지
        if i == 0:
            rank_badge = "🥇 1위"
            rank_color = "#FFD700"
        elif i == 1:
            rank_badge = "🥈 2위"
            rank_color = "#C0C0C0"
        elif i == 2:
            rank_badge = "🥉 3위"
            rank_color = "#CD7F32"
        else:
            rank_badge = f"#{i+1}"
            rank_color = "#4CAF50"
        
        # 향상된 팝업 HTML
        popup_html = f"""
        <div style="width: 380px; font-family: 'Inter', sans-serif; font-size: 14px;">
            <div style="background: linear-gradient(135deg, {color_map.get(place['type'], '#4CAF50')}, #81C784); color: white; padding: 20px; margin: -10px -10px 20px -10px; border-radius: 15px 15px 0 0; text-align: center; position: relative;">
                <div style="position: absolute; top: 10px; right: 15px; background: {rank_color}; color: white; padding: 5px 10px; border-radius: 20px; font-size: 12px; font-weight: bold;">
                    {rank_badge}
                </div>
                <div style="font-size: 2.5em; margin-bottom: 10px;">{place['image_url']}</div>
                <h3 style="margin: 0; font-size: 20px; font-weight: 700;">{place['name']}</h3>
                <p style="margin: 8px 0 0 0; font-size: 14px; opacity: 0.9;">{place['type']} 추천 관광지</p>
            </div>
            
            <div style="padding: 0 10px 10px 10px;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
                    <div style="text-align: center; background: #f8f9fa; padding: 10px; border-radius: 8px;">
                        <div style="font-size: 1.5em; color: {color_map.get(place['type'], '#4CAF50')};">⭐</div>
                        <div style="font-weight: 700; color: #2E7D32;">{place['rating']}/5.0</div>
                        <div style="font-size: 12px; color: #666;">평점</div>
                    </div>
                    <div style="text-align: center; background: #f8f9fa; padding: 10px; border-radius: 8px;">
                        <div style="font-size: 1.5em; color: {color_map.get(place['type'], '#4CAF50')};">📏</div>
                        <div style="font-weight: 700; color: #2E7D32;">{place['distance_from_incheon']}km</div>
                        <div style="font-size: 12px; color: #666;">거리</div>
                    </div>
                </div>
                
                <div style="margin-bottom: 15px;">
                    <p style="margin: 0 0 10px 0; font-weight: 600; color: #2E7D32;">📍 설명</p>
                    <p style="margin: 0; font-size: 13px; line-height: 1.4; color: #555;">{place['description']}</p>
                </div>
                
                <div style="margin-bottom: 15px;">
                    <p style="margin: 0 0 8px 0; font-weight: 600; color: #2E7D32;">💰 예상 비용</p>
                    <p style="margin: 0; font-size: 13px; color: #555;">{place['price_range']}</p>
                </div>
                
                <div style="background: #f0f8f0; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                    <p style="margin: 0 0 10px 0; font-weight: 600; color: #2E7D32;">🚗 교통 정보</p>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 12px;">
                        <div>
                            <strong>자가용:</strong><br>
                            ⏰ {place['travel_time_car']}<br>
                            💵 {place['travel_cost_car']}
                        </div>
                        <div>
                            <strong>대중교통:</strong><br>
                            ⏰ {place['travel_time_train']}<br>
                            💵 {place['travel_cost_train']}
                        </div>
                    </div>
                </div>
                
                {'<div style="text-align: center; margin-bottom: 15px;"><div style="background: linear-gradient(45deg, #4CAF50, #81C784); color: white; padding: 10px 20px; border-radius: 25px; display: inline-block; font-weight: bold;">🎯 추천점수: ' + str(place.get('recommendation_score', 0))[:5] + '/20</div></div>' if 'recommendation_score' in place else ''}
                
                <div style="text-align: center;">
                    <a href="{place['website']}" target="_blank" style="background: linear-gradient(45deg, #4CAF50, #81C784); color: white; padding: 12px 25px; text-decoration: none; border-radius: 25px; font-weight: bold; display: inline-block; transition: transform 0.2s;">
                        🌐 공식 사이트 방문
                    </a>
                </div>
            </div>
        </div>
        """
        
        # 경로선 그리기 (개선된 스타일)
        folium.PolyLine(
            locations=[incheon_airport, [place['lat'], place['lon']]],
            color=color_map.get(place['type'], '#4CAF50'),
            weight=4,
            opacity=0.7,
            dash_array='8, 12',
            popup=f"📍 {place['name']}까지의 경로"
        ).add_to(m)
        
        # 마커 생성
        folium.Marker(
            [place['lat'], place['lon']],
            popup=folium.Popup(popup_html, max_width=380),
            tooltip=f"{rank_badge} {place['name']} ({place['type']})",
            icon=folium.Icon(
                color=color_map.get(place['type'], '#4CAF50'),
                icon=icon_map.get(place['type'], 'info-sign'),
                prefix='fa'
            )
        ).add_to(m)
    
    # 레이어 컨트롤 추가
    folium.LayerControl().add_to(m)
    
    # 미니맵 추가
    from folium.plugins import MiniMap
    minimap = MiniMap(toggle_display=True)
    m.add_child(minimap)
    
    return m

# =============================================================================
# 개선된 CSS 스타일
# =============================================================================

def apply_enhanced_map_styles():
    """개선된 지도 페이지 스타일 적용"""
    st.markdown("""
    <style>
        /* CSS 변수 정의 */
        :root {
            --primary-green: #4CAF50;
            --secondary-green: #81C784;
            --accent-green: #A5D6A7;
            --dark-green: #2E7D32;
            --light-green: #E8F5E8;
            --glass-bg: rgba(255, 255, 255, 0.95);
            --glass-border: rgba(76, 175, 80, 0.4);
            --shadow: 0 8px 32px 0 rgba(76, 175, 80, 0.2);
            --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            --border-radius: 20px;
        }

        /* 전체 앱 배경 */
        [data-testid="stAppViewContainer"] > .main {
            background: linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 50%, #A5D6A7 100%);
            min-height: 100vh;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* 메인 컨테이너 */
        .main .block-container {
            padding: 2rem 3rem !important;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        /* 페이지 제목 */
        .page-title {
            color: var(--dark-green) !important;
            text-align: center;
            background: var(--glass-bg);
            padding: 25px 30px;
            border-radius: var(--border-radius);
            font-size: clamp(2rem, 4vw, 2.8rem) !important;
            margin-bottom: 40px;
            font-weight: 800 !important;
            border: 3px solid var(--primary-green);
            box-shadow: var(--shadow);
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            letter-spacing: -0.02em;
            position: relative;
            overflow: hidden;
        }

        .page-title::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(76, 175, 80, 0.1), transparent);
            transition: var(--transition);
        }

        .page-title:hover::before {
            left: 100%;
            transition: left 0.8s ease;
        }
        
        /* 카드 컴포넌트 기본 스타일 */
        .card-base {
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            border: 2px solid var(--glass-border);
            border-radius: 18px;
            padding: 25px 30px;
            margin: 25px 0;
            transition: var(--transition);
            position: relative;
            overflow: hidden;
        }

        .card-base::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--primary-green), var(--secondary-green));
            transform: scaleX(0);
            transition: var(--transition);
        }

        .card-base:hover::before {
            transform: scaleX(1);
        }

        .card-base:hover {
            border-color: var(--primary-green);
            box-shadow: var(--shadow);
            transform: translateY(-2px);
        }
        
        /* 클러스터 결과 카드 */
        .cluster-result-card {
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            border: 2px solid var(--glass-border);
            border-radius: 18px;
            padding: 25px 30px;
            margin: 25px 0;
            border-left: 6px solid var(--primary-green);
            text-align: center;
            min-height: 300px;
            transition: var(--transition);
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        
        .score-display {
            background: linear-gradient(45deg, var(--primary-green), var(--secondary-green));
            color: white;
            padding: 12px 24px;
            border-radius: 30px;
            font-weight: 700;
            display: inline-block;
            margin: 15px 0;
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
            text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
            font-size: 1.1em;
        }
        
        /* 통계 카드 */
        .stats-card, .metric-card {
            background: var(--glass-bg);
            border: 2px solid var(--glass-border);
            border-radius: 18px;
            padding: 25px 20px;
            text-align: center;
            margin: 15px 0;
            transition: var(--transition);
            height: 140px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            position: relative;
            overflow: hidden;
        }
        
        .stats-card::before, .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(76, 175, 80, 0.1), transparent);
            transition: var(--transition);
        }

        .stats-card:hover::before, .metric-card:hover::before {
            left: 100%;
            transition: left 0.6s ease;
        }
        
        .stats-card:hover, .metric-card:hover {
            border-color: var(--primary-green);
            box-shadow: 0 8px 25px rgba(76, 175, 80, 0.25);
            transform: translateY(-5px) scale(1.02);
            background: rgba(255, 255, 255, 1);
        }
        
        .stats-number, .metric-number {
            font-size: 2.8em;
            font-weight: 800;
            color: var(--dark-green);
            margin-bottom: 8px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
            line-height: 1;
        }
        
        .stats-label, .metric-label {
            color: var(--dark-green);
            font-size: 1.2em;
            font-weight: 600;
            letter-spacing: 0.5px;
            line-height: 1.2;
        }
        
        /* 섹션 제목 */
        .section-title {
            color: var(--dark-green) !important;
            font-size: clamp(1.5rem, 3vw, 2rem);
            font-weight: 700;
            margin: 40px 0 25px 0;
            text-align: center;
            background: var(--glass-bg);
            padding: 15px 25px;
            border-radius: 15px;
            border-left: 5px solid var(--primary-green);
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.15);
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
            position: relative;
        }

        .section-title::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 50px;
            height: 3px;
            background: var(--primary-green);
            border-radius: 2px;
        }
        
        /* 범례/설정 카드 */
        .legend-card, .setting-card {
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            border: 2px solid var(--glass-border);
            border-radius: 18px;
            padding: 25px;
            margin: 20px 0;
            transition: var(--transition);
            position: relative;
        }
        
        .legend-card:hover, .setting-card:hover {
            border-color: var(--primary-green);
            box-shadow: var(--shadow);
            transform: translateY(-3px);
        }
        
        /* 필터 카드 */
        .filter-card {
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            border: 2px solid var(--glass-border);
            border-radius: 18px;
            padding: 25px 30px;
            margin: 25px 0;
            min-height: 300px;
            transition: var(--transition);
        }
        
        .filter-card:hover {
            border-color: var(--primary-green);
            box-shadow: var(--shadow);
        }
        
        /* 지도 컨테이너 개선 */
        .map-container {
            background: var(--glass-bg);
            border: 3px solid var(--primary-green);
            border-radius: var(--border-radius);
            padding: 20px;
            margin: 30px 0;
            box-shadow: var(--shadow);
            position: relative;
            overflow: hidden;
        }

        .map-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 6px;
            background: linear-gradient(90deg, var(--primary-green), var(--secondary-green), var(--accent-green));
        }
        
        /* 버튼 스타일 개선 */
        div[data-testid="stButton"] > button {
            background: linear-gradient(45deg, var(--primary-green), var(--secondary-green)) !important;
            border: none !important;
            border-radius: 15px !important;
            color: white !important;
            font-weight: 700 !important;
            padding: 12px 25px !important;
            transition: var(--transition) !important;
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3) !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            width: 100% !important;
            position: relative !important;
            overflow: hidden !important;
        }

        div[data-testid="stButton"] > button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: var(--transition);
        }
        
        div[data-testid="stButton"] > button:hover {
            background: linear-gradient(45deg, #388E3C, var(--primary-green)) !important;
            transform: translateY(-3px) !important;
            box-shadow: 0 8px 25px rgba(76, 175, 80, 0.4) !important;
        }

        div[data-testid="stButton"] > button:hover::before {
            left: 100%;
            transition: left 0.5s ease;
        }
        
        /* 메뉴 제목 */
        .menu-title {
            color: var(--dark-green);
            text-align: center;
            margin-bottom: 20px;
            font-weight: 700;
            font-size: 1.3em;
        }
        
        /* 사용자 정보 표시 */
        .user-info {
            color: var(--dark-green);
            font-weight: 600;
            line-height: 1.6;
        }

        /* 셀렉트박스 및 슬라이더 스타일링 */
        .stSelectbox > div > div {
            background: var(--glass-bg) !important;
            border: 2px solid var(--glass-border) !important;
            border-radius: 12px !important;
        }

        .stSlider > div > div > div > div {
            color: var(--primary-green) !important;
        }

        /* 체크박스 스타일링 */
        .stCheckbox > label {
            background: var(--glass-bg) !important;
            border: 1px solid var(--glass-border) !important;
            border-radius: 8px !important;
            padding: 8px 12px !important;
            margin: 5px 0 !important;
            transition: var(--transition) !important;
        }

        .stCheckbox > label:hover {
            border-color: var(--primary-green) !important;
            background: rgba(76, 175, 80, 0.1) !important;
        }
        
        /* 경고 및 정보 메시지 */
        div[data-testid="stAlert"] {
            background: var(--glass-bg) !important;
            border: 2px solid #FF8A65 !important;
            border-radius: 12px !important;
            color: var(--dark-green) !important;
            font-weight: 600 !important;
            backdrop-filter: blur(10px) !important;
        }
        
        /* 성공 메시지 */
        div[data-testid="stAlert"][data-baseweb="notification"] {
            border-color: var(--primary-green) !important;
            background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(129, 199, 132, 0.05)) !important;
        }

        /* 지도 설정 패널 개선 */
        .map-settings-panel {
            background: var(--glass-bg);
            border: 2px solid var(--glass-border);
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
        }

        .map-settings-panel h4 {
            color: var(--dark-green);
            margin-bottom: 15px;
            font-weight: 700;
            border-bottom: 2px solid var(--accent-green);
            padding-bottom: 8px;
        }
        
        /* 기본 UI 숨김 */
        [data-testid="stHeader"] { display: none; }
        [data-testid="stSidebarNav"] { display: none; }
        [data-testid="stSidebar"] { display: none; }
        [data-testid="collapsedControl"] { display: none; }
        footer { display: none; }
        
        /* 반응형 디자인 개선 */
        @media (max-width: 1200px) {
            .main .block-container {
                padding: 1.5rem 2rem !important;
            }
        }

        @media (max-width: 768px) {
            .main .block-container {
                padding: 1rem 1.5rem !important;
            }
            
            .page-title {
                font-size: 2rem !important;
                padding: 20px 25px !important;
            }
            
            .stats-number, .metric-number {
                font-size: 2.2em;
            }
            
            .section-title {
                font-size: 1.5em;
                padding: 12px 20px;
            }
            
            .legend-card, .setting-card {
                padding: 15px 20px;
            }

            .cluster-result-card {
                min-height: 250px;
            }
        }

        @media (max-width: 480px) {
            .stats-card, .metric-card {
                height: 120px;
            }

            .stats-number, .metric-number {
                font-size: 2em;
            }

            .card-base {
                padding: 20px;
            }
        }

        /* 접근성 개선 */
        @media (prefers-reduced-motion: reduce) {
            * {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
        }

        /* 포커스 상태 개선 */
        button:focus,
        input:focus,
        select:focus {
            outline: 3px solid rgba(76, 175, 80, 0.5) !important;
            outline-offset: 2px !important;
        }

        /* 스크롤바 스타일링 */
        ::-webkit-scrollbar {
            width: 8px;
        }

        ::-webkit-scrollbar-track {
            background: var(--light-green);
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb {
            background: var(--primary-green);
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: var(--dark-green);
        }
    </style>
    """, unsafe_allow_html=True)

# =============================================================================
# 지도 정보 및 설정 함수 (키 충돌 해결)
# =============================================================================

def render_map_settings():
    """지도 설정 렌더링 - 고유한 키로 중복 오류 해결"""
    
    st.markdown('<h2 class="section-title">🗺️ 지도로 관광지 보기</h2>', unsafe_allow_html=True)
    
    # 설정 패널을 확장 가능한 영역으로 구성
    with st.expander("🛠️ 지도 설정", expanded=True):
        settings_col1, settings_col2 = st.columns(2)
        
        with settings_col1:
            st.markdown('<div class="map-settings-panel">', unsafe_allow_html=True)
            st.markdown("#### 📊 표시 옵션")
            
            # 고유한 키를 사용하여 위젯 생성
            num_places = st.slider(
                "표시할 추천지 수",
                min_value=1,
                max_value=8,
                value=6,
                key="map_places_slider_unique_v2"  # 고유한 키로 변경
            )
            
            map_center = st.selectbox(
                "지도 중심점",
                ["전체 보기", "인천공항", "서울 중심", "부산 중심", "제주 중심"],
                key="map_center_select_unique_v2"  # 고유한 키로 변경
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with settings_col2:
            st.markdown('<div class="map-settings-panel">', unsafe_allow_html=True)
            st.markdown("#### 🎨 카테고리 필터")
            
            show_categories = {}
            category_cols = st.columns(2)
            
            for i, category in enumerate(wellness_destinations.keys()):
                col_idx = i % 2
                with category_cols[col_idx]:
                    show_categories[category] = st.checkbox(
                        category,
                        value=True,
                        key=f"show_category_{category.replace('/', '_')}_unique_v2"  # 고유한 키로 변경
                    )
            st.markdown('</div>', unsafe_allow_html=True)
    
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
    wellness_type, wellness_color = classify_wellness_type(cluster_result['score'], cluster_id)
    
    st.markdown('<h2 class="section-title">🎭 당신의 여행 성향 분석</h2>', unsafe_allow_html=True)
    
    analysis_col1, analysis_col2 = st.columns([1, 2])
    
    with analysis_col1:
        st.markdown(f"""
        <div class="cluster-result-card" style="border-color: {cluster_data['color']};">
            <h3 style="color: {cluster_data['color']}; margin-bottom: 15px; text-align: center;">
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
        st.markdown(f"""
        <div class="filter-card">
            <h4 style="color: #2E7D32; margin-bottom: 15px;">🎨 지도 범례 및 정보</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
                <div style="text-align: center; background: #f8f9fa; padding: 12px; border-radius: 10px;">
                    <div style="font-size: 1.8em; margin-bottom: 5px;">🔴</div>
                    <div style="font-weight: 600; color: #2E7D32; font-size: 0.9em;">인천공항</div>
                    <div style="font-size: 0.8em; color: #666;">(출발지)</div>
                </div>
                <div style="text-align: center; background: #f8f9fa; padding: 12px; border-radius: 10px;">
                    <div style="font-size: 1.8em; margin-bottom: 5px;">🔵</div>
                    <div style="font-weight: 600; color: #2E7D32; font-size: 0.9em;">한류/쇼핑</div>
                </div>
                <div style="text-align: center; background: #f8f9fa; padding: 12px; border-radius: 10px;">
                    <div style="font-size: 1.8em; margin-bottom: 5px;">🟢</div>
                    <div style="font-weight: 600; color: #2E7D32; font-size: 0.9em;">전통문화</div>
                </div>
                <div style="text-align: center; background: #f8f9fa; padding: 12px; border-radius: 10px;">
                    <div style="font-size: 1.8em; margin-bottom: 5px;">🟣</div>
                    <div style="font-weight: 600; color: #2E7D32; font-size: 0.9em;">자연/힐링</div>
                </div>
            </div>
            <div style="text-align: center; background: #f8f9fa; padding: 12px; border-radius: 10px; margin-bottom: 15px;">
                <div style="font-size: 1.8em; margin-bottom: 5px;">🟠</div>
                <div style="font-weight: 600; color: #2E7D32; font-size: 0.9em;">음식/체험</div>
            </div>
            <div style="background: #e8f5e8; padding: 12px; border-radius: 10px; border-left: 4px solid #4CAF50;">
                <p style="margin: 0; color: #2E7D32; font-size: 0.9em; font-weight: 600;">
                    💡 팁: 지도의 마커를 클릭하면 상세 정보를 확인할 수 있습니다!
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    return cluster_result

def render_travel_statistics(places_to_show):
    """여행 통계 정보 렌더링"""
    if not places_to_show:
        return
        
    st.markdown('<h2 class="section-title">📊 추천 관광지 통계</h2>', unsafe_allow_html=True)
    
    # 통계 계산
    avg_distance = np.mean([place['distance_from_incheon'] for place in places_to_show])
    avg_rating = np.mean([place['rating'] for place in places_to_show])
    
    # 자가용 비용 계산 (숫자만 추출)
    car_costs = []
    for place in places_to_show:
        cost_str = place['travel_cost_car'].replace(',', '').replace('원', '')
        if '(' in cost_str:
            cost_str = cost_str.split('(')[0]
        try:
            car_costs.append(int(cost_str))
        except:
            car_costs.append(0)
    
    avg_car_cost = np.mean([cost for cost in car_costs if cost > 0])
    
    # 평균 추천 점수
    avg_rec_score = 0
    if places_to_show and 'recommendation_score' in places_to_show[0]:
        avg_rec_score = np.mean([place['recommendation_score'] for place in places_to_show])
    
    # 통계 카드 표시
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
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
            <div class="stats-label">평균 교통비</div>
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
                <div class="stats-label">평균 추천점수</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number">{len(places_to_show)}</div>
                <div class="stats-label">표시 관광지</div>
            </div>
            """, unsafe_allow_html=True)

def render_recommendation_list(places_to_show):
    """추천 관광지 목록 카드 렌더링"""
    st.markdown('<h2 class="section-title">📋 추천 관광지 목록</h2>', unsafe_allow_html=True)
    
    # 카드 그리드로 표시
    cols = st.columns(2)
    for i, place in enumerate(places_to_show):
        col_idx = i % 2
        
        with cols[col_idx]:
            # 순위 이모지
            if i == 0:
                rank_emoji = "🥇"
                rank_color = "#FFD700"
            elif i == 1:
                rank_emoji = "🥈" 
                rank_color = "#C0C0C0"
            elif i == 2:
                rank_emoji = "🥉"
                rank_color = "#CD7F32"
            else:
                rank_emoji = f"#{i+1}"
                rank_color = "#4CAF50"
            
            st.markdown(f"""
            <div class="legend-card">
                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                    <span style="font-size: 3em; margin-right: 15px;">{place['image_url']}</span>
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
                            <h4 style="color: #2E7D32; margin: 0; font-size: 1.2em;">{place['name']}</h4>
                            <span style="background: {rank_color}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 0.8em; font-weight: bold;">{rank_emoji}</span>
                        </div>
                        <p style="color: #2E7D32; margin: 0; font-size: 0.9em; font-weight: 600;">{place['type']}</p>
                    </div>
                </div>
                <div style="background: #f8f9fa; padding: 12px; border-radius: 10px; margin-bottom: 15px;">
                    <p style="color: #2E7D32; margin: 0; font-size: 0.9em; line-height: 1.4;">
                        {place['description'][:80]}...
                    </p>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; font-size: 0.85em; font-weight: 600; color: #2E7D32;">
                    <div style="text-align: center;">
                        <div>⭐ {place['rating']}/5</div>
                    </div>
                    <div style="text-align: center;">
                        <div>💰 {place['price_range'][:10]}{'...' if len(place['price_range']) > 10 else ''}</div>
                    </div>
                    <div style="text-align: center;">
                        <div>📍 {place['distance_from_incheon']}km</div>
                    </div>
                </div>
                {f'<div style="text-align: center; margin-top: 10px;"><span style="background: linear-gradient(45deg, #4CAF50, #81C784); color: white; padding: 6px 12px; border-radius: 15px; font-size: 0.8em; font-weight: bold;">🎯 {place["recommendation_score"]:.1f}점</span></div>' if 'recommendation_score' in place else ''}
            </div>
            """, unsafe_allow_html=True)

# =============================================================================
# 메인 지도 페이지 함수
# =============================================================================

def enhanced_map_view_page():
    """개선된 지도 뷰 페이지"""
    
    # 스타일 적용
    apply_enhanced_map_styles()
    
    # 헤더
    st.title('🌿 웰컴 투어 추천 시스템')
    st.markdown("---")
    
    # 지도 설정 렌더링
    num_places, map_center, show_categories = render_map_settings()
    
    # 사용자 클러스터 분석 표시
    cluster_result = render_user_cluster_analysis()
    
    # 제목
    st.markdown("---")
    st.markdown('<h1 class="page-title">🗺️ 맞춤형 웰니스 여행지 지도</h1>', unsafe_allow_html=True)
    
    # 추천 결과 가져오기
    if 'recommended_places' not in st.session_state:
        if 'answers' in st.session_state and st.session_state.answers:
            # 세션 상태에 따라 고유한 키로 캐시 관리
            cache_key = str(hash(str(st.session_state.answers)))
            st.session_state.recommended_places = calculate_recommendations_with_cluster(st.session_state.answers)
        else:
            st.error("❌ 설문 데이터가 없습니다. 설문을 먼저 완료해주세요.")
            if st.button("📝 설문하러 가기"):
                st.switch_page("pages/01_questionnaire.py")
            return
    
    recommended_places = st.session_state.recommended_places
    
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
    
    # 클러스터 분석 결과 요약 표시
    if cluster_result:
        cluster_info = get_cluster_info()
        if cluster_result['cluster'] in cluster_info:
            cluster_data = cluster_info[cluster_result['cluster']]
            
            st.markdown('<h2 class="section-title">🎯 개인 맞춤 분석 결과</h2>', unsafe_allow_html=True)
            
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
    st.markdown('<h2 class="section-title">🌍 인터랙티브 관광지 지도</h2>', unsafe_allow_html=True)
    
    # 지도 컨테이너
    st.markdown('<div class="map-container">', unsafe_allow_html=True)
    
    try:
        wellness_map = create_enhanced_wellness_map(places_to_show, center_lat, center_lon, zoom)
        
        # 지도 표시
        map_data = st_folium(
            wellness_map, 
            width=1200, 
            height=600, 
            returned_objects=["last_object_clicked"],
            key="wellness_map_unique_v2"  # 고유한 키로 변경
        )
        
        # 클릭된 마커 정보 표시
        if map_data.get('last_object_clicked'):
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
                    st.markdown('<div class="legend-card" style="margin-top: 20px;">', unsafe_allow_html=True)
                    st.markdown(f'<h3 style="color: #2E7D32; text-align: center;">📍 선택된 관광지: {selected_place["name"]}</h3>', unsafe_allow_html=True)
                    
                    selected_col1, selected_col2 = st.columns([1, 2])
                    
                    with selected_col1:
                        st.markdown(f"""
                        <div style="text-align: center; background: #f8f9fa; padding: 20px; border-radius: 15px;">
                            <div style="font-size: 4em; margin-bottom: 10px;">{selected_place['image_url']}</div>
                            <div style="font-size: 2.5em; font-weight: 800; color: #2E7D32; margin-bottom: 5px;">{selected_place['rating']}</div>
                            <div style="color: #666; font-weight: 600;">평점</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with selected_col2:
                        st.markdown(f"""
                        <div style="background: #f8f9fa; padding: 20px; border-radius: 15px; height: 100%;">
                            <p style="margin: 0 0 10px 0; color: #2E7D32; font-weight: 600;"><strong>🏷️ 유형:</strong> {selected_place['type']}</p>
                            <p style="margin: 0 0 10px 0; color: #2E7D32; font-weight: 600;"><strong>📍 설명:</strong> {selected_place['description']}</p>
                            <p style="margin: 0 0 10px 0; color: #2E7D32; font-weight: 600;"><strong>💰 가격:</strong> {selected_place['price_range']}</p>
                            <p style="margin: 0 0 10px 0; color: #2E7D32; font-weight: 600;"><strong>📏 거리:</strong> {selected_place['distance_from_incheon']}km</p>
                            <p style="margin: 0 0 10px 0; color: #2E7D32; font-weight: 600;"><strong>🚗 자가용:</strong> {selected_place['travel_time_car']} ({selected_place['travel_cost_car']})</p>
                            <p style="margin: 0 0 15px 0; color: #2E7D32; font-weight: 600;"><strong>🚊 대중교통:</strong> {selected_place['travel_time_train']} ({selected_place['travel_cost_train']})</p>
                            
                            {'<p style="margin: 0; color: #2E7D32; font-weight: 600;"><strong>🎯 추천 점수:</strong> ' + str(selected_place.get('recommendation_score', 0))[:5] + '/20</p>' if 'recommendation_score' in selected_place else ''}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div style="text-align: center; margin: 20px 0;">
                        <a href="{selected_place['website']}" target="_blank" style="background: linear-gradient(45deg, #4CAF50, #81C784); color: white; padding: 12px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; display: inline-block;">
                            🌐 공식 웹사이트 방문
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"❌ 지도 로딩 중 오류가 발생했습니다: {str(e)}")
        st.info("💡 페이지를 새로고침하거나 설정을 다시 조정해보세요.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 여행 통계 표시
    render_travel_statistics(places_to_show)
    
    # 추천 관광지 목록
    st.markdown("---")
    render_recommendation_list(places_to_show)
    
    # 액션 버튼
    st.markdown("---")
    st.markdown('<h2 class="section-title">🎯 다음 단계</h2>', unsafe_allow_html=True)
    
    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        if st.button("📝 설문 다시하기", key="map_restart_survey"):
            # 세션 상태 클리어
            for key in ['survey_completed', 'answers', 'score_breakdown', 'recommended_places']:
                if key in st.session_state:
                    del st.session_state[key]
            st.switch_page("pages/01_questionnaire.py")
    
    with action_col2:
        if st.button("📊 상세 추천 결과", key="map_view_results"):
            st.switch_page("pages/04_recommendations.py")
    
    with action_col3:
        if st.button("📈 통계 분석 보기", key="map_view_stats"):
            st.switch_page("pages/06_statistics.py")
    
    # 푸터 정보
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; background: rgba(255, 255, 255, 0.8); padding: 20px; border-radius: 15px; margin: 30px 0;">
        <h4 style="color: #2E7D32; margin-bottom: 10px;">💡 지도 사용 팁</h4>
        <p style="color: #2E7D32; margin: 0; font-weight: 600; line-height: 1.6;">
            • 마커를 클릭하면 관광지 상세 정보를 확인할 수 있습니다<br>
            • 지도 우측 상단의 레이어 버튼으로 지도 스타일을 변경할 수 있습니다<br>
            • 점선은 인천공항에서 각 관광지까지의 경로를 나타냅니다<br>
            • 미니맵을 통해 현재 보고 있는 지역을 파악할 수 있습니다
        </p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# 캐시 관리 및 성능 최적화
# =============================================================================

def clear_map_cache():
    """지도 관련 캐시 클리어"""
    if 'recommended_places' in st.session_state:
        del st.session_state['recommended_places']
    
    # Streamlit 캐시 클리어
    calculate_recommendations_with_cluster.clear()

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
        
        if st.button("🔄 페이지 새로고침"):
            st.rerun()
        
        if st.button("🏠 홈으로 돌아가기"):
            st.switch_page("pages/03_home.py")

if __name__ == "__main__":
    main()
else:
    main()