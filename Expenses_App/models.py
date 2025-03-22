from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserData(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=False)
    name=models.CharField(max_length=100,null=False )
    email=models.EmailField(max_length=100,null=False)
    password=models.CharField(max_length=100,null=False)



class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    income_id = models.AutoField(primary_key=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Income {self.income_id} - {self.user.username}"

class ExpenseCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exp_id = models.AutoField(primary_key=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Expense {self.exp_id} - {self.user.username} - {self.category.name}"

class Saving(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount to save
    description = models.TextField(blank=True, null=True)  # Description for the saving

    def __str__(self):
        return f"Savings - {self.user.username} - {self.date}"

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    limit = models.DecimalField(max_digits=10, decimal_places=2)


    class Meta:
        unique_together = ('user', 'category', )

    def __str__(self):
        return f"Budget - {self.user.username} - {self.category.name}"