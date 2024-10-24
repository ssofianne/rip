from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random

class Work(models.Model):
    title = models.CharField(max_length=100, null=False)
    description = models.TextField(default="У этого вида работ нет описания", null=False)
    price = models.IntegerField(default=5000, null=False)
    imageUrl = models.URLField(null=False)
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name='user')
    moderator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderator')

    place = models.CharField(max_length=100, null=True, blank=True)
    fundraising = models.IntegerField(null=True, blank=True, editable=False)
    
    class Meta:
        db_table = 'reconstruction'
    def __str__(self):
        return f"Reconstruction '{self.id}' by '{self.user.username}' created at '{self.creation_date}'"
    
    def save(self, *args, **kwargs):
        if self.pk is not None:
            original = Reconstruction.objects.get(pk=self.pk)
            if original.status != self.status and self.status == 'completed':
                self.fundraising = self.generate_fundraising()
        
        super().save(*args, **kwargs)

    def generate_fundraising(self):
        return random.randint(5000, 100000)
    

class Space(models.Model):
    reconstruction = models.ForeignKey(Reconstruction, on_delete=models.CASCADE)
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    space = models.CharField(max_length=100, blank=True, null=True, default='')

    class Meta:
        db_table = 'space'
        unique_together = ('reconstruction', 'work')
    def __str__(self):
        return f"Space '{self.id}' in '{self.reconstruction}' of '{self.work}' = '{self.space}'"
