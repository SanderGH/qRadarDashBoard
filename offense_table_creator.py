import time
from requests import get, post
import json
from qpylib import qpylib

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


def get_entity(entity_endpoint, headers, query=None, method='GET'):
    try:
        response = qpylib.REST(method, entity_endpoint, headers=headers, params=query)
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

def GetAnalyticsRuleByID(id, rulesDict):
    rules = json.loads(rulesDict)
    for rule in rules:
        if id==rule['id']:
            return rule
    return None

def GetLocalDestinationAddressByID(Id, destDict):
    destAddresses = json.loads(destDict)
    for ldaItem in destAddresses:
        if Id == ldaItem['id']:
            return ldaItem
    return None

def GetSourceAddressByID(Id, srcDict):
    srcAddresses = json.loads(srcDict)
    for srcItem in srcAddresses:
        if Id == srcItem['id']:
            return srcItem
    return None


def GetObjByIDFromJson(Id, srcDict):
    for item in srcDict:
        if Id == item['id']:
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
#################################
##    #get '/api/analytics/rules'
##    analitic_rules = offense_item['rules']
##    rule_dict = {}
##    rule_list = []
##    for rule_item in analitic_rules:
##        rule_obj = get_entity_by_id(rule_item['id'], rules_endpoint, headers)
##        rule_dict['id'] = rule_obj['id']
##        rule_dict['name'] = rule_obj['name']
##        rule_list.append(rule_dict)
##    offense_dict['rules'] = rule_list
##
##    #get '/api/siem/source_addresses'
##    src_addr_list = []
##    for src_addr_id in offense_item['source_address_ids']:
##        src_addr_obj = get_entity_by_id(src_addr_id, src_addr_endpoint, headers)
##        src_addr_list.append(src_addr_obj['source_ip'])
##    offense_dict['source_addresses'] = src_addr_list
##
##    #get '/api/siem/source_addresses'
##    dst_addr_list = []
##    for dst_addr_id in offense_item['local_destination_address_ids']:
##        dst_addr_obj = get_entity_by_id(dst_addr_id, ld_addr_endpoint, headers)
##        dst_addr_list.append(dst_addr_obj['local_destination_ip'])
##    offense_dict['local_destination_addresses'] = dst_addr_list
#################################
    #get '/api/analytics/rules'

    rulesDict = get_entity(rules_endpoint, headers)
    destDict  = get_entity(ld_addr_endpoint, headers)
    srcDict   = get_entity(src_addr_endpoint, headers)


#######################################################

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
            #rule_obj = get_entity_by_id(rule_item['id'], rules_endpoint, headers)
            rule_obj = GetObjByIDFromJson(rule_item['id'], rulesDict)
            if rule_obj != None:
                rule_dict['id'] = rule_obj['id']
                rule_dict['name'] = rule_obj['name']
                rule_list.append(rule_dict)
        offense_dict['rules'] = rule_list

        #get '/api/siem/source_addresses'
        src_addr_list = []
        for src_addr_id in offense_item['source_address_ids']:
            #src_addr_obj = get_entity_by_id(src_addr_id, src_addr_endpoint, headers)
            src_addr_obj = GetObjByIDFromJson(src_addr_id, srcDict)
            src_addr_list.append(src_addr_obj['source_ip'])
        offense_dict['source_addresses'] = src_addr_list

        #get '/api/siem/source_addresses'
        dst_addr_list = []
        for dst_addr_id in offense_item['local_destination_address_ids']:
            #dst_addr_obj = get_entity_by_id(dst_addr_id, ld_addr_endpoint, headers)
            dst_addr_obj = GetObjByIDFromJson(dst_addr_id, destDict)
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
    search_id = 'd31d572f-f36f-4150-afbc-8b0a64be11f9'
    response=get_entity('/api/ariel/searches/' + search_id +'/results', headers=headers)
    return response.get('events')









