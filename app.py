import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
from openai import OpenAI
import re

# ---------------- CONFIG ----------------

client = OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],  
    base_url="https://openrouter.ai/api/v1"
)

st.set_page_config(
    page_title="AI Investment Planner",
    layout="wide"
)

# ---------------- STYLE ----------------

st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(
        135deg,
        #0f2027,
        #203a43,
        #2c5364
    );
}

/* Title */
.main-title {
    text-align: center;
    font-size: 52px;
    font-weight: 800;
    color: white;
}

/* Subtitle */
.sub-title {
    text-align: center;
    font-size: 18px;
    color: #D3D3D3;
    margin-bottom: 30px;
}

/* Labels */
label {
    color: white !important;
    font-weight: 600;
}

/* Inputs */
.stNumberInput input,
.stTextInput input,
.stSelectbox div {
    background-color: rgba(255,255,255,0.08);
    color: white;
    border-radius: 10px;
}

/* Button */
.stButton>button {
    background: linear-gradient(90deg, #00BFFF, #1E90FF);
    color: white;
    border-radius: 12px;
    height: 3em;
    width: 100%;
    font-size: 16px;
    font-weight: bold;
}

/* Result box (FIXED HEIGHT) */
.result-box {
    background-color: rgba(0,0,0,0.4);
    padding: 30px;
    border-radius: 15px;
    color: white;
    margin-top: 20px;

    min-height: 250px;
}

/* Typed text black */
div[data-baseweb="input"] input {
    color: black !important;
}

div[data-baseweb="select"] input {
    color: black !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------

st.markdown("""
<div class="main-title">
🚀 AI Investment Planner
</div>

<div class="sub-title">
Turn Your Savings Into Smart Investments 📈  
Simple • Fast • Personalized
</div>
""", unsafe_allow_html=True)

# ---------------- API ----------------

def get_ai_response(prompt):

    response = client.chat.completions.create(
        model="mistralai/mixtral-8x7b-instruct",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

# ---------------- INPUT ----------------

st.markdown("""
<h3 style='color:white;'>
🧾 Enter Your Details
</h3>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:

    age = st.number_input(
        "Age",
        min_value=18,
        max_value=60,
        value=None,
        placeholder="Enter your age"
    )

    income = st.number_input(
        "Monthly Income (₹)",
        value=None,
        placeholder="Enter monthly income"
    )

with col2:

    savings = st.number_input(
        "Monthly Savings (₹)",
        value=None,
        placeholder="Enter monthly savings"
    )

    years = st.number_input(
        "Investment Years",
        value=None,
        placeholder="Enter years"
    )

goal = st.selectbox(
    "🎯 Select Your Goal",
    [
        "Retirement",
        "Buy a House",
        "Car Purchase",
        "Higher Education",
        "Emergency Fund",
        "Wealth Creation",
        "Child Education",
        "Travel",
        "Business Investment"
    ],
    index=None,
    placeholder="Choose your financial goal"
)

# ---------------- SESSION ----------------

if "generated" not in st.session_state:
    st.session_state.generated = False

# ---------------- FUNCTION ----------------

def extract_percentages(text):

    pattern = r"(Stocks|Mutual Funds|Gold|Bonds).*?(\d+)%"

    matches = re.findall(pattern, text, re.IGNORECASE)

    data = {}

    for k, v in matches:
        data[k.title()] = int(v)

    return data

# ---------------- GENERATE ----------------

if st.button("✨ Generate Plan"):

    if None in [age, income, savings, years] or goal is None:
        st.warning("⚠️ Please fill all fields")

    else:

        prompt = f"""
Suggest a simple investment plan.

Age: {age}
Income: {income}
Savings: {savings}
Goal: {goal}
Duration: {years} years

Give output EXACTLY like:

Stocks: XX%
Mutual Funds: XX%
Gold: XX%
Bonds: XX%

Then explain in numbered points.
"""

        result = get_ai_response(prompt)

        st.session_state.generated = True
        st.session_state.result = result

# ---------------- DISPLAY ----------------

if st.session_state.generated:

    result = st.session_state.result

    formatted = result.replace("\n", "<br>")

    data = extract_percentages(result)

    st.markdown(f"""
    <div class="result-box">

    <h3>
    📊 Your Personalized Investment Plan
    </h3>

    <div style="font-size:16px; line-height:1.6;">

    {formatted}

    </div>

    """, unsafe_allow_html=True)

# ---------------- GRAPHS ----------------

if st.session_state.generated:

    if savings and years:

        col1, col2 = st.columns(2)

        # Growth

        with col1:

            total = 0
            values = []

            for _ in range(int(years * 12)):
                total = total * 1.1 + savings
                values.append(total)

            df_growth = pd.DataFrame({
                "Month": range(len(values)),
                "Value": values
            })

            fig = px.line(
                df_growth,
                x="Month",
                y="Value",
                title="📈 Investment Growth"
            )

            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",

                title_font=dict(
                    color="cyan",
                    size=18
                ),

                font=dict(color="white"),
                xaxis=dict(color="white"),
                yaxis=dict(color="white")
            )

            st.plotly_chart(fig, use_container_width=True)

        # Market

        with col2:

            market = yf.download("^NSEI", period="1y")

            if isinstance(market.columns, pd.MultiIndex):
                market.columns = market.columns.get_level_values(0)

            fig2 = px.line(
                market,
                x=market.index,
                y="Close",
                title="📊 Market Trend"
            )

            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",

                title_font=dict(
                    color="cyan",
                    size=18
                ),

                font=dict(color="white"),
                xaxis=dict(color="white"),
                yaxis=dict(color="white")
            )

            st.plotly_chart(fig2, use_container_width=True)

# ---------------- CHAT ----------------

st.markdown("""
<h3 style='color:white; margin-top:40px;'>
💬 Ask Anything
</h3>
""", unsafe_allow_html=True)

user_input = st.text_input(
    "Type your question here...",
    placeholder="Ask about investments..."
)

if user_input:

    reply = get_ai_response(user_input)

    formatted_reply = reply.replace("\n", "<br>")

    st.markdown(f"""
    <div class="result-box">

    <h3>
    🤖 Answer
    </h3>

    <div style="font-size:16px; line-height:1.6;">

    {formatted_reply}

    </div>

    </div>
    """, unsafe_allow_html=True)
