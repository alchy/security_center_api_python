#!/usr/bin/python

import json
import requests
from datetime import datetime

DEBUG = False

SC_COOKIE = ''
SC_HEADERS = ''
PARAMS = ''

ENV_TEST = 'Test'
ENV_TEST_FILE = '/home/automaton/servers_prod_ip_all.txt'
ENV_PROD = 'Prod'
ENV_PROD_FILE = '/home/automaton/servers_test_ip_all.txt'


def get_servers_by_ip_page(env, NEXT_PAGE = False):

   if NEXT_PAGE is False:
      URL       = 'https://******/'
      if DEBUG:
         print '[i]setting url to ', URL
   else:
      URL = NEXT_PAGE

   resp      = requests.get(url = URL, cookies = SC_COOKIE, headers = SC_HEADERS, params = PARAMS, verify = False)
   resp_data = json.loads(resp.content)

   if DEBUG:
      print json.dumps(resp_data, indent = 4, sort_keys = True)

   resp_data = json.loads(resp.content)

   try:
      if resp_data['next']:
         NEXT_PAGE = resp_data['next']['$ref']
   except KeyError:
      pass

   item_count = 0
   servers_by_ip = []
   for field in resp_data['items']:
      try:
         if env in field['prostredi']:
            item_count += 1
            servers_by_ip.append(field['ip_server'])
      except KeyError:
         pass

   if item_count == 0:
      return servers_by_ip, False
   else:
      return servers_by_ip, NEXT_PAGE


def get_servers_by_ip(env):
   env_servers = []

   res, NEXT_PAGE = get_servers_by_ip_page(env)
   env_servers.extend(res)

   while NEXT_PAGE:
      if DEBUG:
         print '[i] paginating...'
         print '[i] NEXT_PAGE = ', NEXT_PAGE

      res, NEXT_PAGE = get_servers_by_ip_page(env, NEXT_PAGE)
      try:
         env_servers.extend(res)
      except IndexError:
         pass

   env_servers = set(env_servers)
   env_servers = list(env_servers)

   return env_servers


def save_list_to_file(filename, save_list):
   with open(filename, 'w') as f:
      for item in save_list:
         f.write("%s\n" % item)


if __name__ == '__main__':

   list_of_ips = get_servers_by_ip(ENV_PROD)
   save_list_to_file(ENV_TEST_FILE, list_of_ips)
   if DEBUG:
      print list_of_ips
      print len(list_of_ips)


   list_of_ips = get_servers_by_ip(ENV_TEST)
   save_list_to_file(ENV_PROD_FILE, list_of_ips)
   if DEBUG:
      print list_of_ips
      print len(list_of_ips)
