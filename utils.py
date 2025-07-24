import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import plotly.express as px
import plotly.graph_objects as go

def check_access_permissions(page_type='default'):
    """페이지 접근 권한 확인"""
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.error("⚠️ 로그인 후 이용해주세요.")
        st.page_link("app.py", label="로그인 페이지로 돌아가기", icon="🏠")
        st.stop()
    
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
        "title": "2. 한국 여행에서 쇼핑의 중요도는 어느 정도인가요?",
        "factor": "요인2",  # 쇼핑 중심형
        "options": [
            "쇼핑이 여행의 가장 주요한 목적 중 하나다",
            "쇼핑 후 만족감이 여행 전체 만족도에 큰 영향을 준다",
            "교통정보는 주로 쇼핑 장소 접근을 위해 찾아본다",
            "여행전문사이트에서 쇼핑 정보를 적극 수집한다",
            "쇼핑보다는 다른 활동에 더 관심이 있다"
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
        "scores": [5, 4, 2, 1, 3]  # 새로운 국가 추구 vs 과거 경험
    },
    "q4": {
        "title": "4. 여행지에서 현지 정보 수집을 어떻게 하시나요?",
        "factor": "요인4",  # 실용적 현지 탐색형
        "options": [
            "방문지의 구체적인 정보를 현지에서 적극 수집한다",
            "대형마트를 이용하여 현지 생활을 체험한다",
            "전통시장에서 현지 문화를 직접 경험한다",
            "전통문화체험보다는 실용적 정보에 집중한다",
            "미리 계획한 대로만 움직이는 편이다"
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
            "한국 전통 식료품을 꼭 구매하고 싶다",
            "치안과 안전이 가장 우선적 고려사항이다",
            "한국 전통문화에 깊은 관심이 있다",
            "전통문화보다는 현대적인 것에 관심이 많다",
            "안전보다는 모험적 경험을 선호한다"
        ],
        "scores": [5, 4, 3, 2, 1]
    },
    "q7": {
        "title": "7. 패션/뷰티 쇼핑에 대한 관심도는?",
        "factor": "요인7",  # 패션 쇼핑형
        "options": [
            "의류 쇼핑이 여행의 주요 목적 중 하나다",
            "대형 쇼핑몰에서 최신 트렌드를 확인하고 싶다",
            "신발류 쇼핑에 특별한 관심이 있다",
            "보석이나 액세서리를 구매하고 싶다",
            "패션 쇼핑에는 별로 관심이 없다"
        ],
        "scores": [5, 4, 3, 2, 1]
    },
    "q8": {
        "title": "8. 숙박 및 동반자에 대한 선호도는?",
        "factor": "요인8",  # 프리미엄 사회적 여행형
        "options": [
            "호텔 등 고급 숙박시설을 선호한다",
            "동반자와 함께 여행하는 것을 선호한다",
            "언론매체 정보를 신뢰하고 참고한다",
            "개별 숙박 예약을 통해 맞춤형 서비스를 받고 싶다",
            "저예산으로 혼자 여행하는 것을 선호한다"
        ],
        "scores": [5, 4, 3, 2, 1]
    },
    "q9": {
        "title": "9. 개인적 특성과 쇼핑 패턴에 대해 어떻게 생각하시나요?",
        "factor": "요인9",  # 성별 기반 쇼핑 선호형
        "options": [
            "성별에 따른 쇼핑 선호도 차이가 있다고 생각한다",
            "가족행사보다는 개인적 여행을 선호한다",
            "보석/액세서리 쇼핑을 즐긴다",
            "쇼핑 자체가 큰 만족감을 준다",
            "성별이나 개인 특성과 관계없이 여행한다"
        ],
        "scores": [5, 4, 3, 2, 1]
    },
    "q10": {
        "title": "10. 디지털 미디어 활용과 화장품에 대한 관심도는?",
        "factor": "요인10",  # 디지털 미디어 개인형
        "options": [
            "유튜브 등 동영상 사이트를 적극 활용한다",
            "화장품 쇼핑이 여행의 중요한 목적이다",
            "글로벌 포털사이트에서 정보를 수집한다",
            "친지보다는 개인적으로 정보를 찾는다",
            "디지털 미디어보다 직접 경험을 선호한다"
        ],
        "scores": [5, 4, 3, 2, 1]
    },
    "q11": {
        "title": "11. 출입국 절차와 자연관광에 대한 중요도는?",
        "factor": "요인11",  # 절차 중시 자연 관광형
        "options": [
            "출입국 절차와 비자 등을 매우 중시한다",
            "이동거리와 비행시간을 신중히 고려한다",
            "자연경관 감상이 여행의 주요 목적이다",
            "한류 콘텐츠에도 관심이 있다",
            "절차나 거리보다는 즉흥적 여행을 선호한다"
        ],
        "scores": [5, 4, 3, 2, 1]
    },
    "q12": {
        "title": "12. 교통수단과 식도락에 대한 선호도는?",
        "factor": "요인12",  # 교통 편의 미식형
        "options": [
            "대중교통을 적극적으로 이용하고 싶다",
            "식도락 관광이 여행의 중요한 부분이다",
            "쇼핑과 미식을 함께 즐기고 싶다",
            "숙박 예약 시 교통 접근성을 우선 고려한다",
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
            "name": "트래디셔널 익스플로러",
            "english_name": "Traditional Explorer", 
            "description": "전통문화를 추구하는 신규 탐험가형. 안전과 전통 식품을 중시하며 모바일 편의성도 고려",
            "characteristics": ["전통문화 중시", "안전 우선", "신규 방문", "모바일 편의성"],
            "color": "#8B4513",
            "percentage": 11.3,
            "count": 292,
            "key_factors": {
                "요인6": 1.130,  # 전통문화안전 (매우높음)
                "요인3": 1.089,  # 여행경험축 (첫방문)
                "요인5": 0.413,  # 편의인프라
                "요인2": -0.119  # 쇼핑중심 (낮음)
            }
        },
        2: {
            "name": "헤리티지 러버",
            "english_name": "Heritage Lover",
            "description": "전통문화 애호가형 재방문자. 전통문화 마니아이며 디지털 미디어도 적극 활용",
            "characteristics": ["전통문화 마니아", "재방문 경험", "SNS 활용", "심화 체험"],
            "color": "#4B0082",
            "percentage": 15.4,
            "count": 399,
            "key_factors": {
                "요인6": 1.248,   # 전통문화안전 (전체 최고)
                "요인3": -0.763,  # 여행경험축 (재방문)
                "요인10": 0.274,  # 디지털미디어
                "요인5": 0.264    # 편의인프라
            }
        },
        3: {
            "name": "미니멀 트래블러",
            "english_name": "Minimal Traveler",
            "description": "소극적 힐링 추구형. 복잡한 절차를 회피하고 적극적 관광활동보다 휴식 선호",
            "characteristics": ["힐링 추구", "절차 회피", "소극적 관광", "휴식 중심"],
            "color": "#708090",
            "percentage": 13.9,
            "count": 361,
            "key_factors": {
                "요인11": -0.834,  # 절차자연관광 (매우낮음)
                "요인12": -0.778,  # 교통미식 (매우낮음)
                "요인2": -0.417,   # 쇼핑중심 (낮음)
                "요인6": -0.421    # 전통문화안전 (낮음)
            }
        },
        4: {
            "name": "프리미엄 쇼퍼",
            "english_name": "Premium Shopper",
            "description": "고급 쇼핑 중심형 재방문자. VIP급 쇼핑과 프리미엄 서비스를 추구",
            "characteristics": ["프리미엄 쇼핑", "고급 서비스", "재방문 경험", "편의성 중시"],
            "color": "#FFD700",
            "percentage": 15.9,
            "count": 411,
            "key_factors": {
                "요인2": 0.395,    # 쇼핑중심
                "요인5": 0.362,    # 편의인프라
                "요인8": 0.301,    # 프리미엄사회적
                "요인3": -0.756,   # 여행경험축 (재방문)
                "요인6": -0.834    # 전통문화안전 (매우낮음)
            }
        },
        5: {
            "name": "퍼펙트 플래너",
            "english_name": "Perfect Planner",
            "description": "완벽주의 계획형 첫 방문자. 가장 체계적으로 계획하며 자연관광과 절차를 중시",
            "characteristics": ["완벽한 계획", "체계적 준비", "자연 중시", "절차 준수"],
            "color": "#2E8B57",
            "percentage": 8.1,
            "count": 210,
            "key_factors": {
                "요인1": 1.437,    # 계획적정보추구 (전체 최고)
                "요인3": 0.810,    # 여행경험축 (첫방문)
                "요인11": 0.700,   # 절차자연관광
                "요인5": -0.795,   # 편의인프라 (매우낮음)
                "요인2": -0.444    # 쇼핑중심 (낮음)
            }
        },
        6: {
            "name": "스마트 컨비니언스",
            "english_name": "Smart Convenience", 
            "description": "편의성 추구형 첫 방문자. 스마트 기술과 디지털 서비스를 적극 활용",
            "characteristics": ["디지털 활용", "편의성 추구", "첫 방문", "스마트 여행"],
            "color": "#1E90FF",
            "percentage": 12.2,
            "count": 317,
            "key_factors": {
                "요인3": 0.875,    # 여행경험축 (첫방문)
                "요인5": 0.548,    # 편의인프라
                "요인6": -0.912,   # 전통문화안전 (매우낮음)
                "요인9": -0.333    # 성별기반쇼핑 (낮음)
            }
        },
        7: {
            "name": "인디펜던트 백패커",
            "english_name": "Independent Backpacker",
            "description": "독립적 경제형 여행자. 고급서비스를 회피하고 즉흥적 자유여행 선호",
            "characteristics": ["경제적 여행", "독립적 성향", "즉흥적", "자유여행"],
            "color": "#8FBC8F",
            "percentage": 14.0,
            "count": 364,
            "key_factors": {
                "요인8": -1.169,   # 프리미엄사회적 (전체 최저)
                "요인1": -0.680,   # 계획적정보추구 (낮음)
                "요인10": -0.315,  # 디지털미디어 (낮음)
                "요인11": 0.132    # 절차자연관광 (약간높음)
            }
        },
        8: {
            "name": "멀티 퍼포스 익스피어런서",
            "english_name": "Multi-Purpose Experiencer",
            "description": "다목적 체험형 여행자. 쇼핑부터 자연관광까지 모든 것을 경험하고 싶어하는 유형",
            "characteristics": ["다양한 체험", "프리미엄 서비스", "즉흥적", "멀티 액티비티"],
            "color": "#FF6347",
            "percentage": 9.1,
            "count": 237,
            "key_factors": {
                "요인2": 0.776,    # 쇼핑중심
                "요인11": 0.707,   # 절차자연관광
                "요인3": 0.551,    # 여행경험축 (첫방문)
                "요인6": 0.477,    # 전통문화안전
                "요인8": 0.416,    # 프리미엄사회적
                "요인1": -0.757,   # 계획적정보추구 (매우낮음)
                "요인5": -0.634    # 편의인프라 (매우낮음)
            }
        }
    }

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

def create_factor_analysis_chart(factor_scores):
    """12개 요인 점수 레이더 차트 생성"""
    factor_names = [
        "계획적정보추구", "쇼핑중심", "여행경험축", "실용적현지탐색",
        "편의인프라중시", "전통문화안전", "패션쇼핑", "프리미엄사회적",
        "성별기반쇼핑", "디지털미디어", "절차자연관광", "교통미식"
    ]
    
    values = [factor_scores.get(f"요인{i}", 0) for i in range(1, 13)]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=factor_names,
        fill='toself',
        name='나의 요인 점수',
        line_color='#4CAF50'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[-2, 2]
            )),
        showlegend=True,
        title="12개 요인별 개인 성향 분석",
        font=dict(color='#2E7D32', size=12),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
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
        marker_color='#4CAF50'
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
        font_color='#2E7D32'
    )
    
    return fig

def show_footer():
    """푸터 표시"""
    st.markdown("---")
    st.markdown("💡 **주의사항**: 본 진단 결과는 참고용이며, 실제 여행 계획 시에는 개인의 선호도를 종합적으로 고려하시기 바랍니다.")

# 한국 관광지 데이터 (클러스터별 맞춤)
wellness_destinations = {
    "전통문화체험": [
        {
            "name": "경복궁",
            "lat": 37.5796,
            "lon": 126.9770,
            "type": "전통문화체험",
            "description": "조선왕조의 정궁으로 전통 문화와 역사를 체험할 수 있는 곳",
            "website": "https://www.royalpalace.go.kr",
            "rating": 4.6,
            "price_range": "3,000원",
            "distance_from_incheon": 42,
            "travel_time_car": "1시간",
            "travel_time_train": "1시간 15분",
            "travel_cost_car": "15,000원",
            "travel_cost_train": "2,150원",
            "target_clusters": [1, 2, 5],  # 전통문화 관심 클러스터
            "image_url": "🏛️"
        },
        {
            "name": "한옥마을 (전주)",
            "lat": 35.8156,
            "lon": 127.1530,
            "type": "전통문화체험",
            "description": "전통 한옥과 한국 전통문화를 체험할 수 있는 마을",
            "website": "https://www.jeonju.go.kr",
            "rating": 4.5,
            "price_range": "무료-20,000원",
            "distance_from_incheon": 243,
            "travel_time_car": "3시간",
            "travel_time_train": "2시간 30분",
            "travel_cost_car": "35,000원",
            "travel_cost_train": "25,600원",
            "target_clusters": [1, 2],
            "image_url": "🏘️"
        }
    ],
    "프리미엄쇼핑": [
        {
            "name": "명동 쇼핑거리",
            "lat": 37.5636,
            "lon": 126.9826,
            "type": "프리미엄쇼핑",
            "description": "한류 스타 굿즈와 최신 뷰티 제품을 만날 수 있는 핫플레이스",
            "website": "https://www.visitseoul.net",
            "rating": 4.3,
            "price_range": "10,000-50,000원",
            "distance_from_incheon": 45,
            "travel_time_car": "1시간",
            "travel_time_train": "1시간 10분",
            "travel_cost_car": "15,000원",
            "travel_cost_train": "2,150원",
            "target_clusters": [4, 7, 8],  # 쇼핑 중심 클러스터
            "image_url": "🛍️"
        },
        {
            "name": "강남 압구정로데오",
            "lat": 37.5175,
            "lon": 127.0473,
            "type": "프리미엄쇼핑",
            "description": "프리미엄 브랜드와 최신 패션을 만날 수 있는 고급 쇼핑 지역",
            "website": "https://www.gangnam.go.kr",
            "rating": 4.5,
            "price_range": "50,000-200,000원",
            "distance_from_incheon": 50,
            "travel_time_car": "1시간 20분",
            "travel_time_train": "1시간 30분",
            "travel_cost_car": "18,000원",
            "travel_cost_train": "2,150원",
            "target_clusters": [4, 7],  # 프리미엄 쇼핑 클러스터
            "image_url": "👜"
        }
    ],
    "자연힐링": [
        {
            "name": "제주 한라산",
            "lat": 33.3617,
            "lon": 126.5292,
            "type": "자연힐링",
            "description": "한국 최고봉으로 산림욕과 트레킹이 가능한 자연 치유 공간",
            "website": "https://www.hallasan.go.kr",
            "rating": 4.7,
            "price_range": "무료",
            "distance_from_incheon": 460,
            "travel_time_car": "항공 1시간 + 차량 1시간",
            "travel_time_train": "항공 이용 필수",
            "travel_cost_car": "120,000원 (항공료 포함)",
            "travel_cost_train": "120,000원 (항공료 포함)",
            "target_clusters": [3, 5, 8],  # 자연/힐링 선호 클러스터
            "image_url": "🏔️"
        },
        {
            "name": "설악산 국립공원",
            "lat": 38.1197,
            "lon": 128.4655,
            "type": "자연힐링",
            "description": "아름다운 자연경관과 맑은 공기로 유명한 산악 치유 공간",
            "website": "https://www.knps.or.kr",
            "rating": 4.6,
            "price_range": "3,500원",
            "distance_from_incheon": 185,
            "travel_time_car": "2시간 30분",
            "travel_time_train": "3시간",
            "travel_cost_car": "28,000원",
            "travel_cost_train": "18,500원",
            "target_clusters": [3, 5],
            "image_url": "🌿"
        }
    ],
    "스마트투어": [
        {
            "name": "동대문 디지털플라자",
            "lat": 37.5665,
            "lon": 127.0095,
            "type": "스마트투어",
            "description": "최첨단 디지털 기술과 쇼핑을 결합한 미래형 복합문화공간",
            "website": "https://www.ddp.or.kr",
            "rating": 4.4,
            "price_range": "무료-30,000원",
            "distance_from_incheon": 47,
            "travel_time_car": "1시간 10분",
            "travel_time_train": "1시간 20분",
            "travel_cost_car": "16,000원",
            "travel_cost_train": "2,150원",
            "target_clusters": [6, 8],  # 스마트/디지털 선호 클러스터
            "image_url": "🏢"
        },
        {
            "name": "코엑스",
            "lat": 37.5115,
            "lon": 127.0592,
            "type": "스마트투어",
            "description": "아시아 최대 지하 쇼핑몰과 첨단 시설을 갖춘 복합 문화공간",
            "website": "https://www.coex.co.kr",
            "rating": 4.2,
            "price_range": "무료-50,000원",
            "distance_from_incheon": 52,
            "travel_time_car": "1시간 25분",
            "travel_time_train": "1시간 35분",
            "travel_cost_car": "19,000원",
            "travel_cost_train": "2,150원",
            "target_clusters": [6],
            "image_url": "🏬"
        }
    ],
    "미식체험": [
        {
            "name": "광장시장",
            "lat": 37.5700,
            "lon": 126.9996,
            "type": "미식체험",
            "description": "전통 한식과 길거리 음식을 맛볼 수 있는 대표 전통시장",
            "website": "https://www.kwangjangmarket.co.kr",
            "rating": 4.4,
            "price_range": "3,000-15,000원",
            "distance_from_incheon": 45,
            "travel_time_car": "1시간 10분",
            "travel_time_train": "1시간 20분",
            "travel_cost_car": "18,000원",
            "travel_cost_train": "2,150원",
            "target_clusters": [7, 8],  # 미식/경제적 여행 클러스터
            "image_url": "🍜"
        },
        {
            "name": "홍대 맛집거리",
            "lat": 37.5563,
            "lon": 126.9244,
            "type": "미식체험",
            "description": "트렌디한 카페와 레스토랑이 모인 젊은이들의 거리",
            "website": "https://www.visitseoul.net",
            "rating": 4.2,
            "price_range": "8,000-25,000원",
            "distance_from_incheon": 35,
            "travel_time_car": "50분",
            "travel_time_train": "1시간",
            "travel_cost_car": "12,000원",
            "travel_cost_train": "1,950원",
            "target_clusters": [6, 7, 8],
            "image_url": "🍽️"
        }
    ]
}

def calculate_recommendations_by_cluster(cluster_result):
    """클러스터 기반 맞춤 추천 계산"""
    user_cluster = cluster_result['cluster']
    cluster_info = get_cluster_info()
    
    recommendations = []
    
    # 모든 관광지에 대해 점수 계산
    for category, places in wellness_destinations.items():
        for place in places:
            score = 0
            
            # 클러스터 타겟 매칭 보너스
            if user_cluster in place.get('target_clusters', []):
                score += 40  # 높은 기본 점수
            
            # 기본 평점 반영
            score += place["rating"] * 10
            
            # 클러스터 신뢰도 반영
            score += cluster_result['confidence'] * 20
            
            # 클러스터별 특별 보너스
            cluster_data = cluster_info[user_cluster]
            if "쇼핑" in cluster_data['name'] and "쇼핑" in category:
                score += 20
            elif "전통" in cluster_data['name'] and "전통문화" in category:
                score += 20
            elif "스마트" in cluster_data['name'] and "스마트" in category:
                score += 20
            elif "자연" in cluster_data['characteristics'] and "자연" in category:
                score += 20
            elif "미식" in category and any("미식" in char for char in cluster_data['characteristics']):
                score += 15
            
            place_with_score = place.copy()
            place_with_score["recommendation_score"] = score
            place_with_score["cluster_match"] = user_cluster in place.get('target_clusters', [])
            recommendations.append(place_with_score)
    
    # 점수 순으로 정렬
    recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)
    
    return recommendations[:8]  # 상위 8개 추천

def apply_global_styles():
    """전역 CSS 스타일 적용"""
    st.markdown("""
    <style>
        /* 전역 스타일 변수 */
        :root {
            --primary: #4CAF50;
            --primary-dark: #2E7D32;
            --primary-light: #81C784;
            --secondary: #66BB6A;
            --background: linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 50%, #A5D6A7 100%);
            --card-bg: rgba(255, 255, 255, 0.95);
            --border-radius: 20px;
            --shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            --shadow-hover: 0 12px 40px rgba(76, 175, 80, 0.2);
        }
        
        /* 기본 배경 */
        [data-testid="stAppViewContainer"] > .main {
            background: var(--background);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        /* 메인 컨테이너 */
        .main .block-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem 3rem !important;
        }
        
        /* 카드 공통 스타일 */
        .card {
            background: var(--card-bg);
            backdrop-filter: blur(15px);
            border: 2px solid rgba(76, 175, 80, 0.3);
            border-radius: var(--border-radius);
            padding: 25px;
            margin: 20px 0;
            box-shadow: var(--shadow);
            transition: all 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            border-color: var(--primary);
            box-shadow: var(--shadow-hover);
        }
        
        /* 버튼 공통 스타일 */
        div[data-testid="stButton"] > button {
            background: linear-gradient(45deg, var(--primary), var(--secondary)) !important;
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
            background: linear-gradient(45deg, #388E3C, var(--primary)) !important;
            transform: translateY(-3px) !important;
            box-shadow: 0 8px 25px rgba(76, 175, 80, 0.4) !important;
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
        }
    </style>
    """, unsafe_allow_html=True)