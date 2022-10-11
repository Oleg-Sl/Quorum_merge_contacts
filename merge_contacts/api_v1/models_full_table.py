# from django.db import models
#
# # Create your models here.
#
# # EMAIL - Адрес электронной почты
# # IM - Мессенджеры
# # PHONE - Телефон контакта
# # WEB - URL ресурсов контакта
#
#
# # class Email(models.Model):
# #     VALUE = models.CharField(verbose_name="Адрес электронной почты", max_length=100, blank=True, null=True)
# #     VALUE_TYPE = models.CharField(verbose_name="Тип электронной почты", max_length=100, blank=True, null=True)
# #
# #     def __str__(self):
# #         return f"{self.VALUE}"
# #
# #     class Meta:
# #         verbose_name = 'Email'
# #         verbose_name_plural = 'Emails'
# #
# #
# # class Im(models.Model):
# #     VALUE = models.CharField(verbose_name="Мессенджеры", max_length=100, blank=True, null=True)
# #     VALUE_TYPE = models.CharField(verbose_name="Тип мессенджера", max_length=100, blank=True, null=True)
# #
# #     def __str__(self):
# #         return f"{self.VALUE}"
# #
# #     class Meta:
# #         verbose_name = 'Im'
# #         verbose_name_plural = 'Ims'
# #
# #
# # class Phone(models.Model):
# #     VALUE = models.CharField(verbose_name="Телефон контакта", max_length=50, blank=True, null=True)
# #     VALUE_TYPE = models.CharField(verbose_name="Тип телефона", max_length=50, blank=True, null=True)
# #
# #     def __str__(self):
# #         return f"{self.VALUE}"
# #
# #     class Meta:
# #         verbose_name = 'Phone'
# #         verbose_name_plural = 'Phones'
# #
# #
# # class Web(models.Model):
# #     VALUE = models.CharField(verbose_name="URL ресурсов контакта", max_length=100, blank=True, null=True)
# #     VALUE_TYPE = models.CharField(verbose_name="Тип ресурса", max_length=100, blank=True, null=True)
# #
# #     def __str__(self):
# #         return f"{self.VALUE}"
# #
# #     class Meta:
# #         verbose_name = 'Web'
# #         verbose_name_plural = 'Webs'
#
#
# class Contacts(models.Model):
#     ID = models.PositiveIntegerField(primary_key=True, verbose_name='Идентификатор контакта', unique=True, db_index=True)
#     ADDRESS = models.CharField(verbose_name="Адрес контакта", max_length=500, blank=True, null=True)
#     ADDRESS_CITY = models.CharField(verbose_name="Город", max_length=500, blank=True, null=True)
#     ADDRESS_COUNTRY = models.CharField(verbose_name="Страна", max_length=500, blank=True, null=True)
#     ADDRESS_COUNTRY_CODE = models.CharField(verbose_name="Код страны", max_length=500, blank=True, null=True)
#     ADDRESS_POSTAL_CODE = models.CharField(verbose_name="Почтовый индекс", max_length=500, blank=True, null=True)
#     ADDRESS_PROVINCE = models.CharField(verbose_name="Область", max_length=500, blank=True, null=True)
#     ADDRESS_REGION = models.CharField(verbose_name="Район", max_length=500, blank=True, null=True)
#
#     ASSIGNED_BY_ID = models.IntegerField(verbose_name="Связано с пользователем по ID", blank=True, null=True)
#     BIRTHDATE = models.DateTimeField(verbose_name="Дата рождения", blank=True, null=True)
#     COMMENTS = models.CharField(verbose_name="Комментарии", max_length=500, blank=True, null=True)
#
#     HONORIFIC = models.IntegerField(verbose_name="Вид обращения", blank=True, null=True)
#     LAST_NAME = models.CharField(verbose_name="Фамилия", max_length=100, blank=True, null=True)
#     NAME = models.CharField(verbose_name="Имя", max_length=100, blank=True, null=True)
#     ORIGINATOR_ID = models.CharField(verbose_name="Идентификатор источника данных", max_length=500, blank=True, null=True)
#     ORIGIN_ID = models.CharField(verbose_name="Идентификатор элемента в источнике данных", max_length=500, blank=True, null=True)
#     POST = models.CharField(verbose_name="Должность", max_length=200, blank=True, null=True)
#
#     SOURCE_ID = models.IntegerField(verbose_name="Идентификатор источника", blank=True, null=True)
#     TYPE_ID = models.IntegerField(verbose_name="Идентификатор типа", blank=True, null=True)
#     UTM_CAMPAIGN = models.CharField(verbose_name="Обозначение рекламной кампании", max_length=500, blank=True, null=True)
#     UTM_CONTENT = models.CharField(verbose_name="Содержание кампании", max_length=500, blank=True, null=True)
#     UTM_MEDIUM = models.CharField(verbose_name="Тип трафика", max_length=500, blank=True, null=True)
#     UTM_SOURCE = models.CharField(verbose_name="Рекламная система", max_length=500, blank=True, null=True)
#     UTM_TERM = models.CharField(verbose_name="Условие поиска кампании", max_length=500, blank=True, null=True)
#
#     # Множественное:
#     # EMAIL = models.ManyToManyField(Email)
#     # IM = models.ManyToManyField(Im)
#     # PHONE = models.ManyToManyField(Phone)
#     # WEB = models.ManyToManyField(Web)
#
#     def __str__(self):
#         return f"{self.ID}"
#
#     class Meta:
#         verbose_name = 'Контакт'
#         verbose_name_plural = 'Контакты'
#
#
# class Email(models.Model):
#     VALUE = models.CharField(verbose_name="Адрес электронной почты", max_length=100, blank=True, null=True)
#     VALUE_TYPE = models.CharField(verbose_name="Тип электронной почты", max_length=100, blank=True, null=True)
#     contacts = models.ForeignKey(Contacts, verbose_name='Контакт', on_delete=models.CASCADE, related_name='EMAIL',
#                                  blank=True, null=True)
#
#     def __str__(self):
#         return f"{self.VALUE}"
#
#     class Meta:
#         verbose_name = 'Email'
#         verbose_name_plural = 'Emails'
#
#
# class Im(models.Model):
#     VALUE = models.CharField(verbose_name="Мессенджеры", max_length=100, blank=True, null=True)
#     VALUE_TYPE = models.CharField(verbose_name="Тип мессенджера", max_length=100, blank=True, null=True)
#     contacts = models.ForeignKey(Contacts, verbose_name='Контакт', on_delete=models.CASCADE, related_name='IM',
#                                  blank=True, null=True)
#
#     def __str__(self):
#         return f"{self.VALUE}"
#
#     class Meta:
#         verbose_name = 'Im'
#         verbose_name_plural = 'Ims'
#
#
# class Phone(models.Model):
#     VALUE = models.CharField(verbose_name="Телефон контакта", max_length=50, blank=True, null=True)
#     VALUE_TYPE = models.CharField(verbose_name="Тип телефона", max_length=50, blank=True, null=True)
#     contacts = models.ForeignKey(Contacts, verbose_name='Контакт', on_delete=models.CASCADE, related_name='PHONE',
#                                  blank=True, null=True)
#
#     def __str__(self):
#         return f"{self.VALUE}"
#
#     class Meta:
#         verbose_name = 'Phone'
#         verbose_name_plural = 'Phones'
#
#
# class Web(models.Model):
#     VALUE = models.CharField(verbose_name="URL ресурсов контакта", max_length=100, blank=True, null=True)
#     VALUE_TYPE = models.CharField(verbose_name="Тип ресурса", max_length=100, blank=True, null=True)
#     contacts = models.ForeignKey(Contacts, verbose_name='Контакт', on_delete=models.CASCADE, related_name='WEB',
#                                  blank=True, null=True)
#
#     def __str__(self):
#         return f"{self.VALUE}"
#
#     class Meta:
#         verbose_name = 'Web'
#         verbose_name_plural = 'Webs'
#
#
# class Companies(models.Model):
#     ID = models.PositiveIntegerField(primary_key=True, verbose_name='Идентификатор компании', unique=True,
#                                      db_index=True)
#     TITLE = models.CharField(verbose_name="Название", max_length=1000, blank=True, null=True)
#
#     contacts = models.ManyToManyField(Contacts)
#
#     def __str__(self):
#         return f"{self.ID}. {self.TITLE}"
#
#     class Meta:
#         verbose_name = 'Компания'
#         verbose_name_plural = 'Компания'
#
