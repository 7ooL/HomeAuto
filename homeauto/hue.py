import requests, json, pytz, time, sys, traceback
from django.conf import settings
from homeauto.models.hue import Group, Light, Scene, Bridge, SceneLightstate, Sensor, Schedule
from datetime import datetime
import subprocess, logging
from homeauto.house import register_motion_event
from homeauto.admin_logs import log_addition, log_change, log_deletion

logger = logging.getLogger(__name__)

from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

# group callback to delete off hue hub
@receiver(post_delete, sender=Group)
def delete_group_on_hub(sender, instance, **kwargs):
    delete_group(instance.bridge, instance.id)

def delete_group(bridge, gid):
    api_url = 'http://' + bridge.ip + '/api/' + bridge.username + '/groups/'+str(gid)
    delete_command(api_url)

# group calback to update on hue hub
@receiver(post_save, sender=Group)
def set_group_attributes_on_hub(sender, instance, **kwargs):
    set_group_attributes(instance.bridge, instance)

def set_group_attributes(bridge, group):
    api_url = 'http://' + bridge.ip + '/api/' + bridge.username + '/groups/'+str(group.id)
    payload = {'name':group.name,  'lights':convert_m2m_to_json_array(group.lights.all())}
    if put_command(api_url, payload):
        logger.info("{group:"+group.name+"}{id:"+str(group.id)+"}")

# scene callback to delete off hue hub
@receiver(post_delete, sender=Scene)
def delete_scene_on_hub(sender, instance, **kwargs):
    delete_scene(instance.bridge, instance.id)

def delete_scene(bridge, sid):
    api_url = 'http://' + bridge.ip + '/api/' + bridge.username + '/scenes/'+sid
    delete_command(api_url)

# scene callback to update on hue hub
@receiver(post_save, sender=Scene)
def set_scene_attributes_on_hub(sender, instance, **kwargs):
    set_scene_attributes(instance.bridge, instance)

def set_scene_attributes(bridge, scene):
    api_url = 'http://' + bridge.ip + '/api/' + bridge.username + '/scenes/'+str(scene.id)
    payload = {'name':scene.name,  'lights':convert_m2m_to_json_array(scene.lights.all())}
    if put_command(api_url, payload):
        logger.info("{scene:"+scene.name+"}{id:"+str(scene.id)+"}")

# light callback to delete off hue hub
@receiver(post_delete, sender=Light)
def delete_light_on_hub(sender, instance, **kwargs):
    delete_light(instance.bridge, instance.id)

def delete_light(bridge, lid):
    api_url = 'http://' + bridge.ip + '/api/' + bridge.username + '/lights/'+str(lid)
    delete_command(api_url)

# light callback to update on hue hub
@receiver(post_save, sender=Light)
def set_light_attributes_on_hub(sender, instance, **kwargs):
    set_light_name(instance.bridge, instance)
    set_light_state(instance.bridge, instance)

def set_light_name(bridge, light):
    api_url = 'http://' + bridge.ip + '/api/' + bridge.username + '/lights/'+str(light.id)
    payload = {'name':light.name}
    if put_command(api_url, payload):
        logger.info("{light:"+light.name+"}{id:"+str(light.id)+"}")

def set_light_state(bridge, light):
    api_url = 'http://' + bridge.ip + '/api/' + bridge.username + '/lights/'+str(light.id)+"/state"
    data = {}
    data['on'] = light.on
    data['alert'] = light.alert
    if light.on:
        data['hue'] = light.hue
        data['effect'] = light.effect
        data['bri'] = light.bri
        data['sat'] = light.sat
        data['ct'] = light.ct
        data['xy'] = light.xy
        payload = data
        if put_command(api_url, payload):
            logger.info("{light}:"+light.name+"}{id:"+str(light.id)+"}")


def turn_on_light(light):
    api_url = 'http://' + light.bridge.ip + '/api/' + light.bridge.username + '/lights/' + str(light.id) + '/state'
    payload = {'on':True,  'transitiontime':100}
    if put_command(api_url, payload):
        logger.info("{light:"+light.name+"}{id:"+str(light.id)+"}")


def turn_off_light(light):
    api_url = 'http://' + light.bridge.ip + '/api/' + light.bridge.username + '/lights/' + str(light.id) + '/state'
    payload = {'on':False,  'transitiontime':100}
    if put_command(api_url, payload):
        logger.info("{light:"+light.name+"}{id:"+str(light.id)+"}")


def turn_off_group(group):
    api_url = 'http://' + group.bridge.ip + '/api/' + group.bridge.username + '/groups/' + str(group.id) + '/action'
    payload = {'on':False,  'transitiontime':100}
    if put_command(api_url, payload):
        logger.info("{group:"+group.name+"}{id:"+str(group.id)+"}")


def turn_on_group(group):
    api_url = 'http://' + group.bridge.ip + '/api/' + group.bridge.username + '/groups/' + str(group.id) + '/action'
    payload = {'on':True,  'transitiontime':100}
    if put_command(api_url, payload):
        logger.info("{group:"+group.name+"}{id:"+str(group.id)+"}")


def blink_group(group):
    api_url = 'http://' + group.bridge.ip + '/api/' + group.bridge.username + '/groups/' + str(group.id) + '/action'
    payload = {'on':True,  'alert':'select'}
    if put_command(api_url, payload):
        logger.info("{group:"+group.name+"}{id:"+str(group.id)+"}")


def play_scene(scene):
    api_url = 'http://' + scene.bridge.ip + '/api/' + scene.bridge.username + '/groups/' + str(scene.group.id) + '/action'
    payload = {'scene': scene.id}
    if put_command(api_url, payload):
        logger.info("{scene:"+scene.name+"}{id:"+str(scene.id)+"}")

def create_scene(bridge, payload):
    api_url = 'http://' + bridge.ip + '/api/' + bridge.username + '/scenes/'
    r = post_command(api_url, payload)
    if r is not None:
        id = r.json()[0]['success']['id']
        return id
    return None

def flash_scene(scene):
    # get the group of the scene
    g = Scene.objects.get(id=scene.id).group
    data = {}
    data['name'] = "TEMP_"+scene.name
    data['recycle'] = True
    light_list = []
    lightstates = {}
    for light in g.lights.all():
       light_list.append(str(light.id))
       lightstates[str(light.id)] = get_light_state(light)
    data['lights'] = light_list
    data['lightstates'] = lightstates
    temp_s_id = create_scene(g.bridge, data)
    time.sleep(.2)
    if temp_s_id is not None:
        # play the flash scene
        play_scene(scene)
        time.sleep(2)
        # return lights to previous state
        api_url = 'http://' + g.bridge.ip + '/api/' + g.bridge.username + '/groups/' + str(g.id) + '/action'
        payload = {'scene': temp_s_id}
        put_command(api_url, payload)
        delete_scene(g.bridge,temp_s_id)

#def restore_light_state():

def get_light_state(light):
    api_url = 'http://' + light.bridge.ip + '/api/' + light.bridge.username + '/lights/' + str(light.id)
    r = get_command(api_url)
    if r is not None:
        data = {}
        lightstates = r.json()['state']
        if 'on' in lightstates:
            data['on'] = lightstates['on']
            if 'bri' in lightstates:
                data['bri'] = lightstates['bri']
            if 'sat' in lightstates:
                data['sat'] = lightstates['sat']
            if 'ct' in lightstates:
                data['ct'] = lightstates['ct']
            if 'xy' in lightstates:
                data['xy'] = lightstates['xy']
            return data
    logger.error('Unable to get light state')
    return None


def convert_trans_time(transtime):
    # transtime should come in as seconds, convert to multiple of 100ms
    tt = ((transtime*1000)/100)
    # max time allowed by hue lights, it will fail to set otherwise, i think this is 1.5 hours
    if tt > 65535:
        tt = 65543
    return tt

def set_scene_trans_time(scene, transtime):
    transtime = convert_trans_time(transtime)
    if transtime > 0:
        # get the current light states in the scene to update transition times
        api_url='http://'+ scene.bridge.ip +'/api/'+ scene.bridge.username +'/scenes/'+ str(scene.id)
        r = get_command(api_url)
        if r is not None:
            json_str = json.dumps(r.json())
            json_objects = json.loads(json_str)
            for lights in json_objects['lightstates'].items():
                lights[1]['transitiontime'] = int(transtime)
                api_url='http://'+ scene.bridge.ip +'/api/'+ scene.bridge.username +'/scenes/'+ str(scene.id) +'/lightstates/'+ lights[0]
                payload = lights[1]
                put_command(api_url, payload)

def sync_groups():
    logger.debug('Syncing Hue Groups')
    all_bridges = Bridge.objects.all()
    for bridge in all_bridges:
        api_url = 'http://' + bridge.ip + '/api/' + bridge.username + '/groups'
        r = get_command(api_url)
        if r is not None:
            groups = r.json()
            for group in groups:
                data = {}
                data['bridge'] = bridge
                for light in groups[group]['lights']:
                    if not Light.objects.filter(id=light).exists():
                        logger.info('Creating Light:' + light)
                        l = Light.objects.create(id=light)
                        l.save()
                        log_addition(l)


                if 'on' in groups[group]['action']:
                    data['on'] = groups[group]['action']['on']
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
                # if the group doesn't exist, then create it
                if not Group.objects.filter(id=group).exists():
                    logger.info('Creating group: ' + data['name']+"("+group+")")
                    data['id'] = group
                    g = (Group.objects.create)(**data)
                    g.save()
                    log_addition(g)
                # otherwise update the group
                else:
                    logger.debug('Updating group:' + data['name']+"("+group+")")
                    (Group.objects.filter(id=group).update)(**data)
                # add each light to the group
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
        r = get_command(api_url)
        if r is not None:
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
                    log_addition(g)
                else:
                    logger.debug('Updating light:' + light)
                    (Light.objects.filter(id=light).update)(**data)


def sync_sensors():
    logger.debug('Syncing Hue Sensors')
    all_bridges = Bridge.objects.all()
    for bridge in all_bridges:
        api_url = 'http://' + bridge.ip + '/api/' + bridge.username + '/sensors'
        r = get_command(api_url)
        if r is not None:
            sensors = r.json()
            for sensor in sensors:
                if 'productname' in sensors[sensor]:
                    if sensors[sensor]['productname'] in ('Hue ambient light sensor', 'Hue temperature sensor','Hue motion sensor'):
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
                            log_addition(s)
                        else:
                            if 'presence' in sensors[sensor]['state']:
                                if Sensor.objects.get(id=sensor).presence != data['presence']:
                                    logger.debug(data['name'] + ' detected motion')
                                    register_motion_event('Hue', sensor)
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
        r = get_command(api_url)
        if r is not None:
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
                            try:
                                r = get_command(api_url)
                            except:
                                logger.error("Error:"+ str(traceback.format_exc()))
                            else:
                                lightstates = r.json()['lightstates']
                                for ls in lightstates:
                                    data = {}
                                    lsid = ls + '.' + scene
                                    if 'on' in lightstates[ls]:
                                        data['on'] = lightstates[ls]['on']
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
                                        log_addition(hsls)
                                    else:
                                        logger.debug('Updating lightstate:' + lsid)
                                        (SceneLightstate.objects.filter(id=lsid).update)(**data)
                                    hsls = SceneLightstate.objects.get(id=lsid)
                                    s.lightstates.add(hsls)
                        else:
                            logger.warning('Light (' + scenes['light'] + ')in Scene (' + scene + ') does not exist')


def sync_schedules():
    logger.debug('Syncing Hue Schedules')
    all_bridges = Bridge.objects.all()
    for bridge in all_bridges:
        api_url = 'http://' + bridge.ip + '/api/' + bridge.username + '/schedules'
        r = get_command(api_url)
        if r is not None:
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
                    log_addition(s)
                else:
                    logger.debug('Updating schedule:' + schedule)
                    (Schedule.objects.filter(id=schedule).update)(**data)


def put_command(api_url, payload):
    try:
        r = requests.put(api_url, data=(json.dumps(payload)))
        logger.debug(r.text)
        if 'error' in r.text:
            logger.error('payload tried: ' + str(payload))
            for line in json.loads(r.text):
                if 'error' in line:
                    logger.error(line)
                else:
                    logger.debug(line)
            return False
    except:
        logger.error('except ' + str(api_url))
        logger.error('except ' + str(payload))
        logger.error("Error:"+ str(traceback.format_exc()))
        return False
    return True

def post_command(api_url, payload):
    try:
        r = requests.post(api_url, data=(json.dumps(payload)))
        if 'error' in r.text:
            logger.error('payload tried: ' + str(payload))
            for line in json.loads(r.text):
                if 'error' in line:
                    logger.error(line)
                else:
                    logger.debug(line)
        else:
            logger.info(r.text)
    except:
        logger.error('except ' + str(api_url))
        logger.error('except ' + str(payload))
        logger.error("Error:"+ str(traceback.format_exc()))

        return None
    else:
        return r

def delete_command(api_url):
    try:
        r = requests.delete(api_url)
        if 'error' in r.text:
            logger.error('payload tried: ' + str(payload))
            for line in json.loads(r.text):
                if 'error' in line:
                    logger.error(line)
                else:
                    logger.debug(line)
        else:
            logger.info(r.text)
    except:
        logger.error(str(api_url))
        logger.error("Error:"+ str(traceback.format_exc()))

def get_command(api_url):
    try:
        r = requests.get(api_url)
    except:
        logger.error(str(api_url))
        logger.error("Error:"+ str(traceback.format_exc()))
    else:
        return r
    return None


def convert_m2m_to_json_array(objects):
    first = True
    s = []
    for obj in objects:
        s.append(str(obj.id))
    return s
