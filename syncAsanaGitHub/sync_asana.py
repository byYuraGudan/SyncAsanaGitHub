import asana
import logging
import os

from django.http import HttpResponse
from myproject.settings import ASANA_SETTINGS
from syncAsanaGitHub.models import *

request_logger = logging.getLogger('django.request')

if 'ASANA_ACCESS_TOKEN' in os.environ:
    client = asana.Client.access_token(os.environ['ASANA_ACCESS_TOKEN'])

def checking_request(obj):
    try:
        if obj.get('action') == 'opened':
                print('opened')
                added_task(obj.get('issue'),obj.get('issue').get('assignee'))
                return HttpResponse("OK", status=201)

        if obj.get('action') == 'edited':
            if obj.get('issue'):
                    print('edited issue')
                    changed_task(obj.get('issue'))
                    return HttpResponse("OK", status=200)
            if obj.get('label'):
                    print('edited label')
                    changed_status(obj.get('label'))
                    return HttpResponse("OK", status=200)

        if obj.get('action') == 'deleted':
                if obj.get('issue'):
                    print('deleted issue')
                    delete_task(obj.get('issue'))
                    return HttpResponse("OK", status=204)
                if obj.get('label'):
                    print('deleted issue')
                    deleted_status(obj.get('label'))
                    return HttpResponse("OK", status=204)

        if obj.get('action') == 'closed' or obj.get('action') == 'reopened':
                print('Edit status task')
                closed_task(obj.get('issue'))
                return HttpResponse("OK", status=200)

        if obj.get('action') == 'created':
                if obj.get('comment'):
                    print('created comment')
                    added_comment_to_task(obj.get('issue'),obj.get('comment'))
                    return HttpResponse("OK", status=201)
                if obj.get('label'):
                    print('created label')
                    added_status(obj.get('label'))
                    return HttpResponse("OK", status=201)

        if obj.get('action') == 'labeled' or obj.get('action') == 'unlabeled':
                if obj.get('issue').get('labels'):
                    print('Change status task')
                    changed_status_of_task(obj.get('issue'), obj.get('issue').get('labels'))
                    return  HttpResponse("OK",status=200)
        if obj.get('action') == 'assigned' or obj.get('action') == 'unassigned':
                if obj.get('issue').get('assignees'):
                    print('assigned')
                assigned_task(obj.get('issue'),obj.get('issue').get('assignees'))
                return HttpResponse("OK", status=200)


    except AttributeError as err:
        request_logger.info("Error - %s"%err)
        return HttpResponse("Error - Bad request",status=500)
    return HttpResponse("OK", status=200)


def added_task(obj,assignee):
    """This function create new task in asana"""
    if len(list(IdentityID.objects.filter(github_id=obj.get('number')))) > 0:
        request_logger.info("This task existed")
    else:
        asana_user_id = list(SyncUsers.objects.filter(github_user_id=assignee.get('id') if assignee != None else -1))
        paramTask = {'name':obj['title'],
                     'notes':obj['body'],
                     'projects':[ASANA_SETTINGS['project']['id']],
                     'assignee':asana_user_id[0].asana_user_id if len(asana_user_id) > 0 else None}
        taskAsana = client.tasks.create_in_workspace(ASANA_SETTINGS.get('workspace').get('id'), params=paramTask)
        IdentityID.objects.create(github_id=obj['number'],
                                  asana_id=taskAsana['id'],)
        changed_status_of_task(obj, obj.get('labels'))

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

def assigned_task(obj, assignees):
    asanaID = list(IdentityID.objects.filter(github_id=obj['number']))
    asana_user_id = list(SyncUsers.objects.filter(github_user_id=assignees[0]['id'] if len(assignees) > 0 else -1))
    if len(asanaID) > 0:
        paramTask = {'assignee': asana_user_id[0].asana_user_id if len(asana_user_id) > 0 else None}
        client.tasks.update(asanaID[0].asana_id,params=paramTask)
        request_logger.info("Assigned %s"%paramTask)
    else:
        request_logger.info("Not Assigned")



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

def changed_status_of_task(obj, status):
    asana_id = list(IdentityID.objects.filter(github_id=obj.get('number')))
    statusID = list(StatusTask.objects.filter(github_status_id=status[0].get('id') if len(status) > 0 else -1))
    if len(asana_id) > 0 and len(statusID) > 0:
        params = {'project': ASANA_SETTINGS['project']['id'], 'section': statusID[0].asana_status_id}
        client.tasks.add_project(asana_id[0].asana_id, params=params)
        request_logger.info('Modified status(%s) of task(%s)'%(statusID[0].asana_status_id,asana_id[0].asana_id))
    else:
        request_logger.info("Not modified status task")

def deleted_status(status):
    asana_id = list(StatusTask.objects.filter(github_status_id=status['id']))
    if len(asana_id) > 0:
        client.sections.delete(asana_id[0].asana_status_id)
        request_logger.info("Label deleted (%s)"%asana_id)
    else:
        request_logger.info("Label not deleted")