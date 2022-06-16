#!/usr/local/bin/python
# API consumption tool to capture and compare list of network devices from Librenms/Netbox and outputs the diff
# Helpful for comparing list of monitored network devices configured in librenms against recorded inventory in netbox
# Use to cleanup obsolete netbox inventory records and conversely to ensure any missed devices get configured in librenms for monitoring

from datetime import datetime
import json
import requests
import difflib
import sys

# Netbox vars
NETBOX_URL = 'https://[FIXME_DOMAIN]/netbox/api/dcim/devices/?format=json&limit=0&role=network&role=out-of-band'
NETBOX_API_TOKEN = input("What is your Netbox API Token?\n")
date = datetime.now().strftime("%Y_%m_%d")
netbox_filename = "netbox-junos-ios-" + str(date) + ".txt"
netbox_params = {'Authorization': 'Token {}'.format(NETBOX_API_TOKEN)}
netbox_api_result = requests.get(NETBOX_URL, headers=netbox_params)
netbox_devices_json = json.loads(netbox_api_result.text)

# Librenms vars
LIBRENMS_JUNOS_URL = 'https://librenms.[FIXME_DOMAIN]/api/v0/devices?type=os&query=junos'
LIBRENMS_IOS_URL = 'https://librenms.[FIXME_DOMAIN]/api/v0/devices?type=os&query=ios'
LIBRENMS_API_TOKEN = input("What is your Librenms API Token?\n")
librenms_filename = "librenms-junos-ios-" + str(date) + ".txt"
librenms_params = {'X-Auth-Token': '{}'.format(LIBRENMS_API_TOKEN)}
librenms_junos_api_result = requests.get(LIBRENMS_JUNOS_URL, headers=librenms_params)
librenms_ios_api_result = requests.get(LIBRENMS_IOS_URL, headers=librenms_params)
librenms_junos_devices_json = json.loads(librenms_junos_api_result.text)
librenms_ios_devices_json = json.loads(librenms_ios_api_result.text)

# Get list of ios and junos network devices from Netbox API and save to file:
with open(netbox_filename, "w") as f:
  for i in netbox_devices_json['results']:
       if i['name'] is not None:
         f.write(i['name'])
         f.write("\n")
f.close()

# Get list of junos network devices from Librenms API and save to file:
with open(librenms_filename, "w") as f:
  for i in librenms_junos_devices_json['devices']:
      f.write(i['hostname'])
      f.write("\n")
f.close()

# Get list of ios network devices from Librenms API and save to file:
with open(librenms_filename, "a") as f:
    for i in librenms_ios_devices_json['devices']:
        f.write(i['hostname'])
        f.write("\n")
f.close()

file_1_text = open(netbox_filename).readlines()
file_2_text = open(librenms_filename).readlines()

# Find and print the diff between netbox/librenms network devices
for line in difflib.unified_diff(
    file_1_text, sorted(file_2_text), fromfile=netbox_filename,
    tofile=librenms_filename):
    sys.stdout.write(line)
