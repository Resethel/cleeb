# Generated by Django 5.0.2 on 2024-04-18 08:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(help_text='Name of the sender.', max_length=100, verbose_name='Name')),
                ('email', models.EmailField(help_text='Email address of the sender.', max_length=254, verbose_name='Email')),
                ('subject', models.CharField(help_text='Subject of the message.', max_length=100, verbose_name='Subject')),
                ('message', models.TextField(help_text='Content of the message.', verbose_name='Message')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Date and time when the message was created.', verbose_name='Created at')),
                ('handled', models.BooleanField(default=False, help_text='Flag to indicate if the message was handled by the team.', verbose_name='Handled')),
            ],
            options={
                'verbose_name': 'Contact Message',
                'verbose_name_plural': 'Contact Messages',
            },
        ),
    ]
