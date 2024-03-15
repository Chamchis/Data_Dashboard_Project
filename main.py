import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
from streamlit_option_menu import option_menu

# 페이지 넓게
st.set_page_config(layout="wide")

# 데이터 불러오기 / 한글이 깨지므로 인코딩
df = pd.read_csv('시도별_경제활동별_지역내총생산_20240315165307.csv', encoding='UTF-8')

# 전국 중심 좌표
korea_center = [35.5, 127.5]

# 기본 지도는 난잡하므로 깔끔한 지도
korea_map = folium.Map(location=korea_center, zoom_start=6, tiles='CartoDB positron')

# 시/도 별로 경계선을 긋기 위한 json 파일
geojson_data = 'skorea-provinces-geo.json'
folium.GeoJson(geojson_data, name='geojson_map').add_to(korea_map)

# 시/도 리스트
city_list = ['전국', '서울특별시', '부산광역시', '대구광역시', '인천광역시', '광주광역시', '대전광역시', '울산광역시',
             '세종특별자치시', '경기도', '강원도', '충청북도', '충청남도', '전라북도', '전라남도', '경상북도', '경상남도', '제주특별자치도']

# 메인 메뉴 선택
selected_city = st.sidebar.selectbox("시/도 선택", city_list)

# 시/도 선택에 따른 처리
if selected_city == '전국':
    col1, col2 = st.columns(2)
    with col1:
        folium_static(korea_map)
    with col2:
        st.subheader("전국 총생산")
        st.write(df[df['시도별'] == selected_city])
else:
    col1, col2 = st.columns(2)
    with col1:
        # 시/도 별 데이터 필터링 등 추가 처리
        folium_static(korea_map)
    with col2:
        st.subheader(f"{selected_city} 총생산")
        st.write(df[df['시도별'] == selected_city])
