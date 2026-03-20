from django.db import migrations

def apply_stats_fix(apps, schema_editor):
    from apps.analytics.models import UserStat
    from django.contrib.auth import get_user_model
    User = get_user_model()
    for user in User.objects.all():
        try:
            UserStat.refresh_for_user(user)
        except Exception:
            pass

class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0003_quizstat'),
    ]

    operations = [
        migrations.RunPython(apply_stats_fix),
    ]
