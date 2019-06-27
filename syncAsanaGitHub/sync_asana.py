import asana
import logging
import os

from myproject.settings import ASANA_SETTINGS
from syncAsanaGitHub.models import *

request_logger = logging.getLogger('django.request')

if 'ASANA_ACCESS_TOKEN' in os.environ:
    client = asana.Client.access_token(os.environ['ASANA_ACCESS_TOKEN'])

def added_task(obj):
    """This function create new task in asana"""
    paramTask = {'name':obj['title'],
                 'notes':obj['body'],
                 'projects':[ASANA_SETTINGS['project']['id']]}
    taskAsana = client.tasks.create_in_workspace(ASANA_SETTINGS.get('workspace').get('id'), params=paramTask)
    IdentityID.objects.create(github_id=obj['number'], asana_id=taskAsana['id'])

def changed_task(obj):
    """This function checked number issue in github and id task.
        Next step post changed github issue to asana task"""
    asanaID = list(IdentityID.objects.filter(github_id=obj['number']))
    if len(asanaID) > 0:
        paramTask = {'name':obj['title'],
                     'notes':obj['body']}
        client.tasks.update(asanaID[0].asana_id,params=paramTask)
        request_logger.info("Task, was changed with parameters %s"%paramTask)
    else:
        request_logger.info("Task,not changed")

def delete_task(obj):
    """This function delete task"""
    asanaID = list(IdentityID.objects.filter(github_id=obj['number']))
    if len(asanaID) > 0:
        client.tasks.delete(asanaID[0].asana_id)
        IdentityID.objects.filter(github_id=obj['number']).delete()
        request_logger.info("Task deleted")
    else:
        request_logger.info("Task not deleted")

def closed_task(obj):
    """This function closed and reopen task"""
    asanaID = list(IdentityID.objects.filter(github_id=obj['number']))
    if len(asanaID) > 0:
        client.tasks.update(asanaID[0].asana_id, params={'completed': True if obj['state'] == 'closed' else False})
        request_logger.info("Task was %s"%obj['state'])
    else:
        request_logger.info("Task not closed")

def added_comment_to_task(obj,comment):
    """This function checked number issue in github and id task.
        Next step added new comment from github to asana task"""
    asanaID = list(IdentityID.objects.filter(github_id=obj['number']))
    if len(asanaID) > 0:
        client.tasks.add_comment(asanaID[0].asana_id,params={'text':comment['body']})
        request_logger.info("Comment, add to task (%s)"%asanaID[0].asana_id)
    else:
        request_logger.info("Comment, not add to task")

def added_status_task(status):
    parameters = {"name":status['name']}
    id_status = client.sections.create_in_project(ASANA_SETTINGS['project']['id'], params=parameters)
    StatusTask.objects.create(asana_status_id=id_status.get('id'),github_status_id=status['id'])

def changed_status_task(status):
    parameters = {"name":status['name']}
    asana_id = list(StatusTask.objects.filter(github_status_id=status['id']))
    if len(asana_id) > 0:
        client.sections.update(asana_id[0].asana_status_id, params=parameters)
        request_logger.info("Label update (%s)"%asana_id)
    else:
        request_logger.info("Label not update")


