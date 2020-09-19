from homeauto.models.house import Person
from django.core import serializers
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
import simplejson as json

#import logging
# This retrieves a Python logging instance (or creates it)
#logger = logging.getLogger(__name__)

def persons(request):
    people = serializers.serialize('json', Person.objects.all())
    return HttpResponse(people, content_type="application/json")

def person_detail(request, pk):
    person =  model_to_dict(Person.objects.get(pk=pk))
    return JsonResponse(person)

def person_id(request, name):
    try:
        person = model_to_dict(Person.objects.get(first_name__iexact=name))
        return JsonResponse(person)
    except ObjectDoesNotExist:
        return json404(request, name)

def person_toggleHome(request, pk):
    try:
        person = Person.objects.get(pk=pk)
        person.is_home = not person.is_home
        person.save(update_fields=["is_home"])
        return JsonResponse({'status':person.first_name+" is_home:"+str(person.is_home)})
    except ObjectDoesNotExist:
        return json404(request, pk)


def json404(request, what, exception=None):
    return JsonResponse({'error': str(what)+' was not found'}, status=404)
