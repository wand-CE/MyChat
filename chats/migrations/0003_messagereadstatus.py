# Generated by Django 4.2.4 on 2023-11-14 15:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0002_conversation_is_group'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageReadStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_read', models.BooleanField(default=False)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='read_status', to='chats.message')),
                ('recipientProfile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chats.profile')),
            ],
            options={
                'unique_together': {('recipientProfile', 'message')},
            },
        ),
    ]
