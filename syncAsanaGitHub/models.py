from django.db import models

# Create your models here.
class IdentityID(models.Model):
    asana_id = models.CharField(max_length=100)
    github_id = models.CharField(max_length=100)

class SyncUsers(models.Model):
    asana_user_id = models.CharField(max_length=100)
    github_user_id = models.CharField(max_length=100)
    asana_user_name = models.CharField(max_length=100)
    github_user_name = models.CharField(max_length=100)

class StatusTask(models.Model):
    asana_status_id = models.CharField(max_length=100)
    github_status_id = models.CharField(max_length=100)

class CommentsTask(models.Model):
    asana_comment_id = models.CharField(max_length=100)
    github_comment_id = models.CharField(max_length=100)