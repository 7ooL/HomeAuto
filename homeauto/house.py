import logging, requests, json, smtplib, datetime, os, random, sys, subprocess, traceback
from django.utils import timezone
from django.contrib.auth.models import User
from homeauto.models.hue import Sensor, Scene, Light, Group, Schedule
from homeauto.models.wemo import Wemo
from homeauto.models.decora import Switch
from homeauto.models.vivint import Device, Panel
from homeauto.models.house import Trigger, Nugget, Action, HouseLight, Account, Person, CustomEvent
import homeauto.hue as HueAction
import homeauto.wemo as WemoAction
import homeauto.decora as DecoraAction
from datetime import timedelta
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)

# this is for intercepting databse updates
@receiver(post_save, sender=Person)
def register_person_event(sender, instance, **kwargs):
    logger.info("Person:{"+instance.user.username+"} is home {"+str(instance.is_home)+"}")
    if instance.is_home:
        triggers = Trigger.objects.filter(trigger=(Trigger.PEOPLE), people_has_arrived=True, people=instance)
        for t in triggers:
            results = []
            logger.debug('Evaluating: ' + t.name + "  ("+str(t.people.count())+" people)")
            if t.enabled:
                if t.people.count() > 1:
                    for person in t.people.all():
#                        person = Person.objects.get(id=person.id)
                        if person.is_home:
                            logger.debug('  TEST (arrive): '+person.user.username + ' is home, matching trigger: '+t.name)
                            results.append(True)
                        else:
                            logger.debug('  TEST (arrive): '+person.user.username + ' is not home, not matching trigger: '+t.name)
                            results.append(False)
                else:
                    results.append(True)
            else:
                logger.debug('Trigger:{' + t.name + '}{' + str(t.id) + '}{disabled}')
                results.append(False)
            logger.debug("  Results: "+str(results))
            if all(results):
                logger.debug('Trigger:{' + t.name + '}{' + str(t.id) + '}{fired}')
                evaluate_nuggets(t.id)

    else:
        triggers = Trigger.objects.filter(trigger=(Trigger.PEOPLE), people_has_left=True, people=instance)
        for t in triggers:
            results = []
            logger.debug('Evaluating: ' + t.name + "  ("+str(t.people.count())+" people)")
            if t.enabled:
                if t.people.count() > 1:
                    for person in t.people.all():
 #                       person = Person.objects.get(id=person.id)
                        if not person.is_home:
                            logger.debug('  TEST (leave): '+person.user.username + ' is not home, matching trigger: '+t.name)
                            results.append(True)
                        else:
                            logger.debug('  TEST (leave): '+person.user.username + ' is home, NOT matching trigger: '+t.name)
                            results.append(False)
                else:
                    results.append(True)
            else:
                logger.debug('Trigger:{' + t.name + '}{' + str(t.id) + '}{disabled}')
                results.append(False)
            logger.debug("  Results: "+str(results))
            if all(results):
                logger.debug('Trigger:{' + t.name + '}{' + str(t.id) + '}{fired}')
                evaluate_nuggets(t.id)


def register_watcher_event(event):
    logger.debug(event)
    if event.event_type == 'created':
        logger.info('Received created event - %s.' % event.src_path)
        with open(event.src_path) as f:
            logger.info(subprocess.run(['cat', event.src_path], stdout=subprocess.PIPE))
            if not f.readline().rstrip():
                logger.error('Input file is empty')
                remove_file(event.src_path)
                return
        with open(event.src_path) as f:
            s = f.readline().rstrip().split(':')
            if len(s) == 1:
                try:
                    e = CustomEvent.objects.get(name=(s[0].lower()))
                except:
                    logger.error("Error:"+ str(traceback.format_exc()))
                    logger.error('There are no watcher events defined for: ' + s[0])
                    remove_file(event.src_path)
                    return
                else:
                    try:
                        t = Trigger.objects.get(trigger=(Trigger.CUSTOM_EVENT), event__name=(e.name))
                        if t.enabled:
                            logger.debug('Trigger:{' + t.name + '}{' + str(t.id) + '}{fired}')
                            eval = True
                        else:
                            logger.debug('Trigger:{' + t.name + '}{' + str(t.id) + '}{disabled}')
                            eval = False
                    except Exception as e:
                        try:
                            logger.error(e)
                            eval = False
                        finally:
                            e = None
                            del e
                    if eval:
                        evaluate_nuggets(t.id)

            elif len(s) == 2:
                key = s[0].lower()
                value = s[1]
                logger.info('Found:{' + key + '}{' + value+"}")
                if key == 'arrive':
                    try:
                        p = Person.objects.get(user__username=value)
                        if p:
                            p.is_home = True
                            p.save()
                        else:
                            logger.error('No person was found with the username: ' + str(value))
                    except:
                        logger.error("Unexpected error:"+ str(traceback.format_exc()))
                elif key == 'leave':
                    try:
                        p = Person.objects.get(user__username=value)
                        logger.warning(p.user.first_name+" was found")
                        if p:
                            p.is_home = False
                            try:
                                p.save()
                            except:
                                logger.error("Unexpected error:"+ str(traceback.format_exc()))
                        else:
                            logger.error('No person was found with the username: ' + str(value))
                    except:
                        logger.error("Unexpected error:"+ str(traceback.format_exc()))
                else:
                    logger.error('No action defined for key: ' + str(key))
            else:
                logger.error(event.src_path + ' contains invalid content: ' + str(s))
        remove_file(event.src_path)
    else:
        logger.info('New event - %s.' % event)
    logger.debug("end of register watcher event - %s" % event)


def remove_file(path):
    if os.path.isfile(path):
        logger.debug('removeing ' + path)
        try:
            os.remove(path)
        except:
            logger.error("Unexpected error:"+ str(sys.exc_info()[0]))


def register_motion_event(source, device_id):
    if 'Hue' in source:
        m = Sensor.objects.get(id=device_id)
    elif 'Vivint' in source:
        m = Device.objects.get(id=device_id)
    logger.info('Sensor{' + source + '}{' + m.name + '}{' + str(m.id) + '}{' + m.type + '}{Active}')
    try:
        t = Trigger.objects.get(trigger=(Trigger.MOTION), motion_detector__source_id=device_id)
        if t.enabled:
            logger.debug('Trigger:{' + t.name + '}{' + str(t.id) + '}{fired}')
            eval = True
        else:
            logger.debug('Trigger:{' + t.name + '}{' + str(t.id) + '}{disabled}')
            eval = False
    except:
        eval = False

    if eval:
        evaluate_nuggets(t.id)


def register_sensor_event(source, device_id, state):
    if 'Hue' in source:
        m = Sensor.objects.get(id=device_id)
    elif 'Vivint' in source:
        m = Device.objects.get(id=device_id)
    logger.info('Sensor{' + source + '}{' + m.name + '}{' + str(m.id) + '}{' + m.type + '}{' + state+'}')
    try:
        if state == 'Opened':
            t = Trigger.objects.get(trigger=(Trigger.SENSOR_OPENED), sensor__source_id=device_id)
        elif state == 'Closed':
            t = Trigger.objects.get(trigger=(Trigger.SENSOR_CLOSED), sensor__source_id=device_id)
        elif state == 'Locked':
            t = Trigger.objects.get(trigger=(Trigger.LOCK_LOCKED), lock__source_id=device_id)
        elif state == 'Unlocked':
            t = Trigger.objects.get(trigger=(Trigger.LOCK_UNLOCKED), lock__source_id=device_id)
        else:
            logger.error('Sensor has an unknown state of ' + state)
        if t.enabled:
            logger.debug('Trigger:{' + t.name + '}{' + str(t.id) + '}{fired}')
            eval = True
        else:
            logger.debug('Trigger:{' + t.name + '}{' + str(t.id) + '}{disabled}')
            eval = False
    except:
        eval = False

    if eval:
        evaluate_nuggets(t.id)


def check_secuirty_trigger(t):
    if t.enabled:
        if t.security_armed_to:
            logger.debug("Looking for triggers with security_armed_to flagged")
            if trigger.people__user__first_name == who[0]:
                logger.debug('Trigger:{' + t.name + '}{' + str(t.id) + '}{fired}')
                evaluate_nuggets(t.id)
        if t.security_changed_to:
            logger.debug("Looking for triggers with security_changed_to flagged")
            logger.debug('Trigger:{' + t.name + '}{' + str(t.id) + '}{fired}')
            evaluate_nuggets(t.id)
    else:
        logger.debug('Trigger:{' + t.name + '}{' + str(t.id) + '}{disabled}')

def register_security_event(the_who, state):
    try:
        who = the_who.split()
        username = User.objects.get(first_name=(who[0]), last_name=(who[1])).username
        logger.info('Security{Vivint}{' + username + '} set house to {' + state+'}')
    except:
        logger.info('Security{Vivint}{' + the_who + '} set house to {' + state+']')
    finally:
        who = the_who.split()

    try:
        triggers = Trigger.objects.filter(trigger=(Trigger.SECURITY_ARMED_STATE), security_armed_state=state)
    except:
        logger.error(sys.exc_info()[0])
    else:
        logger.debug('found '+str(triggers.count())+' tiggers with '+state)
        if triggers.count() > 1:
            for trigger in triggers:
                 check_secuirty_trigger(trigger)
        else:
            check_secuirty_trigger(triggers.first())



def register_hvac_event(who, what, oldValue, newValue):
    try:
        v = float(oldValue)
        logger.info('HvacValue:{' + who + '}{' + what + '}{' + str(oldValue) + '}{' + str(newValue)+"}")
    except:
        logger.info('HvacStatus:{' + who + '}{' + what + '}{' + str(oldValue) + '}{' + str(newValue)+"}")


def register_time_event(t):
    if t.enabled:
        logger.debug('Trigger:{' + t.name + '}{' + str(t.id) + '}{fired}')
        evaluate_nuggets(t.id)
    else:
        logger.debug('Trigger:{' + t.name + '}{' + str(t.id) + '}{disabled}')


def check_time_triggers():
    triggers = Trigger.objects.filter(trigger=(Trigger.WINDOW))
    for t in triggers:
        if t.window_start <= timezone.localtime().time() <= t.window_end:
            register_time_event(t)

    triggers = Trigger.objects.filter(trigger=(Trigger.SCHEDULE))
    for t in triggers:
        if t.external_schedule.source == 1:
            schedule = Schedule.objects.get(id=(t.external_schedule.source_id))
            time = schedule.localtime
            time_segments = time.split('/T', 1)
            if 'T' in time_segments[0]:
                start_time = datetime.datetime.strptime(time_segments[0].replace('T', ''), '%H:%M:%S').time()
                if t.external_schedule_delay > 0:
                        start_time = start_time + timedelta(minutes=t.external_schedule_delay)
                end_time = datetime.datetime.strptime(time_segments[1], '%H:%M:%S').time()
                if start_time <= timezone.localtime().time() <= end_time:
                    register_time_event(t)
            elif 'W' in time_segments[0]:
                day = int(datetime.datetime.today().weekday()) + 1
                day_mask = int(time_segments[0].replace('W', ''))
                txt = '{0:08b}'
                day_list = list(txt.format(day_mask))
                if int(day_list[day]) == 1:
                    start_time = datetime.datetime.strptime(time_segments[1].replace('T', ''), '%H:%M:%S')
                    if t.external_schedule_delay > 0:
                        start_time = start_time + timedelta(minutes=t.external_schedule_delay)
                    if len(time_segments) > 2:
                        end_time = datetime.datetime.strptime(time_segments[2], '%H:%M:%S').time()
                    else:
                        end_time = (start_time + datetime.timedelta(minutes=1)).time()
                    if start_time.time() <= timezone.localtime().time() <= end_time:
                        register_time_event(t)
            else:
                logger.error('Hue time format in schedule not accounted for. ' + str(time))
        else:
            logger.warning('There is no external schedule parser setup for type: ' + Trigger.SOURCE[t.external_schedule.source])


def is_anyone_home():
    p = Person.objects.all()
    for person in p:
        if person.is_home:
            return True

    logger.debug('no one is home')
    return False


def is_nugget_runable(nug):
    if nug.enabled:
        if not nug.only_execute_if_someone_is_home:
            return True
        if is_anyone_home():
            return True
    else:
        logger.debug(nug.name + ' is disabled')
    return False


def evaluate_nuggets(t_id):
    nugs = Nugget.objects.filter(triggers=t_id)
    for nug in nugs:
        if is_nugget_runable(nug):
            triggers = nug.triggers.all()
            results = []
            logger.debug('Evaluating: ' + nug.name + "  ("+str(len(triggers))+" triggers)")
            for t in triggers:
                if t.id == t_id:
                    logger.debug('  TEST:  ' + t.name + ' ' + str(t.id) + ' True')
                    results.append(True)
                else:
                    if t.trigger == t.MOTION:
                        if t.motion_detector.source == 0:
                            state = Device.objects.get(id=(t.motion_detector.source_id)).state
                            if state == 'Open':
                                state = True
                            elif state == 'Closed':
                                state = False
                            else:
                                state = False
                            results.append(state)
                            logger.debug('  TEST:  ' + nug.name + ':Vivint:' + t.motion_detector.name + ' state ' + str(state))
                        elif t.motion_detector.source == 1:
                            state = Sensor.objects.get(id=(t.motion_detector.source_id)).presence
                            logger.debug('  TEST:  ' + nug.name + ':Hue:' + t.motion_detector.name + ' state ' + str(state))
                            results.append(state)
                        else:
                            logger.warning('There is no motion state lookup for source ' + str(t.motion_detector_id__source))
                            results.append(False)
                    elif t.trigger == t.WINDOW:
                        if t.window_start <= timezone.localtime().time() <= t.window_end:
                            logger.debug("  TEST:  "+t.name + ' timeframe state True')
                            results.append(True)
                        else:
                            logger.debug("  TEST:  "+t.name + ' timeframe state False')
                            results.append(False)
                    elif t.trigger == t.SCHEDULE:
                        logger.error('code has not been written for SCHEDULE trigger')
                        results.append(False)
                    elif t.trigger == t.SENSOR_OPENED:
                        logger.error('code has not been written for SENSOR_OPENED trigger')
                        results.append(False)
                    elif t.trigger == t.SENSOR_CLOSED:
                        logger.error('code has not been written for SENSOR_CLOSED trigger')
                        results.append(False)
                    elif t.trigger == t.LOCK_UNLOCKED:
                        logger.error('code has not been written for LOCK_UNLOCKED trigger')
                        results.append(False)
                    elif t.trigger == t.LOCK_LOCKED:
                        logger.error('code has not been written for LOCK_LOCKED trigger')
                        results.append(False)
                    elif t.trigger == t.HVAC_ACTIVITY:
                        logger.error('code has not been written for HVAC_ACTIVITY trigger')
                        results.append(False)
                    elif t.trigger == t.HVAC_FAN:
                        logger.error('code has not been written for HVAC_FAN trigger')
                        results.append(False)
                    elif t.trigger == t.HVAC_HITS_TEMP:
                        logger.error('code has not been written for HVAC_HITS_TEMP trigger')
                        results.append(False)
                    elif t.trigger == t.HVAC_HOLD:
                        logger.error('code has not been written for HVAC_HOLD trigger')
                        results.append(False)
                    elif t.trigger == t.HVAC_HEATMODE:
                        logger.error('code has not been written for HVAC_HEATMODE trigger')
                        results.append(False)
                    elif t.trigger == t.HVAC_FILTRLVL:
                        logger.error('code has not been written for HVAC_FILTRLVL trigger')
                        results.append(False)
                    elif t.trigger == t.HVAC_HUMLVL:
                        logger.error('code has not been written for HVAC_HUMLVL trigger')
                        results.append(False)
                    elif t.trigger == t.CUSTOM_EVENT:
                        logger.error('code has not been written for CUSTOM_EVENT trigger')
                        results.append(False)
                    elif t.trigger == t.SECURITY_ARMED_STATE:
                        state = Panel.objects.get(id=(t.security_panel.id)).armed_state
                        if state == t.security_armed_state:
                            logger.debug("  TEST:  "+t.security_armed_state+' matches armed state '+state)
                            results.append(True)
                        else:
                            logger.debug("  TEST:  "+t.security_armed_state+' does not match armed state '+state)
                            results.append(False)
                    elif t.trigger == t.PEOPLE:
                        if t.people_has_left:
                            try:
                                for person in t.people.all():
                                    if person.is_home:
                                        logger.debug("  TEST:  "+person.user.username + ' found to be home False')
                                        results.append(False)
                                    else:
                                        logger.debug("  TEST:  "+person.user.username + ' found to be not home True')
                                        results.append(True)
                            except:
                                results.append(False)
                        elif t.people_has_arrived:
                            try:
                                for person in t.people.all():
                                    if person.is_home:
                                        logger.debug("  TEST:  "+person.user.username + ' found to be home True')
                                        results.append(True)
                                    else:
                                        logger.debug("  TEST:  "+person.user.username + ' found not to be home False')
                                        results.append(False)
                            except:
                                results.append(False)
                    else:
                        logger.error('No nugget evaluation has been defined for: ' + t.trigger)
            logger.debug("  Results: "+str(results))
            if all(results):
                execute_actions(nug.id)
        else:
            logger.debug('Nugget ' + nug.name + ' is not runable and its trigger(s) fired')


def execute_actions(n_id):
    nug = Nugget.objects.get(id=n_id)
    for action in nug.actions.all():
        if action.enabled:
            if action.action_grace_period <= 0 or timezone.localtime() - action.last_action_time > timedelta(minutes=(int(action.action_grace_period))):
                run_action(action)
                logger.debug("execute_actions:{"+action.name+"}{"+str(action.id)+"}{"+action.action+"}{"+str(action.enabled)+"}{"+nug.name+"}{"+str(nug.id)+"}")
            else:
                logger.debug('Not running '+action.name+' as it is within the cool down period of ' + str(action.action_grace_period))
        else:
            logger.debug("execute_actions:{"+action.name+"}{"+str(action.id)+"}{"+action.action+"}{"+str(action.enabled)+"}{"+nug.name+"}{"+str(nug.id)+"}")


def run_action(action):
    logger.debug("Attempting to run "+action.name)
    if action.action == action.PLAY_SCENE:
        scenes = action.scenes.all()
        if scenes:
            for scene in scenes:
                s = Scene.objects.get(id=(scene.id))
                HueAction.set_scene_trans_time(s, action.scenes_transition_time)
                HueAction.play_scene(s)
                # reset scene states to fast
                HueAction.set_scene_trans_time(s,3)
                update_last_run(action)
        else:
            logger.error("run_action:{"+action.name+"}{failed}{Query set is empty}")
    elif action.action == action.PLAY_RANDOM_SCENE:
        scenes = action.scenes.all()
        if scenes:
            scene = random.choice(scenes)
            s = Scene.objects.get(id=(scene.id))
            HueAction.set_scene_trans_time(s, action.scenes_transition_time)
            HueAction.play_scene(s)
            # reset scene states to fast
            HueAction.set_scene_trans_time(s,3)
            update_last_run(action)
        else:
            logger.error("run_action:{"+action.name+"}{failed}{Query set is empty}")
    elif action.action == action.FLASH_SCENE:
        scenes = action.scenes.all()
        if scenes:
            for scene in scenes:
                HueAction.flash_scene(scene)
                update_last_run(action)

        else:
            logger.error("run_action:{"+action.name+"}{failed}{Query set is empty}")
    elif action.action == action.TURN_ON:
        lights = action.lights.all()
        if lights:
            for light in action.lights.all():
                if light.source == 1:
                    if light.source_type == 0:
                        HueAction.turn_on_light(Light.objects.get(id=(light.source_id)))
                        update_last_run(action)
                    elif light.source_type == 1:
                        HueAction.turn_on_group(Group.objects.get(id=(light.source_id)))
                        update_last_run(action)
                    else:
                        logger.error("run_action:{"+action.name+"}{failed}{Unkown source_type "+str(light.source.type)+"}")
                elif light.source == 2:
                    if light.source_type == 4:
                        if WemoAction.turn_on_light(Wemo.objects.get(id=(light.source_id))):
                            update_last_run(action)
                    else:
                        logger.error("run_action:{"+action.name+"}{failed}{Unkown source_type "+str(light.source.type)+"}")
                elif light.source == 3:
                    if light.source_type == 3:
                        if DecoraAction.turn_on_light(Switch.objects.get(id=(light.source_id))):
                            update_last_run(action)
                    else:
                        logger.error("run_action:{"+action.name+"}{failed}{Unkown source_type "+str(light.source.type)+"}")
                else:
                    logger.error("run_action:{"+action.name+"}{failed}{No source for " + str(lights.source) + " type " + str(light.source.type)+"}")
        else:
            logger.error("run_action:{"+action.name+"}{failed}{Query set is empty}")
    elif action.action == action.TURN_OFF:
        lights = action.lights.all()
        if lights:
            for light in lights:
                if light.source == 1: # 1 hue
                    if light.source_type == 0: # 0 Bulb
                        HueAction.turn_off_light(Light.objects.get(id=(light.source_id)))
                    elif light.source_type == 1: # Group
                        HueAction.turn_off_group(Group.objects.get(id=(light.source_id)))
                        update_last_run(action)
                    else:
                        logger.error("run_action:{"+action.name+"}{failed}{Unkown source_type "+str(light.source.type)+"}")
                elif light.source == 2: # 2 wemo
                    if light.source_type == 4: # Plug
                        if WemoAction.turn_off_light(Wemo.objects.get(id=(light.source_id))):
                            update_last_run(action)
                    else:
                        logger.error("run_action:{"+action.name+"}{failed}{Unkown source_type "+str(light.source.type)+"}")
                elif light.source == 3: # 3 decora
                    if light.source_type == 3: # swicth 3
                        if DecoraAction.turn_off_light(Switch.objects.get(id=(light.source_id))):
                            update_last_run(action)
                    else:
                        logger.error("run_action:{"+action.name+"}{failed}{Unkown source_type "+str(light.source)+"}")
                else:
                    logger.error("run_action:{"+action.name+"}{failed}{No source for " + str(lights.source) + " type " + str(light.source.type)+"}")
        else:
            logger.error("run_action:{"+action.name+"}{failed}{Query set is empty}")
    elif action.action == action.BLINK_HUE:
        lights = action.lights.all()
        if lights:
            for light in lights:
                if light.source == 1:
                    if light.source_type == 1:
                        HueAction.blink_group(Group.objects.get(id=(light.source_id)))
                        update_last_run(action)
                    else:
                        logger.error("run_action:{"+action.name+"}{failed}{Unkown source_type "+str(light.source)+"}")
                else:
                    logger.error("run_action:{"+action.name+"}{failed}{No source for " + str(lights.source) + " type " + str(light.source.type)+"}")
        else:
            logger.error("run_action:{"+action.name+"}{failed}{Query set is empty}")
    elif action.action == action.SEND_TEXT:
        people = action.people.all()
        if people:
            for person in people:
                send_text(person.text_address, action.text_message)
                update_last_run(action)
        else:
            logger.error("run_action:{"+action.name+"}{failed}{Query set is empty}")
    elif action.action == action.HVAC_SET_ACTIVITY:
        logger.error("run_action:{"+action.name+"}{failed}{No action code has been developed for this type}")
    elif action.action == action.SECURITY_SET_STATE:
        logger.error("run_action:{"+action.name+"}{failed}{No action code has been developed for this type}")
    elif action.action == action.PEOPLE_LEAVE:
        people = action.people.all()
        if people:
            for p in people:
                p.is_home = False
                p.save()
                update_last_run(action)
        else:
            logger.error("run_action:{"+action.name+"}{failed}{Query set is empty}")
    elif action.action == action.PEOPLE_ARRIVE:
        people = action.people.all()
        if people:
            for p in people:
                p.is_home = True
                p.save()
                update_last_run(action)
        else:
            logger.error("run_action:{"+action.name+"}{failed}{Query set is empty}")
    elif action.action == action.DISABLE_TRIGGER:
        triggers = action.triggers.all()
        if triggers.count() == 0:
            logger.warning("No triggers defined to disable")
        else:
            for t in triggers:
                t.enabled = False
                t.save()
                update_last_run(action)
    elif action.action == action.ENABLE_TRIGGER:
        triggers = action.triggers.all()
        if triggers.count() == 0:
            logger.warning("No triggers defined to disable")
        else:
            for t in triggers:
                t.enabled = True
                t.save()
                update_last_run(action)
    else:
        logger.error("run_action:{"+action.name+"}{failed}{No action code has been developed for this type}")


def update_last_run(action):
    Action.objects.filter(id=(action.id)).update(last_action_time=(timezone.localtime()))
    logger.info("run_action:{"+action.name+"}{success}")

def send_text(phone, message):
    logger.debug('attempting to send text ' + message)
    sent_from = 'Home-Auto'
    to = [phone]
    subject = 'Home-Auto'
    email_text = message
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    gmail = Account.objects.get(name='Gmail')
    server.login(gmail.username, gmail.password)
    server.sendmail(sent_from, to, email_text)
    server.close()
    logger.info("Text:{"+message+"}")
