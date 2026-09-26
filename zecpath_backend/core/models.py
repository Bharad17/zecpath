from django.db import models
class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

class Employer(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    company_name = models.CharField()
class Candidate(models.Model):
    user = models.OneToOneField(User,on_delete = models.CASCADE)
    skills = models.CharField(max_length=200)

class Job(models.Model):
    employer = models.ForeignKey(Employer,on_delete = models.CASCADE,null = True,blank = True)
    title = models.CharField(max_length=100)

class application(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    job = models.ForeignKey(Job,on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate,on_delete=models.CASCADE,null = True,blank = True)
    applied_at = models.DateTimeField()  
