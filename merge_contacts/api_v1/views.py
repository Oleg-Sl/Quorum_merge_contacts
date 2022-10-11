from threading import Thread
from django.shortcuts import render
from django.http import FileResponse, Http404
from django.views.decorators.clickjacking import xframe_options_exempt
from rest_framework import views, status
from rest_framework.response import Response
import logging
import os
import json
from django.conf import settings


from .service import handler, tasks
from .service.bx24 import tokens

# логгер входные данные событий от Битрикс
logger = logging.getLogger('tasks_access')
logger.setLevel(logging.INFO)
fh_tasks_access = logging.handlers.TimedRotatingFileHandler('access.log', when='D', interval=1)
formatter_tasks_access = logging.Formatter('[%(asctime)s] %(levelname).1s %(message)s')
fh_tasks_access.setFormatter(formatter_tasks_access)
logger.addHandler(fh_tasks_access)


# Обработчик установки приложения
class InstallAppApiView(views.APIView):
    @xframe_options_exempt
    def post(self, request):
        data = {
            "domain": request.query_params.get("DOMAIN", ""),
            "auth_token": request.data.get("AUTH_ID", ""),
            "expires_in": request.data.get("AUTH_EXPIRES", 3600),
            "refresh_token": request.data.get("REFRESH_ID", ""),
            "application_token": request.query_params.get("APP_SID", ""),
            'client_endpoint': f'https://{request.query_params.get("DOMAIN", "")}/rest/',
        }
        bx24_tokens.create_secrets_bx24(data)
        return render(request, 'install.html')


# Обработчик удаления приложения
class UninstallAppApiView(views.APIView):
    @xframe_options_exempt
    def post(self, request):
        return Response(status.HTTP_200_OK)


# Обработчик установленного приложения
class IndexApiView(views.APIView):
    @xframe_options_exempt
    def post(self, request):
        with open(os.path.join(settings.BASE_DIR, 'settings.json')) as secrets_file:
            data = json.load(secrets_file)

        return render(request, 'index.html', context={"domen": data.get("DOMEN")})

    @xframe_options_exempt
    def get(self, request):
        with open(os.path.join(settings.BASE_DIR, 'settings.json')) as secrets_file:
            data = json.load(secrets_file)

        return render(request, 'index.html', context={"domen": data.get("DOMEN")})


class DealCreateUpdateViewSet(views.APIView):
    """ Контроллер обработки событий BX24: onVoximplantCallEnd """
    def post(self, request):
        logger.info(request.data)
        event = request.data.get("event", "")
        id_deal = request.data.get("data[FIELDS][ID]", None)
        application_token = request.data.get("auth[application_token]", None)

        if bx24_tokens.get_secret_bx24("application_token") != application_token:
            return Response("Unverified event source", status=status.HTTP_400_BAD_REQUEST)

        if not id_deal:
            return Response("Not transferred ID deal", status=status.HTTP_400_BAD_REQUEST)

        status_code, msg = handler.add_company_in_deal(id_deal)

        if status_code == 200:
            return Response(msg, status=status.HTTP_200_OK)
        else:
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)


thread_merge = None


class MergeContactsViewSet(views.APIView):

    def post(self, request):
        global thread_merge

        logger.info(request.data)
        method = request.data.get("method")

        if thread_merge and thread_merge.is_alive():
            return Response("NO", status=status.HTTP_200_OK)

        thread_merge = Thread(target=tasks.merge_contacts, args=[method, ])
        thread_merge.start()

        return Response("Ok", status=status.HTTP_200_OK)


class StatusMergeContactsViewSet(views.APIView):

    def get(self, request):
        res = {
            "status": False
        }

        if thread_merge:
            state = thread_merge.is_alive()
            res["status"] = state

            if state:
                res["contacts"] = {
                    "start": tasks.contacts_queue.get_start_size(),
                    "actual": tasks.contacts_queue.qsize()
                }
                res["companies"] = {
                    "start": tasks.companies_queue.get_start_size(),
                    "actual": tasks.companies_queue.qsize()
                }
                res["contact_company"] = {
                    "start": tasks.company_contact_queue.get_start_size(),
                    "actual": tasks.company_contact_queue.qsize()
                }
                res["duplicates"] = {
                    "start": tasks.duplicates_queue.get_start_size(),
                    "actual": tasks.duplicates_queue.qsize()
                }

        return Response(res, status=status.HTTP_200_OK)


class ReportViewSet(views.APIView):
    def get(self, request):
        path = os.path.join(settings.BASE_DIR, 'reports')
        return Response(os.listdir(path), status=status.HTTP_200_OK)


class ReportDownloadViewSet(views.APIView):
    def get(self, request):
        f_name = request.query_params.get("file")
        if not f_name:
            return Response('Not found file', status=status.HTTP_404_NOT_FOUND)

        path = os.path.join(settings.BASE_DIR, 'reports', f_name)

        try:
            response = FileResponse(open(path, 'rb'))
            response['content_type'] = "application/octet-stream"
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(path)
            return response
        except Exception:
            raise Http404

    def delete(self, request, *args, **kwargs):
        f_name = request.query_params.get("file")
        if not f_name:
            return Response('Not found file', status=status.HTTP_404_NOT_FOUND)

        path = os.path.join(settings.BASE_DIR, 'reports', f_name)
        if os.path.exists(path):
            os.remove(path)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response('Not found file', status=status.HTTP_404_NOT_FOUND)

    # def delete(self, request, pk, format=None):
    #     event = self.get_object(pk)
    #     event.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)


