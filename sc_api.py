#!/usr/bin/python

import json
import requests
from datetime import datetime

DEBUG = False

SC_USERNAME = "some_username"
SC_PASSWORD = "some_password"
SC_COOKIE   = 'none'
SC_TOKEN    = 'none'
SC_HEADERS  = 'none'
DELIMITER   = ';'

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


def get_vzp_assets():

   URL       = 'https://localhost/rest/asset'
   PARAMS    = ''

   resp      = requests.get(url = URL, cookies = SC_COOKIE, headers = SC_HEADERS, params = PARAMS, verify = False)
   resp_data = json.loads(resp.content)

   if DEBUG:
      print json.dumps(resp_data, indent = 4, sort_keys = True)

   for field in resp_data['response']['usable']:
      if 'vzp' in field['name']:
         print field['name']


def get_vzp_ipinfo(ip_address):

   URL       = 'https://localhost/rest/repository/7/ipInfo'
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
            get_vzp_ipinfo(ip_address)
         except KeyError:
            print ip_address.rstrip() + DELIMITER + 'no_scan'

         ip_address = fp.readline()


if __name__ == '__main__':

   create_session()
   get_lastscan('/home/automaton/servers_prod_ip_all.txt')
   get_lastscan('/home/automaton/servers_test_ip_all.txt')
   #get_vzp_assets()
