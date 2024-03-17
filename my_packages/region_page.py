import streamlit as st
from streamlit_folium import folium_static
import folium
import matplotlib.pyplot as plt

selected_city = ""

# 한글 폰트 경로 설정
plt.rcParams['font.family'] ='Malgun Gothic'

def show_region(gdp, per_gdp, region_map, selected_option):
    gdp_data = gdp[gdp['시도별'] == selected_option] # GDP
    per_gdp_data = per_gdp[per_gdp['시도별'] == selected_option] # 1인당 GDP

    # 선택한 시, 도를 강조
    def my_style(color):
        if color['properties']['name'] == selected_option:
            return {
                'fillColor': 'red',  
                'fillOpacity': 0.5,
                'color': 'blue',
                'weight': 2
            }
        else:
            return {
                'fillOpacity': 0,
                'color': 'gray',
                'weight': 1
            }

    # 지역별 경계를 강조
    folium.GeoJson(
        'skorea-provinces-2018-geo.json',
        name='geojson_map',
        style_function=my_style
    ).add_to(region_map)


    col1, col2, col3 = st.columns(3) 
    with col1:
        # 시/도 별 데이터 필터링 등 추가 처리
        folium_static(region_map)
    with col2:
        # 지역별 GDP 데이터 표시
        st.subheader(f"{selected_option} 총생산 (단위 : 백만원)")
        st.write(gdp_data)
        
        # 지역별 1인당 GDP 데이터 표시
        st.subheader(f"{selected_option} 1인당 총생산 (단위 : 달러)")
        st.write(per_gdp_data)
    with col3:
        # 막대그래프에서 전체 수치를 보여줄 필요는 없기에 '지역내총생산' 항목은 제외
        gdp_data_excluded_name = gdp_data[gdp_data['경제활동별'] != '지역내총생산(시장가격)'] # 검색하여 해결
        # 막대 그래프 표시
        plt.figure(figsize=(6, 4))
        plt.bar(gdp_data_excluded_name['경제활동별'], gdp_data_excluded_name['명목'])
        plt.xlabel('경제활동별')
        plt.ylabel('명목')
        plt.title(f"{selected_option} 총생산")
        plt.xticks(rotation=45, ha='right', fontsize=8) # 글자가 겹침
        st.pyplot(plt)
