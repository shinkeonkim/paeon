from django.shortcuts import render
from .utils import get_similar_company_list_by_registration

def index(request):
    registration_number = request.GET.get('registration_number')
    registration_name = request.GET.get('registration_name')
    
    response = {
        'registration_number': registration_number or '',
        'registration_name': registration_name or '',   
    }
    
    if registration_number == None or registration_name == None:
        return render(request, 'index.html', response)
    
    response['company_list'] = get_similar_company_list_by_registration(registration_name, registration_number)    

    return render(request, 'index.html', response)
