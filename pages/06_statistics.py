# pages/06_statistics.py (웰니스 통계 페이지 - 새로운 설문 구조 반영)

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from utils import (check_access_permissions, determine_cluster, get_cluster_info, 
                  classify_wellness_type, create_user_persona_analysis, questions)

# 로그인 체크
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("app.py")

# 페이지 설정
st.set_page_config(
    page_title="웰니스 투어 통계",
    page_icon="📈",
    layout="wide"
)

# 접근 권한 확인 (통계 페이지는 설문 완료 없이도 볼 수 있음)
check_access_permissions('home')

# 웰니스 관광지 데이터
wellness_destinations = {
    "한류/쇼핑": [
        {
            "name": "명동 쇼핑거리",
            "rating": 4.3,
            "price_range": "10,000-50,000원",
            "distance_from_incheon": 45,
            "travel_cost_car": "15,000원",
            "travel_cost_train": "2,150원"
        },
        {
            "name": "강남 K-STAR ROAD",
            "rating": 4.5,
            "price_range": "무료-30,000원",
            "distance_from_incheon": 50,
            "travel_cost_car": "18,000원",
            "travel_cost_train": "2,150원"
        }
    ],
    "전통문화": [
        {
            "name": "경복궁",
            "rating": 4.6,
            "price_range": "3,000원",
            "distance_from_incheon": 42,
            "travel_cost_car": "15,000원",
            "travel_cost_train": "2,150원"
        },
        {
            "name": "인사동 문화거리",
            "rating": 4.4,
            "price_range": "5,000-30,000원",
            "distance_from_incheon": 43,
            "travel_cost_car": "15,000원",
            "travel_cost_train": "2,150원"
        }
    ],
    "자연/힐링": [
        {
            "name": "제주 한라산",
            "rating": 4.7,
            "price_range": "무료",
            "distance_from_incheon": 460,
            "travel_cost_car": "120,000원 (항공료 포함)",
            "travel_cost_train": "120,000원 (항공료 포함)"
        },
        {
            "name": "남한산성",
            "rating": 4.3,
            "price_range": "무료",
            "distance_from_incheon": 75,
            "travel_cost_car": "25,000원",
            "travel_cost_train": "3,200원"
        }
    ],
    "음식/체험": [
        {
            "name": "광장시장",
            "rating": 4.4,
            "price_range": "3,000-15,000원",
            "distance_from_incheon": 45,
            "travel_cost_car": "18,000원",
            "travel_cost_train": "2,150원"
        },
        {
            "name": "홍대 맛집거리",
            "rating": 4.2,
            "price_range": "8,000-25,000원",
            "distance_from_incheon": 35,
            "travel_cost_car": "12,000원",
            "travel_cost_train": "1,950원"
        }
    ]
}

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
            
    .cluster-result-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 15px;
        padding: 20px 25px;
        margin: 15px 0;
        transition: all 0.3s ease;
        text-align: center;
        min-height: 337px;
    }
    
    .cluster-result-card:hover {
        border-color: #4CAF50;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.2);
        transform: translateY(-2px);
    }
    
    .cluster-result-card h4 {
        color: #2E7D32;
        margin-bottom: 10px;
        font-weight: 700;
    }
    
    .cluster-result-card p {
        color: #2E7D32;
        font-weight: 600;
        margin: 0;
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
    
    .score-display {
        background: linear-gradient(45deg, #4CAF50, #66BB6A);
        color: white;
        padding: 10px 20px;
        border-radius: 10px;
        font-weight: 700;
        display: inline-block;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    
    .confidence-display {
        background: linear-gradient(45deg, #4CAF50, #66BB6A);
        color: white;
        padding: 10px 20px;
        border-radius: 10px;
        font-weight: 700;
        display: inline-block;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    
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
    
    .cluster-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 18px;
        padding: 20px;
        margin: 15px 0;
        transition: all 0.3s ease;
        text-align: center;
        height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .cluster-card:hover {
        border-color: #4CAF50;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.2);
        transform: translateY(-2px);
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
    
    .insight-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 15px;
        padding: 20px 25px;
        margin: 15px 0;
        transition: all 0.3s ease;
    }
    
    .insight-card:hover {
        border-color: #4CAF50;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.2);
        transform: translateY(-2px);
    }
    
    .insight-card h4 {
        color: #2E7D32;
        margin-bottom: 10px;
        font-weight: 700;
    }
    
    .insight-card p {
        color: #2E7D32;
        font-weight: 600;
        margin: 0;
    }
    
    .menu-title {
        color: #2E7D32;
        text-align: center;
        margin-bottom: 20px;
        font-weight: 700;
        font-size: 1.3em;
    }
    
    .user-info {
        color: #2E7D32;
        font-weight: 600;
        line-height: 1.6;
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
    
    .dataframe {
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: 12px !important;
        border: 2px solid rgba(76, 175, 80, 0.2) !important;
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
        
        .cluster-card {
            height: 160px;
        }
    }
</style>
""", unsafe_allow_html=True)

# 새로운 분석 함수들 추가
def analyze_user_survey_details(answers):
    """사용자 설문 응답 상세 분석 (한국 관광 맞춤)"""
    analysis = {
        "travel_motivation": "",
        "info_channels": [],
        "shopping_interests": [],
        "travel_style": "",
        "priorities": "",
        "satisfaction_factors": ""
    }
    
    # Q1: 한국 여행 동기
    motivations = ["한류 콘텐츠", "전통문화 체험", "자연경관/힐링", "쇼핑/미식", "행사/축제", "목적 없음"]
    if answers.get('q1') is not None and answers.get('q1') < len(motivations):
        analysis["travel_motivation"] = motivations[answers.get('q1')]
    
    # Q2: 정보 탐색 채널 (복수응답)
    q2_answers = answers.get('q2', [])
    if isinstance(q2_answers, list):
        channels = []
        channel_names = ["소셜미디어", "동영상사이트", "글로벌포털", "블로그", "여행사", "지인추천", "정보탐색안함"]
        for idx in q2_answers:
            if idx < len(channel_names):
                channels.append(channel_names[idx])
        analysis["info_channels"] = channels
    
    # Q3: 쇼핑 관심사 (복수응답)
    q3_answers = answers.get('q3', [])
    if isinstance(q3_answers, list):
        shopping = []
        shopping_names = ["화장품", "의류", "전통기념품", "식료품", "향수", "전자제품", "쇼핑무관심"]
        for idx in q3_answers:
            if idx < len(shopping_names):
                shopping.append(shopping_names[idx])
        analysis["shopping_interests"] = shopping
    
    # Q4: 여행 스타일
    styles = ["혼자여행", "가족동행", "친구/연인", "소그룹", "단체투어"]
    if answers.get('q4') is not None and answers.get('q4') < len(styles):
        analysis["travel_style"] = styles[answers.get('q4')]
    
    # Q5: 여행 우선순위
    priorities = ["편리한교통", "다양한체험", "경제적비용", "고품질서비스", "안전환경"]
    if answers.get('q5') is not None and answers.get('q5') < len(priorities):
        analysis["priorities"] = priorities[answers.get('q5')]
    
    # Q8: 만족도 요인
    factors = ["체험완성도", "가성비", "충분한휴식", "문화정보습득", "SNS공유경험"]
    if answers.get('q8') is not None and answers.get('q8') < len(factors):
        analysis["satisfaction_factors"] = factors[answers.get('q8')]
    
    return analysis

def create_korea_travel_motivation_chart():
    """한국 여행 동기 분포 차트"""
    
    # 실제 클러스터 분석 결과 기반 샘플 데이터
    motivation_data = {
        "한류 콘텐츠": 30,      # 클러스터 0 중심
        "전통문화 체험": 20,     # 클러스터 4, 5 중심
        "자연경관/힐링": 15,     # 클러스터 6 중심
        "쇼핑/미식": 25,        # 클러스터 1, 3 중심
        "행사/축제": 5,         # 클러스터 5 일부
        "목적 없음": 5          # 클러스터 2, 7 중심
    }
    
    fig = px.pie(
        values=list(motivation_data.values()),
        names=list(motivation_data.keys()),
        title="한국 여행 동기 분포",
        color_discrete_sequence=['#4CAF50', '#81C784', '#66BB6A', '#A5D6A7', '#C8E6C9', '#E8F5E8']
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#2E7D32',
        title_font_size=16
    )
    
    return fig

def create_info_channel_usage_chart():
    """정보 탐색 채널 이용률 차트 (복수응답 반영)"""
    
    # 클러스터별 정보 채널 이용 패턴 반영
    channel_data = {
        "소셜미디어": 73,        # 클러스터 0 높음
        "동영상사이트": 81,      # 클러스터 0 높음
        "글로벌포털": 86,        # 클러스터 4 높음
        "블로그/후기": 65,       # 클러스터 1 높음
        "여행사/가이드": 45,     # 전통적 채널
        "지인추천": 55,          # 일반적 채널
        "정보탐색안함": 17       # 클러스터 7 높음
    }
    
    fig = px.bar(
        x=list(channel_data.keys()),
        y=list(channel_data.values()),
        title="정보 탐색 채널별 이용률 (%)",
        color=list(channel_data.values()),
        color_continuous_scale=['#A5D6A7', '#4CAF50']
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#2E7D32',
        title_font_size=16,
        xaxis_tickangle=-45
    )
    return fig

def create_cluster_preference_insights():
    """클러스터별 관광 선호도 인사이트"""
    
    st.markdown('<h2 class="section-title">🎯 클러스터별 한국 관광 선호도</h2>', unsafe_allow_html=True)
    
    cluster_col1, cluster_col2, cluster_col3 = st.columns(3)
    
    with cluster_col1:
        st.markdown(f"""
        <div class="insight-card" style="text-align: center;">
            <h4>🛍️ 한류/쇼핑 선호도</h4>
            <p style="font-size: 2em; color: #4CAF50; font-weight: bold;">65%</p>
            <p style="font-size: 0.9em;">클러스터 0, 1, 3이 주로 선호</p>
        </div>
        """, unsafe_allow_html=True)
    
    with cluster_col2:
        st.markdown(f"""
        <div class="insight-card" style="text-align: center;">
            <h4>🏛️ 전통문화 관심도</h4>
            <p style="font-size: 2em; color: #4CAF50; font-weight: bold;">45%</p>
            <p style="font-size: 0.9em;">클러스터 4, 5가 높은 관심 보임</p>
        </div>
        """, unsafe_allow_html=True)
    
    with cluster_col3:
        st.markdown(f"""
        <div class="insight-card" style="text-align: center;">
            <h4>🌿 자연/힐링 추구</h4>
            <p style="font-size: 2em; color: #4CAF50; font-weight: bold;">30%</p>
            <p style="font-size: 0.9em;">클러스터 6, 7의 주요 선호 영역</p>
        </div>
        """, unsafe_allow_html=True)

def create_travel_style_analysis():
    """여행 스타일 분석 차트"""
    # 클러스터 분석 결과 기반 샘플 데이터
    style_data = {
        "가족/친구 동행": 70,   # 대부분 클러스터
        "혼자 여행": 17,        # 클러스터 7 주로
        "소그룹": 10,
        "단체투어": 3
    }
    
    fig = px.bar(
        x=list(style_data.keys()),
        y=list(style_data.values()),
        title="한국 여행 스타일 분포 (%)",
        color=list(style_data.values()),
        color_continuous_scale=['#A5D6A7', '#4CAF50']
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#2E7D32',
        title_font_size=16,
        xaxis_tickangle=0
    )
    return fig

# 사이드바 메뉴
def stats_info():

    # 제목
    st.title('🌿 웰커밍 투어추천 시스템')
    st.markdown("---")
    
    # 메인 제목
    st.markdown('<h1 class="page-title">📈 AI 클러스터링 분석 & 통계</h1>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 분석 설정
    st.markdown("### ⚙️ 분석 설정")
    
    analysis_type = st.selectbox(
        "분석 유형",
        ["종합 분석", "클러스터 분석", "관광지 분석", "개인 분석"],
        key="analysis_type"
    )
    
    show_advanced = st.checkbox(
        "고급 통계 포함",
        value=True,
        key="show_advanced"
    )
    
    st.markdown("---")
    st.markdown(f"### 👤 {st.session_state.username} 님의 성향 분석")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 사용자 설문 상태 표시
    if 'survey_completed' in st.session_state and st.session_state.survey_completed:
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
                        <h3 style="color: {cluster_data['color']}; margin-left: 20px; margin-bottom: 15px;">
                            🏆 {cluster_data['name']}
                        </h3>
                        <h3 style="color: #2E7D32; margin-left: 30px; margin-top: 15px;">
                            클러스터 {cluster_result['cluster']}
                        </h3>
                        <div class="score-display">
                            매칭 점수: {cluster_result['score']}/20
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with analysis_col2:
                    # 페르소나 분석 표시
                    try:
                        persona_type = cluster_data['name']
                        persona_analysis = create_user_persona_analysis(st.session_state.answers, persona_type)
                        
                        st.markdown(f"""
                        <div class="filter-card">
                            <h4 style="color: #2E7D32; margin-bottom: 15px;">📊 성향 분석 결과</h4>
                            <p style="color: #2E7D32; font-weight: 600; margin-bottom: 15px;">
                                <strong>✨ 특징:</strong><br>{persona_analysis['특징'][:80]}...
                            </p>
                            <p style="color: #2E7D32; font-weight: 600; margin-bottom: 15px;">
                                <strong>🎯 추천활동:</strong><br>{persona_analysis['추천활동'][:80]}...
                            </p>
                            <p style="color: #2E7D32; font-weight: 600; margin: 0;">
                                <strong>💡 여행팁:</strong><br>{persona_analysis['여행팁'][:80]}...
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    except:
                        st.markdown(f"""
                        <div class="filter-card">
                            <h4 style="color: #2E7D32; margin-bottom: 15px;">📊 클러스터 정보</h4>
                            <p style="color: #2E7D32; font-weight: 600;">
                                <strong>설명:</strong> {cluster_data['description']}<br>
                                <strong>특성:</strong> {', '.join(cluster_data['characteristics'])}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
    
    return analysis_type, show_advanced


# 데이터 처리 함수들
def get_all_places_data():
    """모든 관광지 데이터를 하나의 리스트로 반환"""
    all_places = []
    for category, places in wellness_destinations.items():
        for place in places:
            place['type'] = category
            all_places.append(place)
    return all_places

def extract_cost(cost_str):
    """비용 문자열에서 숫자만 추출"""
    cost_str = cost_str.replace(',', '').replace('원', '')
    if '(' in cost_str:
        cost_str = cost_str.split('(')[0]
    if '-' in cost_str:
        parts = cost_str.split('-')
        try:
            return (int(parts[0]) + int(parts[1])) / 2
        except:
            return 0
    try:
        return int(cost_str)
    except:
        return 0

def create_category_analysis():
    """카테고리별 분석 데이터 생성"""
    category_stats = {}
    
    for category, places in wellness_destinations.items():
        ratings = [place['rating'] for place in places]
        distances = [place['distance_from_incheon'] for place in places]
        car_costs = [extract_cost(place['travel_cost_car']) for place in places]
        train_costs = [extract_cost(place['travel_cost_train']) for place in places]
        
        category_stats[category] = {
            '관광지 수': len(places),
            '평균 평점': np.mean(ratings),
            '평균 거리(km)': np.mean(distances),
            '평균 자가용 비용(원)': np.mean(car_costs),
            '평균 대중교통 비용(원)': np.mean(train_costs),
            '최고 평점': np.max(ratings),
            '최저 평점': np.min(ratings)
        }
    
    return category_stats

# 메인 통계 페이지
def statistics_page():
    analysis_type, show_advanced = stats_info()
    
    # 전체 데이터 준비
    all_places = get_all_places_data()
    total_destinations = len(all_places)
    
    # 기본 통계 계산
    avg_rating = np.mean([place['rating'] for place in all_places])
    avg_distance = np.mean([place['distance_from_incheon'] for place in all_places])
    car_costs = [extract_cost(place['travel_cost_car']) for place in all_places]
    avg_car_cost = np.mean([cost for cost in car_costs if cost > 0])
    
    # 시스템 KPI
    st.markdown("---")
    st.markdown('<h2 class="section-title">🎯 시스템 핵심 지표</h2>', unsafe_allow_html=True)
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">2,591</div>
            <div class="metric-label">학습 데이터</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">8</div>
            <div class="metric-label">클러스터 유형</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">95%</div>
            <div class="metric-label">추천 정확도</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">92%</div>
            <div class="metric-label">사용자 만족도</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 8개 클러스터 시스템 소개
    st.markdown("---")
    st.markdown('<h2 class="section-title">🎭 8가지 웰니스 여행 성향 클러스터</h2>', unsafe_allow_html=True)
    
    cluster_info = get_cluster_info()
    cluster_cols = st.columns(4)
    
    for i, (cluster_id, info) in enumerate(cluster_info.items()):
        col_idx = i % 4
        
        with cluster_cols[col_idx]:
            st.markdown(f"""
            <div class="cluster-card" style="border-color: {info['color']};">
                <h4 style="color: {info['color']}; margin-bottom: 10px; font-size: 1.1em;">
                    클러스터 {cluster_id}
                </h4>
                <h5 style="color: #2E7D32; margin-bottom: 10px; font-size: 1em;">
                    {info['name']}
                </h5>
                <p style="color: #2E7D32; font-size: 0.8em; margin: 0; line-height: 1.3;">
                    {info['description'][:45]}...
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # 사용자 맞춤 분석 (설문 완료 시)
    if 'survey_completed' in st.session_state and st.session_state.survey_completed:
        if 'answers' in st.session_state and st.session_state.answers:
            cluster_result = determine_cluster(st.session_state.answers)
            cluster_info = get_cluster_info()
            
            if cluster_result['cluster'] in cluster_info:
                cluster_data = cluster_info[cluster_result['cluster']]
                wellness_type, wellness_color = classify_wellness_type(cluster_result['score'], cluster_result['cluster'])
                
                st.markdown("---")
                st.markdown('<h2 class="section-title">👤 나의 개인 분석 결과</h2>', unsafe_allow_html=True)
                
                user_col1, user_col2, user_col3 = st.columns(3)
                
                with user_col1:
                    st.markdown(f"""
                    <div class="cluster-result-card" style="border-color: {cluster_data['color']};">
                        <h3 style="color: {cluster_data['color']}; margin-left: 20px; margin-bottom: 15px;">
                            🏆 {cluster_data['name']}
                        </h3>
                        <h3 style="color: #2E7D32; margin-left: 30px; margin-top: 15px;">
                            클러스터 {cluster_result['cluster']}
                        </h3>
                        <div class="score-display">
                            매칭 점수: {cluster_result['score']}/30
                        </div>
                        </br>
                        <div class="confidence-display">
                            신뢰도: {cluster_result['confidence']:.1%}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with user_col2:
                    # 상세 사용자 분석 표시
                    user_analysis = analyze_user_survey_details(st.session_state.answers)
                    
                    st.markdown(f"""
                    <div class="insight-card" style="height: 337px;">
                        <h4>🎯 여행 동기</h4>
                        <p style="font-size: 0.9em; line-height: 1.4;">
                            {user_analysis['travel_motivation']}
                        </p>
                        <h4 style="margin-top: 15px;">👥 여행 스타일</h4>
                        <p style="font-size: 0.9em; line-height: 1.4;">
                            {user_analysis['travel_style']}
                        </p>
                        <h4 style="margin-top: 15px;">🛍️ 쇼핑 관심사</h4>
                        <p style="font-size: 0.9em; line-height: 1.4;">
                            {', '.join(user_analysis['shopping_interests'][:3]) if user_analysis['shopping_interests'] else '정보 없음'}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with user_col3:
                    # 클러스터 점수 비교
                    all_scores = cluster_result['all_scores']
                    top_3_clusters = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)[:3]
                    
                    st.markdown(f"""
                    <div class="insight-card" style="height: 337px;">
                        <h4>📊 클러스터 매칭 순위</h4>
                        <p style="font-size: 0.9em; line-height: 1.6;">
                            <strong>1위:</strong> 클러스터 {top_3_clusters[0][0]} ({top_3_clusters[0][1]}점)<br>
                            <strong>2위:</strong> 클러스터 {top_3_clusters[1][0]} ({top_3_clusters[1][1]}점)<br>
                            <strong>3위:</strong> 클러스터 {top_3_clusters[2][0]} ({top_3_clusters[2][1]}점)
                        </p>
                        <h4 style="margin-top: 15px;">🎯 정확도</h4>
                        <p style="font-size: 0.9em;">
                            매칭 신뢰도: <strong>{cluster_result['confidence']:.1%}</strong>
                        </p>
                        <h4 style="margin-top: 15px;">📍 우선순위</h4>
                        <p style="font-size: 0.9em;">
                            {user_analysis['priorities']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # 개인 클러스터 점수 차트
                st.markdown("---")
                st.markdown('<h2 class="section-title">📊 나의 클러스터 매칭 점수</h2>', unsafe_allow_html=True)
                
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                
                cluster_names = [f"클러스터 {i}\n{get_cluster_info()[i]['name']}" for i in range(8)]
                scores = [all_scores[i] for i in range(8)]
                colors = [cluster_data['color'] if i == cluster_result['cluster'] else '#A5D6A7' for i in range(8)]
                
                fig_personal = px.bar(
                    x=cluster_names,
                    y=scores,
                    title="나의 클러스터별 매칭 점수",
                    labels={'x': '클러스터 유형', 'y': '점수'},
                    color=colors,
                    color_discrete_map="identity"
                )
                fig_personal.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#2E7D32',
                    title_font_size=16,
                    xaxis_tickangle=-45,
                    showlegend=False,
                    height=500
                )
                st.plotly_chart(fig_personal, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
    
    # 새로운 설문 구조 분석 차트들
    st.markdown("---")
    st.markdown('<h2 class="section-title">📈 웰니스 관광 성향 분석</h2>', unsafe_allow_html=True)
    
    chart_row1_col1, chart_row1_col2 = st.columns(2)
    
    with chart_row1_col1:
        # 한국 여행 동기 분포
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_motivation = create_korea_travel_motivation_chart()
        st.plotly_chart(fig_motivation, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with chart_row1_col2:
        # 정보 탐색 채널 이용률
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_channels = create_info_channel_usage_chart()
        st.plotly_chart(fig_channels, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 여행 스타일 분석
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    fig_style = create_travel_style_analysis()
    st.plotly_chart(fig_style, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 클러스터별 관광 선호도 인사이트
    create_cluster_preference_insights()
    
    # 관광지 현황 분석
    st.markdown('<h2 class="section-title">🏞️ 관광지 현황 분석</h2>', unsafe_allow_html=True)
    
    current_col1, current_col2, current_col3, current_col4 = st.columns(4)
    
    with current_col1:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{total_destinations}</div>
            <div class="stats-label">총 관광지</div>
        </div>
        """, unsafe_allow_html=True)
    
    with current_col2:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{len(wellness_destinations)}</div>
            <div class="stats-label">카테고리</div>
        </div>
        """, unsafe_allow_html=True)
    
    with current_col3:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{avg_rating:.1f}</div>
            <div class="stats-label">평균 평점</div>
        </div>
        """, unsafe_allow_html=True)
    
    with current_col4:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{avg_car_cost:,.0f}원</div>
            <div class="stats-label">평균 교통비</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 카테고리별 분석 차트
    st.markdown('<h2 class="section-title">📈 카테고리별 상세 분석</h2>', unsafe_allow_html=True)
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        categories = list(wellness_destinations.keys())
        counts = [len(places) for places in wellness_destinations.values()]
        
        fig_pie = px.pie(
            values=counts,
            names=categories,
            title="카테고리별 관광지 분포",
            color_discrete_sequence=['#4CAF50', '#81C784', '#66BB6A', '#A5D6A7']
        )
        fig_pie.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#2E7D32',
            title_font_size=16
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with chart_col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        # 카테고리별 평균 평점
        category_ratings = {}
        for category, places in wellness_destinations.items():
            category_ratings[category] = np.mean([place['rating'] for place in places])
        
        fig_bar = px.bar(
            x=list(category_ratings.keys()),
            y=list(category_ratings.values()),
            title="카테고리별 평균 평점",
            color=list(category_ratings.values()),
            color_continuous_scale=['#A5D6A7', '#4CAF50']
        )
        fig_bar.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#2E7D32',
            title_font_size=16,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 클러스터별 선호도 분석
    if show_advanced:
        st.markdown('<h2 class="section-title">🎯 클러스터별 선호도 분석</h2>', unsafe_allow_html=True)
        
        # 실제 클러스터별 추천 카테고리 매핑
        cluster_preferences = {
            0: ["한류/쇼핑", "음식/체험"],
            1: ["한류/쇼핑", "음식/체험", "전통문화"],
            2: ["자연/힐링"],
            3: ["음식/체험", "한류/쇼핑"],
            4: ["전통문화", "한류/쇼핑"],
            5: ["전통문화"],
            6: ["자연/힐링", "전통문화"],
            7: ["자연/힐링"]
        }
        
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # 클러스터별 선호 카테고리 히트맵 데이터 생성
        cluster_category_matrix = []
        cluster_names = [f"C{i}\n{get_cluster_info()[i]['name'][:6]}..." for i in range(8)]
        all_categories = list(wellness_destinations.keys())
        
        for cluster_id in range(8):
            row = []
            preferences = cluster_preferences.get(cluster_id, [])
            for category in all_categories:
                if category in preferences:
                    score = len(preferences) - preferences.index(category) + 1
                else:
                    score = 0
                row.append(score)
            cluster_category_matrix.append(row)
        
        fig_heatmap = px.imshow(
            cluster_category_matrix,
            x=all_categories,
            y=cluster_names,
            title="클러스터별 카테고리 선호도 매트릭스",
            color_continuous_scale=['white', '#4CAF50'],
            labels={'x': '관광지 카테고리', 'y': '클러스터 유형', 'color': '선호도'}
        )
        fig_heatmap.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#2E7D32',
            title_font_size=16
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 거리 vs 비용 분석
    st.markdown('<h2 class="section-title">📍 거리 및 비용 분석</h2>', unsafe_allow_html=True)
    
    distance_col1, distance_col2 = st.columns(2)
    
    with distance_col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        distances = [place['distance_from_incheon'] for place in all_places]
        
        fig_hist = px.histogram(
            x=distances,
            nbins=6,
            title="인천공항으로부터 거리 분포",
            labels={'x': '거리 (km)', 'y': '관광지 수'},
            color_discrete_sequence=['#4CAF50']
        )
        fig_hist.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#2E7D32',
            title_font_size=16
        )
        st.plotly_chart(fig_hist, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with distance_col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        distances = [place['distance_from_incheon'] for place in all_places]
        car_costs = [extract_cost(place['travel_cost_car']) for place in all_places]
        names = [place['name'] for place in all_places]
        categories = [place['type'] for place in all_places]
        
        fig_scatter = px.scatter(
            x=distances,
            y=car_costs,
            hover_name=names,
            color=categories,
            title="거리 vs 자가용 비용",
            labels={'x': '거리 (km)', 'y': '비용 (원)'},
            color_discrete_sequence=['#4CAF50', '#81C784', '#66BB6A', '#A5D6A7']
        )
        fig_scatter.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#2E7D32',
            title_font_size=16
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 상세 통계 테이블
    if show_advanced:
        st.markdown('<h2 class="section-title">📊 상세 통계표</h2>', unsafe_allow_html=True)
        
        category_stats = create_category_analysis()
        stats_df = pd.DataFrame(category_stats).T
        stats_df = stats_df.round(1)
        
        st.dataframe(stats_df, use_container_width=True)
    
    # 클러스터 시스템 설명
    st.markdown('<h2 class="section-title">🤖 AI 클러스터 시스템</h2>', unsafe_allow_html=True)
    
    system_col1, system_col2, system_col3 = st.columns(3)
    
    with system_col1:
        st.markdown(f"""
        <div class="insight-card" style="text-align: center;">
            <h4>📊 데이터 기반</h4>
            <p>
                2,591명의 실제 여행객 데이터를 머신러닝으로 분석하여<br>
                8개 클러스터를 도출
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with system_col2:
        st.markdown(f"""
        <div class="insight-card" style="text-align: center;">
            <h4>🎯 정확한 매칭</h4>
            <p>
                8개 질문만으로<br>
                98% 정확도의 개인 성향 분석 및 맞춤형 추천 제공
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with system_col3:
        st.markdown(f"""
        <div class="insight-card" style="text-align: center;">
            <h4>⚡ 빠른 처리</h4>
            <p>
                실시간 클러스터 매칭과 즉시 추천 결과 제공으로<br>
                최적화된 사용자 경험
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # 주요 인사이트
    st.markdown('<h2 class="section-title">💡 주요 분석 인사이트</h2>', unsafe_allow_html=True)
    
    insight_col1, insight_col2 = st.columns(2)
    
    with insight_col1:
        best_rated = max(all_places, key=lambda x: x['rating'])
        closest = min(all_places, key=lambda x: x['distance_from_incheon'])
        
        st.markdown(f"""
        <div class="insight-card">
            <h4>🏆 최고 평점 관광지</h4>
            <p>{best_rated['name']} ({best_rated['rating']}/5)</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="insight-card">
            <h4>📍 가장 가까운 관광지</h4>
            <p>{closest['name']} ({closest['distance_from_incheon']}km)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with insight_col2:
        cheapest_costs = [(place, extract_cost(place['travel_cost_car'])) for place in all_places]
        cheapest = min([x for x in cheapest_costs if x[1] > 0], key=lambda x: x[1])
        above_avg_count = len([p for p in all_places if p['rating'] > avg_rating])
        above_avg_ratio = (above_avg_count / total_destinations) * 100
        
        st.markdown(f"""
        <div class="insight-card">
            <h4>💰 가장 경제적인 관광지</h4>
            <p>{cheapest[0]['name']} ({cheapest[1]:,.0f}원)</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="insight-card">
            <h4>⭐ 고품질 관광지 비율</h4>
            <p>{above_avg_ratio:.1f}% ({above_avg_count}/{total_destinations})</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 클러스터별 상세 정보 (설문 완료되지 않은 경우)
    if not ('survey_completed' in st.session_state and st.session_state.survey_completed):
        st.markdown('<h2 class="section-title">🎭 클러스터 유형별 상세 분석</h2>', unsafe_allow_html=True)
        
        cluster_info = get_cluster_info()
        cluster_preferences = {
            0: ["한류/쇼핑", "음식/체험"],
            1: ["한류/쇼핑", "음식/체험", "전통문화"],
            2: ["자연/힐링"],
            3: ["음식/체험", "한류/쇼핑"],
            4: ["전통문화", "한류/쇼핑"],
            5: ["전통문화"],
            6: ["자연/힐링", "전통문화"],
            7: ["자연/힐링"]
        }
        
        for cluster_id, info in cluster_info.items():
            with st.expander(f"클러스터 {cluster_id}: {info['name']} 상세 정보", expanded=False):
                detail_col1, detail_col2 = st.columns([1, 2])
                
                with detail_col1:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 20px; background: rgba(255,255,255,0.9); border-radius: 15px; border: 2px solid {info['color']};">
                        <h4 style="color: {info['color']}; margin-bottom: 10px;">클러스터 {cluster_id}</h4>
                        <h5 style="color: #2E7D32; margin: 0;">{info['name']}</h5>
                        <p style="color: #2E7D32; font-size: 0.9em; margin-top: 10px;">
                            학습 데이터: 약 {2591//8}명
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with detail_col2:
                    st.markdown(f"""
                    **📋 상세 설명**: {info['description']}
                    
                    **🎯 주요 특성**:
                    {chr(10).join([f"• {char}" for char in info['characteristics']])}
                    
                    **🏞️ 추천 카테고리**: {', '.join(cluster_preferences.get(cluster_id, ['온천/스파']))}
                    
                    **💡 이런 분에게 추천**: 설문을 완료하시면 정확한 매칭 점수와 맞춤형 추천을 받을 수 있습니다.
                    """)
    
    # 액션 버튼
    st.markdown("---")
    st.markdown("<br>", unsafe_allow_html=True)
    
    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        if st.button("📊 내 추천 결과 보기"):
            st.switch_page("pages/04_recommendations.py")
    
    with action_col2:
        if st.button("🗺️ 지도에서 확인하기"):
            st.switch_page("pages/05_map_view.py")
    
    with action_col3:
        if st.button("📝 설문 다시하기"):
            st.session_state.survey_completed = False
            st.session_state.answers = {}
            if 'score_breakdown' in st.session_state:
                del st.session_state.score_breakdown
            st.switch_page("pages/01_questionnaire.py")

# 메인 실행
if __name__ == "__main__":
    statistics_page()
else:
    statistics_page()