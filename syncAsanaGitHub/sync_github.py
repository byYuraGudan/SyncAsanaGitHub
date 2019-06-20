import os
import json
import logging

from github import Github
import asana



if 'ASANA_ACCESS_TOKEN' in os.environ:
    asanaClient = asana.Client.access_token(os.environ['ASANA_ACCESS_TOKEN'])

if 'GITHUB_ACCESS_TOKEN' in os.environ:
    gitClient = Github(os.environ['GITHUB_ACCESS_TOKEN'])

request_logger = logging.getLogger('django.request')

def create_issue(params):
    task = asanaClient.tasks.find_by_id(params['resource'])
    request_logger.info('Task - %s'%task)
    repo = gitClient.get_repo("byYuraGudan/SyncAsanaGitHub")
    print(repo)
    repo.create_issue(title=task['name'],body=task['notes'])


def check_request(events):
    request_logger.info(events)
    if len(events) > 0:
        for event in events:
            if event.get('type') == "task":
                create_issue(event)
