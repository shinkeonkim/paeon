import requests
from django.conf import settings 
from xml.etree import ElementTree as elemTree

from difflib import SequenceMatcher

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
    return registration_number.replace('-', '')[:6]

def parse_registration_name(registration_name: str):
    return registration_name.replace('주식회사', '').replace('(주)', '')

def get_similar_company_list_by_registration(registration_name: str, registration_number: str, keyword):
    registration_name = registration_name.strip()
    registration_number = registration_number.strip()
    keyword = (keyword or "").strip()

    registration_number = parse_registration_number(registration_number)
    result = parse_openapi_result(get_openapi_result(registration_number, keyword))    
    result.sort(key = lambda t: (-similar(t[0][1], registration_name), -int(t[4][1])))
    
    return result
