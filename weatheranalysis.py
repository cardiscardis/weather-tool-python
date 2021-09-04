from datetime import time
from numpy import product
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import base64


st.set_page_config(
    page_title='Australian Weather Aanlytics',
    page_icon='📈',
    layout='wide'
)



def get_table_download_link(dataframe):
            """Generates a link allowing the data in a given panda dataframe to be downloaded
            in:  dataframe
            out: href string
            """
            csv = dataframe.to_csv()
            b64 = base64.b64encode(csv.encode()).decode('utf-8')  # some strings <-> bytes conversions necessary here
            href = f'<a href="data:file/csv;base64,{b64}" download="output.csv">Download csv file output</a>'
            return href

st.title('Australian Weather Analysis.')
st.subheader('Please enter the desired csv file')
upload_file = st.file_uploader(label='Please enter the desired csv file')
weather = pd.read_csv(upload_file)

year_select = st.slider(label='Select Year Range', 
    min_value=min(weather['Year'].tolist()),
    max_value=max(weather['Year'].tolist()),
    value=(min(weather['Year'].tolist()),max(weather['Year'].tolist())))
product_code = weather['Product code'].unique().tolist()
section_select = weather['Bureau of Meteorology station number'].unique().tolist()
section_selection = st.multiselect(label='Select Sections', options=section_select, default=section_select)
product_selection = st.multiselect(label='Select Product Codes', 
    options=product_code, default=product_code)
month_select = st.slider(label='Select Months', min_value=1, max_value=12, value=(1,12))    
dates_select = st.slider(label='Select Dtaes', min_value=1, max_value=31, value=(1,31))
filter = (weather['Year'].between(*year_select)) & (weather['Bureau of Meteorology station number'].isin(section_selection)) & (weather['Product code'].isin(product_selection)) & (weather['Month'].between(*month_select)) & (weather['Day'].between(*dates_select))
weather = weather[filter]
st.write(weather)

st.markdown(get_table_download_link(dataframe=weather), unsafe_allow_html=True)
def main(data):
    monthly_rainfall = px.bar(
        data_frame=data,
        x = 'Month',
        y = 'Rainfall amount (millimetres)',
        color = 'Year',
        animation_frame='Year',
        title='Monthly Rainfall',
        hover_data=['Period over which rainfall was measured (days)','Period over which rainfall was measured (days)']
    )
    st.title(
        'Monthly Rainfall'
    )
    st.plotly_chart(monthly_rainfall)

    daily_rainfall = px.bar(
        data_frame=data,
        x = 'Day',
        y = 'Rainfall amount (millimetres)',
        color = 'Month',
        animation_frame='Year',
        hover_data=['Period over which rainfall was measured (days)','Period over which rainfall was measured (days)']
    )
    daily_rainfall.update_layout(transition = {'duration': 5000})
    st.title('Daily Rainfall')
    st.plotly_chart(daily_rainfall)


    rain_by_year =data.groupby(by='Year')['Rainfall amount (millimetres)'].sum().reset_index()
    
    rain_by_year_bar = px.bar(
        data_frame=rain_by_year,
        x='Year',
        y='Rainfall amount (millimetres)',
        title = 'Total Rain By Year'
    )
    st.title('Total rain by year')
    st.write(rain_by_year)
    st.markdown(get_table_download_link(dataframe=rain_by_year), unsafe_allow_html=True)
    st.plotly_chart(rain_by_year_bar)



    rain_by_year_avg =data.groupby(by='Year')['Rainfall amount (millimetres)'].mean().reset_index()

    rain_by_year_avg_line = px.line(
        data_frame=rain_by_year_avg,
        x='Year',
        y='Rainfall amount (millimetres)',
        title= 'Average Rain By Year'
    )
    st.title('Average rain per year')
    st.write(rain_by_year_avg)
    st.markdown(get_table_download_link(dataframe=rain_by_year_avg), unsafe_allow_html=True)
    st.plotly_chart(rain_by_year_avg_line)


    rain_by_year_month_avg =data.groupby(['Year', 'Month'])['Rainfall amount (millimetres)'].mean().reset_index()
   
    rain_by_year_month_avg_bar = px.bar(
        data_frame=rain_by_year_month_avg,
        x='Month',
        y='Rainfall amount (millimetres)',
        color = 'Year',
        title = 'Average Rain By Month',
        animation_frame='Year'
    )
    rain_by_year_month_avg_bar.update_layout(transition = {'duration': 5000})
    st.title('Average rain per month on yearly basis')
    st.write(rain_by_year_month_avg)
    st.markdown(get_table_download_link(dataframe=rain_by_year_month_avg), unsafe_allow_html=True)
    st.plotly_chart(rain_by_year_month_avg_bar)



Spring = [8,9,10]
Summer = [12,1,2]
Autumn = [3,4,5]
Winter = [6,7,8]
sessions = {
        'Spring' : Spring,
        'Summer'  : Summer,
        'Autumn'  : Autumn,
        'Winter' : Winter
        }

main(data=weather)


for key, value in sessions.items():
    st.title(f'Data By {key}')
    filter = (weather['Month'].isin(value))
    main(data=weather[filter])
    
OJ = [x for x in range(1,10)]
Aj = [x for x in range(1,8)]
SJ = [x for x in range(1,9)]
time_spans = {
    'October to January' : OJ,
    'August to January' : Aj,
    'September to January' : SJ
}
for key, value in time_spans.items():
    st.title(f'Data By {key}')
    filter = (weather['Month'].isin(value))
    main(data=weather[filter])



