#!/usr/bin/python

# uses Tenable Security Center API to get you information when the asset was last scanned
# input:  file with assets, one asset per line
# output: excel asset DELIMITER timestamp_of_the last_scan

import json
import requests
from datetime import datetime

#DEBUG = True
DEBUG = False

SC_REPO_NAME = "COM"                    # use repository with this name or substring
SC_REPO_ID   = 0                        # repository id
SC_ASSET_PRE = "com"                    # filter assets by prefix
SC_USERNAME  = "user"                   # sc user
SC_PASSWORD  = "secret"                 # sc password
SC_COOKIE    = 'none'                   # cookie
SC_TOKEN     = 'none'                   # token
SC_HEADERS   = 'none'                   # headers
DELIMITER    = ';'                      # delimiter for exporting lastscan (get_ipinfo_lastscan)

def create_session():

   global SC_COOKIE
   global SC_TOKEN
   global SC_HEADERS

   URL = 'https://localhost/rest/token'
   PARAMS = { \
        "username" : SC_USERNAME, \
        "password" : SC_PASSWORD, \
        "releaseSession" : "true" \
   }

   resp = requests.post(url = URL, params = PARAMS, verify = False)
   if DEBUG:
      print "[d] BEG: auth response"
      print "[d] content: ", resp.content
      print "[d] cookies: ", resp.cookies
      print "[d] END: auth response"


   resp_data = json.loads(resp.content)
   SC_COOKIE = resp.cookies
   SC_TOKEN = resp_data['response']['token']
   SC_HEADERS  = {'content-type': 'application/json', 'X-SecurityCenter' : SC_TOKEN}

def set_repository(repo_name):

   global    SC_REPO_ID

   URL       = 'https://localhost/rest/repository'
   PARAMS    = ''

   resp      = requests.get(url = URL, cookies = SC_COOKIE, headers = SC_HEADERS, params = PARAMS, verify = False)
   resp_data = json.loads(resp.content)

   if DEBUG:
      print json.dumps(resp_data, indent = 4, sort_keys = True)

   resp_data = json.loads(resp.content)
   for field in resp_data['response']:
      if repo_name in field['name']:
        SC_REPO_ID = int(field['id'])

   if DEBUG:
     print "repository id: ", SC_REPO_ID


def list_asset_groups():

   URL       = 'https://localhost/rest/asset'
   PARAMS    = ''

   resp      = requests.get(url = URL, cookies = SC_COOKIE, headers = SC_HEADERS, params = PARAMS, verify = False)
   resp_data = json.loads(resp.content)

   if DEBUG:
      print json.dumps(resp_data, indent = 4, sort_keys = True)

   for field in resp_data['response']['usable']:
      if SC_ASSET_PRE in field['name']:
         print field['name']


def get_ipinfo_lastscan(ip_address):

   URL       = 'https://localhost/rest/repository/' + str(SC_REPO_ID) + '/deviceInfo'
   #URL       = 'https://localhost/rest/repository/' + str(SC_REPO_ID) + '/ipInfo'
   PARAMS    = 'ip=' + ip_address

   resp      = requests.get(url = URL, cookies = SC_COOKIE, headers = SC_HEADERS, params = PARAMS, verify = False)
   resp_data = json.loads(resp.content)

   lastscan = datetime.utcfromtimestamp(int(resp_data['response']['lastScan'])).strftime('%Y-%m-%d')
   print ip_address.rstrip() + DELIMITER + lastscan


def get_lastscan(asset_file):

   with open(asset_file) as fp:
      ip_address = fp.readline()
      while ip_address:

         try:
            get_ipinfo_lastscan(ip_address)
         except KeyError:
            print ip_address.rstrip() + DELIMITER + 'no_scan'

         ip_address = fp.readline()


if __name__ == '__main__':

   create_session()
   set_repository(SC_REPO_NAME)
   get_lastscan('/home/automaton/servers_prod_ip_all.txt')
   get_lastscan('/home/automaton/servers_test_ip_all.txt')
   list_asset_groups()
   #get_ipinfo_lastscan('ip.v.4.ad')
   #list_asset_groups()
