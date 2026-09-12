import os
from pathlib import Path
from typing import Literal, Optional
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Locate model file safely (support root directory and models/ subdirectory)
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "mental_health_model.pkl"
if not MODEL_PATH.exists():
    MODEL_PATH = BASE_DIR / "models" / "mental_health_model.pkl"

if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Model file 'mental_health_model.pkl' not found in {BASE_DIR} or {BASE_DIR / 'models'}")

model = joblib.load(MODEL_PATH)

top_countries = ['Other', 'India', 'USA', 'Canada', 'Australia', 'UK', 'Germany', 'Mexico', 'Turkey', 'France']

app = FastAPI(
    title="Student Mental Health Score Prediction API",
    description="API for predicting student mental health score based on social media usage, academic habits, and lifestyle factors.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Studentdata(BaseModel):
    age: int = Field(..., ge=10, le=100, description="Age of the student (10-100)", examples=[21])
    gender: Literal["Male", "Female"] = Field(..., description="Gender", examples=["Female"])
    country: str = Field(..., description="Country of residence", examples=["India"])
    academic_level: Literal['Undergraduate', 'Graduate', 'High School'] = Field(..., description="Academic Level", examples=["Undergraduate"])
    most_used_platform: Literal[
        'Facebook', 'LinkedIn', 'Instagram', 'Snapchat', 'Twitter',
        'YouTube', 'TikTok', 'LINE', 'KakaoTalk', 'VKontakte', 'WhatsApp', 'WeChat'
    ] = Field(..., description="Most used social media platform", examples=["Instagram"])
    purpose_of_use: Literal['Networking', 'Education', 'Entertainment', 'News'] = Field(..., description="Primary reason for social media use", examples=["Entertainment"])
    avg_daily_usage: float = Field(..., ge=0.0, le=24.0, description="Average daily social media usage (hours)", examples=[4.5])
    daily_unlocks: int = Field(..., ge=0, description="Daily smartphone unlocks count", examples=[85])
    study_hours: float = Field(..., ge=0.0, le=24.0, description="Daily study hours", examples=[3.5])
    # Support both 'physical_activity_hours' and legacy typo 'physical_activity_hout'
    physical_activity_hours: Optional[float] = Field(default=None, ge=0.0, le=24.0, description="Daily physical activity (hours)", examples=[1.0])
    physical_activity_hout: Optional[float] = Field(default=None, ge=0.0, le=24.0, description="Legacy parameter for physical activity hours", examples=[1.0])
    sleep_hours_per_night: float = Field(..., ge=0.0, le=24.0, description="Average sleep per night (hours)", examples=[7.0])
    stress_level: Literal['Low', 'Medium', 'High', 'Very High'] = Field(..., description="Self-reported stress level", examples=["Medium"])


class PredictionResponse(BaseModel):
    predicted_mental_score: float
    wellness_category: str
    status: str = "success"


def get_wellness_category(score: float) -> str:
    if score >= 7.5:
        return "Excellent / Thriving"
    elif score >= 6.2:
        return "Moderate / Balanced"
    elif score >= 5.0:
        return "Mild Concern / Elevated Stress"
    else:
        return "High Concern / Vulnerable"


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Student Mental Health Score Prediction API",
        "docs_url": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "model_loaded": True}


@app.post("/predict", response_model=PredictionResponse)
@app.get("/predict", response_model=PredictionResponse)  # Maintain backward compatibility
def predict(data: Studentdata):
    try:
        # Resolve physical activity hours from either field
        act_hours = data.physical_activity_hours
        if act_hours is None:
            act_hours = data.physical_activity_hout if data.physical_activity_hout is not None else 0.0

        country_group = data.country if data.country in top_countries else "Other"

        input_row = pd.DataFrame([{
            'Age': data.age,
            'Gender': data.gender,
            'Country': data.country,
            'Academic_Level': data.academic_level,
            'Most_Used_Platform': data.most_used_platform,
            'Purpose_Of_Use': data.purpose_of_use,
            'Avg_Daily_Usage_Hours': data.avg_daily_usage,
            'Daily_Unlocks': data.daily_unlocks,
            'Study_Hours': data.study_hours,
            'Physical_Activity_Hours': act_hours,
            'Sleep_Hours_Per_Night': data.sleep_hours_per_night,
            'Stress_Level': data.stress_level,
            'Grouped_Country': country_group
        }])

        prediction = model.predict(input_row)[0]
        score = round(float(prediction), 2)
        category = get_wellness_category(score)

        return PredictionResponse(
            predicted_mental_score=score,
            wellness_category=category,
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")