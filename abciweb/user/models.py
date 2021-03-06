from django.db import models
import datetime

class ABCIUser(models.Model):
    username = models.CharField(max_length=30, primary_key=True)
    pubkey = models.CharField(max_length=30)
    prvkey_file = models.CharField(max_length=50)
    time = models.DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return self.username

class DataTemplate(models.Model):
    tid = models.CharField(max_length=30, primary_key=True)
    sender = models.CharField(max_length=30)
    tname = models.CharField(max_length=30)
    category = models.CharField(max_length=30)
    path = models.CharField(max_length=80)
    time = models.DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return self.tid

class Offer(models.Model):
    cid = models.CharField(max_length=50, primary_key=True)
    tid = models.CharField(max_length=30)
    seller = models.CharField(max_length=30)
    buyer = models.CharField(max_length=30)
    fee = models.FloatField()
    encode = models.CharField(max_length=20,default='plain')
    time = models.DateTimeField(default=datetime.datetime.now)
    cid = models.CharField(max_length=50)
    path = models.CharField(max_length=80)
    status = models.CharField(max_length=10,default="new")

    def __str__(self):
        return self.cid

class Data(models.Model):
    did = models.CharField(max_length=30, primary_key=True)
    tid = models.CharField(max_length=30)
    encode = models.CharField(max_length=30)
    owner = models.CharField(max_length=80)
    path = models.CharField(max_length=80)
    time = models.DateTimeField(default=datetime.datetime.now)
    key = models.CharField(max_length=80)

    def __str__(self):
        return self.did

class Transaction(models.Model):
    sid = models.CharField(max_length=30, primary_key=True)
    did = models.CharField(max_length=30)
    cid = models.CharField(max_length=30)
    path = models.CharField(max_length=80)
    time = models.DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return self.sid

class symmkeys(models.Model):
    kid = models.CharField(max_length=80, primary_key=True)
    owner = models.CharField(max_length=80)
    key = models.CharField(max_length=80)

    def __str__(self):
        return self.kid