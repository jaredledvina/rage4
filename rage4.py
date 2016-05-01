#!/bin/python3

import argparse
import configparser
import json
import logging as log
import os
import requests
import sys
from tabulate import tabulate

config = configparser.ConfigParser()
if os.path.isfile('config.ini'):
    config.read('config.ini')
email = config['rage4']['username'] or os.environ.get('RAGE4_USERNAME')
api_key = config['rage4']['api_token'] or os.environ.get('RAGE4_API_TOKEN') 
# log.error("Unable to find config and environment variables")

base_url = 'https://rage4.com/rapi/'


class DNS_Manager:
    """A DNS Managing class"""
    def __init__(self, base_url, api_key, email):
        self.base_url = base_url
        self.api_key = api_key
        self.email = email
        self.auth = (email, api_key) 
        self.domains = self._make_request('getdomains/', {}) 
        for d in self.domains:
            payload = {
                'id': d['id'],
                'name': d['name']}
        self.records = self._make_request('getrecords/', payload)
    
    def _make_request(self, endpoint, payload):
        log.debug('Sending payload: {}'.format(payload))
        try:
            r = requests.get(self.base_url + endpoint, auth=self.auth, params=payload)
        except requests.ConnectionError as e:
            log.error('Received Connection Error: {}'.format(e)) 
            raise 
        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            log.error('Receieved HTTP Error: {}'.format(e))
            raise
        log.debug(r.json())
        log.debug('Status Code: {}'.format(r.status_code))
        return r.json()
    
    def _records_with_type(self, type):
        return [record for record in self.records if record['type'] == type]
    
    def _records_with_name(self, name):
        return [record for record in self.records if record['name'] == name]

    def _record_exists(self, name):
        for item in self.records:
            if name == item['name']:
                return True

    def show(self, record):
        types = ['A', 'AAAA', 'CNAME', 'TXT']
        table = []
        if record in types:
            log.debug('Looking up {} as type'.format(record))
            for each in self._records_with_type(record):
                table.append([each['name'], each['content']])
        else:
            log.debug('Looking up {} as name'.format(record))
            for each in self._records_with_name(record):
                table.append([each['name'], each['content']])
        if not table: 
            log.error('Unable to find record: {}'.format(record))
        else:
            print(tabulate(table))


    def add(self, type, priority, name, content):
        #TODO: Check if record already exists
        if not self._record_exists(name):
            payload = {
                    'id': self.domains[0]['id'],
                    'name': name,
                    'content': content,
                    'type': type,
                    'priority': priority
                  }
            self._make_request('createrecord/', payload)
            log.info('Created record: {} {} {}'.format(name, type, content))
        else:
            log.error('Record with the name {} already exists'.format(name))

    def delete(self, record_name):
        for item in self._records_with_name(record_name):
            payload = { 'id': item['id']} 
            self._make_request('deleterecord/', payload)
            log.info('Deleted record: {}'.format(record_name))


if __name__ == '__main__':
    dns = DNS_Manager(base_url, api_key, email)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='Enable debug messages')
    subparser = parser.add_subparsers()

    parser_create = subparser.add_parser('create',
                                         help='Create an new record')
    parser_create.add_argument('type', type=str)
    parser_create.add_argument('priority', type=int, default=1)
    parser_create.add_argument('name', type=str)
    parser_create.add_argument('content', type=str)
    parser_create.set_defaults(action='create')

    parser_show = subparser.add_parser('show',
                                       help='Show record by type or search')
    parser_show.add_argument('search', type=str)
    parser_show.set_defaults(action='show')

    parser_delete = subparser.add_parser('delete',
                                         help='Delete record by name')
    parser_delete.add_argument('name', type=str)
    parser_delete.set_defaults(action='delete')

    args = parser.parse_args()

    if args.verbose:
        log.basicConfig(level=log.DEBUG,
                            format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        log.basicConfig(level=log.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')

    if hasattr(args, 'action'):
        if args.action == "create":
            dns.add(args.type, args.priority, args.name, args.content)
        elif args.action == "show":
            dns.show(args.search)
        elif args.action == "delete":
            dns.delete(args.name)
    else:
        logging.error('Unknown action. Use -h for more information')
