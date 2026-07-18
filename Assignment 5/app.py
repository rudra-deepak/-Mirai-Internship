# ============================================================
# MirAI School of Technology - Capstone Project
# Multi-Modal Visual Novel Engine
# Part 1 - Imports, Config, Sidebar, Session State
# ============================================================

import streamlit as st
import google.genai as genai
from google.genai import types

import requests
import json
import os
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
from gtts import gTTS

# ------------------------------------------------------------
# Page Config
# ------------------------------------------------------------

st.set_page_config(
    page_title="🎮 AI Visual Novel",
    page_icon="🎭",
    layout="wide"
)

# ------------------------------------------------------------
# Load Environment Variables
# ------------------------------------------------------------

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("❌ GOOGLE_API_KEY not found inside .env")
    st.stop()

# ------------------------------------------------------------
# Create Output Folder
# ------------------------------------------------------------

os.makedirs("generated", exist_ok=True)

# ------------------------------------------------------------
# Cache Gemini Client
# ------------------------------------------------------------

@st.cache_resource
def load_client():
    return genai.Client(api_key=API_KEY)

client = load_client()

# ------------------------------------------------------------
# Premium CSS
# ------------------------------------------------------------

st.markdown("""
<style>

.stApp{
    background:#0f1117;
    color:white;
}

h1{
    text-align:center;
    color:#ffffff;
}

.story-box{
    background:#181c25;
    padding:25px;
    border-radius:20px;
    border:1px solid #2f3542;
    font-size:18px;
    line-height:1.7;
    margin-top:15px;
}

div.stButton>button{
    width:100%;
    padding:15px;
    border-radius:15px;
    background:#6C5CE7;
    color:white;
    border:none;
    font-size:17px;
    font-weight:bold;
}

div.stButton>button:hover{
    background:#8E7CFF;
    color:white;
}

.sidebar-title{
    font-size:24px;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# Title
# ------------------------------------------------------------

st.title("🎮 AI Multi-Modal Visual Novel")

st.caption("Powered by Gemini + Pollinations + gTTS")

# ------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------

with st.sidebar:

    st.header("⚙️ Story Settings")

    genre = st.selectbox(
        "Story Genre",
        [
            "Fantasy",
            "Sci-Fi",
            "Horror",
            "Mystery",
            "Cyberpunk",
            "Adventure",
            "Zombie Apocalypse",
            "Romance"
        ]
    )

    art_style = st.selectbox(
        "Art Style",
        [
            "Anime",
            "Studio Ghibli",
            "Realistic",
            "Pixar",
            "Oil Painting",
            "Comic",
            "Fantasy Art",
            "Pixel Art"
        ]
    )

    difficulty = st.selectbox(
        "Difficulty",
        [
            "Easy",
            "Normal",
            "Hard"
        ]
    )

    st.divider()

    st.markdown("### 📖 Story")

    if st.button("🔄 Restart Story"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ------------------------------------------------------------
# Session State Initialization
# ------------------------------------------------------------

if "chat" not in st.session_state:
    st.session_state.chat = None

if "history" not in st.session_state:
    st.session_state.history = []

if "story" not in st.session_state:
    st.session_state.story = ""

if "image_prompt" not in st.session_state:
    st.session_state.image_prompt = ""

if "choices" not in st.session_state:
    st.session_state.choices = []

if "current_image" not in st.session_state:
    st.session_state.current_image = None

if "audio_file" not in st.session_state:
    st.session_state.audio_file = None

if "started" not in st.session_state:
    st.session_state.started = False

# ------------------------------------------------------------
# Create Chat Session
# ------------------------------------------------------------

if st.session_state.chat is None:

    st.session_state.chat = client.chats.create(
        model="models/gemini-3.5-flash"
    )

    # ============================================================
# PART 2
# Gemini JSON Engine
# ============================================================

SYSTEM_PROMPT = f"""
You are an AI Visual Novel Engine.

Story Genre:
{genre}

Art Style:
{art_style}

Difficulty:
{difficulty}

IMPORTANT RULES:

You MUST reply ONLY with valid JSON.

DO NOT use markdown.

DO NOT use ```json

DO NOT explain anything.

Return EXACTLY this structure:

{{
    "story_text":"...",
    "image_prompt":"...",
    "options":[
        "...",
        "...",
        "..."
    ]
}}

Rules:

1. story_text
- Around 120-180 words
- Continue the story naturally
- Make it immersive

2. image_prompt
- Extremely descriptive
- Mention:
    • environment
    • lighting
    • camera angle
    • cinematic style
    • characters
    • colors
    • atmosphere
    • art style ({art_style})
- Optimized for AI image generation

3. options
- Generate 2 or 3 choices only
- Short
- Exciting
- Different outcomes

Never output anything except JSON.
"""


# ============================================================
# Parse Gemini JSON Safely
# ============================================================

def parse_json(text):

    text = text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "")

    if text.startswith("```"):
        text = text.replace("```", "")

    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    return json.loads(text)


# ============================================================
# Ask Gemini
# ============================================================

def generate_story(user_choice):

    prompt = f"""
{SYSTEM_PROMPT}

Player Action:

{user_choice}
"""

    try:

        response = st.session_state.chat.send_message(prompt)

        data = parse_json(response.text)

        story = data["story_text"]

        image_prompt = data["image_prompt"]

        options = data["options"]

        st.session_state.story = story

        st.session_state.image_prompt = image_prompt

        st.session_state.choices = options

        st.session_state.history.append(
            {
                "story": story,
                "image_prompt": image_prompt,
                "choices": options
            }
        )

        return True

    except json.JSONDecodeError:

        st.error("Gemini returned invalid JSON.")

        return False

    except KeyError:

        st.error("JSON missing required keys.")

        return False

    except Exception as e:

        st.error(f"Gemini Error:\n{e}")

        return False


# ============================================================
# Start Story Button
# ============================================================

if not st.session_state.started:

    st.markdown("---")

    st.subheader("🎬 Begin Your Adventure")

    if st.button("🚀 Start Story"):

        with st.spinner("Creating your world..."):

            success = generate_story(
                "Start a completely new adventure."
            )

            if success:

                st.session_state.started = True

                st.rerun()



# ============================================================
# PART 3
# Pollinations Image Generation
# ============================================================

from urllib.parse import quote


# ------------------------------------------------------------
# Generate Image
# ------------------------------------------------------------

def generate_image(prompt):

    try:

        encoded_prompt = quote(prompt)

        image_url = (
            "https://image.pollinations.ai/prompt/"
            f"{encoded_prompt}"
            "?width=1024"
            "&height=1024"
            "&seed=42"
            "&model=flux"
            "&nologo=true"
        )

        response = requests.get(
            image_url,
            timeout=60
        )

        response.raise_for_status()

        image = Image.open(BytesIO(response.content))

        image_path = "generated/story_image.png"

        image.save(image_path)

        st.session_state.current_image = image_path

        return image_path

    except requests.exceptions.Timeout:

        st.toast("🖼️ Image server timed out. Continuing without visual...")

        st.session_state.current_image = None

        return None

    except requests.exceptions.RequestException:

        st.toast("🖼️ Image server is busy. Continuing without visual...")

        st.session_state.current_image = None

        return None

    except Exception:

        st.toast("⚠️ Unable to generate image.")

        st.session_state.current_image = None

        return None


# ------------------------------------------------------------
# Create image for current story
# ------------------------------------------------------------

if (
    st.session_state.started
    and st.session_state.story
):

    if (
        st.session_state.current_image is None
        and st.session_state.image_prompt
    ):

        with st.spinner("🎨 Generating illustration..."):

            generate_image(
                st.session_state.image_prompt
            )


# ------------------------------------------------------------
# Render Image
# ------------------------------------------------------------

if st.session_state.current_image is not None:

    st.image(
        st.session_state.current_image,
        use_container_width=True,
        caption="AI Generated Scene"
    )

# ============================================================
# PART 4
# Text-to-Speech (gTTS)
# ============================================================

import hashlib


# ------------------------------------------------------------
# Generate Narration Audio
# ------------------------------------------------------------

def generate_audio(text):

    try:

        # Create a unique filename so the browser refreshes audio
        file_hash = hashlib.md5(text.encode("utf-8")).hexdigest()[:12]

        audio_path = f"generated/story_{file_hash}.mp3"

        # Avoid regenerating if it already exists
        if not os.path.exists(audio_path):

            tts = gTTS(
                text=text,
                lang="en",
                slow=False
            )

            tts.save(audio_path)

        st.session_state.audio_file = audio_path

        return audio_path

    except Exception as e:

        st.toast("🔊 Unable to generate narration.")

        st.session_state.audio_file = None

        print(e)

        return None


# ------------------------------------------------------------
# Generate narration for current story
# ------------------------------------------------------------

if (
    st.session_state.started
    and st.session_state.story
):

    expected_hash = hashlib.md5(
        st.session_state.story.encode("utf-8")
    ).hexdigest()[:12]

    expected_audio = f"generated/story_{expected_hash}.mp3"

    if st.session_state.audio_file != expected_audio:

        with st.spinner("🎙️ Creating narration..."):

            generate_audio(
                st.session_state.story
            )


# ------------------------------------------------------------
# Render Story Text
# ------------------------------------------------------------

if st.session_state.story:

    st.markdown(
        f"""
<div class="story-box">

{st.session_state.story}

</div>
""",
        unsafe_allow_html=True
    )


# ------------------------------------------------------------
# Audio Player
# ------------------------------------------------------------

if (
    st.session_state.audio_file
    and os.path.exists(st.session_state.audio_file)
):

    st.audio(
        st.session_state.audio_file,
        format="audio/mp3"
    )

# ============================================================
# PART 5
# Dynamic Choice Buttons
# ============================================================

st.markdown("---")

if st.session_state.started:

    st.subheader("🎮 What will you do next?")

    # If there are no options, end the story gracefully
    if len(st.session_state.choices) == 0:

        st.success("🎉 The story has reached its ending!")

        if st.button("🔄 Start a New Adventure"):

            for key in list(st.session_state.keys()):
                del st.session_state[key]

            st.rerun()

    else:

        # Generate a button for every AI-generated choice
        for index, option in enumerate(st.session_state.choices):

            if st.button(
                option,
                key=f"choice_{index}"
            ):

                with st.spinner("📖 Continuing your adventure..."):

                    success = generate_story(option)

                    if success:

                        # Clear previous media so new content is generated
                        st.session_state.current_image = None
                        st.session_state.audio_file = None

                        st.rerun()


# ============================================================
# Story Timeline
# ============================================================

if st.session_state.started:

    st.markdown("---")

    with st.expander("📜 Story Timeline", expanded=False):

        if len(st.session_state.history) == 0:

            st.info("No story history yet.")

        else:

            for chapter, scene in enumerate(
                st.session_state.history,
                start=1
            ):

                st.markdown(f"### Chapter {chapter}")

                st.write(scene["story"])

                if chapter != len(st.session_state.history):

                    st.divider()


# ============================================================
# Sidebar Statistics
# ============================================================

with st.sidebar:

    st.divider()

    st.subheader("📊 Adventure Stats")

    st.metric(
        "Scenes",
        len(st.session_state.history)
    )

    st.metric(
        "Choices Available",
        len(st.session_state.choices)
    )

    st.metric(
        "Genre",
        genre
    )

    st.metric(
        "Art Style",
        art_style
    )


# ============================================================
# Footer
# ============================================================

st.markdown("---")

st.caption(
    "🎭 AI Visual Novel Engine | "
    "Powered by Gemini • Pollinations • gTTS"
)


