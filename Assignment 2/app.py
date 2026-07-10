
import os
from dotenv import load_dotenv
import streamlit as st
from google import genai
from google.genai import types

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="AI Multiverse",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

html,body,[class*="css"]{
font-family:'Poppins',sans-serif;
}

/* Background */

.stApp{

background:
radial-gradient(circle at top left,#7c3aed55,transparent 35%),
radial-gradient(circle at top right,#2563eb55,transparent 35%),
radial-gradient(circle at bottom,#06b6d455,transparent 35%),
linear-gradient(135deg,#020617,#0f172a,#111827);

background-size:200% 200%;

animation:bgMove 15s ease infinite;

color:white;

}

/* Animated Background */

@keyframes bgMove{

0%{background-position:0% 50%;}

50%{background-position:100% 50%;}

100%{background-position:0% 50%;}

}

/* Hide Streamlit */

header{
visibility:hidden;
}

footer{
visibility:hidden;
}

#MainMenu{
visibility:hidden;
}

/* Hero */

.hero{

padding:35px;

border-radius:25px;

background:rgba(255,255,255,.08);

backdrop-filter:blur(25px);

border:1px solid rgba(255,255,255,.12);

text-align:center;

box-shadow:0 0 45px rgba(124,58,237,.2);

margin-bottom:30px;

}

.hero h1{

font-size:60px;

margin:0;

background:linear-gradient(90deg,#a855f7,#3b82f6,#06b6d4);

-webkit-background-clip:text;

-webkit-text-fill-color:transparent;

}

.hero p{

color:#cbd5e1;

font-size:18px;

}

/* Character Card */

.character{

background:rgba(255,255,255,.07);

padding:20px;

border-radius:20px;

text-align:center;

border:1px solid rgba(255,255,255,.08);

transition:.35s;

cursor:pointer;

}

.character:hover{

transform:translateY(-6px);

border-color:#8b5cf6;

box-shadow:0 0 25px rgba(139,92,246,.3);

}

/* Chat */

[data-testid="stChatMessage"]{

background:rgba(255,255,255,.05);

backdrop-filter:blur(25px);

border-radius:20px;

padding:18px;

border:1px solid rgba(255,255,255,.08);

margin-bottom:15px;

}

/* Input */

textarea{

background:#111827!important;

border-radius:18px!important;

border:2px solid #8b5cf6!important;

color:white!important;

}

/* Button */

.stButton>button{

width:100%;

height:55px;

border-radius:15px;

background:linear-gradient(90deg,#9333ea,#2563eb);

color:white;

font-weight:700;

border:none;

transition:.3s;

}

.stButton>button:hover{

transform:translateY(-2px);

box-shadow:0 0 20px #7c3aed;

}

/* Metrics */

[data-testid="metric-container"]{

background:rgba(255,255,255,.05);

border-radius:18px;

padding:15px;

border:1px solid rgba(255,255,255,.08);

}

</style>
""",unsafe_allow_html=True)

# --------------------------------------------------
# GEMINI
# --------------------------------------------------

load_dotenv()

client=genai.Client(
api_key=os.getenv("GEMINI_API_KEY")
)

# --------------------------------------------------
# PERSONAS
# --------------------------------------------------

personas={

"👨🏻‍⚕️ Doctor":
"""
You are Mr. Doctor.
Always greet first.
Be calm.
Answer accurately.
If problem sounds serious advise hospital.
""",

"👩🏻‍🍳 Mother Chef":
"""
You are a sweet caring mother.
Talk lovingly.
Give recipes when needed.
""",

"👨🏻‍🏫 Teacher":
"""
You are a college professor.
Explain simply.
Use examples.
""",

"👨🏻‍💻 Coding Buddy":
"""
You are a friendly coding buddy.
Explain code clearly.
""",

"🥗 Dietitian":
"""
You are an experienced dietitian.
Give practical healthy advice.
"""

}

# --------------------------------------------------
# SESSION
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages=[]

if "selected" not in st.session_state:
    st.session_state.selected="👨🏻‍⚕️ Doctor"



# --------------------------------------------------
# HERO
# --------------------------------------------------

st.markdown("""
<div class="hero">
<h1>🚀AI Multiverse</h1>
<p>One AI • Infinite Personalities</p>
<p style="opacity:.7;">Created by <b>Rudra Deepak</b></p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# CHARACTER SELECTION
# --------------------------------------------------

st.markdown("## 🎭 Choose Your AI")

characters = list(personas.keys())

cols = st.columns(len(characters))

for i, char in enumerate(characters):

    with cols[i]:

        active = st.session_state.selected == char

        if active:
            btn = f"✅ {char}"
        else:
            btn = char

        if st.button(btn, use_container_width=True):

            st.session_state.selected = char
            st.rerun()

# --------------------------------------------------
# CURRENT CHARACTER
# --------------------------------------------------

selected = st.session_state.selected

st.markdown("---")

c1, c2 = st.columns([1, 3])

with c1:

    st.markdown(f"""
<div style="
background:rgba(255,255,255,.06);
padding:20px;
border-radius:20px;
text-align:center;
border:1px solid rgba(255,255,255,.08);
">

<h1 style="font-size:60px;margin:0;">
{selected.split()[0]}
</h1>

<h3>{selected.replace(selected.split()[0],'').strip()}</h3>

<p style="color:#cbd5e1;">
Ready to help you 🚀
</p>

</div>
""", unsafe_allow_html=True)

with c2:

    m1, m2, m3 = st.columns(3)

    with m1:
        st.metric(
            "🤖 Model",
            "Gemini 2.5"
        )

    with m2:
        st.metric(
            "💬 Messages",
            len(st.session_state.messages)
        )

    with m3:
        st.metric(
            "🎭 Character",
            selected.replace(selected.split()[0], "").strip()
        )

st.markdown("---")

# --------------------------------------------------
# START SCREEN
# --------------------------------------------------

if len(st.session_state.messages) == 0:

    st.markdown(f"""
## 👋 Welcome

You are currently chatting with **{selected}**

### Try asking:

- Tell me about yourself.
- Help me solve a problem.
- Explain something.
- Give me advice.
""")
    



    # --------------------------------------------------
# CHAT HISTORY
# --------------------------------------------------

avatars = {
    "👨🏻‍⚕️ Doctor": "👨🏻‍⚕️",
    "👩🏻‍🍳 Mother Chef": "👩🏻‍🍳",
    "👨🏻‍🏫 Teacher": "👨🏻‍🏫",
    "👨🏻‍💻 Coding Buddy": "👨🏻‍💻",
    "🥗 Dietitian": "🥗"
}

for msg in st.session_state.messages:

    with st.chat_message(
        msg["role"],
        avatar=msg.get("avatar", "🤖")
    ):

        st.markdown(msg["content"])


# --------------------------------------------------
# CHAT INPUT
# --------------------------------------------------

prompt = st.chat_input("💬 Ask anything...")

if prompt:

    # ---------------- USER MESSAGE ----------------

    st.session_state.messages.append({

        "role": "user",
        "content": prompt,
        "avatar": "🧑"

    })

    with st.chat_message("user", avatar="🧑"):

        st.markdown(prompt)

    # ---------------- AI RESPONSE ----------------

    with st.chat_message(
        "assistant",
        avatar=avatars[selected]
    ):

        with st.spinner(f"{selected} is thinking..."):

            try:

                response = client.models.generate_content(

                    model="gemini-2.5-flash",

                    contents=prompt,

                    config=types.GenerateContentConfig(

                        system_instruction=personas[selected]

                    )

                )

                answer = response.text

            except Exception as e:

                answer = f"""
❌ Error

{e}

Check:

• Internet Connection

• API Key

• Gemini Quota
"""

        st.markdown(answer)

    st.session_state.messages.append({

        "role": "assistant",

        "content": answer,

        "avatar": avatars[selected]

    })


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("<br>", unsafe_allow_html=True)

c1, c2 = st.columns([8, 2])

with c1:

    st.caption("🌌 AI Multiverse • Powered by Gemini 2.5 Flash")

with c2:

    if st.button("🗑 Clear Chat"):

        st.session_state.messages = []

        st.rerun()


st.markdown(
"""
<hr style="border:1px solid rgba(255,255,255,.1);">

<center>

Made with ❤️ by <b>Rudra Deepak</b>

</center>
""",
unsafe_allow_html=True
)

