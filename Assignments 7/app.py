import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
import os
from google import genai
import requests
from datetime import datetime

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Life-OS",
    page_icon="🧠",
    layout="wide"
)

# -----------------------------
# LOAD ENVIRONMENT VARIABLES
# -----------------------------
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)

# -----------------------------
# CUSTOM CSS
# -----------------------------
st.markdown("""
<style>

.main {
    background-color:#0f172a;
}

.metric-card{
    background:#1e293b;
    padding:20px;
    border-radius:15px;
}

.block-container{
    padding-top:2rem;
}

h1,h2,h3{
    color:white;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# TITLE
# -----------------------------
st.title("🧠 Life-OS")
st.caption("AI Powered Digital Wellbeing Dashboard <span style='color: Red; text-decoration: bold;'>By Rudra Deepak</span>", unsafe_allow_html=True)

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("screentime.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("⚙ Controls")

selected_date = st.sidebar.selectbox(
    "Select Day",
    sorted(df["Date"].dt.date.unique(), reverse=True)
)

daily_goal = st.sidebar.slider(
    "Daily Goal (Minutes)",
    min_value=60,
    max_value=600,
    value=240,
    step=30
)

# -----------------------------
# FILTER DATA
# -----------------------------
day_df = df[df["Date"].dt.date == selected_date]

# -----------------------------
# DAILY METRICS
# -----------------------------
total_minutes = int(day_df["Minutes_Used"].sum())

most_used_app = (
    day_df.groupby("App_Name")["Minutes_Used"]
    .sum()
    .idxmax()
)

goal_difference = total_minutes - daily_goal

# -----------------------------
# KPI ROW
# -----------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="📱 Total Screen Time",
        value=f"{total_minutes} mins"
    )

with col2:
    st.metric(
        label="🔥 Most Used App",
        value=most_used_app
    )

with col3:
    st.metric(
        label="🎯 Goal Difference",
        value=f"{goal_difference:+} mins",
        delta=f"{goal_difference:+} mins",
        delta_color="inverse"
    )

st.divider()

# -----------------------------
# CHARTS
# -----------------------------

left, right = st.columns(2)

with left:

    trend = (
        df.groupby(df["Date"].dt.date)["Minutes_Used"]
        .sum()
        .reset_index()
    )

    fig = px.line(
        trend,
        x="Date",
        y="Minutes_Used",
        title="📈 14-Day Screen Time Trend",
        markers=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with right:

    category = (
        day_df.groupby("Category")["Minutes_Used"]
        .sum()
        .reset_index()
    )

    fig2 = px.bar(
        category,
        x="Category",
        y="Minutes_Used",
        color="Category",
        title="📊 Today's Usage by Category"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

st.divider()

# -----------------------------
# DATA SUMMARY FOR GEMINI
# -----------------------------

summary = (
    day_df.groupby("Category")["Minutes_Used"]
    .sum()
)

summary_text = summary.to_string()

st.subheader("🤖 AI Productivity Coach")

# -----------------------------
# GEMINI AI ANALYSIS
# -----------------------------

prompt = f"""
You are Life-OS, an AI productivity and wellbeing coach.

Your personality:
- Honest
- Brutally fair
- Supportive
- Practical
- Motivational

Today's Screen Time Summary (minutes):

{summary_text}

Today's total screen time:
{total_minutes} minutes.

User's daily goal:
{daily_goal} minutes.

Instructions:

1. Give the user a Productivity Score out of 10.
2. Mention the biggest strength.
3. Mention the biggest weakness.
4. Analyze every category separately.
5. If Social Media is high, recommend replacing it with:
   - Gym
   - Walking
   - Reading
   - Meditation
   - Meal prep
6. If Entertainment is high, explain dopamine overload.
7. If Coding or Education is high, appreciate consistency.
8. Suggest three realistic actions for tomorrow.
9. Finish with one motivational quote.

Keep the response under 250 words.

Use Markdown formatting.
"""

try:

    with st.spinner("Analyzing your digital lifestyle..."):

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        ai_response = response.text

except Exception as e:

    ai_response = f"""
❌ Gemini API Error

{e}

Check:

• GEMINI_API_KEY

• Internet Connection

• Installed google-genai package

"""

# -----------------------------
# PRODUCTIVITY SCORE
# -----------------------------

score = 100

if total_minutes > daily_goal:
    score -= min(
        60,
        int((total_minutes - daily_goal) / 5)
    )

social = category[
    category["Category"] == "Social Media"
]["Minutes_Used"].sum()

entertainment = category[
    category["Category"] == "Entertainment"
]["Minutes_Used"].sum()

coding = category[
    category["Category"] == "Coding"
]["Minutes_Used"].sum()

education = category[
    category["Category"] == "Education"
]["Minutes_Used"].sum()

score += min(20, coding // 20)
score += min(15, education // 15)

score -= min(25, social // 10)
score -= min(25, entertainment // 10)

score = max(0, min(score, 100))

# -----------------------------
# SCORE CARD
# -----------------------------

st.subheader("🏆 Productivity Score")

progress = score / 100

st.progress(progress)

st.metric(
    "Today's Score",
    f"{score}/100"
)

# -----------------------------
# GOAL STATUS
# -----------------------------

if total_minutes <= daily_goal:

    st.success(
        "🎉 Great job! You stayed within your daily goal."
    )

elif total_minutes <= daily_goal + 60:

    st.info(
        "🙂 Slightly over your goal. Tomorrow can be even better."
    )

else:

    st.warning(
        "⚠️ High screen time detected. It's time to reclaim your day!"
    )

# -----------------------------
# GEMINI RESPONSE
# -----------------------------

st.subheader("🧠 AI Lifestyle Coach")

if total_minutes > daily_goal:

    st.warning(ai_response)

else:

    st.info(ai_response)

st.divider()

# -----------------------------
# CATEGORY BREAKDOWN TABLE
# -----------------------------

st.subheader("📋 Category Breakdown")

category_table = category.copy()

category_table.columns = [
    "Category",
    "Minutes Used"
]

st.dataframe(
    category_table,
    use_container_width=True
)

# -----------------------------
# GUILT-TRIP AVATAR (INNOVATION)
# -----------------------------

st.divider()
st.subheader("🎨 Your Digital Avatar")

if score >= 80:
    avatar_prompt = (
        "A disciplined warrior meditating at sunrise, futuristic digital art, "
        "cinematic lighting, ultra detailed, motivational."
    )
elif score >= 60:
    avatar_prompt = (
        "A focused student working on a laptop in a clean workspace, "
        "minimalist, productive, vibrant colors."
    )
elif score >= 40:
    avatar_prompt = (
        "A tired office worker surrounded by glowing smartphones, "
        "messy desk, realistic digital illustration."
    )
else:
    avatar_prompt = (
        "A lazy zombie staring at a glowing smartphone in a dark room, "
        "surrounded by social media icons, cinematic, detailed artwork."
    )

image_url = (
    "https://image.pollinations.ai/prompt/"
    + requests.utils.quote(avatar_prompt)
)

st.image(
    image_url,
    caption="AI Generated Digital Wellbeing Avatar",
    use_container_width=True
)

# -----------------------------
# SHAREABLE ACCOUNTABILITY LINK
# -----------------------------

st.divider()
st.subheader("🔗 Accountability Link")

try:
    st.query_params["screen_time"] = str(total_minutes)
except Exception:
    # Older Streamlit versions
    pass

st.info(
    "Copy this page URL and send it to your accountability partner."
)

# -----------------------------
# TODAY'S QUICK TIPS
# -----------------------------

st.divider()
st.subheader("💡 Today's Habit Challenge")

tips = []

if social > 120:
    tips.append("📵 Replace 30 minutes of social media with a walk.")

if entertainment > 120:
    tips.append("📚 Read 20 pages of a book before watching videos.")

if coding > 120:
    tips.append("💻 Excellent coding streak! Remember to stretch every hour.")

if education > 60:
    tips.append("🎓 Keep learning—consistency beats intensity.")

if total_minutes > daily_goal:
    tips.append("⏰ Enable app timers for Instagram and YouTube.")

if not tips:
    tips.append("🌟 You're maintaining a healthy digital balance. Keep it up!")

for tip in tips:
    st.markdown(f"- {tip}")

# -----------------------------
# DAILY QUOTE
# -----------------------------

st.divider()

st.markdown(
    """
> **"You don't need more time. You need fewer distractions."**
"""
)

# -----------------------------
# FOOTER
# -----------------------------

st.markdown("---")

st.markdown(
    """
<div style="text-align:center; color:gray;">
    <h4>🧠 Life-OS</h4>
    <p>AI Powered Digital Wellbeing Dashboard </p>
    <p>Built with ❤️ using Streamlit + Gemini AI</p>
    <p style="font-size: 30px; color: Green;"> By Rudra Deepak</p>
</div>
""",
    unsafe_allow_html=True
)

