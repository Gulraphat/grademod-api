"""Backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from grademod.views import *
from model.views import *
from honor.views import *

urlpatterns =[
    path('importFile/', ImportFileView.as_view(), name='import-file'),
    path('exportExcel/', ExportExcelView.as_view(), name='export-excel'),
    path('clearData/', ClearDataView.as_view(), name='delete-all-data'),

    path('studentStatus/', StudentStatusList.as_view(), name='studentStatus-list'),
    path('studentStatus/<int:pk>/', StudentStatusDetail.as_view(), name='studentStatus-detail'),
    path('entranceStatus/', EntranceStatusList.as_view(), name='entranceStatus-list'),
    path('entranceStatus/<int:pk>/', EntranceStatusDetail.as_view(), name='entranceStatus-detail'),
    path('student/', StudentList.as_view(), name='student-list'),
    path('student/<int:pk>/', StudentDetail.as_view(), name='student-detail'),
    path('academicSemester/', AcademicSemesterList.as_view(), name='academicSemester-list'),
    path('academicSemester/<int:pk>/', AcademicSemesterDetail.as_view(), name='academicSemester-detail'),
    path('grade/', GradeList.as_view(), name='grade-list'),
    path('grade/<str:pk1>/<int:pk2>/', GradeDetail.as_view(), name='grade-detail'),
    path('course/', CourseList.as_view(), name='course-list'),
    path('course/<int:pk>/', CourseDetail.as_view(), name='course-detail'),
    path('enroll/', EnrollList.as_view(), name='enroll-list'),
    path('enroll/<str:pk1>/<int:pk2>/<int:pk3>/', EnrollDetail.as_view(), name='enroll-detail'),
    path('enroll/<str:id>/<int:yr>', EnrollByID.as_view(),name='enroll-by-id'),
    path('schoolGroup/', SchoolGroupList.as_view(), name='schoolGroup-list'),
    path('schoolGroup/<int:pk>/', SchoolGroupDetail.as_view(), name='schoolGroup-detail'),
    path('schoolType/', SchoolTypeList.as_view(), name='schoolType-list'),
    path('schoolType/<int:pk>/', SchoolTypeDetail.as_view(), name='schoolType-detail'),
    path('school/', SchoolList.as_view(), name='school-list'),
    path('school/<int:pk>/', SchoolDetail.as_view(), name='school-detail'),
    path('admitData/', AdmitData.as_view(), name='admit-data'),
    path('admitAcademicYear/', AdmitAcademicYear.as_view(), name='admit-year'),
    path('programName/', ProgramName.as_view(), name='program-name'),
    path('totalAdmitbySchool/', TotalAdmitBySchool.as_view(), name='total-admit-by-school'),
    path('schoolByProv/', SchoolByProv.as_view(), name='school-by-prov'),
    path('admitBySchoolYear/', AdmitBySchoolYear.as_view(), name='admit-school-year'),

    path('completeStudent/', CompleteStudentData.as_view(), name='complete-student'),
    path('enrollCourse/<str:id>/', EnrollCourse.as_view(), name='enroll-course'),
    path('grade/<str:id>/', GradeByStudent.as_view(), name='grade-by-student'),

    # เริ่มต้นของหมิว
    path('predict1_1/', Prediction1_1.as_view(), name='predict1_1'),
    path('schoolStat/', schoolStat.as_view(), name='schoolStatistic'), 
    path('schoolHonorStat/', schoolHonorStat.as_view(), name='schoolHonorStatistic'),
    path('schoolGroupStat/', schoolGroupStat.as_view(), name='schoolGroupStatistic'),
    path('programStat/', ProgramStat.as_view(), name='programStatistic'),
    path('programHonorStat/', ProgramHonorStat.as_view(), name='programHonorStatistic'),
    path('honorByAcademicYear/', HonorByAcademicYear.as_view(), name='programStatisticByAcademicYear'),
    path('honorByYearAndGroup/', HonorByYearAndGroup.as_view(), name='honorByYearAndGroup'),
    path('honorByYear/', HonorByYear.as_view(), name='honorByYear'),
    path('probationByYear/', ProbationByYear.as_view(), name='probationByYear'),

    # เริ่มต้นของจีน
    path('GPAX1_1/<int:academic_year>', GPAX1_1_by_year().as_view(), name='GPAX Year 1 Semester 1'),
    path('lastestAcademicYear/', LastestAcademicYear.as_view(), name='lastestAcademicYear'),
    path('predictionData/', PredictionData.as_view(), name='predictionData'),
    path('predictionData/<str:mode>', PredictionDataByMode.as_view(), name='predictionDataByYear'),
    path('totalByProvince/', TotalByProv.as_view(), name='totalByProvince'),
    path('totalBySchool/', TotalAdmitBySchoolName.as_view(), name='totalBySchool'),
]

