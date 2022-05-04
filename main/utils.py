from django.conf import settings 

import os
import csv
import requests
from xml.etree import ElementTree as elemTree
from difflib import SequenceMatcher
from datetime import datetime

from .models import PensionCompany

from .dump import DUMP

DOWNLOAD_FILENAME = 'pension_company.csv'
API_DEV_MODE = settings.API_DEV_MODE
API_URL = 'http://apis.data.go.kr/B552015/NpsBplcInfoInqireService/getBassInfoSearch'
MAX_RESULT_SIZE = 100000

def similar(a: str, b: str):
    return SequenceMatcher(None, a, b).ratio()


def get_openapi_result(registration_number: str, keyword: str):
    params = {
        'serviceKey': settings.SERVICE_KEY,
        'wkpl_nm': keyword,
        'bzowr_rgst_no': str(registration_number),
        'numOfRows': MAX_RESULT_SIZE,
    }

    response = requests.get(API_URL, params=params)
    
    return response.text


def parse_openapi_result(text: str):
    items = elemTree.fromstring(text).find('body').find('items')
      
    result = []
    for item in items.iter('item'):
        dic = {}
        dic['name'] = item.find('wkplNm').text
        dic['registration_number'] = item.find('bzowrRgstNo').text
        dic['address'] = item.find('wkplRoadNmDtlAddr').text
        dic['created_at'] = item.find('dataCrtYm').text
        dic['seq'] = item.find('seq').text

        result.append([*dic.items()])

    return result

def parse_registration_number(registration_number: str):
    return registration_number.replace('-', '')

def parse_registration_name(registration_name: str):
    return registration_name.replace('주식회사', '').replace('(주)', '')

def get_similar_company_list_by_registration(registration_name: str, registration_number: str, keyword):
    registration_name = registration_name.strip()
    registration_number = registration_number.strip()
    keyword = (keyword or "").strip()

    registration_number = parse_registration_number(registration_number)
    result = DUMP if API_DEV_MODE else parse_openapi_result(get_openapi_result(registration_number[:6], keyword))    
    result.sort(key = lambda t: (-similar(t[0][1], registration_name), -int(t[4][1])))
    
    return result

def get_similar_company_list_by_registration_from_pension_company(registration_name: str, registration_number: str, keyword):
    registration_name = registration_name.strip()
    registration_number = registration_number.strip()
    keyword = (keyword or "").strip()
    
    registration_number = parse_registration_number(registration_number)
    
    result = [*PensionCompany.objects.filter(registration_number = registration_number).values(
        'name',
        'registration_number',
        'lot_number_address',
        'road_name_address',
        'employees_count',
        'data_created_at',
    )]
    
    result.sort(key = lambda t: (-similar(t['name'], registration_name), -datetime(int(t['data_created_at'][:4]), int(t['data_created_at'][5:]), 1).timestamp()))

    result = [item.items() for item in result]

    return result

def download_company_csv():    
    with open(DOWNLOAD_FILENAME, 'wb') as file:
        response = requests.get("https://www.data.go.kr/catalog/15083277/fileData.json")
        csv_url = response.json()['distribution'][0]['contentUrl']
        
        response = requests.get(csv_url)
        file.write(response.content)


# ['자료생성년월', ' 사업장명', ' 사업자등록번호', ' 사업장가입상태코드 1 등록 2 탈퇴', ' 우편번호', ' 사업장지번상세주소', ' 사업장도로명상세주소', ' 고객법정동주소코드', ' 고객행정동주소코드', ' 법정동주소광역시도코드', ' 법정동주소광역시시군구코드', ' 법정동주소광역시시군구읍면동코드', ' 사업장형태구분코드 1 법인 2 개인', ' 사업장업종코드', ' 사업장업종코드명', ' 적용일자', ' 재등록일자', ' 탈퇴일자', ' 가입자수', ' 당월고지금액', ' 신규취득자수', ' 상실가입자수']
def update_pension_company():
    with open(DOWNLOAD_FILENAME, 'r', encoding='cp949') as file:
        csv_file = csv.reader(file)
        
        bulk_pension_companies = []
    
        for idx, row in enumerate(csv_file):
            if idx == 0:
                print(row)
                continue
            
            pension_company = PensionCompany(
                name = row[1],
                registration_number = row[2],
                lot_number_address = row[5],
                road_name_address = row[6],
                employees_count = row[18],
                data_created_at = row[0],
            )
            
            bulk_pension_companies.append(pension_company)
            
        PensionCompany.objects.all().delete()
        PensionCompany.objects.bulk_create(bulk_pension_companies)

def delete_csv_file():
    os.remove(DOWNLOAD_FILENAME)


def reload_pension_company():
    download_company_csv()
    update_pension_company()
    delete_csv_file()
