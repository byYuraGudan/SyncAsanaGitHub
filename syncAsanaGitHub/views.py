import hmac
from hashlib import sha1
import logging

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.encoding import force_bytes

import requests
from ipaddress import ip_address, ip_network


request_logger = logging.getLogger('django.request')

@require_POST
@csrf_exempt
def hello(request):
    request_logger.info(request.headers)
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

    # If request reached this point we are in a good shape
    # Process the GitHub events
    event = request.META.get('HTTP_X_GITHUB_EVENT', 'ping')
    return HttpResponse(request.body)

#
# @csrf_exempt
# def asana(request):
#     request_logger.info(str(request.body))
#     if request.headers.get('X-Hook-Secret'):
#         res = HttpResponse("OK",status=200)
#         res['X-Hook-Secret']=request.headers.get('X-Hook-Secret')
#         return res
#     else:
#         return HttpResponse("NOK",status=200)



@csrf_exempt
def asana(request):
    request_logger.info(request.headers)
    request_logger.info(request.body)
    return HttpResponse("OK",status=200)


def index(request):
    return  HttpResponse('Hello, world. You`are at the sync index')