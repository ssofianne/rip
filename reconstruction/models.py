from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager

class NewUserManager(UserManager):
    def create_user(self,email,password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email address')
        
        email = self.normalize_email(email) 
        user = self.model(email=email, **extra_fields) 
        user.set_password(password)
        user.save(using=self.db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(("email адрес"), unique=True)
    password = models.CharField(max_length=255, verbose_name="Пароль")    
    is_staff = models.BooleanField(default=False, verbose_name="Является ли пользователь менеджером?")
    is_superuser = models.BooleanField(default=False, verbose_name="Является ли пользователь админом?")
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)

    USERNAME_FIELD = 'email'

    objects =  NewUserManager()

class Work(models.Model):
    title = models.CharField(max_length=100, null=False)
    description = models.TextField(default="У этого вида работ нет описания", null=False)
    price = models.IntegerField(default=5000, null=False)
    imageurl = models.URLField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False, null=False)
    class Meta:
        db_table = 'work'
    def __str__(self):
        return f"Work '{self.id}':  '{self.title}'"
    

class Reconstruction(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('deleted', 'Удалена'),
        ('created', 'Сформирована'),
        ('completed', 'Завершена'),
        ('rejected', 'Отклонена')
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='draft', null=False)
    creation_date = models.DateTimeField(default=timezone.now, null=False)
    apply_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False, related_name='user')
    moderator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderator')

    place = models.CharField(max_length=100, null=True, blank=True)
    fundraising = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'reconstruction'
    def __str__(self):
        return f"Reconstruction '{self.id}' by '{self.user.email}' created at '{self.creation_date}'"

    

class Space(models.Model):
    reconstruction = models.ForeignKey(Reconstruction, on_delete=models.CASCADE)
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    space = models.CharField(max_length=100, blank=True, null=True, default='')

    class Meta:
        db_table = 'space'
        unique_together = ('reconstruction', 'work')
    def __str__(self):
        return f"Space '{self.id}' in '{self.reconstruction}' of '{self.work}' = '{self.space}'"
