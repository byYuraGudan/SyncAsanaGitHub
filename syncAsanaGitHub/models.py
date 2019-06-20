from django.db import models

# Create your models here.
class IdentityID(models.Model):
    asana_id = models.IntegerField()
    github_id = models.IntegerField()

