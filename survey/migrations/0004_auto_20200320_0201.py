# Generated by Django 2.2.11 on 2020-03-19 23:01

from django.db import migrations, models
import survey.validators


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0003_auto_20200320_0026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='choice',
            name='text',
            field=models.CharField(max_length=255, validators=[survey.validators.validate_especial_charachters]),
        ),
        migrations.AlterField(
            model_name='question',
            name='note',
            field=models.TextField(blank=True, help_text='Any notes/remarks you want to add to the question (optional)', validators=[survey.validators.validate_especial_charachters]),
        ),
        migrations.AlterField(
            model_name='question',
            name='text',
            field=models.TextField(validators=[survey.validators.validate_especial_charachters], verbose_name='question text'),
        ),
    ]