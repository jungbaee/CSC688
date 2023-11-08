# Generated by Django 4.2.3 on 2023-08-19 02:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("main", "0011_remove_quizresult_timestamp"),
    ]

    operations = [
        migrations.AddField(
            model_name="quizresult",
            name="score_percentage",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AlterField(
            model_name="quizresult",
            name="correct_answers",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="quizresult",
            name="incorrect_answers",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="quizresult",
            name="total_questions",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="quizresult",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
    ]