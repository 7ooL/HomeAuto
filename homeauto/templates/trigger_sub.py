from django.http import HttpResponse
import json

def get_subcategory(request): 
    id = request.GET.get('id','') 
    result = list(Subcategory.objects.filter(category_id=int(id)).values('id', 'name')) 
    return HttpResponse(json.dumps(result), content_type="application/json") 
