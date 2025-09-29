import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

def check_access_permissions(page_type='default'):
    """페이지 접근 권한 확인"""
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.error("⚠️ 로그인 후 이용해주세요.")
        if st.button("🏠 로그인 페이지로 돌아가기", key="access_login_btn"):
            st.switch_page("app.py")
        st.stop()
    
    if page_type not in ['home', 'questionnaire']:
        if 'survey_completed' not in st.session_state or not st.session_state.survey_completed:
            st.warning("⚠️ 설문조사를 먼저 완료해주세요.")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📝 설문조사 하러 가기", key="access_survey_btn"):
                    st.switch_page("pages/01_questionnaire.py")
            with col2:
                if st.button("🏠 홈으로 가기", key="access_home_btn"):
                    st.switch_page("pages/03_home.py")
            st.stop()

# 7개 문항 정의 (기존 12개에서 7개로 축소)
questions = {
    "q1": {
        "title": "1. 한국에 머무를 계획 기간은 얼마나 되나요?",
        "category": "체류 기간",
        "options": [
            "1~6일 (단기 관광)",
            "7~10일 (일반적인 여행)",
            "11~20일 (중장기 여행)", 
            "21일 이상 (장기 체류)"
        ],
        "weights": {
            0: {"cluster_0": 0, "cluster_1": 1, "cluster_2": 2},  # 1~6일
            1: {"cluster_0": 0, "cluster_1": 2, "cluster_2": 0},  # 7~10일
            2: {"cluster_0": 1, "cluster_1": 1, "cluster_2": 0},  # 11~20일
            3: {"cluster_0": 3, "cluster_1": 0, "cluster_2": 0}   # 21일+
        }
    },
    "q2": {
        "title": "2. 1인 1일 예상 지출액은 어느 정도인가요? (USD 기준)",
        "category": "지출 수준",
        "options": [
            "$0~150 (저예산형)",
            "$151~350 (중간 예산형)",
            "$351~700 (고예산형)",
            "$701 이상 (프리미엄형)"
        ],
        "weights": {
            0: {"cluster_0": 3, "cluster_1": 0, "cluster_2": 0},  # $0~150
            1: {"cluster_0": 0, "cluster_1": 2, "cluster_2": 0},  # $151~350
            2: {"cluster_0": 0, "cluster_1": 0, "cluster_2": 1},  # $351~700
            3: {"cluster_0": 0, "cluster_1": 0, "cluster_2": 3}   # $701+
        }
    },
    "q3": {
        "title": "3. 한국 방문은 몇 번째인가요?",
        "category": "방문 경험",
        "options": [
            "처음 방문",
            "2~3번째 방문",
            "4~5번째 방문",
            "6번째 이상 방문"
        ],
        "weights": {
            0: {"cluster_0": 0, "cluster_1": 2, "cluster_2": 0},  # 처음
            1: {"cluster_0": 1, "cluster_1": 2, "cluster_2": 0},  # 2~3번
            2: {"cluster_0": 1, "cluster_1": 0, "cluster_2": 1},  # 4~5번
            3: {"cluster_0": 0, "cluster_1": 0, "cluster_2": 3}   # 6번+
        }
    },
    "q4": {
        "title": "4. 주된 숙박 형태는 무엇에 가장 가깝나요?",
        "category": "숙박 유형",
        "options": [
            "친척이나 친구 집",
            "호텔이나 리조트",
            "게스트하우스나 호스텔",
            "에어비앤비나 콘도미니엄"
        ],
        "weights": {
            0: {"cluster_0": 3, "cluster_1": 0, "cluster_2": 0},  # 친척/친구
            1: {"cluster_0": 0, "cluster_1": 2, "cluster_2": 1},  # 호텔/리조트
            2: {"cluster_0": 1, "cluster_1": 1, "cluster_2": 0},  # 게스트/호스텔
            3: {"cluster_0": 0, "cluster_1": 1, "cluster_2": 1}   # 에어비앤비/콘도
        }
    },
    "q5": {
        "title": "5. 전통문화 체험(한복 입기, 전통 음식 만들기 등)에 대한 관심도는?",
        "category": "문화 체험",
        "options": [
            "매우 높다 - 꼭 체험하고 싶다",
            "어느 정도 있다 - 기회가 되면 해보고 싶다",
            "잘 모르겠다 - 상황에 따라",
            "관심이 낮다 - 별로 중요하지 않다"
        ],
        "weights": {
            0: {"cluster_0": 1, "cluster_1": 2, "cluster_2": 0},  # 매우 높다
            1: {"cluster_0": 1, "cluster_1": 1, "cluster_2": 0},  # 어느 정도
            2: {"cluster_0": 0, "cluster_1": 0, "cluster_2": 0},  # 잘 모름
            3: {"cluster_0": 0, "cluster_1": 0, "cluster_2": 1}   # 낮다
        }
    },
    "q6": {
        "title": "6. 박물관이나 전시관 관람에 대한 의향은?",
        "category": "문화 관람",
        "options": [
            "매우 높다 - 여러 곳을 방문하고 싶다",
            "어느 정도 있다 - 1-2곳 정도는 가보고 싶다",
            "잘 모르겠다 - 시간이 남으면",
            "관심이 낮다 - 굳이 가지 않아도 된다"
        ],
        "weights": {
            0: {"cluster_0": 1, "cluster_1": 2, "cluster_2": 0},  # 매우 높다
            1: {"cluster_0": 1, "cluster_1": 1, "cluster_2": 0},  # 어느 정도
            2: {"cluster_0": 0, "cluster_1": 0, "cluster_2": 0},  # 잘 모름
            3: {"cluster_0": 0, "cluster_1": 0, "cluster_2": 1}   # 낮다
        }
    },
    "q7": {
        "title": "7. 아래 중 가장 본인의 여행 스타일에 가까운 것은?",
        "category": "여행 스타일",
        "options": [
            "오래 머물며 여유있게 지인도 만나고 문화도 천천히 즐긴다",
            "평균적인 일정으로 주요 명소와 체험을 균형있게 본다",
            "짧게 강하게! 쇼핑·미식 등 소비 중심으로 효율적으로 즐긴다"
        ],
        "weights": {
            0: {"cluster_0": 3, "cluster_1": 0, "cluster_2": 0},  # 장기·지인·여유
            1: {"cluster_0": 0, "cluster_1": 3, "cluster_2": 0},  # 평균형·균형
            2: {"cluster_0": 0, "cluster_1": 0, "cluster_2": 3}   # 짧고 강한 소비
        }
    }
}

# 3개 클러스터 정보 (기존 8개에서 3개로 축소)
def get_cluster_info():
    """3개 클러스터 정보"""
    return {
        0: {
            "name": "장기체류 지인방문형",
            "english_name": "Long-stay Social Visitor", 
            "description": "한국에 오래 머물며 지인과의 만남을 중시하고, 저예산으로 문화를 천천히 체험하는 유형입니다.",
            "characteristics": ["장기 체류", "지인 방문", "저예산", "문화 체험"],
            "color": "#2ECC71",
            "percentage": 25.8,
            "count": 669,
            "key_factors": {
                "체류기간": "21일 이상",
                "지출수준": "저예산형",
                "방문경험": "재방문자",
                "숙박형태": "지인집"
            }
        },
        1: {
            "name": "전형적 중간형 관광객",
            "english_name": "Typical Balanced Tourist",
            "description": "일반적인 관광 일정과 예산으로 한국의 주요 명소와 문화를 균형있게 체험하는 대표적인 관광객 유형입니다.",
            "characteristics": ["표준 일정", "균형 예산", "문화 관심", "호텔 선호"],
            "color": "#3498DB",
            "percentage": 52.4,
            "count": 1358,
            "key_factors": {
                "체류기간": "7-10일",
                "지출수준": "중간 예산형",
                "방문경험": "처음 또는 재방문",
                "숙박형태": "호텔/리조트"
            }
        },
        2: {
            "name": "단기 고소비 재방문층",
            "english_name": "Short-stay Premium Repeater",
            "description": "짧은 기간 동안 고예산으로 쇼핑, 미식 등을 집중적으로 즐기는 경험 많은 재방문 고객입니다.",
            "characteristics": ["단기 집중", "고예산", "쇼핑 중심", "효율 추구"],
            "color": "#E74C3C",
            "percentage": 21.8,
            "count": 564,
            "key_factors": {
                "체류기간": "1-6일",
                "지출수준": "고예산형",
                "방문경험": "다수 재방문",
                "숙박형태": "프리미엄 숙소"
            }
        }
    }

@st.cache_data(ttl=3600)
def load_wellness_destinations():
    """실제 CSV 파일에서 웰니스 관광지 데이터 로드"""
    try:
        # CSV 파일 로드
        df = pd.read_csv('region_data.csv')
        
        # 데이터 검증
        required_columns = ['name', 'lat', 'lon', 'type', 'description', 'rating', 
                          'price_range', 'distance_from_incheon', 'cluster']
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"❌ CSV 파일에 필수 컬럼이 누락되었습니다: {missing_columns}")
            return pd.DataFrame()
        
        # 데이터 정리
        df = df.dropna(subset=['name', 'lat', 'lon'])
        
        # 타입별 한국어 카테고리 매핑
        type_mapping = {
            '스파/온천': 'spa_oncheon',
            '산림/자연치유': 'forest_healing', 
            '웰니스 리조트': 'wellness_resort',
            '체험/교육': 'experience_education',
            '리조트/호텔': 'resort_hotel',
            '문화/예술': 'culture_art',
            '힐링/테라피': 'healing_therapy',
            '한방/전통의학': 'traditional_medicine',
            '레저/액티비티': 'leisure_activity',
            '기타': 'others'
        }
        
        # 영어 타입 컬럼 추가
        df['type_en'] = df['type'].map(type_mapping).fillna('others')
        
        return df
        
    except FileNotFoundError:
        st.error("❌ region_data.csv 파일을 찾을 수 없습니다.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ 데이터 로드 중 오류가 발생했습니다: {str(e)}")
        return pd.DataFrame()

def calculate_cluster_scores(answers):
    """설문 답변을 바탕으로 3개 클러스터 점수 계산"""
    cluster_scores = {"cluster_0": 0, "cluster_1": 0, "cluster_2": 0}
    
    # 각 문항의 답변에 따라 클러스터별 점수 누적
    for q_key, answer_idx in answers.items():
        if q_key in questions and answer_idx is not None:
            question_data = questions[q_key]
            weights = question_data["weights"][answer_idx]
            
            for cluster, weight in weights.items():
                cluster_scores[cluster] += weight
    
    return cluster_scores

def determine_cluster(answers):
    """설문 답변으로부터 클러스터 결정 (새로운 3개 클러스터 방식)"""
    cluster_scores = calculate_cluster_scores(answers)
    
    # 최고 점수의 클러스터 선택
    best_cluster_key = max(cluster_scores, key=cluster_scores.get)
    best_cluster_id = int(best_cluster_key.split('_')[1])
    
    # 신뢰도 계산 (최고 점수 / 전체 점수 합)
    total_score = sum(cluster_scores.values())
    confidence = cluster_scores[best_cluster_key] / total_score if total_score > 0 else 0
    
    # 동점 처리 (타이브레이커)
    if list(cluster_scores.values()).count(cluster_scores[best_cluster_key]) > 1:
        # Q1(체류일) 우선순위로 타이브레이커
        q1_answer = answers.get('q1')
        if q1_answer is not None:
            if q1_answer == 3:  # 21일 이상 → cluster_0 우선
                best_cluster_id = 0
            elif q1_answer == 1:  # 7-10일 → cluster_1 우선  
                best_cluster_id = 1
            elif q1_answer == 0:  # 1-6일 → cluster_2 우선
                best_cluster_id = 2
        
        # Q2(지출) 2순위 타이브레이커
        if list(cluster_scores.values()).count(cluster_scores[best_cluster_key]) > 1:
            q2_answer = answers.get('q2')
            if q2_answer is not None:
                if q2_answer == 0:  # 저예산 → cluster_0
                    best_cluster_id = 0
                elif q2_answer == 1:  # 중간예산 → cluster_1
                    best_cluster_id = 1
                elif q2_answer >= 2:  # 고예산 → cluster_2
                    best_cluster_id = 2
    
    return {
        'cluster': best_cluster_id,
        'confidence': confidence,
        'cluster_scores': cluster_scores,
        'score': cluster_scores[f"cluster_{best_cluster_id}"]
    }

def calculate_factor_scores(answers):
    """호환성을 위한 더미 함수 - 3개 클러스터에서는 사용하지 않음"""
    # 3개 주요 차원으로 간소화된 점수 반환
    return {
        "체류기간": answers.get('q1', 0) * 0.5,
        "지출수준": answers.get('q2', 0) * 0.8, 
        "방문경험": answers.get('q3', 0) * 0.6,
        "숙박형태": answers.get('q4', 0) * 0.4,
        "문화관심": (answers.get('q5', 0) + answers.get('q6', 0)) * 0.3,
        "여행스타일": answers.get('q7', 0) * 0.7
    }

def determine_cluster_from_factors(factor_scores):
    """호환성을 위한 래퍼 함수"""
    # factor_scores는 사용하지 않고, 세션의 answers를 직접 사용
    if 'answers' in st.session_state:
        return determine_cluster(st.session_state.answers)
    else:
        return {'cluster': 1, 'confidence': 0.5, 'cluster_scores': {}, 'score': 0}

def classify_wellness_type(answers):
    """웰니스 성향 분류 (호환성을 위한 별칭)"""
    return determine_cluster(answers)

def validate_answers():
    """설문 답변 유효성 검사"""
    errors = set()
    
    for key in questions.keys():
        if key not in st.session_state.answers or st.session_state.answers[key] is None:
            errors.add(key)
    
    st.session_state.validation_errors = errors
    return len(errors) == 0

def reset_survey_state():
    """설문 관련 세션 상태 초기화"""
    reset_keys = [
        'answers', 'survey_completed', 'validation_errors', 
        'factor_scores', 'cluster_result', 'total_score',
        'recommendation_results', 'show_results'
    ]
    
    for key in reset_keys:
        if key in st.session_state:
            del st.session_state[key]

@st.cache_data(ttl=1800)
def calculate_recommendations_by_cluster(cluster_result):
    """클러스터 기반 실제 웰니스 관광지 추천 계산"""
    wellness_df = load_wellness_destinations()
    
    if wellness_df.empty:
        return []
    
    user_cluster = cluster_result['cluster']
    cluster_info = get_cluster_info()
    
    recommendations = []
    
    # 클러스터별 선호 관광지 타입 매핑 (3개 클러스터 기준)
    cluster_preferences = {
        0: ['한방/전통의학', '문화/예술', '체험/교육'],           # 장기체류 지인방문형
        1: ['스파/온천', '산림/자연치유', '웰니스 리조트'],      # 전형적 중간형 관광객  
        2: ['웰니스 리조트', '스파/온천', '리조트/호텔']        # 단기 고소비 재방문층
    }
    
    preferred_types = cluster_preferences.get(user_cluster, ['스파/온천'])
    
    # 각 관광지에 대해 추천 점수 계산
    for idx, place in wellness_df.iterrows():
        score = 0
        
        # 기본 평점 반영 (0-10점을 0-40점으로 스케일)
        score += place['rating'] * 4
        
        # 클러스터 선호 타입 보너스
        if place['type'] in preferred_types:
            type_bonus = (3 - preferred_types.index(place['type'])) * 15
            score += type_bonus
        
        # 클러스터별 특별 가중치
        if user_cluster == 0:  # 장기체류 지인방문형
            # 접근성과 가격 중시
            if '무료' in str(place['price_range']) or place['price_range'].startswith(('10,000', '20,000')):
                score += 15
            if place['distance_from_incheon'] <= 100:  # 가까운 거리 선호
                score += 10
                
        elif user_cluster == 1:  # 전형적 중간형 관광객
            # 평점과 균형 중시
            score += place['rating'] * 2  # 평점 가중치 추가
            if 50000 <= int(''.join(filter(str.isdigit, place['price_range'].split('-')[0]))) <= 200000:
                score += 10  # 중간 가격대 선호
                
        elif user_cluster == 2:  # 단기 고소비 재방문층
            # 프리미엄과 효율성 중시
            if any(keyword in place['price_range'] for keyword in ['500,000', '1,000,000']):
                score += 20  # 고가격대 선호
            if place['rating'] >= 8.0:  # 고평점 선호
                score += 15
        
        # 접근성 보너스 (거리가 가까울수록 높은 점수)
        distance_score = max(0, 15 - (place['distance_from_incheon'] / 50))
        score += distance_score
        
        # 클러스터 신뢰도 반영
        score += cluster_result['confidence'] * 20
        
        # 결과 생성
        place_recommendation = {
            'name': place['name'],
            'lat': place['lat'],
            'lon': place['lon'],
            'type': place['type'],
            'description': place['description'],
            'rating': place['rating'],
            'price_range': place['price_range'],
            'distance_from_incheon': place['distance_from_incheon'],
            'travel_time_car': place.get('travel_time_primary', '정보 없음'),
            'travel_time_train': place.get('travel_time_secondary', '정보 없음'),
            'travel_cost_car': place.get('travel_cost_primary', '정보 없음'),
            'travel_cost_train': place.get('travel_cost_secondary', '정보 없음'),
            'image_url': place.get('image_url', '🌿'),
            'recommendation_score': score,
            'cluster_match': place['type'] in preferred_types,
            'website': place.get('website', ''),
            'sources': place.get('sources', ''),
            'cluster_region': place.get('cluster', 1)
        }
        
        recommendations.append(place_recommendation)
    
    # 점수 순으로 정렬
    recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)
    
    return recommendations

def get_cluster_region_info():
    """클러스터별 지역 정보 반환"""
    return {
        1: {
            "name": "경상북도 김천/거창 권역",
            "description": "산림치유와 전통 체험이 결합된 내륙 산간지역",
            "recommended_stay": "1박 2일",
            "main_features": ["산림치유", "전통체험", "자연환경"],
            "color": "#2ECC71"
        },
        2: {
            "name": "서울/경기/인천 수도권",
            "description": "접근성이 우수한 도심형 웰니스 시설 집중",
            "recommended_stay": "당일 또는 1박",
            "main_features": ["도심접근성", "프리미엄스파", "편의시설"],
            "color": "#3498DB"
        },
        3: {
            "name": "대구/경북 동남부 권역",
            "description": "도시형 문화시설과 자연치유 시설 혼재",
            "recommended_stay": "1박 2일",
            "main_features": ["문화시설", "도시관광", "자연치유"],
            "color": "#E67E22"
        },
        4: {
            "name": "제주도 권역",
            "description": "제주 특유의 자연환경을 활용한 프리미엄 웰니스 리조트",
            "recommended_stay": "2박 3일",
            "main_features": ["프리미엄리조트", "제주자연", "특별한경험"],
            "color": "#E74C3C"
        }
    }

def create_factor_analysis_chart(factor_scores):
    """간소화된 요인 점수 차트 생성 (3개 클러스터용)"""
    factor_names = list(factor_scores.keys())
    values = list(factor_scores.values())
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=factor_names,
        fill='toself',
        name='나의 여행 성향',
        line_color='#3498DB',
        fillcolor='rgba(52, 152, 219, 0.2)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(values) + 1],
                tickfont=dict(size=10, color='#2C3E50'),
                gridcolor='rgba(52, 152, 219, 0.3)'
            ),
            angularaxis=dict(
                tickfont=dict(size=11, color='#2C3E50'),
                gridcolor='rgba(52, 152, 219, 0.3)'
            )
        ),
        showlegend=True,
        title="여행 성향 분석",
        font=dict(color='#2C3E50', size=12),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=500
    )
    
    return fig

def create_cluster_comparison_chart(user_cluster, factor_scores):
    """사용자와 클러스터 평균 비교 차트 (3개 클러스터용)"""
    cluster_info = get_cluster_info()
    cluster_data = cluster_info[user_cluster]
    
    # 간소화된 비교 차트
    categories = ['체류기간', '지출수준', '방문경험', '문화관심']
    user_scores = [factor_scores.get(cat, 0) for cat in categories]
    
    # 클러스터 평균 점수 (임의 설정)
    cluster_averages = {
        0: [3, 1, 2, 2],  # 장기체류형: 긴 체류, 낮은 지출, 중간 경험, 문화관심
        1: [2, 2, 1, 3],  # 중간형: 중간 체류, 중간 지출, 낮은 경험, 높은 문화관심
        2: [1, 3, 3, 1]   # 고소비형: 짧은 체류, 높은 지출, 높은 경험, 낮은 문화관심
    }
    
    cluster_scores = cluster_averages.get(user_cluster, [2, 2, 2, 2])
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=categories,
        y=user_scores,
        name="나의 점수",
        marker_color='#3498DB'
    ))
    
    fig.add_trace(go.Bar(
        x=categories,
        y=cluster_scores,
        name=f"{cluster_data['name']} 평균",
        marker_color=cluster_data['color'],
        opacity=0.7
    ))
    
    fig.update_layout(
        title=f"나 vs {cluster_data['name']} 비교",
        xaxis_title="평가 항목",
        yaxis_title="점수",
        barmode='group',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#2C3E50',
        height=400
    )
    
    return fig

def show_footer():
    """푸터 표시"""
    st.markdown("---")
    st.markdown("💡 **주의사항**: 본 진단 결과는 참고용이며, 실제 여행 계획 시에는 개인의 선호도를 종합적으로 고려하시기 바랍니다.")

def apply_global_styles():
    """밝은 테마 전역 CSS 스타일 적용"""
    st.markdown("""
    <style>
        /* 전역 스타일 변수 - 밝은 테마 */
        :root {
            --primary: #3498DB;
            --primary-dark: #2980B9;
            --primary-light: #5DADE2;
            --secondary: #2ECC71;
            --accent: #E74C3C;
            --background: #F8F9FA;
            --card-bg: rgba(255, 255, 255, 0.95);
            --text-primary: #2C3E50;
            --text-secondary: #34495E;
            --border-color: rgba(52, 152, 219, 0.2);
            --shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            --shadow-hover: 0 8px 25px rgba(52, 152, 219, 0.15);
        }
        
        /* 기본 배경 - 밝은 그라데이션 */
        .stApp {
            background: linear-gradient(135deg, #F8F9FA 0%, #E8F4FD 50%, #D6EAF8 100%);
            min-height: 100vh;
        }
        
        [data-testid="stAppViewContainer"] > .main {
            background: transparent;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        
        /* 메인 컨테이너 */
        .main .block-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem 1.5rem !important;
        }
        
        /* 카드 공통 스타일 - 깔끔한 밝은 디자인 */
        .card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
            margin: 16px 0;
            box-shadow: var(--shadow);
            transition: all 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-hover);
            border-color: var(--primary);
        }
        
        /* 버튼 스타일 - 모던하고 깔끔한 디자인 */
        div[data-testid="stButton"] > button {
            background: linear-gradient(135deg, var(--primary), var(--primary-light)) !important;
            border: none !important;
            border-radius: 12px !important;
            color: white !important;
            font-weight: 600 !important;
            padding: 12px 24px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 2px 8px rgba(52, 152, 219, 0.2) !important;
            font-size: 14px !important;
            letter-spacing: 0.5px !important;
        }
        
        div[data-testid="stButton"] > button:hover {
            background: linear-gradient(135deg, var(--primary-dark), var(--primary)) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 16px rgba(52, 152, 219, 0.3) !important;
        }
        
        /* 텍스트 스타일 */
        .main h1, .main h2, .main h3 {
            color: var(--text-primary) !important;
            font-weight: 700 !important;
        }
        
        .main p, .main span, .main div {
            color: var(--text-secondary) !important;
        }
        
        /* 입력 필드 스타일 */
        div[data-testid="stTextInput"] > div > div > input,
        div[data-testid="stSelectbox"] > div > div > div {
            border: 2px solid var(--border-color) !important;
            border-radius: 8px !important;
            padding: 12px !important;
            background: white !important;
            color: var(--text-primary) !important;
            font-size: 14px !important;
        }
        
        div[data-testid="stTextInput"] > div > div > input:focus,
        div[data-testid="stSelectbox"] > div > div > div:focus {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1) !important;
        }
        
        /* 라디오 버튼 스타일 개선 */
        div[data-testid="stRadio"] > div {
            gap: 12px !important;
        }
        
        div[data-testid="stRadio"] label {
            background: white !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 12px !important;
            padding: 16px 20px !important;
            margin: 0 !important;
            transition: all 0.3s ease !important;
            cursor: pointer !important;
            min-height: 60px !important;
            display: flex !important;
            align-items: center !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
        }
        
        div[data-testid="stRadio"] label:hover {
            transform: translateY(-1px) !important;
            border-color: var(--primary) !important;
            box-shadow: 0 4px 16px rgba(52, 152, 219, 0.15) !important;
        }
        
        div[data-testid="stRadio"] input:checked + div {
            background: rgba(52, 152, 219, 0.05) !important;
            border-color: var(--primary) !important;
            box-shadow: 0 4px 16px rgba(52, 152, 219, 0.2) !important;
            transform: translateY(-1px) !important;
        }
        
        /* 알림 메시지 스타일 */
        div[data-testid="stAlert"] {
            border-radius: 12px !important;
            border: none !important;
            box-shadow: var(--shadow) !important;
            margin: 16px 0 !important;
        }
        
        .stSuccess {
            background: rgba(46, 204, 113, 0.1) !important;
            color: #27AE60 !important;
        }
        
        .stError {
            background: rgba(231, 76, 60, 0.1) !important;
            color: #E74C3C !important;
        }
        
        .stWarning {
            background: rgba(243, 156, 18, 0.1) !important;
            color: #F39C12 !important;
        }
        
        .stInfo {
            background: rgba(52, 152, 219, 0.1) !important;
            color: var(--primary) !important;
        }
        
        /* 진행률 바 스타일 */
        div[data-testid="stProgress"] > div > div {
            background: linear-gradient(90deg, var(--primary), var(--secondary)) !important;
            border-radius: 8px !important;
            height: 12px !important;
        }
        
        div[data-testid="stProgress"] > div {
            background: rgba(52, 152, 219, 0.1) !important;
            border-radius: 8px !important;
            height: 12px !important;
        }
        
        /* Streamlit UI 요소 숨기기 */
        [data-testid="stHeader"] { display: none; }
        [data-testid="stSidebarNav"] { display: none; }
        [data-testid="stSidebar"] { display: none; }
        footer { display: none; }
        
        /* 반응형 디자인 */
        @media (max-width: 768px) {
            .main .block-container {
                padding: 1rem !important;
            }
            
            .card {
                margin: 12px 0;
                padding: 16px;
            }
        }
    </style>
    """, unsafe_allow_html=True)

def export_recommendations_to_csv(recommendations, user_info=None):
    """추천 결과를 CSV로 내보내기"""
    if not recommendations:
        return None
        
    # DataFrame 생성
    export_data = []
    for i, place in enumerate(recommendations, 1):
        export_data.append({
            '순위': i,
            '관광지명': place['name'],
            '유형': place['type'],
            '평점': place['rating'],
            '추천점수': f"{place['recommendation_score']:.1f}",
            '가격대': place['price_range'],
            '거리(km)': place['distance_from_incheon'],
            '자차시간': place['travel_time_car'],
            '대중교통시간': place['travel_time_train'],
            '자차비용': place['travel_cost_car'],
            '대중교통비용': place['travel_cost_train'],
            '설명': place['description'][:100] + '...' if len(place['description']) > 100 else place['description'],
            '웹사이트': place.get('website', ''),
            '클러스터매칭': '✅' if place['cluster_match'] else '❌'
        })
    
    df = pd.DataFrame(export_data)
    
    # CSV 바이트 문자열로 변환
    csv = df.to_csv(index=False, encoding='utf-8-sig')
    
    return csv.encode('utf-8-sig')

def get_statistics_summary():
    """시스템 통계 요약 정보"""
    wellness_df = load_wellness_destinations()
    
    if wellness_df.empty:
        return {}
    
    stats = {
        'total_destinations': len(wellness_df),
        'total_types': wellness_df['type'].nunique(),
        'total_clusters': wellness_df['cluster'].nunique(),
        'avg_rating': wellness_df['rating'].mean(),
        'avg_distance': wellness_df['distance_from_incheon'].mean(),
        'type_distribution': wellness_df['type'].value_counts().to_dict(),
        'cluster_distribution': wellness_df['cluster'].value_counts().to_dict(),
        'rating_stats': {
            'min': wellness_df['rating'].min(),
            'max': wellness_df['rating'].max(),
            'std': wellness_df['rating'].std()
        }
    }
    
    return stats