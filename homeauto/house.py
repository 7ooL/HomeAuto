import logging, requests, json, smtplib, datetime, os
from django.utils import timezone
from homeauto.models.hue import Sensor, Scene, Light, Group, Schedule
from homeauto.models.wemo import Wemo
from homeauto.models.decora import Switch
from homeauto.models.vivint import Device, Panel
from homeauto.models.house import Trigger, Nugget, Action, HouseLight, Account, Person, CustomEvent
import homeauto.hue as HueAction
import homeauto.wemo as WemoAction
import homeauto.decora as DecoraAction
from datetime import timedelta
from django.db.models.signals import pre_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)

# this is for intercepting databse updates
@receiver(pre_save, sender=Person)
def register_person_event(sender, instance, **kwargs):
    if instance.is_home:
        try:
            t = Trigger.objects.get(trigger=(Trigger.PEOPLE), people_has_arrived=True, people=instance)
            if t.enabled:
                if t.people.count() > 1:
                    for person in t.people.all():
                        if not person.is_home:
                            eval = False
                            logger.debug(person.user.username + ' found not to be home')
                            return
                        else:
                            eval = True

                    logger.debug('Trigger:' + t.name + ' ' + str(t.id) + ' fired')
                else:
                    logger.debug('Trigger:' + t.name + ' ' + str(t.id) + ' fired')
                    eval = True
            else:
                logger.debug('Trigger:' + t.name + ' ' + str(t.id) + ' disabled')
                eval = False
        except Exception as e:
            try:
                eval = False
            finally:
                e = None
                del e
        if eval:
            evaluate_nuggets(t.id)
    else:
        try:
            t = Trigger.objects.get(trigger=(Trigger.PEOPLE), people_has_arrived=False, people=instance)
            if t.enabled:
                if t.people.count() > 1:
                    for person in t.people.all():
                        if person.is_home:
                            eval = False
                            logger.debug(person.user.username + ' found to still be home')
                            return
                        else:
                            eval = True

                    logger.debug('Trigger:' + t.name + ' ' + str(t.id) + ' fired')
                else:
                    logger.debug('Trigger:' + t.name + ' ' + str(t.id) + ' fired')
                    eval = True
            else:
                logger.debug('Trigger:' + t.name + ' ' + str(t.id) + ' disabled')
                eval = False
        except Exception as e:
            try:
                eval = False
            finally:
                e = None
                del e
        if eval:
            evaluate_nuggets(t.id)


def register_watcher_event(event):
    if event.event_type == 'created':
        logger.debug('Received created event - %s.' % event.src_path)
        with open(event.src_path) as f:
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
                    logger.error('There are no watcher events defined for: ' + s[0])
                    remove_file(event.src_path)
                    return
                else:
                    try:
                        logger.warning(e.name)
                        t = Trigger.objects.get(trigger=(Trigger.CUSTOM_EVENT), event__name=(e.name))
                        if t.enabled:
                            logger.debug('Trigger:' + t.name + ' ' + str(t.id) + ' fired')
                            eval = True
                        else:
                            logger.debug('Trigger:' + t.name + ' ' + str(t.id) + ' disabled')
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
                key = s[0]
                value = s[1]
                logger.debug('Found:' + key + ':' + value)
                if key.lower() == 'arrive':
                    p = Person.objects.get(user__username=value)
                    if p:
                        p.is_home = True
                        p.save()
                    else:
                        logger.error('No person was found with the username: ' + str(value))
                elif key.lower() == 'leave':
                    p = Person.objects.get(user__username=value)
                    if p:
                        p.is_home = False
                        p.save()
                    else:
                        logger.error('No person was found with the username: ' + str(value))
                else:
                    logger.error('No action defined for key: ' + str(key))
            else:
                logger.error(event.src_path + ' contains invalid content: ' + str(s))
        remove_file(event.src_path)


def remove_file(path):
    if os.path.isfile(path):
        logger.debug('removeing ' + path)
        os.remove(path)


def register_motion_event(source, device_id):
    if 'Hue' in source:
        m = Sensor.objects.get(id=device_id)
    elif 'Vivint' in source:
        m = Device.objects.get(id=device_id)
    logger.debug('Sensor:' + source + ':' + m.name + ':' + str(m.id) + ':' + m.type + ':Active')
    try:
        t = Trigger.objects.get(trigger=(Trigger.MOTION), motion_detector__source_id=device_id)
        if t.enabled:
            logger.debug('Trigger:' + t.name + ' ' + str(t.id) + ' fired')
            eval = True
        else:
            logger.debug('Trigger:' + t.name + ' ' + str(t.id) + ' disabled')
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
    logger.debug('Sensor:' + source + ':' + m.name + ':' + str(m.id) + ':' + m.type + ':' + state)
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
            logger.debug('Trigger:' + t.name + ' ' + str(t.id) + ' fired')
            eval = True
        else:
            logger.debug('Trigger:' + t.name + ' ' + str(t.id) + ' disabled')
            eval = False
    except:
        eval = False

    if eval:
        evaluate_nuggets(t.id)


def register_security_event(who, state):
    logger.debug('Security:Vivint:' + who + ' set house to ' + state)
    who = who.split()
    try:
        t = Trigger.objects.get(trigger=(Trigger.SECURITY_ARMED_STATE), people__user__first_name=(who[0]), armed_state=state)
        logger.error(t)
        if t.enabled:
            logger.debug('Trigger:' + t.name + ' ' + str(t.id) + ' fired')
            eval = True
        else:
            logger.debug('Trigger:' + t.name + ' ' + str(t.id) + ' disabled')
            eval = False
    except:
        eval = False

    if eval:
        evaluate_nuggets(t.id)


def register_hvac_event(who, what, oldValue, newValue):
    logger.info('Hvac:' + who + ':' + what + ' changed from ' + str(oldValue) + ' to ' + str(newValue))


def register_time_event(t):
    if t.enabled:
        logger.debug('Trigger:' + t.name + ' ' + str(t.id) + ' fired')
        evaluate_nuggets(t.id)
    else:
        logger.debug('Trigger:' + t.name + ' ' + str(t.id) + ' disabled')


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
            logger.info('Evaluating:' + nug.name)
            triggers = nug.triggers.all()
            results = []
            for t in triggers:
                if t.id == t_id:
                    logger.debug('Trigger:' + t.name + ' ' + str(t.id) + ' True')
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
                            logger.debug('Evaluating:' + nug.name + ':Vivint:' + t.motion_detector.name + ' state ' + str(state))
                        elif t.motion_detector.source == 1:
                            state = Sensor.objects.get(id=(t.motion_detector.source_id)).presence
                            logger.debug('Evaluating:' + nug.name + ':Hue:' + t.motion_detector.name + ' state ' + str(state))
                            results.append(state)
                        else:
                            logger.warning('There is no motion state lookup for source ' + str(t.motion_detector_id__source))
                            results.append(False)
                    else:
                        if t.trigger == t.WINDOW:
                            if t.window_start <= timezone.localtime().time() <= t.window_end:
                                logger.debug(t.name + ' timeframe state True')
                                results.append(True)
                            else:
                                logger.debug(t.name + ' timeframe state False')
                                results.append(False)
                        else:
                            if t.trigger == t.SCHEDULE:
                                logger.debug('evaluating a SCHEDULE trigger')
                            else:
                                if t.trigger == t.SENSOR_OPENED:
                                    logger.debug('evaluating a SENSOR_OPENED trigger')
                                else:
                                    if t.trigger == t.SENSOR_CLOSED:
                                        logger.debug('evaluating a SENSOR_CLOSED trigger')
                                    else:
                                        if t.trigger == t.LOCK_UNLOCKED:
                                            logger.debug('evaluating a LOCK_UNLOCKED trigger')
                                        else:
                                            if t.trigger == t.LOCK_LOCKED:
                                                logger.debug('evaluating a LOCK_LOCKED trigger')
                                            else:
                                                if t.trigger == t.HVAC_ACTIVITY:
                                                    logger.debug('evaluating a HVAC_ACTIVITY trigger')
                                                else:
                                                    if t.trigger == t.HVAC_FAN:
                                                        logger.debug('evaluating a HVAC_FAN trigger')
                                                    else:
                                                        if t.trigger == t.HVAC_HITS_TEMP:
                                                            logger.debug('evaluating a HVAC_HITS_TEMP trigger')
                                                        else:
                                                            if t.trigger == t.HVAC_HOLD:
                                                                logger.debug('evaluating a HVAC_HOLD trigger')
                                                            else:
                                                                if t.trigger == t.HVAC_HEATMODE:
                                                                    logger.debug('evaluating a HVAC_HEATMODE trigger')
                                                                else:
                                                                    if t.trigger == t.HVAC_FILTRLVL:
                                                                        logger.debug('evaluating a HVAC_FILTRLVL trigger')
                                                                    else:
                                                                        if t.trigger == t.HVAC_HUMLVL:
                                                                            logger.debug('evaluating a HVAC_HUMLVL trigger')
                                                                        else:
                                                                            if t.trigger == t.SECURITY_ARMED_STATE:
                                                                                logger.debug('evaluating a SECURITY_ARMED_STATE trigger')
                                                                                try:
                                                                                    Panel.objects.get(armed_state=(t.armed_state))
                                                                                    results.append(True)
                                                                                except:
                                                                                    results.append(False)

                                                                            else:
                                                                                logger.error('No nugget evaluation has been defined for: ' + t.TRIGGER_TYPES)

            logger.debug(nug)
            logger.debug(results)
            if all(results):
                execute_actions(nug.id)
            else:
                logger.debug('One or more of the triggers was false, so no actions will be taken.')
        else:
            logger.debug('Nugget ' + nug.name + ' is not runable and its trigger(s) fired')


def execute_actions(n_id):
    nug = Nugget.objects.get(id=n_id)
    for action in nug.actions.all():
        if action.enabled:
            if action.action_grace_period <= 0 or timezone.localtime() - action.last_action_time > timedelta(minutes=(int(action.action_grace_period))):
                logger.info('Action:' + action.name + ':' + nug.name + ':' + str(action.enabled))
                run_actions(action)
            else:
                logger.debug('Not running action as it has run within the grace period of ' + str(action.action_grace_period))
        else:
            logger.warning('Action:' + action.name + ':' + nug.name + ':' + str(action.enabled))


def run_actions(action):
    if action.action == action.PLAY_SCENE:
        scenes = action.scenes.all()
        if scenes:
            for scene in scenes:
                HueAction.play_scene(Scene.objects.get(id=(scene.id)))

        else:
            logger.error('Query set is empty for:' + action.name)
    elif action.action == action.TURN_ON:
        lights = action.lights.all()
        if lights:
            for light in action.lights.all():
                if light.source == 1:
                    if light.source_type == 0:
                        HueAction.turn_on_light(Light.objects.get(id=(light.source_id)))
                    elif light.source_type == 1:
                        HueAction.turn_on_group(Group.objects.get(id=(light.source_id)))
                    else:
                        logger.warning('No source_type for ' + str(light.source.type))
                else:
                    if light.source == 2:
                        if light.source_type == 4:
                            WemoAction.turn_on_light(Wemo.objects.get(id=(light.source_id)))
                        else:
                            logger.warning('No source_type for ' + str(light.source.type))
                    else:
                        if light.source == 3:
                            if light.source_type == 2:
                                DecoraAction.turn_on_light(Switch.objects.get(id=(light.source_id)))
                            else:
                                logger.warning('No source_type for ' + str(light.source.type))
                        else:
                            logger.warning('No source for ' + str(lights.source) + ' type ' + str(light.source.type))

        else:
            logger.error('Query set is empty for:' + action.name)
    elif action.action == action.TURN_OFF:
        lights = action.lights.all()
        if lights:
            for light in lights:
                if light.source == 1:
                    if light.source_type == 0:
                        HueAction.turn_off_light(Light.objects.get(id=(light.source_id)))
                    elif light.source_type == 1:
                        HueAction.turn_off_group(Group.objects.get(id=(light.source_id)))
                    else:
                        logger.warning('No source_type for ' + str(light.source.type))
                else:
                    if light.source == 2:
                        if light.source_type == 4:
                            WemoAction.turn_off_light(Wemo.objects.get(id=(light.source_id)))
                        else:
                            logger.warning('No source_type for ' + str(light.source.type))
                    else:
                        if light.source == 3:
                            if light.source_type == 2:
                                DecoraAction.turn_off_light(Switch.objects.get(id=(light.source_id)))
                            else:
                                logger.warning('No source_type for ' + str(light.source))
                        else:
                            logger.warning('No source for ' + str(lights.source) + ' type ' + str(light.source.type))

        else:
            logger.error('Query set is empty for:' + action.name)
    elif action.action == action.BLINK_HUE:
        lights = action.lights.all()
        if lights:
            for light in lights:
                if light.source == 1:
                    if light.source_type == 1:
                        HueAction.blink_group(Group.objects.get(id=(light.source_id)))
                    else:
                        logger.warning('No source_type for ' + str(light.source.type) + ' this only supports type group(1)')
                else:
                    logger.warning('No source for ' + str(lights.source) + ' type ' + str(light.source.type))

        else:
            logger.error('Query set is empty for:' + action.name)
    elif action.action == action.SEND_TEXT:
        people = action.people.all()
        if people:
            for person in people:
                send_text(person.text_address, action.text_message)

        else:
            logger.error('Query set is empty for:' + action.name)
    elif action.action == action.HVAC_SET_ACTIVITY:
        logger.warning('No action code has been defined for: ' + action.action)
    elif action.action == action.SECURITY_SET_STATE:
        logger.warning('No action code has been defined for: ' + action.action)
    elif action.action == action.PEOPLE_LEAVE:
        people = action.people.all()
        if people:
            for p in people:
                p.is_home = False
                p.save()

        else:
            logger.error('Query set is empty for:' + action.name)
    elif action.action == action.PEOPLE_ARRIVE:
        people = action.people.all()
        if people:
            for p in people:
                p.is_home = True
                p.save()

        else:
            logger.error('Query set is empty for:' + action.name)
    else:
        logger.warning('No action code has been defined for: ' + action.action)
    Action.objects.filter(id=(action.id)).update(last_action_time=(timezone.localtime()))


def put_command(api_url, payload):
    try:
        r = requests.put(api_url, data=(json.dumps(payload)))
        logger.debug(r.text)
        if 'error' in r.text:
            logger.error(r.text)
    except:
        logger.error('except ' + str(api_url))
        logger.error('except ' + str(payload))


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
    logger.info(message)
