
from django.urls import path
from homeauto import views
#from homeauto import api
#import logging
urlpatterns = [

 path('', (views.dashboard_index), name='dashboard_index'),

]
# path('people', (views.people_index), name='people_index'),
# path('people/<int:pk>/', (views.person_detail), name='person_detail'),
# path('services', (views.services_index), name='services_index'),
# path('services/<int:pk>/', (views.service_detail), name='service_detail'),
# path('lights', (views.lights_index), name='lights_index'),
# path('lights/<int:pk>/', (views.light_detail), name='light_detail'),
# path('groups', (views.groups_index), name='groups_index'),
# path('groups/<int:pk>/', (views.group_detail), name='group_detail'),
# path('scenes', (views.scenes_index), name='scenes_index'),
# path('scenes/<int:pk>/', (views.scene_detail), name='scene_detail'),
# path('api/person/', api.persons),
# path('api/person/<int:pk>', api.person_detail),
# path('api/person/<str:name>', api.person_id),
# path('api/person/<int:pk>/toggleHome', api.person_toggleHome)]


