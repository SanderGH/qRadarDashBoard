import time,datetime
from requests import get, post
import json
from qpylib import qpylib
from collections import Counter

def get_offenses():
    offenses_endpoint = '/api/siem/offenses'
    headers = {"Content-type": "application/json",
               "Accept"      : "application/json"}
    try:
        response = qpylib.REST('GET', offenses_endpoint, headers=headers)
        if response.status_code != 200:
            qpylib.log('API returned an error. Error: {0}'.format(response.content), level='error')
        return response.json()
    except Exception, e:
        qpylib.log('unable to retrieve offense records from QRadar. Error: {0}'.format(str(e)), level='error')


def get_entity(entity_endpoint, headers, query=None, method='GET', fields='', filter=''):
    try:
        full_request = str(entity_endpoint)
        is_fields = False
        if fields != '':
            full_request += '?fields=' + fields
            is_fields = True

        if filter != '':
            if is_fields:
                full_request += '&filter=' + filter
            else:
                full_request += '?filter=' + filter

        response = qpylib.REST(method, full_request, headers=headers, params=query)
        if response.status_code != 200:
            qpylib.log('API returned an error. Error: {0}'.format(response.content), level='error')
        return response.json()
    except Exception, e:
        qpylib.log('Unable to retrieve entity records from QRadar. Error: {0}'.format(str(e)), level='error')

def get_entity_by_id(id, entity_endpoint, headers):
    try:
        full_entity_endpoint = entity_endpoint + '/' +str(id)
        response = qpylib.REST('GET', full_entity_endpoint, headers=headers)
        if response.status_code != 200:
            qpylib.log('API returned an error. Error: {0}'.format(response.content), level='error')
        return response.json()
    except Exception, e:
        qpylib.log('Unable to retrieve entity records from QRadar. Error: {0}'.format(str(e)), level='error')

def get_object_by_field_from_json(key_field, relate_id, json_response):
    for item in json_response:
        if relate_id == item[key_field]:
            return item
    return None


def create_offense_table():
    offense_table = []
    headers = {"Content-type": "application/json",
               "Accept"      : "application/json"}

    rules_endpoint     = '/api/analytics/rules'
    offenses_endpoint  = '/api/siem/offenses'
    src_addr_endpoint  = '/api/siem/source_addresses'
    ld_addr_endpoint   = '/api/siem/local_destination_addresses'

    rules_dict    = get_entity(rules_endpoint, headers)
    ld_addr_dict  = get_entity(ld_addr_endpoint, headers)
    src_addr      = get_entity(src_addr_endpoint, headers)

    offenses = get_entity(offenses_endpoint, headers)
    for offense_item in  offenses:
        offense_dict  = {}

        offense_dict['id']                = offense_item['id']
        offense_dict['status']            = offense_item['status']
        offense_dict['severity']          = offense_item['severity']
        offense_dict['domain_id']         = offense_item['domain_id']
        offense_dict['start_time']        = offense_item['start_time']
        offense_dict['close_time']        = offense_item['close_time']
        offense_dict['assigned_to']       = offense_item['assigned_to']
        offense_dict['event_count']       = offense_item['event_count']
        offense_dict['closing_user']      = offense_item['closing_user']
        offense_dict['offense_source']    = offense_item['offense_source']
        offense_dict['last_updated_time'] = offense_item['last_updated_time']

        #get '/api/analytics/rules'
        analitic_rules = offense_item['rules']
        rule_dict = {}
        rule_list = []
        for rule_item in analitic_rules:
            rule_obj = get_object_by_field_from_json('id', rule_item['id'], rules_dict)
            if rule_obj != None:
                rule_dict['id'] = rule_obj['id']
                rule_dict['name'] = rule_obj['name']
                rule_list.append(rule_dict)
        offense_dict['rules'] = rule_list

        #get '/api/siem/source_addresses'
        src_addr_list = []
        for src_addr_id in offense_item['source_address_ids']:
            src_addr_obj = get_object_by_field_from_json('id', src_addr_id, src_addr)
            src_addr_list.append(src_addr_obj['source_ip'])
        offense_dict['source_addresses'] = src_addr_list

        #get '/api/siem/local_destination_addresses'
        dst_addr_list = []
        for dst_addr_id in offense_item['local_destination_address_ids']:
            dst_addr_obj = get_object_by_field_from_json('id', dst_addr_id, ld_addr_dict)
            dst_addr_list.append(dst_addr_obj['local_destination_ip'])
        offense_dict['local_destination_addresses'] = dst_addr_list

        #get notes
##        notes_endpoint = offenses_endpoint + '/' + str(offense_item['id']) + '/notes'
##        offense_notes_list = get_entity(notes_endpoint, headers)
##        note_list = []
##        for note_item in offense_notes_list:
##            note_list.append(note_item['note_text'])
        offense_dict['note'] = []

        offense_table.append(offense_dict)

    return json.dumps(offense_table)


def create_source_table():
    sources_table = []
    headers = {"Content-type": "application/json",
               "Accept"      : "application/json"}

    event_sources_endpoint  = '/api/config/event_sources/log_source_management/log_sources'
    event_sources = get_entity(event_sources_endpoint, headers)
    for source_item in event_sources:
        source_dict  = {}

        source_dict['name']            = source_item['name']
        source_dict['status']          = source_item['status']
        source_dict['average_eps']     = source_item['average_eps']
        source_dict['last_event_time'] = source_item['last_event_time']

        sources_table.append(source_dict)

    return json.dumps(sources_table)

def get_data_per_log_source(ls):
    data = dict()
    for bucket in ls:
        data[int(bucket.get('hour'))] = float(bucket.get('COUNT'))
    return data

def highchartify_data(events):
    series = []
    categories = []
    ls = dict()
    for event in events:
        if not event.get('hour') in categories:
            categories.append(event.get('hour'))
        if event.get('log') in ls:
            ls[event.get('log')].append(event)
        else:
            ls[event.get('log')] = [event]
    logsources = list(ls.keys())
    for logsource in logsources:
        dataDict = get_data_per_log_source(ls.get(logsource))
        data = [0] * 25
        i=0
        for cat in categories:
            if int(cat) in dataDict:
                data[i] = dataDict.get(int(cat))
            i = i+1
        series.append({'name':logsource, 'data':data})
    return series


def get_log_sources_data():
    headers = {"Content-type": "application/json",
               "Accept"      : "application/json",
               "Version"     : "7.0"}

    event_sources_endpoint  = '/api/ariel/searches'
##    query = {'query_expression':"select DATEFORMAT(starttime,'HH') as hour, LOGSOURCENAME(logsourceid) as log, count(*) from events group by hour, log order by hour last 24 hours"}
##    response = get_entity(event_sources_endpoint, headers, query, 'POST')
##    search_id = response['search_id']
##    error = False
##    while (response['status'] != 'COMPLETED') and not error:
##        if (response['status'] == 'EXECUTE') | (response['status'] == 'SORTING') | (response['status'] == 'WAIT'):
##            response=get_entity('/api/ariel/searches/' + search_id, headers=headers)
##        else:
##            error = True
##
##    response=get_entity('/api/ariel/searches/' + search_id +'/results', headers=headers)
    search_id = '05fd68f4-a769-4fc0-a515-90aec90fa0c3'
    response=get_entity('/api/ariel/searches/' + search_id +'/results', headers=headers)
    return response.get('events')

def group_by_severity(offense_type, key_field):
    severity = {}
    severity_counter = Counter()
    severity_hours = {}
    for item in offense_type:
        severity_counter[item['severity']] += 1
        #decoded_time = datetime.datetime.utcfromtimestamp(item['start_time']/1000)
        decoded_time = datetime.datetime.utcfromtimestamp(item[key_field]/1000)
        if severity_hours.has_key(item['severity']) is not True:
            severity_hours[item['severity']] = [0] * 25
        severity_hours[item['severity']][decoded_time.hour] += 1

    for item in offense_type:
        severity_data = {}
        severity_data['count'] = severity_counter[item['severity']]
        severity_data['hours'] = severity_hours[item['severity']]
        severity[item['severity']] = severity_data
    return severity


def get_registered_offenses():
    fields = 'severity,assigned_to,start_time,close_time'
    headers = {"Content-type": "application/json",
               "Accept"      : "application/json"}

    yesterday =  datetime.datetime.now() - datetime.timedelta(hours=480)
    start_time = int(time.mktime(yesterday.timetuple()))
    filter = 'assigned_to is null and close_time is null and start_time >=' + str(start_time*1000)

    offenses_endpoint  = '/api/siem/offenses'
    registered_offenses = get_entity(offenses_endpoint, headers, None, fields=fields,filter=filter)

    return group_by_severity(registered_offenses, 'start_time')

def get_closed_offenses():
    fields = 'severity,assigned_to,start_time,close_time'
    headers = {"Content-type": "application/json",
               "Accept"      : "application/json"}

    yesterday =  datetime.datetime.now() - datetime.timedelta(hours=480)
    start_time = int(time.mktime(yesterday.timetuple()))
    filter = 'assigned_to is not null and close_time is not null'

    offenses_endpoint  = '/api/siem/offenses'
    closed_offenses = get_entity(offenses_endpoint, headers, None, fields=fields,filter=filter)

    return group_by_severity(closed_offenses, 'close_time')

def make_series_for_registered_offenses():
    all_offenses = {}
    all_offenses['registered'] = get_registered_offenses()
    all_offenses['closed']     = get_closed_offenses()

    return json.dumps(all_offenses)







