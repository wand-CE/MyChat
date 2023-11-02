# Generated by Django 4.2.4 on 2023-10-29 05:38

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0010_remove_message_is_read_remove_message_recipient'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
    ]