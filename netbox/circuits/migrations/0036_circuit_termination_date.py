# Generated by Django 4.0.5 on 2022-06-22 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('circuits', '0035_provider_asns'),
    ]

    operations = [
        migrations.AddField(
            model_name='circuit',
            name='termination_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
