import pandas as pd
def changeSchoolName(data):
    df = pd.DataFrame(data)

    df['SCHOOLNAME'] = df['SCHOOLNAME'].replace({'๐':'0', '๑':'1', '๒':'2', '๓': '3', '๔': '4',
                                                     '๕': '5', '๖': '6', '๗': '7', '๘': '8', '๙': '9'},regex = True)
    
    df['SCHOOLNAME'] = df['SCHOOLNAME'].str.replace("\(", " (",regex = True)
    df['SCHOOLNAME'] = df['SCHOOLNAME'].str.replace("\[", " [",regex = True)

    tmpDf = df[df['SCHOOLNAME'].str.contains('\"', regex = False)]

    for index,row in tmpDf.iterrows():
        tmp = row['SCHOOLNAME'].split("\"")
        # print(tmp)
        df.loc[index, ['SCHOOLNAME']] = tmp[0] + " \"" + tmp[1] + "\" " + tmp[2]
    
    df['SCHOOLNAME'] = df['SCHOOLNAME'].str.strip()
    df['SCHOOLNAME'] = df['SCHOOLNAME'].str.replace(' +',' ',regex = True)
    df['SCHOOLNAME'] = df['SCHOOLNAME'].replace({"เตรียมอุดมศึกษาพัฒนาการ นนทบุรี (ชื่อเดิม เตรียมอุดมศึกษาพัฒนาการบางใหญ่)":
                                                               "เตรียมอุดมศึกษาพัฒนาการ นนทบุรี",
                                                               "วิสุทธรังษี จังหวัดกาญจนบุรี":
                                                               "วิสุทธรังษี"})
    return df

from firebase_admin import auth
from rest_framework.response import Response

def authenticate_user(uid):
    if uid:
        try:
            auth.get_user(uid)
            return Response(status=200)
        except:
            return Response(data={
                "error": {
                    "code": 404,
                    "message": "ไม่มี user นี้ในระบบ"
                }
            }, status=404)
    else:
        return Response(data={
            "error": {
                "code": 401,
                "message": "Unauthorized"
            }
        }, status=401)