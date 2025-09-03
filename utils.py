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

# 12개 요인별 설문 문항 정의
questions = {
    "q1": {
        "title": "1. 여행 계획을 세울 때 어떤 방식을 선호하시나요?",
        "factor": "요인1",  # 계획적 정보 추구형
        "options": [
            "숙박시설을 개별적으로 자세히 비교하여 예약한다",
            "글로벌 포털사이트에서 종합적으로 정보를 수집한다", 
            "맛집 정보를 미리 철저히 조사한다",
            "호텔 위주로 안전하고 편안한 숙소를 선택한다",
            "대충 정해도 현지에서 알아서 해결할 수 있다"
        ],
        "scores": [5, 4, 3, 2, 1]
    },
    "q2": {
        "title": "2. 한국 여행에서 웰니스/힐링의 중요도는 어느 정도인가요?",
        "factor": "요인2",  # 웰니스 중심형
        "options": [
            "웰니스가 여행의 가장 주요한 목적 중 하나다",
            "힐링과 휴식이 여행 전체 만족도에 큰 영향을 준다",
            "스파나 온천 정보를 적극적으로 찾아본다",
            "웰니스 시설이 있으면 좋지만 필수는 아니다",
            "웰니스보다는 다른 활동에 더 관심이 있다"
        ],
        "scores": [5, 4, 3, 2, 1]
    },
    "q3": {
        "title": "3. 한국 여행 경험에 대해 어떻게 생각하시나요?",
        "factor": "요인3",  # 한국 여행 경험축
        "options": [
            "한국은 나에게 완전히 새로운 탐험지다",
            "새로운 국가를 경험하는 것이 가장 흥미롭다",
            "이전 방문 경험을 바탕으로 계획한다",
            "과거 한국 방문 경험이 큰 도움이 된다",
            "경험 여부는 크게 중요하지 않다"
        ],
        "scores": [5, 4, 2, 1, 3]
    },
    "q4": {
        "title": "4. 여행지에서 현지 정보 수집을 어떻게 하시나요?",
        "factor": "요인4",  # 실용적 현지 탐색형
        "options": [
            "방문지의 구체적인 정보를 현지에서 적극 수집한다",
            "현지인들과 소통하여 숨은 명소를 찾는다",
            "관광안내소나 현지 가이드를 적극 활용한다",
            "미리 계획한 장소만 방문하는 편이다",
            "특별한 정보 수집 없이 즉석에서 결정한다"
        ],
        "scores": [5, 4, 3, 2, 1]
    },
    "q5": {
        "title": "5. 여행 중 편의시설과 이동성에 대한 중요도는?",
        "factor": "요인5",  # 편의 인프라 중시형
        "options": [
            "모바일/인터넷 편의성이 매우 중요하다",
            "이동거리가 길면 여행 만족도가 크게 떨어진다",
            "대중교통 편의성을 중시한다",
            "관광지 정보 접근성이 좋아야 한다",
            "다소 불편해도 특별한 경험이 더 중요하다"
        ],
        "scores": [5, 4, 3, 2, 1]
    },
    "q6": {
        "title": "6. 한국의 전통문화와 안전에 대한 관심도는?",
        "factor": "요인6",  # 전통문화 안전 추구형
        "options": [
            "한국 전통 문화를 깊이 체험하고 싶다",
            "치안과 안전이 가장 우선적 고려사항이다",
            "전통과 현대가 조화된 곳을 선호한다",
            "전통문화보다는 현대적인 것에 관심이 많다",
            "안전보다는 모험적 경험을 선호한다"
        ],
        "scores": [5, 4, 3, 2, 1]
    },
    "q7": {
        "title": "7. 자연환경과 산림치유에 대한 관심도는?",
        "factor": "요인7",  # 자연치유형
        "options": [
            "산림욕과 자연치유가 여행의 주요 목적이다",
            "깨끗한 자연환경에서 힐링하고 싶다",
            "국립공원이나 생태공원을 선호한다",
            "자연도 좋지만 도시 관광을 더 선호한다",
            "자연환경에는 별로 관심이 없다"
        ],
        "scores": [5, 4, 3, 2, 1]
    },
    "q8": {
        "title": "8. 숙박 및 서비스 수준에 대한 선호도는?",
        "factor": "요인8",  # 프리미엄 서비스형
        "options": [
            "5성급 호텔이나 프리미엄 리조트를 선호한다",
            "고급 스파나 웰니스 서비스를 중시한다",
            "서비스 품질이 가격보다 중요하다",
            "적당한 수준의 숙박시설로도 만족한다",
            "저예산으로 경제적인 여행을 선호한다"
        ],
        "scores": [5, 4, 3, 2, 1]
    },
    "q9": {
        "title": "9. 여행 동반자와 여행 스타일에 대해 어떻게 생각하시나요?",
        "factor": "요인9",  # 사회적 여행형
        "options": [
            "가족이나 친구와 함께하는 여행을 선호한다",
            "그룹 활동이나 단체 프로그램을 좋아한다",
            "동반자와 함께 추억을 만드는 것이 중요하다",
            "혼자만의 시간도 필요하다",
            "완전히 혼자 여행하는 것을 선호한다"
        ],
        "scores": [5, 4, 3, 2, 1]
    },
    "q10": {
        "title": "10. 디지털 미디어 활용과 정보 수집에 대한 관심도는?",
        "factor": "요인10",  # 디지털 활용형
        "options": [
            "유튜브나 SNS에서 여행정보를 적극 수집한다",
            "온라인 리뷰나 평점을 매우 중시한다",
            "모바일 앱을 통한 예약과 정보 확인을 선호한다",
            "오프라인 정보도 함께 참고한다",
            "디지털보다는 직접 경험을 더 선호한다"
        ],
        "scores": [5, 4, 3, 2, 1]
    },
    "q11": {
        "title": "11. 출입국 절차와 여행 준비에 대한 중요도는?",
        "factor": "요인11",  # 절차 중시형
        "options": [
            "출입국 절차와 비자 등을 매우 세심하게 준비한다",
            "여행 보험이나 안전 대비책을 철저히 마련한다",
            "모든 일정과 예약을 미리 확정한다",
            "기본적인 준비만 하고 유연하게 대응한다",
            "최소한의 준비만 하고 즉흥적으로 여행한다"
        ],
        "scores": [5, 4, 3, 2, 1]
    },
    "q12": {
        "title": "12. 교통수단과 접근성에 대한 선호도는?",
        "factor": "요인12",  # 교통 편의형
        "options": [
            "대중교통을 적극적으로 이용하고 싶다",
            "교통비용보다는 편의성과 시간을 중시한다",
            "숙박 예약 시 교통 접근성을 우선 고려한다",
            "렌터카나 개인 차량 이용을 선호한다",
            "교통편보다는 목적지 자체가 더 중요하다"
        ],
        "scores": [5, 4, 3, 2, 1]
    }
}

# 클러스터 정보 (실제 분석 결과 기반)
def get_cluster_info():
    """12개 요인 기반 8개 클러스터 정보"""
    return {
        1: {
            "name": "네이처 씨커",
            "english_name": "Nature Seeker", 
            "description": "자연과 전통문화를 추구하는 탐험가형. 산림치유와 전통 체험을 통해 깊이 있는 힐링을 추구합니다.",
            "characteristics": ["자연치유 중시", "전통문화 관심", "체험 활동 선호", "깊이 있는 여행"],
            "color": "#2ECC71",
            "percentage": 15.9,
            "count": 413,
            "key_factors": {
                "요인7": 1.2,   # 자연치유 (높음)
                "요인6": 0.8,   # 전통문화
                "요인4": 0.6,   # 현지탐색
                "요인11": 0.5   # 절차중시
            }
        },
        2: {
            "name": "어반 웰니스",
            "english_name": "Urban Wellness",
            "description": "도심형 프리미엄 웰니스를 추구하는 유형. 접근성이 좋은 고급 스파와 힐링 시설을 선호합니다.",
            "characteristics": ["도심 접근성", "프리미엄 서비스", "편의성 중시", "효율적 일정"],
            "color": "#3498DB",
            "percentage": 18.2,
            "count": 472,
            "key_factors": {
                "요인8": 1.1,   # 프리미엄서비스 (높음)
                "요인5": 0.9,   # 편의인프라
                "요인2": 0.8,   # 웰니스중심
                "요인10": 0.7   # 디지털활용
            }
        },
        3: {
            "name": "밸런스드 익스플로러",
            "english_name": "Balanced Explorer",
            "description": "다양한 경험을 균형있게 추구하는 여행자. 문화와 자연, 휴식과 활동을 조화롭게 계획합니다.",
            "characteristics": ["균형잡힌 여행", "다양한 체험", "문화 관심", "적당한 예산"],
            "color": "#E67E22",
            "percentage": 14.3,
            "count": 371,
            "key_factors": {
                "요인4": 0.9,   # 현지탐색
                "요인6": 0.7,   # 전통문화
                "요인3": 0.6,   # 여행경험
                "요인12": 0.5   # 교통편의
            }
        },
        4: {
            "name": "프리미엄 힐러",
            "english_name": "Premium Healer",
            "description": "최고급 웰니스 리조트와 프리미엄 힐링 서비스를 추구하는 럭셔리 여행자입니다.",
            "characteristics": ["럭셔리 리조트", "프리미엄 스파", "완벽한 휴식", "고급 서비스"],
            "color": "#E74C3C",
            "percentage": 11.4,
            "count": 296,
            "key_factors": {
                "요인8": 1.4,   # 프리미엄서비스 (매우높음)
                "요인2": 1.1,   # 웰니스중심
                "요인1": 0.8,   # 계획적정보추구
                "요인5": 0.7    # 편의인프라
            }
        },
        5: {
            "name": "컬처 커넥터",
            "english_name": "Culture Connector",
            "description": "전통문화와 현지 체험에 깊이 관심이 있는 문화 탐구형 여행자입니다.",
            "characteristics": ["전통문화 탐구", "현지 체험", "문화적 몰입", "교육적 여행"],
            "color": "#8E44AD",
            "percentage": 12.7,
            "count": 329,
            "key_factors": {
                "요인6": 1.3,   # 전통문화 (매우높음)
                "요인4": 1.0,   # 현지탐색
                "요인11": 0.6,  # 절차중시
                "요인9": 0.5    # 사회적여행
            }
        },
        6: {
            "name": "스마트 트래블러",
            "english_name": "Smart Traveler",
            "description": "디지털 기술을 적극 활용하여 효율적이고 스마트한 여행을 추구하는 현대적 여행자입니다.",
            "characteristics": ["디지털 활용", "효율적 일정", "정보 중시", "모던 라이프스타일"],
            "color": "#1ABC9C",
            "percentage": 13.6,
            "count": 353,
            "key_factors": {
                "요인10": 1.2,  # 디지털활용 (높음)
                "요인1": 1.0,   # 계획적정보추구
                "요인5": 0.8,   # 편의인프라
                "요인12": 0.6   # 교통편의
            }
        },
        7: {
            "name": "프리덤 씨커",
            "english_name": "Freedom Seeker",
            "description": "자유롭고 즉흥적인 여행을 선호하며, 개인적인 힐링과 자유로운 탐험을 추구합니다.",
            "characteristics": ["자유로운 여행", "즉흥적 계획", "개인적 힐링", "유연한 일정"],
            "color": "#9B59B6",
            "percentage": 8.9,
            "count": 231,
            "key_factors": {
                "요인7": 0.9,   # 자연치유
                "요인9": -0.8,  # 사회적여행 (낮음)
                "요인11": -0.6, # 절차중시 (낮음)
                "요인1": -0.5   # 계획적정보추구 (낮음)
            }
        },
        8: {
            "name": "액티브 웰니스",
            "english_name": "Active Wellness",
            "description": "활동적인 웰니스와 다양한 체험을 통해 에너지를 충전하는 역동적 여행자입니다.",
            "characteristics": ["활동적 힐링", "다양한 액티비티", "에너지 충전", "체험 중심"],
            "color": "#F39C12",
            "percentage": 5.0,
            "count": 130,
            "key_factors": {
                "요인4": 1.1,   # 현지탐색
                "요인7": 0.8,   # 자연치유
                "요인9": 0.7,   # 사회적여행
                "요인12": 0.6   # 교통편의
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

def calculate_factor_scores(answers):
    """설문 답변을 12개 요인 점수로 변환"""
    factor_scores = {}
    
    for i in range(1, 13):
        factor_key = f"요인{i}"
        factor_scores[factor_key] = 0.0
    
    # 각 문항의 답변을 해당 요인 점수로 변환
    for q_key, answer_idx in answers.items():
        if q_key in questions and answer_idx is not None:
            question_data = questions[q_key]
            factor = question_data["factor"]
            score = question_data["scores"][answer_idx]
            
            # 1-5 점수를 -2 ~ +2 범위로 정규화 (요인분석 스케일에 맞춤)
            normalized_score = (score - 3) * 0.8
            factor_scores[factor] = normalized_score
    
    return factor_scores

def determine_cluster_from_factors(factor_scores):
    """12개 요인 점수를 바탕으로 클러스터 결정"""
    cluster_info = get_cluster_info()
    
    # 각 클러스터와의 유사도 계산
    cluster_similarities = {}
    
    for cluster_id, info in cluster_info.items():
        similarity = 0.0
        key_factors = info["key_factors"]
        
        # 주요 요인들과의 유사도 계산
        for factor, target_value in key_factors.items():
            user_value = factor_scores.get(factor, 0.0)
            # 유클리드 거리의 역수로 유사도 계산
            distance = abs(user_value - target_value)
            similarity += 1 / (1 + distance)
        
        # 주요 요인 수로 평균화
        cluster_similarities[cluster_id] = similarity / len(key_factors)
    
    # 가장 유사한 클러스터 선택
    best_cluster = max(cluster_similarities, key=cluster_similarities.get)
    confidence = cluster_similarities[best_cluster] / sum(cluster_similarities.values())
    
    return {
        'cluster': best_cluster,
        'confidence': confidence,
        'similarities': cluster_similarities,
        'factor_scores': factor_scores,
        'score': cluster_similarities[best_cluster] * 20  # 점수화
    }

# 호환성을 위한 별칭 함수
def determine_cluster(answers):
    """설문 답변으로부터 클러스터 결정 (호환성을 위한 래퍼 함수)"""
    factor_scores = calculate_factor_scores(answers)
    return determine_cluster_from_factors(factor_scores)

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
    
    # 클러스터별 선호 관광지 타입 매핑
    cluster_preferences = {
        1: ['산림/자연치유', '체험/교육', '한방/전통의학'],  # 네이처 씨커
        2: ['스파/온천', '웰니스 리조트', '힐링/테라피'],     # 어반 웰니스
        3: ['문화/예술', '체험/교육', '산림/자연치유'],       # 밸런스드 익스플로러
        4: ['웰니스 리조트', '스파/온천', '리조트/호텔'],     # 프리미엄 힐러
        5: ['문화/예술', '체험/교육', '한방/전통의학'],       # 컬처 커넥터
        6: ['스파/온천', '웰니스 리조트', '레저/액티비티'],   # 스마트 트래블러
        7: ['산림/자연치유', '힐링/테라피', '체험/교육'],     # 프리덤 씨커
        8: ['레저/액티비티', '산림/자연치유', '체험/교육']    # 액티브 웰니스
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
        
        # 접근성 보너스 (거리가 가까울수록 높은 점수)
        distance_score = max(0, 20 - (place['distance_from_incheon'] / 50))
        score += distance_score
        
        # 클러스터 신뢰도 반영
        score += cluster_result['confidence'] * 20
        
        # 가격 접근성 (무료나 저렴한 가격 우대)
        if '무료' in str(place['price_range']):
            score += 10
        elif place['price_range'].startswith(('10,000', '20,000', '30,000')):
            score += 5
        
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
        },
        6: {
            "name": "경북 영주/영월 권역",
            "description": "국립공원과 연계된 생태치유 전문지역",
            "recommended_stay": "1박 2일",
            "main_features": ["국립공원", "생태치유", "산림욕"],
            "color": "#1ABC9C"
        },
        7: {
            "name": "강원 홍천/원주 권역",
            "description": "문화예술과 힐링이 조화된 복합 관광지역",
            "recommended_stay": "1박 2일",
            "main_features": ["문화예술", "힐링센터", "복합관광"],
            "color": "#9B59B6"
        },
        8: {
            "name": "강원 평창/정선 권역",
            "description": "스키리조트 연계 사계절 웰니스 리조트",
            "recommended_stay": "1박 2일",
            "main_features": ["스키리조트", "사계절관광", "액티비티"],
            "color": "#F39C12"
        },
        9: {
            "name": "강원 동해안 권역",
            "description": "동해안 자연환경과 온천을 활용한 해안형 웰니스",
            "recommended_stay": "1박 2일",
            "main_features": ["동해안경관", "천연온천", "해안힐링"],
            "color": "#16A085"
        }
    }

def create_factor_analysis_chart(factor_scores):
    """12개 요인 점수 레이더 차트 생성"""
    factor_names = [
        "계획적정보추구", "웰니스중심", "여행경험축", "실용적현지탐색",
        "편의인프라중시", "전통문화안전", "자연치유형", "프리미엄서비스",
        "사회적여행", "디지털활용", "절차중시", "교통편의"
    ]
    
    values = [factor_scores.get(f"요인{i}", 0) for i in range(1, 13)]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=factor_names,
        fill='toself',
        name='나의 요인 점수',
        line_color='#3498DB',
        fillcolor='rgba(52, 152, 219, 0.2)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[-2, 2],
                tickfont=dict(size=10, color='#2C3E50'),
                gridcolor='rgba(52, 152, 219, 0.3)'
            ),
            angularaxis=dict(
                tickfont=dict(size=11, color='#2C3E50'),
                gridcolor='rgba(52, 152, 219, 0.3)'
            )
        ),
        showlegend=True,
        title="12개 요인별 개인 성향 분석",
        font=dict(color='#2C3E50', size=12),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=500
    )
    
    return fig

def create_cluster_comparison_chart(user_cluster, factor_scores):
    """사용자와 클러스터 평균 비교 차트"""
    cluster_info = get_cluster_info()
    cluster_data = cluster_info[user_cluster]
    
    factors = list(range(1, 13))
    user_scores = [factor_scores.get(f"요인{i}", 0) for i in factors]
    cluster_key_factors = cluster_data["key_factors"]
    
    # 클러스터 평균 점수 (주요 요인만 표시, 나머지는 0)
    cluster_scores = []
    for i in factors:
        factor_key = f"요인{i}"
        if factor_key in cluster_key_factors:
            cluster_scores.append(cluster_key_factors[factor_key])
        else:
            cluster_scores.append(0)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=[f"요인{i}" for i in factors],
        y=user_scores,
        name="나의 점수",
        marker_color='#3498DB'
    ))
    
    fig.add_trace(go.Bar(
        x=[f"요인{i}" for i in factors],
        y=cluster_scores,
        name=f"{cluster_data['name']} 평균",
        marker_color=cluster_data['color'],
        opacity=0.7
    ))
    
    fig.update_layout(
        title=f"나 vs {cluster_data['name']} 요인별 비교",
        xaxis_title="12개 요인",
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