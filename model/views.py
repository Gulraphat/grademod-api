from rest_framework.views import APIView
from rest_framework.response import Response
import joblib # ใช้สำหรับ load model ติดตั้ง pip install joblib
import pandas as pd
from rest_framework.permissions import AllowAny
from Backend.utils import *

class Prediction1_1(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Load the model
        model = joblib.load('model/modelAndEncoder1_1/model1_1.pkl')
        encSchName = joblib.load('model/modelAndEncoder1_1/encoderSchoolName.joblib')
        encSchProv = joblib.load('model/modelAndEncoder1_1/encoderSchoolProv.joblib')

        # Get the input data from the request
        data = request.data

        # Preprocess the input data
        df = pd.DataFrame(data)

        try:    
            df["SCHOOL_NAME"] = encSchName.transform(df["SCHOOL_NAME"])
            df["SCHOOLPROV"] = encSchProv.transform(df["SCHOOLPROV"])

            # Make a prediction using the loaded model
            df["prediction"] = model.predict(df[["SCHOOL_NAME", 'OLDGPA', 'SCHOOLPROV']]) # ใช้สำหรับ predict ข้อมูล ต้องติดตั้ง pip install scikit-learn

            df["SCHOOL_NAME"] = encSchName.inverse_transform(df["SCHOOL_NAME"])
            df["SCHOOLPROV"] = encSchProv.inverse_transform(df["SCHOOLPROV"])

            response = df.to_dict(orient='records')
        except:
            return Response(data={
                    "error" : {
                        "code" : 404,
                        "message": "ไม่สามารถทำนายด้วยโรงเรียนหรือจังหวัดที่ไม่มีในประวัติได้"
                    }
                })

        return Response(response)