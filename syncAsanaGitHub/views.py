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
    request_logger.info("Webhooks with github")
    return HttpResponse("OK",status=200)

@require_POST
@csrf_exempt
def github_webhooks(request):
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

    return sync_asana.checking_request(obj)



@require_POST
@csrf_exempt
def asana_webhooks(request):
    request_logger.info(request.body)
    events = json.loads(request.body)
    if events.get('events'):
        sync_github.checking_request(events.get('events'))
    res = HttpResponse("OK", status=200)
    res['X-Hook-Secret'] = request.headers.get('X-Hook-Secret')
    return res

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