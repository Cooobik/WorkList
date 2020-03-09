import requests
from lxml import etree
from bs4 import BeautifulSoup
from datetime import datetime
import re
import pprint
#import wget
from mysql.connector import MySQLConnection, Error
#from python_mysql_dbconfig import read_db_config
import mysql.connector



#-----------------------------------------------------------------------------
#WGET
#wget.download('href')

#-----------------------------------------------------------------------------







#-----------------------------------------------------------------------------
#Connect to DataBase
mydb = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "Вшьф_1999",
        database= "aim_dev_eu"
    )
#-----------------------------------------------------------------------------






#-----------------------------------------------------------------------------
#First Parse to DB
def insert_args(args):
    
    query = "INSERT INTO eu_nc_update_log(date_update,name_file_update,date_date) VALUES(%s,%s,%s)"
    cursor=mydb.cursor()
    try:
        
        cursor.executemany(query, args)
        #mydb.commit()

    except Error as e:
        print('Error:', e)
    finally:
        cursor.close()
        #mydb.close()
#-----------------------------------------------------------------------------







#-----------------------------------------------------------------------------
#Check last Date update in DB
def check_last_date_update_in_DB():
    cursor=mydb.cursor()
    try:
        cursor.execute("SELECT MAX(date_date) FROM eu_nc_update_log")
        last_date_update = cursor.fetchall()
        #print(last_date_update)    
    except Error as e:
        print('Error:', e)
    finally:
        cursor.close()
        mydb.close()


#-----------------------------------------------------------------------------








#-----------------------------------------------------------------------------
#Script
DATE_REGEX = r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}'
FILENAME_REGEX = r'\w+\.7z'

def get_html(url):
    req = requests.get(url)
    return req.text

def get_all_info(html):
    list_of_site_parse = list()
    date_now = datetime.now()
    soup = BeautifulSoup(html, 'lxml')
    trs = soup.find('table').find_all('tr', class_ = 'mouseout')
    
    for tr in trs:         
        try:
            date_td = tr.findChildren('td',text = re.compile(DATE_REGEX))
            if len(date_td) > 0:
                ndate = datetime.strptime(date_td[0].text[2:], "%d/%m/%Y %H:%M:%S")
                #if ndate > last_date_update
                    #download_apdate = tr.findChildren('td').get('href')
                files = tr.findChildren('td')
                for file_name in files:
                    filename = file_name.findChildren('a', text = re.compile(FILENAME_REGEX))
                    if len(filename)>0:                   
                        list_of_site_parse.append((date_now, filename[0].text, ndate))
                         
        except ValueError as ve:
            print('ValueError Raised:', ve)        
    pp = pprint.PrettyPrinter(indent=0)
    pp.pprint(list_of_site_parse)
    return list_of_site_parse
#-----------------------------------------------------------------------------







#-----------------------------------------------------------------------------
def main():
    url = 'https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&dir=comext/COMEXT_DATA/PRODUCTS'
    check_last_date_update_in_DB()

    all_info_from_site = get_all_info(get_html(url))
    insert_args(all_info_from_site)
    
    


if __name__ == '__main__':
    main()
#-----------------------------------------------------------------------------