from django.conf import settings
from homeauto.models.hue import Group, Light, Scene, Bridge, SceneLightstate, Sensor, Schedule
import requests, json, pytz
from datetime import datetime
import subprocess, logging
from homeauto.house import register_motion_event, put_command

logger = logging.getLogger(__name__)

def turn_on_light(light):
    api_url = 'http://' + light.bridge.ip + '/api/' + light.bridge.username + '/lights/' + str(light.id) + '/state'
    payload = {'on':True,  'transitiontime':100}
    put_command(api_url, payload)


def turn_off_light(light):
    api_url = 'http://' + light.bridge.ip + '/api/' + light.bridge.username + '/lights/' + str(light.id) + '/state'
    payload = {'on':False,  'transitiontime':100}
    put_command(api_url, payload)


def turn_off_group(group):
    api_url = 'http://' + group.bridge.ip + '/api/' + group.bridge.username + '/groups/' + str(group.id) + '/action'
    payload = {'on':False,  'transitiontime':100}
    put_command(api_url, payload)


def turn_on_group(group):
    api_url = 'http://' + group.bridge.ip + '/api/' + group.bridge.username + '/groups/' + str(group.id) + '/action'
    payload = {'on':True,  'transitiontime':100}
    put_command(api_url, payload)


def blink_group(group):
    api_url = 'http://' + group.bridge.ip + '/api/' + group.bridge.username + '/groups/' + str(group.id) + '/action'
    payload = {'on':True,  'alert':'select'}
    put_command(api_url, payload)


def play_scene(scene):
    api_url = 'http://' + scene.bridge.ip + '/api/' + scene.bridge.username + '/groups/' + str(scene.group.id) + '/action'
    payload = {'scene': scene.id}
    put_command(api_url, payload)


def sync_groups():
    logger.debug('Syncing Hue Groups')
    all_bridges = Bridge.objects.all()
    for bridge in all_bridges:
        api_url = 'http://' + bridge.ip + '/api/' + bridge.username + '/groups'
        r = requests.get(api_url)
        groups = r.json()
        for group in groups:
            data = {}
            data['bridge'] = bridge.id
            for light in groups[group]['lights']:
                if not Light.objects.filter(id=light).exists():
                    logger.info('Creating Light:' + light)
                    l = Light.objects.create(id=light)
                    l.save()

            if 'on' in groups[group]['action']:
                data['on'] = groups[group]['action']['on']
            else:
                if 'hue' in groups[group]['action']:
                    data['hue'] = groups[group]['action']['hue']
                if 'effect' in groups[group]['action']:
                    data['effect'] = groups[group]['action']['effect']
                if 'bri' in groups[group]['action']:
                    data['bri'] = groups[group]['action']['bri']
                if 'sat' in groups[group]['action']:
                    data['sat'] = groups[group]['action']['sat']
                if 'ct' in groups[group]['action']:
                    data['ct'] = groups[group]['action']['ct']
                if 'xy' in groups[group]['action']:
                    data['xy'] = groups[group]['action']['xy']
                if 'alert' in groups[group]['action']:
                    data['alert'] = groups[group]['action']['alert']
                if 'colormode' in groups[group]['action']:
                    data['colormode'] = groups[group]['action']['colormode']
                if 'type' in groups[group]:
                    data['type'] = groups[group]['type']
                if 'name' in groups[group]:
                    data['name'] = groups[group]['name']
                if not Group.objects.filter(id=group).exists():
                    logger.info('Creating group:' + group)
                    data['id'] = group
                    g = (Group.objects.create)(**data)
                    g.save()
                else:
                    logger.debug('Updating group:' + group)
                    (Group.objects.filter(id=group).update)(**data)
                g = Group.objects.get(id=group)
                for light in groups[group]['lights']:
                    l = Light.objects.get(id=light)
                    logger.debug('Adding light ' + str(l) + ' to group: ' + str(g))
                    g.lights.add(l)


def sync_lights():
    logger.debug('Syncing Hue Lights')
    all_bridges = Bridge.objects.all()
    for bridge in all_bridges:
        api_url = 'http://' + bridge.ip + '/api/' + bridge.username + '/lights'
        r = requests.get(api_url)
        lights = r.json()
        for light in lights:
            data = {}
            data['bridge'] = bridge.id
            if 'name' in lights[light]:
                data['name'] = lights[light]['name']
            if 'on' in lights[light]['state']:
                data['on'] = lights[light]['state']['on']
            if 'hue' in lights[light]['state']:
                data['hue'] = lights[light]['state']['hue']
            if 'effect' in lights[light]['state']:
                data['effect'] = lights[light]['state']['effect']
            if 'bri' in lights[light]['state']:
                data['bri'] = lights[light]['state']['bri']
            if 'sat' in lights[light]['state']:
                data['sat'] = lights[light]['state']['sat']
            if 'ct' in lights[light]['state']:
                data['ct'] = lights[light]['state']['ct']
            if 'xy' in lights[light]['state']:
                data['xy'] = lights[light]['state']['xy']
            if 'alert' in lights[light]['state']:
                data['alert'] = lights[light]['state']['alert']
            if 'colormode' in lights[light]['state']:
                data['colormode'] = lights[light]['state']['colormode']
            if 'reachable' in lights[light]['state']:
                data['reachable'] = lights[light]['state']['reachable']
            if 'type' in lights[light]:
                data['type'] = lights[light]['type']
            if 'modelid' in lights[light]:
                data['modelid'] = lights[light]['modelid']
            if not Light.objects.filter(id=light).exists():
                logger.info('Creating light:' + light)
                data['id'] = light
                g = (Light.objects.create)(**data)
                g.save()
            else:
                logger.debug('Updating light:' + light)
                (Light.objects.filter(id=light).update)(**data)


def sync_sensors():
    logger.debug('Syncing Hue Sensors')
    all_bridges = Bridge.objects.all()
    for bridge in all_bridges:
        api_url = 'http://' + bridge.ip + '/api/' + bridge.username + '/sensors'
        r = requests.get(api_url)
        sensors = r.json()
        for sensor in sensors:
            if 'productname' in sensors[sensor]:
                if sensors[sensor]['productname'] in ('Hue ambient light sensor', 'Hue temperature sensor',
                                                      'Hue motion sensor'):
                    data = {}
                    data['bridge'] = bridge.id
                    if 'type' in sensors[sensor]:
                        data['type'] = sensors[sensor]['type']
                    if 'modelid' in sensors[sensor]:
                        data['modelid'] = sensors[sensor]['modelid']
                    if 'productname' in sensors[sensor]:
                        data['productname'] = sensors[sensor]['productname']
                    if 'name' in sensors[sensor]:
                        data['name'] = sensors[sensor]['name']
                    if 'lastupdated' in sensors[sensor]['state']:
                        unaware = datetime.strptime(sensors[sensor]['state']['lastupdated'], '%Y-%m-%dT%H:%M:%S')
                        data['lastupdated'] = pytz.utc.localize(unaware)
                    if 'dark' in sensors[sensor]['state']:
                        data['dark'] = sensors[sensor]['state']['dark']
                    if 'darklight' in sensors[sensor]['state']:
                        data['darklight'] = sensors[sensor]['state']['darklight']
                    if 'lightlevel' in sensors[sensor]['state']:
                        data['lightlevel'] = sensors[sensor]['state']['lightlevel']
                    if 'tempreature' in sensors[sensor]['state']:
                        data['tempreature'] = sensors[sensor]['state']['tempreature']
                    if 'presence' in sensors[sensor]['state']:
                        data['presence'] = sensors[sensor]['state']['presence']
                        if data['presence']:
                            logger.debug(data['name'] + ' detected motion')
                            register_motion_event('Hue', sensor)
                    if 'on' in sensors[sensor]['config']:
                        data['on'] = sensors[sensor]['config']['on']
                    if 'battery' in sensors[sensor]['config']:
                        data['battery'] = sensors[sensor]['config']['battery']
                    if 'reachable' in sensors[sensor]['config']:
                        data['reachable'] = sensors[sensor]['config']['reachable']
                    if 'alert' in sensors[sensor]['config']:
                        data['alert'] = sensors[sensor]['config']['alert']
                    if 'ledindication' in sensors[sensor]['config']:
                        data['ledindication'] = sensors[sensor]['config']['ledindication']
                    if 'sensitivity' in sensors[sensor]['config']:
                        data['sensitivity'] = sensors[sensor]['config']['sensitivity']
                    if 'sensitivitymax' in sensors[sensor]['config']:
                        data['sensitivitymax'] = sensors[sensor]['config']['sensitivitymax']
                    if 'tholddark' in sensors[sensor]['config']:
                        data['tholddark'] = sensors[sensor]['config']['tholddark']
                    if 'tholdoffset' in sensors[sensor]['config']:
                        data['tholdoffset'] = sensors[sensor]['config']['tholdoffset']
                    if not Sensor.objects.filter(id=sensor).exists():
                        logger.info('Creating sensor:' + sensor)
                        data['id'] = sensor
                        s = (Sensor.objects.create)(**data)
                        s.save()
                    else:
                        logger.debug('Updating sensor:' + sensor)
                        (Sensor.objects.filter(id=sensor).update)(**data)
                else:
                    logger.debug('sensor has an unsupported product type: ' + sensors[sensor]['productname'])
            else:
                logger.debug('sensor had no product name')


def sync_scenes():
    logger.debug('Syncing Hue Scenes')
    all_bridges = Bridge.objects.all()
    for bridge in all_bridges:
        api_url = 'http://' + bridge.ip + '/api/' + bridge.username + '/scenes'
        r = requests.get(api_url)
        scenes = r.json()
        for scene in scenes:
            data = {}
            data['bridge'] = bridge
            if 'name' in scenes[scene]:
                data['name'] = scenes[scene]['name']
            if 'type' in scenes[scene]:
                data['type'] = scenes[scene]['type']
            if 'owner' in scenes[scene]:
                data['owner'] = scenes[scene]['owner']
            if 'group' in scenes[scene]:
                if Group.objects.filter(id=(scenes[scene]['group'])).exists():
                    data['group'] = Group.objects.get(id=(scenes[scene]['group']))
                elif int(scenes[scene]['group']) != 0:
                    logger.warning('Group (' + scenes[scene]['group'] + ') in Scene (' + scene + ') does not exist')
            if not Scene.objects.filter(id=scene).exists():
                logger.info('Creating scene:' + scene)
                data['id'] = scene
                s = (Scene.objects.create)(**data)
                s.save()
            else:
                logger.debug('Updating scene:' + scene)
                (Scene.objects.filter(id=scene).update)(**data)
            if 'lights' in scenes[scene]:
                s = Scene.objects.get(id=scene)
                for light in scenes[scene]['lights']:
                    if Light.objects.filter(id=light).exists():
                        l = Light.objects.get(id=light)
                        logger.debug('Adding light: ' + str(l) + ' to scene: ' + str(s))
                        s.lights.add(l)
                        api_url = 'http://' + bridge.ip + '/api/' + bridge.username + '/scenes/' + scene
                        r = requests.get(api_url)
                        try:
                            lightstates = r.json()['lightstates']
                            for ls in lightstates:
                                data = {}
                                lsid = ls + '.' + scene
                                if 'on' in lightstates[ls]:
                                    data['on'] = lightstates[ls]['on']
                                else:
                                    if 'bri' in lightstates[ls]:
                                        data['bri'] = lightstates[ls]['bri']
                                    if 'sat' in lightstates[ls]:
                                        data['sat'] = lightstates[ls]['sat']
                                    if 'ct' in lightstates[ls]:
                                        data['ct'] = lightstates[ls]['ct']
                                    if 'xy' in lightstates[ls]:
                                        data['xy'] = lightstates[ls]['xy']
                                    if not SceneLightstate.objects.filter(id=lsid).exists():
                                        logger.info('Creating lightstate:' + lsid)
                                        data['id'] = lsid
                                        hsls = (SceneLightstate.objects.create)(**data)
                                        hsls.save()
                                    else:
                                        logger.debug('Updating lightstate:' + lsid)
                                        (SceneLightstate.objects.filter(id=lsid).update)(**data)
                                    hsls = SceneLightstate.objects.get(id=lsid)
                                    s.lightstates.add(hsls)

                        except ValueError as error:
                            try:
                                logger.error(error)
                            finally:
                                error = None
                                del error

                    else:
                        logger.warning('Light (' + scenes['light'] + ')in Scene (' + scene + ') does not exist')


def sync_schedules():
    logger.debug('Syncing Hue Schedules')
    all_bridges = Bridge.objects.all()
    for bridge in all_bridges:
        api_url = 'http://' + bridge.ip + '/api/' + bridge.username + '/schedules'
        r = requests.get(api_url)
        schedules = r.json()
        for schedule in schedules:
            data = {}
            data['bridge'] = bridge.id
            if 'name' in schedules[schedule]:
                data['name'] = schedules[schedule]['name']
            if 'description' in schedules[schedule]:
                data['description'] = schedules[schedule]['description']
            if 'status' in schedules[schedule]:
                if schedules[schedule]['status'] == 'enabled':
                    data['enabled'] = True
                elif schedules[schedule]['status'] == 'disabled':
                    data['enabled'] = False
                else:
                    logger.warning('Unknown schedule status: ' + schedules[schedule]['status'])
            if 'localtime' in schedules[schedule]:
                data['localtime'] = schedules[schedule]['localtime']
            if not Schedule.objects.filter(id=schedule).exists():
                logger.info('Creating schedule:' + schedule)
                data['id'] = schedule
                s = (Schedule.objects.create)(**data)
                s.save()
            else:
                logger.debug('Updating schedule:' + schedule)
                (Schedule.objects.filter(id=schedule).update)(**data)
