import json
import os
import time
import re
import logging
from pprint import pprint


from requests import adapters, post, exceptions, get as http_get
from urllib.parse import unquote
from mimetypes import guess_extension as extension
from django.conf import settings


adapters.DEFAULT_RETRIES = 10
BX24__COUNT_METHODS_IN_BATH = 10
BX24__COUNT_RECORDS_IN_METHODS = 25


class Bitrix24:
    api_url = 'https://{domain}/rest/{method}.json'
    oauth_url = 'https://oauth.bitrix.info/oauth/token/'
    timeout = 60

    def __init__(self):
        self.length_batch = BX24__COUNT_METHODS_IN_BATH
        self.domain = None
        self.auth_token = None
        self.refresh_token = None
        self.client_id = None
        self.client_secret = None
        self.expires_in = None
        self.init_tokens()

    def init_tokens(self):
        self.domain = "bits24.bitrix24.ru"
        self.auth_token = "27188a63005f01e40054d652000000094038074b268e984bbc1887a29ad1936badc387"
        self.refresh_token = "1797b163005f01e40054d65200000009403807acc21e6a359117b888f51a116a9a6f64"
        self.client_id = "local.636b7e50680e85.54510656"
        self.client_secret = "GbLhCYkKRSIM0iwUcKR9lzZ1iM8lWVESIroMYJXFGABv30OJJl"
        self.expires_in = 3600

    def refresh_tokens(self):
        r = {}
        try:
            r = post(
                self.oauth_url,
                params={'grant_type': 'refresh_token', 'client_id': self.client_id, 'client_secret': self.client_secret,
                        'refresh_token': self.refresh_token})
            result = json.loads(r.text)

            self.auth_token = result['access_token']
            self.refresh_token = result['refresh_token']
            self.expires_in = result['expires_in']
            return True
        except (ValueError, KeyError):
            result = dict(error='Error on decode oauth response [%s]' % r.text)
            return result

    def call(self, method, data):
        # if not self.domain or self.auth_token:
        #     self.init_tokens()

        try:
            url = self.api_url.format(domain=self.domain, method=method)
            params = dict(auth=self.auth_token)
            headers = {
                'Content-Type': 'application/json',
            }
            r = post(url, data=json.dumps(data), params=params, headers=headers, timeout=self.timeout)
            result = json.loads(r.text)
        except ValueError:
            result = dict(error=f'Error on decode api response [{r.text}]')
        except exceptions.ReadTimeout:
            result = dict(error=f'Timeout waiting expired [{str(self.timeout)} sec]')
        except exceptions.ConnectionError:
            result = dict(error=f'Max retries exceeded [{str(adapters.DEFAULT_RETRIES)}]')

        if 'error' in result and result['error'] in ('NO_AUTH_FOUND', 'expired_token'):
            result_update_token = self.refresh_tokens()
            if result_update_token is not True:
                return result
            result = self.call(method, data)

        elif 'error' in result and result['error'] in ['QUERY_LIMIT_EXCEEDED', ]:
            print(result)
            time.sleep(2)
            return self.call(method, data)

        return result

    def batch(self, cmd):
        if not cmd or not isinstance(cmd, dict):
            return dict(error='Invalid batch structure')

        return self.call(
            'batch',
            {
                "halt": 0,
                "cmd": cmd
            }
        )

    # возвращает количество объектов для заданного списочного метода
    def get_count_records(self, method, filters={}):
        data = {}
        if filters:
            data["filter"] = filters

        response = self.call(method, data)
        if response and 'total' in response:
            return response['total']

    # формирование команд для batch запросов
    @staticmethod
    def forming_long_batch_commands(method, total_contacts, fields=[], filters={}):
        cmd = {}
        for i in range(0, total_contacts, BX24__COUNT_RECORDS_IN_METHODS):
            cmd[f'key_{i}'] = f'{method}?start={i}&'
            # for field in fields:
            #     cmd[f'key_{i}'] += f'&select[]={field}'
            cmd[f'key_{i}'] += '&'.join([f'select[]={field}' for field in fields])
            if filters:
                cmd[f'key_{i}'] += '&'
                cmd[f'key_{i}'] += '&'.join([f'FILTER[{key}]={val}' for key, val in filters.items()])

        return cmd

    # разбивка команд на группы по определенной длине
    def split_long_batch_commands(self, commands):
        count = 0
        cmd = {}
        cmd_list = []
        for key in commands:
            count += 1
            cmd[key] = commands[key]
            if count == self.length_batch:
                cmd_list.append(cmd)
                count = 0
                cmd = {}

        if cmd:
            cmd_list.append(cmd)

        return cmd_list

    # объединение результатов запроса
    @staticmethod
    def merge_long_batch_result(keys, data):
        res = []
        for key in keys:
            res.extend(data.get(key, []))

        return res

    def long_batch(self, method):
        result_batch = []
        # всего записей
        total_contacts = self.get_count_records(method)
        # словарь команд для извлечения всех данных
        commands = self.forming_long_batch_commands(method, total_contacts)
        # список команд для выполнения batch запросов
        cmd_list = self.split_long_batch_commands(commands)
        # выполнение запросов
        for cmd in cmd_list:
            response = self.batch(cmd)
            if 'result' not in response or 'result' not in response['result']:
                continue
            result_batch.extend(self.merge_long_batch_result(cmd.keys(), response['result']['result']))

        return result_batch

    def download_file(self, url_path, fileid, recursion=5):
        recursion -= 1
        try:
            url = f'https://{self.domain}{url_path}'
            params = {
                'auth': self.auth_token
            }

            result = http_get(url, params)

        except exceptions.ReadTimeout:
            result = dict(error=f'Timeout waiting expired [{str(self.timeout)} sec]')
        except exceptions.ConnectionError:
            result = dict(error=f'Max retries exceeded [{str(adapters.DEFAULT_RETRIES)}]')

        if 'error' in result or 'X-Bitrix-Ajax-Status' in result.headers:
            result_update_token = self.refresh_tokens()
            if result_update_token is not True:
                return
            if recursion > 0:
                return self.download_file(url_path, fileid, recursion)
        else:
            f_name = self.get_filename(result.headers, fileid)
            f_path = os.path.join(settings.BASE_DIR, 'files', f_name)
            with open(f_path, 'wb') as f:
                f.write(result.content)

            return f_path

    def get_filename(self, headers, fileid):
        data = headers.get('Content-Disposition')

        if data:
            filename = re.search(r'filename="(.+)";', data).group(1)
            return unquote(filename)
        else:
            content_type = headers.get("Content-Type")

            if content_type and extension(content_type):
                filename = fileid + extension(content_type)
                return unquote(filename)
            else:
                return unquote(fileid)


bx = Bitrix24()
# res = bx.call("crm.activity.list", {})
# pprint(res)
def handler():
    for _ in range(450):
        # res = bx.call("crm.deal.list", {})
        res = bx.batch({
            "1": 'crm.deal.list?select[]=ID&select[]=TITLE',
            "2": 'crm.deal.list?select[]=ID&select[]=TITLE',
            "3": 'crm.deal.list?select[]=ID&select[]=TITLE',
            "4": 'crm.deal.list?select[]=ID&select[]=TITLE',
            "5": 'crm.deal.list?select[]=ID&select[]=TITLE',
            "6": 'crm.deal.list?select[]=ID&select[]=TITLE',
            "7": 'crm.deal.list?select[]=ID&select[]=TITLE',
            "8": 'crm.deal.list?select[]=ID&select[]=TITLE',
            "9": 'crm.deal.list?select[]=ID&select[]=TITLE',
            "10": 'crm.deal.list?select[]=ID&select[]=TITLE',
            "11": 'crm.deal.list?select[]=ID&select[]=TITLE',
        })
        pprint(res.get("time", {}))


# from threading import Thread, Lock
# bx = Bitrix24()
# N = 100
# lst = []
# for _ in range(N):
#     lst.append(Thread(target=handler))
#
# for trd in lst:
#     trd.start()
#
# for trd in lst:
#     trd.join()


COUNT_METHODS_IN_BATCH = 1
def copy_comments(origin_contact, contacts):
    cmd = {}
    # method_timeline_comment = "crm.activity.list?select[]=ID&contact={contact}"
    method_timeline_comment = "crm.timeline.comment.list?filter[ENTITY_TYPE]=contact&filter[ENTITY_ID]={contact}"
    for ind, contact in enumerate(contacts):
        if contact == origin_contact:
            continue
        cmd[contact] = method_timeline_comment.format(contact=contact)

    response = bx.batch(cmd)
    if "result" not in response or "result" not in response["result"] or "result_total" not in response["result"]:
        return

    contacts_comments = response["result"]["result"]
    contacts_total = response["result"]["result_total"]
    contacts_next = response["result"]["result_next"]

    if contacts_next and contacts_total:
        cmd = {}
        for contact, start in contacts_next.items():
            count_records = 50
            count = contacts_total[contact]
            for i in range(count // count_records):
                method = method_timeline_comment.format(contact=contact)
                method += f"&start={start + i * count_records}"
                cmd[f"{contact}_{i}"] = method

        i = 1
        cmd_list = []
        cmd_block = {}
        for key, val in cmd.items():
            if i > COUNT_METHODS_IN_BATCH:
                cmd_list.append(cmd_block)
                cmd_block = {}
                i = 1
            cmd_block[key] = val
            i += 1
        else:
            if cmd_block:
                cmd_list.append(cmd_block)

        for cmd in cmd_list:
            response = bx.batch(cmd)
            if "result" not in response or "result" not in response["result"]:
                return
            for key, val in response["result"]["result"].items():
                contact, _ = key.split("_")
                contacts_comments[contact].extend(val)

    comments_list = [comment for contact, comments in contacts_comments.items() for comment in comments]

    cmd = {}
    method_timeline_comment_add = "crm.timeline.comment.add?fields[AUTHOR_ID]={AUTHOR_ID}&" \
                                  "fields[COMMENT]={COMMENT}&" \
                                  "fields[CREATED]={CREATED}&" \
                                  "fields[ENTITY_ID]={ENTITY_ID}&" \
                                  "fields[ENTITY_TYPE]={ENTITY_TYPE}"
    for comment in comments_list:
        key = comment["ID"]
        comment["ENTITY_ID"] = origin_contact
        cmd[key] = method_timeline_comment_add.format(**comment)

    i = 1
    cmd_list = []
    cmd_block = {}
    for key, val in cmd.items():
        if i > COUNT_METHODS_IN_BATCH:
            cmd_list.append(cmd_block)
            cmd_block = {}
            i = 1
        cmd_block[key] = val
        i += 1
    else:
        if cmd_block:
            cmd_list.append(cmd_block)

    for cmd in cmd_list:
        response = bx.batch(cmd)
        if "result" not in response or "result" not in response["result"]:
            return


def copy_activities(origin_contact, contacts):
    cmd = {}
    method_activity_list = "crm.activity.list?filter[OWNER_TYPE_ID]=3&filter[OWNER_ID]={contact}&select[]=ID"
    for ind, contact in enumerate(contacts):
        if contact == origin_contact:
            continue
        cmd[contact] = method_activity_list.format(contact=contact)

    response = bx.batch(cmd)
    if "result" not in response or "result" not in response["result"] or "result_total" not in response["result"]:
        return

    activities = response["result"]["result"]
    totals = response["result"]["result_total"]
    nexts = response["result"]["result_next"]

    if nexts and totals:
        cmd = {}
        for contact, start in nexts.items():
            count_records = 50
            count = totals[contact]
            for i in range(count // count_records):
                method = method_activity_list.format(contact=contact)
                method += f"&start={start + i * count_records}"
                cmd[f"{contact}_{i}"] = method

        i = 1
        cmd_list = []
        cmd_block = {}
        for key, val in cmd.items():
            if i > COUNT_METHODS_IN_BATCH:
                cmd_list.append(cmd_block)
                cmd_block = {}
                i = 1
            cmd_block[key] = val
            i += 1
        else:
            if cmd_block:
                cmd_list.append(cmd_block)

        for cmd in cmd_list:
            response = bx.batch(cmd)
            if "result" not in response or "result" not in response["result"]:
                return
            for key, val in response["result"]["result"].items():
                contact, _ = key.split("_")
                activities[contact].extend(val)

    activities_list = [comment for contact, comments in activities.items() for comment in comments]

    cmd = {}
    method_activity_add = "crm.activity.binding.add?activityId={activity}&" \
                          "entityTypeId=3&" \
                          "entityId={origin_contact}"
    for activity in activities_list:
        key = activity["ID"]
        cmd[key] = method_activity_add.format(activity=activity["ID"], origin_contact=origin_contact)
    pprint(cmd)
    i = 1
    cmd_list = []
    cmd_block = {}
    for key, val in cmd.items():
        if i > COUNT_METHODS_IN_BATCH:
            cmd_list.append(cmd_block)
            cmd_block = {}
            i = 1
        cmd_block[key] = val
        i += 1
    else:
        if cmd_block:
            cmd_list.append(cmd_block)

    for cmd in cmd_list:
        response = bx.batch(cmd)
        if "result" not in response or "result" not in response["result"]:
            return
        pprint(response)




copy_activities(223, [223, 225, 235])
copy_comments(223, [223, 225, 235])
# crm.activity.binding.add({activityId: number, entityTypeId: number, entityId: number)
# res = bx.call("crm.timeline.note.get", {
#     "ownerTypeId": 3,
#     "ownerId": 223,
#     "itemType": 2,
#     "itemId": 1701
# })
# res = bx.call("crm.activity.list", {"order": { "ID": "DESC" }, "select": ["ID"]})
# res = bx.call("crm.activity.get", {"ID": 1701})
# pprint(res)
# copy_timeline_comment(223, [223, 225, 235])

# filter[OWNER_TYPE_ID]=3&filter[OWNER_ID]=3&select[]=ID
    # "crm.activity.list",
    # {
    #     order: {"ID": "DESC"},
    #     filter:
    #         {
    #             "OWNER_TYPE_ID": 3,
    #             "OWNER_ID": 102
    #         },
    #     select: ["*", "COMMUNICATIONS"]
    # },
    # "crm.activity.list",
    # {
    #     order: {"ID": "DESC"},
    #     filter:
    #         {
    #             "OWNER_TYPE_ID": 3,
    #             "OWNER_ID": 102
    #         },
    #     select: ["*", "COMMUNICATIONS"]
    # },
    # OWNER_TYPE_ID - это
    # {"ID": 1, "NAME": "Лид"},
    # {"ID": 2, "NAME": "Сделка"},
    # {"ID": 3, "NAME": "Контакт"},
    # {"ID": 4, "NAME": "Компания"},
    # {"ID": 7, "NAME": "Предложение"},
    # {"ID": 5, "NAME": "Счёт"},
    # {"ID": 8, "NAME": "Реквизиты"}
    # OWNER_ID - это соответсnвенно ID сущности.
    # crm.activity.binding.add({activityId: number, entityTypeId: number, entityId: number)
