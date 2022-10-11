from django.db import models


from ..params import DUPLICATES_FIELDS
from api_v1.models import Email, Contacts, Companies


# get duplicate values
def get_duplicate_value(method_merge):
    if method_merge == "email_company":
        return get_duplicates_by_email_and_company()
    elif method_merge == "email_contact_name":
        return get_duplicates_by_email_and_name_contact()


# ДУБЛИКАТЫ: ИМЯ + EMAIL
def get_duplicates_by_email_and_name_contact():
    duplicates = Contacts.objects.filter(EMAIL__isnull=False, NAME__isnull=False).annotate(
        res=models.functions.Concat(
            *DUPLICATES_FIELDS['email_contact_name'],
            output_field=models.CharField()
        )
    ).values('res').annotate(tt=models.Count('res')).filter(tt__gte=2).values_list('res', flat=True)

    return duplicates


# ДУБЛИКАТЫ: КОМПАНИЯ + EMAIL
def get_duplicates_by_email_and_company():
    duplicates = Contacts.objects.filter(EMAIL__isnull=False, companies__isnull=False).annotate(
        res=models.functions.Concat(
            *DUPLICATES_FIELDS['email_company'],
            output_field=models.CharField()
        )
    ).values('res').annotate(tt=models.Count('res')).filter(tt__gte=2).values_list('res', flat=True)

    return duplicates


def get_id_duplicate_by_str(value, method_merge):
    ids = None
    if method_merge == "email_company":
        ids = Contacts.objects.annotate(
            res=models.functions.Concat(
                *DUPLICATES_FIELDS['email_company'],
                output_field=models.CharField()
            )
        ).filter(res=value).values_list('ID', flat=True)
    elif method_merge == "email_contact_name":
        ids = Contacts.objects.annotate(
            res=models.functions.Concat(
                *DUPLICATES_FIELDS['email_contact_name'],
                output_field=models.CharField()
            )
        ).filter(res=value).values_list('ID', flat=True)

    return ids

















# duplicates = Contacts.objects.values('EMAIL__uniq_value').annotate(
#     total=models.Count('EMAIL__uniq_value')
# ).filter(
#     total__gte=2
# ).values_list('EMAIL__uniq_value', flat=True)
# duplicates = Email.objects.values('uniq_value').annotate(
#     total=models.Count('uniq_value')
# ).filter(
#     total__gte=2
# ).values_list('uniq_value', flat=True)


# def get_id_duplicate_by_str(value, method_merge):
#     ids = None
#     if method_merge == "email_company":
#         ids = Contacts.objects.annotate(
#             res=models.functions.Concat(
#                 *DUPLICATES_FIELDS['email_company'],
#                 # 'EMAIL__VALUE_TYPE', 'companies__TITLE',
#                 output_field=models.CharField()
#             )
#         ).filter(res=value).values_list('ID', flat=True)
#     elif method_merge == "email_contact_name":
#         ids = Contacts.objects.filter(EMAIL__uniq_value=value).values_list('ID', flat=True)
#
#     return ids



# duplicates_ids = Contacts.objects.annotate(
#     res=models.functions.Concat(
#         *DUPLICATES_FIELDS['email_contact_name'],
#         # 'EMAIL__VALUE_TYPE', 'NAME',
#         output_field=models.CharField()
#     )
# ).filter(res__in=duplicates).values_list('ID', flat=True)
# pprint(duplicates_ids)

# duplicates_ids = Contacts.objects.filter(companies__isnull=False).annotate(
#     res=models.functions.Concat(
#         *DUPLICATES_FIELDS['email_company'],
#         # 'EMAIL__VALUE_TYPE', 'companies__TITLE',
#         output_field=models.CharField()
#     )
# ).filter(res__in=duplicates).values_list('ID', flat=True)

