import os
import json
import logging

from github import Github
from syncAsanaGitHub.models import  IdentityID
from syncAsanaGitHub.json_convert import json2obj

import asana

request_logger = logging.getLogger('django.request')



if 'ASANA_ACCESS_TOKEN' in os.environ:
    asanaClient = asana.Client.access_token(os.environ['ASANA_ACCESS_TOKEN'])

if 'GITHUB_ACCESS_TOKEN' in os.environ:
    gitClient = Github(os.environ['GITHUB_ACCESS_TOKEN'])
    repoGit = gitClient.get_repo("byYuraGudan/SyncAsanaGitHub")


def create_issue(asanaTask):
    currentTask = asanaClient.tasks.find_by_id(asanaTask.resource)
    currentTask = json2obj(json.dumps(currentTask))
    new_issue = repoGit.create_issue(title=currentTask.name, body=currentTask.notes)
    IdentityID.objects.create(asana_id=asanaTask.resource, github_id=new_issue.number)
    request_logger.info(currentTask)
    request_logger.info(new_issue)

def change_issue(asanaTask):
    currentTask = asanaClient.tasks.find_by_id(asanaTask.resource)
    currentTask = json2obj(json.dumps(currentTask))

def check_request(events):
    try:
        request_logger.info(events)
        if len(events) > 0:
            for event in events:
                if event.type == "task":
                    task_event(event)
    except AttributeError as err:
        request_logger.info("Error - %s"%err)


def task_event(event):
    if event.action == 'added':
        create_issue(event)
    if event.action == 'changed':
        pass

def comment_event(event):
    pass

