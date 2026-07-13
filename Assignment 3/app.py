import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from google import genai

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="AI Multiverse",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# LOAD GEMINI
# =====================================================

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# =====================================================
# SESSION STATE
# =====================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "personality" not in st.session_state:
    st.session_state.personality = "Helpful Assistant"

if "theme_color" not in st.session_state:
    st.session_state.theme_color = "#8A2BE2"

if "chat_started" not in st.session_state:
    st.session_state.chat_started = False

# =====================================================
# PREMIUM CSS
# =====================================================

st.markdown("""
<style>

/* Hide Streamlit */

#MainMenu{
visibility:hidden;
}

footer{
visibility:hidden;
}

header{
visibility:hidden;
}

/* Background */

.stApp{
background:linear-gradient(
135deg,
#0f172a,
#111827,
#1e1b4b,
#312e81
);

background-size:400% 400%;
animation:bgMove 15s ease infinite;
}

@keyframes bgMove{

0%{
background-position:0% 50%;
}

50%{
background-position:100% 50%;
}

100%{
background-position:0% 50%;
}

}

/* Main */

.block-container{

padding-top:2rem;

max-width:1200px;

}

/* Header */

.mainTitle{

font-size:3rem;

font-weight:700;

text-align:center;

color:white;

margin-bottom:5px;

}

/* Subtitle */

.subtitle{

text-align:center;

font-size:18px;

color:#d1d5db;

margin-bottom:30px;

}

/* Sidebar */

section[data-testid="stSidebar"]{

background:rgba(20,20,30,0.92);

backdrop-filter:blur(20px);

border-right:1px solid rgba(255,255,255,0.08);

}

/* Glass Card */

.glass{

background:rgba(255,255,255,0.06);

padding:18px;

border-radius:18px;

border:1px solid rgba(255,255,255,0.08);

backdrop-filter:blur(20px);

margin-bottom:15px;

}

/* Chat */

.stChatMessage{

background:rgba(255,255,255,0.05);

border-radius:15px;

padding:10px;

margin-bottom:10px;

}

/* Buttons */

.stButton>button{

width:100%;

border-radius:12px;

height:45px;

font-weight:600;

}

/* Selectbox */

.stSelectbox{

margin-bottom:10px;

}

/* Metric */

[data-testid="metric-container"]{

background:rgba(255,255,255,0.05);

border-radius:15px;

padding:15px;

}

</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================

st.markdown(
"""
<div class="mainTitle">
🌌 AI Multiverse
</div>

<div class="subtitle">
Premium AI Assistant powered by Gemini
</div>
""",
unsafe_allow_html=True
)

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.title("⚙ Control Panel")

    st.markdown("---")

    personality = st.selectbox(
        "AI Personality",
        [
            "Helpful Assistant",
            "Coding Expert",
            "Teacher",
            "Doctor",
            "Fitness Coach",
            "Chef",
            "Travel Guide",
            "Funny Friend"
        ],
        index=0
    )

    st.session_state.personality = personality

    st.markdown("---")

    st.subheader("📊 Chat Statistics")

    user_count = len(
        [m for m in st.session_state.messages if m["role"]=="user"]
    )

    ai_count = len(
        [m for m in st.session_state.messages if m["role"]=="assistant"]
    )

    total = len(st.session_state.messages)

    st.metric("Total Messages", total)

    st.metric("User Messages", user_count)

    st.metric("AI Messages", ai_count)

    st.markdown("---")

    if st.button("🗑 Clear Conversation"):

        st.session_state.messages=[]

        st.rerun()

    st.markdown("---")

    st.info(
"""
### Assignment Features

✅ Session State

✅ Chat Memory

✅ Chat Input

✅ Sidebar Settings

✅ Modern UI

✅ Responsive Layout
"""
)

# =====================================================
# SHOW CHAT HISTORY
# =====================================================

for message in st.session_state.messages:

    avatar="👤"

    if message["role"]=="assistant":
        avatar="🤖"

    with st.chat_message(message["role"], avatar=avatar):

        st.markdown(message["content"])

# =====================================================
# WELCOME SCREEN
# =====================================================

if len(st.session_state.messages)==0:

    st.markdown("""

<div class="glass">

## 👋 Welcome

This chatbot remembers every message using **Streamlit Session State**.

Start chatting below!

</div>

""", unsafe_allow_html=True)
    
# =====================================================
# HELPER FUNCTIONS
# =====================================================

import time

def build_system_prompt(personality):
    prompts = {
        "Helpful Assistant": (
            "You are a friendly, intelligent AI assistant. "
            "Answer clearly and politely."
        ),

        "Coding Expert": (
            "You are an expert software engineer. "
            "Give optimized code, explain concepts simply, "
            "and follow best coding practices."
        ),

        "Teacher": (
            "You are an experienced teacher. "
            "Explain concepts step-by-step with examples."
        ),

        "Doctor": (
            "You provide general educational health information only. "
            "Do not diagnose diseases or replace a medical professional."
        ),

        "Fitness Coach": (
            "You are a fitness coach. "
            "Provide workout and nutrition guidance."
        ),

        "Chef": (
            "You are a professional chef. "
            "Suggest recipes with simple instructions."
        ),

        "Travel Guide": (
            "You are a travel guide. "
            "Recommend destinations, food, and itineraries."
        ),

        "Funny Friend": (
            "Be funny, entertaining, and cheerful while remaining helpful."
        )
    }

    return prompts.get(personality, prompts["Helpful Assistant"])


def stream_text(text):
    """
    Creates a typewriter effect.
    """

    placeholder = st.empty()

    output = ""

    for word in text.split():

        output += word + " "

        placeholder.markdown(output + "▌")

        time.sleep(0.02)

    placeholder.markdown(output)

    return output.strip()


# =====================================================
# CHAT INPUT
# =====================================================

if prompt := st.chat_input("💬 Ask anything..."):

    st.session_state.chat_started = True

    # --------------------------
    # Timestamp
    # --------------------------

    current_time = datetime.now().strftime("%I:%M %p")

    # --------------------------
    # Save User Message
    # --------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
            "time": current_time
        }
    )

    # --------------------------
    # Display User Message
    # --------------------------

    with st.chat_message("user", avatar="👤"):

        st.markdown(prompt)

        st.caption(current_time)

    # =====================================================
    # BUILD CHAT HISTORY
    # =====================================================

    history = []

    system_prompt = build_system_prompt(
        st.session_state.personality
    )

    history.append(
        system_prompt
    )

    for msg in st.session_state.messages:

        if msg["role"] == "user":

            history.append(
                f"User: {msg['content']}"
            )

        else:

            history.append(
                f"Assistant: {msg['content']}"
            )

    conversation = "\n".join(history)

    # =====================================================
    # GEMINI RESPONSE
    # =====================================================

    with st.chat_message("assistant", avatar="🤖"):

        with st.spinner("Thinking..."):

            try:

                response = client.models.generate_content(

                    model="gemini-2.5-flash",

                    contents=conversation

                )

                ai_reply = response.text

            except Exception as e:

                ai_reply = f"""
❌ Error

{str(e)}

Please check:

• Internet connection

• Gemini API Key

• API quota
"""

        stream_text(ai_reply)

        st.caption(datetime.now().strftime("%I:%M %p"))

    # =====================================================
    # SAVE ASSISTANT MESSAGE
    # =====================================================

    st.session_state.messages.append(

        {

            "role": "assistant",

            "content": ai_reply,

            "time": datetime.now().strftime("%I:%M %p")

        }

    )
