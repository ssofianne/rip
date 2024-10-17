# Generated by Django 5.1.2 on 2024-10-10 10:37

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Work',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.CharField(default='У этого вида работ нет описания', max_length=500)),
                ('price', models.IntegerField(default=5000)),
                ('imageUrl', models.URLField()),
                ('is_deleted', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'work',
            },
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('draft', 'Черновик'), ('deleted', 'Удалена'), ('created', 'Сформирована'), ('completed', 'Завершена'), ('rejected', 'Отклонена')], default='draft', max_length=50)),
                ('creation_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('apply_date', models.DateTimeField(blank=True, null=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('place', models.CharField(blank=True, max_length=100, null=True)),
                ('fundraising', models.IntegerField(blank=True, null=True)),
                ('moderator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='moderator', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'application',
            },
        ),
        migrations.CreateModel(
            name='Space',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('space', models.IntegerField()),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reconstruction_app.application')),
                ('work', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reconstruction_app.work')),
            ],
            options={
                'db_table': 'space',
                'unique_together': {('application', 'work')},
            },
        ),
    ]