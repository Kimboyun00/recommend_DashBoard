import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils import (check_access_permissions, get_cluster_info, 
                  create_factor_analysis_chart, create_cluster_comparison_chart,
                  calculate_recommendations_by_cluster, questions)

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
    page_title="12개 요인 분석 결과",
    page_icon="🎯",
    layout="wide"
)

# 접근 권한 확인
check_access_permissions()

# 고급 CSS 스타일링
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
    
    /* 메인 제목 */
    .main-title {
        color: #2E7D32 !important;
        text-align: center;
        background: rgba(255, 255, 255, 0.95);
        padding: 25px 30px;
        border-radius: 25px;
        font-size: 2.8em !important;
        margin-bottom: 40px;
        font-weight: 800 !important;
        border: 3px solid #4CAF50;
        box-shadow: 0 15px 40px rgba(76, 175, 80, 0.2);
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        letter-spacing: 1px;
    }
    
    /* 클러스터 결과 카드 */
    .cluster-result-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(25px);
        border: 3px solid rgba(76, 175, 80, 0.4);
        border-radius: 25px;
        padding: 35px;
        margin: 25px 0;
        text-align: center;
        box-shadow: 0 20px 60px rgba(76, 175, 80, 0.15);
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
    }
    
    .cluster-result-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 25px 70px rgba(76, 175, 80, 0.25);
        border-color: #4CAF50;
    }
    
    .cluster-result-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 6px;
        background: linear-gradient(45deg, #4CAF50, #66BB6A);
        border-radius: 25px 25px 0 0;
    }
    
    /* 점수 표시 */
    .score-display {
        background: linear-gradient(45deg, #4CAF50, #66BB6A);
        color: white;
        padding: 15px 25px;
        border-radius: 20px;
        font-weight: 800;
        display: inline-block;
        margin: 20px 0;
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.4);
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        font-size: 1.2em;
    }
    
    .confidence-display {
        background: linear-gradient(45deg, #2E7D32, #4CAF50);
        color: white;
        padding: 10px 20px;
        border-radius: 15px;
        font-weight: 700;
        display: inline-block;
        margin: 10px 0;
        box-shadow: 0 6px 20px rgba(46, 125, 50, 0.3);
        font-size: 1.1em;
    }
    
    /* 추천 카드 */
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
    
    /* 랭킹 배지 */
    .ranking-badge {
        position: absolute;
        top: -15px;
        right: 25px;
        background: linear-gradient(45deg, #4CAF50, #66BB6A);
        color: white;
        padding: 12px 20px;
        border-radius: 25px;
        font-weight: 800;
        font-size: 16px;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    
    /* 섹션 제목 */
    .section-title {
        color: #2E7D32 !important;
        font-size: 2.2em;
        font-weight: 700;
        margin: 50px 0 30px 0;
        text-align: center;
        background: rgba(255, 255, 255, 0.9);
        padding: 20px 30px;
        border-radius: 20px;
        border-left: 6px solid #4CAF50;
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.15);
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    /* 분석 카드 */
    .analysis-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 20px;
        padding: 25px 30px;
        margin: 25px 0;
        transition: all 0.3s ease;
    }
    
    .analysis-card:hover {
        border-color: #4CAF50;
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.2);
        transform: translateY(-3px);
    }
    
    /* 차트 컨테이너 */
    .chart-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 25px;
        padding: 30px;
        margin: 25px 0;
        box-shadow: 0 10px 30px rgba(76, 175, 80, 0.1);
    }
    
    .chart-container:hover {
        border-color: #4CAF50;
        box-shadow: 0 15px 40px rgba(76, 175, 80, 0.2);
    }
    
    /* 정보 태그 */
    .info-tag {
        background: rgba(76, 175, 80, 0.15);
        border: 2px solid rgba(76, 175, 80, 0.3);
        border-radius: 15px;
        padding: 10px 18px;
        margin: 8px 5px;
        display: inline-block;
        color: #2E7D32;
        font-size: 0.95em;
        font-weight: 700;
        transition: all 0.3s ease;
    }
    
    .info-tag:hover {
        background: rgba(76, 175, 80, 0.25);
        border-color: #4CAF50;
        transform: translateY(-2px);
    }
    
    /* 특성 리스트 */
    .characteristics-list {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 15px 0;
        justify-content: center;
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
    
    /* 메트릭 카드 */
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 20px;
        padding: 25px 20px;
        text-align: center;
        margin: 15px 0;
        transition: all 0.3s ease;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .metric-card:hover {
        border-color: #4CAF50;
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.25);
        transform: translateY(-3px);
        background: rgba(255, 255, 255, 1);
    }
    
    .metric-number {
        font-size: 2.8em;
        font-weight: 800;
        color: #2E7D32;
        margin-bottom: 8px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    .metric-label {
        color: #2E7D32;
        font-size: 1.2em;
        font-weight: 600;
        letter-spacing: 0.5px;
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
        
        .main-title {
            font-size: 2.2em !important;
            padding: 20px 25px !important;
        }
        
        .recommendation-card {
            padding: 20px;
            margin: 15px 0;
        }
        
        .section-title {
            font-size: 1.8em;
            padding: 15px 20px;
        }
        
        .cluster-result-card {
            padding: 25px 20px;
        }
    }
</style>
""", unsafe_allow_html=True)

def recommendations_page():
    """12개 요인 기반 추천 결과 페이지"""
    
    # 제목
    st.markdown('<h1 class="main-title">🎯 12개 요인 기반 성향 분석 결과</h1>', unsafe_allow_html=True)
    
    # 데이터 확인
    if 'cluster_result' not in st.session_state:
        st.error("❌ 분석 결과가 없습니다. 설문을 다시 진행해주세요.")
        if st.button("📝 설문하러 가기"):
            st.switch_page("pages/01_questionnaire.py")
        return
    
    cluster_result = st.session_state.cluster_result
    factor_scores = st.session_state.factor_scores
    cluster_info = get_cluster_info()
    user_cluster = cluster_result['cluster']
    cluster_data = cluster_info[user_cluster]
    
    # 클러스터 분석 결과 표시
    st.markdown('<h2 class="section-title">🎭 당신의 여행 성향 클러스터</h2>', unsafe_allow_html=True)
    
    result_col1, result_col2 = st.columns([1, 1])
    
    with result_col1:
        st.markdown(f"""
        <div class="cluster-result-card" style="border-color: {cluster_data['color']};">
            <h3 style="color: {cluster_data['color']}; font-size: 1.8em; margin-bottom: 20px;">
                🏆 {cluster_data['name']}
            </h3>
            <h4 style="color: #666; margin-bottom: 15px;">
                {cluster_data['english_name']}
            </h4>
            <div class="score-display">
                매칭 신뢰도: {cluster_result['confidence']:.1%}
            </div>
            <div class="confidence-display">
                클러스터 {user_cluster} / 8개 유형
            </div>
            <p style="color: #2E7D32; font-weight: 600; margin-top: 20px; line-height: 1.6;">
                {cluster_data['description']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with result_col2:
        st.markdown(f"""
        <div class="analysis-card">
            <h4 style="color: #2E7D32; margin-bottom: 20px;">📊 클러스터 특성 분석</h4>
            <div class="characteristics-list">
                {' '.join([f'<span class="info-tag">{char}</span>' for char in cluster_data['characteristics']])}
            </div>
            <hr style="margin: 20px 0; border-color: #4CAF50;">
            <div style="text-align: left;">
                <p style="color: #2E7D32; font-weight: 600;">
                    <strong>📈 전체 비율:</strong> {cluster_data['percentage']}% ({cluster_data['count']:,}명)
                </p>
                <p style="color: #2E7D32; font-weight: 600;">
                    <strong>🎯 주요 키워드:</strong> 
                    {', '.join(list(cluster_data['key_factors'].keys())[:3])}
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 12개 요인 점수 시각화
    st.markdown('<h2 class="section-title">📊 12개 요인별 개인 분석</h2>', unsafe_allow_html=True)
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        factor_chart = create_factor_analysis_chart(factor_scores)
        st.plotly_chart(factor_chart, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)
    
    with chart_col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        comparison_chart = create_cluster_comparison_chart(user_cluster, factor_scores)
        st.plotly_chart(comparison_chart, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 요인별 세부 분석
    st.markdown('<h2 class="section-title">🔍 요인별 세부 분석</h2>', unsafe_allow_html=True)
    
    factor_col1, factor_col2 = st.columns(2)
    
    # 상위 요인들
    sorted_factors = sorted(factor_scores.items(), key=lambda x: abs(x[1]), reverse=True)
    top_factors = sorted_factors[:6]
    
    with factor_col1:
        st.markdown("""
        <div class="analysis-card">
            <h4 style="color: #2E7D32;">🔝 주요 특성 요인</h4>
        """, unsafe_allow_html=True)
        
        for i, (factor, score) in enumerate(top_factors[:3]):
            factor_num = factor.replace('요인', '')
            factor_names = {
                "1": "계획적 정보 추구", "2": "쇼핑 중심", "3": "여행 경험", 
                "4": "현지 탐색", "5": "편의 인프라", "6": "전통문화 안전",
                "7": "패션 쇼핑", "8": "프리미엄 사회적", "9": "성별 기반 쇼핑",
                "10": "디지털 미디어", "11": "절차 자연관광", "12": "교통 미식"
            }
            
            factor_name = factor_names.get(factor_num, f"요인{factor_num}")
            intensity = "높음" if score > 0 else "낮음"
            color = "#4CAF50" if score > 0 else "#FF7043"
            
            st.markdown(f"""
            <div style="margin: 15px 0; padding: 15px; background: rgba(76, 175, 80, 0.1); border-radius: 10px;">
                <strong style="color: {color};">{factor_name}</strong><br>
                <span style="color: #666;">점수: {score:.2f} ({intensity})</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with factor_col2:
        st.markdown("""
        <div class="analysis-card">
            <h4 style="color: #2E7D32;">📈 클러스터 매칭 분석</h4>
        """, unsafe_allow_html=True)
        
        # 다른 클러스터와의 유사도 표시
        similarities = cluster_result['similarities']
        sorted_similarities = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
        
        for i, (cluster_id, similarity) in enumerate(sorted_similarities[:3]):
            other_cluster = cluster_info[cluster_id]
            is_current = cluster_id == user_cluster
            
            st.markdown(f"""
            <div style="margin: 15px 0; padding: 15px; background: {'rgba(76, 175, 80, 0.2)' if is_current else 'rgba(76, 175, 80, 0.05)'}; border-radius: 10px;">
                <strong style="color: {other_cluster['color']};">
                    {'🎯 ' if is_current else f'{i+1}. '}{other_cluster['name']}
                </strong><br>
                <span style="color: #666;">유사도: {similarity:.1%}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 맞춤형 관광지 추천
    st.markdown('<h2 class="section-title">🏞️ 맞춤형 한국 관광지 추천</h2>', unsafe_allow_html=True)
    
    recommended_places = calculate_recommendations_by_cluster(cluster_result)
    
    # 추천 통계
    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
    
    with metrics_col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{len(recommended_places)}</div>
            <div class="metric-label">추천 관광지</div>
        </div>
        """, unsafe_allow_html=True)
    
    with metrics_col2:
        cluster_matches = sum(1 for place in recommended_places if place.get('cluster_match', False))
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{cluster_matches}</div>
            <div class="metric-label">완벽 매칭</div>
        </div>
        """, unsafe_allow_html=True)
    
    with metrics_col3:
        avg_score = np.mean([place['recommendation_score'] for place in recommended_places])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{avg_score:.0f}</div>
            <div class="metric-label">평균 점수</div>
        </div>
        """, unsafe_allow_html=True)
    
    with metrics_col4:
        avg_rating = np.mean([place['rating'] for place in recommended_places])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{avg_rating:.1f}</div>
            <div class="metric-label">평균 평점</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 추천 관광지 리스트
    st.markdown('<h2 class="section-title">🎯 상위 추천 관광지</h2>', unsafe_allow_html=True)
    
    for i, place in enumerate(recommended_places[:6]):
        with st.container():
            st.markdown(f"""
            <div class="recommendation-card">
                <div class="ranking-badge">#{i+1}</div>
                <div style="display: flex; align-items: center; margin: 20px 0;">
                    <div style="font-size: 4em; margin-right: 30px;">{place['image_url']}</div>
                    <div style="flex: 1;">
                        <h3 style="color: #2E7D32; margin: 0 0 10px 0; font-size: 1.6em;">{place['name']}</h3>
                        <p style="color: #666; margin: 0 0 15px 0; line-height: 1.6;">{place['description']}</p>
                        <div style="display: flex; flex-wrap: wrap; gap: 10px; margin: 15px 0;">
                            <span class="info-tag">⭐ {place['rating']}/5</span>
                            <span class="info-tag">💰 {place['price_range']}</span>
                            <span class="info-tag">🏷️ {place['type']}</span>
                            <span class="info-tag">🎯 {place['recommendation_score']:.0f}점</span>
                            {'<span class="info-tag" style="background: rgba(76, 175, 80, 0.3);">✅ 완벽매칭</span>' if place.get('cluster_match') else ''}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # 설문 응답 요약
    with st.expander("📋 나의 설문 응답 요약", expanded=False):
        if 'answers' in st.session_state:
            response_col1, response_col2 = st.columns(2)
            
            with response_col1:
                st.markdown("### 📝 응답 내역 (1-6번)")
                for i, (q_key, answer_idx) in enumerate(list(st.session_state.answers.items())[:6]):
                    if q_key in questions and answer_idx is not None:
                        question_data = questions[q_key]
                        answer_text = question_data['options'][answer_idx]
                        st.markdown(f"**Q{i+1}:** {answer_text}")
            
            with response_col2:
                st.markdown("### 📝 응답 내역 (7-12번)")
                for i, (q_key, answer_idx) in enumerate(list(st.session_state.answers.items())[6:]):
                    if q_key in questions and answer_idx is not None:
                        question_data = questions[q_key]
                        answer_text = question_data['options'][answer_idx]
                        st.markdown(f"**Q{i+7}:** {answer_text}")
    
    # 액션 버튼
    st.markdown("---")
    st.markdown('<h2 class="section-title">🎯 다음 단계</h2>', unsafe_allow_html=True)
    
    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        if st.button("🗺️ 지도에서 관광지 보기"):
            st.switch_page("pages/05_map_view.py")
    
    with action_col2:
        if st.button("📈 상세 통계 분석"):
            st.switch_page("pages/06_statistics.py")
    
    with action_col3:
        if st.button("📝 설문 다시하기"):
            # 세션 상태 클리어
            for key in ['survey_completed', 'answers', 'factor_scores', 'cluster_result']:
                if key in st.session_state:
                    del st.session_state[key]
            st.switch_page("pages/01_questionnaire.py")

# 메인 실행
if __name__ == "__main__":
    recommendations_page()
else:
    recommendations_page()