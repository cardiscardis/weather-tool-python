# -*- coding: utf-8 -*-
"""
Created on Tue Sep  7 07:08:16 2021

@author: EMMANUEL
"""

# import the module
import pandas as pd
from sqlalchemy import create_engine
import mysql.connector as msql
from mysql.connector import Error
from bs4 import BeautifulSoup
import requests
from io import BytesIO
from zipfile import ZipFile

#remember to install lmxl and pymysql

#database data
host = 'localhost'
database= 'weatherToolDB'
user= 'root'
password = ''

# initialize stations and their codes. This may be extended to as many stations as there is. I used only 3 stations
stationData = [['Bowral', 'Post Office (closed)', '68005'], ['Bowral', 'Bowral (Parry Drive)', '68102'], \
        ['Braidwood', 'Braidwood (Wallace St)', '69010']]
        

#variables:
link = ''
agent = {'User-Agent': 'Chrome/92.0.4515.159'}
mydb = ''
cursor = ''
engine = ''

try:
    #connect to mysql host
    conn = msql.connect(host=host, user=user, password=password)
    if conn.is_connected():
        cursor = conn.cursor()        
        
        #create database if it doesn't exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS weatherToolDB")
    print("database is created")

    #connect to database
    conn = msql.connect(host="localhost", database=database, user="root", password="",use_pure=True)    
    if conn.is_connected():
        cursor = conn.cursor()
    
    #select database    
    cursor.execute("select database();")
    record = cursor.fetchone()
    print("You're connected to database: ", record)  
    
    #Create Stations Table if it doesn't exist    
    print('Creating station table....')    
    #query = "CREATE TABLE IF NOT EXISTS station (station_name CHAR(50), sub_station_name CHAR(100), station_code INT(5))"
    #cursor.execute(query)
    #print("station table is created....")    
 
    # Create the pandas DataFrame for station data
    stationDF = pd.DataFrame(stationData, columns = ['station', 'sub_station', 'code'])
    
    # create sqlalchemy engine
    engine = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}"  
            .format(user=user, pw=password, db=database))

    # Insert whole station DataFrame into MySQL
    stationDF.to_sql('station', con = engine, if_exists = 'replace', chunksize = 1000,index=False)
    print('station table created and data inserted')
    
    #select station code whose data to download and compose page url
    cursor.execute("SELECT code FROM station")
    c = cursor.fetchall()    
    codes = next(zip(*c))
                
    if codes:        
        for code in codes:
            root = 'http://www.bom.gov.au/jsp/ncc/cdio/weatherData/av?p_nccObsCode=136&p_display_type=dailyDataFile&p_startYear=&p_c=&p_stn_num='                    

            pageUrl = requests.get(f'{root}{code}', headers=agent)
            content = pageUrl.text              
            
            #Get csv download link
            soup = BeautifulSoup(content, 'lxml')                      
            anchor = soup.find('a', title='Data file for daily rainfall data for all years')                  
    
            if anchor:
               link = anchor.get('href')
               print(link)
            else:
               print("anchor not found")    
             
            url = "http://www.bom.gov.au"    
            filename = requests.get(f'{url}/{link}', headers=agent).content
            zf = ZipFile( BytesIO(filename), 'r' )
            
            for item in zf.namelist():
                print("File in zip: "+ item)
                    
            match = [s for s in zf.namelist() if ".csv" in s][0]    
            df = pd.read_csv( zf.open(match), names=list(range(8)), encoding='latin-1', delimiter=',', header=0)      
            print(df.head())
            df = df.iloc[1: , :]    
            df = df.fillna(-1)    
            df.columns = ['product_code', 'station_number', 'year', 'month', 'day', 'rainfall_amount', \
                          'measure_in_days', 'quality']           
                
            df.to_sql('rain' + code, con = engine, if_exists = 'replace', chunksize = 1000,index=False)
            print('rain' + code + ' table created and data inserted')       
        
        #Extract Min Temp Data
        for code in codes:
            root = 'http://www.bom.gov.au/jsp/ncc/cdio/weatherData/av?p_nccObsCode=123&p_display_type=dailyDataFile&p_startYear=&p_c=&p_stn_num='        
            pageUrl = requests.get(f'{root}{code}', headers=agent)
            content = pageUrl.text              
            
            #Get csv download link
            soup = BeautifulSoup(content, 'lxml')                      
            anchor = soup.find('a', title='Data file for daily minimum temperature data for all years')                  
    
            if anchor:
               link = anchor.get('href')
               print(link)
            else:
               print("anchor not found")    
             
            url = "http://www.bom.gov.au"    
            filename = requests.get(f'{url}/{link}', headers=agent).content
            zf = ZipFile( BytesIO(filename), 'r' )
            
            for item in zf.namelist():
                print("File in zip: "+ item)
                    
            match = [s for s in zf.namelist() if ".csv" in s][0]    
            df = pd.read_csv( zf.open(match), names=list(range(8)), encoding='latin-1', delimiter=',', header=0)      
            print(df.head())
            df = df.iloc[1: , :]    
            df = df.fillna(-1)    
            df.columns = ['product_code', 'station_number', 'year', 'month', 'day', 'min_temp_celsius', \
                          'days_of_accumulation', 'quality']           
                
            df.to_sql('min_temp' + code, con = engine, if_exists = 'replace', chunksize = 1000,index=False)
            print('max_temp' + code + ' table created and data inserted')       
            
            
        #Get Max Temp Data:
        for code in codes:
            root = 'http://www.bom.gov.au/jsp/ncc/cdio/weatherData/av?p_nccObsCode=122&p_display_type=dailyDataFile&p_startYear=&p_c=&p_stn_num='     
            pageUrl = requests.get(f'{root}{code}', headers=agent)
            content = pageUrl.text              
            
            #Get csv download link
            soup = BeautifulSoup(content, 'lxml')                      
            anchor = soup.find('a', title='Data file for daily maximum temperature data for all years')                  
    
            if anchor:
               link = anchor.get('href')
               print(link)
            else:
               print("anchor not found")    
             
            url = "http://www.bom.gov.au"    
            filename = requests.get(f'{url}/{link}', headers=agent).content
            zf = ZipFile( BytesIO(filename), 'r' )
            
            for item in zf.namelist():
                print("File in zip: "+ item)
                    
            match = [s for s in zf.namelist() if ".csv" in s][0]    
            df = pd.read_csv( zf.open(match), names=list(range(8)), encoding='latin-1', delimiter=',', header=0)      
            print(df.head())
            df = df.iloc[1: , :]    
            df = df.fillna(-1)    
            df.columns = ['product_code', 'station_number', 'year', 'month', 'day', 'max_temp_celsius', \
                          'days_of_accumulation', 'quality']           
                
            df.to_sql('max_temp' + code, con = engine, if_exists = 'replace', chunksize = 1000,index=False)
            print('max_temp' + code + ' table created and data inserted')       
            
            
        #Get Solar Exposure Data:
        for code in codes:
            root = 'http://www.bom.gov.au/jsp/ncc/cdio/weatherData/av?p_nccObsCode=193&p_display_type=dailyDataFile&p_startYear=&p_c=&p_stn_num='     
            pageUrl = requests.get(f'{root}{code}', headers=agent)
            content = pageUrl.text              
            
            #Get csv download link
            soup = BeautifulSoup(content, 'lxml')                      
            anchor = soup.find('a', title='Data file for daily global solar exposure data for all years')                  
    
            if anchor:
               link = anchor.get('href')
               print(link)
            else:
               print("anchor not found")    
             
            url = "http://www.bom.gov.au"    
            filename = requests.get(f'{url}/{link}', headers=agent).content
            zf = ZipFile( BytesIO(filename), 'r' )
            
            for item in zf.namelist():
                print("File in zip: "+ item)
                    
            match = [s for s in zf.namelist() if ".csv" in s][0]    
            df = pd.read_csv( zf.open(match), names=list(range(6)), encoding='latin-1', delimiter=',', header=0)      
            print(df.head())
            df = df.iloc[1: , :]    
            df = df.fillna(-1)    
            df.columns = ['product_code', 'station_number', 'year', 'month', 'day', 'solar_exposure']           
                
            df.to_sql('solar' + code, con = engine, if_exists = 'replace', chunksize = 1000,index=False)
            print('solar' + code + ' table created and data inserted')       
        
    # Close the connection
    if (conn.is_connected()):
        cursor.close()
        conn.close()
        print('MySQL connection is closed')
except Error as e:
    print("Error while connecting to MySQL", e)
