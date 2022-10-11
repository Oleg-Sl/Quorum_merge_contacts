import time
from pprint import pprint


from .bx24.requests import Bitrix24
from .params import COUNT_THREAD
from .duplicates.search import get_duplicate_value
from .bx24.queues import MyQueue, QueueCommands, QueueByModels
from .bx24.multithreads_requests import (
    ArrayThreadsGetContacts,
    ArrayThreadsBatchGetCompanies,
    ArrayThreadsBatchGetCompanyBindContact,
    ArrayThreadsMergeContact
)
from .report.report_to_html import Report
from api_v1.models import Email, Contacts, Companies


bx24 = Bitrix24()

contacts_queue = None
companies_queue = None
company_contact_queue = None
duplicates_queue = None


def merge_contacts(method_merge):
    global contacts_queue
    global companies_queue
    global company_contact_queue
    global duplicates_queue
    report = Report()
    point_1 = time.time()

    # создание отчета
    # lock.acquire()
    report.create()
    # lock.release()

    # Очистка таблиц БД
    clear_database()

    # Список названий полей таблиц БД
    fields_contact = [contact.name for contact in Contacts._meta.get_fields()]
    fields_company = [company.name for company in Companies._meta.get_fields()]

    # Очереди
    contacts_queue = QueueCommands('crm.contact.list', bx24, COUNT_THREAD)
    companies_queue = QueueCommands('crm.company.list', bx24, COUNT_THREAD)
    company_contact_queue = QueueByModels(bx24, COUNT_THREAD)
    duplicates_queue = MyQueue(COUNT_THREAD)

    # Создание объектов для конкурентного общения с Битрикс24 по HTTP
    threads_contacts = ArrayThreadsGetContacts(contacts_queue, bx24, COUNT_THREAD)
    threads_companies = ArrayThreadsBatchGetCompanies(companies_queue, bx24, COUNT_THREAD)
    threads_company_contact = ArrayThreadsBatchGetCompanyBindContact(company_contact_queue, bx24, COUNT_THREAD)
    threads_duplicates = ArrayThreadsMergeContact(duplicates_queue, bx24, COUNT_THREAD, method_merge, report)

    # Создание потоков
    threads_contacts.create()
    threads_companies.create()
    threads_company_contact.create()
    threads_duplicates.create()

    # Запуск потоков
    threads_contacts.start()
    threads_companies.start()
    threads_company_contact.start()
    threads_duplicates.start()

    # Формирование очереди запросов и ожидание завершения получения данных - КОНТАКТЫ
    contacts_queue.forming(fields_contact)
    threads_contacts.join()
    point_2 = time.time()
    # print("Контакты получены")

    # Заполнение очереди запросов и ожидание завершения получения данных - КОМПАНИИ
    companies_queue.forming(fields_company)
    threads_companies.join()
    point_3 = time.time()
    # print("Компании получены")

    # Получение данных отношения компания-контакт из Битрикс
    company_contact_queue.forming(Companies)
    threads_company_contact.join()
    point_4 = time.time()
    # print("Связи контакт-компания получены")

    # формирование списка дублирующихся значений полей
    duplicates = get_duplicate_value(method_merge)
    point_5 = time.time()
    pprint(duplicates)

    # Заполнение очереди дубликатов контактов
    duplicates_queue.set_start_size(len(duplicates))
    [duplicates_queue.send_queue(id_contact) for id_contact in duplicates]
    duplicates_queue.send_queue_stop()
    point_6 = time.time()

    threads_duplicates.join()
    point_7 = time.time()

    # закрытие отчета
    report.closed()

    time.sleep(2)

    # print('point_2 = ', point_2 - point_1)
    # print('point_3 = ', point_3 - point_1)
    # print('point_4 = ', point_4 - point_1)
    # print('point_5 = ', point_5 - point_1)
    # print('point_6 = ', point_6 - point_1)
    # print('point_7 = ', point_7 - point_1)
    print("END!!!")


def clear_database():
    Email.objects.all().delete()
    Contacts.objects.all().delete()
    Companies.objects.all().delete()

