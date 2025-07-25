# pages/05_map_view.py - 실제 CSV 데이터 기반 지도 뷰

import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
import sys
import os

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from utils import (check_access_permissions, determine_cluster, get_cluster_info, 
                      load_wellness_destinations, calculate_recommendations_by_cluster,
                      get_cluster_region_info, apply_global_styles, export_recommendations_to_csv)
except ImportError as e:
    st.error(f"❌ 필수 모듈을 불러올 수 없습니다: {e}")
    st.info("💡 `utils.py` 파일이 올바른 위치에 있는지 확인해주세요.")
    st.stop()

# 페이지 고유 ID 생성 (세션별 고유 키 보장)
if 'map_page_instance_id' not in st.session_state:
    st.session_state.map_page_instance_id = int(time.time() * 1000)

PAGE_ID = st.session_state.map_page_instance_id

# 로그인 체크
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("app.py")

# 설문 완료 체크
if 'survey_completed' not in st.session_state or not st.session_state.survey_completed:
    st.warning("⚠️ 설문조사를 먼저 완료해주세요.")
    if st.button("📝 설문조사 하러 가기", key=f"survey_btn_{PAGE_ID}"):
        st.switch_page("pages/01_questionnaire.py")
    st.stop()

# 페이지 설정
st.set_page_config(
    page_title="웰니스 투어 지도",
    page_icon="🗺️",
    layout="wide"
)

# 접근 권한 확인
check_access_permissions()
apply_global_styles()

# 지도 페이지 전용 CSS
st.markdown("""
<style>
    /* 지도 컨테이너 스타일 */
    .map-container {
        background: var(--card-bg);
        backdrop-filter: blur(25px);
        border: 3px solid rgba(76, 175, 80, 0.4);
        border-radius: 25px;
        padding: 20px;
        margin: 25px 0;
        box-shadow: var(--shadow);
        transition: all 0.3s ease;
    }
    
    .map-container:hover {
        border-color: var(--primary);
        box-shadow: var(--shadow-hover);
    }
    
    /* 페이지 제목 */
    .page-title {
        color: var(--primary-dark) !important;
        text-align: center;
        background: var(--card-bg);
        padding: 30px 40px;
        border-radius: 25px;
        font-size: 3.2em !important;
        margin-bottom: 40px;
        font-weight: 800 !important;
        border: 3px solid var(--primary);
        box-shadow: var(--shadow);
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        letter-spacing: 1px;
    }
    
    /* 필터 카드 */
    .filter-card {
        background: var(--card-bg);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 20px;
        padding: 25px 30px;
        margin: 25px 0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .filter-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(45deg, var(--primary), var(--secondary));
        border-radius: 20px 20px 0 0;
    }
    
    .filter-card:hover {
        border-color: var(--primary);
        box-shadow: var(--shadow-hover);
    }
    
    /* 통계 카드 */
    .stats-card {
        background: var(--card-bg);
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
    
    .stats-card:hover {
        border-color: var(--primary);
        box-shadow: var(--shadow-hover);
        transform: translateY(-3px);
    }
    
    .stats-number {
        font-size: 2.8em;
        font-weight: 800;
        color: var(--primary-dark);
        margin-bottom: 8px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    .stats-label {
        color: var(--primary-dark);
        font-size: 1.2em;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    /* 섹션 제목 */
    .section-title {
        color: var(--primary-dark) !important;
        font-size: 2.2em;
        font-weight: 700;
        margin: 40px 0 25px 0;
        text-align: center;
        background: var(--card-bg);
        padding: 20px 30px;
        border-radius: 20px;
        border-left: 6px solid var(--primary);
        box-shadow: var(--shadow);
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    /* 클러스터 분석 카드 */
    .cluster-analysis-card {
        background: var(--card-bg);
        backdrop-filter: blur(25px);
        border: 3px solid rgba(76, 175, 80, 0.4);
        border-radius: 25px;
        padding: 35px;
        margin: 25px 0;
        text-align: center;
        box-shadow: var(--shadow);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .cluster-analysis-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 6px;
        background: linear-gradient(45deg, var(--primary), var(--secondary));
        border-radius: 25px 25px 0 0;
    }
    
    .cluster-analysis-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 50px rgba(76, 175, 80, 0.25);
        border-color: var(--primary);
    }
    
    /* 범례 카드 */
    .legend-card {
        background: var(--card-bg);
        border: 2px solid rgba(76, 175, 80, 0.3);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
    }
    
    .legend-item {
        display: flex;
        align-items: center;
        margin: 10px 0;
        padding: 8px 12px;
        background: rgba(76, 175, 80, 0.05);
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    
    .legend-item:hover {
        background: rgba(76, 175, 80, 0.15);
        transform: translateX(5px);
    }
    
    .legend-color {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        margin-right: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    
    /* 다운로드 버튼 */
    .download-section {
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), var(--card-bg));
        border: 2px solid rgba(76, 175, 80, 0.4);
        border-radius: 20px;
        padding: 25px;
        margin: 30px 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def create_folium_map(places_to_show, center_lat=37.5, center_lon=127.0, zoom=7):
    """Folium 기반 상세 지도 생성"""
    
    # 지도 생성
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles='CartoDB positron',
        attr='CartoDB'
    )
    
    # 인천공항 마커
    incheon_airport = [37.4602, 126.4407]
    folium.Marker(
        incheon_airport,
        popup=folium.Popup("✈️ 인천국제공항 (출발지)", max_width=200),
        tooltip="✈️ 인천국제공항",
        icon=folium.Icon(color='red', icon='plane', prefix='fa')
    ).add_to(m)
    
    # 타입별 색상 매핑
    color_map = {
        "스파/온천": "blue",
        "산림/자연치유": "green", 
        "웰니스 리조트": "purple",
        "체험/교육": "orange",
        "리조트/호텔": "pink",
        "문화/예술": "lightgreen",
        "힐링/테라피": "lightblue",
        "한방/전통의학": "darkgreen",
        "레저/액티비티": "red",
        "기타": "gray"
    }
    
    # 관광지 마커들 생성
    for i, place in enumerate(places_to_show):
        # 팝업 HTML 생성
        popup_html = f"""
        <div style="width: 350px; font-family: 'Noto Sans KR', sans-serif;">
            <h4 style="color: #2E7D32; margin-bottom: 10px; border-bottom: 2px solid #4CAF50; padding-bottom: 5px;">
                #{i+1} {place['name']}
            </h4>
            <div style="margin: 10px 0;">
                <strong>🏷️ 유형:</strong> <span style="color: #4CAF50; font-weight: 600;">{place['type']}</span>
            </div>
            <div style="margin: 10px 0;">
                <strong>⭐ 평점:</strong> <span style="color: #FF9800; font-weight: 600;">{place['rating']}/10</span>
            </div>
            <div style="margin: 10px 0;">
                <strong>📍 거리:</strong> {place['distance_from_incheon']}km
            </div>
            <div style="margin: 10px 0;">
                <strong>💰 가격:</strong> {place['price_range']}
            </div>
            <div style="margin: 10px 0;">
                <strong>🚗 자차:</strong> {place.get('travel_time_car', '정보없음')} ({place.get('travel_cost_car', '정보없음')})
            </div>
            <div style="margin: 10px 0;">
                <strong>🚇 대중교통:</strong> {place.get('travel_time_train', '정보없음')} ({place.get('travel_cost_train', '정보없음')})
            </div>
            <div style="margin: 10px 0;">
                <strong>🎯 추천점수:</strong> <span style="color: #2E7D32; font-weight: 700;">{place['recommendation_score']:.1f}점</span>
            </div>
            <div style="margin: 15px 0; padding: 10px; background-color: #f5f5f5; border-radius: 8px;">
                <strong>📝 설명:</strong><br>
                <span style="line-height: 1.4;">{place['description'][:150]}{'...' if len(place['description']) > 150 else ''}</span>
            </div>
            {'<div style="margin: 10px 0; color: #4CAF50; font-weight: 600;">✅ 완벽매칭</div>' if place.get('cluster_match') else ''}
        </div>
        """
        
        # 마커 색상 결정
        marker_color = color_map.get(place['type'], 'gray')
        
        folium.Marker(
            [place['lat'], place['lon']],
            popup=folium.Popup(popup_html, max_width=400),
            tooltip=f"#{i+1} {place['name']} ({place['type']})",
            icon=folium.Icon(color=marker_color, icon='info-sign')
        ).add_to(m)
    
    return m

def create_plotly_map(places_to_show):
    """Plotly 기반 인터랙티브 지도 생성"""
    if not places_to_show:
        return None
        
    # 데이터 준비
    df_map = pd.DataFrame(places_to_show)
    
    # 타입별 색상 매핑
    type_colors = {
        '스파/온천': '#FF6B6B',
        '산림/자연치유': '#4ECDC4', 
        '웰니스 리조트': '#45B7D1',
        '체험/교육': '#FFA726',
        '리조트/호텔': '#AB47BC',
        '문화/예술': '#66BB6A',
        '힐링/테라피': '#FF7043',
        '한방/전통의학': '#26A69A',
        '레저/액티비티': '#EC407A',
        '기타': '#78909C'
    }
    
    # 색상 리스트 생성
    df_map['color'] = df_map['type'].map(type_colors).fillna('#78909C')
    
    fig = go.Figure()
    
    # 관광지 마커 추가
    for type_name in df_map['type'].unique():
        type_data = df_map[df_map['type'] == type_name]
        
        fig.add_trace(go.Scattermapbox(
            lat=type_data['lat'],
            lon=type_data['lon'],
            mode='markers',
            marker=dict(
                size=type_data['recommendation_score'] / 5,  # 점수에 따른 크기
                color=type_colors.get(type_name, '#78909C'),
                opacity=0.8
            ),
            text=type_data['name'],
            hovertemplate='<b>%{text}</b><br>' +
                         'Type: ' + type_name + '<br>' +
                         'Rating: %{customdata[0]}/10<br>' +
                         'Distance: %{customdata[1]}km<br>' +
                         'Score: %{customdata[2]:.1f}<br>' +
                         '<extra></extra>',
            customdata=type_data[['rating', 'distance_from_incheon', 'recommendation_score']].values,
            name=type_name
        ))
    
    # 인천공항 마커 추가
    fig.add_trace(go.Scattermapbox(
        lat=[37.4602],
        lon=[126.4407],
        mode='markers',
        marker=dict(size=20, color='red', symbol='airport'),
        text=['인천국제공항'],
        hovertemplate='<b>%{text}</b><br>출발지<extra></extra>',
        name='인천공항'
    ))
    
    fig.update_layout(
        mapbox=dict(
            style='open-street-map',
            center=dict(lat=37.5, lon=127.8),
            zoom=6
        ),
        height=700,
        margin=dict(l=0, r=0, t=30, b=0),
        title="웰니스 관광지 분포 (추천점수별 크기)",
        showlegend=True
    )
    
    return fig

def render_map_settings():
    """지도 설정 렌더링"""
    
    st.markdown('<h2 class="section-title">🗺️ 지도 설정</h2>', unsafe_allow_html=True)
    
    with st.expander("🛠️ 지도 표시 옵션", expanded=True):
        settings_col1, settings_col2 = st.columns(2)
        
        with settings_col1:
            st.markdown("#### 📊 표시 옵션")
            
            num_places = st.slider(
                "표시할 추천지 수",
                min_value=5,
                max_value=20,
                value=10,
                key=f"map_places_slider_{PAGE_ID}"
            )
            
            map_type = st.selectbox(
                "지도 유형",
                ["상세 지도 (Folium)", "분석 지도 (Plotly)"],
                key=f"map_type_select_{PAGE_ID}"
            )
            
            map_center = st.selectbox(
                "지도 중심점",
                ["전체 보기", "수도권", "제주도", "강원도", "경상도"],
                key=f"map_center_select_{PAGE_ID}"
            )
        
        with settings_col2:
            st.markdown("#### 🎨 카테고리 필터")
            
            # 실제 데이터에서 타입 목록 가져오기
            wellness_df = load_wellness_destinations()
            if not wellness_df.empty:
                available_types = wellness_df['type'].unique()
                
                show_categories = {}
                for i, category in enumerate(available_types):
                    show_categories[category] = st.checkbox(
                        f"{category} ({len(wellness_df[wellness_df['type'] == category])}개)",
                        value=True,
                        key=f"show_category_{i}_{PAGE_ID}"
                    )
            else:
                st.error("❌ 관광지 데이터를 불러올 수 없습니다.")
                show_categories = {}
    
    return num_places, map_type, map_center, show_categories

def render_user_cluster_analysis():
    """사용자 클러스터 분석 결과 표시"""
    if 'cluster_result' not in st.session_state:
        return None
        
    cluster_result = st.session_state.cluster_result
    cluster_id = cluster_result['cluster']
    cluster_info = get_cluster_info()
    
    if cluster_id not in cluster_info:
        return None
        
    cluster_data = cluster_info[cluster_id]
    
    st.markdown('<h2 class="section-title">🎭 당신의 여행 성향 분석</h2>', unsafe_allow_html=True)
    
    analysis_col1, analysis_col2 = st.columns([1, 1])
    
    with analysis_col1:
        st.markdown(f"""
        <div class="cluster-analysis-card" style="border-color: {cluster_data['color']};">
            <h3 style="color: {cluster_data['color']}; font-size: 1.8em; margin-bottom: 15px;">
                🏆 {cluster_data['name']}
            </h3>
            <h4 style="color: #666; margin-bottom: 15px; font-size: 1.2em;">
                {cluster_data['english_name']}
            </h4>
            <div style="background: linear-gradient(45deg, #4CAF50, #66BB6A); color: white; 
                        padding: 15px 25px; border-radius: 20px; display: inline-block; margin: 15px 0;
                        font-weight: 800; font-size: 1.2em; box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);">
                매칭 신뢰도: {cluster_result['confidence']:.1%}
            </div>
            <p style="color: #2E7D32; font-weight: 600; line-height: 1.6; margin-top: 15px;">
                {cluster_data['description']}
            </p>
        </div>
        """, unsafe_allow_html=True)

    with analysis_col2:
        # 지도 범례 및 클러스터 특성
        st.markdown(f"""
        <div class="legend-card">
            <h4 style="color: #2E7D32; margin-bottom: 15px;">🎨 지도 범례</h4>
            <div class="legend-item">
                <div class="legend-color" style="background-color: red;"></div>
                <span style="font-weight: 600;">인천국제공항 (출발지)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #FF6B6B;"></div>
                <span>스파/온천</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #4ECDC4;"></div>
                <span>산림/자연치유</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #45B7D1;"></div>
                <span>웰니스 리조트</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #FFA726;"></div>
                <span>체험/교육</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 주요 특성 표시
        st.markdown(f"""
        <div class="legend-card">
            <h4 style="color: #2E7D32; margin-bottom: 15px;">🎯 주요 특성</h4>
            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                {' '.join([f'<span style="background: rgba(76, 175, 80, 0.2); color: #2E7D32; padding: 6px 12px; border-radius: 15px; font-weight: 600; font-size: 0.9em;">{char}</span>' for char in cluster_data['characteristics']])}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    return cluster_result

def render_statistics_dashboard(places_to_show):
    """통계 대시보드 렌더링"""
    if not places_to_show:
        return
        
    st.markdown('<h2 class="section-title">📊 추천 결과 통계</h2>', unsafe_allow_html=True)
    
    # 기본 통계 계산
    avg_distance = np.mean([place['distance_from_incheon'] for place in places_to_show])
    avg_rating = np.mean([place['rating'] for place in places_to_show])
    avg_score = np.mean([place['recommendation_score'] for place in places_to_show])
    cluster_matches = sum(1 for place in places_to_show if place.get('cluster_match', False))
    
    # 타입별 분포
    type_counts = {}
    for place in places_to_show:
        place_type = place['type']
        type_counts[place_type] = type_counts.get(place_type, 0) + 1
    
    # 통계 카드들
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
    with stat_col1:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{len(places_to_show)}</div>
            <div class="stats-label">추천 관광지</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_col2:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{avg_distance:.0f}km</div>
            <div class="stats-label">평균 거리</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_col3:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{avg_rating:.1f}</div>
            <div class="stats-label">평균 평점</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_col4:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{cluster_matches}</div>
            <div class="stats-label">완벽 매칭</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 차트 섹션
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # 타입별 분포 차트
        if type_counts:
            fig_pie = px.pie(
                values=list(type_counts.values()),
                names=list(type_counts.keys()),
                title="추천 관광지 유형별 분포"
            )
            fig_pie.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#2E7D32'
            )
            st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
    
    with chart_col2:
        # 거리별 평점 산점도
        distances = [place['distance_from_incheon'] for place in places_to_show]
        ratings = [place['rating'] for place in places_to_show]
        names = [place['name'] for place in places_to_show]
        
        fig_scatter = px.scatter(
            x=distances,
            y=ratings,
            hover_name=names,
            title="거리 vs 평점 분석",
            labels={'x': '거리 (km)', 'y': '평점 (10점 만점)'}
        )
        fig_scatter.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#2E7D32'
        )
        st.plotly_chart(fig_scatter, use_container_width=True, config={'displayModeBar': False})

def render_download_section(places_to_show, cluster_result):
    """다운로드 섹션 렌더링"""
    st.markdown('<h2 class="section-title">📥 결과 다운로드</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="download-section">
        <h4 style="color: #2E7D32; margin-bottom: 15px;">📊 추천 결과 내보내기</h4>
        <p style="color: #666; margin-bottom: 20px;">
            개인 맞춤형 추천 결과를 CSV 파일로 다운로드하여 여행 계획에 활용하세요.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    download_col1, download_col2, download_col3 = st.columns(3)
    
    with download_col2:
        if st.button("📄 CSV 파일 다운로드", key=f"download_csv_{PAGE_ID}", use_container_width=True):
            try:
                # 사용자 정보 준비
                user_info = {
                    'username': st.session_state.get('username', '익명'),
                    'cluster_name': get_cluster_info()[cluster_result['cluster']]['name'],
                    'confidence': cluster_result['confidence']
                }
                
                # CSV 데이터 생성
                csv_data = export_recommendations_to_csv(places_to_show, user_info)
                
                if csv_data:
                    st.download_button(
                        label="💾 파일 저장",
                        data=csv_data,
                        file_name=f"wellness_recommendations_{st.session_state.get('username', 'user')}_{time.strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key=f"download_file_{PAGE_ID}"
                    )
                    st.success("✅ CSV 파일이 준비되었습니다!")
                else:
                    st.error("❌ 파일 생성 중 오류가 발생했습니다.")
                    
            except Exception as e:
                st.error(f"❌ 다운로드 준비 중 오류: {str(e)}")

def enhanced_map_view_page():
    """개선된 지도 뷰 페이지 메인 함수"""
    
    # 헤더
    st.markdown('<h1 class="page-title">🗺️ 맞춤형 웰니스 여행지 지도</h1>', unsafe_allow_html=True)
    
    # 지도 설정
    num_places, map_type, map_center, show_categories = render_map_settings()
    
    # 사용자 클러스터 분석 표시
    cluster_result = render_user_cluster_analysis()
    
    if not cluster_result:
        st.error("❌ 클러스터 분석 결과가 없습니다. 설문을 다시 진행해주세요.")
        if st.button("📝 설문하러 가기", key=f"survey_redirect_{PAGE_ID}"):
            st.switch_page("pages/01_questionnaire.py")
        return
    
    # 추천 결과 가져오기
    try:
        recommended_places = calculate_recommendations_by_cluster(cluster_result)
        if not recommended_places:
            st.warning("⚠️ 추천 결과가 없습니다. 다른 설정을 시도해보세요.")
            return
            
    except Exception as e:
        st.error(f"❌ 추천 계산 중 오류: {str(e)}")
        return
    
    # 카테고리 필터링
    filtered_places = []
    for place in recommended_places:
        if show_categories.get(place['type'], True):
            filtered_places.append(place)
    
    # 표시할 관광지 수 제한
    places_to_show = filtered_places[:num_places]
    
    if not places_to_show:
        st.warning("⚠️ 표시할 관광지가 없습니다. 카테고리 필터를 확인해주세요.")
        return
    
    # 지도 중심점 설정
    center_coords = {
        "전체 보기": (36.5, 127.8, 7),
        "수도권": (37.5, 126.9, 9),
        "제주도": (33.4, 126.5, 10),
        "강원도": (37.8, 128.5, 9),
        "경상도": (35.8, 128.6, 8)
    }
    
    center_lat, center_lon, zoom = center_coords[map_center]
    
    # 지도 표시
    st.markdown("---")
    
    if map_type == "상세 지도 (Folium)":
        st.markdown('<h2 class="section-title">🌍 상세 관광지 지도</h2>', unsafe_allow_html=True)
        
        try:
            st.markdown('<div class="map-container">', unsafe_allow_html=True)
            
            folium_map = create_folium_map(places_to_show, center_lat, center_lon, zoom)
            
            map_data = st_folium(
                folium_map, 
                width=1200, 
                height=600, 
                returned_objects=["last_object_clicked"],
                key=f"folium_map_{PAGE_ID}"
            )
            
            # 클릭된 마커 정보 표시
            if map_data['last_object_clicked']:
                clicked_data = map_data['last_object_clicked']
                if clicked_data and 'lat' in clicked_data and 'lng' in clicked_data:
                    # 클릭된 위치와 가장 가까운 관광지 찾기
                    clicked_lat, clicked_lon = clicked_data['lat'], clicked_data['lng']
                    min_distance = float('inf')
                    closest_place = None
                    
                    for place in places_to_show:
                        distance = ((place['lat'] - clicked_lat) ** 2 + (place['lon'] - clicked_lon) ** 2) ** 0.5
                        if distance < min_distance:
                            min_distance = distance
                            closest_place = place
                    
                    if closest_place and min_distance < 0.1:  # 0.1도 이내
                        st.info(f"🏛️ **선택된 관광지**: {closest_place['name']} ({closest_place['type']})")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ 상세 지도 로딩 중 오류: {str(e)}")
    
    else:  # Plotly 지도
        st.markdown('<h2 class="section-title">📊 분석 지도 (인터랙티브)</h2>', unsafe_allow_html=True)
        
        try:
            st.markdown('<div class="map-container">', unsafe_allow_html=True)
            
            plotly_map = create_plotly_map(places_to_show)
            if plotly_map:
                st.plotly_chart(plotly_map, use_container_width=True, config={'displayModeBar': True})
            else:
                st.error("❌ 분석 지도를 생성할 수 없습니다.")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ 분석 지도 로딩 중 오류: {str(e)}")
    
    # 통계 대시보드
    render_statistics_dashboard(places_to_show)
    
    # 다운로드 섹션
    render_download_section(places_to_show, cluster_result)
    
    # 액션 버튼
    st.markdown("---")
    st.markdown('<h2 class="section-title">🎯 다음 단계</h2>', unsafe_allow_html=True)
    
    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        if st.button("📝 설문 다시하기", key=f"restart_survey_{PAGE_ID}"):
            # 세션 상태 클리어
            for key in ['survey_completed', 'answers', 'score_breakdown', 'cluster_result', 'factor_scores']:
                if key in st.session_state:
                    del st.session_state[key]
            st.switch_page("pages/01_questionnaire.py")
    
    with action_col2:
        if st.button("📊 상세 추천 결과", key=f"view_results_{PAGE_ID}"):
            st.switch_page("pages/04_recommendations.py")
    
    with action_col3:
        if st.button("📈 통계 분석 보기", key=f"view_stats_{PAGE_ID}"):
            st.switch_page("pages/06_statistics.py")

def main():
    """메인 실행 함수"""
    try:
        enhanced_map_view_page()
    except Exception as e:
        st.error("❌ 페이지 로딩 중 오류가 발생했습니다.")
        st.exception(e)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 페이지 새로고침", key=f"refresh_{PAGE_ID}"):
                st.rerun()
        with col2:
            if st.button("🏠 홈으로 돌아가기", key=f"home_{PAGE_ID}"):
                st.switch_page("pages/03_home.py")

if __name__ == "__main__":
    main()
else:
    main()