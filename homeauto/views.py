from django.shortcuts import render
import homeauto.models.house as house
import homeauto.models.hue as hue
import homeauto.models.wemo as device
from django.http import JsonResponse
import simplejson as json

def dashboard_index(request):
    persons = house.Person.objects.all()
    services = house.Service.objects.all()
    lights = hue.Light.objects.all()
    context = {'persons':persons, 
     'services':services, 
     'lights':lights}
    return render(request, 'dashboard_index.html', context)


def people_index(request):
    persons = house.Person.objects.all()
    context = {'persons': persons}
    return render(request, 'people_index.html', context)


def person_detail(request, pk):
    person = house.Person.objects.get(pk=pk)
    context = {'person': person}
    return render(request, 'person_detail.html', context)


def services_index(request):
    services = house.Service.objects.all()
    context = {'services': services}
    return render(request, 'services_index.html', context)


def service_detail(request, pk):
    service = house.Service.objects.get(pk=pk)
    context = {'service': service}
    return render(request, 'service_detail.html', context)


def lights_index(request):
    lights = hue.Light.objects.all()
    wemos = device.Wemo.objects.all()
    context = {'lights':lights, 
     'wemos':wemos}
    return render(request, 'lights_index.html', context)


def light_detail(request):
    return render(request, 'light_detail.html', context)


def groups_index(request):
    return render(request, 'groups_index.html', context)


def group_detail(request):
    return render(request, 'group_detail.html', context)


def scenes_index(request):
    return render(request, 'scenes_index.html', context)


def scene_detail(request):
    return render(request, 'scene_detail.html', context)
