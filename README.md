# 🧠 Student Mental Health Score Predictor

An end-to-end Machine Learning web application designed to assess student mental health wellbeing based on digital habits (social media usage, daily phone unlocks), academic patterns, and lifestyle choices (sleep, exercise, stress levels).

---

## 🏗️ Architecture Overview

The system consists of two decoupled components:
1. **Backend (FastAPI):** High-performance REST API serving predictions using a trained Scikit-Learn `RandomForestRegressor` pipeline.
2. **Frontend (Streamlit):** Interactive, responsive UI with real-time API communication, live gauge charts, persona presets, and lifestyle insights.

---

## 📁 Project Structure

```text
Mental Health Score/
│
├── main.py                                           # FastAPI REST API backend
├── streamlit_app.py                                  # Streamlit frontend application
├── app.py                                            # Convenience alias for Streamlit
│
├── mental_health_model.pkl                           # Serialized ML pipeline (Random Forest)
├── mental_score_prediction.ipynb                     # Data exploration, cleaning & training notebook
├── Student Social Media And Mental Health Impact.csv # Survey dataset (5,000 records)
│
├── Dockerfile                                        # Container build definition
├── docker-compose.yml                                # Container orchestration specification
├── requirements.txt                                  # Python dependencies
├── .gitignore                                        # Version control exclusions
└── README.md                                         # Project documentation
```

---

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the FastAPI Backend
Launch the backend server on port `8000`:
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
- Interactive Swagger API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### 3. Start the Streamlit Frontend
In a second terminal, launch the Streamlit interface:
```bash
streamlit run streamlit_app.py
```
Or:
```bash
streamlit run app.py
```
The app will open automatically in your browser at `http://localhost:8501`.

---

## 🔌 API Endpoints

### `POST /predict`
Submit student parameters to get the predicted mental health score.

**Sample Request Body:**
```json
{
  "age": 21,
  "gender": "Female",
  "country": "India",
  "academic_level": "Undergraduate",
  "most_used_platform": "YouTube",
  "purpose_of_use": "Education",
  "avg_daily_usage": 2.5,
  "daily_unlocks": 50,
  "study_hours": 5.0,
  "physical_activity_hours": 2.0,
  "sleep_hours_per_night": 8.0,
  "stress_level": "Low"
}
```

**Sample Response:**
```json
{
  "predicted_mental_score": 7.97,
  "wellness_category": "Excellent / Thriving",
  "status": "success"
}
```

---

## 🎯 Target Score Interpretation

| Score Range | Category | Description |
| :--- | :--- | :--- |
| **7.5 - 10.0** | 🟢 Excellent / Thriving | High psychological resilience and balanced habits |
| **6.2 - 7.4** | 🟡 Moderate / Balanced | General average wellbeing |
| **5.0 - 6.1** | 🟠 Mild Concern | Elevated stress; sleep or digital detox recommended |
| **< 5.0** | 🔴 High Concern | High risk; immediate lifestyle interventions recommended |
