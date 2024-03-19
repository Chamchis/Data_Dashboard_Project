import streamlit as st
from streamlit_folium import folium_static
import folium
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# 한글 폰트 경로 설정
plt.rcParams['font.family'] ='Malgun Gothic'

pop = pd.read_csv('인구__가구_및_주택_–_읍면동_연도_끝자리_0__5___시군구_그_외_연도__20240318151543.csv',encoding='cp949')

def show_region(gdp_region, per_gdp, region_map, selected_option):
    gdp_data = gdp_region[gdp_region['시도별'] == selected_option] # GDP
    per_gdp_data = per_gdp[per_gdp['시도별'] == selected_option] # 1인당 GDP

    # 선택한 시, 도를 강조
    def my_style(color):
        if color['properties']['name'] == selected_option:
            return {
                'fillColor': 'blue',  
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

    with st.container():
        col1, col2, col3 = st.columns((2,1,1)) 
        with col1:
            st.subheader(f'{selected_option}')
            folium_static(region_map)
        with col2:
            # 지역별 GDP 데이터 표시
            st.subheader("경제활동별 생산 (단위 : 조)")
            gdp_data_display = gdp_data[['경제활동별','명목']].copy() # 원본 데이터를 복사하여 변경
            gdp_data_display['명목'] = gdp_data_display['명목'] // 1000000  # 백만원 단위를 조 단위로 변환
            gdp_data_display = gdp_data_display[gdp_data_display['경제활동별'] != '총부가가치(기초가격)']
            st.data_editor(gdp_data_display,hide_index=True,width=300,height=510)
        with col3:
                # 메트릭카드
                selected_option_per_gdp = per_gdp_data.loc[per_gdp_data['시도별'] == selected_option, '1인당 지역내총생산'].iloc[0]

                st.subheader(f'1인당 총생산 (달러)')
                st.metric('전국 평균', 41948)
                st.metric(label=f'{selected_option}', value=selected_option_per_gdp)

                pop_metric = pop.loc[pop['행정구역별(읍면동)'] == selected_option, '총인구 (명)']
                pop_metric = pop_metric.values[0] // 10000
                st.subheader('인구수 (만명)')
                st.metric('전국',5169)
                st.metric(f'{selected_option}',pop_metric)

        col4, col5 = st.columns(2)
        with col4:
            # 막대그래프에서 전체 수치를 보여줄 필요는 없기에 '지역내총생산' 항목은 제외
            gdp_data_excluded_name = gdp_data[gdp_data['경제활동별'].isin(['농업, 임업 및 어업', '광제조업',
                                        '전기, 가스, 증기 및 공기 조절 공급업','건설업','서비스업'])]
            top_10_region_gdp = gdp_data_excluded_name.nlargest(5,'명목')
            # 막대 그래프 표시
            plt.figure(figsize=(6, 4))
            plt.bar(top_10_region_gdp['경제활동별'], top_10_region_gdp['명목'] // 1000000)
            plt.xlabel('경제활동별 (조)')
            plt.ylabel('총생산')
            plt.title(f"{selected_option} 상위 5개 경제활동별 생산량 그래프")
            plt.xticks(rotation=45, ha='right', fontsize=8) # 글자가 겹침
            st.pyplot(plt)
        with col5:
            # 가독성을 위하여 일정 확률 이하는 '기타'로 묶어서 표시
            merged_data = gdp_data_excluded_name.copy()
            total_percent = merged_data['명목'].sum()
            threshold = 0.1
            merged_data['명목'] = merged_data['명목'] / total_percent
            small_values = merged_data[merged_data['명목'] < threshold]

            if len(small_values) > 0:
                other_values = small_values['명목'].sum()
                merged_data.loc[merged_data['명목'] < threshold, '경제활동별'] = '기타'
                merged_data = merged_data.groupby('경제활동별').sum().reset_index()

            # 원형그래프 표시
            st.subheader(f'{selected_option} 경제활동별 생산량 비율')
            fig, ax = plt.subplots(figsize=(8,8))
            ax.pie(merged_data['명목'], labels=merged_data['경제활동별'], autopct='%1.1f%%', startangle=90, textprops={'fontsize':20})
            ax.axis('equal')
            st.pyplot(fig)