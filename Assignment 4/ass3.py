import streamlit as st
import requests
import urllib.parse
import random

# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(
    page_title="AI Image Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================================================
# CUSTOM CSS
# ======================================================

st.markdown("""
<style>

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

.stApp{
background:linear-gradient(135deg,#0f172a,#1e1b4b,#312e81,#4c1d95);
background-size:400% 400%;
animation:gradient 12s ease infinite;
}

@keyframes gradient{
0%{background-position:0% 50%;}
50%{background-position:100% 50%;}
100%{background-position:0% 50%;}
}

.main-title{
text-align:center;
font-size:48px;
font-weight:bold;
color:white;
margin-bottom:10px;
}

.subtitle{
text-align:center;
font-size:18px;
color:#d1d5db;
margin-bottom:30px;
}

.block{
background:rgba(255,255,255,0.08);
padding:20px;
border-radius:15px;
backdrop-filter:blur(15px);
border:1px solid rgba(255,255,255,0.1);
margin-bottom:20px;
}

</style>
""", unsafe_allow_html=True)

# ======================================================
# HEADER
# ======================================================

st.markdown("""
<div class='main-title'>
🎨 AI Image Studio
</div>

<div class='subtitle'>
Generate beautiful AI Images with Pollinations AI
</div>
""", unsafe_allow_html=True)

# ======================================================
# SIDEBAR
# ======================================================

with st.sidebar:

    st.title("⚙ Image Settings")

    art_style = st.selectbox(
        "Choose Art Style",
            [
        "Photorealistic",
        "Cinematic",
        "Hyper Realistic",
        "Fantasy",
        "Studio Ghibli",
        "Anime",
        "Cyberpunk",
        "Steampunk",
        "Pixar",
        "Disney",
        "3D Render",
        "Digital Painting",
        "Oil Painting",
        "Watercolor",
        "Concept Art",
        "Comic Book",
        "Pixel Art",
        "Minimalist",
        "Low Poly",
        "Neon"
]
    )

    width = st.slider(
        "Image Width",
        512,
        2048,
        1280,
        step=64
    )

    height = st.slider(
        "Image Height",
        512,
        2048,
        1280,
        step=64
    )

    magic = st.checkbox("✨ Enable Magic Enhance")

    seed = st.number_input(
    "🎲 Random Seed",
    value=42,
    step=1
)

    st.markdown("---")

    st.info("""
### Features

✅ Width & Height Control

✅ Magic Enhance

✅ Surprise Me

✅ Download PNG

✅ Pollinations AI
""")

# ======================================================
# PROMPT INPUT
# ======================================================

prompt = st.text_area(
    "Describe your image",
    placeholder="Example: A futuristic city floating above the clouds at sunset..."
)

# ======================================================
# RANDOM PROMPTS
# ======================================================

surprise_prompts = [

    "An astronaut riding a horse on Mars",

    "A cyberpunk street food vendor in Tokyo",

    "A dragon made of clouds flying above New York",

    "A giant cat working inside an office",

    "An underwater futuristic city with glowing whales",

    "A samurai walking through a neon forest",

    "Floating islands connected with waterfalls",

    "A robot painter creating the Mona Lisa",

    "A castle inside a volcano",

    "A magical owl wearing golden armor"

]

# ======================================================
# BUTTONS
# ======================================================

col1, col2 = st.columns(2)

with col1:
    generate = st.button("🎨 Generate Image")

with col2:
    surprise = st.button("🎲 Surprise Me")



    # ======================================================
# IMAGE GENERATION FUNCTIONS
# ======================================================

def build_prompt(user_prompt, style, magic_enabled=False):
    """
    Creates the final prompt sent to Pollinations AI.
    """

    full_prompt = (
        f"{user_prompt}, "
        f"{style}, "
        f"beautiful composition, "
        f"highly detailed"
    )

    if magic_enabled:
        full_prompt += (
            ", masterpiece, best quality, ultra realistic, "
            "8k UHD, HDR, cinematic lighting, sharp focus, "
            "professional photography, photorealistic, "
            "ray tracing, global illumination, volumetric lighting, "
            "intricate details, award winning, octane render, "
            "unreal engine 5, highly detailed textures"
        )

    return full_prompt


def generate_image(prompt_text):
    """
    Generates an image using Pollinations AI.
    """

    encoded_prompt = urllib.parse.quote(prompt_text)

    # Assignment Task 1
    url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width={width}"
        f"&height={height}"
        f"&seed={seed}"
    )

    return url


def download_image(image_url):
    """
    Downloads image bytes.
    """

    response = requests.get(image_url)

    if response.status_code == 200:
        return response.content

    return None


# ======================================================
# NORMAL IMAGE GENERATION
# ======================================================

if generate:

    if prompt.strip() == "":
        st.warning("Please enter a prompt first.")

    else:

        with st.spinner("Generating your masterpiece..."):

            final_prompt = build_prompt(
                prompt,
                art_style,
                magic
            )

            image_url = generate_image(final_prompt)

            st.image(
                image_url,
                use_container_width=True,
                caption="Generated Image"
            )

            image_bytes = download_image(image_url)

            if image_bytes:

                # Assignment Task 2
                st.download_button(
                    "📥 Download Image",
                    data=image_bytes,
                    file_name=f"{art_style.lower().replace(' ','_')}_image.png",
                    mime="image/png"
                )

            st.success("Image generated successfully!")

# ======================================================
# SURPRISE ME
# ======================================================

if surprise:

    random_prompt = random.choice(surprise_prompts)

    st.info(f"🎲 Prompt: {random_prompt}")

    with st.spinner("Creating surprise artwork..."):

        final_prompt = build_prompt(
            random_prompt,
            art_style,
            magic
        )

        image_url = generate_image(final_prompt)

        st.image(
            image_url,
            use_container_width=True,
            caption=random_prompt
        )

        image_bytes = download_image(image_url)

        if image_bytes:

            st.download_button(
                "📥 Download Surprise Image",
                data=image_bytes,
                file_name="surprise_image.png",
                mime="image/png"
            )

        st.success("Surprise image generated!")


# ======================================================
# BONUS FEATURES
# ======================================================

st.markdown("---")

with st.expander("ℹ️ About This Project"):

    st.markdown("""
### 🎨 AI Image Studio

Built using:

- 🐍 Python
- 🎈 Streamlit
- 🤖 Pollinations AI

#### Features

- ✅ Custom Prompt
- ✅ Surprise Me
- ✅ Magic Enhance
- ✅ Width & Height Controls
- ✅ PNG Download
- ✅ Modern UI
""")

# ======================================================
# SESSION HISTORY
# ======================================================

if "history" not in st.session_state:
    st.session_state.history = []

if generate and prompt.strip():

    st.session_state.history.append(
        {
            "Prompt": prompt,
            "Style": art_style,
            "Size": f"{width} × {height}"
        }
    )

if surprise:

    st.session_state.history.append(
        {
            "Prompt": random_prompt,
            "Style": art_style,
            "Size": f"{width} × {height}"
        }
    )

# ======================================================
# HISTORY
# ======================================================

if len(st.session_state.history):

    st.markdown("## 🕘 Recent Generations")

    for item in reversed(st.session_state.history[-5:]):

        st.markdown(
            f"""
<div class="block">

**Prompt**

{item["Prompt"]}

🎨 Style: **{item["Style"]}**

📐 Size: **{item["Size"]}**

</div>
""",
            unsafe_allow_html=True
        )

# ======================================================
# METRICS
# ======================================================

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Images Generated",
        len(st.session_state.history)
    )

with col2:
    st.metric(
        "Current Width",
        width
    )

with col3:
    st.metric(
        "Current Height",
        height
    )

# ======================================================
# FOOTER
# ======================================================

st.markdown("---")

st.markdown(
"""
<div style='text-align:center;
color:#d1d5db;
padding:20px;'>

Made using Streamlit & Pollinations AI 
by Rudra Deepak

</div>
""",
unsafe_allow_html=True
)
