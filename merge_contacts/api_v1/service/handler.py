import json

from .bx24.requests import Bitrix24
from .report.report_to_html import Report
from .params import TYPE_MERGE_FIELD
from.field_contacts_merge.data_update import FieldsContactsUpdate

from api_v1.models import Email, Contacts, Companies


bx24 = Bitrix24()


# добавление контакта в БД
def contacts_create(res_from_bx, lock):
    for _, contacts in res_from_bx.items():
        for contact in contacts:
            emails = []
            if "EMAIL" in contact:
                emails = contact.pop("EMAIL")

            # замена пустых значений на None
            contact = replace_empty_value_with_none__in_dict(contact)

            # сохранение контакта
            lock.acquire()
            contact_item, created = Contacts.objects.update_or_create(**contact)
            lock.release()

            if emails:
                lock.acquire()
                email_create(emails, contact_item)
                lock.release()


# добавление EMAIL в БД
def email_create(emails, contact):
    for email in emails:
        # uniq_value = f"{email['VALUE']}{contact_name}" if email['VALUE'] and contact_name else None
        Email.objects.update_or_create(VALUE=email['VALUE'], VALUE_TYPE=email['VALUE_TYPE'], contacts=contact)


# добавление компаний в БД
def companies_create(res_from_bx, lock):
    for _, companies in res_from_bx.items():
        for company in companies:
            # сохранение компании
            lock.acquire()
            company_item, created = Companies.objects.update_or_create(**company)
            lock.release()


# связывание записей таблиц контактов и компаний в БД
def company_bind_contact(res_from_bx, lock):
    for id_company, contacts in res_from_bx.items():
        for contact in contacts:
            # сохранение компании
            lock.acquire()
            company_obj = Companies.objects.get(ID=id_company)
            contact_obj = Contacts.objects.get(ID=contact['CONTACT_ID'])
            res = company_obj.contacts.add(contact_obj)
            lock.release()


# замена пустых значений в словаре на None
def replace_empty_value_with_none__in_dict(d):
    for key in d:
        if not d[key]:
            d[key] = None

    return d


# объединение контактов с переданным списком идентификаторов
def merge_contacts(ids, lock, report):
    fields = get_fields_contact()

    # список контактов (возвращает словарь {<id_контакта>: <данные>})
    contacts = get_data_contacts(ids)
    if not contacts:
        return

    # объединение значений полей
    contacts_update = FieldsContactsUpdate(bx24, contacts)
    # ID последнего созданного контакта
    id_contact_last = contacts_update.get_id_max_date()
    # ID компании для добавления в последний созданный контакт
    companies = contacts_update.get_field_company_non_empty()

    data = {}
    for field, field_data in fields.items():
        if field_data['isReadOnly'] is True:
            continue
        elif field in TYPE_MERGE_FIELD['max_length']:
            data[field] = contacts_update.get_field_rule_max_length(field)
        elif field in TYPE_MERGE_FIELD['concat_asc_date']:
            data[field] = contacts_update.get_field_rule_concat_asc_date(field)
        elif field in TYPE_MERGE_FIELD['concat_desc_date']:
            data[field] = contacts_update.get_field_rule_concat_desc_date(field)
        elif field_data['type'] == 'crm_multifield':
            field_content = contacts_update.get_field_type_crm_multifield(field)
            if field_content:
                data[field] = field_content
        elif field_data['type'] == 'file':
            field_content = contacts_update.get_field_type_file(field)
            if field_content:
                data[field] = field_content
        else:
            field_content = contacts_update.get_field_non_empty(field)
            if field_content:
                data[field] = field_content

    # обновление контакта
    res_update_contact = update_data_contacts(id_contact_last, data)
    # добавление компаний к контакту
    res_add_companies = add_companies_to_contact(id_contact_last, companies)

    # print('res_update_contact = ', res_update_contact)
    # print('res_add_companies =  ', res_add_companies)
    if res_update_contact and res_add_companies:
        # добавление данных в отчет
        lock.acquire()
        report.add_fields(fields)
        report.add(contacts, id_contact_last, data, companies)
        lock.release()

        del_companies_to_contact(ids, id_contact_last)


# удаление контактов
def del_companies_to_contact(ids_contacts, id_contact_last):
    for id_contact in ids_contacts:
        if int(id_contact) in [id_contact_last, int(id_contact_last)]:
            continue

        res_del = bx24.call(
            'crm.contact.delete',
            {'id': id_contact}
        )


# добавляет компании к контакту
def add_companies_to_contact(id_contact, companies):
    print('companies = ', companies)
    if not companies:
        return True

    response = bx24.call(
        'crm.contact.company.items.set',
        {
            'id': id_contact,
            'items': [{'COMPANY_ID': company_id} for company_id in companies]
        }
    )

    if 'result' not in response:
        return

    return response['result']


# обновляет данные контакта
def update_data_contacts(id_contact, data):
    response = bx24.call(
        'crm.contact.update',
        {
            'id': id_contact,
            'fields': {
                **data,
            },
            'params': {"REGISTER_SONET_EVENT": "Y"}
        }
    )

    if 'result' not in response:
        return

    return response['result']


# запрашивает данные контактов по id
def get_data_contacts(ids):
    cmd = {}
    for id_contact in ids:
        cmd[id_contact] = f'crm.contact.get?id={id_contact}'

    response = bx24.batch(cmd)

    if 'result' not in response or 'result' not in response['result']:
        return

    return response['result']['result']


# запрашивает и возвращает список всех полей контакта
def get_fields_contact():
    response_fields = bx24.call('crm.contact.fields', {})
    if 'result' not in response_fields:
        return

    return response_fields['result']


# привязывает к сделке компанию полученную из первого связанного контакта - в Битрикс24
def add_company_in_deal(id_deal):
    response = bx24.batch(
        {
            'deal': f'crm.deal.get?id={id_deal}',
            'contacts': f'crm.deal.contact.items.get?id={id_deal}'
        }
    )

    if 'result' not in response or 'result' not in response['result']:
        # print('Ответ от биртикс не содержит поле "result"')
        return 400, 'Ответ от биртикс не содержит поле "result"'
    if 'deal' not in response['result']['result']:
        # print('Ответ от биртикс не содержит поле "deal"')
        return 400, 'Ответ от биртикс не содержит поле "deal"'
    if 'contacts' not in response['result']['result']:
        # print('Ответ от биртикс не содержит поле "contacts"')
        return 400, 'Ответ от биртикс не содержит поле "contacts"'

    deal = response['result']['result']['deal']
    contacts = response['result']['result']['contacts']
    company_id = deal.get('COMPANY_ID', None)

    if (company_id and company_id != '0') or not contacts:
        # print('В сделке присутствует связанная компания или отсутствуют контакты')
        return 200, 'В сделке присутствует связанная компания или отсутствуют контакты'

    contact_id = contacts[0].get('CONTACT_ID')

    # Получение данных контакта по его id
    response_contact = bx24.call(
        'crm.contact.get',
        {'id': contact_id}
    )

    if 'result' not in response_contact:
        # print('Ответ на запрос "crm.contact.get" не содержит поле "result"')
        return 400, 'Ответ на запрос "crm.contact.get" не содержит поле "result"'

    contact = response_contact['result']
    company_id = contact.get('COMPANY_ID', None)

    if not company_id:
        return 200, 'К контакту не привязана компания'

    response_deal_update = bx24.call(
        'crm.deal.update',
        {
            'id': id_deal,
            'fields': {
                'COMPANY_ID': company_id
            }
        }
    )

    return 200, 'Ok'

