from django.db.models import Count
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.views.generic import View
from django.http import HttpResponse
from django.db import transaction
from .models import *
from .serializers import *
from .ImportFile import readFile
from Backend.utils import *
import io, sqlite3

class AuthenticatedAPIView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        uid = request.META.get('HTTP_UID')
        response = authenticate_user(uid)
        if response.status_code != 200:
            return response
        return super().get(request, *args, **kwargs)

class ImportFileView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print('getting request')
        for key in request.data:
            print('key', key)
            print('data', request.data[key])
        if 'file' not in request.data:
            return Response({'message': 'No file found'}, status=status.HTTP_400_BAD_REQUEST)
        file = request.data['file']
        readFile(file)
        return Response({'message': 'Import File Successfully'}, status=status.HTTP_200_OK)    

class SchoolGroupList(AuthenticatedAPIView, generics.ListCreateAPIView):
    queryset = SchoolGroup.objects.all()
    serializer_class = SchoolGroupSerializer
    permission_classes = [AllowAny]

class SchoolGroupDetail(AuthenticatedAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = SchoolGroup.objects.all()
    serializer_class = SchoolGroupSerializer
    permission_classes = [AllowAny]

class SchoolTypeList(AuthenticatedAPIView, generics.ListCreateAPIView):
    queryset = SchoolType.objects.all()
    serializer_class = SchoolTypeSerializer
    permission_classes = [AllowAny]

class SchoolTypeDetail(AuthenticatedAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = SchoolType.objects.all()
    serializer_class = SchoolTypeSerializer
    permission_classes = [AllowAny]

class SchoolList(AuthenticatedAPIView, generics.ListCreateAPIView):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer

class SchoolDetail(AuthenticatedAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer

class StudentStatusList(AuthenticatedAPIView, generics.ListCreateAPIView):
    queryset = StudentStatus.objects.all()
    serializer_class = StudentStatusSerializer

class StudentStatusDetail(AuthenticatedAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentStatus.objects.all()
    serializer_class = StudentStatusSerializer

class EntranceStatusList(AuthenticatedAPIView, generics.ListCreateAPIView):
    queryset = EntranceStatus.objects.all()
    serializer_class = EntranceStatusSerializer

class EntranceStatusDetail(AuthenticatedAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = EntranceStatus.objects.all()
    serializer_class = EntranceStatusSerializer

class StudentList(AuthenticatedAPIView, generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class StudentDetail(AuthenticatedAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class AcademicSemesterList(AuthenticatedAPIView, generics.ListCreateAPIView):
    queryset = AcademicSemester.objects.all()
    serializer_class = AcademicSemesterSerializer

class AcademicSemesterDetail(AuthenticatedAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = AcademicSemester.objects.all()
    serializer_class = AcademicSemesterSerializer

class GradeList(AuthenticatedAPIView, generics.ListCreateAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer

class GradeDetail(AuthenticatedAPIView, generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'pk1','pk2'
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer

    def get_object(self):
        pk1 = self.kwargs.get('pk1')
        pk2 = self.kwargs.get('pk2')
        return Grade.objects.get(Student_ID = pk1, Year_ID = pk2)

class CourseList(AuthenticatedAPIView, generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class CourseDetail(AuthenticatedAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class EnrollList(AuthenticatedAPIView, generics.ListCreateAPIView):
    queryset = Enroll.objects.all()
    serializer_class = EnrollSerializer

class EnrollDetail(AuthenticatedAPIView, generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'pk1','pk2','pk3'
    queryset = Enroll.objects.all()
    serializer_class = EnrollSerializer

    def get_object(self):
        pk1 = self.kwargs.get('pk1')
        pk2 = self.kwargs.get('pk2')
        pk3 = self.kwargs.get('pk3')
        return Enroll.objects.get(Student_ID=pk1, Course_ID=pk2, Year_ID=pk3)

class EnrollByID(AuthenticatedAPIView, generics.ListAPIView):
    serializer_class = EnrollByIDSerializer

    def get_queryset(self):
        student_id = self.kwargs.get('id')
        year_id = self.kwargs.get('yr')
        return Enroll.objects.filter(Student_ID = student_id, Year_ID = year_id).values('Student_ID','Course_ID','Grade','Year_ID')

class AdmitData(AuthenticatedAPIView, generics.ListAPIView):
    queryset = Student.objects.values('AdmitAcademicYear').annotate(total_students = Count('Student_ID')).order_by('AdmitAcademicYear')
    serializer_class = AdmitDataSerializer

class AdmitAcademicYear(AuthenticatedAPIView, generics.ListAPIView):
    queryset = Student.objects.values('AdmitAcademicYear').distinct()
    serializer_class = AdmitAcademicYearSerializer

class ProgramName(AuthenticatedAPIView, generics.ListAPIView):
    queryset = Student.objects.values('ProgramName').distinct()
    serializer_class = ProgramSerializer

class TotalAdmitBySchool(AuthenticatedAPIView, generics.ListAPIView):
    # get total admit by school group
    queryset = Student.objects.values('School_ID__Type_ID__TypeName').annotate(total_students = Count('Student_ID')).order_by('School_ID__Type_ID__TypeName').distinct()
    serializer_class  = TotalAdmitBySchoolSerializer

class TotalAdmitBySchoolName(AuthenticatedAPIView, generics.ListAPIView):
    # get total admit by school name
    queryset = Student.objects.values('School_ID').annotate(total_students = Count('Student_ID')).order_by('School_ID').distinct()
    serializer_class = TotalAdmitBySchoolNameSerializer

class SchoolByProv(AuthenticatedAPIView, generics.ListAPIView):
    queryset = School.objects.all().order_by('SchoolProvince')
    serializer_class = SchoolSerializer

class TotalByProv(AuthenticatedAPIView, generics.ListAPIView):
    queryset = Student.objects.values('School_ID__SchoolProvince').annotate(total_students = Count('Student_ID')).order_by('School_ID__SchoolProvince').distinct()
    serializer_class = TotalByProvSerializer

class AdmitBySchoolYear(AuthenticatedAPIView, generics.ListAPIView):
    queryset = Student.objects.all()
    serializer_class = AdmitBySchoolYearSerializer

    def get(self, request, *args, **kwargs):
        uid = request.META.get('HTTP_UID')
        response = authenticate_user(uid)
        if response.status_code != 200:
            return response
        queryset = Student.objects.select_related('School_ID__Type_ID__Group_ID', 'AdmitAcademicYear').prefetch_related('School_ID__Type_ID').values('AdmitAcademicYear', 'School_ID__Type_ID__Group_ID').annotate(total_students=Count('Student_ID'))
        yearGroup = {}
        for item in queryset:
            year = item['AdmitAcademicYear']
            groupName = item ['School_ID__Type_ID__Group_ID']
            total_students = item['total_students']
            if year not in yearGroup:
                yearGroup[year] = {}
            yearGroup[year][groupName] = total_students
        response_data = []
        for year, groups in yearGroup.items():
            response_data.append({'AdmitAcademicYear': year, 'schoolGroup' : groups})
        return Response(response_data)

class CompleteStudentData(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        uid = request.META.get('HTTP_UID')
        response = authenticate_user(uid)
        if response.status_code != 200:
            return response
        
        # ดึงข้อมูลจาก model
        students = pd.DataFrame.from_records(Student.objects.all().values())
        schools = pd.DataFrame.from_records(School.objects.all().values())
        statuses = pd.DataFrame.from_records(StudentStatus.objects.all().values())
        types = pd.DataFrame.from_records(SchoolType.objects.all().values())
        groups = pd.DataFrame.from_records(SchoolGroup.objects.all().values())
        entrances = pd.DataFrame.from_records(EntranceStatus.objects.all().values())

        # เปลี่ยนชื่อ key ให้ตรงกับชื่อคอลัมน์
        students = students.rename(columns={'School_ID_id': 'School_ID', 'Status_ID_id': 'Status_ID', 'Entrance_ID_id': 'Entrance_ID'})
        schools = schools.rename(columns={'Type_ID_id': 'Type_ID'})
        types = types.rename(columns={'Group_ID_id': 'Group_ID'})
        entrances = entrances.rename(columns={'Entrance_ID_id': 'Entrance_ID'})

        # fillna
        students = students.fillna(0)

        # รวมข้อมูล
        merged_data = pd.merge(students, schools, on='School_ID', how='left')
        merged_data = pd.merge(merged_data, statuses, on='Status_ID', how='left')
        merged_data = pd.merge(merged_data, types, on='Type_ID', how='left')
        merged_data = pd.merge(merged_data, groups, on='Group_ID', how='left')
        merged_data = pd.merge(merged_data, entrances, on='Entrance_ID', how='left')
        merged_data = merged_data.fillna(0)

        merged_data["School_ID"] = merged_data["School_ID"].astype('Int64')
        merged_data["Type_ID"] = merged_data["Type_ID"].astype('Int64')
        merged_data["Group_ID"] = merged_data["Group_ID"].astype('Int64')
        merged_data["Entrance_ID"] = merged_data["Entrance_ID"].astype('Int64')

        order_columns = [
            'Student_ID',
            'TH_fName',
            'TH_sName',
            'EN_fName',
            'EN_sName',
            'AdmitAcademicYear',
            'OldGPA',
            'Entrance_ID',
            'EntranceName',
            'ProgramName',
            "Status_ID",
            "StatusName",
            'School_ID',
            'SchoolName',
            'SchoolProvince',
            "Type_ID",
            "TypeName",
            "Group_ID",
            "GroupName",
        ]

        merged_data = merged_data.reindex(order_columns, axis=1)

        # API response
        response = merged_data.to_dict(orient='records')

        return Response(response)

# class CompleteStudentDetail(generics.ListAPIView):

class ExportExcelView(View):
    permission_classes = [AllowAny]
    def get(self, request, *args, **kwargs):
        # get info_df
        info_data = Student.objects.select_related('School_ID', 'Status_ID', 'Entrance_ID').values(
        'Student_ID', 'TH_fName', 'TH_sName', 'EN_fName', 'EN_sName', 'AdmitAcademicYear', 'ProgramName', 'OldGPA',
        'School_ID__SchoolName', 'Status_ID__StatusName', 'Entrance_ID__EntranceName'
        )
        info_df = pd.DataFrame(info_data)
        info_df = info_df.rename(columns={'Status_ID__StatusName': 'StudentStatus','Entrance_ID__EntranceName': 'EntranceStatus',
                                'School_ID__SchoolName':'SchoolName'})
        info_df = info_df.reindex(columns=['Student_ID', 'TH_fName', 'TH_sName', 'EN_fName', 'EN_sName', 'AdmitAcademicYear', 'ProgramName',
                                'StudentStatus', 'EntranceStatus', 'SchoolName', 'OldGPA'])

        grade_data = Grade.objects.select_related('Student_ID', 'Year_ID').prefetch_related(
            'Student_ID__Enroll_set', 'Student_ID__Enroll_set__Course_ID'
        ).values(
            'Student_ID', 'Year_ID__Year_ID', 'Year_ID__AcademicYear', 'Year_ID__Semester', 'GPA', 'GPAX'
        )
        tempgrade_df = pd.DataFrame(grade_data)

        enroll_data = Enroll.objects.select_related('Course_ID').values(
            'Student_ID', 'Course_ID', 'Course_ID__CourseCode', 'Course_ID__CourseName', 'Course_ID__Credit', 'Year_ID__Year_ID',
            'Year_ID__AcademicYear', 'Year_ID__Semester', 'Grade'
        )
        enroll_df = pd.DataFrame(enroll_data)
        course_df = pd.DataFrame(Course.objects.values('Course_ID', 'CourseCode', 'CourseName', 'Credit'))

        # map grade_df with all related values
        grade_df = pd.merge(tempgrade_df, enroll_df, on=['Student_ID', 'Year_ID__Year_ID', 'Year_ID__AcademicYear', 'Year_ID__Semester'], how='left')
        grade_df = pd.merge(grade_df,course_df, on='Course_ID', how='left')
        grade_df = grade_df.drop(['Year_ID__Year_ID','Course_ID','Course_ID__CourseCode','Course_ID__CourseName','Course_ID__Credit'], axis=1)
        grade_df = grade_df.rename(columns={'Year_ID__AcademicYear':'AcademicYear','Year_ID__Semester':'Semester'})
        grade_df = grade_df.reindex(columns=['Student_ID','AcademicYear','Semester','CourseCode','CourseName','Grade','Credit','GPA','GPAX'])

        # create excel file and response
        excelFile = io.BytesIO()
        writer = pd.ExcelWriter(excelFile, engine='xlsxwriter')
        info_df.to_excel(writer, sheet_name='Info', index=False)
        grade_df.to_excel(writer, sheet_name='Grade', index=False)
        writer.save()

        # create response by sending file back as form data
        response = HttpResponse(excelFile.getvalue(), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="CPE_dataFile.xlsx"'

        return response

class ClearDataView(APIView):
    permission_classes = [AllowAny]
    #@transaction.atomic
    def delete(self,request):
        with transaction.atomic():  
            conn = sqlite3.connect('studentSheet.db')
            cursor = conn.cursor() 
            cursor.execute('DELETE FROM Enroll')
            cursor.execute('DELETE FROM Grade')
            cursor.execute('DELETE FROM Student')
            cursor.execute('DELETE FROM School')
            cursor.execute('DELETE FROM AcademicSemester')
            conn.commit()
            conn.close()
        return Response({'message': 'All records deleted.'})


class EnrollCourse(APIView):
    permission_classes = [AllowAny]

    def get(self, request, id):
        uid = request.META.get('HTTP_UID')
        response = authenticate_user(uid)
        if response.status_code != 200:
            return response

        # get student
        filter_Enroll = Enroll.objects.filter(Student_ID = id).values()

        if filter_Enroll.exists():
            enrolls = pd.DataFrame.from_records(filter_Enroll)
            courses = pd.DataFrame.from_records(Course.objects.all().values())
            
            enrolls = enrolls.rename(columns={'Course_ID_id':'Course_ID'})
            enrolls = enrolls.rename(columns={'Student_ID_id':'Student_ID'})
            enrolls = enrolls.rename(columns={'Year_ID_id':'Year_ID'})
            courses = courses.rename(columns={'Course_ID_id':'Course_ID'})

            # merge enroll and course
            merged_data = pd.merge(enrolls, courses, on='Course_ID', how='left')
            merged_data = merged_data.reindex(columns=['Course_ID','CourseCode','CourseName','Credit','Year_ID','Grade'])

            # API response
            response = merged_data.to_dict(orient='records')
            return Response(response)

        else:
            return Response({'message': 'No records.'})


class GradeByStudent(APIView):
    permission_classes = [AllowAny]

    def get(self, request, id):
        uid = request.META.get('HTTP_UID')
        response = authenticate_user(uid)
        if response.status_code != 200:
            return response

        # get studentabs
        filter_Grade = Grade.objects.filter(Student_ID = id).values()

        if filter_Grade.exists():
            grades = pd.DataFrame.from_records(filter_Grade)
            years = pd.DataFrame.from_records(AcademicSemester.objects.all().values())

            grades = grades.rename(columns={'Student_ID_id':'Student_ID'})
            grades = grades.rename(columns={'Year_ID_id':'Year_ID'})

            # merge enroll and course
            merged_data = pd.merge(grades, years, on='Year_ID', how='left')
            
            print(merged_data)

            # API response
            response = merged_data.to_dict(orient='records')
            return Response(response)

        else:
            return Response({'message': 'No records.'})
