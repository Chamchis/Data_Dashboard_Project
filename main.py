import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
from my_packages import region_page
import matplotlib.pyplot as plt

# 한글 폰트 경로 설정
plt.rcParams['font.family'] ='Malgun Gothic'

# 페이지 설정
st.set_page_config(layout='wide')

# 데이터 불러오기 및 인코딩
df_gdp = pd.read_csv('시도별_경제활동별_지역내총생산_20240315165307.csv', encoding='cp949')
per_df_gdp = pd.read_csv('시도별_1인당_지역내총생산__지역총소득__개인소득_20240316162000.csv', encoding='cp949')

# 특정 열만 선택 - 경제활동별 GDP
df_gdp_selected_columns = ['시도별','경제활동별','명목']
gdp_region = df_gdp[df_gdp_selected_columns]

# 특정 열만 선택 - 총 합산 GDP
df_gdp_selected_columns_korea = ['종합_시도별','종합_명목']
gdp_sum = df_gdp[df_gdp_selected_columns_korea]
gdp_sum['종합_명목'] =  gdp_sum['종합_명목'] // 1000000

# 특정 열만 갖고오기 1인당 GDP
df_per_gdp_selected_columns_per_gdp = ['시도별','1인당 지역내총생산']
per_gdp = per_df_gdp[df_per_gdp_selected_columns_per_gdp]

# 빈칸 제거
gdp_region.dropna(inplace=True) # 경제활동별
gdp_sum.dropna(inplace=True) # 총 합산
per_gdp.dropna(inplace=True) # 1인당

# 시/도 리스트
city_list = ['전국', '서울특별시', '부산광역시', '대구광역시', '인천광역시', '광주광역시', '대전광역시', '울산광역시','세종특별자치시']
do_list = ['경기도', '강원도', '충청북도', '충청남도', '전라북도', '전라남도', '경상북도', '경상남도', '제주특별자치도']

# 전국 중심 좌표
korea_center = [36, 127.5]

# 지역별 확대 좌표 
region_center = {
    '서울특별시': [37.5565, 126.9780],
    '부산광역시': [35.1796, 129.0756],
    '대구광역시': [35.8214, 128.6014],
    '인천광역시': [37.5145, 126.4648],
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

# 수치가 높을수록 지도상에 강조
def color_map(data_option, coulmn_option):
    choropleth_layer = folium.Choropleth(
        geo_data=geojson_data,
        data=data_option,
        columns=coulmn_option,
        key_on='feature.properties.name',
        fill_color='YlOrRd',
        fill_opacity=0.7,

        legend_name=''
    ).add_to(korea_map)

# 사이드바 
with st.sidebar:
    st.header('안녕하세요!')
    # 셀렉박스에서 선택한 값을 저장. 시/도를 나타냄
    selected_sido = st.sidebar.selectbox("시/도 선택", city_list + do_list)
    # 전국페이지에서만 지역 총생산, 1인당 총생산을 선택할 수 있는 셀렉박스
    if selected_sido ==  '전국':
        selected_gdp = st.sidebar.selectbox('',['지역 총생산','1인당 총생산'])
    # 사이드바 문구
    st.subheader('자료 출처 : KOSIS 국가통계포털')
    st.text('시도별_경제활동별_지역내총생산_20240\n315165307.csv')
    st.text('시도별_1인당_지역내총생산__지역총소득\n__개인소득_20240316162000.csv')
    st.text('2022년 기준입니다.')

# '전국' 페이지
if selected_sido == '전국':
    # '전국' > '지역 총생산' 페이지
    if selected_gdp == '지역 총생산':
        with st.container():
            col1, col2 ,col3 = st.columns([2,1,1])
            gdp_sum_sorted = gdp_sum.sort_values(by='종합_명목', ascending=False)  # 숫자를 높은 순서대로 정렬
            gdp_sum_sorted = gdp_sum_sorted.rename(columns={'종합_시도별':'시/도','종합_명목':'총생산 (조)'}) # 데이터프레임에 표기되는 문구를 변경
            gdp_sum_sorted = gdp_sum_sorted[gdp_sum_sorted['시/도'] != '전국'] # 지역별 수치를 보여줘야 하므로 전국 항목은 제외함
            with col1: # 지도
                st.subheader('대한민국 총생산 (단위 : 조)')
                color_map(gdp_sum_sorted, ['시/도','총생산 (조)'])
                folium_static(korea_map)

            with col2: # 전국 GDP 데이터 표시
                st.subheader("시/도 순위")
                st.dataframe(gdp_sum_sorted, hide_index=True,width=300,height=510)

            with col3: # 메트릭카드
                max_gdp_location = gdp_sum_sorted.iloc[0]['시/도']
                max_gdp_value = int(gdp_sum_sorted.iloc[0]['총생산 (조)']) # int:정수부분만 표시
                min_gdp_location = gdp_sum_sorted.iloc[-1]['시/도']
                min_gdp_value = int(gdp_sum_sorted.iloc[-1]['총생산 (조)'])

                st.subheader('지역별 최고/최저')
                st.metric(label=max_gdp_location, value=max_gdp_value)
                st.metric(label=min_gdp_location, value=min_gdp_value)

                # 경제활동별 매트릭카드
                economic = gdp_region[gdp_region['시도별'] == '전국'] 
                gdp_region = economic[~economic['경제활동별'].isin(['지역내총생산(시장가격)', '순생산물세', '총부가가치(기초가격)'])] # 합산항목은 제외

                # 최고/최저값 계산
                max_economy_activity = gdp_region[gdp_region['명목'] == gdp_region['명목'].max()]['경제활동별'].values[0]
                max_economy_value = int(gdp_region['명목'].max()) // 1000000

                min_economy_activity = gdp_region[gdp_region['명목'] == gdp_region['명목'].min()]['경제활동별'].values[0]
                min_economy_value = int(gdp_region['명목'].min()) // 1000000

                st.subheader('경제활동별 최고/최저')
                st.metric(label=max_economy_activity, value=max_economy_value)
                st.metric(label=min_economy_activity, value=min_economy_value)
                
            col4, col5 = st.columns(2)
            with col4:
                # 상위 5개의 데이터만 추출
                gdp_region = gdp_region[gdp_region['경제활동별'].isin(['농업, 임업 및 어업', '광제조업',
                                        '전기, 가스, 증기 및 공기 조절 공급업','건설업','서비스업'])]
                top_5_gdp = gdp_region.nlargest(5, '명목')
                # 경제활동별 생산량 그래프
                plt.figure(figsize=(6, 4))
                plt.bar(top_5_gdp['경제활동별'], top_5_gdp['명목'] // 1000000) 
                plt.xlabel('경제활동별')
                plt.ylabel('총생산')
                plt.title('상위 5개 경제활동별 생산량 그래프')
                plt.xticks(rotation=45, ha='right')
                st.pyplot(plt)
            with col5:
                # 가독성을 위하여 일정 수치 이하는 '기타'로 묶어서 표시
                threshold = 80
                small_values = gdp_sum_sorted[gdp_sum_sorted['총생산 (조)'] < threshold]
                merged_data = gdp_sum_sorted.copy()
                if len(small_values) > 0:
                    merged_data.loc[merged_data['총생산 (조)'] < threshold, '시/도'] = '기타'
                    merged_data = merged_data.groupby('시/도').sum().reset_index()
                # 원형그래프 표시
                st.subheader('전국 생산량 비율')
                fig, ax = plt.subplots(figsize=(8,8))
                ax.pie(merged_data['총생산 (조)'], labels=merged_data['시/도'], autopct='%1.1f%%', startangle=90, textprops={'fontsize':20})
                ax.axis('equal')
                st.pyplot(fig)


    elif selected_gdp == '1인당 총생산':
        with st.container():
            col1, col2 ,col3 = st.columns([2,1,1])
            per_gdp = per_gdp.rename(columns={'시도별':'시/도','1인당 지역내총생산':'총생산 (달러)'})
            with col1:
                # 지도
                st.subheader('대한민국 1인당 총생산')
                color_map(per_gdp, ['시/도','총생산 (달러)'])
                folium_static(korea_map)
            with col2:
                # 전국 1인당 GDP 데이터 표시
                per_gdp = per_gdp[per_gdp['시/도'] != '전국']
                st.subheader('시/도 순위')
                per_gdp_sorted = per_gdp.sort_values(by='총생산 (달러)',ascending=False)
                st.dataframe(per_gdp_sorted,hide_index=True,width=300,height=510)
            with col3:
                # 메트릭카드
                max_per_gdp_location = per_gdp_sorted.iloc[0]['시/도']
                max_per_gdp_value = int(per_gdp_sorted.iloc[0]['총생산 (달러)']) # int:정수부분만 표시
                min_per_gdp_location = per_gdp_sorted.iloc[-1]['시/도']
                min_per_gdp_value = int(per_gdp_sorted.iloc[-1]['총생산 (달러)'])


                st.subheader('지역별 최고/최저 (달러)')
                st.metric(label=max_per_gdp_location, value=max_per_gdp_value)
                st.metric(label=min_per_gdp_location, value=min_per_gdp_value)
                st.subheader('세계/전국 평균 (달러)')
                st.metric('세계 평균', 13870)
                st.metric('전국 평균', 41948)

            col4, col5 = st.columns(2)
            with col4:
                # 상위 10개의 데이터만 추출
                per_gdp_sorted = per_gdp_sorted[per_gdp_sorted['시/도'] != '전국']
                top_10_per_gdp = per_gdp_sorted.nlargest(10, '총생산 (달러)')
                # 막대그래프 표시
                plt.figure(figsize=(6,4))
                plt.bar(top_10_per_gdp['시/도'], top_10_per_gdp['총생산 (달러)'])
                plt.title('상위 10개 지역 1인당 총생산')
                plt.xlabel('지역별 (달러)')
                plt.ylabel('총생산')
                plt.xticks(rotation=45, ha='right', fontsize=8) # 글자가 겹침
                st.pyplot(plt)
            with col5:
                gdp_per_capita = {
                    '국가': ['중국', '일본', '러시아', '영국', '미국', '한국'],
                    '1인당 GDP': [12621, 33949, 12593, 46066, 80034, 32423]
                }
                gdp_per_capita_data = pd.DataFrame(gdp_per_capita)
                gdp_per_capita_data = gdp_per_capita_data.sort_values(by='1인당 GDP',ascending=False)
                # 막대그래프 표시
                plt.figure(figsize=(6,4))
                plt.bar(gdp_per_capita_data['국가'], gdp_per_capita_data['1인당 GDP'])
                plt.title('세계 주요국 1인당 총생산')
                plt.xlabel('국가별 (달러)')
                plt.ylabel('총생산')
                plt.xticks(rotation=45,ha='right',fontsize=8)
                st.pyplot(plt)
else: # 셀렉박스에서 다른 지역을 선택했을때
    # 시/도에 따라 줌을 다르게 설정
    if selected_sido in city_list:
        zoom = 9
    else:
        zoom = 7
    # 선택한 지역 지도
    region_map = folium.Map(location=region_center[selected_sido], zoom_start = zoom, tiles='CartoDB positron')
    # 마커 표시
    folium.Marker(
        location=region_center[selected_sido],
        tooltip=f"{selected_sido}"
    ).add_to(region_map)
    folium.GeoJson(geojson_data, name='geojson_map').add_to(region_map)
    region_page.show_region(gdp_region,per_gdp,region_map,selected_sido)
