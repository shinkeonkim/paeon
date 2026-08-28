import os
import csv
import requests
from difflib import SequenceMatcher
from datetime import datetime

from .models import PensionCompany

DOWNLOAD_FILENAME = 'pension_company.csv'


def similar(a: str, b: str):
    return SequenceMatcher(None, a, b).ratio()


def parse_registration_number(registration_number: str):
    return registration_number.replace('-', '')


def parse_registration_name(registration_name: str):
    return registration_name.replace('주식회사', '').replace('(주)', '')


def get_similar_company_list_by_registration_from_pension_company(registration_name: str, registration_number: str, keyword):
    registration_name = registration_name.strip()
    registration_number = registration_number.strip()
    keyword = (keyword or "").strip()

    registration_number = parse_registration_number(registration_number)[:6]

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
    print("File Download Start!")

    try:
        with open(DOWNLOAD_FILENAME, 'wb') as file:
            response = requests.get("https://www.data.go.kr/catalog/15083277/fileData.json")
            csv_url = response.json()['distribution'][0]['contentUrl']

            print(f"{csv_url}에서 다운받고 있습니다.")

            response = requests.get(csv_url)
            file.write(response.content)
    except Exception as err:
        print("File Download Error", err)
        return False

    print("File Download Complete!")
    return True


# ['자료생성년월', ' 사업장명', ' 사업자등록번호', ' 사업장가입상태코드 1 등록 2 탈퇴', ' 우편번호', ' 사업장지번상세주소', ' 사업장도로명상세주소', ' 고객법정동주소코드', ' 고객행정동주소코드', ' 법정동주소광역시도코드', ' 법정동주소광역시시군구코드', ' 법정동주소광역시시군구읍면동코드', ' 사업장형태구분코드 1 법인 2 개인', ' 사업장업종코드', ' 사업장업종코드명', ' 적용일자', ' 재등록일자', ' 탈퇴일자', ' 가입자수', ' 당월고지금액', ' 신규취득자수', ' 상실가입자수']
def update_pension_company():
    with open(DOWNLOAD_FILENAME, 'r', encoding='cp949') as file:
        csv_file = csv.reader(file)

        bulk_pension_companies = []

        print("Pension Company Data Reload Start!")

        for idx, row in enumerate(csv_file):
            if idx == 0:
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
        PensionCompany.objects.bulk_create(bulk_pension_companies, 400)

        print("Pension Company Data Reload Complete!")


def delete_csv_file():
    os.remove(DOWNLOAD_FILENAME)


def reload_pension_company():
    if download_company_csv():
        update_pension_company()
        delete_csv_file()
