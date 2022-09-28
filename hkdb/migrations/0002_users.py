from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [('hkdb', '0001_initial')]

    operations = [
        migrations.CreateModel(
            name='tg_users',
            fields=[
                ( 'id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ( 'tg_id', models.TextField(editable=True, verbose_name=b'ID from Telegram')),
            ],
        ),
        migrations.CreateModel(
            name='tg_admins',
            fields=[
                ( 'id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ( 'user', models.ForeignKey('hkdb.tg_users', on_delete=models.CASCADE) ),
            ],
        ),
        migrations.CreateModel(
            name='tg_requests',
            fields=[
                ( 'id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ( 'tg_id', models.TextField(editable=True, verbose_name=b'ID from Telegram'))
            ],
        ),
    ]