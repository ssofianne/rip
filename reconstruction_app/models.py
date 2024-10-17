from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Work(models.Model):
    title = models.CharField(max_length=100, null=False)
    description = models.CharField(max_length=500, default="У этого вида работ нет описания", null=False)
    price = models.IntegerField(default=5000, null=False)
    imageUrl = models.URLField(null=False)
    is_deleted = models.BooleanField(default=False, null=False)
    class Meta:
        db_table = 'work'
    def __str__(self):
        return f"Work '{self.id}':  '{self.title}'"
    

class Application(models.Model):
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
    fundraising = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'application'
    def __str__(self):
        return f"Application '{self.id}' by '{self.user.username}' created at '{self.creation_date}'"
    

class Space(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    space = models.IntegerField()
    class Meta:
        db_table = 'space'
        unique_together = ('application', 'work')
    def __str__(self):
        return f"Space '{self.id}' in '{self.application}' of '{self.work}' = '{self.space}'"
