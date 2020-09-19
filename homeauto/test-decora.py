
#import time, datetime
#import subprocess, sys, getopt

#from decimal import Decimal

#from subprocess import call

# /home/ha/web_home_auto/homeauto/python-decora_wifi/decora_wifi

from decora_wifi import DecoraWiFiSession
from decora_wifi.models.person import Person
from decora_wifi.models.residential_account import ResidentialAccount
from decora_wifi.models.residence import Residence



username = 'mr.matthew.f.martin@gmail.com'
password = 'QQKmER67n&!g5'


#home.decora("Foyer", "OFF", "None")
#time.sleep(5)
#home.decora("Foyer", "ON", "10")




session = DecoraWiFiSession()
session.login(username, password)

perms = session.user.get_residential_permissions()
all_residences = []
for permission in perms:
  print(permission)
  if permission.residentialAccountId is not None:
    acct = ResidentialAccount(session, permission.residentialAccountId)
    for res in acct.get_residences():
      all_residences.append(res)
  elif permission.residenceId is not None:
    res = Residence(session, permission.residenceId)
    all_residences.append(res)
for residence in all_residences:
#  print(residence)
  for switch in residence.get_iot_switches():
    attribs = {}
#    print(switch)

#    if switch.name == switch_name:
#      if brightness is not "None":
#        attribs['brightness'] = brightness
#      if command == 'ON':
#        attribs['power'] = 'ON'
#      else:
#        attribs['power'] = 'OFF'
#      logging.debug(switch.name+':'+str(attribs))
#    switch.update_attributes(attribs)

#Person.logout(session)



s = 6
e = 7



#if home.private.getboolean('Devices','decora'):
#  for x in range(s,e):
#    home.decora(home.private.get('Decora', 'switch_'+str(x)), "OFF", "None")

#time.sleep(10)
#if home.private.getboolean('Devices','decora'):
#  for x in range(s,e):
#    home.decora(home.private.get('Decora', 'switch_'+str(x)), "ON", "None")

#time.sleep(10)
#if home.private.getboolean('Devices','decora'):
#  for x in range(s,e):
#    home.decora(home.private.get('Decora', 'switch_'+str(x)), "OFF", "None")

