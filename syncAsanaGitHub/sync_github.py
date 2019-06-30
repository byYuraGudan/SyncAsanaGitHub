import os
import json
import logging

from github import Github
from django.http import HttpResponse
from syncAsanaGitHub.models import  IdentityID,StatusTask,SyncUsers
from myproject.settings import ASANA_SETTINGS


import asana

request_logger = logging.getLogger('django.request')



if 'ASANA_ACCESS_TOKEN' in os.environ:
    asanaClient = asana.Client.access_token(os.environ['ASANA_ACCESS_TOKEN'])

if 'GITHUB_ACCESS_TOKEN' in os.environ:
    gitClient = Github(os.environ['GITHUB_ACCESS_TOKEN'])
    repoGit = gitClient.get_repo("byYuraGudan/SyncAsanaGitHub")


def create_issue(event):
    if len(list(IdentityID.objects.filter(asana_id=event.get('resource')))) > 0:
        return HttpResponse("OK",status=200)
    else:
        task = asanaClient.tasks.find_by_id(event.get('resource'))
        new_issue = repoGit.create_issue(title=task.get('name'), body=task.get('notes'))
        IdentityID.objects.create(asana_id=event.get('resource'), github_id=new_issue.number)
        request_logger.info(task)
        request_logger.info(new_issue)
        return HttpResponse("Create issue",status=201)


def change_issue(event):
    task = asanaClient.tasks.find_by_id(event.get('resource'))
    github_task_number = list(IdentityID.objects.filter(asana_id = task.get('id')))
    if len(github_task_number) > 0:
        request_logger.info("Change issue")
        issue = repoGit.get_issue(int(github_task_number[0].github_id))
        asana_user_id = task.get('assignee').get('id') if task_event.get('assignee') != None else -1
        assignee = list(SyncUsers.objects.filter(asana_user_id=asana_user_id))
        issue.edit(title=task.get('name'),
                   body=task.get('notes'),
                   state= 'closed' if task.get('completed') else 'opened',
                   assignee=assignee.github_user_name if len(assignee) > 0 else '',
                   labels=[task.get('memberships')[0].get('section').get('name')])
        return HttpResponse("Issue changed",status=200)
    else:
        request_logger.info("Issue not changed")
        return HttpResponse("Issue changed", status=304)






def checking_request(events):
    try:
        request_logger.info(events)
        if len(events) > 0:
            for event in events:
                print(event)
                if event.get('parent') != 1127318215881837:
                    if event.get('type') == 'task':
                        if event.get('action') == 'added':
                            request_logger.info('create task')
                            return create_issue(event)
                        if event.get('action') == 'changed':
                            return change_issue(event)
                        if event.get('action') == 'deleted':
                            pass
    except AttributeError as err:
        request_logger.info("Error - %s"%err)
        return HttpResponse("Error", status=500)
    return HttpResponse("OK")


def task_event(event):
    if event.action == 'added':
        create_issue(event)
    if event.action == 'changed':
        pass

def comment_event(event):
    pass

