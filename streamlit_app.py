import os
from pathlib import Path
import time
import requests
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# ---------------------------------------------------------
# Page Configuration (Sidebar completely hidden)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Student Mental Health Predictor",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# Custom Styling (CSS)
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Completely hide sidebar and collapse toggle */
    [data-testid="stSidebar"], [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* Container Spacing */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1100px;
    }

    /* Hero Header */
    .hero-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 2rem 2.5rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 1.8rem;
        margin-top: 1.8rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.08);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.35rem;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1rem;
        margin: 0;
        max-width: 700px;
        line-height: 1.45;
    }

    /* Status Pill */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .status-online {
        background-color: #dcfce7;
        color: #15803d;
        border: 1px solid #86efac;
    }
    .status-offline {
        background-color: #fef3c7;
        color: #b45309;
        border: 1px solid #fde68a;
    }

    /* Section Card */
    .form-section {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.4rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
        margin-bottom: 1rem;
    }
    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Result Card */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.6rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.2rem;
    }
    .badge {
        display: inline-block;
        padding: 0.35rem 0.85rem;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .badge-excellent { background-color: #dcfce7; color: #166534; border: 1px solid #86efac; }
    .badge-moderate { background-color: #fef9c3; color: #854d0e; border: 1px solid #fde047; }
    .badge-mild { background-color: #ffedd5; color: #9a3412; border: 1px solid #fdba74; }
    .badge-high { background-color: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }

    /* Recommendations */
    .recommendation-box {
        border-left: 4px solid #6366f1;
        background-color: #f8fafc;
        padding: 0.9rem 1.1rem;
        border-radius: 0 10px 10px 0;
        margin-bottom: 0.65rem;
        font-size: 0.92rem;
        color: #334155;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# FastAPI Connection & Configuration
# ---------------------------------------------------------
API_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000").rstrip("/")

is_connected = False
try:
    res_ping = requests.get(f"{API_URL}/health", timeout=1.0)
    if res_ping.status_code == 200:
        is_connected = True
except Exception:
    try:
        res_ping_root = requests.get(f"{API_URL}/", timeout=1.0)
        if res_ping_root.status_code == 200:
            is_connected = True
    except Exception:
        is_connected = False

# ---------------------------------------------------------
# Hero Banner
# ---------------------------------------------------------
status_html = (
    '<div class="status-badge status-online">🟢 FastAPI Connected</div>'
    if is_connected
    else '<div class="status-badge status-offline">🟡 FastAPI Offline (Direct Fallback Ready)</div>'
)

st.markdown(f"""
<div class="hero-header">
    <div>
        <div class="hero-title">🧠 Student Mental Health Score Predictor</div>
        <p class="hero-subtitle">
            Evaluate psychological well-being based on digital screen habits, study routine, physical activity, and stress factors.
        </p>
    </div>
    <div>
        {status_html}
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Prediction Input Form
# ---------------------------------------------------------
with st.form("prediction_form", border=False):
    col_demo, col_digital, col_lifestyle = st.columns(3, gap="medium")

    # 1. Demographics & Academics
    with col_demo:
        st.markdown("""
        <div class="section-title">👤 Demographics & Education</div>
        """, unsafe_allow_html=True)

        age = st.slider("Age", min_value=16, max_value=35, value=21, help="Age of the student in years.")
        gender = st.radio("Gender", ["Female", "Male"], horizontal=True)

        country_options = [
            'India', 'USA', 'Canada', 'Australia', 'UK', 'Germany', 'Mexico', 'Turkey', 'France',
            'Brazil', 'China', 'Japan', 'South Korea', 'Singapore', 'Spain', 'Italy', 'Netherlands', 'Other'
        ]
        country = st.selectbox("Country of Origin", country_options, index=0)
        academic_level = st.selectbox("Academic Level", ['Undergraduate', 'Graduate', 'High School'], index=0)

    # 2. Digital Habits
    with col_digital:
        st.markdown("""
        <div class="section-title">📱 Digital & Social Media</div>
        """, unsafe_allow_html=True)

        platform_options = [
            'Instagram', 'YouTube', 'TikTok', 'Facebook', 'LinkedIn',
            'Twitter', 'Snapchat', 'WhatsApp', 'LINE', 'KakaoTalk', 'WeChat', 'VKontakte'
        ]
        most_used_platform = st.selectbox("Most Used Platform", platform_options, index=0,)
        purpose_of_use = st.selectbox("Primary Purpose of Use", ['Entertainment', 'Education', 'Networking', 'News'], index=0)
        avg_daily_usage = st.slider(
            "Social Media Usage (Hours/Day)",
            min_value=0.5,
            max_value=12.0,
            value=4.0,
            step=0.5,
            help="Total hours spent daily across social media platforms."
        )
        daily_unlocks = st.slider(
            "Daily Phone Unlocks",
            min_value=10,
            max_value=280,
            value=85,
            step=5,
            help="Estimated frequency of unlocking the smartphone per day."
        )

    # 3. Lifestyle & Health
    with col_lifestyle:
        st.markdown("""
        <div class="section-title">🌿 Daily Lifestyle & Habits</div>
        """, unsafe_allow_html=True)

        study_hours = st.slider(
            "Study Hours / Day",
            min_value=0.0,
            max_value=12.0,
            value=4.5,
            step=0.5,
            help="Active study and academic time outside classroom lectures."
        )
        physical_activity = st.slider(
            "Physical Activity (Hours/Day)",
            min_value=0.0,
            max_value=5.0,
            value=1.5,
            step=0.25,
            help="Workout, jogging, gym, sports, or brisk walking."
        )
        sleep_hours = st.slider(
            "Sleep Hours / Night",
            min_value=3.0,
            max_value=12.0,
            value=7.0,
            step=0.5,
            help="Average sleep hours per night."
        )
        stress_level = st.select_slider(
            "Perceived Stress Level",
            options=['Low', 'Medium', 'High', 'Very High'],
            value='Medium'
        )

    st.markdown("<br>", unsafe_allow_html=True)
    submit_btn = st.form_submit_button(
        "🔮 Predict Mental Health Score",
        type="primary",
        use_container_width=True
    )

# ---------------------------------------------------------
# Prediction Execution & Results
# ---------------------------------------------------------
if submit_btn:
    payload = {
        "age": int(age),
        "gender": gender,
        "country": country,
        "academic_level": academic_level,
        "most_used_platform": most_used_platform,
        "purpose_of_use": purpose_of_use,
        "avg_daily_usage": float(avg_daily_usage),
        "daily_unlocks": int(daily_unlocks),
        "study_hours": float(study_hours),
        "physical_activity_hours": float(physical_activity),
        "sleep_hours_per_night": float(sleep_hours),
        "stress_level": stress_level
    }

    score = None
    category = None
    source_label = ""

    with st.spinner("Processing inputs and evaluating prediction..."):
        # 1. Try FastAPI REST API
        try:
            start_time = time.time()
            res = requests.post(f"{API_URL}/predict", json=payload, timeout=4)
            latency_ms = round((time.time() - start_time) * 1000, 1)

            if res.status_code == 200:
                data = res.json()
                score = float(data.get("predicted_mental_score", 0.0))
                category = data.get("wellness_category", "")
                source_label = f"FastAPI Server ({latency_ms} ms)"
        except Exception:
            pass

        # 2. Local Fallback if API is offline
        if score is None:
            try:
                import joblib
                model_file = Path("mental_health_model.pkl")
                if not model_file.exists():
                    model_file = Path("models/mental_health_model.pkl")

                if model_file.exists():
                    loaded_model = joblib.load(model_file)
                    top_countries = ['Other', 'India', 'USA', 'Canada', 'Australia', 'UK', 'Germany', 'Mexico', 'Turkey', 'France']
                    country_group = country if country in top_countries else "Other"

                    row = pd.DataFrame([{
                        'Age': age,
                        'Gender': gender,
                        'Country': country,
                        'Academic_Level': academic_level,
                        'Most_Used_Platform': most_used_platform,
                        'Purpose_Of_Use': purpose_of_use,
                        'Avg_Daily_Usage_Hours': avg_daily_usage,
                        'Daily_Unlocks': daily_unlocks,
                        'Study_Hours': study_hours,
                        'Physical_Activity_Hours': physical_activity,
                        'Sleep_Hours_Per_Night': sleep_hours,
                        'Stress_Level': stress_level,
                        'Grouped_Country': country_group
                    }])
                    raw_pred = loaded_model.predict(row)[0]
                    score = round(float(raw_pred), 2)
                    source_label = "Local Inference Engine"

                    if score >= 7.5:
                        category = "Excellent / Thriving"
                    elif score >= 6.2:
                        category = "Moderate / Balanced"
                    elif score >= 5.0:
                        category = "Mild Concern / Elevated Stress"
                    else:
                        category = "High Concern / Vulnerable"
            except Exception as e:
                st.error(f"Inference error: {e}")

    # Display Assessment Results
    if score is not None:
        st.markdown("---")
        st.markdown("### 📊 Assessment Results")

        if score >= 7.5:
            badge_class = "badge-excellent"
            badge_icon = "🟢"
            accent_color = "#16a34a"
            summary_desc = "Optimal psychological wellbeing. High emotional resilience and healthy lifestyle balance."
        elif score >= 6.2:
            badge_class = "badge-moderate"
            badge_icon = "🟡"
            accent_color = "#ca8a04"
            summary_desc = "Satisfactory mental wellbeing, aligning closely with general student population benchmarks."
        elif score >= 5.0:
            badge_class = "badge-mild"
            badge_icon = "🟠"
            accent_color = "#ea580c"
            summary_desc = "Mild distress detected. Screen time, stress levels, or sleep patterns may need attention."
        else:
            badge_class = "badge-high"
            badge_icon = "🔴"
            accent_color = "#dc2626"
            summary_desc = "Elevated risk of burnout or persistent fatigue. Targeted lifestyle adjustments recommended."

        res_col1, res_col2 = st.columns([1, 1], gap="large")

        with res_col1:
            st.markdown(f"""
            <div class="metric-card" style="border-top: 4px solid {accent_color};">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                    <span style="font-weight:700; color:#64748b; font-size:0.9rem; text-transform:uppercase;">Predicted Score</span>
                    <span class="badge {badge_class}">{badge_icon} {category}</span>
                </div>
                <div style="display:flex; align-items:baseline; gap:10px;">
                    <span style="font-size:3.5rem; font-weight:800; color:#0f172a;">{score:.2f}</span>
                    <span style="font-size:1.4rem; font-weight:600; color:#94a3b8;">/ 10.0</span>
                </div>
                <p style="color:#475569; font-size:0.95rem; margin-top:0.4rem;">{summary_desc}</p>
                <hr style="margin: 0.9rem 0; border: none; border-top: 1px solid #f1f5f9;">
                <div style="display:flex; justify-content:space-between; font-size:0.85rem; color:#64748b;">
                    <span>Provider: <strong>{source_label}</strong></span>
                    <span>Student Average: <strong>6.23 / 10</strong></span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### 💡 Tailored Recommendations")
            recs = []
            if sleep_hours < 6.5:
                recs.append(f"Improve Sleep Duration: Getting {sleep_hours}h sleep per night lowers cognitive resilience. Aim for 7 to 8.5 hours.")
            if avg_daily_usage >= 5.0 or daily_unlocks > 130:
                recs.append(f"**Reduce Digital Interruption:** High daily usage ({avg_daily_usage}h) and frequent unlocks ({daily_unlocks}) create focus fragmentation. Try time-blocking social media.")
            if physical_activity < 1.0:
                recs.append(f"Increase Physical Movement: You recorded {physical_activity}h of daily physical activity. Even a 30-minute daily walk releases endorphins and reduces stress.")
            if stress_level in ["High", "Very High"]:
                recs.append("Active Stress Management: Consider scheduling dedicated breaks, brief mindfulness meditation, or connecting with student support groups.")
            if not recs:
                recs.append("Excellent Equilibrium! Your sleep, study, and digital habits actively foster strong psychological wellbeing.")

            for r in recs:
                st.markdown(f'<div class="recommendation-box">{r}</div>', unsafe_allow_html=True)

        with res_col2:
            # Interactive Gauge Meter
            gauge_fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Wellbeing Meter", 'font': {'size': 20, 'color': '#1e293b'}},
                delta={'reference': 6.23, 'increasing': {'color': "#16a34a"}, 'decreasing': {'color': "#dc2626"}},
                gauge={
                    'axis': {'range': [1, 10], 'tickwidth': 1, 'tickcolor': "#94a3b8"},
                    'bar': {'color': accent_color},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "#e2e8f0",
                    'steps': [
                        {'range': [1, 5.0], 'color': 'rgba(239, 68, 68, 0.15)'},
                        {'range': [5.0, 6.2], 'color': 'rgba(249, 115, 22, 0.15)'},
                        {'range': [6.2, 7.5], 'color': 'rgba(234, 179, 8, 0.15)'},
                        {'range': [7.5, 10], 'color': 'rgba(34, 197, 94, 0.15)'}
                    ],
                    'threshold': {
                        'line': {'color': "#0f172a", 'width': 3},
                        'thickness': 0.8,
                        'value': score
                    }
                }
            ))
            gauge_fig.update_layout(height=290, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(gauge_fig, use_container_width=True)

            # Benchmark Comparison Bar Chart
            metrics = ["Sleep (hrs)", "Exercise (hrs)", "Study (hrs)", "Screen Time (hrs)"]
            student_values = [sleep_hours, physical_activity, study_hours, avg_daily_usage]
            benchmarks = [6.63, 1.48, 4.07, 5.08]

            comp_fig = go.Figure(data=[
                go.Bar(name='You', x=metrics, y=student_values, marker_color=accent_color),
                go.Bar(name='Average Student', x=metrics, y=benchmarks, marker_color='#94a3b8')
            ])
            comp_fig.update_layout(
                barmode='group',
                title="Your Profile vs Average Student",
                height=220,
                margin=dict(l=10, r=10, t=35, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            comp_fig.update_yaxes(gridcolor='#e2e8f0')
            st.plotly_chart(comp_fig, use_container_width=True)



