from django.conf import settings
from homeauto.models.hue import Group, Light, Scene, Bridge, SceneLightstate, Sensor, Schedule
import requests, json, pytz

from datetime import datetime
import subprocess
import logging

from homeauto.house import RegisterMotionEvent, putCommand


# This retrieves a Python logging instance (or creates it)
logger = logging.getLogger(__name__)

def turnOnLight(light):
    api_url='http://'+light.bridge.ip+'/api/'+light.bridge.username+'/lights/'+str(light.id)+'/state'
    payload = {'on': True,'transitiontime': 100}
    putCommand(api_url, payload)

def turnOffLight(light):
    api_url='http://'+light.bridge.ip+'/api/'+light.bridge.username+'/lights/'+str(light.id)+'/state'
    payload = {'on': False,'transitiontime': 100}
    putCommand(api_url, payload)

def turnOffGroup(group):
    api_url='http://'+group.bridge.ip+'/api/'+group.bridge.username+'/groups/'+str(group.id)+'/action'
    payload = {'on': False,'transitiontime': 100}
    putCommand(api_url, payload)

def turnOnGroup(group):
    # dealing with all lights, use group 0
    api_url='http://'+group.bridge.ip+'/api/'+group.bridge.username+'/groups/'+str(group.id)+'/action'
    payload = {'on': True,'transitiontime': 100}
    putCommand(api_url, payload)

def blinkGroup (group):
    api_url='http://'+group.bridge.ip+'/api/'+group.bridge.username+'/groups/'+str(group.id)+'/action'
    payload = {'on': True, 'alert': "select"}
    putCommand(api_url, payload)

def playScene(scene):
    api_url='http://'+scene.bridge.ip+'/api/'+scene.bridge.username+'/groups/'+str(scene.group.id)+'/action'
    payload = {'scene': scene.id}
    putCommand(api_url, payload)

def SyncGroups():
    logger.debug("Syncing Hue Groups" )
    all_bridges = Bridge.objects.all()
    for bridge in all_bridges:
        # make request for all groups
        # /api/<username>/groups
        api_url='http://'+bridge.ip+'/api/'+bridge.username+'/groups'
        r = requests.get(api_url)
        groups = r.json()

        for group in groups:
             data = {}
             data["bridge"] = bridge.id
             # make sure lights exist before adding them to group
#             lightdata = []
             for light in groups[group]['lights']:
                 if not Light.objects.filter(id=light).exists():
                     logger.info("Creating Light:"+light)
                     l = Light.objects.create(id=light)
                     l.save()

             # some groups dont have all the possible values
             if "on" in groups[group]['action']:
                 data['on']=groups[group]['action']['on']

             if "hue" in groups[group]['action']:
                 data['hue']=groups[group]['action']['hue']

             if "effect" in groups[group]['action']:
                 data['effect']=groups[group]['action']['effect']

             if "bri" in groups[group]['action']:
                 data['bri']=groups[group]['action']['bri']

             if "sat" in groups[group]['action']:
                 data['sat']=groups[group]['action']['sat']

             if "ct" in groups[group]['action']:
                 data['ct']=groups[group]['action']['ct']

             if "xy" in groups[group]['action']:
                 data['xy']=groups[group]['action']['xy']

             if "alert" in groups[group]['action']:
                 data['alert']=groups[group]['action']['alert']

             if "colormode" in groups[group]['action']:
                 data['colormode']=groups[group]['action']['colormode']

             if "type" in groups[group]:
                 data['type']=groups[group]['type']

             if "name" in groups[group]:
                 data['name']=groups[group]['name']

             # if the group doesn't exist, then create it
             if not Group.objects.filter(id=group).exists():
                 logger.info("Creating group:"+group)
                 data['id'] = group
                 g = Group.objects.create(**data)
                 g.save()
             # otherwise update the group
             else:
                 logger.debug("Updating group:"+group)
                 Group.objects.filter(id=group).update(**data)

             # add each light to the group
             g = Group.objects.get(id=group)
             for light in groups[group]['lights']:
                 l = Light.objects.get(id=light)
                 logger.debug("Adding light "+str(l)+" to group: "+str(g))
                 g.lights.add(l)

def SyncLights():
    logger.debug("Syncing Hue Lights" )
    all_bridges = Bridge.objects.all()
    for bridge in all_bridges:
        # make request for all lights
        # /api/<username>/lights
        api_url='http://'+bridge.ip+'/api/'+bridge.username+'/lights'
        r = requests.get(api_url)
        lights = r.json()

        for light in lights:
             data = {}
             data["bridge"] = bridge.id

             if "name" in lights[light]:
                 data['name']=lights[light]['name']
             if "on" in lights[light]['state']:
                 data['on']=lights[light]['state']['on']
             if "hue" in lights[light]['state']:
                 data['hue']=lights[light]['state']['hue']
             if "effect" in lights[light]['state']:
                 data['effect']=lights[light]['state']['effect']
             if "bri" in lights[light]['state']:
                 data['bri']=lights[light]['state']['bri']
             if "sat" in lights[light]['state']:
                 data['sat']=lights[light]['state']['sat']
             if "ct" in lights[light]['state']:
                 data['ct']=lights[light]['state']['ct']
             if "xy" in lights[light]['state']:
                 data['xy']=lights[light]['state']['xy']
             if "alert" in lights[light]['state']:
                 data['alert']=lights[light]['state']['alert']
             if "colormode" in lights[light]['state']:
                 data['colormode']=lights[light]['state']['colormode']
             if "reachable" in lights[light]['state']:
                 data['reachable']=lights[light]['state']['reachable']
             if "type" in lights[light]:
                 data['type']=lights[light]['type']
             if "modelid" in lights[light]:
                 data['modelid']=lights[light]['modelid']

             # if the light doesn't exist, then create it
             if not Light.objects.filter(id=light).exists():
                 logger.info("Creating light:"+light)
                 data['id'] = light
                 g = Light.objects.create(**data)
                 g.save()
             # otherwise update the light
             else:
                 logger.debug("Updating light:"+light)
                 Light.objects.filter(id=light).update(**data)



def SyncSensors():
    logger.debug("Syncing Hue Sensors" )
    all_bridges = Bridge.objects.all()
    for bridge in all_bridges:
        # make request for all sensors
        # /api/<username>/sensors
        api_url='http://'+bridge.ip+'/api/'+bridge.username+'/sensors'
        r = requests.get(api_url)
        sensors = r.json()

        for sensor in sensors:
             # only store data for specifc product types
             if "productname" in sensors[sensor]:
                 if sensors[sensor]['productname'] in ['Hue ambient light sensor','Hue temperature sensor','Hue motion sensor']:

                     data = {}
                     data["bridge"] = bridge.id

                     if "type" in sensors[sensor]:
                         data['type']=sensors[sensor]['type']
                     if "modelid" in sensors[sensor]:
                         data['modelid']=sensors[sensor]['modelid']
                     if "productname" in sensors[sensor]:
                         data['productname']=sensors[sensor]['productname']
                     if "name" in sensors[sensor]:
                         data['name']=sensors[sensor]['name']

                     # state
                     if "lastupdated" in sensors[sensor]['state']:
                         # example: 2020-07-26T23:36:48
                         unaware =datetime.strptime(sensors[sensor]['state']['lastupdated'], '%Y-%m-%dT%H:%M:%S')
                         data['lastupdated']=pytz.utc.localize(unaware)

                     if "dark" in sensors[sensor]['state']:
                         data['dark']=sensors[sensor]['state']['dark']
                     if "darklight" in sensors[sensor]['state']:
                         data['darklight']=sensors[sensor]['state']['darklight']
                     if "lightlevel" in sensors[sensor]['state']:
                         data['lightlevel']=sensors[sensor]['state']['lightlevel']
                     if "tempreature" in sensors[sensor]['state']:
                         data['tempreature']=sensors[sensor]['state']['tempreature']
                     if "presence" in sensors[sensor]['state']:
                         data['presence']=sensors[sensor]['state']['presence']
                         if data['presence']:
                             logger.debug(data['name']+" detected motion")
                             RegisterMotionEvent("Hue", sensor)

                     # config
                     if "on" in sensors[sensor]['config']:
                         data['on']=sensors[sensor]['config']['on']
                     if "battery" in sensors[sensor]['config']:
                         data['battery']=sensors[sensor]['config']['battery']
                     if "reachable" in sensors[sensor]['config']:
                         data['reachable']=sensors[sensor]['config']['reachable']
                     if "alert" in sensors[sensor]['config']:
                         data['alert']=sensors[sensor]['config']['alert']
                     if "ledindication" in sensors[sensor]['config']:
                         data['ledindication']=sensors[sensor]['config']['ledindication']
                     if "sensitivity" in sensors[sensor]['config']:
                         data['sensitivity']=sensors[sensor]['config']['sensitivity']
                     if "sensitivitymax" in sensors[sensor]['config']:
                         data['sensitivitymax']=sensors[sensor]['config']['sensitivitymax']
                     if "tholddark" in sensors[sensor]['config']:
                         data['tholddark']=sensors[sensor]['config']['tholddark']
                     if "tholdoffset" in sensors[sensor]['config']:
                         data['tholdoffset']=sensors[sensor]['config']['tholdoffset']

                     # if the sensor doesn't exist, then create it
                     if not Sensor.objects.filter(id=sensor).exists():
                         logger.info("Creating sensor:"+sensor)
                         data['id'] = sensor
                         s = Sensor.objects.create(**data)
                         s.save()
                     # otherwise update the sensor
                     else:
                         logger.debug("Updating sensor:"+sensor)
                         Sensor.objects.filter(id=sensor).update(**data)

                 else:
                     logger.debug("sensor has an unsupported product type: " + sensors[sensor]['productname'])
             else:
                 logger.debug("sensor had no product name")



def SyncScenes():
    logger.debug("Syncing Hue Scenes" )
    all_bridges = Bridge.objects.all()
    for bridge in all_bridges:
        # make request for all scenes
        # /api/<username>/scenes
        api_url='http://'+bridge.ip+'/api/'+bridge.username+'/scenes'
        r = requests.get(api_url)
        scenes = r.json()

        for scene in scenes:
             data = {}
             data["bridge"] = bridge

             if "name" in scenes[scene]:
                 data['name']=scenes[scene]['name']
             if "type" in scenes[scene]:
                 data['type']=scenes[scene]['type']
             if "owner" in scenes[scene]:
                 data['owner']=scenes[scene]['owner']

             if "group" in scenes[scene]:
                if Group.objects.filter(id=scenes[scene]['group']).exists():
                    data['group']=Group.objects.get(id=scenes[scene]['group'])
                else:
                    if int(scenes[scene]['group']) != 0:
                        logger.warning("Group ("+scenes[scene]['group']+") in Scene ("+scene+") does not exist")

             # if the scene doesn't exist, then create it
             if not Scene.objects.filter(id=scene).exists():
                 logger.info("Creating scene:"+scene)
                 data['id'] = scene
                 s = Scene.objects.create(**data)
                 s.save()
             # otherwise update the scene
             else:
                 logger.debug("Updating scene:"+scene)
                 Scene.objects.filter(id=scene).update(**data)

             # add each light to the scene
             if "lights" in scenes[scene]:
                 s = Scene.objects.get(id=scene)
                 for light in scenes[scene]['lights']:
                     if Light.objects.filter(id=light).exists():
                         l = Light.objects.get(id=light)
                         logger.debug("Adding light: "+str(l)+" to scene: "+str(s))
                         s.lights.add(l)
                         # get each light state for the scene
                         # /api/<username>/scenes/<id>
                         api_url='http://'+bridge.ip+'/api/'+bridge.username+'/scenes/'+scene
                         r = requests.get(api_url)
                         try:
                             lightstates = r.json()['lightstates']
                             for ls in lightstates:
                                 data = {}
                                 lsid=ls+"."+scene
                                 if "on" in lightstates[ls]:
                                     data['on']=lightstates[ls]['on']
                                 if "bri" in lightstates[ls]:
                                     data['bri']=lightstates[ls]['bri']
                                 if "sat" in lightstates[ls]:
                                     data['sat']=lightstates[ls]['sat']
                                 if "ct" in lightstates[ls]:
                                     data['ct']=lightstates[ls]['ct']
                                 if "xy" in lightstates[ls]:
                                     data['xy']=lightstates[ls]['xy']
                                 # if the lightstate doesn't exist, then create it
                                 if not SceneLightstate.objects.filter(id=lsid).exists():
                                     logger.info("Creating lightstate:"+lsid)
                                     data['id'] = lsid
                                     hsls = SceneLightstate.objects.create(**data)
                                     hsls.save()
                                 # otherwise update the light
                                 else:
                                     logger.debug("Updating lightstate:"+lsid)
                                     SceneLightstate.objects.filter(id=lsid).update(**data)
                                 hsls = SceneLightstate.objects.get(id=lsid)
                                 s.lightstates.add(hsls)
                         except ValueError as error:
                             logger.error(error)
                     else:
                         logger.warning("Light ("+scenes['light']+")in Scene ("+scene+") does not exist")


# schedules
def SyncSchedules():
    logger.debug("Syncing Hue Schedules" )
    all_bridges = Bridge.objects.all()
    for bridge in all_bridges:
        # make request for all schedules
        # /api/<username>/schedules
        api_url='http://'+bridge.ip+'/api/'+bridge.username+'/schedules'
        r = requests.get(api_url)
        schedules = r.json()

        for schedule in schedules:
             data = {}
             data["bridge"] = bridge.id

             if "name" in schedules[schedule]:
                 data['name']=schedules[schedule]['name']
             if "description" in schedules[schedule]:
                 data['description']=schedules[schedule]['description']
             if "status" in schedules[schedule]:
                 if schedules[schedule]['status'] == "enabled":
                     data['enabled'] = True
                 elif schedules[schedule]['status'] == "disabled":
                     data['enabled'] = False
                 else:
                     logger.warning("Unknown schedule status: "+schedules[schedule]['status'])

             if "localtime" in schedules[schedule]:
                 data['localtime']=schedules[schedule]['localtime']

             # if the schedule doesn't exist, then create it
             if not Schedule.objects.filter(id=schedule).exists():
                 logger.info("Creating schedule:"+schedule)
                 data['id'] = schedule
                 s = Schedule.objects.create(**data)
                 s.save()
             # otherwise update the schedule
             else:
                 logger.debug("Updating schedule:"+schedule)
                 Schedule.objects.filter(id=schedule).update(**data)

