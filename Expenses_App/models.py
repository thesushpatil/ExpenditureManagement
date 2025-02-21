from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserData(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=False)
    name=models.CharField(max_length=100,null=False )
    email=models.EmailField(max_length=100,null=False)
    password=models.CharField(max_length=100,null=False)
