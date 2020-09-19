import logging
import requests, json, smtplib
from django.utils import timezone

from homeauto.models.hue import Sensor, Scene, Light, Group
from homeauto.models.wemo import Wemo
from homeauto.models.decora import Switch
from homeauto.models.vivint import Device, Panel
from homeauto.models.house import Trigger, Nugget, Action, HouseLight, Account

import homeauto.hue as HueAction
import homeauto.wemo as WemoAction
import homeauto.decora as DecoraAction

from datetime import timedelta

# This retrieves a Python logging instance (or creates it)
logger = logging.getLogger(__name__)

# this is for intercepting databse updates through the web ui
#from django.db.models.signals import pre_save
#from django.dispatch import receiver
#@receiver(pre_save, sender=Sensor)
#def RegisterSignalEvent(sender, instance, **kwargs):
#    logger.error("recieved signal!!!")

def RegisterMotionEvent(source, device_id):
    if "Hue" in source:
        m = Sensor.objects.get(id=device_id)
    elif "Vivint" in source:
        m = Device.objects.get(id=device_id)
    logger.debug(source+": "+m.name+"("+str(m.id)+") Motion Detected")
    # check if there is a trigger for this motion event
    try:
        t = Trigger.objects.get(trigger=Trigger.MOTION, motion_detector__source_id=device_id)
        if t.enabled:
            logger.debug("Trigger "+t.name+"("+str(t.id)+") fired!")
            eval=True
        else:
            logger.debug("Trigger "+t.name+ " will not fire because it is disabled")
            eval=False
    except:
       eval=False
       pass
    if eval:
       evaluateNuggets(t.id)

def RegisterSensorEvent(source, device_id, state):
    if "Hue" in source:
        m = Sensor.objects.get(id=device_id)
    elif "Vivint" in source:
        m = Device.objects.get(id=device_id)
    logger.debug(source+": "+m.name+"("+str(m.id)+") is now "+state)
    try:
        if state == "Opened":
            t = Trigger.objects.get(trigger=Trigger.SENSOR_OPENED, sensor__source_id=device_id)
        elif state == "Closed":
            t = Trigger.objects.get(trigger=Trigger.SENSOR_CLOSED, sensor__source_id=device_id)
        elif state == "Locked":
            t = Trigger.objects.get(trigger=Trigger.LOCK_LOCKED, lock__source_id=device_id)
        elif state == "Unlocked":
            t = Trigger.objects.get(trigger=Trigger.LOCK_UNLOCKED, lock__source_id=device_id)
        else:
            logger.error("Sensor has an unknown state of "+state)

        if t.enabled:
            logger.debug("Trigger "+t.name+"("+str(t.id)+") fired!")
            eval=True
        else:
            logger.debug("Trigger "+t.name+ " will not fire because it is disabled")
            eval=False
    except:
       eval=False
       pass
    if eval:
       evaluateNuggets(t.id)

def RegisterSecurityEvent(who, state):
    # arm state
    logger.debug(who+" set house to "+state)
    who = who.split()
    try:
        t = Trigger.objects.get(trigger=Trigger.SECURITY_ARMED_STATE, people__user__first_name=who[0], armed_state=state)
        logger.error(t)
        if t.enabled:
            logger.info("Trigger "+t.name+"("+str(t.id)+") fired!")
            eval=True
        else:
            logger.debug("Trigger "+t.name+ " will not fire because it is disabled")
            eval=False
    except:
       eval=False
       pass

    if eval:
       evaluateNuggets(t.id)



def RegisterHvacEvent(who, what, oldValue, newValue):
    logger.info(who+" "+what+" has changed from "+str(oldValue)+" to "+str(newValue))


def RegisterWindowEvent(t):
    if t.enabled:
        logger.debug("Trigger "+t.name+"("+str(t.id)+") fired!")
        evaluateNuggets(t.id)
    else:
        logger.debug("Trigger "+t.name+ " will not fire because it is disabled")

def check_trigger_windows():
    triggers = Trigger.objects.filter(trigger="Window")
    logger.debug("checking time window triggers")
    for t in triggers:
        if t.window_start <= timezone.localtime().time() <= t.window_end :
            RegisterWindowEvent(t)

def evaluateNuggets(t_id):
    nugs = Nugget.objects.filter(triggers=t_id)
    for nug in nugs:
        if nug.enabled:
            logger.debug("Evaluating "+nug.name)
            # you now have a nugget that has the particular trigger which cause this evaluation
            triggers = nug.triggers.all()
            results = []
            for t in triggers:
            # evaulate if each trigger is true?
                if t.id == t_id:
                    logger.debug(t.name+" state: True")
                    results.append(True)
                elif t.trigger == t.MOTION:
                    # vivint motion
                    if t.motion_detector.source == 0:
                        state = Device.objects.get(id=t.motion_detector.source_id).state
                        if state == "Open":
                            state=True
                        elif state == "Closed":
                            state=False
                        else:
                            state=False
                        results.append(state)
                        logger.debug("Vivint Motion Sensor "+t.motion_detector.name+" state: "+str(state))
                    # hue motion
                    elif t.motion_detector.source == 1:
                        state = Sensor.objects.get(id=t.motion_detector.source_id).presence
                        logger.debug("Hue Motion Sensor "+t.motion_detector.name+" state: "+str(state))
                        results.append(state)
                    else:
                        logger.warning("There is no motion state lookup for source: "+str(t.motion_detector_id__source)) 
                        results.append(False)
                elif t.trigger == t.WINDOW:
                    if t.window_start <= timezone.localtime().time() <= t.window_end :
                        logger.debug(t.name+" timeframe state: True")
                        results.append(True)
                    else:
                        logger.debug(t.name+" timeframe state: False")
                        results.append(False)
                elif t.trigger == t.SCHEDULE:
                    logger.debug("evaluating a SCHEDULE trigger")
        #            results.append(state)
                elif t.trigger == t.SENSOR_OPENED:
                    logger.debug("evaluating a SENSOR_OPENED trigger")
        #            results.append(state)
                elif t.trigger == t.SENSOR_CLOSED:
                    logger.debug("evaluating a SENSOR_CLOSED trigger")
        #            results.append(state)
                elif t.trigger == t.LOCK_UNLOCKED:
                    logger.debug("evaluating a LOCK_UNLOCKED trigger")
        #            results.append(state)
                elif t.trigger == t.LOCK_LOCKED:
                    logger.debug("evaluating a LOCK_LOCKED trigger")
        #            results.append(state)
                elif t.trigger == t.HVAC_ACTIVITY:
                    logger.debug("evaluating a HVAC_ACTIVITY trigger")
        #            results.append(state)
                elif t.trigger == t.HVAC_FAN:
                    logger.debug("evaluating a HVAC_FAN trigger")
        #            results.append(state)
                elif t.trigger == t.HVAC_HITS_TEMP:
                    logger.debug("evaluating a HVAC_HITS_TEMP trigger")
        #            results.append(state)
                elif t.trigger == t.HVAC_HOLD:
                    logger.debug("evaluating a HVAC_HOLD trigger")
        #            results.append(state)
                elif t.trigger == t.HVAC_HEATMODE:
                    logger.debug("evaluating a HVAC_HEATMODE trigger")
        #            results.append(state)
                elif t.trigger == t.HVAC_FILTRLVL:
                    logger.debug("evaluating a HVAC_FILTRLVL trigger")
        #            results.append(state)
                elif t.trigger == t.HVAC_HUMLVL:
                    logger.debug("evaluating a HVAC_HUMLVL trigger")
        #            results.append(state)
                elif t.trigger == t.SECURITY_ARMED_STATE:
                    logger.debug("evaluating a SECURITY_ARMED_STATE trigger")
                    try:
                        Panel.objects.get(armed_state = t.armed_state)
                        results.append(True)
                    except:
                        results.append(False)
            logger.debug(nug)
            logger.debug(results)
            if all(results):
                executeActions(nug.id)
            else:
                logger.debug("One or more of the triggers was false, so no actions will be taken.")
        else:
            logger.debug("Nugget "+nug.name+" is disbled and its trigger(s) fired")

def executeActions(n_id):
    nug = Nugget.objects.get(id=n_id)
    for action in nug.actions.all():
        if action.enabled:
            # honor action grace period
            if action.action_grace_period <= 0 or (timezone.localtime() - action.last_action_time > timedelta(minutes=int(action.action_grace_period))):
                logger.info("action "+action.name+" in "+nug.name+" will execute!")
                runActions(action)
            else:
                logger.debug("Not running action as it has run within the grace period of "+str(action.action_grace_period))
        else:
            logger.warning(action.name+" is disabled and will not execute")


def runActions(action):
    if action.action == action.PLAY_SCENE:
        HueAction.playScene(Scene.objects.get(id=action.scene.id))
    elif action.action == action.TURN_ON:
        for light in action.lights.all():
            if light.source == 1: # 1 hue
                if light.source_type == 0: # bulb 0
                    HueAction.turnOnLight(Light.objects.get(id=light.source_id))
                elif light.source_type == 1: # group 1
                    HueAction.turnOnGroup(Group.objects.get(id=light.source_id))
                else:
                    logger.warning("No source_type for: "+str(light.source.type))
            elif light.source == 2: # 2 wemo
                if light.source_type == 4: # plug 4
                    WemoAction.turnOnLight(Wemo.objects.get(id=light.source_id))
                else:
                    logger.warning("No source_type for: "+str(light.source.type))
            elif light.source == 3: # 3 decora
                if light.source_type == 2: #  switch 3
                    DecoraAction.turnOnLight(Switch.objects.get(id=light.source_id))
                else:
                    logger.warning("No source_type for: "+str(light.source.type))
            else:
                logger.warning("No source for: "+str(lights.source)+" type: "+str(light.source.type))
    elif action.action == action.TURN_OFF:
        for light in action.lights.all():
            if light.source == 1: # 1 hue
                if light.source_type == 0: # bulb 0
                    HueAction.turnOffLight(Light.objects.get(id=light.source_id))
                elif light.source_type == 1: # group 1
                    HueAction.turnOffGroup(Group.objects.get(id=light.source_id))
                else:
                    logger.warning("No source_type for: "+str(light.source.type))
            elif light.source == 2: # 2 wemo
                if light.source_type == 4: # plug 4
                    WemoAction.turnOffLight(Wemo.objects.get(id=light.source_id))
                else:
                    logger.warning("No source_type for: "+str(light.source.type))
            elif light.source == 3: # 3 decora
                if light.source_type == 2: #  switch 3
                    DecoraAction.turnOffLight(Switch.objects.get(id=light.source_id))
                else:
                    logger.warning("No source_type for: "+str(light.source.type))
            else:
                logger.warning("No source for: "+str(lights.source)+" type: "+str(light.source.type))
    elif action.action == action.BLINK_HUE:
        for light in action.lights.all():
            if light.source == 1: # 1 hue
                if light.source_type == 1: # group 1
                    HueAction.blinkGroup(Group.objects.get(id=light.source_id))
                else:
                    logger.warning("No source_type for: "+str(light.source.type)+" this only supports type group(1)")
            else:
                logger.warning("No source for: "+str(lights.source)+" type: "+str(light.source.type))
    elif action.action == action.SEND_TEXT:
        for person in action.people.all():
            sendText(person.text_address, action.text_message)
    Action.objects.filter(id=action.id).update(last_action_time = timezone.localtime())



def putCommand(api_url, payload):
    try:
        r = requests.put(api_url, data=json.dumps(payload))
        logger.debug(r.text)
        if 'error' in r.text:
          logger.error(r.text)
    except:
      logger.error("except: "+str(api_url))
      logger.error("except: "+str(payload))

def sendText(phone, message):
    logger.debug('attempting to send text: '+message)
    sent_from = "Home-Auto"
    to = [phone]
    subject = 'Home-Auto'
    email_text = message

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    gmail = Account.objects.get(name="Gmail")
    server.login(gmail.username, gmail.password)
    server.sendmail(sent_from, to, email_text)
    server.close()
    logger.info(message)





