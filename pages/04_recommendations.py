# pages/04_recommendations.py - 실제 CSV 데이터 기반 추천 결과

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import sys
import os

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from utils import (check_access_permissions, get_cluster_info, 
                      create_factor_analysis_chart, create_cluster_comparison_chart,
                      calculate_recommendations_by_cluster, questions, 
                      load_wellness_destinations, get_cluster_region_info,
                      apply_global_styles, export_recommendations_to_csv,
                      get_statistics_summary)
except ImportError as e:
    st.error(f"❌ 필수 모듈을 불러올 수 없습니다: {e}")
    st.info("💡 `utils.py` 파일이 올바른 위치에 있는지 확인해주세요.")
    st.stop()

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
apply_global_styles()

# 추천 결과 페이지 전용 CSS
st.markdown("""
<style>
    /* 메인 제목 */
    .main-title {
        color: var(--primary-dark) !important;
        text-align: center;
        background: var(--card-bg);
        padding: 30px 40px;
        border-radius: 30px;
        font-size: 3.2em !important;
        margin-bottom: 40px;
        font-weight: 800 !important;
        border: 3px solid var(--primary);
        box-shadow: 0 20px 60px rgba(76, 175, 80, 0.2);
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        letter-spacing: 1px;
        position: relative;
        overflow: hidden;
    }
    
    .main-title::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 6px;
        background: linear-gradient(45deg, var(--primary), var(--secondary));
        border-radius: 30px 30px 0 0;
    }
            
    /* 클러스터 결과 카드 */
    .cluster-result-card {
        background: var(--card-bg);
        backdrop-filter: blur(25px);
        border: 3px solid rgba(76, 175, 80, 0.4);
        border-radius: 25px;
        padding: 40px;
        margin: 30px 0;
        text-align: center;
        box-shadow: 0 20px 60px rgba(76, 175, 80, 0.15);
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
    }
    
    .cluster-result-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 25px 70px rgba(76, 175, 80, 0.25);
        border-color: var(--primary);
    }
    
    .cluster-result-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 6px;
        background: linear-gradient(45deg, var(--primary), var(--secondary));
        border-radius: 25px 25px 0 0;
    }
    
    /* 추천 카드 */
    .recommendation-card {
        background: var(--card-bg);
        backdrop-filter: blur(25px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 25px;
        padding: 35px;
        margin: 25px 0;
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
    }
    
    .recommendation-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 60px rgba(76, 175, 80, 0.25);
        background: rgba(255, 255, 255, 1);
        border-color: var(--primary);
    }
    
    .recommendation-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 6px;
        background: linear-gradient(45deg, var(--primary), var(--secondary));
        border-radius: 25px 25px 0 0;
    }
    
    /* 랭킹 배지 */
    .ranking-badge {
        position: absolute;
        top: -15px;
        right: 25px;
        background: linear-gradient(45deg, var(--primary), var(--secondary));
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
        color: var(--primary-dark) !important;
        font-size: 2.4em;
        font-weight: 700;
        margin: 50px 0 30px 0;
        text-align: center;
        background: var(--card-bg);
        padding: 25px 35px;
        border-radius: 25px;
        border-left: 6px solid var(--primary);
        box-shadow: 0 10px 30px rgba(76, 175, 80, 0.15);
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    /* 분석 카드 */
    .analysis-card {
        background: var(--card-bg);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 20px;
        padding: 30px;
        margin: 25px 0;
        transition: all 0.3s ease;
    }
    
    .analysis-card:hover {
        border-color: var(--primary);
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.2);
        transform: translateY(-3px);
    }
    
    /* 차트 컨테이너 */
    .chart-container {
        background: var(--card-bg);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 25px;
        padding: 30px;
        margin: 25px 0;
        box-shadow: var(--shadow);
    }
    
    .chart-container:hover {
        border-color: var(--primary);
        box-shadow: var(--shadow-hover);
    }
    
    /* 정보 태그 */
    .info-tag {
        background: rgba(76, 175, 80, 0.15);
        border: 2px solid rgba(76, 175, 80, 0.3);
        border-radius: 15px;
        padding: 10px 18px;
        margin: 8px 5px;
        display: inline-block;
        color: var(--primary-dark);
        font-size: 0.95em;
        font-weight: 700;
        transition: all 0.3s ease;
    }
    
    .info-tag:hover {
        background: rgba(76, 175, 80, 0.25);
        border-color: var(--primary);
        transform: translateY(-2px);
    }
    
    /* 메트릭 카드 */
    .metric-card {
        background: var(--card-bg);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 20px;
        padding: 30px 20px;
        text-align: center;
        margin: 20px 0;
        transition: all 0.3s ease;
        height: 160px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .metric-card:hover {
        border-color: var(--primary);
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.25);
        transform: translateY(-3px);
        background: rgba(255, 255, 255, 1);
    }
    
    .metric-number {
        font-size: 3.2em;
        font-weight: 800;
        color: var(--primary-dark);
        margin-bottom: 10px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    .metric-label {
        color: var(--primary-dark);
        font-size: 1.3em;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    /* 지역 클러스터 카드 */
    .region-cluster-card {
        background: linear-gradient(135deg, var(--card-bg), rgba(232, 245, 232, 0.9));
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 20px;
        padding: 25px;
        margin: 20px 0;
        transition: all 0.3s ease;
    }
    
    .region-cluster-card:hover {
        border-color: var(--primary);
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.2);
    }
    
    /* 다운로드 섹션 */
    .download-section {
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), var(--card-bg));
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 25px;
        padding: 35px;
        margin: 30px 0;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .download-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 6px;
        background: linear-gradient(45deg, var(--primary), var(--secondary));
        border-radius: 25px 25px 0 0;
    }
    
    /* 관광지 상세 정보 */
    .destination-detail {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        border-left: 4px solid var(--primary);
    }
    
    .destination-rating {
        background: linear-gradient(45deg, #FF6B6B, #FF8E53);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
        margin: 5px;
        box-shadow: 0 3px 10px rgba(255, 107, 107, 0.3);
    }
    
    .destination-price {
        background: linear-gradient(45deg, #4CAF50, #66BB6A);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
        margin: 5px;
        box-shadow: 0 3px 10px rgba(76, 175, 80, 0.3);
    }
    
    .destination-distance {
        background: linear-gradient(45deg, #2196F3, #42A5F5);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
        margin: 5px;
        box-shadow: 0 3px 10px rgba(33, 150, 243, 0.3);
    }
</style>
""", unsafe_allow_html=True)

def create_region_distribution_chart(recommendations):
    """지역별 추천 분포 차트"""
    if not recommendations:
        return None
        
    # 클러스터별 개수 계산
    cluster_counts = {}
    cluster_region_info = get_cluster_region_info()
    
    for place in recommendations:
        cluster_id = place.get('cluster_region', 1)
        if cluster_id in cluster_region_info:
            region_name = cluster_region_info[cluster_id]['name']
            cluster_counts[region_name] = cluster_counts.get(region_name, 0) + 1
    
    if not cluster_counts:
        return None
    
    fig = px.bar(
        x=list(cluster_counts.keys()),
        y=list(cluster_counts.values()),
        title="지역별 추천 관광지 분포",
        color=list(cluster_counts.values()),
        color_continuous_scale=['#E8F5E8', '#4CAF50', '#2E7D32']
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#2E7D32',
        title_font_size=16,
        xaxis_tickangle=-45,
        height=400,
        showlegend=False
    )
    
    return fig

def create_price_rating_scatter(recommendations):
    """가격대별 평점 산점도"""
    if not recommendations:
        return None
    
    # 가격 데이터 정리
    price_numeric = []
    ratings = []
    names = []
    types = []
    
    for place in recommendations:
        try:
            price_str = place['price_range']
            if '무료' in price_str:
                price_avg = 0
            else:
                # 가격 범위에서 평균값 계산
                prices = [int(p.replace(',', '').replace('원', '')) for p in price_str.split('-') if p.replace(',', '').replace('원', '').isdigit()]
                price_avg = sum(prices) / len(prices) if prices else 50000
            
            price_numeric.append(price_avg)
            ratings.append(place['rating'])
            names.append(place['name'])
            types.append(place['type'])
            
        except:
            continue
    
    if not price_numeric:
        return None
    
    fig = px.scatter(
        x=price_numeric,
        y=ratings,
        color=types,
        size=[50] * len(price_numeric),
        hover_name=names,
        title="가격대별 평점 분석",
        labels={'x': '평균 가격 (원)', 'y': '평점 (10점 만점)'}
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#2E7D32',
        height=500
    )
    
    return fig

def render_cluster_analysis_result():
    """클러스터 분석 결과 렌더링"""
    if 'cluster_result' not in st.session_state or 'factor_scores' not in st.session_state:
        return None
        
    cluster_result = st.session_state.cluster_result
    factor_scores = st.session_state.factor_scores
    cluster_info = get_cluster_info()
    user_cluster = cluster_result['cluster']
    cluster_data = cluster_info[user_cluster]
    
    st.markdown('<h2 class="section-title">🎭 당신의 여행 성향 클러스터</h2>', unsafe_allow_html=True)
    
    result_col1, result_col2 = st.columns([1, 1])
    
    with result_col1:
        st.markdown(f"""
        <div class="cluster-result-card" style="border-color: {cluster_data['color']};">
            <h3 style="color: {cluster_data['color']}; font-size: 2.2em; margin-bottom: 20px;">
                🏆 {cluster_data['name']}
            </h3>
            <h4 style="color: #666; margin-bottom: 20px; font-size: 1.4em;">
                {cluster_data['english_name']}
            </h4>
            <div style="background: linear-gradient(45deg, {cluster_data['color']}, {cluster_data['color']}80); 
                        color: white; padding: 18px 28px; border-radius: 25px; display: inline-block; 
                        margin: 20px 0; font-weight: 800; font-size: 1.3em; 
                        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.4);">
                매칭 신뢰도: {cluster_result['confidence']:.1%}
            </div>
            <p style="color: #2E7D32; font-weight: 600; margin-top: 25px; line-height: 1.8; font-size: 1.1em;">
                {cluster_data['description']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with result_col2:
        st.markdown(f"""
        <div class="analysis-card">
            <h4 style="color: #2E7D32; margin-bottom: 20px; font-size: 1.4em;">📊 클러스터 특성 분석</h4>
            <div style="display: flex; flex-wrap: wrap; gap: 12px; margin: 20px 0; justify-content: center;">
                {' '.join([f'<span class="info-tag">{char}</span>' for char in cluster_data['characteristics']])}
            </div>
            <hr style="margin: 25px 0; border-color: #4CAF50;">
            <div style="text-align: left;">
                <p style="color: #2E7D32; font-weight: 600; margin: 12px 0; font-size: 1.1em;">
                    <strong>📈 전체 비율:</strong> {cluster_data['percentage']}% ({cluster_data['count']:,}명)
                </p>
                <p style="color: #2E7D32; font-weight: 600; margin: 12px 0; font-size: 1.1em;">
                    <strong>🎯 주요 키워드:</strong> 
                    {', '.join(list(cluster_data['key_factors'].keys())[:3])}
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    return cluster_result

def render_factor_analysis():
    """12개 요인 분석 렌더링"""
    if 'factor_scores' not in st.session_state:
        return
        
    factor_scores = st.session_state.factor_scores
    cluster_result = st.session_state.cluster_result
    user_cluster = cluster_result['cluster']
    
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

def render_wellness_recommendations():
    """실제 CSV 데이터 기반 웰니스 관광지 추천"""
    if 'cluster_result' not in st.session_state:
        return []
        
    cluster_result = st.session_state.cluster_result
    
    # 실제 추천 계산
    try:
        recommended_places = calculate_recommendations_by_cluster(cluster_result)
        
        if not recommended_places:
            st.warning("⚠️ 추천 관광지를 찾을 수 없습니다.")
            return []
            
    except Exception as e:
        st.error(f"❌ 추천 계산 중 오류: {str(e)}")
        return []
    
    st.markdown('<h2 class="section-title">🏞️ 맞춤형 한국 웰니스 관광지 추천</h2>', unsafe_allow_html=True)
    
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
    
    return recommended_places

def render_top_recommendations(recommended_places):
    """상위 추천 관광지 상세 표시"""
    if not recommended_places:
        return
        
    st.markdown('<h2 class="section-title">🎯 상위 추천 관광지</h2>', unsafe_allow_html=True)
    
    # 상위 8개 관광지 표시
    for i, place in enumerate(recommended_places[:8]):
        with st.container():
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

def render_analysis_charts(recommended_places):
    """분석 차트 렌더링"""
    if not recommended_places:
        return
        
    st.markdown('<h2 class="section-title">📈 추천 결과 상세 분석</h2>', unsafe_allow_html=True)
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        region_chart = create_region_distribution_chart(recommended_places)
        if region_chart:
            st.plotly_chart(region_chart, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("지역별 분포 데이터가 부족합니다.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with chart_col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        price_chart = create_price_rating_scatter(recommended_places)
        if price_chart:
            st.plotly_chart(price_chart, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("가격-평점 분석 데이터가 부족합니다.")
        st.markdown('</div>', unsafe_allow_html=True)

def render_download_section(recommended_places, cluster_result):
    """다운로드 섹션"""
    st.markdown('<h2 class="section-title">📥 결과 다운로드</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="download-section">
        <h4 style="color: #2E7D32; margin-bottom: 20px; font-size: 1.6em;">📊 개인 맞춤 추천 결과 저장</h4>
        <p style="color: #666; margin-bottom: 25px; font-size: 1.1em; line-height: 1.6;">
            12개 요인 분석 결과와 맞춤형 관광지 추천 리스트를 CSV 파일로 다운로드하여<br>
            여행 계획 수립과 일정 관리에 활용하세요.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    download_col1, download_col2, download_col3 = st.columns([1, 1, 1])
    
    with download_col2:
        if st.button("📄 상세 추천 리스트 다운로드", key="download_recommendations", use_container_width=True):
            try:
                # 사용자 정보 및 클러스터 정보 준비
                cluster_info = get_cluster_info()
                user_info = {
                    'username': st.session_state.get('username', '익명'),
                    'cluster_name': cluster_info[cluster_result['cluster']]['name'],
                    'cluster_id': cluster_result['cluster'],
                    'confidence': cluster_result['confidence'],
                    'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # CSV 데이터 생성
                csv_data = export_recommendations_to_csv(recommended_places, user_info)
                
                if csv_data:
                    st.download_button(
                        label="💾 CSV 파일 저장",
                        data=csv_data,
                        file_name=f"wellness_recommendations_{st.session_state.get('username', 'user')}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key="download_csv_file"
                    )
                    st.success("✅ 다운로드가 준비되었습니다!")
                else:
                    st.error("❌ 파일 생성 중 오류가 발생했습니다.")
                    
            except Exception as e:
                st.error(f"❌ 다운로드 준비 중 오류: {str(e)}")

def render_survey_summary():
    """설문 응답 요약"""
    if 'answers' not in st.session_state:
        return
        
    with st.expander("📋 나의 설문 응답 요약", expanded=False):
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
    
def recommendations_page():
    """메인 추천 결과 페이지"""
    
    # 제목
    st.markdown('<h1 class="main-title">🎯 12개 요인 기반 성향 분석 결과</h1>', unsafe_allow_html=True)
    
    # 클러스터 분석 결과 표시
    cluster_result = render_cluster_analysis_result()
    if not cluster_result:
        st.error("❌ 분석 결과가 없습니다. 설문을 다시 진행해주세요.")
        if st.button("📝 설문하러 가기"):
            st.switch_page("pages/01_questionnaire.py")
        return
    
    # 12개 요인 분석
    render_factor_analysis()
    
    # 웰니스 관광지 추천
    recommended_places = render_wellness_recommendations()
    
    if recommended_places:
        # 상위 추천 관광지 상세 표시
        render_top_recommendations(recommended_places)
        
        # 분석 차트
        render_analysis_charts(recommended_places)
        
        # 다운로드 섹션
        render_download_section(recommended_places, cluster_result)
    
    # 설문 응답 요약
    render_survey_summary()
    
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
    recommendations_page()# pages/04_recommendations.py - 실제 CSV 데이터 기반 추천 결과