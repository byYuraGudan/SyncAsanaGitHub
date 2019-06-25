from django.db import models

# Create your models here.
class IdentityID(models.Model):
    asana_id = models.CharField(max_length=100)
    github_id = models.CharField(max_length=100)

