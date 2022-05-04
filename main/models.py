from statistics import mode
from django.db import models
from django.utils.translation import gettext as _

class PensionCompany(models.Model):
    name = models.TextField()  # 사업장명 / 회사명
    registration_number = models.TextField()  # 사업자등록번호
    lot_number_address = models.TextField()  # 지번주소
    road_name_address = models.TextField()  # 도로명주소
    employees_count = models.IntegerField()  # 기입자 수 / 사원 수
    data_created_at = models.CharField(
        max_length=7,
    )  # 자료 생성년월 (ex. '2022-02')
    
    class Meta:
        verbose_name = _('PensionCompany')
        verbose_name_plural = _('PensionCompanies')
