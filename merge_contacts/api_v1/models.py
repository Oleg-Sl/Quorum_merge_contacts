from django.db import models


class Contacts(models.Model):
    ID = models.PositiveIntegerField(primary_key=True, verbose_name='Идентификатор контакта', unique=True, db_index=True)
    NAME = models.CharField(verbose_name="Имя", max_length=100, blank=True, null=True, db_index=True)

    def __str__(self):
        return f"{self.ID}"

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'


class Email(models.Model):
    VALUE = models.CharField(verbose_name="Адрес электронной почты", max_length=100, blank=True, null=True, db_index=True)
    VALUE_TYPE = models.CharField(verbose_name="Тип электронной почты", max_length=100, blank=True, null=True)
    # uniq_value = models.CharField(verbose_name="Поле по которому идет поиск дублей", max_length=200, blank=True, null=True)
    contacts = models.ForeignKey(Contacts, verbose_name='Контакт', on_delete=models.CASCADE, related_name='EMAIL',
                                 blank=True, null=True, db_index=True)

    def __str__(self):
        return f"{self.VALUE}"

    class Meta:
        verbose_name = 'Email'
        verbose_name_plural = 'Emails'


class Companies(models.Model):
    ID = models.PositiveIntegerField(primary_key=True, verbose_name='Идентификатор компании', unique=True,
                                     db_index=True)
    TITLE = models.CharField(verbose_name="Название", max_length=1000, blank=True, null=True, db_index=True)
    contacts = models.ManyToManyField(Contacts, db_index=True)

    def __str__(self):
        return f"{self.ID}. {self.TITLE}"

    class Meta:
        verbose_name = 'Компания'
        verbose_name_plural = 'Компания'






















# EMAIL - Адрес электронной почты
# IM - Мессенджеры
# PHONE - Телефон контакта
# WEB - URL ресурсов контакта


# class Email(models.Model):
#     VALUE = models.CharField(verbose_name="Адрес электронной почты", max_length=100, blank=True, null=True)
#     VALUE_TYPE = models.CharField(verbose_name="Тип электронной почты", max_length=100, blank=True, null=True)
#
#     def __str__(self):
#         return f"{self.VALUE}"
#
#     class Meta:
#         verbose_name = 'Email'
#         verbose_name_plural = 'Emails'


# from api_v1.models import Email, Contacts, Companies
# c1, s1 = Contacts.objects.update_or_create(ID=1, NAME="Company_1")
# c4, s4 = Contacts.objects.update_or_create(ID=4, NAME="Company_4")
# Email.objects.create(VALUE="qwe@mail.ru", contacts=c1)
# Email.objects.create(VALUE="123@mail.ru", contacts=c1)
# Email.objects.create(VALUE="999@mail.ru", contacts=c1)
# d1, ss1 = Companies.objects.update_or_create(ID=11, TITLE="CCCCCCC")
# c1.contacts_set.add(ID=11, TITLE="CCCCCCC")
# Contacts.objects.all()
# Email.objects.all()
# Companies.objects.all()
# Contacts.objects.all().delete()
# Email.objects.all().delete()
# d1.contacts.add(c1)
# d1.contacts.add(c4)
# [d for d in Contacts.objects.all()]
# [d for d in Companies.objects.all()]

# Добавление
# contact_1, created = Contacts.objects.update_or_create(ID=1, NAME="Contact_1")
# Email.objects.create(VALUE="qwe@mail.ru", contacts=contact_1)
# company_1, created = Companies.objects.update_or_create(ID=1, TITLE="Company_1")
# company_1.contacts.add(contact_1)
# 133.contacts.add(99)
#

# Очистка таблицы
# Contacts.objects.all().delete()
# Companies.objects.all().delete()



# # ДУБЛИКАТЫ: ИМЯ + EMAIL
# dup = Contacts.objects.annotate(
#     res=models.functions.Concat(
#         'EMAIL__VALUE_TYPE', 'NAME',
#         output_field=models.CharField()
#     )
# ).values('res').annotate(tt=models.Count('res')).filter(tt__gte=2).values_list('res', flat=True)
#
# d = Contacts.objects.annotate(
#     res=models.functions.Concat(
#         'EMAIL__VALUE_TYPE', 'NAME',
#         output_field=models.CharField()
#     )
# ).filter(res__in=dup).values_list('ID', flat=True)


# # ДУБЛИКАТЫ: КОМПАНИЯ + EMAIL
# dup = Contacts.objects.filter(companies__isnull=False).annotate(
#     res=models.functions.Concat(
#         'EMAIL__VALUE_TYPE', 'companies__TITLE',
#         output_field=models.CharField()
#     ),
#     # filter=models.Q(companies__isnull=False)
# ).values('res').annotate(tt=models.Count('res')).filter(tt__gte=2).values_list('res', flat=True)
#
# d = Contacts.objects.filter(companies__isnull=False).annotate(
#     res=models.functions.Concat(
#         'EMAIL__VALUE_TYPE', 'companies__TITLE',
#         output_field=models.CharField()
#     )
# ).filter(res__in=dup).values_list('ID', flat=True)



# d = Contacts.objects.annotate(
#     res=models.functions.Concat(
#         'EMAIL__VALUE_TYPE', 'NAME',
#         output_field=models.CharField()
#     )
# ).filter(res__in=dup).values('res').annotate(qwe=models.F('pk'))
#
# d = Contacts.objects.annotate(
#     res=models.functions.Concat(
#         'EMAIL__VALUE_TYPE', 'NAME',
#         output_field=models.CharField()
#     )
# ).filter(
#     res='WORKПавел'
# )
# Contacts.objects.annotate(
#     res=models.functions.Concat(
#         'EMAIL__VALUE_TYPE', 'NAME',
#         output_field=models.CharField()
#     )
# ).filter(res='WORKАлексей').values_list('ID', flat=True)

