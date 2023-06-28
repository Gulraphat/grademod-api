from rest_framework import serializers
from .models import *
from Backend.utils import *

class SchoolTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolType
        fields = ['Type_ID','TypeName','Group_ID']

class SchoolGroupSerializer(serializers.ModelSerializer):
    schoolList = SchoolTypeSerializer(many=True, read_only=True)
    class Meta:
        model = SchoolGroup
        fields = ['Group_ID','GroupName','schoolList']

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'

class StudentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentStatus
        fields = '__all__'

class EntranceStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntranceStatus
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class AcademicSemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicSemester
        fields = '__all__'

class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class EnrollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enroll
        fields = '__all__'

class EnrollByIDSerializer(serializers.Serializer):
    Student_ID = serializers.CharField()
    Course_ID = serializers.IntegerField()
    Grade = serializers.CharField()
    Year_ID = serializers.IntegerField()
    class Meta:
        model = Enroll
        fields = '__all__'

class AdmitDataSerializer(serializers.Serializer):
    AdmitAcademicYear = serializers.IntegerField()
    total_students = serializers.IntegerField()

class AdmitAcademicYearSerializer(serializers.Serializer):
    AdmitAcademicYear = serializers.IntegerField()

class ProgramSerializer(serializers.Serializer):
    ProgramName = serializers.CharField()

class TotalAdmitBySchoolSerializer(serializers.Serializer):
    TypeName = serializers.CharField(source = 'School_ID__Type_ID__TypeName')
    total_students = serializers.IntegerField()
    
class TotalAdmitBySchoolNameSerializer(serializers.Serializer):
    School_ID = serializers.IntegerField()
    total_students = serializers.IntegerField()

class AdmitBySchoolYearSerializer(serializers.Serializer):
    AdmitAcademicYear = serializers.IntegerField()
    schoolGroup = serializers.CharField(source = 'School_ID__Type_ID__Group_ID')
    total_students = serializers.IntegerField()
    GroupName = serializers.CharField(source = 'School_ID__Type_ID__Group_ID__GroupName')

class TotalByProvSerializer(serializers.Serializer):
    SchoolProvince = serializers.CharField(source = 'School_ID__SchoolProvince')
    total_students = serializers.IntegerField()