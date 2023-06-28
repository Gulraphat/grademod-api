# %%
import pandas as pd
import sqlite3
import numpy as np
from Backend.utils import *
from firebase_admin import db

# %%
admitYear = 'ADMIT_ACAD_YEAR'
programName = 'PROGRAM_PROJECT_NAME_TH'
studentStatus = 'STUDENT_STATUS_NAME'
entStatus = 'ENT_STATUS_NAME'
schoolName = 'SCHOOLNAME'
schoolProv = 'SCHOOLPROV'
oldGPA = 'OLDGPA'

academicYear = 'ACAD_YEAR'
semester = 'SEMESTER_ID'
courseCode = 'COURSE_CODE'
courseName = 'COURSE_NAME_EN'
grade = 'GRADE'
credit = 'GET_CREDIT'
gpa = 'GPA'
gpax = 'GPAX'

# %%
# อ่านไฟล์ตามประเภทที่ user อัพโหลดเข้ามา
def readFile(file):
    fileName = file.name

    if fileName.endswith('.csv'):
        if fileName == 'studentInfo.csv':
            studentInfo_df = pd.read_csv(file, dtype={'STUDENT_ID': str})
            studentInfo_df = studentInfo_df[['STUDENT_ID','TH_fName','TH_sName', 'EN_fName', 'EN_sName', admitYear, programName, studentStatus, entStatus, schoolName, schoolProv, oldGPA]]
            studentInfo_df = studentInfo_df.dropna()
            studentGrade_df = pd.DataFrame(columns=['STUDENT_ID',academicYear,semester,courseCode,courseName,grade,credit,gpa,gpax],)
            importInfo(studentInfo_df, studentGrade_df)
        elif fileName == 'studentGrade.csv':
            studentGrade_df = pd.read_csv(file, dtype={'STUDENT_ID': str})
            importGrade(studentGrade_df)
        else:
            return "Please import file with specified name"
    elif fileName.endswith('.xlsx'):
        dataFile = pd.read_excel(file, sheet_name = None)
        studentInfo_df = dataFile['ประวัติ']
        studentGrade_df = dataFile['GPA']
        studentInfo_df = studentInfo_df[['STUDENT_ID','TH_fName','TH_sName', 'EN_fName', 'EN_sName', admitYear, programName, studentStatus, entStatus, schoolName, schoolProv, oldGPA]]
        importInfo(studentInfo_df, studentGrade_df)
        importGrade(studentGrade_df)
    else:
        raise ValueError('Error: Unsupported File Type!')

# %%
# อ่านข้อมูลโรงเรียน ประเภทโรงเรียน จาก realtime db
ref = db.reference('/webData/schoolData/data')
schoolData = ref.get()
schoolData_df = pd.DataFrame.from_dict(schoolData) # schoolData = school_id, schoolName, TypeName

def importInfo(studentInfo_df, studentGrade_df):
    # %%
    # connect to database
    conn = sqlite3.connect('studentSheet.db')
    cursor = conn.cursor()
    # %%
    # ใช้คำสั่งแปลงชื่อโรงเรียนตรงนี้
    studentInfo_df = changeSchoolName(studentInfo_df)
    studentInfo_df[schoolProv] = studentInfo_df[schoolProv].fillna('ไม่มีข้อมูล')
    keepInfoID = pd.merge(studentInfo_df, studentGrade_df, on = 'STUDENT_ID', how='left')
    studentGrade_df = keepInfoID.drop(columns=['TH_fName','TH_sName', 'EN_fName', 'EN_sName', admitYear, programName, studentStatus, entStatus, schoolName, schoolProv, oldGPA])
    studentGrade_df[[academicYear, semester, credit]] = studentGrade_df[[academicYear, semester, credit]].astype('Int64')
    studentGrade_df.replace('', np.nan, inplace=True)
    studentGrade_df.dropna(inplace=True)
    # %%
    # create status df and running number
    status_df = pd.DataFrame((studentInfo_df[studentStatus]).drop_duplicates())
    status_df.columns = ['StatusName']
    statusList = cursor.execute("SELECT Status_ID, StatusName From StudentStatus").fetchall()
    statusList = pd.DataFrame(statusList, columns=["Status_ID", "StatusName"])
    status_df = statusList.merge(status_df,how='outer').drop_duplicates("StatusName")
    status_df['Status_ID'] = [f'{id}' for id in enumerate(status_df['Status_ID'], 1)]
    status_df['Status_ID'] = [id.split(',')[0].replace('(', '') for id in status_df['Status_ID'] if pd.notna(id)]
    status_df['Status_ID'] = status_df['Status_ID'].astype('Int64')

    # %%
    # make df to sqlite table
    status_df.to_sql('StudentStatus', conn, if_exists='replace', index = False)
    conn.commit()

    # %%
    # create entrance status df and running number
    entrance_df = pd.DataFrame((studentInfo_df[entStatus]).unique())
    entrance_df.columns = ['EntranceName']
    entList = cursor.execute("SELECT Entrance_ID, EntranceName From EntranceStatus").fetchall()
    entList = pd.DataFrame(entList, columns=["Entrance_ID", "EntranceName"])
    entrance_df = entList.merge(entrance_df,how='outer').drop_duplicates("EntranceName")
    entrance_df['Entrance_ID'] = [f'{id}' for id in enumerate(entrance_df['Entrance_ID'], 1)]
    entrance_df['Entrance_ID'] = [id.split(',')[0].replace('(', '') for id in entrance_df['Entrance_ID'] if pd.notna(id)]
    entrance_df['Entrance_ID'] = entrance_df['Entrance_ID'].astype('Int64')

    # %%
    # make df to sqlite table
    entrance_df.to_sql('EntranceStatus', conn, if_exists='replace', index = False)
    conn.commit()

    # %%
    # map student's school data to school data from realtime db
    school_df = pd.DataFrame(studentInfo_df[[schoolName,schoolProv]]).drop_duplicates()
    school_df = school_df.rename(columns = {schoolName:'SchoolName', schoolProv : 'SchoolProvince'})
    school_df = schoolData_df.merge(school_df, left_on ="SchoolName", right_on = 'SchoolName',how='outer')
    school_df['SchoolType'] = school_df['SchoolType'].fillna('')
    school_df.loc[school_df['SchoolName'].isin(['ต่างประเทศ','มหาวิทยาลัยอื่นๆ','โรงเรียนนานาชาติอื่นๆ','ไม่มีข้อมูล']), 'SchoolProvince'] = 'ไม่มีข้อมูล'
    school_df.dropna(subset=['SchoolProvince'], inplace=True)

    # %%
    # get school type from db
    type_id = cursor.execute("SELECT Type_ID, TypeName FROM SchoolType").fetchall()
    type_id = pd.DataFrame(type_id, columns=["Type_ID", "SchoolType"])

    # %%
    # get Type_ID for school
    school_df = school_df.merge(type_id, on="SchoolType", how='outer')
    school_df = school_df.drop("SchoolType", axis=1)
    school_df['Type_ID'] = school_df['Type_ID'].astype('Int64')
    school_df['Type_ID'] = school_df['Type_ID'].fillna(0)
    school_df = school_df.dropna(subset=['SchoolName'])

    # %% [markdown]
    # Merge new school with school table

    # %%
    schoolList = cursor.execute("SELECT School_ID, SchoolName, SchoolProvince, Type_ID From School").fetchall()
    schoolList = pd.DataFrame(schoolList, columns=["School_ID", "SchoolName", "SchoolProvince", "Type_ID"])
    # ป้องกันกรณีมีโรงเรียนใหม่แล้วจะทำให้คอลัมน์ Type_ID กลายเป็น float 
    schoolList['Type_ID'] = pd.to_numeric(schoolList['Type_ID'], errors='coerce').fillna(0).astype('Int64')

    schoolList['School_ID'] = schoolList['School_ID'].astype('Int64')
    schoolList['Type_ID'] = schoolList['Type_ID'].astype('Int64')
    school_df['School_ID'] = school_df['School_ID'].astype('Int64')
    school_df['Type_ID'] = school_df['Type_ID'].astype('Int64')

    school_df = schoolList.merge(school_df,how='right').drop_duplicates("SchoolName")
    school_df = school_df.drop_duplicates(subset='SchoolName')

    # %%
    # make df to sqlite table
    for schoolNameCheck, newSchoolProvince in zip(school_df['SchoolName'], school_df['SchoolProvince']):
        cursor.execute("SELECT * FROM School WHERE SchoolName=?", (schoolNameCheck,))
        existing_school = cursor.fetchone()
        if existing_school is not None:
            # School name already exists, update the schoolProvince
            cursor.execute("UPDATE School SET SchoolProvince=? WHERE SchoolName=?", (newSchoolProvince, schoolNameCheck))
            conn.commit()
        else:
            # Generate a new school ID and insert a new row
            if schoolList.empty:
                last_school_id = 1
            else:
                last_school_id = schoolList['School_ID'].max() + 1
            
            school_df['School_ID'] = range(last_school_id, last_school_id + len(school_df))
            schoolToSQL = "INSERT INTO School (School_ID, SchoolName, SchoolProvince, Type_ID) VALUES (?, ?, ?, ?)"
            school_df = school_df.reindex(columns=['School_ID', 'SchoolName', 'SchoolProvince', 'Type_ID'])
            with conn:
                cursor = conn.cursor()
                cursor.executemany(schoolToSQL, school_df.values.tolist())
                conn.commit()


    # %%
    # get foreign key of school,entrance,status for student df
    school_id = cursor.execute("SELECT School_ID, SchoolName, SchoolProvince FROM School").fetchall()
    school_id = pd.DataFrame(school_id, columns=["School_ID", 'SchoolName', 'SchoolProvince'])
    studentSchool_df = studentInfo_df.merge(school_id, left_on=[schoolName, schoolProv], right_on=['SchoolName', 'SchoolProvince'], how='left', suffixes=('_left', '_right'))
    studentSchool_df = studentSchool_df.drop([schoolName,schoolProv,'SchoolName', 'SchoolProvince'],axis = 1)

    status_id = cursor.execute("SELECT Status_ID, StatusName FROM StudentStatus").fetchall()
    status_id = pd.DataFrame(status_id, columns=["Status_ID", studentStatus])
    studenStatus_df = studentSchool_df.merge(status_id, on = studentStatus, how="left")
    studenStatus_df = studenStatus_df.drop(studentStatus, axis=1)

    entrance_id = cursor.execute("SELECT Entrance_ID, EntranceName FROM EntranceStatus").fetchall()
    entrance_id = pd.DataFrame(entrance_id,columns=["Entrance_ID", entStatus])
    student_df = studenStatus_df.merge(entrance_id, on=entStatus, how="left")
    student_df = student_df.drop(entStatus, axis = 1)
    student_df.columns = ['Student_ID','TH_fName','TH_sName', 'EN_fName', 'EN_sName', 'AdmitAcademicYear', 'ProgramName', 'OldGPA', 'School_ID', 'Status_ID', 'Entrance_ID']

    # %% [markdown]
    # INSERT student info which does not duplicate

    # %%
    studentToSQL = '''INSERT OR REPLACE INTO Student (Student_ID, TH_fName, TH_sName, EN_fName, EN_sName, 
                    AdmitAcademicYear, ProgramName, OldGPA, School_ID, Status_ID, Entrance_ID) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
    for row in student_df.itertuples(index=False):
        cursor.execute(studentToSQL, row)
    conn.commit()
    conn.close()
# %%
def importGrade(studentGrade_df):
    # %%
    # connect to database
    conn = sqlite3.connect('studentSheet.db')
    cursor = conn.cursor()
    # %%
    academicSemester_df = pd.DataFrame(studentGrade_df[[academicYear,semester]]).drop_duplicates()
    academicSemester_df.columns = ['AcademicYear','Semester']
    academicSemester_df = academicSemester_df.sort_values(by=['AcademicYear','Semester'],ascending=[True,True])
    yearList = cursor.execute("SELECT Year_ID, AcademicYear, Semester From AcademicSemester").fetchall()
    yearList = pd.DataFrame(yearList, columns=["Year_ID", "AcademicYear", "Semester"])
    academicSemester_df = yearList.merge(academicSemester_df,how='outer').drop_duplicates(["AcademicYear", "Semester"])
    academicSemester_df['Year_ID'] = [f'{id}' for id in enumerate(academicSemester_df['Year_ID'], 1)]
    academicSemester_df['Year_ID'] = [id.split(',')[0].replace('(', '') for id in academicSemester_df['Year_ID'] if pd.notna(id)]
    academicSemester_df['Year_ID'] = academicSemester_df['Year_ID'].astype('Int64')

    # %%
    academicSemester_df.to_sql('AcademicSemester', conn, if_exists='replace', index = False)
    conn.commit()

    # %%
    course_df = pd.DataFrame(studentGrade_df[[courseCode,courseName,credit]]).drop_duplicates()
    course_df.columns = ['CourseCode', 'CourseName', 'Credit']
    courseList = cursor.execute("SELECT Course_ID, CourseName, CourseCode, Credit From Course").fetchall()
    courseList = pd.DataFrame(courseList, columns=["Course_ID", "CourseName", "CourseCode", "Credit"])
    course_df = courseList.merge(course_df,how='outer').drop_duplicates(["CourseName", "CourseCode"])
    course_df['Course_ID'] = [f'{id}' for id in enumerate(course_df['Course_ID'], 1)]
    course_df['Course_ID'] = [id.split(',')[0].replace('(', '') for id in course_df['Course_ID'] if pd.notna(id)]
    course_df['Course_ID'] = course_df['Course_ID'].astype('Int64')

    # %%
    course_df.to_sql('Course', conn, if_exists='replace', index = False)
    conn.commit()
    # %%
    year_id = cursor.execute("SELECT Year_ID, AcademicYear, Semester FROM AcademicSemester").fetchall()
    year_id = pd.DataFrame(year_id, columns=["Year_ID", academicYear, semester])
    grade_df = studentGrade_df.merge(year_id, on = [academicYear, semester], how="left")
    grade_df = grade_df.drop([academicYear, semester,courseCode,courseName,grade,credit],axis = 1)
    grade_df = grade_df.drop_duplicates()
    gradeColumnOrder = ['STUDENT_ID','Year_ID','GPA','GPAX']
    grade_df= grade_df[gradeColumnOrder]

    # %%
    gradeToSQL = '''INSERT OR IGNORE INTO Grade (Student_ID, Year_ID, GPA, GPAX)
                    VALUES (?, ?, ?, ?)'''
    for row in grade_df.itertuples(index=False):
        cursor.execute(gradeToSQL, row)
    conn.commit()

    # %%
    grade_df = studentGrade_df.merge(year_id, on = [academicYear, semester], how="left")
    gradeEnroll_df = grade_df.drop([academicYear, semester,"GPA","GPAX",credit], axis = 1)

    course_id = cursor.execute("SELECT Course_ID, CourseCode, CourseName FROM Course").fetchall()
    course_id = pd.DataFrame(course_id, columns=["Course_ID", courseCode, courseName])
    enroll_df = gradeEnroll_df.merge(course_id, on = [courseCode, courseName], how="left")
    enroll_df = enroll_df.drop([courseCode,courseName], axis = 1)
    enroll_df = enroll_df.drop_duplicates()
    enrollColumnOrder = ['STUDENT_ID','Year_ID','Course_ID','GRADE']
    enroll_df= enroll_df[enrollColumnOrder]

    # %%
    enrollToSQL = '''INSERT OR IGNORE INTO Enroll (Student_ID, Year_ID, Course_ID, Grade)
                    VALUES (?, ?, ?, ?)'''
    for row in enroll_df.itertuples(index=False):
        cursor.execute(enrollToSQL, row)
    conn.commit()
    conn.close()