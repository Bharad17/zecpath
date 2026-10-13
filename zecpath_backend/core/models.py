from django.contrib.auth.models import AbstractUser
from django.db import models
class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)

    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('EMPLOYER', 'Employer'),
        ('CANDIDATE', 'Candidate'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Employer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100, blank=True, default="")
    domain = models.CharField(max_length=100, blank=True, default="")
    company_size = models.CharField(max_length=50, blank=True, default="")
    is_verified = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)


class Candidate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    skills = models.CharField(max_length=200, blank=True, default="")
    education = models.CharField(max_length=200, blank=True, default="")
    experience = models.TextField(blank=True, default="")
    expected_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    is_deleted = models.BooleanField(default=False)


class Job(models.Model):
    employer = models.ForeignKey(Employer,on_delete = models.CASCADE,null = True,blank = True)
    title = models.CharField(max_length=100)

class application(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    job = models.ForeignKey(Job,on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate,on_delete=models.CASCADE,null = True,blank = True)
    applied_at = models.DateTimeField()  
