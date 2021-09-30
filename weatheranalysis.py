#from datetime import time
#from numpy import product
import pandas as pd
import plotly.express as px
#import plotly.graph_objects as go
import streamlit as st
import base64
import mysql.connector as msql
#from mysql.connector import Error

st.set_page_config(
    page_title='Australian Weather Aanlytics',
    page_icon='📈',
    layout='wide'
)
    
#define variables
wo = '' #weather option

# Initialize connection.
# Uses st.cache to only run once.
@st.cache(allow_output_mutation=True, hash_funcs={"_thread.RLock": lambda _: None})
def init_connection():
    return msql.connect(**st.secrets["mysql"])   

# Perform query.
# Uses st.cache to only rerun when the query changes or after 10 min.
#@st.cache(ttl=600)
def run_query(query, conn):    
    result_dataFrame = pd.read_sql(query, conn)    
    #conn.close() #close the connection
    return result_dataFrame    

def run_query_with_params(query, connection, column_list):        
    with connection as conn:        
        df = pd.read_sql(query, conn)
        return df

def get_table_download_link(dataframe):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = dataframe.to_csv()
    b64 = base64.b64encode(csv.encode()).decode('utf-8')  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="output.csv">Download csv file output</a>'
    return href

#initialize connection
conn = init_connection()

#Get Station Codes
q = "Select code from station;"
code = run_query(q, conn)

#page title
st.title('Australian Weather Analysis.')
st.subheader('Please select the desired data to view')

#Define Controls
weather_option = st.selectbox('Weather Type', ('Rainfall', 'Minimum Temperature', 'Maximum Temperature', 'Solar Exposure'))
station_option = st.selectbox('Station Option', code)

#Map choice with database columns
if weather_option == 'Rainfall':
    wo = 'rain'
elif weather_option == 'Minimum Temperature':
    wo = 'min_temp'
elif weather_option == 'Maximum Temperature':
    wo = 'max_temp'
elif weather_option == 'Solar Exposure':
    wo = 'solar'  

#Get user desired info
query = "select * from {}".format(''.join([wo + '' + station_option]))# * len([wo, station_option])))
weather = run_query_with_params(query, conn, [wo, station_option])

#upload_file = st.file_uploader(label='Please enter the desired csv file')
weather = weather.replace('-1', None)
weather = weather.replace(-1, None)

st.write(weather.head())
#weather = pd.read_csv(upload_file)

year_select = st.slider(label='Select Year Range', 
    min_value=min(weather['year'].tolist()),
    max_value=max(weather['year'].tolist()),
    value=(min(weather['year'].tolist()),max(weather['year'].tolist())))

product_code = weather['product_code'].unique().tolist()
section_select = weather['station_number'].unique().tolist()

section_selection = st.multiselect(label='Select Sections', options=section_select, default=section_select)
product_selection = st.multiselect(label='Select Product Codes', options=product_code, default=product_code)
month_select = st.slider(label='Select Months', min_value=1, max_value=12, value=(1,12))    
dates_select = st.slider(label='Select Dtaes', min_value=1, max_value=31, value=(1,31))
filter = (weather['year'].between(*year_select)) & (weather['station_number'].isin(section_selection)) & (weather['product_code'].isin(product_selection)) & (weather['month'].between(*month_select)) & (weather['day'].between(*dates_select))
weather = weather[filter]
st.write(weather)

if weather_option == 'Rainfall':
    st.markdown(get_table_download_link(dataframe=weather), unsafe_allow_html=True)
    def main(data):
        monthly_rainfall = px.bar(
            data_frame=data,
            x = 'month',
            y = 'rainfall_amount',
            color = 'year',
            animation_frame='year',
            title='Monthly Rainfall',
            hover_data=['measure_in_days','measure_in_days']
        )
        st.title(
            'Monthly Rainfall'
        )
        st.plotly_chart(monthly_rainfall)
    
        daily_rainfall = px.bar(
            data_frame=data,
            x = 'day',
            y = 'rainfall_amount',
            color = 'month',
            animation_frame='year',
            hover_data=['measure_in_days','measure_in_days']
        )
        daily_rainfall.update_layout(transition = {'duration': 5000})
        st.title('Daily Rainfall')
        st.plotly_chart(daily_rainfall)
    
    
        rain_by_year =data.groupby(by='year')['rainfall_amount'].sum().reset_index()
        
        rain_by_year_bar = px.bar(
            data_frame=rain_by_year,
            x='year',
            y='rainfall_amount',
            title = 'Total Rain By Year'
        )
        st.title('Total rain by year')
        st.write(rain_by_year)
        st.markdown(get_table_download_link(dataframe=rain_by_year), unsafe_allow_html=True)
        st.plotly_chart(rain_by_year_bar)
    
    
    
        rain_by_year_avg =data.groupby(by='year')['rainfall_amount'].mean().reset_index()
    
        rain_by_year_avg_line = px.line(
            data_frame=rain_by_year_avg,
            x='year',
            y='rainfall_amount',
            title= 'Average Rain By Year'
        )
        st.title('Average rain per year')
        st.write(rain_by_year_avg)
        st.markdown(get_table_download_link(dataframe=rain_by_year_avg), unsafe_allow_html=True)
        st.plotly_chart(rain_by_year_avg_line)
    
    
        rain_by_year_month_avg =data.groupby(['year', 'month'])['rainfall_amount'].mean().reset_index()
       
        rain_by_year_month_avg_bar = px.bar(
            data_frame=rain_by_year_month_avg,
            x='month',
            y='rainfall_amount',
            color = 'year',
            title = 'Average Rain By Month',
            animation_frame='year'
        )
        rain_by_year_month_avg_bar.update_layout(transition = {'duration': 5000})
        st.title('Average rain per month on yearly basis')
        st.write(rain_by_year_month_avg)
        st.markdown(get_table_download_link(dataframe=rain_by_year_month_avg), unsafe_allow_html=True)
        st.plotly_chart(rain_by_year_month_avg_bar)
#weather_option = st.selectbox('Weather Type', ('Rainfall', 'Minimum Temperature', 'Maximum Temperature', 'Solar Exposure'))
elif weather_option == 'Minimum Temperature':
    st.markdown(get_table_download_link(dataframe=weather), unsafe_allow_html=True)
    def main(data):
        monthly_temp = px.bar(
            data_frame=data,
            x = 'month',
            y = 'min_temp_celsius',
            color = 'year',
            animation_frame='year',
            title='Monthly Minimum Temperature',
            hover_data=['days_of_accumulation','days_of_accumulation']
        )
        st.title(
            'Monthly Minimum Temperature'
        )
        st.plotly_chart(monthly_temp)
    
        daily_min_temp = px.bar(
            data_frame=data,
            x = 'day',
            y = 'min_temp_celsius',
            color = 'month',
            animation_frame='year',
            hover_data=['days_of_accumulation','days_of_accumulation']
        )
        daily_min_temp.update_layout(transition = {'duration': 5000})
        st.title('Daily Minimum Temperature')
        st.plotly_chart(daily_min_temp)
    
    
        min_temp_by_year = data.groupby(by='year')['min_temp_celsius'].sum().reset_index()
        
        min_temp_by_year_bar = px.bar(
            data_frame=min_temp_by_year,
            x='year',
            y='min_temp_celsius',
            title = 'Total Minimum Temperature By Year'
        )
        st.title('Total minimum Temperature by year')
        st.write(min_temp_by_year)
        st.markdown(get_table_download_link(dataframe=min_temp_by_year), unsafe_allow_html=True)
        st.plotly_chart(min_temp_by_year_bar)
    
    
    
        min_temp_by_year_avg =data.groupby(by='year')['min_temp_celsius'].mean().reset_index()
    
        min_temp_by_year_avg_line = px.line(
            data_frame=min_temp_by_year_avg,
            x='year',
            y='min_temp_celsius',
            title= 'Average Minimum Temperature By Year'
        )
        st.title('Average Minimum Temperature per year')
        st.write(min_temp_by_year_avg)
        st.markdown(get_table_download_link(dataframe=min_temp_by_year_avg), unsafe_allow_html=True)
        st.plotly_chart(min_temp_by_year_avg_line)
    
    
        min_temp_by_year_month_avg =data.groupby(['year', 'month'])['min_temp_celsius'].mean().reset_index()
       
        min_temp_by_year_month_avg_bar = px.bar(
            data_frame=min_temp_by_year_month_avg,
            x='month',
            y='min_temp_celsius',
            color = 'year',
            title = 'Average Minimum Temperature By Month',
            animation_frame='year'
        )
        min_temp_by_year_month_avg_bar.update_layout(transition = {'duration': 5000})
        st.title('Average Minimum Temperature per month on yearly basis')
        st.write(min_temp_by_year_month_avg)
        st.markdown(get_table_download_link(dataframe=min_temp_by_year_month_avg), unsafe_allow_html=True)
        st.plotly_chart(min_temp_by_year_month_avg_bar)
#weather_option = st.selectbox('Weather Type', ('Rainfall', 'Minimum Temperature', 'Maximum Temperature', 'Solar Exposure'))
elif weather_option == 'Maximum Temperature':
    st.markdown(get_table_download_link(dataframe=weather), unsafe_allow_html=True)
    def main(data):
        monthly_temp = px.bar(
            data_frame=data,
            x = 'month',
            y = 'max_temp_celsius',
            color = 'year',
            animation_frame='year',
            title='Monthly Maximum Temperature',
            hover_data=['days_of_accumulation','days_of_accumulation']
        )
        st.title(
            'Monthly Maximum Temperature'
        )
        st.plotly_chart(monthly_temp)
    
        daily_max_temp = px.bar(
            data_frame=data,
            x = 'day',
            y = 'max_temp_celsius',
            color = 'month',
            animation_frame='year',
            hover_data=['days_of_accumulation','days_of_accumulation']
        )
        daily_max_temp.update_layout(transition = {'duration': 5000})
        st.title('Daily Maximum Temperature')
        st.plotly_chart(daily_max_temp)
    
    
        max_temp_by_year = data.groupby(by='year')['max_temp_celsius'].sum().reset_index()
        
        max_temp_by_year_bar = px.bar(
            data_frame=max_temp_by_year,
            x='year',
            y='max_temp_celsius',
            title = 'Total Maximum Temperature By Year'
        )
        st.title('Total Maximum Temperature by year')
        st.write(max_temp_by_year)
        st.markdown(get_table_download_link(dataframe=max_temp_by_year), unsafe_allow_html=True)
        st.plotly_chart(max_temp_by_year_bar)
    
    
    
        max_temp_by_year_avg =data.groupby(by='year')['max_temp_celsius'].mean().reset_index()
    
        max_temp_by_year_avg_line = px.line(
            data_frame=max_temp_by_year_avg,
            x='year',
            y='max_temp_celsius',
            title= 'Average Maximum Temperature By Year'
        )
        st.title('Average Maximum Temperature per year')
        st.write(max_temp_by_year_avg)
        st.markdown(get_table_download_link(dataframe=max_temp_by_year_avg), unsafe_allow_html=True)
        st.plotly_chart(max_temp_by_year_avg_line)
    
    
        max_temp_by_year_month_avg =data.groupby(['year', 'month'])['max_temp_celsius'].mean().reset_index()
       
        max_temp_by_year_month_avg_bar = px.bar(
            data_frame=max_temp_by_year_month_avg,
            x='month',
            y='max_temp_celsius',
            color = 'year',
            title = 'Average Maximum Temperature By Month',
            animation_frame='year'
        )
        max_temp_by_year_month_avg_bar.update_layout(transition = {'duration': 5000})
        st.title('Average Maximum Temperature per month on yearly basis')
        st.write(max_temp_by_year_month_avg)
        st.markdown(get_table_download_link(dataframe=max_temp_by_year_month_avg), unsafe_allow_html=True)
        st.plotly_chart(max_temp_by_year_month_avg_bar)
#weather_option = st.selectbox('Weather Type', ('Rainfall', 'Minimum Temperature', 'Maximum Temperature', 'Solar Exposure'))
elif weather_option == 'Solar Exposure':
    st.markdown(get_table_download_link(dataframe=weather), unsafe_allow_html=True)
    def main(data):
        monthly_exp = px.bar(
            data_frame=data,
            x = 'month',
            y = 'solar_exposure',
            color = 'year',
            animation_frame='year',
            title='Monthly Solar Exposure',
            #hover_data=['days_of_accumulation','days_of_accumulation']
        )
        st.title(
            'Monthly Solar Exposure'
        )
        st.plotly_chart(monthly_exp)
    
        daily_exp = px.bar(
            data_frame=data,
            x = 'day',
            y = 'solar_exposure',
            color = 'month',
            animation_frame='year',
            #hover_data=['days_of_accumulation','days_of_accumulation']
        )
        daily_exp.update_layout(transition = {'duration': 5000})
        st.title('Daily Solar Exposure')
        st.plotly_chart(daily_exp)
    
    
        exp_by_year = data.groupby(by='year')['solar_exposure'].sum().reset_index()
        
        exp_by_year_bar = px.bar(
            data_frame=exp_by_year,
            x='year',
            y='solar_exposure',
            title = 'Total Solar Exposure By Year'
        )
        st.title('Total Solar Exposure by year')
        st.write(exp_by_year)
        st.markdown(get_table_download_link(dataframe=exp_by_year), unsafe_allow_html=True)
        st.plotly_chart(exp_by_year_bar)
    
    
    
        exp_by_year_avg =data.groupby(by='year')['solar_exposure'].mean().reset_index()
    
        exp_by_year_avg_line = px.line(
            data_frame=exp_by_year_avg,
            x='year',
            y='solar_exposure',
            title= 'Average Solar Exposure By Year'
        )
        st.title('Average Solar Exposure per year')
        st.write(exp_by_year_avg)
        st.markdown(get_table_download_link(dataframe=exp_by_year_avg), unsafe_allow_html=True)
        st.plotly_chart(exp_by_year_avg_line)
    
    
        exp_by_year_month_avg =data.groupby(['year', 'month'])['solar_exposure'].mean().reset_index()
       
        exp_by_year_month_avg_bar = px.bar(
            data_frame=exp_by_year_month_avg,
            x='month',
            y='solar_exposure',
            color = 'year',
            title = 'Average Solar Exposure By Month',
            animation_frame='year'
        )
        exp_by_year_month_avg_bar.update_layout(transition = {'duration': 5000})
        st.title('Average Solar Exposure per month on yearly basis')
        st.write(exp_by_year_month_avg)
        st.markdown(get_table_download_link(dataframe=exp_by_year_month_avg), unsafe_allow_html=True)
        st.plotly_chart(exp_by_year_month_avg_bar)
        
        
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
    filter = (weather['month'].isin(value))
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
    filter = (weather['month'].isin(value))
    main(data=weather[filter])