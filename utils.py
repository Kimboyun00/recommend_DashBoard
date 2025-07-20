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
        "title": "1. 한국 여행의 주된 목적은 무엇인가요?",
        "options": [
            "한류 콘텐츠 관련 (K-pop, 드라마, 영화)",
            "전통문화 체험 (고궁, 한옥, 전통예술)",
            "자연경관 감상 및 힐링",
            "쇼핑 및 미식 체험",
            "특별한 행사나 축제 참여"
        ]
    },
    "q2": {
        "title": "2. 여행 정보를 주로 어디서 얻나요? (복수 선택 가능)",
        "options": [
            "소셜미디어 (인스타그램, 페이스북)",
            "동영상 사이트 (유튜브, 틱톡)",
            "글로벌 포털사이트 (구글 등)",
            "블로그 및 개인 후기",
            "여행사 또는 가이드북",
            "지인 추천"
        ],
        "multiple": True
    },
    "q3": {
        "title": "3. 한국에서 가장 관심 있는 쇼핑 품목은?",
        "options": [
            "화장품 및 뷰티용품",
            "의류 및 패션아이템",
            "전통 기념품 및 특산품",
            "식료품 및 간식",
            "전자제품",
            "쇼핑에 관심 없음"
        ]
    },
    "q4": {
        "title": "4. 선호하는 여행 스타일은?",
        "options": [
            "혼자서 자유롭게",
            "가족이나 친구와 함께",
            "소규모 그룹 투어",
            "대규모 단체 투어"
        ]
    },
    "q5": {
        "title": "5. 한국 여행에서 가장 중요하게 생각하는 것은?",
        "options": [
            "편리한 교통 및 언어소통",
            "다양한 체험 활동",
            "경제적인 여행비용",
            "고품질 숙박 및 서비스",
            "안전하고 깨끗한 환경"
        ]
    },
    "q6": {
        "title": "6. 한국에서 가장 하고 싶은 활동은? (복수 선택 가능)",
        "options": [
            "쇼핑 (면세점, 시장 등)",
            "음식/미식 체험",
            "전통문화 체험",
            "자연경관 감상",
            "한류 관련 장소 방문",
            "행사/축제 참여"
        ],
        "multiple": True
    },
    "q7": {
        "title": "7. 선호하는 숙박 시설은?",
        "options": [
            "고급 호텔",
            "비즈니스 호텔",
            "게스트하우스/호스텔",
            "한옥 스테이",
            "펜션/리조트"
        ]
    },
    "q8": {
        "title": "8. 여행 후 가장 중요하게 생각하는 것은?",
        "options": [
            "새로운 경험과 추억",
            "다양한 정보와 지식 습득",
            "충분한 휴식과 힐링",
            "SNS에 공유할 만한 콘텐츠",
            "경제적 만족감 (가성비)"
        ]
    }
}

# 실제 데이터 기반 클러스터 점수 계산 함수들
def calculate_cluster_0_score(answers):
    """클러스터 0: 한류 트렌디형"""
    score = 0
    
    # Q1: 한류 콘텐츠 관심도
    if answers.get('q1') == 0: score += 4  # 한류 콘텐츠
    
    # Q2: SNS/동영상 사이트 이용 (복수응답)
    q2_answers = answers.get('q2', [])
    if isinstance(q2_answers, list):
        if 0 in q2_answers: score += 3  # 소셜미디어
        if 1 in q2_answers: score += 3  # 동영상 사이트
    
    # Q3: 쇼핑 선호
    if answers.get('q3') in [0, 1]: score += 3  # 화장품, 의류
    
    # Q4: 동행자와 함께
    if answers.get('q4') == 1: score += 2  # 가족/친구와
    
    # Q6: 쇼핑 및 한류 관련 활동 (복수응답)
    q6_answers = answers.get('q6', [])
    if isinstance(q6_answers, list):
        if 0 in q6_answers: score += 2  # 쇼핑
        if 4 in q6_answers: score += 3  # 한류 관련 장소
    
    # Q8: SNS 콘텐츠 중시
    if answers.get('q8') == 3: score += 2  # SNS 공유 콘텐츠
    
    return score

def calculate_cluster_1_score(answers):
    """클러스터 1: 종합형 실속파"""
    score = 0
    
    # Q1: 다양한 동기 (한류 외의 모든 옵션)
    if answers.get('q1') in [1, 2, 3, 4]: score += 2
    
    # Q2: 다양한 정보 채널 이용 (복수응답 개수)
    q2_answers = answers.get('q2', [])
    if isinstance(q2_answers, list):
        if len(q2_answers) >= 3: score += 4  # 3개 이상 정보 채널
        elif len(q2_answers) >= 2: score += 2
    
    # Q3: 다양한 쇼핑 품목
    if answers.get('q3') in [0, 1, 2, 3]: score += 2  # 쇼핑에 관심
    
    # Q5: 실용성 중시
    if answers.get('q5') in [0, 2]: score += 3  # 편리함, 경제성
    
    # Q6: 다양한 활동 관심 (복수응답)
    q6_answers = answers.get('q6', [])
    if isinstance(q6_answers, list):
        if len(q6_answers) >= 3: score += 3  # 다양한 활동
    
    # Q8: 경제적 만족
    if answers.get('q8') == 4: score += 2  # 가성비
    
    return score

def calculate_cluster_2_score(answers):
    """클러스터 2: 수동형 관광객"""
    score = 0
    
    # Q2: 정보탐색 소극적 (적은 정보 채널)
    q2_answers = answers.get('q2', [])
    if isinstance(q2_answers, list):
        if len(q2_answers) <= 1: score += 4  # 1개 이하 정보 채널
    
    # Q3: 쇼핑 무관심
    if answers.get('q3') == 5: score += 3  # 쇼핑에 관심 없음
    
    # Q6: 활동 참여도 낮음 (복수응답)
    q6_answers = answers.get('q6', [])
    if isinstance(q6_answers, list):
        if len(q6_answers) <= 1: score += 4  # 1개 이하 활동
    
    # 기본적으로 모든 관심도가 낮은 경우
    total_interests = 0
    if answers.get('q1') is not None: total_interests += 1
    if len(answers.get('q6', [])) > 0: total_interests += len(answers.get('q6', []))
    
    if total_interests <= 2: score += 3
    
    return score

def calculate_cluster_3_score(answers):
    """클러스터 3: 체험중심 실용형"""
    score = 0
    
    # Q1: 쇼핑 및 미식 체험
    if answers.get('q1') == 3: score += 4  # 쇼핑/미식
    
    # Q3: 쇼핑 관심
    if answers.get('q3') in [0, 1, 3]: score += 3  # 화장품, 의류, 식료품
    
    # Q5: 편의성 중시
    if answers.get('q5') == 0: score += 3  # 편리한 교통/언어소통
    
    # Q6: 쇼핑, 음식 체험 (복수응답)
    q6_answers = answers.get('q6', [])
    if isinstance(q6_answers, list):
        if 0 in q6_answers: score += 3  # 쇼핑
        if 1 in q6_answers: score += 3  # 음식/미식
    
    # Q8: 새로운 경험
    if answers.get('q8') == 0: score += 2  # 새로운 경험
    
    return score

def calculate_cluster_4_score(answers):
    """클러스터 4: 고소득 전통형"""
    score = 0
    
    # Q1: 전통문화 체험
    if answers.get('q1') == 1: score += 4  # 전통문화
    
    # Q2: 글로벌 포털사이트 이용 (복수응답)
    q2_answers = answers.get('q2', [])
    if isinstance(q2_answers, list):
        if 2 in q2_answers: score += 3  # 글로벌 포털사이트
    
    # Q4: 동행자와 함께
    if answers.get('q4') == 1: score += 2  # 가족/친구와
    
    # Q5: 고품질 서비스
    if answers.get('q5') == 3: score += 3  # 고품질 숙박/서비스
    
    # Q6: 전통문화 체험 (복수응답)
    q6_answers = answers.get('q6', [])
    if isinstance(q6_answers, list):
        if 2 in q6_answers: score += 3  # 전통문화 체험
    
    # Q7: 고급 호텔
    if answers.get('q7') == 0: score += 2  # 고급 호텔
    
    return score

def calculate_cluster_5_score(answers):
    """클러스터 5: 행사 관심형"""
    score = 0
    
    # Q1: 행사/축제 참여
    if answers.get('q1') == 4: score += 4  # 행사/축제
    elif answers.get('q1') == 1: score += 2  # 전통문화
    
    # Q5: 경제적 여행
    if answers.get('q5') == 2: score += 3  # 경제적 비용
    
    # Q6: 행사/축제 및 전통문화 (복수응답)
    q6_answers = answers.get('q6', [])
    if isinstance(q6_answers, list):
        if 5 in q6_answers: score += 4  # 행사/축제
        if 2 in q6_answers: score += 2  # 전통문화
    
    # Q8: 가성비
    if answers.get('q8') == 4: score += 3  # 경제적 만족감
    
    return score

def calculate_cluster_6_score(answers):
    """클러스터 6: 자연 힐링형"""
    score = 0
    
    # Q1: 자연경관 감상
    if answers.get('q1') == 2: score += 4  # 자연경관/힐링
    
    # Q3: 쇼핑 적당한 관심
    if answers.get('q3') in [2, 3]: score += 2  # 전통 기념품, 식료품
    
    # Q5: 안전하고 깨끗한 환경
    if answers.get('q5') == 4: score += 3  # 안전/깨끗함
    
    # Q6: 자연경관 감상 (복수응답)
    q6_answers = answers.get('q6', [])
    if isinstance(q6_answers, list):
        if 3 in q6_answers: score += 4  # 자연경관 감상
    
    # Q7: 고급 호텔이나 펜션
    if answers.get('q7') in [0, 4]: score += 2  # 고급 호텔, 펜션/리조트
    
    # Q8: 휴식과 힐링
    if answers.get('q8') == 2: score += 4  # 충분한 휴식/힐링
    
    return score

def calculate_cluster_7_score(answers):
    """클러스터 7: 소외형 여행객"""
    score = 0
    
    # Q2: 정보탐색 매우 소극적
    q2_answers = answers.get('q2', [])
    if isinstance(q2_answers, list):
        if len(q2_answers) == 0: score += 4  # 정보 채널 없음
        elif len(q2_answers) == 1: score += 2
    
    # Q4: 혼자 여행
    if answers.get('q4') == 0: score += 4  # 혼자서
    
    # Q6: 활동 참여도 매우 낮음
    q6_answers = answers.get('q6', [])
    if isinstance(q6_answers, list):
        if len(q6_answers) == 0: score += 4  # 활동 없음
        elif len(q6_answers) == 1: score += 2
    
    # 전반적으로 소극적인 패턴
    passive_indicators = 0
    if answers.get('q3') == 5: passive_indicators += 1  # 쇼핑 무관심
    if len(answers.get('q2', [])) <= 1: passive_indicators += 1  # 정보탐색 소극적
    if len(answers.get('q6', [])) <= 1: passive_indicators += 1  # 활동 소극적
    
    score += passive_indicators * 2
    
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
    
    # 신뢰도 계산
    total_score = sum(cluster_scores.values())
    confidence = best_score / max(total_score, 1) if total_score > 0 else 0.5
    
    # 동점 처리
    sorted_clusters = sorted(cluster_scores.items(), 
                           key=lambda x: x[1], reverse=True)
    
    if len(sorted_clusters) > 1 and sorted_clusters[0][1] == sorted_clusters[1][1]:
        resolved_result = resolve_tie(answers, sorted_clusters[0][0], sorted_clusters[1][0])
        if isinstance(resolved_result, dict):
            return resolved_result
        else:
            best_cluster = resolved_result
    
    return {
        'cluster': best_cluster,
        'score': best_score,
        'confidence': confidence,
        'all_scores': cluster_scores
    }

def resolve_tie(answers, cluster1, cluster2):
    """동점 시 추가 규칙으로 결정"""
    
    # 기본 클러스터 점수 재계산
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
    
    selected_cluster = cluster1  # 기본값
    
    # 여행 목적으로 구분
    q1_answer = answers.get('q1')
    if q1_answer == 0:  # 한류
        if cluster1 == 0 or cluster2 == 0:
            selected_cluster = 0
    elif q1_answer == 1:  # 전통문화
        if cluster1 == 4 or cluster2 == 4:
            selected_cluster = 4
        elif cluster1 == 5 or cluster2 == 5:
            selected_cluster = 5
    elif q1_answer == 2:  # 자연경관
        if cluster1 == 6 or cluster2 == 6:
            selected_cluster = 6
    elif q1_answer == 3:  # 쇼핑/미식
        if cluster1 == 3 or cluster2 == 3:
            selected_cluster = 3
    
    # 여행 스타일로 구분
    if answers.get('q4') == 0:  # 혼자 여행
        if cluster1 == 7 or cluster2 == 7:
            selected_cluster = 7
    
    # 신뢰도 계산
    best_score = cluster_scores[selected_cluster]
    total_score = sum(cluster_scores.values())
    confidence = best_score / max(total_score, 1) if total_score > 0 else 0.5
    
    return {
        'cluster': selected_cluster,
        'score': best_score,
        'confidence': confidence,
        'all_scores': cluster_scores
    }

def calculate_wellness_score(answers):
    """웰니스 관광 성향 점수 계산 (클러스터 기반)"""
    cluster_result = determine_cluster(answers)
    
    if isinstance(cluster_result, dict):
        cluster_score = cluster_result['score']
        cluster_id = cluster_result['cluster']
        confidence = cluster_result['confidence']
        all_scores = cluster_result['all_scores']
    else:
        cluster_id = cluster_result
        cluster_score = 15
        confidence = 0.8
        all_scores = {i: 10 if i == cluster_id else 5 for i in range(8)}
    
    max_possible_score = 25  # 최대 가능 점수 증가
    wellness_score = min(100, (cluster_score / max_possible_score) * 100)
    
    score_breakdown = {
        'cluster_id': cluster_id,
        'cluster_score': cluster_score,
        'confidence': confidence,
        'all_cluster_scores': all_scores
    }
    
    return wellness_score, score_breakdown

def classify_wellness_type(score, cluster_id=None):
    """웰니스 관광 성향 분류 (실제 클러스터 기반)"""
    
    cluster_types = {
        0: ("한류 트렌디형", "#4CAF50"),
        1: ("종합형 실속파", "#8BC34A"),
        2: ("수동형 관광객", "#FFC107"),
        3: ("체험중심 실용형", "#FF9800"),
        4: ("고소득 전통형", "#F44336"),
        5: ("행사 관심형", "#9C27B0"),
        6: ("자연 힐링형", "#E91E63"),
        7: ("소외형 여행객", "#2196F3")
    }
    
    if cluster_id is not None and cluster_id in cluster_types:
        return cluster_types[cluster_id]
    
    # 점수 기반 분류 (호환성 유지)
    if score <= 30:
        return "수동형 관광객", "#FFC107"
    elif score <= 50:
        return "종합형 실속파", "#8BC34A"
    elif score <= 70:
        return "체험중심 실용형", "#FF9800"
    else:
        return "한류 트렌디형", "#4CAF50"

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
        "한류 트렌디형": {
            "특징": "한류 콘텐츠와 SNS를 중심으로 하는 트렌디하고 활발한 여행객",
            "추천활동": "K-pop 관련 명소, 트렌디한 쇼핑몰, SNS 핫플레이스 탐방",
            "여행팁": "최신 트렌드 정보를 SNS로 확인하고 동행자와 함께 즐거운 쇼핑을 계획하세요",
            "선호지역": "강남, 홍대, 명동, 성수동",
            "예산대": "중상급 (쇼핑과 체험 중심)"
        },
        "종합형 실속파": {
            "특징": "다양한 관심사를 가지고 정보를 적극적으로 탐색하는 실용적인 여행객",
            "추천활동": "문화체험과 쇼핑, 미식을 균형있게 조합한 종합 투어",
            "여행팁": "다양한 정보 채널을 활용하여 알찬 일정을 계획하고 가성비를 고려하세요",
            "선호지역": "시내 전역, 전통시장, 복합쇼핑몰",
            "예산대": "중급 (효율적 예산 운용)"
        },
        "수동형 관광객": {
            "특징": "관광활동에 소극적이며 동행자의 계획에 의존하는 수동적인 여행객",
            "추천활동": "편안한 카페, 간단한 시내 관광, 가이드 투어",
            "여행팁": "무리하지 않는 선에서 편안하게 즐길 수 있는 일정을 추천합니다",
            "선호지역": "접근성 좋은 시내 중심가",
            "예산대": "하급 (최소한의 비용)"
        },
        "체험중심 실용형": {
            "특징": "음식과 쇼핑 중심의 체험을 중시하며 편의성을 추구하는 실용적 여행객",
            "추천활동": "맛집 투어, 시장 체험, 쇼핑몰 탐방, 요리 클래스",
            "여행팁": "교통이 편리한 곳을 중심으로 미식과 쇼핑을 즐기는 일정을 짜세요",
            "선호지역": "명동, 인사동, 동대문, 남대문시장",
            "예산대": "중급 (체험과 쇼핑 중심)"
        },
        "고소득 전통형": {
            "특징": "전통과 현대 문화에 모두 관심이 있는 고소득층 성향의 여행객",
            "추천활동": "고궁 투어, 전통문화 체험, 고급 쇼핑, 프리미엄 한식",
            "여행팁": "품질 높은 서비스와 깊이 있는 문화 체험을 중심으로 계획하세요",
            "선호지역": "경복궁, 창덕궁, 인사동, 강남 고급 쇼핑가",
            "예산대": "상급 (프리미엄 경험 중심)"
        },
        "행사 관심형": {
            "특징": "전통문화와 특별한 행사에 관심이 있는 계획적이고 경제적인 여행객",
            "추천활동": "문화 축제, 전통 공연, 계절별 특별 행사 참여",
            "여행팁": "사전에 행사 일정을 확인하고 경제적인 패키지를 활용하세요",
            "선호지역": "문화유적지, 축제 개최지, 전통 공연장",
            "예산대": "중하급 (가성비 중심)"
        },
        "자연 힐링형": {
            "특징": "자연경관과 휴식을 중시하는 여유롭고 힐링을 추구하는 여행객",
            "추천활동": "자연공원 산책, 한강 유람, 온천, 스파, 조용한 카페",
            "여행팁": "충분한 휴식과 자연을 즐길 수 있는 여유로운 일정을 계획하세요",
            "선호지역": "한강공원, 남산, 북한산, 온천 리조트",
            "예산대": "중상급 (편안한 숙박과 힐링 중심)"
        },
        "소외형 여행객": {
            "특징": "혼자 여행하며 정보탐색과 참여도가 낮은 소극적인 여행객",
            "추천활동": "혼자서도 편안한 박물관, 조용한 카페, 간단한 시내 관광",
            "여행팁": "혼자서도 안전하고 편안하게 즐길 수 있는 장소를 중심으로 하세요",
            "선호지역": "안전한 시내 중심가, 대중교통 접근성 좋은 곳",
            "예산대": "하급 (최소 비용으로 안전 중심)"
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
    """실제 분석된 8개 클러스터의 상세 정보"""
    
    cluster_info = {
        0: {
            "name": "한류 트렌디형",
            "description": "한류 콘텐츠와 SNS를 중심으로 하는 트렌디한 쇼핑 선호 여행객",
            "characteristics": ["한류 콘텐츠 높은 관심", "SNS/동영상 활발 이용", "쇼핑 선호", "주로 여성", "동행자와 함께"],
            "color": "#4CAF50",
            "keywords": ["한류", "SNS", "쇼핑", "트렌드", "동행"]
        },
        1: {
            "name": "종합형 실속파",
            "description": "다양한 동기와 정보 채널을 활용하는 종합적이고 실용적인 여행객",
            "characteristics": ["다양한 여행 동기", "정보수집 적극적", "쇼핑품목 다양", "실용성 중시", "고른 관심사"],
            "color": "#8BC34A",
            "keywords": ["종합", "실속", "다양성", "정보탐색", "실용"]
        },
        2: {
            "name": "수동형 관광객",
            "description": "관광활동에 낮은 참여도를 보이는 수동적인 여행객",
            "characteristics": ["낮은 참여도", "무관심", "낮은 만족도", "정보탐색 소극적", "동행자 의존"],
            "color": "#FFC107",
            "keywords": ["수동", "무관심", "의존", "소극적", "저만족"]
        },
        3: {
            "name": "체험중심 실용형",
            "description": "음식과 쇼핑 중심의 체험을 중시하며 편의성을 추구하는 실용적 여행객",
            "characteristics": ["음식/미식 중심", "쇼핑 활발", "편의성 중시", "교통정보 중요", "체험 위주"],
            "color": "#FF9800",
            "keywords": ["미식", "쇼핑", "편의", "체험", "실용"]
        },
        4: {
            "name": "고소득 전통형",
            "description": "전통과 현대에 모두 관심이 있는 고소득층 성향의 정보탐색 능력이 뛰어난 여행객",
            "characteristics": ["높은 정보탐색 능력", "면세점 이용", "전통문화 관심", "고궁 방문", "동행 여행"],
            "color": "#F44336",
            "keywords": ["전통", "고소득", "면세점", "정보능력", "문화"]
        },
        5: {
            "name": "행사 관심형",
            "description": "전통문화와 행사에 관심이 있는 경제적이고 계획적인 여행객",
            "characteristics": ["전통문화 관심", "행사/축제 참여", "경제적 여행", "가성비 고려", "계획적"],
            "color": "#9C27B0",
            "keywords": ["전통", "행사", "축제", "가성비", "계획"]
        },
        6: {
            "name": "자연 힐링형",
            "description": "자연경관과 휴식을 중시하는 여유롭고 힐링을 추구하는 여행객",
            "characteristics": ["자연경관 중시", "충분한 사전준비", "호텔 선호", "휴식 중심", "힐링 추구"],
            "color": "#E91E63",
            "keywords": ["자연", "힐링", "휴식", "호텔", "경관"]
        },
        7: {
            "name": "소외형 여행객",
            "description": "정보탐색과 참여도가 모두 낮은 소외형 혼자 여행객",
            "characteristics": ["혼자 여행", "낮은 정보탐색", "낮은 참여도", "낮은 만족도", "소극적 태도"],
            "color": "#2196F3",
            "keywords": ["혼자", "소극적", "저만족", "소외", "정보부족"]
        }
    }
    
    return cluster_info