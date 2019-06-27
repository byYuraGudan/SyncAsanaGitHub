import hmac
from hashlib import sha1
import logging
from syncAsanaGitHub.json_convert import json2obj
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.encoding import force_bytes

import json
from syncAsanaGitHub import sync_asana,sync_github
from syncAsanaGitHub.models import *
import requests
from ipaddress import ip_address, ip_network


request_logger = logging.getLogger('django.request')

@require_POST
@csrf_exempt
def hello(request):
    # If request reached this point we are in a good shape
    # Process the GitHub events
    return HttpResponse("OK",status=200)

@require_POST
@csrf_exempt
def github(request):
    request_logger.info(request.body)
    # Verify if request came from GitHub
    forwarded_for = u'{}'.format(request.META.get('HTTP_X_FORWARDED_FOR'))
    client_ip_address = ip_address(forwarded_for)
    whitelist = requests.get('https://api.github.com/meta').json()['hooks']

    for valid_ip in whitelist:
        if client_ip_address in ip_network(valid_ip):
            break
    else:
        return HttpResponseForbidden('Permission denied.')

    # Verify the request signature
    header_signature = request.META.get('HTTP_X_HUB_SIGNATURE')
    if header_signature is None:
        return HttpResponseForbidden('Permission denied.')

    sha_name, signature = header_signature.split('=')
    if sha_name != 'sha1':
        return HttpResponseServerError('Operation not supported.', status=501)

    mac = hmac.new(force_bytes(settings.GITHUB_WEBHOOK_KEY), msg=force_bytes(request.body), digestmod=sha1)
    if not hmac.compare_digest(force_bytes(mac.hexdigest()), force_bytes(signature)):
        return HttpResponseForbidden('Permission denied.')

    request_logger.info(request.body)
    obj = json.loads(request.body)

    try:
        if obj.get('action') == 'opened':
                print('opened')
                sync_asana.added_task(obj.get('issue'),obj.get('issue').get('assignee'))
                return HttpResponse("OK", status=201)

        if obj.get('action') == 'edited':
            if obj.get('comment'):
                    print('edited comment')
                    sync_asana.changed_task(obj.get('issue'))
                    return HttpResponse("OK", status=200)
            if obj.get('label'):
                    print('edited label')
                    sync_asana.changed_status(obj.get('label'))
                    return HttpResponse("OK", status=200)

        if obj.get('action') == 'deleted':
                print('deleted')
                sync_asana.delete_task(obj.get('issue'))
                return HttpResponse("OK", status=204)

        if obj.get('action') == 'closed' or obj.get('action') == 'reopened':
                print('Edit status task')
                sync_asana.closed_task(obj.get('issue'))
                return HttpResponse("OK", status=200)

        if obj.get('action') == 'created':
                if obj.get('comment'):
                    print('created comment')
                    sync_asana.added_comment_to_task(obj.get('issue'),obj.get('comment'))
                    return HttpResponse("OK", status=201)
                if obj.get('label'):
                    print('created label')
                    sync_asana.added_status(obj.get('label'))
                    return HttpResponse("OK", status=201)

        if obj.get('action') == 'labeled' or obj.get('action') == 'unlabeled':
                if obj.get('issue').get('labels'):
                    print('Change status task')
                    sync_asana.change_status_of_task(obj.get('issue'),obj.get('issue').get('labels'))
                    return  HttpResponse("OK",status=200)
        if obj.get('action') == 'assigned' or obj.get('action') == 'unassigned':
                if obj.get('issue').get('assignees'):
                    print('assigned')
                sync_asana.assigned_task(obj.get('issue'),obj.get('issue').get('assignees'))
                return HttpResponse("OK", status=200)


    except AttributeError as err:
        request_logger.info("Error - %s"%err)
        return HttpResponse("Error - Bad request",status=500)
    return HttpResponse("OK", status=200)

@csrf_exempt
def asana(request):
    request_logger.info(request.body)
    # if request.method == "POST":
    #     body = json2obj(request.body)
    #     sync_github.check_request(body.events)
    return HttpResponse("OK",status=200)

@require_POST
@csrf_exempt
def asana_subscribe_webhooks(request):
    request_logger.info(str(request.body))
    if request.headers.get('X-Hook-Secret'):
        res = HttpResponse("OK",status=200)
        res['X-Hook-Secret']=request.headers.get('X-Hook-Secret')
        return res
    else:
        return HttpResponse("NOK",status=200)

def index(request):
    print("List IdentityTaskId")
    for i in list(IdentityID.objects.all()):
        print("%s - %s"%(i.github_id,i.asana_id))
    print("List UserTask")
    for i in list(SyncUsers.objects.all()):
        print("%s(%s) - %s(%s)"%(i.github_user_name,i.github_user_id,i.asana_user_name,i.asana_user_id))
    print("List StatusTaskID")
    for i in list(StatusTask.objects.all()):
        print("%s - %s"%(i.github_status_id,i.asana_status_id))
    # SyncUsers.objects.create(github_user_name="byYuraGudan",github_user_id="34908227",asana_user_name="Yurii Hudan",asana_user_id="1126657026625460")
    # SyncUsers.objects.create(github_user_name="bockardo",github_user_id="11328675",asana_user_name="bockardo",asana_user_id="1128736727323219")
    return  HttpResponse('Hello, world. You`are at the sync index')