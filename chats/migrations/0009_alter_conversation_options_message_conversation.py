# Generated by Django 4.2.4 on 2023-10-27 20:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0008_alter_profile_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='conversation',
            options={'verbose_name': 'Conversation', 'verbose_name_plural': 'Conversations'},
        ),
        migrations.AddField(
            model_name='message',
            name='conversation',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chats.conversation'),
            preserve_default=False,
        ),
    ]
