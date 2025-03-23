# Generated by Django 5.1.7 on 2025-03-23 16:21

import cloudinary.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('os_project', '0003_migrate_user_data'),
        ('user_profile', '0004_remove_os_maintainer_favourite_projects_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Milestone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('target_date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('locked', models.BooleanField(default=False)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='milestones', to='os_project.project')),
            ],
        ),
        migrations.CreateModel(
            name='MilestoneGoal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('NOT_STARTED', 'Not Started'), ('IN_PROGRESS', 'In Progress'), ('READY_FOR_REVIEW', 'Ready for Review'), ('COMPLETED', 'Completed')], default='NOT_STARTED', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('evidence_link', models.URLField(blank=True, null=True)),
                ('evidence_image', cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='evidence_image')),
                ('milestone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='goals', to='os_project.milestone')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectMentor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expertise_areas', models.CharField(blank=True, max_length=200)),
                ('availability', models.CharField(blank=True, max_length=200)),
                ('notes', models.TextField(blank=True)),
                ('mentor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mentored_projects', to='user_profile.mentor')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mentors', to='os_project.project')),
            ],
            options={
                'unique_together': {('project', 'mentor')},
            },
        ),
    ]
