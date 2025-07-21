# pages/04_recommendations.py (웰니스 추천 결과 페이지)

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils import (check_access_permissions, questions, determine_cluster, 
                  get_cluster_info, create_user_persona_analysis, 
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
    page_title="웰니스 투어 추천 결과",
    page_icon="🎯",
    layout="wide"
)

# 접근 권한 확인
check_access_permissions()

# 한국 관광지 데이터 (실제 클러스터 분석에 맞게 수정)
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

# 실제 클러스터 분석 결과 기반 추천 알고리즘 (수정됨)
def calculate_cluster_recommendations(survey_answers):
    """실제 클러스터 분석 결과 기반 추천 계산 - 100점 만점 표준화"""
    if not survey_answers:
        return []
    
    # 클러스터 결정
    cluster_result = determine_cluster(survey_answers)
    cluster_id = cluster_result['cluster']
    
    # 실제 클러스터 분석 결과 기반 추천 카테고리
    cluster_preferences = {
        0: ["한류/쇼핑", "음식/체험"],          # 한류 트렌디형 - 한류 콘텐츠, 쇼핑 선호
        1: ["한류/쇼핑", "음식/체험", "전통문화"],  # 종합형 실속파 - 다양한 관심사
        2: ["자연/힐링"],                      # 수동형 관광객 - 소극적 관광
        3: ["음식/체험", "한류/쇼핑"],          # 체험중심 실용형 - 음식/쇼핑 중심
        4: ["전통문화", "한류/쇼핑"],          # 고소득 전통형 - 전통문화 + 면세점
        5: ["전통문화"],                      # 행사 관심형 - 전통문화/행사 중심
        6: ["자연/힐링", "전통문화"],          # 자연 힐링형 - 자연경관 중시
        7: ["자연/힐링"]                      # 소외형 여행객 - 소극적 참여
    }
    
    preferred_categories = cluster_preferences.get(cluster_id, ["음식/체험"])
    recommendations = []
    
    # 점수 비중 설정 (총 100점)
    MAX_CATEGORY_SCORE = 40  # 카테고리 선호도 (40점)
    MAX_RATING_SCORE = 30    # 평점 점수 (30점)
    MAX_CLUSTER_SCORE = 20   # 클러스터 점수 (20점)
    MAX_DISTANCE_SCORE = 10  # 거리 보정 (10점)
    
    # 모든 관광지에 대해 점수 계산
    for category, places in wellness_destinations.items():
        for place in places:
            # 1. 클러스터 선호 카테고리 점수 (40점 만점)
            category_score = 0
            if category in preferred_categories:
                preference_rank = preferred_categories.index(category)
                if preference_rank == 0:
                    category_score = 40  # 1순위 선호
                elif preference_rank == 1:
                    category_score = 30  # 2순위 선호
                elif preference_rank == 2:
                    category_score = 20  # 3순위 선호
            
            # 2. 관광지 평점 점수 (30점 만점)
            rating_score = (place["rating"] / 5.0) * MAX_RATING_SCORE
            
            # 3. 개인 클러스터 매칭 점수 (20점 만점)
            cluster_score = (cluster_result['score'] / 30.0) * MAX_CLUSTER_SCORE
            
            # 4. 접근성 보정 점수 (10점 만점)
            min_distance = 35   # 최단거리 (홍대)
            max_distance = 500  # 최장거리 기준
            distance_score = max(0, (max_distance - place['distance_from_incheon']) / (max_distance - min_distance)) * MAX_DISTANCE_SCORE
            
            # 총점 계산 (100점 만점)
            total_score = category_score + rating_score + cluster_score + distance_score
            
            place_with_score = place.copy()
            place_with_score["recommendation_score"] = round(total_score, 1)
            place_with_score["cluster_id"] = cluster_id
            place_with_score["cluster_confidence"] = cluster_result['confidence']
            
            # 점수 세부사항 추가
            place_with_score["score_breakdown"] = {
                "category": round(category_score, 1),
                "rating": round(rating_score, 1),
                "cluster": round(cluster_score, 1),
                "distance": round(distance_score, 1)
            }
            
            recommendations.append(place_with_score)
    
    # 점수 순으로 정렬
    recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)
    
    return recommendations[:8]

# CSS 스타일
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
    
    .recommendations-title {
        color: #2E7D32 !important;
        text-align: left;
        background: rgba(255, 255, 255, 0.95);
        padding: 25px 30px;
        font-size: 2.8em !important;
        margin-bottom: 40px;
        font-weight: 800 !important;
        letter-spacing: 1px;
    }
    
    .cluster-result-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 18px;
        padding: 25px 30px;
        margin: 25px 0;
        border-left: 6px solid #4CAF50;
        text-align: center;
        min-height: 300px;
    }
    
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
    
    .filter-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 18px;
        padding: 25px 30px;
        margin: 25px 0;
        min-height: 300px;
        transition: all 0.3s ease;
    }
    
    .filter-container:hover {
        border-color: #4CAF50;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.2);
    }
    
    /* 필터 컨테이너 내부의 컬럼 스타일링 */
    .filter-container div[data-testid="column"] {
        padding: 10px;
    }
    
    .filter-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 18px;
        padding: 25px 30px;
        margin: 25px 0;
        min-height: 300px;
        transition: all 0.3s ease;
    }
    
    .filter-card:hover {
        border-color: #4CAF50;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.2);
    }
    
    .chart-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 20px;
        padding: 25px;
        margin: 20px 0;
    }
    
    .chart-container:hover {
        border-color: #4CAF50;
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.2);
    }
    
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
    
    .user-info {
        color: #2E7D32;
        font-weight: 600;
        line-height: 1.6;
    }
    
    .menu-title {
        color: #2E7D32;
        text-align: center;
        margin-bottom: 20px;
        font-weight: 700;
    }
    
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
    
    [data-testid="stHeader"] { display: none; }
    [data-testid="stSidebarNav"] { display: none; }
    [data-testid="stSidebar"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }
    footer { display: none; }
    
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

# 메인 추천 결과 페이지
def recommendations_page():
    
    # 제목
    st.title('🌿 웰커밍 투어추천 시스템')
    st.markdown("---")
    
    # 클러스터 분석 결과 표시
    if 'answers' in st.session_state and st.session_state.answers:
        cluster_result = determine_cluster(st.session_state.answers)
        cluster_id = cluster_result['cluster']
        cluster_info = get_cluster_info()
        
        if cluster_id in cluster_info:
            cluster_data = cluster_info[cluster_id]
            wellness_type, wellness_color = classify_wellness_type(cluster_result['score'], cluster_id)
            
            st.markdown('<h2 class="section-title">🎭 당신의 한국 여행 성향</h2>', unsafe_allow_html=True)
            
            analysis_col1, analysis_col2 = st.columns([1, 2])
            
            with analysis_col1:
                st.markdown(f"""
                <div class="cluster-result-card" style="border-color: {cluster_data['color']};">
                    <h3 style="color: {cluster_data['color']}; margin-bottom: 15px;">
                        🏆 {cluster_data['name']}
                    </h3>
                    <div class="score-display">
                        매칭 점수: {cluster_result['score']}/30
                    </div>
                    <p style="color: #2E7D32; font-weight: 600; margin-top: 15px; font-size: 0.9em;">
                        신뢰도: {cluster_result['confidence']:.1%}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with analysis_col2:
                # 페르소나 분석 표시
                persona_analysis = create_user_persona_analysis(st.session_state.answers, wellness_type)
                
                st.markdown(f"""
                <div class="filter-card">
                    <h4 style="color: #2E7D32; margin-bottom: 15px;">📊 성향 분석 결과</h4>
                    <p style="color: #2E7D32; font-weight: 600; margin-bottom: 15px;">
                        <strong>✨ 특징:</strong><br>{persona_analysis['특징']}
                    </p>
                    <p style="color: #2E7D32; font-weight: 600; margin-bottom: 15px;">
                        <strong>🎯 추천활동:</strong><br>{persona_analysis['추천활동']}
                    </p>
                    <p style="color: #2E7D32; font-weight: 600; margin: 0;">
                        <strong>💡 여행팁:</strong><br>{persona_analysis['여행팁']}
                    </p>
                </div>
                """, unsafe_allow_html=True)

    # 설문 결과 요약
    with st.expander("📋 설문 응답 내역", expanded=False):
        if 'answers' in st.session_state and st.session_state.answers:
            for key, answer in st.session_state.answers.items():
                if key in questions:
                    question_title = questions[key]['title']
                    question_data = questions[key]
                    
                    # 복수응답 문항 처리
                    if question_data.get('multiple', False):
                        if isinstance(answer, list) and answer:
                            answer_texts = []
                            for idx in answer:
                                if idx < len(question_data['options']):
                                    answer_texts.append(f"• {question_data['options'][idx]}")
                            answer_display = "\n".join(answer_texts) if answer_texts else "답변 없음"
                        else:
                            answer_display = "답변 없음"
                    # 단일응답 문항 처리
                    else:
                        if answer is not None and answer < len(question_data['options']):
                            answer_display = f"• {question_data['options'][answer]}"
                        else:
                            answer_display = "답변 없음"
                    
                    st.markdown(f"**{question_title}**")
                    st.markdown(answer_display)
                    st.markdown("---")
        else:
            st.markdown("설문 답변 데이터가 없습니다.")
    
    st.markdown("---")

    # 필터 섹션
    def create_filter_section():
        """필터 섹션을 생성하고 선택된 값들을 반환합니다."""
        st.markdown('<h2 class="section-title">🎛️ 추천 필터</h2>', unsafe_allow_html=True)
        
        # 세션 상태 초기화
        if 'category_filter' not in st.session_state:
            st.session_state.category_filter = list(wellness_destinations.keys())
        if 'distance_filter' not in st.session_state:
            st.session_state.distance_filter = 500
        
        # expander를 사용한 필터 섹션
        with st.expander("🎛️ 필터 옵션 설정", expanded=True):
            filter_col1, filter_col2, filter_col3 = st.columns(3)
            
            with filter_col1:
                st.markdown("#### 🏷️ 관심 카테고리")
                selected_categories = st.multiselect(
                    "카테고리를 선택하세요",
                    list(wellness_destinations.keys()),
                    default=st.session_state.category_filter,
                    key="category_filter_new",
                    help="원하는 관광 카테고리를 모두 선택하세요"
                )
                st.session_state.category_filter = selected_categories
            
            with filter_col2:
                st.markdown("#### 📏 거리 설정")
                distance_max = st.slider(
                    "최대 거리 (km)",
                    min_value=30,
                    max_value=500,
                    value=st.session_state.distance_filter,
                    step=50,
                    key="distance_filter_new",
                    help="인천공항으로부터의 최대 허용 거리"
                )
                st.session_state.distance_filter = distance_max
            
            with filter_col3:
                st.markdown("#### 👤 현재 설정")
                
                # 사용자 정보 계산
                cluster_name = "미분석"
                if 'answers' in st.session_state and st.session_state.answers:
                    cluster_result = determine_cluster(st.session_state.answers)
                    cluster_info = get_cluster_info()
                    if cluster_result['cluster'] in cluster_info:
                        cluster_name = cluster_info[cluster_result['cluster']]['name']
                
                # 현재 설정 요약 표시
                st.info(f"""
                **👤 사용자:** {st.session_state.username}  
                **🎭 성향:** {cluster_name}  
                **📊 선택된 카테고리:** {len(selected_categories)}개  
                **📏 거리 범위:** {distance_max}km 이내
                """)
                
                # 필터링 결과 미리보기
                if selected_categories:
                    st.success(f"✅ {', '.join(selected_categories)}")
                else:
                    st.warning("⚠️ 카테고리를 하나 이상 선택하세요")
        
        return selected_categories, distance_max
    
    # 필터 섹션 호출
    selected_categories, distance_max = create_filter_section()

    # 추천 결과 계산
    recommended_places = calculate_cluster_recommendations(st.session_state.answers)
    
    # 필터 적용
    filtered_places = []
    for place in recommended_places:
        if place['type'] not in st.session_state.category_filter:
            continue
        if place['distance_from_incheon'] > st.session_state.distance_filter:
            continue
        filtered_places.append(place)
    
    # 추천 결과 표시
    def create_chart_section(filtered_places):
        """개선된 차트 섹션"""
        # 추천 결과 제목
        st.markdown(f'<h2 class="section-title">🏆 웰니스 관광지 추천 결과</h2>', 
                    unsafe_allow_html=True)
        
        if len(filtered_places) == 0:
            st.warning("⚠️ 필터 조건에 맞는 관광지가 없습니다. 필터를 조정해주세요.")
            return False
        
        # expander를 사용한 차트 섹션
        with st.expander("", expanded=True):
            # 차트 설정 옵션
            chart_col1, chart_col2 = st.columns([3, 1])
            
            with chart_col2:
                max_places = len(filtered_places)
                show_count = st.selectbox(
                    "표시할 개수",
                    options=list(range(1, max_places + 1)),
                    index=min(7, max_places - 1),  # 기본값: 8개 (인덱스는 7)
                    help="차트에 표시할 관광지 개수를 선택하세요"
                )
            
            # 데이터 준비
            display_count = min(show_count, len(filtered_places))
            chart_places = filtered_places[:display_count]
            
            names = [place['name'] for place in chart_places]
            scores = [place['recommendation_score'] for place in chart_places]
            types = [place['type'] for place in chart_places]
            
            # 차트 생성
            fig = px.bar(
                x=names,
                y=scores,
                color=types,
                title=f"카테고리별 관광지 추천 점수 (100점 만점)",
                labels={'x': '관광지명', 'y': '추천 점수 (점)', 'color': '웰니스 카테고리'},
                text=scores,
                # 색상 대비 강화 - 더 구분되는 색상 사용
                color_discrete_sequence=['#2E7D32', '#FF6B35', '#6B73FF', '#FFD23F']
            )

            # 차트 레이아웃 개선
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#2E7D32',
                xaxis_tickangle=0,  # 관광지명 수평으로 변경
                font_size=11,
                height=500,  # 높이 증가로 범례와 겹침 방지
                title_x=0.5,  # 제목 중앙 정렬
                title_xanchor='center',  # 제목 앵커 중앙으로 설정
                title_font_size=16,  # 제목 크기 증가
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.35,  # 범례 위치를 더 아래로 이동
                    xanchor="center",
                    x=0.5,
                    bgcolor='rgba(255,255,255,0.8)',  # 범례 배경 추가
                    bordercolor='rgba(76, 175, 80, 0.3)',
                    borderwidth=1
                ),
                margin=dict(l=50, r=50, t=60, b=150),  # 하단 여백 증가
                xaxis=dict(
                    tickmode='array',
                    tickvals=list(range(len(names))),
                    ticktext=[name[:15] + '...' if len(name) > 15 else name for name in names],  # 긴 이름 줄임
                    tickfont=dict(size=10, color="#000000")
                )
            )

            # 텍스트 표시 개선
            fig.update_traces(
                texttemplate='%{text:.0f}점',
                textposition='outside',
                textfont_size=10,  # 텍스트 크기 증가
                textfont_color='#2E7D32',
                textfont_weight='bold'  # 텍스트 굵게
            )

            # y축 범위 조정
            if scores:
                fig.update_yaxes(range=[0, 100])  # 여백 증가

            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            # 차트 하단 통계 정보
            if scores:
                stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
                
                with stat_col1:
                    st.metric(
                        label="🏆 최고 점수",
                        value=f"{max(scores):.0f}점",
                        help="가장 높은 추천 점수"
                    )
                
                with stat_col2:
                    st.metric(
                        label="📊 평균 점수", 
                        value=f"{sum(scores)/len(scores):.0f}점",
                        help="표시된 관광지들의 평균 점수"
                    )
                
                with stat_col3:
                    st.metric(
                        label="📍 표시 개수",
                        value=f"{display_count}개",
                        help="현재 차트에 표시된 관광지 수"
                    )
                
                with stat_col4:
                    st.metric(
                        label="🎯 전체 결과", 
                        value=f"{len(filtered_places)}개",
                        help="필터 조건에 맞는 전체 관광지 수"
                    )
        
        return True
    
    st.markdown("---")

    def create_score_system_explanation():
        """점수 시스템 설명을 위한 별도 섹션"""
        
        # 점수 시스템 설명 박스
        with st.expander("📊 점수 시스템 이해하기", expanded=False):
            # 설명 섹션을 두 개 컬럼으로 나누기
            explain_col1, explain_col2 = st.columns([2, 1])
            
            with explain_col1:
                st.markdown("""
                ### 🎯 100점 만점 점수 구성
                
                **1. 카테고리 선호도 (40점) 🏆**
                - 🥇 1순위 선호 카테고리: **40점**
                - 🥈 2순위 선호 카테고리: **30점**  
                - 🥉 3순위 선호 카테고리: **20점**
                - ❌ 비선호 카테고리: **0점**
                
                **2. 관광지 평점 (30점) ⭐**
                - 관광지 평점(1-5점)을 30점으로 변환
                - 예시: 4.8점 → 28.8점, 4.0점 → 24점
                
                **3. 개인 클러스터 매칭 (20점) 🎭**
                - 설문 기반 개인 성향 점수 반영
                - 클러스터 점수(0-20점) 그대로 적용
                
                **4. 접근성 보정 (10점) 📍**
                - 인천공항으로부터의 거리 기반
                - 가까울수록 높은 점수 (60km=10점, 500km=0점)
                
                ---
                **💡 점수가 높을수록 당신에게 더 적합한 관광지입니다!**
                """)
            
            with explain_col2:
                # 점수 구성 비율 파이 차트
                score_components = {
                    "카테고리 선호도\n(40점)": 40,
                    "관광지 평점\n(30점)": 30,
                    "클러스터 매칭\n(20점)": 20,
                    "접근성\n(10점)": 10
                }
                
                fig_pie = px.pie(
                    values=list(score_components.values()),
                    names=list(score_components.keys()),
                    title="점수 구성 비율",
                    color_discrete_sequence=['#2E7D32', '#FF6B35', '#6B73FF', '#FFD23F']
                )
                
                fig_pie.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#2E7D32',
                    title_font_size=14,
                    title_x=0.5,
                    height=350,
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1.05,
                        font=dict(size=10)
                    ),
                    margin=dict(l=10, r=80, t=40, b=10)
                )
                
                fig_pie.update_traces(
                    textposition='inside',
                    textinfo='percent',
                    textfont_size=12,
                    textfont_color='white'
                )
                
                st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
            
            # 하단에 점수 해석 가이드 추가
            st.markdown("---")
            
            guide_col1, guide_col2, guide_col3 = st.columns(3)
            
            with guide_col1:
                st.markdown("""
                #### 🟢 높은 점수 (80-100점)
                - 당신의 성향에 **매우 적합**
                - 우선적으로 고려할 관광지
                - 만족도가 높을 것으로 예상
                """)
            
            with guide_col2:
                st.markdown("""
                #### 🟡 중간 점수 (60-79점)
                - 당신의 성향에 **적합**
                - 고려해볼 만한 관광지
                - 개인 취향에 따라 만족도 차이
                """)
            
            with guide_col3:
                st.markdown("""
                #### 🔴 낮은 점수 (0-59점)
                - 당신의 성향과 **다소 맞지 않음**
                - 신중한 고려 필요
                - 다른 대안 검토 권장
                """)

    # 차트 섹션 호출
    if not create_chart_section(filtered_places):
        return  # 결과가 없으면 여기서 종료
    
    # 점수 시스템 설명 박스
    create_score_system_explanation()
    
    # 상세 추천 결과
    st.markdown("---")
    st.markdown('<h3 class="section-title">🌿 상세 추천 정보</h3>', unsafe_allow_html=True)
    
    def create_recommendation_card_safe(place, index):
        """더 안전한 추천 카드 생성"""
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown(f"""
            <div style="text-align: center; font-size: 4.5em; margin: 25px 0; filter: drop-shadow(0 4px 8px rgba(76, 175, 80, 0.3));">
                {place['image_url']}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Streamlit 네이티브 컴포넌트 사용
            st.markdown(f"## #{index + 1} {place['name']}")
            st.write(place['description'])
            
            # 점수 표시
            st.success(f"🎯 추천 점수: {place['recommendation_score']:.0f}/100점")

            # 정보 태그들
            st.markdown(f"""
            <div style="display: flex; flex-wrap: wrap; gap: 10px; margin: 20px 0;">
                <div style="background: rgba(76, 175, 80, 0.15); border: 2px solid rgba(76, 175, 80, 0.3); border-radius: 12px; padding: 8px 15px; color: #2E7D32; font-weight: 700; flex: 1; min-width: 120px; text-align: center;">
                    ⭐ 평점 : {place['rating']}/5
                </div>
                <div style="background: rgba(76, 175, 80, 0.15); border: 2px solid rgba(76, 175, 80, 0.3); border-radius: 12px; padding: 8px 15px; color: #2E7D32; font-weight: 700; flex: 1; min-width: 120px; text-align: center;">
                    💰 비용 : {place['price_range']}
                </div>
                <div style="background: rgba(76, 175, 80, 0.15); border: 2px solid rgba(76, 175, 80, 0.3); border-radius: 12px; padding: 8px 15px; color: #2E7D32; font-weight: 700; flex: 1; min-width: 120px; text-align: center;">
                    📍 거리 : {place['distance_from_incheon']}km
                </div>
                <div style="background: rgba(76, 175, 80, 0.15); border: 2px solid rgba(76, 175, 80, 0.3); border-radius: 12px; padding: 8px 15px; color: #2E7D32; font-weight: 700; flex: 1; min-width: 120px; text-align: center;">
                    🏷️ 카테고리 : {place['type']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 교통 정보
            st.markdown(f"""
            **🚗 자가용:** {place['travel_time_car']} ({place['travel_cost_car']})  
            **🚊 대중교통:** {place['travel_time_train']} ({place['travel_cost_train']})  
            **🤖 AI 신뢰도:** {place['cluster_confidence']:.1%}
            """)
            
            # 버튼들
            btn_col1, btn_col2, btn_col3 = st.columns(3)
            
            with btn_col1:
                if st.button("🌐 공식 사이트", key=f"website_{index}", use_container_width=True):
                    st.markdown(f"🔗 **공식 사이트:** [{place['name']}]({place['website']})")
                    st.info("위 링크를 클릭하여 공식 사이트로 이동하세요!")

            with btn_col2:
                if st.button("🗺️ 지도에서 보기", key=f"map_{index}", use_container_width=True):
                    st.session_state.selected_place = place
                    st.switch_page("pages/05_map_view.py")

            with btn_col3:
                if st.button("💾 저장", key=f"save_{index}", use_container_width=True):
                    st.success(f"✅ {place['name']} 저장됨!")

    st.markdown("<br><br>", unsafe_allow_html=True)

    for i, place in enumerate(filtered_places):
        create_recommendation_card_safe(place, i)
        st.markdown("---")
    
    # 클러스터 분석 인사이트
    if 'answers' in st.session_state and st.session_state.answers:
        cluster_result = determine_cluster(st.session_state.answers)
        cluster_info = get_cluster_info()
        
        if cluster_result['cluster'] in cluster_info:
            cluster_data = cluster_info[cluster_result['cluster']]
            
            st.markdown('<h3 class="section-title">💡 AI 분석 인사이트</h3>', unsafe_allow_html=True)
            
            insight_col1, insight_col2 = st.columns(2)
            
            with insight_col1:
                st.markdown(f"""
                <div class="filter-card">
                    <h4 style="color: {cluster_data['color']};">🎯 당신의 성향 키워드</h4>
                    <div style="margin: 15px 0;">
                        {' '.join([f'<span class="info-tag" style="background: {cluster_data["color"]}20; border-color: {cluster_data["color"]}; color: {cluster_data["color"]};">{char}</span>' for char in cluster_data['characteristics']])}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with insight_col2:
                # 전체 클러스터 점수 분포
                all_scores = cluster_result['all_scores']
                top_clusters = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)[:3]
                
                st.markdown(f"""
                <div class="filter-card">
                    <h4 style="color: #2E7D32;">📊 클러스터 매칭 분석</h4>
                    <p style="color: #2E7D32; font-weight: 600; margin-bottom: 10px;">
                        <strong>1위:</strong> {cluster_info[top_clusters[0][0]]['name']} ({top_clusters[0][1]}점)<br>
                        <strong>2위:</strong> {cluster_info[top_clusters[1][0]]['name']} ({top_clusters[1][1]}점)<br>
                        <strong>3위:</strong> {cluster_info[top_clusters[2][0]]['name']} ({top_clusters[2][1]}점)
                    </p>
                    <p style="color: #2E7D32; font-weight: 600; font-size: 0.9em;">
                        💡 매칭 정확도: {cluster_result['confidence']:.1%}
                    </p>
                </div>
                """, unsafe_allow_html=True)
    
    # 추천 알고리즘 설명
    st.markdown("---")
    st.markdown('<h3 class="section-title">🤖 AI 추천 알고리즘</h3>', unsafe_allow_html=True)
    
    algo_col1, algo_col2, algo_col3 = st.columns(3)
    
    with algo_col1:
        st.markdown(f"""
        <div class="filter-card" style="text-align: center;">
            <h4 style="color: #2E7D32; margin-bottom: 15px;">🎯 1단계: 성향 분석</h4>
            <p style="color: #2E7D32; font-weight: 600; font-size: 0.9em;">
                8개 질문으로<br>
                8가지 클러스터 중<br>
                최적 성향 결정
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with algo_col2:
        st.markdown(f"""
        <div class="filter-card" style="text-align: center;">
            <h4 style="color: #2E7D32; margin-bottom: 15px;">⚖️ 2단계: 점수 계산</h4>
            <p style="color: #2E7D32; font-weight: 600; font-size: 0.9em;">
                클러스터 선호도 +<br>
                관광지 평점 +<br>
                접근성 보정
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with algo_col3:
        st.markdown(f"""
        <div class="filter-card" style="text-align: center;">
            <h4 style="color: #2E7D32; margin-bottom: 15px;">🏆 3단계: 최종 추천</h4>
            <p style="color: #2E7D32; font-weight: 600; font-size: 0.9em;">
                개인 맞춤형<br>
                우선순위 기반<br>
                상위 추천지 선별
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # 액션 버튼
    st.markdown("---")
    st.markdown("<br>", unsafe_allow_html=True)

    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        if st.button("🗺️ 지도에서 모든 추천지 보기", type="primary"):
            st.session_state.recommended_places = filtered_places
            st.switch_page("pages/05_map_view.py")
    
    with action_col2:
        if st.button("📝 설문 다시하기"):
            st.session_state.survey_completed = False
            st.session_state.answers = {}
            if 'score_breakdown' in st.session_state:
                del st.session_state.score_breakdown
            st.switch_page("pages/01_questionnaire.py")
    
    with action_col3:
        if st.button("📊 통계 분석 보기"):
            st.switch_page("pages/06_statistics.py")

# 메인 실행
if __name__ == "__main__":
    recommendations_page()
else:
    recommendations_page()