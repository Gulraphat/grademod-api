from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import pandas as pd
import requests # ใช้สำหรับเรียกใช้ API ติดตั้ง pip install requests
from grademod.models import *
from Backend.utils import *

from firebase_admin import db
import joblib

def allStudentData():    
    # ดึงข้อมูลจาก model
    students = pd.DataFrame.from_records(Student.objects.all().values())
    schools = pd.DataFrame.from_records(School.objects.all().values())
    statuses = pd.DataFrame.from_records(StudentStatus.objects.all().values())
    types = pd.DataFrame.from_records(SchoolType.objects.all().values())
    groups = pd.DataFrame.from_records(SchoolGroup.objects.all().values())

    # เปลี่ยนชื่อ key ให้ตรงกับชื่อคอลัมน์
    students = students.rename(columns={'School_ID_id': 'School_ID', 'Status_ID_id': 'Status_ID'})
    schools = schools.rename(columns={'Type_ID_id': 'Type_ID'})
    types = types.rename(columns={'Group_ID_id': 'Group_ID'})

    # fillna
    students = students.fillna(0)

    # รวมข้อมูล
    merged_data = pd.merge(students, schools, on='School_ID', how='left')
    merged_data = pd.merge(merged_data, statuses, on='Status_ID', how='left')
    merged_data = pd.merge(merged_data, types, on='Type_ID', how='left')
    merged_data = pd.merge(merged_data, groups, on='Group_ID', how='left')
    # merged_data = merged_data.fillna(0)

    students = merged_data[['Student_ID', 'SchoolName', 'TypeName', 'GroupName', 'StatusName', 'AdmitAcademicYear', 'ProgramName', 'OldGPA']]
    students = students.fillna('ไม่มีข้อมูล')

    GPAXQuery = Grade.objects.select_related('Student_ID', 'Student_ID__Status_ID').values('Student_ID', 'Student_ID__Status_ID__StatusName', 'Year_ID', 'Year_ID__AcademicYear', 'Year_ID__Semester', 'GPAX')
    gpaDf = pd.DataFrame(GPAXQuery)

    # เปลี่ยนชื่อคอลัมน์
    gpaDf = gpaDf.rename(columns={'Student_ID__Status_ID__StatusName': 'StatusName',
                                      'Year_ID__AcademicYear': 'AcademicYear',
                                      'Year_ID__Semester': 'Semester'})

    # เปลี่ยนชื่อหลักสูตรเป็นตัวย่อ
    students = students.replace({'ProgramName' :
                              {'วิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมคอมพิวเตอร์ ปริญญาตรี 4 ปี' : 'CPE',
                              'วิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมคอมพิวเตอร์ ปริญญาตรี 4 ปี  (หลักสูตรนานาชาติ)' : 'CPE inter',
                              'หลักสูตรวิทยาศาสตรบัณฑิต สาขาวิชาวิทยาศาสตร์ข้อมูลสุขภาพ ปริญญาตรี 4 ปี' : 'CPE HDS',
                              'หลักสูตรวิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมคอมพิวเตอร์ ปริญญาตรี 4 ปี (โครงการจากพื้นที่การศึกษาราชบุรี)' : 'CPE RC'}
                              })

    # แยกข้อมูลลการเรียนปีสุดท้ายของนักศึกษาที่สำเร็จการศึกษา
    gradStudent = students[students['StatusName'] == 'สำเร็จการศึกษา']
    gradGPA = gpaDf[gpaDf['Student_ID'].isin(gradStudent['Student_ID'])]
    gradGPA = gradGPA.sort_values(['Student_ID','Year_ID']).reset_index()
    grad_GPAX = []
    for index,row in gradStudent.iterrows():
        if row.StatusName == 'สำเร็จการศึกษา':
            current_student = gradGPA[gradGPA.Student_ID.isin([row.Student_ID])]
            if len(current_student) > 0:
                last_i = current_student.take([-1])
                grad_GPAX.append([last_i.Student_ID.values[0], row.AdmitAcademicYear, last_i.AcademicYear.values[0], last_i.GPAX.values[0]])   
    GPAXDf = pd.DataFrame(grad_GPAX, columns = ['Student_ID', 'AdmitAcademicYear', 'LastAcademicYear', 'GPAX'])

    # อ่านข้อมูลจาก Firebase Realtime Database
    ref = db.reference('/webData/honorCriteria')
    honorCriteria = ref.get()

    # แยกนักศึกษาที่ได้เกียรตินิยม ถ้าแก้เกรดได้จะรับมาจาก online database ยังไง
    first = GPAXDf.loc[(GPAXDf['GPAX'] >= honorCriteria['first']) & (GPAXDf['LastAcademicYear'] - GPAXDf['AdmitAcademicYear'] <4)]
    second = GPAXDf.loc[(GPAXDf['GPAX'] >= honorCriteria['second']) & (GPAXDf['GPAX'] < honorCriteria['first'])]

    # เพิ่มสถานะเกียรตินิยม
    for index, row in students.iterrows():
        if row.Student_ID in second['Student_ID'].values:
            students.loc[index, ['StatusName']] = ['เกียรตินิยม อันดับ 2']
        if row.Student_ID in first['Student_ID'].values:
            students.loc[index, ['StatusName']] = ['เกียรตินิยม อันดับ 1']

    # merge ปีที่จบการศึกษา
    students = pd.merge(students, GPAXDf[['Student_ID', 'LastAcademicYear']], on='Student_ID', how='left')
    students = students.fillna(0)
    students['LastAcademicYear'] = students['LastAcademicYear'].astype(int)
    students = students[students['GroupName'] != 'ไม่มีข้อมูล']

    return students

class schoolStat(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        uid = request.META.get('HTTP_UID')
        response = authenticate_user(uid)
        if response.status_code != 200:
            return response
        
        df = allStudentData()

        schoolNameDf = df[['SchoolName', 'TypeName', 'StatusName', 'OldGPA']]

        # #ตารางจำนวนนักศึกษาแต่ละโรงเรียนแบบไม่แยกหลักสูตร
        school = schoolNameDf.groupby(['SchoolName', 'TypeName', 'StatusName']).count()
        school.rename(columns = {'OldGPA': 'Count'}, inplace = True)
        school = school.reset_index()[['SchoolName', 'TypeName', 'StatusName', 'Count']]

        # #เปลี่ยนรูปแบบตาราง
        schoolView = school.pivot_table(index=['SchoolName', 'TypeName'], columns='StatusName', values='Count', fill_value=0, aggfunc='first')

        # #รวมจำนวนนักศึกษา
        schoolView['สำเร็จการศึกษา'] = schoolView['สำเร็จการศึกษา'] + schoolView['เกียรตินิยม อันดับ 1'] + schoolView['เกียรตินิยม อันดับ 2']
        schoolView['เกียรตินิยม'] = schoolView['เกียรตินิยม อันดับ 1'] + schoolView['เกียรตินิยม อันดับ 2']
        column_names = ['คัดชื่อออก', 'ตกออก', 'ลาออก', 'สำเร็จการศึกษา', 'เสียชีวิต', 'โอนย้ายหลักสูตร']
        schoolView['จำนวนพ้นสภาพทั้งหมด'] = schoolView[column_names].sum(axis=1)
        column_names = ['คัดชื่อออก', 'ตกออก', 'ลาออก', 'สำเร็จการศึกษา', 'เสียชีวิต', 'โอนย้ายหลักสูตร', 'ปกติ', 'ลาพัก']
        schoolView['จำนวนนักศึกษาทั้งหมด'] = schoolView[column_names].sum(axis=1)
        reindexColumn = ['SchoolName', 'TypeName', 'ปกติ', 'ลาพัก', 'คัดชื่อออก', 'ตกออก', 'ลาออก', 'เสียชีวิต', 'โอนย้ายหลักสูตร',
                          'เกียรตินิยม อันดับ 1', 'เกียรตินิยม อันดับ 2', 'เกียรตินิยม', 'สำเร็จการศึกษา', 'จำนวนพ้นสภาพทั้งหมด', 'จำนวนนักศึกษาทั้งหมด']
        schoolView = schoolView.reset_index()[reindexColumn]

        # API response
        response = schoolView.to_dict(orient='records')  

        return Response(response)

class schoolHonorStat(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        uid = request.META.get('HTTP_UID')
        response = authenticate_user(uid)
        if response.status_code != 200:
            return response
        
        df = allStudentData()

        response = requests.get('http://localhost:8000/schoolStat/', headers={'uid': uid})
        data = response.json()
        schoolView = pd.DataFrame(data)

        honor = df[(df['StatusName']=='เกียรตินิยม อันดับ 1') | (df['StatusName']=='เกียรตินิยม อันดับ 2') & (df['OldGPA']!=0)]

        # สถิติต่างๆของคนได้รับเกียรตินิยมของแต่ละโรงเรียน
        schoolHonorMean = honor.groupby(['SchoolName']).mean(numeric_only=True)
        schoolHonorMean = schoolHonorMean.reset_index()[['SchoolName', 'OldGPA']]

        schoolHonorMedian = honor.groupby(['SchoolName']).median(numeric_only=True)
        schoolHonorMedian = schoolHonorMedian.reset_index()[['SchoolName', 'OldGPA']]

        schoolHonorSD = honor.groupby(['SchoolName']).std(numeric_only=True)
        schoolHonorSD = schoolHonorSD.reset_index()[['SchoolName', 'OldGPA']]

        # merge dataframes
        honorReport = pd.merge(schoolHonorMean, schoolHonorMedian, on='SchoolName', suffixes=('_mean', '_median'))
        honorReport = pd.merge(honorReport, schoolHonorSD, on='SchoolName')

        # rename columns
        honorReport = honorReport.rename(columns={'OldGPA_mean': 'Mean', 'OldGPA_median': 'Median', 'OldGPA': 'Std'})

        # ตารางสถิติคนได้รับเกียรตินิยมของแต่ละโรงเรียน
        schoolHonorReport = pd.merge(schoolView, honorReport, on='SchoolName', how='left')

        schoolHonorReport['อัตราส่วนที่ได้รับเกียรตินิยม'] = schoolView['เกียรตินิยม']/schoolView['จำนวนพ้นสภาพทั้งหมด']
        schoolHonorReport['จำนวนคนได้รับเกียรตินิยม'] = schoolView['เกียรตินิยม']

        # ใส่ค่า 0 ให้โรงเรียนที่ไม่มีสถิติ
        schoolHonorReport = schoolHonorReport.fillna(value = 0)

        # reset index
        schoolHonorReport = schoolHonorReport.reset_index()[['SchoolName', 'Mean', 'Median', 'Std', 'อัตราส่วนที่ได้รับเกียรตินิยม', 'จำนวนคนได้รับเกียรตินิยม', 'จำนวนพ้นสภาพทั้งหมด']]

        # API response
        response = schoolHonorReport.to_dict(orient='records')

        return Response(response)

class schoolGroupStat(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        uid = request.META.get('HTTP_UID')
        response = authenticate_user(uid)
        if response.status_code != 200:
            return response

        df = allStudentData()

        schoolGroupDf = df[['GroupName', 'StatusName', 'OldGPA']]

        #ตารางจำนวนนักศึกษาแต่ละกลุ่มโรงเรียนแบบไม่แยกหลักสูตร
        schoolGroup = schoolGroupDf.groupby(['GroupName', 'StatusName']).count()
        schoolGroup.rename(columns = {'OldGPA':'Count'}, inplace = True)
        schoolGroup = schoolGroup.reset_index()[['GroupName', 'StatusName', 'Count']]

        #เปลี่ยนรูปแบบตาราง
        schoolGroupView = schoolGroup.pivot_table(index=['GroupName'], columns='StatusName', values='Count', fill_value = 0, aggfunc='first')

        #รวมจำนวนนักศึกษา
        schoolGroupView['สำเร็จการศึกษา'] = schoolGroupView['สำเร็จการศึกษา'] + schoolGroupView['เกียรตินิยม อันดับ 1'] + schoolGroupView['เกียรตินิยม อันดับ 2']
        schoolGroupView['เกียรตินิยม'] = schoolGroupView['เกียรตินิยม อันดับ 1'] + schoolGroupView['เกียรตินิยม อันดับ 2']
        column_names = ['คัดชื่อออก', 'ตกออก', 'ลาออก', 'สำเร็จการศึกษา', 'เสียชีวิต', 'โอนย้ายหลักสูตร']
        schoolGroupView['จำนวนพ้นสภาพทั้งหมด'] = schoolGroupView[column_names].sum(axis=1)
        column_names = ['คัดชื่อออก', 'ตกออก', 'ลาออก', 'สำเร็จการศึกษา', 'เสียชีวิต', 'โอนย้ายหลักสูตร', 'ปกติ', 'ลาพัก']
        schoolGroupView['จำนวนนักศึกษาทั้งหมด'] = schoolGroupView[column_names].sum(axis=1)
        reindexColumn = ['GroupName', 'ปกติ', 'ลาพัก', 'คัดชื่อออก', 'ตกออก', 'ลาออก', 'เสียชีวิต', 'โอนย้ายหลักสูตร',
                          'เกียรตินิยม อันดับ 1', 'เกียรตินิยม อันดับ 2', 'เกียรตินิยม', 'สำเร็จการศึกษา', 'จำนวนพ้นสภาพทั้งหมด', 'จำนวนนักศึกษาทั้งหมด']
        schoolGroupView = schoolGroupView.reset_index()[reindexColumn]

        # API response
        response = schoolGroupView.to_dict(orient='records')

        return Response(response)

class ProgramStat(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        uid = request.META.get('HTTP_UID')
        response = authenticate_user(uid)
        if response.status_code != 200:
            return response

        df = allStudentData()

        # ตารางนักศึกษาแต่ละหลักสูตร
        programDf = df[['ProgramName', 'StatusName', 'OldGPA']]

        # ตารางจำนวนนักศึกษาแต่ละหลักสูตร
        program = programDf.groupby(['ProgramName', 'StatusName']).count()
        program.rename(columns = {'OldGPA':'Count'}, inplace = True)
        program = program.reset_index()[['ProgramName', 'StatusName', 'Count']]

        # เปลี่ยนรูปแบบตาราง
        programView = program.pivot_table(index=['ProgramName'], columns='StatusName', values='Count', fill_value = 0, aggfunc='first')

        # รวมจำนวนนักศึกษา
        programView['สำเร็จการศึกษา'] = programView['สำเร็จการศึกษา'] + programView['เกียรตินิยม อันดับ 1'] + programView['เกียรตินิยม อันดับ 2']
        programView['เกียรตินิยม'] = programView['เกียรตินิยม อันดับ 1'] + programView['เกียรตินิยม อันดับ 2']
        column_names = ['คัดชื่อออก', 'ตกออก', 'ลาออก', 'สำเร็จการศึกษา', 'เสียชีวิต', 'โอนย้ายหลักสูตร']
        programView['จำนวนพ้นสภาพทั้งหมด'] = programView[column_names].sum(axis=1)
        column_names = ['คัดชื่อออก', 'ตกออก', 'ลาออก', 'สำเร็จการศึกษา', 'เสียชีวิต', 'โอนย้ายหลักสูตร', 'ปกติ', 'ลาพัก']
        programView['จำนวนนักศึกษาทั้งหมด'] = programView[column_names].sum(axis=1)
        reindexColumn = ['ProgramName', 'ปกติ', 'ลาพัก', 'คัดชื่อออก', 'ตกออก', 'ลาออก', 'เสียชีวิต', 'โอนย้ายหลักสูตร',
                            'เกียรตินิยม อันดับ 1', 'เกียรตินิยม อันดับ 2', 'เกียรตินิยม', 'สำเร็จการศึกษา', 'จำนวนพ้นสภาพทั้งหมด', 'จำนวนนักศึกษาทั้งหมด']
        programView = programView.reset_index()[reindexColumn]

        # API response
        response = programView.to_dict(orient='records')

        return Response(response)
    
class ProgramHonorStat(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        uid = request.META.get('HTTP_UID')
        response = authenticate_user(uid)
        if response.status_code != 200:
            return response

        df = allStudentData()

        response = requests.get('http://localhost:8000/programStat/', headers={'uid': uid})
        data = response.json()
        programView = pd.DataFrame(data)

        honor = df[(df['StatusName']=='เกียรตินิยม อันดับ 1') | (df['StatusName']=='เกียรตินิยม อันดับ 2') & (df['OldGPA']!=0)]
        programHonor = pd.DataFrame(honor, columns = ['ProgramName','OldGPA'])

        # สถิติต่างๆของคนได้รับเกียรตินิยมของแต่ละหลักสูตร
        programHonorMean = programHonor.groupby(['ProgramName']).mean(numeric_only=True)
        programHonorMean = programHonorMean.reset_index()[['ProgramName', 'OldGPA']]

        programHonorMedian = programHonor.groupby(['ProgramName']).median(numeric_only=True)
        programHonorMedian = programHonorMedian.reset_index()[['ProgramName', 'OldGPA']]

        programHonorSD = programHonor.groupby(['ProgramName']).std(numeric_only=True)
        programHonorSD = programHonorSD.reset_index()[['ProgramName', 'OldGPA']]

        # merge dataframes
        honorReport = pd.merge(programHonorMean, programHonorMedian, on='ProgramName', suffixes=('_mean', '_median'))
        honorReport = pd.merge(honorReport, programHonorSD, on='ProgramName')

        # rename columns
        honorReport = honorReport.rename(columns={'OldGPA_mean': 'Mean', 'OldGPA_median': 'Median', 'OldGPA': 'Std'})

        # ตารางสถิติคนได้รับเกียรตินิยมของแต่ละโรงเรียน
        programHonorReport = pd.merge(programView, honorReport, on='ProgramName', how='left')

        programHonorReport['อัตราส่วนที่ได้รับเกียรตินิยม'] = programView['เกียรตินิยม']/programView['จำนวนพ้นสภาพทั้งหมด']
        programHonorReport['จำนวนคนได้รับเกียรตินิยม'] = programView['เกียรตินิยม']

        # ใส่ค่า 0 ให้โรงเรียนที่ไม่มีสถิติ
        programHonorReport = programHonorReport.fillna(value = 0)

        # reset index
        programHonorReport = programHonorReport.reset_index()[['ProgramName', 'Mean', 'Median', 'Std', 'อัตราส่วนที่ได้รับเกียรตินิยม', 'จำนวนคนได้รับเกียรตินิยม', 'จำนวนพ้นสภาพทั้งหมด']]

        # API response
        response = programHonorReport.to_dict(orient='records')

        return Response(response)

class HonorByAcademicYear(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        uid = request.META.get('HTTP_UID')
        response = authenticate_user(uid)
        if response.status_code != 200:
            return response

        df = allStudentData()

        # ตารางนักศึกษาแต่ละหลักสูตร
        programDf = df[['AdmitAcademicYear', 'ProgramName', 'StatusName', 'OldGPA']]

        # ตารางจำนวนนักศึกษาแต่ละหลักสูตรแยกตามปีการศึกษาที่เข้า
        program = programDf.groupby(['AdmitAcademicYear', 'ProgramName', 'StatusName']).count()
        program.rename(columns = {'OldGPA':'Count'}, inplace = True)
        program = program.reset_index()[['AdmitAcademicYear', 'ProgramName', 'StatusName', 'Count']]

        # เปลี่ยนรูปแบบตาราง
        programView = program.pivot_table(index=['AdmitAcademicYear', 'ProgramName'], columns='StatusName', values='Count', fill_value = 0, aggfunc='first')

        # รวมจำนวนนักศึกษา
        programView['สำเร็จการศึกษา'] = programView['สำเร็จการศึกษา'] + programView['เกียรตินิยม อันดับ 1'] + programView['เกียรตินิยม อันดับ 2']
        programView['เกียรตินิยม'] = programView['เกียรตินิยม อันดับ 1'] + programView['เกียรตินิยม อันดับ 2']
        column_names = ['คัดชื่อออก', 'ตกออก', 'ลาออก', 'สำเร็จการศึกษา', 'เสียชีวิต', 'โอนย้ายหลักสูตร']
        programView['จำนวนพ้นสภาพทั้งหมด'] = programView[column_names].sum(axis=1)
        column_names = ['คัดชื่อออก', 'ตกออก', 'ลาออก', 'สำเร็จการศึกษา', 'เสียชีวิต', 'โอนย้ายหลักสูตร', 'ปกติ', 'ลาพัก']
        programView['จำนวนนักศึกษาทั้งหมด'] = programView[column_names].sum(axis=1)

        # กรองข้อมูลเหลือแต่ปีที่สำเร็จการศึกษา
        programView = programView[programView['สำเร็จการศึกษา'] != 0]
        programView['อัตราส่วนที่ได้รับเกียรตินิยม'] = programView['เกียรตินิยม']/programView['จำนวนพ้นสภาพทั้งหมด']
        reindexColumn = ['AdmitAcademicYear', 'ProgramName', 'จำนวนพ้นสภาพทั้งหมด','เกียรตินิยม อันดับ 1', 'เกียรตินิยม อันดับ 2', 'อัตราส่วนที่ได้รับเกียรตินิยม']
        programView = programView.reset_index()[reindexColumn]

        # API response
        response = programView.to_dict(orient='records')

        return Response(response)
    
class HonorByYearAndGroup(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        uid = request.META.get('HTTP_UID')
        response = authenticate_user(uid)
        if response.status_code != 200:
            return response

        df = allStudentData()

        # ตารางนักศึกษาแต่ละหลักสูตร
        df = df[(df['StatusName']=='เกียรตินิยม อันดับ 1') | (df['StatusName']=='เกียรตินิยม อันดับ 2')]
        yearDf = df[['LastAcademicYear', 'GroupName', 'StatusName', 'OldGPA']]

        # ตารางจำนวนนักศึกษาแต่ละหลักสูตรแยกตามปีการศึกษาที่เข้า
        yearHonor = yearDf.groupby(['LastAcademicYear', 'GroupName', 'StatusName']).count()
        yearHonor.rename(columns = {'OldGPA':'Count'}, inplace = True)
        yearHonor = yearHonor.reset_index()[['LastAcademicYear', 'GroupName', 'StatusName', 'Count']]

        # เปลี่ยนรูปแบบตาราง
        yearHonorView = yearHonor.pivot_table(index=['LastAcademicYear', 'GroupName' ], columns='StatusName', values='Count', fill_value = 0, aggfunc='first')

        # รวมจำนวนนักศึกษา
        yearHonorView['เกียรตินิยม'] = yearHonorView['เกียรตินิยม อันดับ 1'] + yearHonorView['เกียรตินิยม อันดับ 2']
        reindexColumn = ['LastAcademicYear', 'GroupName', 'เกียรตินิยม']
        yearHonorView = yearHonorView.reset_index()[reindexColumn]  

        # API response
        response = yearHonorView.to_dict(orient='records')

        return Response(response)
    
class HonorByYear(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        uid = request.META.get('HTTP_UID')
        response = authenticate_user(uid)
        if response.status_code != 200:
            return response

        df = allStudentData()

        # ตารางนักศึกษาแต่ละหลักสูตร
        df = df[(df['StatusName']=='เกียรตินิยม อันดับ 1') | (df['StatusName']=='เกียรตินิยม อันดับ 2') | (df['StatusName']=='สำเร็จการศึกษา')]
        yearDf = df[['LastAcademicYear', 'StatusName', 'OldGPA']]

        # ตารางจำนวนนักศึกษาแต่ละหลักสูตรแยกตามปีการศึกษาที่เข้า
        yearHonor = yearDf.groupby(['LastAcademicYear', 'StatusName']).count()
        yearHonor.rename(columns = {'OldGPA':'Count'}, inplace = True)
        yearHonor = yearHonor.reset_index()[['LastAcademicYear', 'StatusName', 'Count']]

        # เปลี่ยนรูปแบบตาราง
        yearHonorView = yearHonor.pivot_table(index=['LastAcademicYear' ], columns='StatusName', values='Count', fill_value = 0, aggfunc='first')

        # รวมจำนวนนักศึกษา
        yearHonorView['เกียรตินิยม'] = yearHonorView['เกียรตินิยม อันดับ 1'] + yearHonorView['เกียรตินิยม อันดับ 2']
        yearHonorView['สำเร็จการศึกษา'] = yearHonorView['สำเร็จการศึกษา'] + yearHonorView['เกียรตินิยม อันดับ 1'] + yearHonorView['เกียรตินิยม อันดับ 2']
        reindexColumn = ['LastAcademicYear', 'เกียรตินิยม', 'สำเร็จการศึกษา']
        yearHonorView = yearHonorView.reset_index()[reindexColumn]  

        # API response
        response = yearHonorView.to_dict(orient='records')

        return Response(response)
    
class ProbationByYear(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        uid = request.META.get('HTTP_UID')
        response = authenticate_user(uid)
        if response.status_code != 200:
            return response

        df = allStudentData()

        GPAXQuery = Grade.objects.select_related('Student_ID', 'Student_ID__Status_ID').values('Student_ID', 'Student_ID__Status_ID__StatusName', 'Year_ID__AcademicYear', 'Year_ID__Semester', 'GPAX')
        gpaDf = pd.DataFrame(GPAXQuery)

        # เปลี่ยนชื่อคอลัมน์
        gpaDf = gpaDf.rename(columns={'Student_ID__Status_ID__StatusName': 'StatusName',
                                      'Year_ID__AcademicYear': 'AcademicYear',
                                      'Year_ID__Semester': 'Semester'})
        
        # เกณฑ์ติดวิทยาฑัณฑ์
        ref = db.reference('/webData/gradeCriteria')
        gradeCriteria = ref.get()
        probationCriteria = gradeCriteria['probation']

        # ผลการเรียนเฉลี่ยแต่ละปีการศึกษา
        GPAXList = []

        for index, row in df.iterrows():
            current_student = gpaDf[gpaDf['Student_ID'].isin([row['Student_ID']])]
            if len(current_student) > 0:
                #initial
                semester = 0

                last_i = current_student.take([-1])
                lastAcademicYear = last_i.AcademicYear.values[0]

                for indexC, rowC in current_student.iterrows():
                    GPAX = 0
                    if(rowC['Semester'] != semester):
                        if(rowC['Semester'] != 3):
                            GPAX = rowC['GPAX']
                            semester = rowC['Semester']
                            #append GPAX
                            GPAXList.append([row['Student_ID'], rowC['AcademicYear'], rowC['Semester'], GPAX, lastAcademicYear])
        
        GPAXDf = pd.DataFrame(GPAXList, columns = ['Student_ID', 'AcademicYear', 'Semester', 'GPAX', 'lastAcademicYear'])
        GPAXDf = df.merge(GPAXDf, on=["Student_ID"], how="right")
        GPAXDf = GPAXDf[GPAXDf['Semester'] == 2][['Student_ID', 'AcademicYear', 'GPAX', 'StatusName', 'lastAcademicYear']]
        GPAXDf['Probation'] = GPAXDf.apply(lambda row: 'Probation' 
                                           if row['GPAX'] < probationCriteria and (row['AcademicYear'] != row['lastAcademicYear'] or row['StatusName'] == 'ปกติ') 
                                           else 'Normal', axis=1)
        probation = GPAXDf[GPAXDf['Probation'] == 'Probation'][['AcademicYear', 'Probation']].groupby('AcademicYear').count()
        probation = probation.rename(columns={'Probation': 'TotalProbation'})
        probation = probation.reset_index()[['AcademicYear', 'TotalProbation']]

        # API response
        response = probation.to_dict(orient='records')

        return Response(response)

class GPAX1_1_by_year(APIView):
    permission_classes = [AllowAny]

    def get(self, request, academic_year):
        uid = request.META.get('HTTP_UID')
        response = authenticate_user(uid)
        if response.status_code != 200:
            return response

        df = allStudentData()

        GPAXQuery = Grade.objects.select_related('Student_ID', 'Student_ID__Status_ID').values('Student_ID', 'Student_ID__Status_ID__StatusName', 'Year_ID__AcademicYear', 'Year_ID__Semester', 'GPAX')
        gpaDf = pd.DataFrame(GPAXQuery)

        # เปลี่ยนชื่อคอลัมน์
        gpaDf = gpaDf.rename(columns={'Student_ID__Status_ID__StatusName': 'StatusName',
                                      'Year_ID__AcademicYear': 'AcademicYear',
                                      'Year_ID__Semester': 'Semester'})
        
        # ผลการเรียนเฉลี่ยแต่ละปีการศึกษา
        GPAXList = []

        for index, row in df.iterrows():
            current_student = gpaDf[gpaDf['Student_ID'].isin([row['Student_ID']])]
            if len(current_student) > 0:
                #initial
                GPAX = 0

                if current_student.Semester.values[0] == 1 and current_student.AcademicYear.values[0] == academic_year:
                    GPAX = current_student.GPAX.values[0]
                    academicYear = current_student.AcademicYear.values[0]
                    GPAXList.append([row['Student_ID'], academicYear, GPAX])

        # สร้าง dataframe ของ GPAXList
        GPAXDf = pd.DataFrame(GPAXList, columns = ['Student_ID', 'AcademicYear', 'GPAX'])

        # API response
        response = GPAXDf.to_dict(orient='records')

        return Response(response)

def getLastestAcademicYear():
    allAdmitAcademicYear = Student.objects.values('AdmitAcademicYear').distinct()
    return allAdmitAcademicYear.order_by('-AdmitAcademicYear').first()['AdmitAcademicYear']

def getLastestYearID():
    lastestAcademicYear = getLastestAcademicYear()
    return AcademicSemester.objects.filter(AcademicYear=lastestAcademicYear).first().Year_ID

def getGPAX1_1(academicYear):
    df = allStudentData()

    GPAXQuery = Grade.objects.select_related('Student_ID', 'Student_ID__Status_ID').values('Student_ID', 'Student_ID__Status_ID__StatusName', 'Year_ID__AcademicYear', 'Year_ID__Semester', 'GPAX')
    gpaDf = pd.DataFrame(GPAXQuery)

    # เปลี่ยนชื่อคอลัมน์
    gpaDf = gpaDf.rename(columns={'Student_ID__Status_ID__StatusName': 'StatusName',
                                    'Year_ID__AcademicYear': 'AcademicYear',
                                    'Year_ID__Semester': 'Semester'})
    
    # ผลการเรียนเฉลี่ยแต่ละปีการศึกษา
    GPAXList = []

    for index, row in df.iterrows():
        current_student = gpaDf[gpaDf['Student_ID'].isin([row['Student_ID']])]
        if len(current_student) > 0:
            #initial
            GPAX = 0

            if current_student.Semester.values[0] == 1 and current_student.AcademicYear.values[0] == academicYear:
                GPAX = current_student.GPAX.values[0]
                academicYear = current_student.AcademicYear.values[0]
                GPAXList.append([row['Student_ID'], academicYear, GPAX])

    # สร้าง dataframe ของ GPAXList
    GPAXDf = pd.DataFrame(GPAXList, columns = ['Student_ID', 'AcademicYear', 'GPAX'])
    
    return GPAXDf

class LastestAcademicYear(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        uid = request.META.get('HTTP_UID')
        response = authenticate_user(uid)
        if response.status_code != 200:
            return response

        lastestAcademicYear = getLastestAcademicYear()
        lastestYear_ID = getLastestYearID()

        # API response
        response = {'lastestAcademicYear': lastestAcademicYear,
                    'lastestYear_ID': lastestYear_ID}

        return Response(response)


def getCompleteData():
    students = pd.DataFrame.from_records(Student.objects.all().values())
    schools = pd.DataFrame.from_records(School.objects.all().values())
    statuses = pd.DataFrame.from_records(StudentStatus.objects.all().values())
    types = pd.DataFrame.from_records(SchoolType.objects.all().values())
    groups = pd.DataFrame.from_records(SchoolGroup.objects.all().values())

    # เปลี่ยนชื่อ key ให้ตรงกับชื่อคอลัมน์
    students = students.rename(columns={'School_ID_id': 'School_ID', 'Status_ID_id': 'Status_ID', 'Entrance_ID_id': 'Entrance_ID'})
    schools = schools.rename(columns={'Type_ID_id': 'Type_ID'})
    types = types.rename(columns={'Group_ID_id': 'Group_ID'})

    # fillna
    students = students.fillna(0)

    # รวมข้อมูล
    merged_data = pd.merge(students, schools, on='School_ID', how='left')
    merged_data = pd.merge(merged_data, statuses, on='Status_ID', how='left')
    merged_data = pd.merge(merged_data, types, on='Type_ID', how='left')
    merged_data = pd.merge(merged_data, groups, on='Group_ID', how='left')
    merged_data = merged_data.fillna(0)

    merged_data["School_ID"] = merged_data["School_ID"].astype('Int64')
    merged_data["Type_ID"] = merged_data["Type_ID"].astype('Int64')
    merged_data["Group_ID"] = merged_data["Group_ID"].astype('Int64')

    order_columns = [
        'Student_ID',
        'TH_fName',
        'TH_sName',
        'EN_fName',
        'EN_sName',
        'AdmitAcademicYear',
        'OldGPA',
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

    return merged_data

def predictYear1_1(data):
    # Load the model
    model = joblib.load('model/modelAndEncoder1_1/model1_1.pkl')
    encSchName = joblib.load('model/modelAndEncoder1_1/encoderSchoolName.joblib')
    encSchProv = joblib.load('model/modelAndEncoder1_1/encoderSchoolProv.joblib')

    # Preprocess the input data
    df = pd.DataFrame(data)

    try:    
        df["SCHOOL_NAME"] = encSchName.transform(df["SCHOOL_NAME"])
        df["SCHOOLPROV"] = encSchProv.transform(df["SCHOOLPROV"])

        # Make a prediction using the loaded model
        df["prediction"] = model.predict(df[["SCHOOL_NAME", 'OLDGPA', 'SCHOOLPROV']])

        df["SCHOOL_NAME"] = encSchName.inverse_transform(df["SCHOOL_NAME"])
        df["SCHOOLPROV"] = encSchProv.inverse_transform(df["SCHOOLPROV"])

        response = df.to_dict(orient='records')
    except:
        response = {
            "error" : {
                "code" : 404,
                "message": "ไม่สามารถทำนายด้วยโรงเรียนหรือจังหวัดที่ไม่มีในประวัติได้"
            }
        }
    
    return response

def predictYear1_2(data):
    # Load the model
    model = joblib.load('model/modelAndEncoder1_2/model1_2_Ada.pkl')
    encSchName = joblib.load('model/modelAndEncoder1_2/encoderSchoolName.joblib')
    encProgram = joblib.load('model/modelAndEncoder1_2/encoderProgram.joblib')
    grade = {'A' : 4, 'B+': 3.5, 'B': 3, 'C+': 2.5, 'C': 2, 'D+': 1.5, 'D':1, 'F': 0, 'Fe':0, 'Fa':0, 'W':0, 'I':0}

    # Preprocess the input data
    df = pd.DataFrame(data)      

    if df['MTH101'].isin(['U', 'S']).any():
        response = {
                    "error" : {
                        "code" : 405,
                        "message": "ไม่สามารถทำนายด้วยผลการเรียนรายวิชาเป็น S และ U ได้"
                    }
                }

    else:
        try:
            shortProgram = {'วิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมคอมพิวเตอร์ ปริญญาตรี 4 ปี' : 'CPE',
                            'วิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมคอมพิวเตอร์ ปริญญาตรี 4 ปี  (หลักสูตรนานาชาติ)' : 'CPE inter',
                            'หลักสูตรวิทยาศาสตรบัณฑิต สาขาวิชาวิทยาศาสตร์ข้อมูลสุขภาพ ปริญญาตรี 4 ปี' : 'CPE HDS',
                            'หลักสูตรวิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมคอมพิวเตอร์ ปริญญาตรี 4 ปี (โครงการจากพื้นที่การศึกษาราชบุรี)' : 'CPE RC'}
            df['PROGRAM_PROJECT_NAME_TH'] = df['PROGRAM'].map(shortProgram)

            df["SCHOOL_NAME"] = encSchName.transform(df["SCHOOL_NAME"])
            df['MTH101num'] = df['MTH101'].map(grade)
            df["PROGRAM_PROJECT_NAME_TH"] = encProgram.transform(df["PROGRAM_PROJECT_NAME_TH"])

            # Make a prediction using the loaded model
            df["prediction"] = model.predict(df[["SCHOOL_NAME", 'OLDGPA', 'GPAX1_1', 'MTH101num', "PROGRAM_PROJECT_NAME_TH"]]) # ใช้สำหรับ predict ข้อมูล ต้องติดตั้ง pip install scikit-learn

            df["SCHOOL_NAME"] = encSchName.inverse_transform(df["SCHOOL_NAME"])
            df = df.drop(['MTH101num', 'PROGRAM_PROJECT_NAME_TH'], axis=1)

            response = df.to_dict(orient='records')

        except:
            response = {
                "error" : {
                    "code" : 404,
                    "message": "ไม่สามารถทำนายด้วยโรงเรียนหรือจังหวัดที่ไม่มีในประวัติได้"
                }
            }

    return response

def getMathGrade(studentID):
    Enroll_df = pd.DataFrame.from_records(Enroll.objects.all().values())
    Enroll_df = Enroll_df.rename(columns={'Student_ID_id': 'Student_ID'})
    Enroll_df_student = Enroll_df.loc[Enroll_df['Student_ID'] == studentID]
    
    Course_df = pd.DataFrame.from_records(Course.objects.all().values())
    Course_df = Course_df.rename(columns={'Course_ID_id': 'Course_ID'})

    MTHDetail = Course_df[Course_df['CourseCode'] == 'MTH101']
    MTHCourse_ID = MTHDetail['Course_ID'].values[0]

    MTHGrade = Enroll_df_student[Enroll_df_student['Course_ID_id'] == MTHCourse_ID]
    lastestYear_ID = getLastestYearID()
    MTHGrade = MTHGrade[MTHGrade['Year_ID_id'] == lastestYear_ID]
    if len(MTHGrade) == 0:
        return 0
    else:
        return MTHGrade['Grade'].values[0]

class PredictionData(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        uid = request.META.get('HTTP_UID')
        response = authenticate_user(uid)
        if response.status_code != 200:
            return response

        studentData = getCompleteData()

        lastestAcademicYear = getLastestAcademicYear()
        GPAX1_1 = getGPAX1_1(lastestAcademicYear)
        mode = ""

        if len(GPAX1_1) == 0:
            mode = "first"

        else:
            mode = "second"
        
        # API response
        return Response({
            "mode": mode,
        })

class PredictionDataByMode(APIView):
    permission_classes = [AllowAny]
    def get(self, request, mode):
        uid = request.META.get('HTTP_UID')
        response = authenticate_user(uid)
        if response.status_code != 200:
            return response

        studentData = getCompleteData()

        lastestAcademicYear = getLastestAcademicYear()
        GPAX1_1 = getGPAX1_1(lastestAcademicYear)
        response_data = []

        if mode == "first":
            for i in range(len(studentData)):
                student = studentData.iloc[[i]]
                if student['AdmitAcademicYear'].values[0] == lastestAcademicYear:
                    input_data = {
                        "SCHOOL_NAME": student['SchoolName'],
                        "SCHOOLPROV": student['SchoolProvince'],
                        "OLDGPA": student['OldGPA']
                    }

                    response = predictYear1_1(input_data)

                    if 'error' in response:
                        prediction = 'ไม่มีโรงเรียนในประวัติ'
                    else:
                        prediction = response[0]['prediction']
                    
                    predictionResult = prediction
                    TH_fName = student['TH_fName'].values[0] + ' ' + student['TH_sName'].values[0]
                    if(student['EN_fName'].values[0] != 0 and student['EN_sName'].values[0] != 0):
                        EN_fName = student['EN_fName'].values[0] + ' ' + student['EN_sName'].values[0]
                    else:
                        EN_fName = ''
                    
                    display_data = {
                        "SchoolName": student['SchoolName'].values[0],
                        "SchoolProvince": student['SchoolProvince'].values[0],
                        "OldGPA": student['OldGPA'].values[0],
                    }

                    response_data.append({
                        "Student_ID": student['Student_ID'].values[0],
                        "TH_FullName": TH_fName,
                        "EN_FullName": EN_fName,
                        "prediction": predictionResult,
                        **display_data
                    })

        else:
            for i in range(len(GPAX1_1)):
                GPAX_student = GPAX1_1.iloc[[i]]
                student = studentData[studentData['Student_ID'] == GPAX_student['Student_ID'].values[0]]
                student = student.iloc[[0]]
                if student['StatusName'].values[0] == 'ปกติ':
                    GPAX1_1_grade = GPAX_student['GPAX']
                    mathGrade = getMathGrade(student['Student_ID'].values[0])

                    input_data = {
                        "SCHOOL_NAME": student['SchoolName'],
                        "OLDGPA": student['OldGPA'],
                        "GPAX1_1": GPAX_student['GPAX'].values[0],
                        "MTH101": mathGrade,
                        "PROGRAM": student['ProgramName']
                    }

                    response = predictYear1_2(input_data)

                    if 'error' in response:
                        if response['error']['code'] == 404:
                            prediction = 'ไม่มีโรงเรียนในประวัติ'
                        elif response['error']['code'] == 405:
                            prediction = 'ไม่สามารถทำนายได้'
                    else:
                        prediction = response[0]['prediction']
                    
                    predictionResult = prediction
                    TH_FullName = student['TH_fName'].values[0] + ' ' + student['TH_sName'].values[0]
                    EN_FullName = student['EN_fName'].values[0] + ' ' + student['EN_sName'].values[0]
                    display_data = {
                        "SchoolName": student['SchoolName'].values[0],
                        "OldGPA": student['OldGPA'].values[0],
                        "GPAX1_1": GPAX_student['GPAX'].values[0],
                        "MTH101": mathGrade,
                        "ProgramName": student['ProgramName'].values[0]
                    }

                    response_data.append({
                        "Student_ID": student['Student_ID'].values[0],
                        "TH_FullName": TH_FullName,
                        "EN_FullName": EN_FullName,
                        "prediction": predictionResult,
                        **display_data
                    })
        
        # API response
        return Response({
            "mode": mode,
            "data": response_data
        })



        