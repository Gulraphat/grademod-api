# Generated by Django 4.1.7 on 2023-05-15 16:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AcademicSemester',
            fields=[
                ('Year_ID', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('AcademicYear', models.IntegerField()),
                ('Semester', models.IntegerField()),
            ],
            options={
                'db_table': 'AcademicSemester',
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('Course_ID', models.IntegerField(primary_key=True, serialize=False)),
                ('CourseCode', models.TextField()),
                ('CourseName', models.TextField()),
                ('Credit', models.IntegerField()),
            ],
            options={
                'db_table': 'Course',
            },
        ),
        migrations.CreateModel(
            name='EntranceStatus',
            fields=[
                ('Entrance_ID', models.IntegerField(primary_key=True, serialize=False)),
                ('EntranceName', models.TextField()),
            ],
            options={
                'db_table': 'EntranceStatus',
            },
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('School_ID', models.IntegerField(primary_key=True, serialize=False)),
                ('SchoolName', models.TextField()),
                ('SchoolProvince', models.TextField()),
            ],
            options={
                'db_table': 'School',
            },
        ),
        migrations.CreateModel(
            name='SchoolGroup',
            fields=[
                ('Group_ID', models.IntegerField(primary_key=True, serialize=False)),
                ('GroupName', models.TextField()),
            ],
            options={
                'db_table': 'SchoolGroup',
            },
        ),
        migrations.CreateModel(
            name='StudentStatus',
            fields=[
                ('Status_ID', models.IntegerField(primary_key=True, serialize=False)),
                ('StatusName', models.TextField()),
            ],
            options={
                'db_table': 'StudentStatus',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('Student_ID', models.TextField(primary_key=True, serialize=False)),
                ('TH_fName', models.TextField()),
                ('TH_sName', models.TextField()),
                ('EN_fName', models.TextField()),
                ('EN_sName', models.TextField()),
                ('AdmitAcademicYear', models.IntegerField()),
                ('ProgramName', models.TextField()),
                ('OldGPA', models.FloatField()),
                ('Entrance_ID', models.ForeignKey(db_column='Entrance_ID', on_delete=django.db.models.deletion.PROTECT, to='grademod.entrancestatus')),
                ('School_ID', models.ForeignKey(db_column='School_ID', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='schoolName', to='grademod.school')),
                ('Status_ID', models.ForeignKey(db_column='Status_ID', on_delete=django.db.models.deletion.PROTECT, to='grademod.studentstatus')),
            ],
            options={
                'db_table': 'Student',
            },
        ),
        migrations.CreateModel(
            name='SchoolType',
            fields=[
                ('Type_ID', models.IntegerField(primary_key=True, serialize=False)),
                ('TypeName', models.TextField()),
                ('Group_ID', models.ForeignKey(db_column='Group_ID', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='schoolList', to='grademod.schoolgroup')),
            ],
            options={
                'db_table': 'SchoolType',
            },
        ),
        migrations.AddField(
            model_name='school',
            name='Type_ID',
            field=models.ForeignKey(db_column='Type_ID', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='schoolName', to='grademod.schooltype'),
        ),
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('Student_ID', models.ForeignKey(db_column='Student_ID', on_delete=django.db.models.deletion.PROTECT, primary_key=True, serialize=False, to='grademod.student')),
                ('GPA', models.FloatField()),
                ('GPAX', models.FloatField()),
                ('Year_ID', models.ForeignKey(db_column='Year_ID', on_delete=django.db.models.deletion.CASCADE, to='grademod.academicsemester')),
            ],
            options={
                'db_table': 'Grade',
                'unique_together': {('Student_ID', 'Year_ID')},
            },
        ),
        migrations.CreateModel(
            name='Enroll',
            fields=[
                ('Student_ID', models.ForeignKey(db_column='Student_ID', on_delete=django.db.models.deletion.PROTECT, primary_key=True, serialize=False, to='grademod.student')),
                ('Grade', models.TextField()),
                ('Course_ID', models.ForeignKey(db_column='Course_ID', on_delete=django.db.models.deletion.PROTECT, to='grademod.course')),
                ('Year_ID', models.ForeignKey(db_column='Year_ID', on_delete=django.db.models.deletion.CASCADE, to='grademod.academicsemester')),
            ],
            options={
                'db_table': 'Enroll',
                'auto_created': False,
                'unique_together': {('Student_ID', 'Course_ID', 'Year_ID')},
            },
        ),
    ]
