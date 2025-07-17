import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import plotly.express as px
import plotly.graph_objects as go


def check_access_permissions(page_type='default'):
    """페이지 접근 권한 확인
    
    Args:
        page_type (str): 페이지 유형
            - 'home': 홈페이지 (설문 완료 확인 안함)
            - 'questionnaire': 설문 페이지 (설문 완료 확인 안함)
            - 'default': 기본값 (로그인 + 설문 완료 둘 다 확인)
    """
    import streamlit as st
    
    # 로그인 확인
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.error("⚠️ 로그인 후 이용해주세요.")
        st.page_link("app.py", label="로그인 페이지로 돌아가기", icon="🏠")
        st.stop()
    
    # 설문 완료 확인 (홈페이지와 설문 페이지는 제외)
    if page_type not in ['home', 'questionnaire']:
        if 'survey_completed' not in st.session_state or not st.session_state.survey_completed:
            st.warning("⚠️ 설문조사를 먼저 완료해주세요.")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📝 설문조사 하러 가기"):
                    st.switch_page("pages/01_questionnaire.py")
            with col2:
                if st.button("🏠 홈으로 가기"):
                    st.switch_page("pages/03_home.py")
            st.stop()

# --- 웰니스 관광 성향 진단 설문 관련 함수 및 데이터 (수정됨) ---
questions = {
    "q1": {
        "title": "1. 여행 시 가장 중요하게 생각하는 것은?",
        "options": [
            "안전하고 치안이 좋은 곳 (안전 지향)",
            "새로운 경험과 모험 (모험 추구)", 
            "편리하고 쾌적한 시설 (편의 중시)",
            "비용 대비 효율성 (경제성 중시)"
        ]
    },
    "q2": {
        "title": "2. 선호하는 여행 스타일은? (복수 선택 가능)",
        "options": [
            "혼자서 자유롭게 (개인형)",
            "가족이나 친구와 함께 (사회형)",
            "소규모 그룹으로 (소그룹형)", 
            "대규모 단체로 (단체형)"
        ],
        "multiple": True  # 복수 선택 표시
    },
    "q3": {
        "title": "3. 한국 여행에서 가장 하고 싶은 활동은?",
        "options": [
            "쇼핑 (명동, 강남 등)",
            "문화체험 (고궁, 한옥마을 등)",
            "미식탐방 (전통음식, 맛집 등)",
            "자연관광 (제주도, 설악산 등)"
        ]
    },
    "q4": {
        "title": "4. 숙박시설 선택 기준은?",
        "options": [
            "최고급 호텔 (프리미엄)",
            "깨끗하고 편리한 호텔 (스탠다드)",
            "현지 특색있는 숙소 (게스트하우스 등)",
            "가성비 좋은 숙소 (경제형)"
        ]
    },
    "q5": {
        "title": "5. 여행 정보는 주로 어디서 얻나요?",
        "options": [
            "소셜미디어 (인스타그램, 페이스북 등)",
            "검색엔진 (구글, 네이버 등)",
            "여행 전문 사이트/앱",
            "지인 추천이나 여행 가이드북"
        ]
    },
    "q6": {
        "title": "6. 쇼핑할 때 주로 구매하는 것은?",
        "options": [
            "화장품, 뷰티용품",
            "의류, 패션아이템",
            "전통 기념품, 특산품",
            "전자제품, 브랜드 제품"
        ]
    },
    "q7": {
        "title": "7. 여행 예산 중 가장 많이 투자하고 싶은 분야는?",
        "options": [
            "숙박 (좋은 호텔)",
            "쇼핑 (기념품, 선물)",
            "음식 (고급 레스토랑, 특별한 음식)",
            "체험활동 (문화체험, 투어)"
        ]
    },
    "q8": {
        "title": "8. 여행 후 가장 중요하게 생각하는 것은?",
        "options": [
            "안전하게 다녀왔다는 안도감",
            "새로운 경험에 대한 만족감",
            "쇼핑이나 구매에 대한 만족",
            "문화적 학습과 성장",
            "일상에서 벗어난 충분한 휴식"  # 새로 추가된 휴식 관련 옵션
        ]
    }
}

# 클러스터별 점수 계산 함수들 (수정됨)
def calculate_cluster_0_score(answers):
    """클러스터 0: 안전추구 모험가형"""
    score = 0
    
    # Q1: 안전 중시
    if answers.get('q1') == 0: score += 3  # 안전 지향
    elif answers.get('q1') == 1: score += 2  # 모험 추구
    
    # Q2: 사회적 여행 (복수응답 처리)
    q2_answers = answers.get('q2', [])
    if isinstance(q2_answers, list):
        if 1 in q2_answers: score += 2  # 가족이나 친구와
        if 2 in q2_answers: score += 1  # 소그룹
    
    # Q3: 다양한 활동
    if answers.get('q3') == 0: score += 1  # 쇼핑
    
    # Q4: 호텔 선호
    if answers.get('q4') == 1: score += 2  # 스탠다드 호텔
    elif answers.get('q4') == 0: score += 1  # 프리미엄 호텔
    
    # Q8: 안전 중시 (새 옵션 반영)
    if answers.get('q8') == 0: score += 3  # 안전감
    elif answers.get('q8') == 1: score += 1  # 새로운 경험
    elif answers.get('q8') == 4: score += 1  # 휴식 (중립적 처리)
    
    return score

def calculate_cluster_1_score(answers):
    """클러스터 1: 안전우선 편의형"""
    score = 0
    
    # Q1: 안전 최우선
    if answers.get('q1') == 0: score += 4  # 안전 지향
    elif answers.get('q1') == 2: score += 2  # 편의 중시
    
    # Q2: 사회적 여행 (복수응답 처리)
    q2_answers = answers.get('q2', [])
    if isinstance(q2_answers, list):
        if 1 in q2_answers: score += 2  # 가족이나 친구와
    
    # Q4: 편리한 호텔
    if answers.get('q4') == 1: score += 3  # 스탠다드 호텔
    elif answers.get('q4') == 0: score += 2  # 프리미엄 호텔
    
    # Q7: 숙박 투자
    if answers.get('q7') == 0: score += 2  # 숙박
    
    # Q8: 안전감과 휴식
    if answers.get('q8') == 0: score += 3  # 안전감
    elif answers.get('q8') == 4: score += 2  # 휴식 (편의형에 적합)
    
    return score

def calculate_cluster_2_score(answers):
    """클러스터 2: 문화체험 힐링형"""
    score = 0
    
    # Q3: 문화체험
    if answers.get('q3') == 1: score += 4  # 문화체험
    elif answers.get('q3') == 3: score += 2  # 자연관광
    
    # Q4: 호텔 선호
    if answers.get('q4') == 1: score += 2  # 스탠다드 호텔
    
    # Q7: 체험활동 투자
    if answers.get('q7') == 3: score += 3  # 체험활동
    
    # Q8: 문화적 성장과 휴식
    if answers.get('q8') == 3: score += 3  # 문화적 학습과 성장
    elif answers.get('q8') == 1: score += 1  # 새로운 경험
    elif answers.get('q8') == 4: score += 2  # 휴식 (힐링형에 적합)
    
    return score

def calculate_cluster_3_score(answers):
    """클러스터 3: 쇼핑마니아 사교형"""
    score = 0
    
    # Q2: 사회적 여행 (복수응답 처리)
    q2_answers = answers.get('q2', [])
    if isinstance(q2_answers, list):
        if 1 in q2_answers: score += 3  # 가족이나 친구와
        if 2 in q2_answers: score += 2  # 소그룹
    
    # Q3: 쇼핑 중심
    if answers.get('q3') == 0: score += 4  # 쇼핑
    
    # Q6: 의류/패션
    if answers.get('q6') == 1: score += 3  # 의류, 패션아이템
    elif answers.get('q6') == 0: score += 2  # 화장품, 뷰티용품
    
    # Q7: 쇼핑 투자
    if answers.get('q7') == 1: score += 4  # 쇼핑
    
    # Q8: 쇼핑 만족
    if answers.get('q8') == 2: score += 3  # 쇼핑이나 구매에 대한 만족
    elif answers.get('q8') == 4: score += 1  # 휴식 (중립적 처리)
    
    return score

def calculate_cluster_4_score(answers):
    """클러스터 4: 프리미엄 모험형"""
    score = 0
    
    # Q1: 모험 추구
    if answers.get('q1') == 1: score += 3  # 모험 추구
    elif answers.get('q1') == 2: score += 2  # 편의 중시
    
    # Q4: 최고급 호텔
    if answers.get('q4') == 0: score += 4  # 프리미엄 호텔
    elif answers.get('q4') == 1: score += 2  # 스탠다드 호텔
    
    # Q5: 검색엔진 활용
    if answers.get('q5') == 1: score += 2  # 검색엔진
    
    # Q7: 숙박 투자
    if answers.get('q7') == 0: score += 3  # 숙박
    
    # Q8: 새로운 경험
    if answers.get('q8') == 1: score += 3  # 새로운 경험에 대한 만족감
    elif answers.get('q8') == 4: score += 1  # 휴식 (중립적 처리)
    
    return score

def calculate_cluster_5_score(answers):
    """클러스터 5: 탐험형 문화애호가"""
    score = 0
    
    # Q1: 모험 추구
    if answers.get('q1') == 1: score += 3  # 모험 추구
    
    # Q2: 사회적 여행 (복수응답 처리)
    q2_answers = answers.get('q2', [])
    if isinstance(q2_answers, list):
        if 1 in q2_answers: score += 2  # 가족이나 친구와
    
    # Q3: 문화체험
    if answers.get('q3') == 1: score += 3  # 문화체험
    elif answers.get('q3') == 3: score += 2  # 자연관광
    
    # Q4: 호텔 선호
    if answers.get('q4') == 1: score += 2  # 스탠다드 호텔
    
    # Q8: 새로운 경험과 성장
    if answers.get('q8') == 1: score += 2  # 새로운 경험
    elif answers.get('q8') == 3: score += 2  # 문화적 학습과 성장
    elif answers.get('q8') == 4: score += 1  # 휴식 (중립적 처리)
    
    return score

def calculate_cluster_6_score(answers):
    """클러스터 6: 문화미식 여성형"""
    score = 0
    
    # Q3: 문화체험과 미식
    if answers.get('q3') == 1: score += 3  # 문화체험
    elif answers.get('q3') == 2: score += 3  # 미식탐방
    
    # Q6: 화장품/뷰티
    if answers.get('q6') == 0: score += 3  # 화장품, 뷰티용품
    elif answers.get('q6') == 1: score += 2  # 의류, 패션아이템
    
    # Q7: 음식과 체험
    if answers.get('q7') == 2: score += 2  # 음식
    elif answers.get('q7') == 3: score += 2  # 체험활동
    
    # Q8: 문화적 성장과 휴식
    if answers.get('q8') == 3: score += 2  # 문화적 학습과 성장
    elif answers.get('q8') == 4: score += 2  # 휴식 (여성형에 적합)
    
    return score

def calculate_cluster_7_score(answers):
    """클러스터 7: 종합체험 활동형"""
    score = 0
    
    # Q1: 안전 고려
    if answers.get('q1') == 0: score += 2  # 안전 지향
    
    # Q2: 사회적 여행 (복수응답 처리)
    q2_answers = answers.get('q2', [])
    if isinstance(q2_answers, list):
        if 1 in q2_answers: score += 2  # 가족이나 친구와
    
    # Q3: 문화체험과 미식
    if answers.get('q3') == 1: score += 3  # 문화체험
    elif answers.get('q3') == 2: score += 3  # 미식탐방
    elif answers.get('q3') == 0: score += 2  # 쇼핑
    
    # Q7: 다양한 투자
    if answers.get('q7') == 2: score += 2  # 음식
    elif answers.get('q7') == 3: score += 2  # 체험활동
    
    # Q8: 종합 만족과 휴식
    if answers.get('q8') == 3: score += 2  # 문화적 학습과 성장
    elif answers.get('q8') == 1: score += 1  # 새로운 경험
    elif answers.get('q8') == 4: score += 2  # 휴식 (종합형에 적합)
    
    return score

def determine_cluster(answers):
    """설문 응답을 바탕으로 해당하는 클러스터를 결정"""
    
    cluster_scores = {
        0: calculate_cluster_0_score(answers),
        1: calculate_cluster_1_score(answers),
        2: calculate_cluster_2_score(answers),
        3: calculate_cluster_3_score(answers),
        4: calculate_cluster_4_score(answers),
        5: calculate_cluster_5_score(answers),
        6: calculate_cluster_6_score(answers),
        7: calculate_cluster_7_score(answers)
    }
    
    # 가장 높은 점수의 클러스터 반환
    best_cluster = max(cluster_scores, key=cluster_scores.get)
    best_score = cluster_scores[best_cluster]
    
    # 동점 처리 (상위 2개 클러스터가 비슷한 경우)
    sorted_clusters = sorted(cluster_scores.items(), 
                           key=lambda x: x[1], reverse=True)
    
    if len(sorted_clusters) > 1 and sorted_clusters[0][1] == sorted_clusters[1][1]:
        # 동점인 경우 추가 규칙 적용
        return resolve_tie(answers, sorted_clusters[0][0], sorted_clusters[1][0])
    
    return {
        'cluster': best_cluster,
        'score': best_score,
        'confidence': best_score / max(sum(cluster_scores.values()), 1),
        'all_scores': cluster_scores
    }

def resolve_tie(answers, cluster1, cluster2):
    """동점 시 추가 규칙으로 결정"""
    
    # 안전 vs 모험 성향으로 구분
    if answers.get('q1') == 0:  # 안전 중시
        return cluster1 if cluster1 in [0, 1, 7] else cluster2
    elif answers.get('q1') == 1:  # 모험 추구
        return cluster1 if cluster1 in [0, 4, 5] else cluster2
    
    # 쇼핑 성향으로 구분
    if answers.get('q3') == 0:  # 쇼핑 중심
        return cluster1 if cluster1 == 3 else cluster2
    
    # 기본값
    return cluster1

def calculate_wellness_score(answers):
    """웰니스 관광 성향 점수 계산 (클러스터 기반)"""
    cluster_result = determine_cluster(answers)
    
    # 클러스터 점수를 웰니스 점수로 변환 (0-100 스케일)
    cluster_score = cluster_result['score']
    max_possible_score = 20  # 각 클러스터의 최대 가능 점수
    
    wellness_score = min(100, (cluster_score / max_possible_score) * 100)
    
    score_breakdown = {
        'cluster_id': cluster_result['cluster'],
        'cluster_score': cluster_score,
        'confidence': cluster_result['confidence'],
        'all_cluster_scores': cluster_result['all_scores']
    }
    
    return wellness_score, score_breakdown

def classify_wellness_type(score, cluster_id=None):
    """웰니스 관광 성향 분류 (클러스터 기반)"""
    
    cluster_types = {
        0: ("안전추구 모험가형", "#4CAF50"),
        1: ("안전우선 편의형", "#8BC34A"), 
        2: ("문화체험 힐링형", "#FFC107"),
        3: ("쇼핑마니아 사교형", "#FF9800"),
        4: ("프리미엄 모험형", "#F44336"),
        5: ("탐험형 문화애호가", "#9C27B0"),
        6: ("문화미식 여성형", "#E91E63"),
        7: ("종합체험 활동형", "#2196F3")
    }
    
    if cluster_id is not None and cluster_id in cluster_types:
        return cluster_types[cluster_id]
    
    # 기존 점수 기반 분류 (호환성 유지)
    if score <= 30:
        return "안전우선 편의형", "#4CAF50"
    elif score <= 50:
        return "문화체험 힐링형", "#8BC34A"
    elif score <= 70:
        return "종합체험 활동형", "#FFC107"
    elif score <= 85:
        return "쇼핑마니아 사교형", "#FF9800"
    else:
        return "프리미엄 모험형", "#F44336"

def validate_wellness_answers():
    """설문 답변 유효성 검사 (복수응답 지원)"""
    errors = set()
    
    for key, question_data in questions.items():
        if key not in st.session_state.answers or st.session_state.answers[key] is None:
            errors.add(key)
        elif question_data.get('multiple', False):  # 복수응답 문항 체크
            # 복수응답 문항은 빈 리스트가 아닌지 확인
            if st.session_state.answers[key] == []:
                errors.add(key)
    
    st.session_state.validation_errors = errors
    return len(errors) == 0

def show_footer():
    """푸터 표시"""
    st.markdown("---")
    st.markdown("💡 **주의사항**: 본 진단 결과는 참고용이며, 실제 여행 계획 시에는 개인의 건강 상태와 선호도를 종합적으로 고려하시기 바랍니다.")

# --- 웰니스 관광 성향 세션 상태 초기화 함수 ---
def reset_wellness_survey_state():
    """웰니스 설문 관련 세션 상태 초기화"""
    reset_keys = [
        'answers', 'survey_completed', 'validation_errors', 
        'wellness_type', 'total_score', 'score_breakdown',
        'recommendation_results', 'show_results', 
        'selected_destinations', 'user_preferences',
        'clustering_results', 'pca_results',
        'survey_results',
        'category_filter', 'distance_filter',
        'recommended_places', 'selected_place'
    ]
    
    for key in reset_keys:
        if key in st.session_state:
            del st.session_state[key]
    
    st.session_state.reset_survey_flag = False

# --- 웰니스 관광 데이터 로딩 및 추천 함수 ---

@st.cache_data(ttl=3600)
def load_wellness_destinations_data(file_path='wellness_destinations.csv'):
    """
    웰니스 관광지 데이터를 로드하고 전처리합니다.
    데이터에는 다음 컬럼들이 포함되어야 합니다:
    - destination_name: 관광지명
    - country: 국가
    - region: 지역
    - wellness_type: 웰니스 유형 (스파, 요가, 자연힐링 등)
    - price_range: 가격대 (1-5 등급)
    - duration_days: 권장 여행 기간
    - rating: 평점
    - activities: 주요 활동 (콤마로 구분)
    - description: 설명
    """
    try:
        # 실제 파일이 없는 경우 샘플 데이터 생성
        df = create_sample_wellness_data()
        
    except FileNotFoundError:
        st.warning(f"⚠️ 데이터 파일 '{file_path}'을(를) 찾을 수 없어 샘플 데이터를 사용합니다.")
        df = create_sample_wellness_data()
    except Exception as e:
        st.error(f"⚠️ 데이터 로드 중 오류 발생: {e}")
        df = create_sample_wellness_data()

    return df

def create_sample_wellness_data():
    """샘플 웰니스 관광 데이터 생성"""
    np.random.seed(42)
    
    destinations = [
        # 한국 웰니스 관광지
        {"destination_name": "제주 스파랜드", "country": "한국", "region": "제주", 
         "wellness_type": "스파/온천", "price_range": 3, "duration_days": 3,
         "rating": 4.5, "activities": "온천,스파,마사지", "description": "제주의 자연 온천을 활용한 힐링 스파"},
        
        {"destination_name": "지리산 템플스테이", "country": "한국", "region": "전라남도", 
         "wellness_type": "명상/영성", "price_range": 2, "duration_days": 2,
         "rating": 4.3, "activities": "명상,사찰체험,자연트레킹", "description": "지리산 자락의 고요한 사찰에서의 힐링"},
        
        {"destination_name": "강원도 웰니스 리조트", "country": "한국", "region": "강원도", 
         "wellness_type": "자연힐링", "price_range": 4, "duration_days": 4,
         "rating": 4.2, "activities": "숲치유,요가,건강식단", "description": "청정 자연 속에서 즐기는 웰니스 프로그램"},
        
        # 해외 웰니스 관광지
        {"destination_name": "발리 우붓 스파 리트리트", "country": "인도네시아", "region": "발리", 
         "wellness_type": "스파/요가", "price_range": 4, "duration_days": 7,
         "rating": 4.7, "activities": "요가,스파,명상,발리니즈마사지", "description": "발리 우붓의 자연 속에서 즐기는 요가와 스파"},
        
        {"destination_name": "태국 코사무이 데톡스 리조트", "country": "태국", "region": "코사무이", 
         "wellness_type": "건강관리", "price_range": 5, "duration_days": 10,
         "rating": 4.6, "activities": "데톡스,건강식단,마사지,요가", "description": "몸과 마음을 정화하는 전문 데톡스 프로그램"},
        
        {"destination_name": "일본 하코네 온천 료칸", "country": "일본", "region": "하코네", 
         "wellness_type": "온천/전통", "price_range": 4, "duration_days": 3,
         "rating": 4.4, "activities": "온천,전통료리,명상", "description": "일본 전통 온천 문화를 체험할 수 있는 료칸"},
        
        {"destination_name": "스위스 알프스 웰니스 호텔", "country": "스위스", "region": "그라우뷘덴", 
         "wellness_type": "산악힐링", "price_range": 5, "duration_days": 5,
         "rating": 4.8, "activities": "알파인스파,하이킹,명상,건강식단", "description": "알프스의 청정 자연 속에서 즐기는 프리미엄 웰니스"},
        
        {"destination_name": "터키 파묵칼레 온천", "country": "터키", "region": "데니즐리", 
         "wellness_type": "자연온천", "price_range": 3, "duration_days": 4,
         "rating": 4.1, "activities": "온천,고대유적탐방,스파", "description": "석회 계단으로 유명한 천연 온천지"},
        
        {"destination_name": "인도 리시케시 요가 아쉬람", "country": "인도", "region": "우타라칸드", 
         "wellness_type": "요가/영성", "price_range": 2, "duration_days": 14,
         "rating": 4.3, "activities": "요가,명상,아유르베다,갠지스강", "description": "요가의 성지에서 진정한 요가 수행을 경험"},
        
        {"destination_name": "아이슬란드 블루라군", "country": "아이슬란드", "region": "레이캬비크", 
         "wellness_type": "지열온천", "price_range": 4, "duration_days": 3,
         "rating": 4.5, "activities": "지열온천,스파,오로라관측", "description": "세계적으로 유명한 지열 온천 스파"}
    ]
    
    df = pd.DataFrame(destinations)
    
    # 추가 특성 컬럼 생성
    df['family_friendly'] = np.random.choice([0, 1], size=len(df), p=[0.3, 0.7])
    df['luxury_level'] = np.random.randint(1, 6, size=len(df))
    df['accessibility'] = np.random.randint(1, 6, size=len(df))
    df['season_best'] = np.random.choice(['봄', '여름', '가을', '겨울', '연중'], size=len(df))
    
    return df

def perform_wellness_clustering(df, user_preferences):
    """사용자 선호도를 바탕으로 웰니스 관광지 클러스터링 수행"""
    
    # 수치형 특성 선택
    features = ['price_range', 'duration_days', 'rating', 'family_friendly', 'luxury_level', 'accessibility']
    X = df[features].copy()
    
    # 표준화
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # KMeans 클러스터링
    n_clusters = min(5, len(df))
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df['cluster'] = kmeans.fit_predict(X_scaled)
    
    # PCA로 2차원 시각화
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    df['pca_1'] = X_pca[:, 0]
    df['pca_2'] = X_pca[:, 1]
    
    return df, kmeans, scaler, pca

def recommend_wellness_destinations(df, wellness_type, user_preferences):
    """웰니스 성향과 사용자 선호도에 맞는 관광지 추천"""
    
    # 클러스터별 추천 로직
    cluster_mapping = {
        "안전추구 모험가형": {"preferred_types": ["스파/온천", "자연힐링"], "max_price": 4, "max_duration": 7},
        "안전우선 편의형": {"preferred_types": ["스파/온천", "온천/전통"], "max_price": 4, "max_duration": 5},
        "문화체험 힐링형": {"preferred_types": ["명상/영성", "요가/영성", "온천/전통"], "max_price": 3, "max_duration": 10},
        "쇼핑마니아 사교형": {"preferred_types": ["스파/요가", "건강관리"], "max_price": 5, "max_duration": 7},
        "프리미엄 모험형": {"preferred_types": ["산악힐링", "건강관리", "지열온천"], "max_price": 5, "max_duration": 14},
        "탐험형 문화애호가": {"preferred_types": ["요가/영성", "자연힐링", "명상/영성"], "max_price": 4, "max_duration": 14},
        "문화미식 여성형": {"preferred_types": ["스파/요가", "온천/전통", "건강관리"], "max_price": 4, "max_duration": 7},
        "종합체험 활동형": {"preferred_types": ["스파/요가", "자연힐링", "건강관리"], "max_price": 5, "max_duration": 10}
    }
    
    type_config = cluster_mapping.get(wellness_type, cluster_mapping["문화체험 힐링형"])
    
    # 기본 필터링
    filtered_df = df[
        (df['wellness_type'].isin(type_config['preferred_types'])) |
        (df['price_range'] <= type_config['max_price']) |
        (df['duration_days'] <= type_config['max_duration'])
    ].copy()
    
    if filtered_df.empty:
        filtered_df = df.copy()
    
    # 추천 점수 계산
    filtered_df['recommendation_score'] = (
        filtered_df['rating'] * 0.3 +
        (6 - filtered_df['price_range']) * 0.2 +  # 가격이 낮을수록 높은 점수
        filtered_df['accessibility'] * 0.2 +
        filtered_df['luxury_level'] * 0.3
    )
    
    # 상위 추천지 선별
    top_recommendations = filtered_df.nlargest(8, 'recommendation_score')
    
    return top_recommendations

def create_wellness_visualization(df, recommendations):
    """웰니스 관광지 데이터 시각화"""
    
    # 1. 추천 관광지 분포 (가격대별, 평점별)
    fig1 = px.scatter(
        recommendations, 
        x='price_range', 
        y='rating',
        size='recommendation_score',
        color='wellness_type',
        hover_data=['destination_name', 'country'],
        title="추천 웰니스 관광지 분포"
    )
    fig1.update_layout(
        xaxis_title="가격대",
        yaxis_title="평점",
        showlegend=True
    )
    
    # 2. 국가별 추천 관광지 수
    country_counts = recommendations['country'].value_counts()
    fig2 = px.bar(
        x=country_counts.index,
        y=country_counts.values,
        title="국가별 추천 관광지 수"
    )
    fig2.update_layout(
        xaxis_title="국가",
        yaxis_title="추천 관광지 수"
    )
    
    # 3. 웰니스 유형별 분포
    type_counts = recommendations['wellness_type'].value_counts()
    fig3 = px.pie(
        values=type_counts.values,
        names=type_counts.index,
        title="추천 웰니스 유형 분포"
    )
    
    return fig1, fig2, fig3

def create_user_persona_analysis(answers, wellness_type):
    """사용자 페르소나 분석 결과 생성"""
    
    persona_analysis = {
        "안전추구 모험가형": {
            "특징": "안전을 우선시하면서도 새로운 경험을 추구하는 균형잡힌 여행객",
            "추천활동": "안전한 환경에서의 모험적 체험, 가이드 투어, 그룹 활동",
            "여행팁": "신뢰할 수 있는 여행사를 통해 안전한 모험 프로그램을 선택하세요"
        },
        "안전우선 편의형": {
            "특징": "안전하고 편리한 여행을 최우선으로 하는 신중한 여행객", 
            "추천활동": "호텔 내 시설 이용, 가이드 투어, 유명 관광지 방문",
            "여행팁": "검증된 숙소와 안전한 교통수단을 이용하여 여행 계획을 세우세요"
        },
        "문화체험 힐링형": {
            "특징": "문화적 체험과 정신적 힐링을 추구하는 성찰적 여행객",
            "추천활동": "문화유적 탐방, 명상 프로그램, 전통 체험, 자연 속 힐링",
            "여행팁": "현지 문화를 깊이 체험할 수 있는 프로그램과 충분한 휴식 시간을 확보하세요"
        },
        "쇼핑마니아 사교형": {
            "특징": "쇼핑과 사교 활동을 즐기는 활발하고 사교적인 여행객",
            "추천활동": "쇼핑몰 탐방, 현지 시장 구경, 그룹 투어, SNS 핫플레이스 방문",
            "여행팁": "쇼핑 예산을 미리 계획하고 현지인이나 다른 여행객과의 교류를 즐기세요"
        },
        "프리미엄 모험형": {
            "특징": "고급스러운 서비스와 특별한 경험을 추구하는 모험적 여행객",
            "추천활동": "프리미엄 투어, 특별 체험 프로그램, 고급 레스토랑, 럭셔리 숙소",
            "여행팁": "품질 높은 서비스와 독특한 경험을 제공하는 프리미엄 옵션을 선택하세요"
        },
        "탐험형 문화애호가": {
            "특징": "새로운 문화를 깊이 탐험하고 학습하려는 적극적인 여행객",
            "추천활동": "문화 유적 탐방, 현지인과의 교류, 전통 예술 체험, 역사 투어",
            "여행팁": "사전에 문화와 역사를 공부하고 현지 가이드와 함께하는 심층 투어를 선택하세요"
        },
        "문화미식 여성형": {
            "특징": "문화적 체험과 미식을 동시에 즐기는 세련된 여성 여행객",
            "추천활동": "현지 요리 클래스, 전통 시장 투어, 문화 공연 관람, 뷰티 체험",
            "여행팁": "현지 음식 문화를 깊이 체험하고 아름다운 사진을 남길 수 있는 장소를 방문하세요"
        },
        "종합체험 활동형": {
            "특징": "다양한 활동을 골고루 체험하고 싶어하는 에너지 넘치는 여행객",
            "추천활동": "다양한 액티비티, 문화 체험, 맛집 투어, 자연 관광, 쇼핑",
            "여행팁": "알찬 일정으로 다양한 경험을 쌓되, 적절한 휴식시간도 확보하세요"
        }
    }
    
    return persona_analysis.get(wellness_type, persona_analysis["문화체험 힐링형"])

# --- 여행 데이터 분석을 위한 추가 함수들 ---

def analyze_travel_trends(df):
    """여행 트렌드 분석"""
    
    trends = {
        "popular_destinations": df.groupby('country')['rating'].mean().sort_values(ascending=False).head(5),
        "price_distribution": df['price_range'].value_counts().sort_index(),
        "wellness_type_popularity": df['wellness_type'].value_counts(),
        "average_duration": df['duration_days'].mean(),
        "high_rated_destinations": df[df['rating'] >= 4.5]['destination_name'].tolist()
    }
    
    return trends

def create_travel_insights_dashboard(df, user_type):
    """여행 인사이트 대시보드 생성"""
    
    insights = {
        "total_destinations": len(df),
        "countries_covered": df['country'].nunique(),
        "avg_rating": df['rating'].mean(),
        "price_range_distribution": df['price_range'].value_counts().to_dict(),
        "user_type_recommendations": len(df[df['wellness_type'].str.contains('|'.join(['스파', '요가', '명상']), na=False)])
    }
    
    return insights

# 설문 완료 후 survey_results 생성 함수 수정
def convert_answers_to_survey_results(answers):
    """answers를 survey_results 형태로 변환 (복수응답 지원)"""
    survey_results = {}
    
    if not answers:
        return survey_results
    
    for key, answer in answers.items():
        if key in questions:
            question_title = questions[key]['title']
            
            # 복수응답 문항 처리
            if questions[key].get('multiple', False):
                if isinstance(answer, list) and answer:
                    answer_texts = [questions[key]['options'][idx] for idx in answer if idx < len(questions[key]['options'])]
                    answer_text = " | ".join(answer_texts)
                else:
                    answer_text = "답변 없음"
            else:
                # 단일 선택 문항 처리
                if answer is not None and answer < len(questions[key]['options']):
                    answer_text = questions[key]['options'][answer]
                else:
                    answer_text = "답변 없음"
            
            survey_results[question_title] = answer_text
    
    return survey_results

# 클러스터 정보를 제공하는 함수 추가
def get_cluster_info():
    """8개 클러스터의 상세 정보 제공"""
    
    cluster_info = {
        0: {
            "name": "안전추구 모험가형",
            "description": "안전을 우선시하면서도 새로운 경험을 추구하는 균형잡힌 성향",
            "characteristics": ["안전 중시", "사회적 여행 선호", "호텔 선호", "적당한 모험 추구"],
            "color": "#4CAF50"
        },
        1: {
            "name": "안전우선 편의형", 
            "description": "안전과 편의성을 최우선으로 하는 신중한 여행 성향",
            "characteristics": ["안전 최우선", "편리한 숙박", "가족/친구와 여행", "숙박비 투자"],
            "color": "#8BC34A"
        },
        2: {
            "name": "문화체험 힐링형",
            "description": "문화적 체험과 정신적 성장을 추구하는 성향",
            "characteristics": ["문화체험 중시", "체험활동 투자", "학습과 성장 지향", "자연관광 선호"],
            "color": "#FFC107"
        },
        3: {
            "name": "쇼핑마니아 사교형",
            "description": "쇼핑과 사교활동을 중심으로 하는 활발한 여행 성향",
            "characteristics": ["쇼핑 중심", "사회적 여행", "패션/뷰티 관심", "쇼핑 예산 투자"],
            "color": "#FF9800"
        },
        4: {
            "name": "프리미엄 모험형",
            "description": "고급스러운 서비스와 모험적 경험을 추구하는 성향",
            "characteristics": ["모험 추구", "프리미엄 호텔", "새로운 경험 중시", "숙박비 투자"],
            "color": "#F44336"
        },
        5: {
            "name": "탐험형 문화애호가",
            "description": "문화 탐험과 새로운 경험을 동시에 추구하는 성향",
            "characteristics": ["모험적 성향", "문화체험 선호", "사회적 여행", "경험과 성장 추구"],
            "color": "#9C27B0"
        },
        6: {
            "name": "문화미식 여성형",
            "description": "문화체험과 미식을 함께 즐기는 세련된 여행 성향",
            "characteristics": ["문화/미식 관심", "뷰티/패션 선호", "음식/체험 투자", "문화적 성장"],
            "color": "#E91E63"
        },
        7: {
            "name": "종합체험 활동형",
            "description": "다양한 활동을 골고루 체험하려는 적극적인 성향",
            "characteristics": ["종합적 체험", "다양한 활동", "안전 고려", "문화/미식 관심"],
            "color": "#2196F3"
        }
    }
    
    return cluster_info