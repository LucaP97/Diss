# Generated by Django 4.2.1 on 2023-07-04 13:44

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SearchData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Tweets',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Text', models.CharField(max_length=400)),
                ('created_at', models.DateTimeField()),
                ('retweet_count', models.IntegerField()),
                ('favorite_count', models.IntegerField()),
                ('tweet_url', models.URLField()),
                ('media_urls', jsonfield.fields.JSONField()),
                ('included_urls', jsonfield.fields.JSONField()),
                ('place', models.CharField(blank=True, max_length=200, null=True)),
                ('sentiment', models.CharField(max_length=50)),
                ('sentiment_scores', jsonfield.fields.JSONField()),
                ('key_phrases', jsonfield.fields.JSONField()),
                ('entities', jsonfield.fields.JSONField()),
            ],
        ),
    ]