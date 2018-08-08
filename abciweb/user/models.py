from django.db import models

class ABCIUser(models.Model):
    username = models.CharField(max_length=30)
    pubkey = models.CharField(max_length=30)
    prvkey_file = models.CharField(max_length=50)

    def __str__(self):
        return self.username

class DataTemplate(models.Model):
    tid = models.CharField(max_length=30)
    sender = models.CharField(max_length=30)
    tname = models.CharField(max_length=30)
    category = models.CharField(max_length=30)
    path = models.CharField(max_length=80)

    def __str__(self):
        return self.tid

