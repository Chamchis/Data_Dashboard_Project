import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
from my_packages import region_page
import matplotlib.pyplot as plt
# 한글 폰트 경로 설정
plt.rcParams['font.family'] ='Malgun Gothic'

# 페이지 넓게
st.set_page_config(layout="wide")

# 데이터 불러오기 / 한글이 깨지므로 인코딩
gdp_original = pd.read_csv('시도별_경제활동별_지역내총생산_20240315165307.csv', encoding='cp949')
per_gdp_original = pd.read_csv('시도별_1인당_지역내총생산__지역총소득__개인소득_20240316162000.csv', encoding='cp949')

# 특정 열만 갖고오기 GDP
selected_columns_gdp = ['시도별','경제활동별','명목']
selected_columns_korea = ['종합_시도별','종합_경제활동별','종합_명목']
gdp = gdp_original[selected_columns_gdp] # 지역별
gdp_korea = gdp_original[selected_columns_korea] # 전국

# 특정 열만 갖고오기 1인당 GDP
selected_columns_per_gdp = ['시도별','1인당 지역내총생산','1인당 지역총소득','1인당 개인소득','1인당 민간소비']
selected_columns_per_gdp_korea = ['시도별','1인당 지역내총생산']
per_gdp = per_gdp_original[selected_columns_per_gdp] # 지역별
per_gdp_korea = per_gdp_original[selected_columns_per_gdp_korea] # 전국

# 빈칸 제거
gdp.dropna(inplace=True)
gdp_korea.dropna(inplace=True)

# 시/도 리스트
city_list = ['전국', '서울특별시', '부산광역시', '대구광역시', '인천광역시', '광주광역시', '대전광역시', '울산광역시','세종특별자치시']
do_list = ['경기도', '강원도', '충청북도', '충청남도', '전라북도', '전라남도', '경상북도', '경상남도', '제주특별자치도']

# 사이드바 
with st.sidebar:
    st.header('안녕하세요!')
    # 셀렉박스에서 선택한 값을 저장. 시/도를 나타냄
    selected_option = st.sidebar.selectbox("시/도 선택", city_list + do_list)
    # 사이드바 문구
    st.subheader('자료 출처 : KOSIS 국가통계포털')
    st.text('시도별_경제활동별_지역내총생산_20240\n315165307.csv')
    st.text('시도별_1인당_지역내총생산__지역총소득__개인소득_20240316162000.csv')
    st.text('2022년 기준입니다.')

# 전국 중심 좌표
korea_center = [36, 127.5]

# 지역별 확대 좌표 
region_center = {
    '서울특별시': [37.5565, 126.9780],
    '부산광역시': [35.1796, 129.0756],
    '대구광역시': [35.8214, 128.6014],
    '인천광역시': [37.4563, 126.7052],
    '광주광역시': [35.1595, 126.8526],
    '대전광역시': [36.3504, 127.3845],
    '울산광역시': [35.5384, 129.3114],
    '세종특별자치시': [36.4805, 127.2892],
    '경기도': [37.4138, 127.5183],
    '강원도': [37.8228, 128.1555],
    '충청북도': [36.8002, 127.6470],
    '충청남도': [36.5184, 126.8000],
    '전라북도': [35.7175, 127.1530],
    '전라남도': [34.8679, 126.9910],
    '경상북도': [36.5755, 128.5058],
    '경상남도': [35.2383, 128.6921],
    '제주특별자치도': [33.4890, 126.4983]
}

# 기본 지도는 난잡하므로 깔끔한 지도
korea_map = folium.Map(location=korea_center, zoom_start=6, tiles='CartoDB positron')

# 시/도 별로 경계선을 긋기 위한 json 파일
geojson_data = 'skorea-provinces-2018-geo.json'
folium.GeoJson(geojson_data, name='geojson_map').add_to(korea_map)

# 시/도 선택에 따른 처리
if selected_option == '전국':
    col1, col2 ,col3 = st.columns([1,1,2])
    with col1:
        folium_static(korea_map,width=400, height=300)
    with col2:
        # 전국 GDP 데이터 표시
        st.subheader("전국 총생산 (단위 : 백만원)")
        st.write(gdp_korea)

        # 전국 1인당 GDP 데이터 표시
        st.subheader('1인당 총생산 (단위 : 달러)')
        st.write(per_gdp_korea)
    with col3:
        # 막대그래프 표시
        plt.figure(figsize=(5, 2))
        plt.bar(gdp_korea['종합_시도별'], gdp_korea['종합_명목'])
        plt.xlabel('지역별 총생산')
        plt.xticks(rotation=45, ha='right', fontsize=8) # 글자가 겹침
        plt.ylabel('명목')
        plt.title(f"{selected_option} 총생산")
        st.pyplot(plt)
else:
    # 시/도에 따라 줌을 다르게 설정
    if selected_option in city_list:
        zoom = 9
    else:
        zoom = 7

    # 선택한 지역 지도
    region_map = folium.Map(location=region_center[selected_option], zoom_start = zoom, tiles='CartoDB positron', width=400, height=300)
    # 마커 표시
    folium.Marker(
        location=region_center[selected_option],
        tooltip=f"{selected_option}"
    ).add_to(region_map)
    folium.GeoJson(geojson_data, name='geojson_map').add_to(region_map)
    region_page.show_region(gdp,per_gdp,region_map,selected_option)
