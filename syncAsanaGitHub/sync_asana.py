import asana
import logging
import os

from myproject.settings import ASANA_SETTINGS
from syncAsanaGitHub.models import *

request_logger = logging.getLogger('django.request')

if 'ASANA_ACCESS_TOKEN' in os.environ:
    client = asana.Client.access_token(os.environ['ASANA_ACCESS_TOKEN'])

def added_task(obj,assignee):
    """This function create new task in asana"""
    asana_user_id = list(SyncUsers.objects.filter(github_user_id=assignee.get('id') if assignee != None else -1))
    paramTask = {'name':obj['title'],
                 'notes':obj['body'],
                 'projects':[ASANA_SETTINGS['project']['id']],
                 'assignee':asana_user_id[0].asana_user_id if len(asana_user_id) > 0 else None}
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

def assigned_task(obj,assigne):
    asanaID = list(IdentityID.objects.filter(github_id=obj['number']))
    asana_user_id = list(SyncUsers.objects.filter(github_user_id=assigne['id']))
    if len(asanaID) > 0:
        request_logger.info("%s - %s" % (asana_user_id[0].asana_user_id, assigne['id']))
        paramTask = {'assignee': asana_user_id[0].asana_user_id if len(asana_user_id) > 0 else None}
        client.tasks.update(asanaID[0].asana_id,params=paramTask)
        request_logger.info("Assigned %s"%paramTask)
    else:
        request_logger.info("Not Assigned")

def unassigned_task(obj):
    asanaID = list(IdentityID.objects.filter(github_id=obj['number']))
    if len(asanaID) > 0:
        paramTask = {'assignee': None}
        client.tasks.update(asanaID[0].asana_id,params=paramTask)
        request_logger.info("Unassigned %s"%paramTask)
    else:
        request_logger.info("Not unassigned")


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

def added_status(status):
    """This function added status(section) in asana"""
    parameters = {"name":status['name']}
    id_status = client.sections.create_in_project(ASANA_SETTINGS['project']['id'], params=parameters)
    StatusTask.objects.create(asana_status_id=id_status.get('id'),github_status_id=status['id'])

def changed_status(status):
    """This function changed status(section) in asana"""
    asana_id = list(StatusTask.objects.filter(github_status_id=status['id']))
    if len(asana_id) > 0:
        parameters = {"name": status['name']}
        client.sections.update(asana_id[0].asana_status_id, params=parameters)
        request_logger.info("Label update (%s)"%asana_id)
    else:
        request_logger.info("Label not update")

def change_status_of_task(obj,label):
    print(obj)
    print(label)
    asana_id = list(IdentityID.objects.filter(github_id=obj.get('number')))
    statusID = list(StatusTask.objects.filter(github_status_id=label.get('id')))
    if len(asana_id) > 0 and statusID >0:
        params = {'project': ASANA_SETTINGS['project']['id'], 'section': statusID[0].asana_status_id}
        client.tasks.add_project(asana_id[0].asana_id, params=params)
        request_logger.info('Modified status(%s) of task(%s)'%(statusID[0].asana_status_id,asana_id[0].asana_id))
    else:
        request_logger("Not modified status task")




