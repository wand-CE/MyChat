# Generated by Django 4.2.4 on 2023-10-29 05:41

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0011_conversation_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conversation',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]