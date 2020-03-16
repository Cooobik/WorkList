import requests
from lxml import etree
from bs4 import BeautifulSoup
from datetime import datetime
import re
import pprint
import wget
from mysql.connector import MySQLConnection, Error
import mysql.connector
from pyunpack import Archive
import os





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
        # mydb.commit()

    except Error as e:
        print('Error:', e)
    finally:
        cursor.close()
        mydb.close()
#-----------------------------------------------------------------------------






#-----------------------------------------------------------------------------
#Check last Date update in DB
def check_last_date_update_in_DB():
    cursor=mydb.cursor()
    try:
        cursor.execute("SELECT MAX(date_date) FROM eu_nc_update_log")
        last_date_update = cursor.fetchall()    
    except Error as e:
        print('Error:', e)
    finally:
        cursor.close()
        # mydb.close()
    return last_date_update


#-----------------------------------------------------------------------------








#-----------------------------------------------------------------------------
#Script
DATE_REGEX = r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}'
FILENAME_REGEX = r'\w+\.7z'

def get_html(url):
    req = requests.get(url) 
    return req.text

# def get_all_info(html):
#     list_of_site_parse = list()
#     date_now = datetime.now()
#     soup = BeautifulSoup(html, 'lxml')
#     trs = soup.find('table').find_all('tr', class_ = 'mouseout')
    
#     for tr in trs:         
#         try:
#             date_td = tr.findChildren('td',text = re.compile(DATE_REGEX))
#             if len(date_td) > 0:
#                 ndate = datetime.strptime(date_td[0].text[2:], "%d/%m/%Y %H:%M:%S") 
#                 files = tr.findChildren('td')
#                 for file_name in files:
#                     filename = file_name.findChildren('a', text = re.compile(FILENAME_REGEX))
#                     if len(filename)>0:                   
#                         list_of_site_parse.append((date_now, filename[0].text, ndate))                  
#         except ValueError as ve:
#             print('ValueError Raised:', ve)        
#     pp = pprint.PrettyPrinter(indent=0)
#     pp.pprint(list_of_site_parse)
#     return list_of_site_parse
#-----------------------------------------------------------------------------



#-----------------------------------------------------------------------------
def get_all_info(html):
    list_of_site_parse = list()
    date_now = datetime.now()
    soup = BeautifulSoup(html, 'lxml')
    trs = soup.find('table').find_all('tr', class_ = 'mouseout')
    last_date_update = check_last_date_update_in_DB()

    for tr in trs:           
        try:
            date_td = tr.findChildren('td',text = re.compile(DATE_REGEX))
            tds = tr.find_all('td')
            td = tds[4] 
            if len(date_td) > 0:
                ndate = datetime.strptime(date_td[0].text[2:], "%d/%m/%Y %H:%M:%S") 
                files = tr.findChildren('td')
                href = td.find('a').get('href')
                for file_name in files:
                    filename = file_name.findChildren('a', text = re.compile(FILENAME_REGEX))
                    if len(filename)>0:                    
                        if ndate > last_date_update[0][0]:  
                            list_of_site_parse.append((date_now, filename[0].text, ndate))
                            wget.download(href, out='C:/ProgramData/MySQL/MySQL Server 8.0/Data/aim_dev_eu/')           
                            Archive('C:/ProgramData/MySQL/MySQL Server 8.0/Data/aim_dev_eu/'+ filename[0].text).extractall('C:/ProgramData/MySQL/MySQL Server 8.0/Data/aim_dev_eu/')
                            cursor=mydb.cursor()
                            try:
                                if int(filename[0].text[8:10]) < 13:
                                    cursor.execute("LOAD DATA INFILE'" + filename[0].text[0:-2]+'dat' + "' INTO TABLE eu_nc_month FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 LINES (DECLARANT,DECLARANT_ISO,PARTNER,PARTNER_ISO,TRADE_TYPE,PRODUCT_NC,PRODUCT_SITC,PRODUCT_cpa2002,PRODUCT_cpa2008,PRODUCT_CPA2_1,PRODUCT_BEC,PRODUCT_SECTION,FLOW,STAT_REGIME,SUPP_UNIT,PERIOD,VALUE_IN_EUROS,QUANTITY_IN_KG,SUP_QUANTITY)")
                                else:
                                    cursor.execute("LOAD DATA INFILE'" + filename[0].text[0:-2]+'dat' + "' INTO TABLE eu_nc_full FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 LINES (DECLARANT,DECLARANT_ISO,PARTNER,PARTNER_ISO,TRADE_TYPE,PRODUCT_NC,PRODUCT_SITC,PRODUCT_cpa2002,PRODUCT_cpa2008,PRODUCT_CPA2_1,PRODUCT_BEC,PRODUCT_SECTION,FLOW,STAT_REGIME,SUPP_UNIT,PERIOD,VALUE_IN_EUROS,QUANTITY_IN_KG,SUP_QUANTITY)")   
                                mydb.commit()
                            except Error as e:
                                print('Error:', e)
                            finally:
                                cursor.close()
                                # mydb.close()
                            os.remove('C:/ProgramData/MySQL/MySQL Server 8.0/Data/aim_dev_eu/'+ filename[0].text)
                            os.remove('C:/ProgramData/MySQL/MySQL Server 8.0/Data/aim_dev_eu/'+ filename[0].text[0:-2] +'dat')
        except ValueError as ve:
            print('ValueError Raised:', ve)           
    # pp = pprint.PrettyPrinter(indent=0)
    # pp.pprint(list_of_site_parse)
    return list_of_site_parse
#-----------------------------------------------------------------------------








#-----------------------------------------------------------------------------
# def get_links_and_unzip(html):
#     links = []
#     soup = BeautifulSoup(html, 'lxml')
#     trs = soup.find('table').find_all('tr', class_ = 'mouseout')
#     for i in range(1,len(trs)-1):
#         try:
#             files = trs[i].findChildren('td')
#             tds = trs[i].find_all('td')
#             td = tds[4]
#             href = td.find('a').get('href')        
#             for file_name in files:
#                 filename = file_name.findChildren('a', text = re.compile(FILENAME_REGEX))
#                 if len(filename and href)>0:
#                     wget.download(href)            
#                     Archive(filename[0].text).extractall('.')
#                     links.append(href)                 
#         except ValueError as ve:
#             print('ValueError Raised:', ve)  
#     return links
#-----------------------------------------------------------------------------






#-----------------------------------------------------------------------------
#Create new table and push unzip files
# def insert_unzip_files():
#     cursor=mydb.cursor()
#     try:
#         if filename[0].text[8:10] < 13:
#             cursor.execute("LOAD DATA INFILE'" + filename[0].text[0:-2]+'dat' + "' INTO TABLE eu_nc_month FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 LINES (DECLARANT,DECLARANT_ISO,PARTNER,PARTNER_ISO,TRADE_TYPE,PRODUCT_NC,PRODUCT_SITC,PRODUCT_cpa2002,PRODUCT_cpa2008,PRODUCT_CPA2_1,PRODUCT_BEC,PRODUCT_SECTION,FLOW,STAT_REGIME,SUPP_UNIT,PERIOD,VALUE_IN_EUROS,QUANTITY_IN_KG,SUP_QUANTITY)")
#         else:
#             cursor.execute("LOAD DATA INFILE'" + filename[0].text[0:-2]+'dat' + "' INTO TABLE eu_nc_full FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 LINES (DECLARANT,DECLARANT_ISO,PARTNER,PARTNER_ISO,TRADE_TYPE,PRODUCT_NC,PRODUCT_SITC,PRODUCT_cpa2002,PRODUCT_cpa2008,PRODUCT_CPA2_1,PRODUCT_BEC,PRODUCT_SECTION,FLOW,STAT_REGIME,SUPP_UNIT,PERIOD,VALUE_IN_EUROS,QUANTITY_IN_KG,SUP_QUANTITY)")
#         mydb.commit()  
#     except Error as e:
#         print('Error:', e)
#     finally:
#         cursor.close()
#         mydb.close()
#-----------------------------------------------------------------------------






#-----------------------------------------------------------------------------
def main():
    url = 'https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&dir=comext/COMEXT_DATA/PRODUCTS'

    # get_links_and_unzip(get_html(url))
    check_last_date_update_in_DB()
    all_info_from_site = get_all_info(get_html(url))
    insert_args(all_info_from_site)
    # insert_unzip_files()
    
    


if __name__ == '__main__':
    main()
#-----------------------------------------------------------------------------