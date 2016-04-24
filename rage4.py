#!/bin/python3

import argparse
import configparser
import json
import logging
import requests
from tabulate import tabulate

config = configparser.ConfigParser()
config.read('config.ini')

EMAIL = config['rage4']['username']
API_TOKEN = config['rage4']['api_token']

BASE_URL = 'https://rage4.com/rapi/'


def api(endpoint, payload=''):
    logging.debug('Sending payload: {}'.format(payload))
    try:
        r = requests.get(BASE_URL + endpoint, auth=(EMAIL, API_TOKEN),
                         params=payload)
    except requests.ConnectionError as e:
        logging.error('Received Connection Error: {}'.format(e))
        raise

    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        logging.error('Receieved HTTP Error: {}'.format(e))
        raise
    logging.debug(r.json())
    logging.debug('Status Code: {}'.format(r.status_code))
    return r.json()


def getdomains():
    return api('getdomains/')


def listrecords():
    for id in getdomains():
        payload = {}
        payload = {'id': id['id'], 'name': id['name']}
        return api('getrecords/', payload)


def getrecordsbytype(type):
    table = []
    for record in listrecords():
        if type != 'all' and record['type'] == type:
            table.append([record['name'], record['content']])
        elif type == 'all':
            table.append([record['name'], record['content']])
    print(tabulate(table))


def createrecord(name, content, type, priority):
    #TODO: Check if record already exists
    payload = {}
    id = getdomains()
    id = id[0]
    payload = {
                'id': id['id'],
                'name': name,
                'content': content,
                'type': type,
                'priority': priority
              }
    api('createrecord/', payload)
    logging.info('Created record: {} {} {}'.format(name, type, content))


def deleterecord(name):
    id = []
    for entry in listrecords():
        if entry['name'] == name:
            id.append(entry['id'])
    if id:
        for id in id:
            payload = {
                        'id': id
                      }
            api('deleterecord/', payload)
            logging.info('Deleted record: {}'.format(id))
    else:
        logging.error('Unable to find entry {}'.format(name))

def updaterecord(name, content):
    #TODO: Make this real
    logging.info("This method is not implemented yet")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Play with the Rage4 API')
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='Enable debug messages')
    subparser = parser.add_subparsers()

    parser_create = subparser.add_parser('create',
                                         help='Create an new record')
    parser_create.add_argument('name', type=str)
    parser_create.add_argument('content', type=str)
    parser_create.add_argument('type', type=str)
    parser_create.add_argument('priority', type=int, default=1)
    parser_create.set_defaults(action='create')

    parser_show = subparser.add_parser('show',
                                       help='Show record by type')
    parser_show.add_argument('type', type=str)
    parser_show.set_defaults(action='show')

    parser_delete = subparser.add_parser('delete',
                                         help='Delete record by name')
    parser_delete.add_argument('name', type=str)
    parser_delete.set_defaults(action='delete')

    parser_show = subparser.add_parser('update',
                                       help='Update record')
    parser_show.add_argument('name', type=str)
    parser_show.add_argument('content', type=str)
    parser_show.set_defaults(action='update')

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')

    if hasattr(args, 'action'):
        if args.action == "create":
            createrecord(args.name, args.content, args.type, args.priority)
        elif args.action == "show":
            getrecordsbytype(args.type)
        elif args.action == "delete":
            deleterecord(args.name)
        elif args.action == "update":
            updaterecord(args.name)
    else:
        logging.error('Unknown action. Use -h for more information')
