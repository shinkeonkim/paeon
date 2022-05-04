from django.shortcuts import render
from .utils import get_similar_company_list_by_registration_from_pension_company, parse_registration_number

def index(request):
    registration_number = request.GET.get('registration_number')
    registration_name = request.GET.get('registration_name')
    keyword = request.GET.get('keyword')
    
    response = {
        'registration_number': registration_number or '',
        'registration_name': registration_name or '',
        'parsed_registration_number': parse_registration_number(registration_number or ''),
        'keyword': keyword or ''
    }
    
    if registration_number == None or registration_name == None:
        return render(request, 'index.html', response)
    
    response['company_list'] = get_similar_company_list_by_registration_from_pension_company(
        registration_name,
        registration_number,
        keyword
    )

    return render(request, 'index.html', response)
