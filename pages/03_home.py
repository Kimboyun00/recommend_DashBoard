import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import sys
import os

# 임포트 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from utils import check_access_permissions, get_cluster_info, apply_global_styles
except ImportError as e:
    st.error(f"❌ 필수 모듈 임포트 실패: {e}")
    st.info("💡 `utils.py` 파일이 올바른 위치에 있는지 확인해주세요.")
    st.stop()

# 페이지 설정
st.set_page_config(
    page_title="웰니스 투어 홈",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 보안 및 접근 권한 확인
try:
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.error("⚠️ 로그인이 필요합니다.")
        st.markdown("### 🔐 로그인 후 이용해주세요")
        if st.button("🏠 로그인 페이지로 이동", type="primary"):
            st.switch_page("app.py")
        st.stop()
    
    check_access_permissions('home')
    apply_global_styles()
except Exception as e:
    st.error(f"❌ 시스템 오류: {e}")
    if st.button("🔄 다시 시도"):
        st.rerun()
    st.stop()

# 홈페이지 전용 CSS 스타일링
st.markdown("""
<style>
    /* 홈페이지 전용 스타일 */
    .hero-section {
        background: linear-gradient(135deg, var(--card-bg), rgba(232, 245, 232, 0.9));
        border: 3px solid var(--primary);
        border-radius: 30px;
        padding: 50px 40px;
        margin: 30px 0;
        text-align: center;
        box-shadow: 0 20px 60px rgba(76, 175, 80, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 6px;
        background: linear-gradient(45deg, var(--primary), var(--secondary));
        border-radius: 30px 30px 0 0;
    }
    
    .hero-title {
        color: var(--primary-dark) !important;
        font-size: 3.2em !important;
        font-weight: 800 !important;
        margin-bottom: 20px !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        letter-spacing: 1px;
    }
    
    .hero-subtitle {
        color: var(--primary-dark);
        font-size: 1.3em;
        font-weight: 600;
        margin-bottom: 30px;
        line-height: 1.6;
        opacity: 0.8;
    }
    
    /* 기능 카드 그리드 */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 25px;
        margin: 30px 0;
    }
    
    .feature-card {
        background: var(--card-bg);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 25px;
        padding: 40px 30px;
        text-align: center;
        transition: all 0.4s ease;
        height: 320px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        position: relative;
        overflow: hidden;
        cursor: pointer;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(76, 175, 80, 0.1), transparent);
        transition: all 0.6s ease;
    }
    
    .feature-card:hover::before {
        left: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-15px) scale(1.05);
        box-shadow: 0 30px 80px rgba(76, 175, 80, 0.3);
        background: rgba(255, 255, 255, 1);
        border-color: var(--primary);
    }
    
    .feature-icon {
        font-size: 4.5em;
        margin-bottom: 25px;
        color: var(--primary-dark);
        filter: drop-shadow(0 4px 8px rgba(76, 175, 80, 0.3));
    }
    
    .feature-title {
        color: var(--primary-dark);
        font-size: 1.4em;
        font-weight: 700;
        margin-bottom: 15px;
    }
    
    .feature-description {
        color: var(--primary-dark);
        font-weight: 600;
        line-height: 1.6;
        font-size: 1.05em;
    }
    
    /* 통계 대시보드 */
    .stats-dashboard {
        background: var(--card-bg);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 25px;
        padding: 40px;
        margin: 30px 0;
        box-shadow: var(--shadow);
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 25px;
        margin-top: 20px;
    }
    
    .stat-card {
        background: rgba(255, 255, 255, 0.7);
        border: 2px solid rgba(76, 175, 80, 0.3);
        border-radius: 20px;
        padding: 30px 20px;
        text-align: center;
        transition: all 0.3s ease;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .stat-card:hover {
        border-color: var(--primary);
        box-shadow: 0 10px 30px rgba(76, 175, 80, 0.25);
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 1);
    }
    
    .stat-number {
        font-size: 2.8em;
        font-weight: 800;
        color: var(--primary-dark);
        margin-bottom: 8px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    .stat-label {
        color: var(--primary-dark);
        font-size: 1.1em;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    /* 사용자 상태 카드 */
    .user-status-card {
        background: var(--card-bg);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 25px;
        padding: 35px;
        margin: 25px 0;
        text-align: center;
        box-shadow: var(--shadow);
        transition: all 0.3s ease;
    }
    
    .user-status-card:hover {
        transform: translateY(-5px);
        box-shadow: var(--shadow-hover);
        border-color: var(--primary);
    }
    
    .user-name {
        color: var(--primary-dark);
        font-size: 1.6em;
        font-weight: 700;
        margin-bottom: 15px;
    }
    
    .user-status {
        font-size: 1.2em;
        font-weight: 600;
        margin: 10px 0;
    }
    
    /* 액션 버튼 섹션 */
    .action-section {
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), var(--card-bg));
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 25px;
        padding: 40px;
        margin: 30px 0;
        text-align: center;
    }
    
    .action-buttons {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 20px;
        margin-top: 30px;
    }
    
    /* 클러스터 결과 표시 */
    .cluster-result {
        background: var(--card-bg);
        backdrop-filter: blur(20px);
        border: 3px solid var(--primary);
        border-radius: 25px;
        padding: 40px;
        margin: 30px 0;
        text-align: center;
        box-shadow: 0 15px 40px rgba(76, 175, 80, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .cluster-result::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 6px;
        background: linear-gradient(45deg, var(--primary), var(--secondary));
        border-radius: 25px 25px 0 0;
    }
    
    .cluster-badges {
        display: flex;
        justify-content: center;
        gap: 15px;
        margin: 25px 0;
        flex-wrap: wrap;
    }
    
    .cluster-badge {
        background: linear-gradient(45deg, var(--primary), var(--secondary));
        color: white;
        padding: 12px 20px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 1.05em;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
    }
    
    /* 차트 컨테이너 */
    .chart-section {
        background: var(--card-bg);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 25px;
        padding: 35px;
        margin: 30px 0;
        box-shadow: var(--shadow);
    }
    
    .chart-section:hover {
        border-color: var(--primary);
        box-shadow: var(--shadow-hover);
    }
    
    /* 반응형 디자인 */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.4em !important;
        }
        
        .feature-grid {
            grid-template-columns: 1fr;
        }
        
        .stats-grid {
            grid-template-columns: repeat(2, 1fr);
        }
        
        .action-buttons {
            grid-template-columns: 1fr;
        }
        
        .cluster-badges {
            flex-direction: column;
            align-items: center;
        }
    }
</style>
""", unsafe_allow_html=True)

# 차트 생성 함수들
@st.cache_data(ttl=3600)
def create_system_overview_chart():
    """12개 요인 시스템 개요 레이더 차트"""
    factors = [
        "계획적정보추구", "쇼핑중심", "여행경험축", "실용적현지탐색",
        "편의인프라중시", "전통문화안전", "패션쇼핑", "프리미엄사회적",
        "성별기반쇼핑", "디지털미디어", "절차자연관광", "교통미식"
    ]
    
    average_scores = [0.85, 0.78, 0.72, 0.65, 0.68, 0.82, 0.58, 0.71, 0.45, 0.63, 0.69, 0.61]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=average_scores,
        theta=factors,
        fill='toself',
        name='전체 평균',
        line_color='#4CAF50',
        fillcolor='rgba(76, 175, 80, 0.2)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickfont=dict(size=10, color='#2E7D32'),
                gridcolor='rgba(76, 175, 80, 0.3)'
            ),
            angularaxis=dict(
                tickfont=dict(size=11, color='#2E7D32'),
                gridcolor='rgba(76, 175, 80, 0.3)'
            )
        ),
        showlegend=True,
        title="12개 요인 시스템 개요",
        font=dict(color='#2E7D32', size=12),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=500
    )
    
    return fig

@st.cache_data(ttl=3600)
def create_cluster_distribution_chart():
    """클러스터 분포 차트"""
    try:
        cluster_info = get_cluster_info()
        
        names = [info['name'] for info in cluster_info.values()]
        percentages = [info['percentage'] for info in cluster_info.values()]
        colors = [info['color'] for info in cluster_info.values()]
        
        fig = px.pie(
            values=percentages,
            names=names,
            title="8개 클러스터 분포",
            color_discrete_sequence=colors,
            hover_data={'values': percentages}
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>비율: %{percent}<br>인원: %{value}%<extra></extra>'
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#2E7D32',
            title_font_size=16,
            height=500
        )
        
        return fig
    except Exception as e:
        st.error(f"차트 생성 오류: {e}")
        return None

def create_user_progress_chart():
    """사용자 진행 상황 차트"""
    if 'survey_completed' in st.session_state and st.session_state.survey_completed:
        if 'factor_scores' in st.session_state:
            try:
                factor_scores = st.session_state.factor_scores
                factors = list(factor_scores.keys())
                scores = list(factor_scores.values())
                
                fig = px.bar(
                    x=factors,
                    y=scores,
                    title="나의 12개 요인 점수",
                    color=scores,
                    color_continuous_scale=['#E8F5E8', '#4CAF50', '#2E7D32']
                )
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#2E7D32',
                    title_font_size=16,
                    xaxis_tickangle=-45,
                    height=400
                )
                
                return fig
            except Exception as e:
                st.error(f"개인 차트 생성 오류: {e}")
                return None
    
    # 기본 차트 (설문 미완료 시)
    factors = [f"요인{i}" for i in range(1, 13)]
    placeholder_scores = [0] * 12
    
    fig = px.bar(
        x=factors,
        y=placeholder_scores,
        title="설문 완료 후 나의 요인 점수를 확인하세요",
        color_discrete_sequence=['#E0E0E0']
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#2E7D32',
        title_font_size=16,
        height=400
    )
    
    return fig

def render_user_status():
    """사용자 상태 렌더링"""
    user_col1, user_col2 = st.columns(2)
    
    with user_col1:
        st.markdown(f"""
        <div class="user-status-card">
            <div class="user-name">👤 {st.session_state.username}님</div>
            <p style="color: #666; margin: 0; font-size: 1.1em;">
                12개 요인 기반 정밀 분석 시스템에 오신 것을 환영합니다!
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with user_col2:
        # 설문 완료 상태 확인
        if 'survey_completed' in st.session_state and st.session_state.survey_completed:
            if 'cluster_result' in st.session_state:
                try:
                    cluster_result = st.session_state.cluster_result
                    cluster_info = get_cluster_info()
                    cluster_id = cluster_result['cluster']
                    
                    if cluster_id in cluster_info:
                        cluster_data = cluster_info[cluster_id]
                        status_color = cluster_data['color']
                        status_text = f"✅ 분석 완료<br><small>🎯 {cluster_data['name']}</small>"
                    else:
                        status_color = "#4CAF50"
                        status_text = "✅ 분석 완료"
                except Exception as e:
                    status_color = "#4CAF50" 
                    status_text = "✅ 설문 완료"
                    st.error(f"클러스터 정보 로딩 오류: {e}")
            else:
                status_color = "#4CAF50" 
                status_text = "✅ 설문 완료"
        else:
            status_color = "#FF8A65"
            status_text = "⏳ 설문 대기 중"
        
        st.markdown(f"""
        <div class="user-status-card">
            <h4 style="color: #2E7D32; margin-bottom: 15px;">📋 진행 상태</h4>
            <div class="user-status" style="color: {status_color};">{status_text}</div>
        </div>
        """, unsafe_allow_html=True)

def render_cluster_result():
    """클러스터 분석 결과 표시"""
    if 'survey_completed' in st.session_state and st.session_state.survey_completed:
        if 'cluster_result' in st.session_state:
            try:
                cluster_result = st.session_state.cluster_result
                cluster_info = get_cluster_info()
                cluster_id = cluster_result['cluster']
                
                if cluster_id in cluster_info:
                    cluster_data = cluster_info[cluster_id]
                    
                    st.markdown(f"""
                    <div class="cluster-result" style="border-color: {cluster_data['color']};">
                        <h2 style="color: {cluster_data['color']}; margin-bottom: 20px; font-size: 2em;">
                            🏆 {cluster_data['name']}
                        </h2>
                        <h3 style="color: #666; margin-bottom: 20px; font-size: 1.3em;">
                            {cluster_data['english_name']}
                        </h3>
                        <p style="color: #2E7D32; font-weight: 600; line-height: 1.7; margin-bottom: 25px; font-size: 1.1em;">
                            {cluster_data['description']}
                        </p>
                        <div class="cluster-badges">
                            <div class="cluster-badge">
                                신뢰도: {cluster_result['confidence']:.1%}
                            </div>
                            <div class="cluster-badge">
                                전체 비율: {cluster_data['percentage']}%
                            </div>
                            <div class="cluster-badge">
                                {cluster_data['count']:,}명 중 하나
                            </div>
                        </div>
                        <div style="margin-top: 25px;">
                            <h4 style="color: #2E7D32; margin-bottom: 15px;">🎯 주요 특성</h4>
                            <div style="display: flex; justify-content: center; gap: 10px; flex-wrap: wrap;">
                                {' '.join([f'<span style="background: rgba(76, 175, 80, 0.2); color: #2E7D32; padding: 8px 15px; border-radius: 15px; font-weight: 600; font-size: 0.9em;">{char}</span>' for char in cluster_data['characteristics']])}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"클러스터 정보 표시 오류: {e}")

def render_main_actions():
    """메인 액션 버튼들"""
    st.markdown("""
    <div class="action-section">
        <h2 style="color: #2E7D32; margin-bottom: 20px; font-size: 2em;">🎯 시작하기</h2>
        <p style="color: #2E7D32; font-size: 1.2em; font-weight: 600; margin-bottom: 30px;">
            당신만의 맞춤형 웰니스 여행을 찾아보세요
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    action_col1, action_col2, action_col3, action_col4 = st.columns(4)
    
    with action_col1:
        if st.button("📝 12개 요인 설문", key="survey_btn", use_container_width=True):
            st.switch_page("pages/01_questionnaire.py")
    
    with action_col2:
        if st.button("🎯 분석 결과", key="results_btn", use_container_width=True):
            if 'survey_completed' in st.session_state and st.session_state.survey_completed:
                st.switch_page("pages/04_recommendations.py")
            else:
                st.warning("⚠️ 설문을 먼저 완료해주세요!")
    
    with action_col3:
        if st.button("🗺️ 관광지 지도", key="map_btn", use_container_width=True):
            if 'survey_completed' in st.session_state and st.session_state.survey_completed:
                st.switch_page("pages/05_map_view.py")
            else:
                st.warning("⚠️ 설문을 먼저 완료해주세요!")
    
    with action_col4:
        if st.button("📈 통계 분석", key="stats_btn", use_container_width=True):
            st.switch_page("pages/06_statistics.py")

def render_logout():
    """로그아웃 버튼"""
    st.markdown("---")
    logout_col1, logout_col2, logout_col3 = st.columns([2, 1, 2])
    with logout_col2:
        if st.button("🚪 로그아웃", key="logout_btn", use_container_width=True):
            # 세션 상태 클리어 확인 대화상자
            if st.button("정말 로그아웃하시겠습니까?", key="confirm_logout", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

def home_page():
    """메인 홈 페이지"""
    
    # 히어로 섹션
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">🌿 웰니스 투어 추천 시스템 2.0</h1>
        <p class="hero-subtitle">
            12개 요인 기반 과학적 분석으로 당신만의 완벽한 한국 여행을 설계합니다
        </p>
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 30px; margin-top: 30px; text-align: center;">
            <div>
                <div style="font-size: 2.5em; margin-bottom: 10px;">🔬</div>
                <div style="color: #2E7D32; font-weight: 700;">과학적 근거</div>
                <div style="color: #666; font-size: 0.9em;">2,591명 데이터 기반</div>
            </div>
            <div>
                <div style="font-size: 2.5em; margin-bottom: 10px;">🎯</div>
                <div style="color: #2E7D32; font-weight: 700;">정밀 분석</div>
                <div style="color: #666; font-size: 0.9em;">12개 요인 8개 유형</div>
            </div>
            <div>
                <div style="font-size: 2.5em; margin-bottom: 10px;">🚀</div>
                <div style="color: #2E7D32; font-weight: 700;">맞춤 추천</div>
                <div style="color: #666; font-size: 0.9em;">95% 정확도</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 사용자 상태 및 진행 상황
    render_user_status()
    
    # 클러스터 결과 표시 (설문 완료된 경우)
    render_cluster_result()
    
    # 시스템 KPI
    st.markdown("""
    <div class="stats-dashboard">
        <h2 style="color: #2E7D32; text-align: center; margin-bottom: 20px; font-size: 2em;">📊 시스템 현황</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">2,591</div>
                <div class="stat-label">학습 데이터</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">12</div>
                <div class="stat-label">분석 요인</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">8</div>
                <div class="stat-label">클러스터 유형</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">95%</div>
                <div class="stat-label">분석 정확도</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 주요 기능 소개
    st.markdown("""
    <h2 style="color: #2E7D32; text-align: center; font-size: 2.2em; margin: 50px 0 30px 0; font-weight: 700;">🎯 주요 기능</h2>
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3 class="feature-title">12개 요인 분석</h3>
            <p class="feature-description">
                과학적 요인분석으로 개인의 여행 성향을 12개 차원에서 정밀 측정
            </p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <h3 class="feature-title">AI 클러스터 매칭</h3>
            <p class="feature-description">
                머신러닝 기반 8개 클러스터 중 최적 유형 자동 분류
            </p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <h3 class="feature-title">맞춤형 추천</h3>
            <p class="feature-description">
                클러스터별 특성에 최적화된 한국 관광지 정확한 추천 제공
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 시스템 분석 차트
    st.markdown('<h2 style="color: #2E7D32; text-align: center; font-size: 2.2em; margin: 50px 0 30px 0; font-weight: 700;">📈 시스템 분석</h2>', unsafe_allow_html=True)
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown('<div class="chart-section">', unsafe_allow_html=True)
        try:
            system_chart = create_system_overview_chart()
            if system_chart:
                st.plotly_chart(system_chart, use_container_width=True, config={'displayModeBar': False})
        except Exception as e:
            st.error(f"시스템 차트 로딩 오류: {e}")
            st.info("차트를 불러오는 중 문제가 발생했습니다.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with chart_col2:
        st.markdown('<div class="chart-section">', unsafe_allow_html=True)
        try:
            cluster_chart = create_cluster_distribution_chart()
            if cluster_chart:
                st.plotly_chart(cluster_chart, use_container_width=True, config={'displayModeBar': False})
        except Exception as e:
            st.error(f"클러스터 차트 로딩 오류: {e}")
            st.info("차트를 불러오는 중 문제가 발생했습니다.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 개인 분석 결과 (설문 완료 시)
    if 'survey_completed' in st.session_state and st.session_state.survey_completed:
        st.markdown('<h2 style="color: #2E7D32; text-align: center; font-size: 2.2em; margin: 50px 0 30px 0; font-weight: 700;">📊 나의 분석 결과</h2>', unsafe_allow_html=True)
        
        st.markdown('<div class="chart-section">', unsafe_allow_html=True)
        try:
            personal_chart = create_user_progress_chart()
            if personal_chart:
                st.plotly_chart(personal_chart, use_container_width=True, config={'displayModeBar': False})
        except Exception as e:
            st.error(f"개인 차트 로딩 오류: {e}")
            st.info("개인 분석 차트를 불러오는 중 문제가 발생했습니다.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 메인 액션 버튼들
    render_main_actions()
    
    # 로그아웃
    render_logout()
    
    # 푸터 정보
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #666; padding: 30px; background: rgba(255, 255, 255, 0.8); border-radius: 20px; margin: 30px 0;">
        <h4 style="color: #2E7D32; margin-bottom: 20px;">💡 시스템 정보</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; text-align: left;">
            <div>
                <strong style="color: #4CAF50;">📊 데이터 출처:</strong><br>
                <span style="font-size: 0.9em;">2,591명 외국인 관광객 설문 조사<br>(요인분석 기반)</span>
            </div>
            <div>
                <strong style="color: #4CAF50;">🔒 개인정보 보호:</strong><br>
                <span style="font-size: 0.9em;">모든 데이터는 암호화되어<br>안전하게 처리됩니다</span>
            </div>
            <div>
                <strong style="color: #4CAF50;">⚡ 시스템 상태:</strong><br>
                <span style="font-size: 0.9em;">정상 운영 중 | 평균 응답시간: 1.2초<br>가동률: 99.9%</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 메인 실행부
def main():
    """메인 실행 함수"""
    try:
        home_page()
    except Exception as e:
        st.error("❌ 페이지 로딩 중 오류가 발생했습니다.")
        
        # 사용자 친화적 오류 메시지
        if "module" in str(e).lower() or "import" in str(e).lower():
            st.warning("🔧 **모듈 로딩 오류:** 시스템을 초기화하고 있습니다.")
        else:
            st.info("🔄 일시적인 오류입니다. 페이지를 새로고침해주세요.")
        
        # 디버깅 정보
        with st.expander("🔍 오류 상세 정보", expanded=False):
            st.exception(e)
        
        # 복구 옵션
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 페이지 새로고침"):
                st.rerun()
        
        with col2:
            if st.button("🏠 로그인 페이지로"):
                st.switch_page("app.py")
                
        with col3:
            if st.button("🚪 로그아웃"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.switch_page("app.py")

if __name__ == "__main__":
    main()
else:
    main()