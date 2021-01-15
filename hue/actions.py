
from hue.models import Group, Light, Scene, Bridge, SceneLightstate, Sensor, Schedule
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
import logging, traceback, requests, json, time
from requests.exceptions import ConnectionError

logger = logging.getLogger(__name__)

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
    if instance.group is not None:
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

def put_command(api_url, payload):
    logger.debug('api: '+api_url)
    logger.debug('payload: '+json.dumps(payload))
    try:
        r = requests.put(api_url, data=(json.dumps(payload)))
        logger.debug('response: '+r.text)
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
            logger.error('api_url tried: ' + str(api_url))
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
    except ConnectionError as e:
        logger.error(str(api_url))
        logger.error(str(e))
        return None
    except:
        logger.error(str(api_url))
        logger.error("Error:"+ str(traceback.format_exc()))
        return None
    else:
        return r

def convert_m2m_to_json_array(objects):
    first = True
    s = []
    for obj in objects:
        s.append(str(obj.id))
        logger.debug(obj.id)
    return s
