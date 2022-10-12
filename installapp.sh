#!/bin/sh

# Склонировать репозиторий командой (ввести yes при запросе во время установки):
#git clone https://github.com/Oleg-Sl/Quorum_merge_contacts.git

# Перейти в директорию загруженного проекта:
#cd QQuorum_merge_contacts/

# Создание docker-образа:
docker build ./merge_contacts/

mkdir ./merge_contacts/reports
mkdir ./merge_contacts/files

# !!! ЗДЕСЬ - добавить из Битрикс "client_id" и "client_secret"
echo '{
  "domain": "",
  "client_endpoint": "",
  "auth_token": "",
  "refresh_token": "",
  "application_token": "",
  "expires_in": 3600,
  "client_secret": "",
  "client_id": ""
}' > ./merge_contacts/bx24_secrets.json

# !!! ЗДЕСЬ написать URL вашего сервера
echo '{
  "DOMEN": "https://atonapplication.xyz"
}' > ./merge_contacts/settings.json

echo '{
  "SECRET_KEY": "django-insecure-%0xuz0@kx%e_gwco870bg2^x4*2@akp1sfchy4^-sdws_814sd",
  "DJANGO_MODULE_STR": "production"
}' > ./merge_contacts/django_secrets.json

echo 'END'

docker compose create
docker compose start
