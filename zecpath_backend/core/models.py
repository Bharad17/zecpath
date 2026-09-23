from django.db import models
class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

class Job(models.Model):
    title = models.CharField(max_length=100)

class application(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    job = models.ForeignKey(Job,on_delete=models.CASCADE)
    applied_at = models.DateTimeField()  
