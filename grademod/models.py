from django.db import models

# Create your models here.
class SchoolGroup(models.Model):
    Group_ID = models.AutoField(primary_key = True, unique=True)
    GroupName = models.TextField()
    class Meta:
        db_table = 'SchoolGroup'

class SchoolType(models.Model):
    Type_ID = models.IntegerField(primary_key = True, null = False)
    TypeName = models.TextField()
    Group_ID = models.ForeignKey(SchoolGroup, on_delete = models.SET_NULL, null = True, db_column='Group_ID', related_name='schoolList')
    class Meta:
        db_table = 'SchoolType'

class School(models.Model):
    School_ID = models.IntegerField(primary_key = True, null = False)
    SchoolName = models.TextField()
    SchoolProvince = models.TextField()
    Type_ID = models.ForeignKey(SchoolType, on_delete = models.PROTECT, null = True, db_column='Type_ID',related_name='schoolName')
    class Meta:
        db_table = 'School'

class StudentStatus(models.Model):
    Status_ID = models.IntegerField(primary_key = True, null = False)
    StatusName = models.TextField(null = False)
    class Meta:
        db_table = 'StudentStatus'

class EntranceStatus(models.Model):
    Entrance_ID = models.IntegerField(primary_key = True, null = False)
    EntranceName = models.TextField(null = False)
    class Meta:
        db_table = 'EntranceStatus'

class Student(models.Model):
    Student_ID = models.TextField(primary_key = True, null = False)
    TH_fName = models.TextField()
    TH_sName = models.TextField()
    EN_fName = models.TextField()
    EN_sName = models.TextField()
    AdmitAcademicYear = models.IntegerField(null = False)
    ProgramName = models.TextField(null = False)
    OldGPA = models.FloatField(null = False)
    School_ID = models.ForeignKey(School, on_delete = models.PROTECT, null = True, db_column='School_ID',related_name='schoolName')
    Status_ID = models.ForeignKey(StudentStatus, on_delete = models.PROTECT, null = False, db_column='Status_ID')
    Entrance_ID = models.ForeignKey(EntranceStatus, on_delete = models.PROTECT, null = False, db_column='Entrance_ID')
    class Meta:
        db_table = 'Student'

class AcademicSemester(models.Model):
    Year_ID = models.IntegerField(primary_key = True, unique=True)
    AcademicYear = models.IntegerField(null = False)
    Semester = models.IntegerField(null = False)
    class Meta:
        db_table = 'AcademicSemester'

class Grade(models.Model):
    Student_ID = models.ForeignKey(Student, primary_key=True, on_delete = models.PROTECT, null = False, db_column='Student_ID')
    Year_ID = models.ForeignKey(AcademicSemester, on_delete=models.CASCADE, to_field='Year_ID', db_column='Year_ID')
    GPA = models.FloatField(null = False)
    GPAX = models.FloatField(null = False)
    class Meta:
        unique_together = ('Student_ID','Year_ID')
        db_table = 'Grade'

class Course(models.Model):
    Course_ID = models.IntegerField(primary_key = True, null = False)
    CourseCode = models.TextField(null = False)
    CourseName = models.TextField(null = False)
    Credit = models.IntegerField(null = False)
    class Meta:
        db_table = 'Course'

class Enroll(models.Model):
    Student_ID = models.ForeignKey(Student, primary_key=True, on_delete = models.PROTECT, null = False, db_column='Student_ID')
    Course_ID = models.ForeignKey(Course, on_delete = models.PROTECT, null = False, db_column='Course_ID')
    Year_ID = models.ForeignKey(AcademicSemester, on_delete = models.CASCADE, null = False, db_column='Year_ID', to_field='Year_ID')
    Grade = models.TextField(null = False)
    class Meta:
        unique_together = ('Student_ID','Course_ID','Year_ID')   
        db_table = 'Enroll'
        auto_created = False