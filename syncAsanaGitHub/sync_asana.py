import asana
from github import Github
from myproject.settings import ASANA_SETTINGS
from syncAsanaGitHub.models import IdentityID
import os
import json

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
    IdentityID.objects.create(asana_id=taskAsana['id'], github_id=obj['number'])

def changed_task(obj):
    asanaID = list(IdentityID.objects.filter(github_id=obj['number']))
    paramTask = {'name':obj['title'],
                 'notes':obj['body'],
                 'projects':[ASANA_SETTINGS['project']['id']]
                 }
    client.tasks.update(asanaID[0].asana_id,params=paramTask)
    pass

def closed_task(obj):
    asanaID = list(IdentityID.objects.filter(github_id=obj['number']))
    client.tasks.update(asanaID[0].asana_id, params={'completed': True if obj['state'] == 'close' else False})

def added_comment_to_task(obj):
    client.tasks.add_comment('id_task',params={'text':'text'})
