import asana
import logging
from github import Github
from myproject.settings import ASANA_SETTINGS
from syncAsanaGitHub.models import IdentityID
import os
import json

request_logger = logging.getLogger('django.request')


if 'ASANA_ACCESS_TOKEN' in os.environ:
    client = asana.Client.access_token(os.environ['ASANA_ACCESS_TOKEN'])

if 'GITHUB_ACCESS_TOKEN' in os.environ:
    gitClient = Github(os.environ['GITHUB_ACCESS_TOKEN'])
    repoGit = gitClient.get_repo("byYuraGudan/SyncAsanaGitHub")


def added_task(obj):
    paramTask = {'name':obj['title'],
                 'notes':obj['body'],
                 'projects':[ASANA_SETTINGS['project']['id']]
                 }
    taskAsana = client.tasks.create_in_workspace(ASANA_SETTINGS.get('workspace').get('id'), params=paramTask)
    IdentityID.objects.create(github_id=obj['number'], asana_id=taskAsana['id'])

def changed_task(obj):
    asanaID = list(IdentityID.objects.filter(github_id=obj['number']))
    print(asanaID)
    for i in asanaID:
        print("%s - %s"%(i.github_id,i.asana_id))
    if len(asanaID) > 0:
        paramTask = {'name':obj['title'],
                     'notes':obj['body']}
        client.tasks.update(asanaID[0].asana_id,params=paramTask)
        request_logger.info("Task, was changed with parameters %s"%paramTask)
    else:
        request_logger.info("Task,not changed")


def closed_task(obj):
    asanaID = list(IdentityID.objects.filter(github_id=obj['number']))
    print(asanaID)
    if len(asanaID) > 0 :
        client.tasks.update(asanaID[0].asana_id, params={'completed': True if obj['state'] == 'closed' else False})
        request_logger.info("Task was closed")
    else:
        request_logger.info("Task not closed")

def added_comment_to_task(obj,comment):
    """This function checked number issue in github and id task.
        Next step added new comment from github to asana task"""
    asanaID = list(IdentityID.objects.filter(github_id=obj['number']))
    if len(asanaID) > 0:
        client.tasks.add_comment(asanaID[0].asana_id,params={'text':comment['body']})
    else:
        request_logger.info("Comment, not add to task")
