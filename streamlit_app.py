import streamlit as st
import openai
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import tempfile
from datetime import datetime
import os

# -----------------------
# CONFIG APP
# -----------------------
st.set_page_config(
    page_title="Atelier Créatif — EDU",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown(
    """
    <style>
    body { background: #f0f8ff; }
    .stButton>button {
        border-radius: 10px;
        padding: 0.5em 1em;
        margin: 3px;
        font-weight: 600;
    }
    .card {
        background: #ffffff;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
    .suggestion-btn {
        display: inline-block;
        margin: 3px;
        padding: 0.3em 0.8em;
        border-radius: 12px;
        background: #e6f7ff;
        border: 1px solid #91d5ff;
        cursor: pointer;
    }
    .suggestion-btn:hover { background: #bae7ff; }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------
# TITRE + INTRO
# -----------------------
st.markdown("<h1 style='text-align: center; color: #ff69b4;'>🎨 Atelier Créatif — EDU</h1>", unsafe_allow_html=True)
st.markdown(
    """
    <p style="text-align: center; font-size:16px;">
    Créez facilement des <b>histoires, poèmes, chansons ou saynettes</b> pour vos élèves (6–14 ans).<br>
    Répondez aux questions ➝ téléchargez en <b>PDF</b> ✨
    </p>
    """,
    unsafe_allow_html=True
)

st.info("💡 Votre clé OpenAI est sécurisée via Streamlit Cloud (Secrets).")

# -----------------------
# CLÉ OPENAI
# -----------------------
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    st.error("⚠️ Aucune clé API trouvée. Ajoutez OPENAI_API_KEY dans les Secrets Streamlit Cloud.")
    st.stop()
openai.api_key = api_key

# -----------------------
# CARROUSEL IMAGES (avec SLIDER)
# -----------------------
st.markdown("## 🎬 Inspirations")

images = [
    {"file": "slide1.jpg", "caption": "✨ Crée une histoire magique avec tes élèves"},
    {"file": "slide2.jpg", "caption": "🎭 Joue une saynette pleine d’émotion"},
    {"file": "slide4.jpg", "caption": "🎵 Compose une chanson collaborative"},
]

# État initial
if "carousel_index" not in st.session_state:
    st.session_state.carousel_index = 0

total_imgs = len(images)

# Slider (1..N) synchronisé avec l'état
slider_val = st.slider(
    "Sélectionne une image",
    min_value=1, max_value=total_imgs,
    value=st.session_state.carousel_index + 1,
    key="carousel_slider"
)
st.session_state.carousel_index = slider_val - 1

# Affichage image
current = images[st.session_state.carousel_index]
if os.path.exists(current["file"]):
    st.image(current["file"], use_column_width=True, caption=current["caption"])
else:
    st.warning(f"Image introuvable : {current['file']} (ajoute-la dans le repo)")
    st.markdown(f"**{current['caption']}**")

# Boutons ← →
c1, c2, c3 = st.columns([1,6,1])
with c1:
    if st.button("⬅️"):
        st.session_state.carousel_index = (st.session_state.carousel_index - 1) % total_imgs
        st.session_state.carousel_slider = st.session_state.carousel_index + 1
with c3:
    if st.button("➡️"):
        st.session_state.carousel_index = (st.session_state.carousel_index + 1) % total_imgs
        st.session_state.carousel_slider = st.session_state.carousel_index + 1

# -----------------------
# LANGUE & ACTIVITÉ
# -----------------------
st.markdown("### 🌍 Choisissez la langue et l’activité")

lang_buttons = {"🇫🇷 FR": "FR", "🇬🇧 EN": "EN"}
cols = st.columns(len(lang_buttons))
for i, (label, code) in enumerate(lang_buttons.items()):
    if cols[i].button(label):
        st.session_state.lang = code

if "lang" not in st.session_state:
    st.session_state.lang = "FR"
lang = st.session_state.lang

act_buttons = {"📚 Histoire": "Histoire", "🎭 Saynette": "Saynette"}
cols = st.columns(len(act_buttons))
for i, (label, code) in enumerate(act_buttons.items()):
    if cols[i].button(label):
        st.session_state.activity = code

if "activity" not in st.session_state:
    st.session_state.activity = "Histoire"
activity = st.session_state.activity

# -----------------------
# CHAMP AUTEUR
# -----------------------
st.markdown("### ✍️ Auteur")
author = st.text_input("Nom de l’auteur :", "Ma classe")

# -----------------------
# QUESTIONS + SUGGESTIONS
# -----------------------
QPACK = {
    "FR": {
        "Histoire": [
            {"q": "Héros/héroïne ?", "sug": ["Fillette curieuse", "Garçon inventeur", "Chat qui parle"]},
            {"q": "Lieu ?", "sug": ["Cour d’école", "Forêt magique", "Bus scolaire"]},
            {"q": "Objectif ?", "sug": ["Retrouver un trésor", "Aider un ami", "Gagner un concours"]},
            {"q": "Obstacle ?", "sug": ["Orage", "Rival jaloux", "Labyrinthe"]},
            {"q": "Allié ?", "sug": ["Meilleure amie", "Professeur", "Écureuil"]},
        ],
        "Saynette": [
            {"q": "Personnages ?", "sug": ["Deux amis", "Prof et élève", "Frères"]},
            {"q": "Lieu ?", "sug": ["Cantine", "Bus", "Gymnase"]},
            {"q": "Conflit ?", "sug": ["Quiproquo", "Objet perdu", "Concours raté"]},
        ],
    },
    "EN": {
        "Histoire": [  # simple fallback in EN
            {"q": "Hero/heroine?", "sug": ["Curious girl", "Inventor boy", "Talking cat"]},
            {"q": "Setting?", "sug": ["Schoolyard", "Magic forest", "School bus"]},
        ],
        "Saynette": [
            {"q": "Characters?", "sug": ["Two friends", "Teacher & student", "Siblings"]},
            {"q": "Place?", "sug": ["Cafeteria", "Bus", "Gym"]},
            {"q": "Conflict?", "sug": ["Misunderstanding", "Lost item", "Failed contest"]},
        ],
    },
}

st.markdown("### 📝 Répondez aux questions")
answers = []
questions = QPACK.get(lang, QPACK["FR"]).get(activity, [])

progress = st.progress(0)
for i, q in enumerate(questions, start=1):
    with st.container():
        st.markdown(f"<div class='card'><b>{i}. {q['q']}</b></div>", unsafe_allow_html=True)
        # garantir une clé d'état
        st.session_state.setdefault(f"q{i}", "")
        val = st.text_input("", key=f"q{i}")
        sug_cols = st.columns(len(q["sug"]))
        for j, sug in enumerate(q["sug"]):
            if sug_cols[j].button(sug, key=f"sug{i}_{j}"):
                st.session_state[f"q{i}"] = sug
                val = sug
        answers.append(val)
    progress.progress(int(i / max(1, len(questions)) * 100))

# -----------------------
# GÉNÉRATION DU TEXTE
# -----------------------
if st.button("🪄 Générer le texte", use_container_width=True, type="primary"):
    if not any(answers):
        st.error("⚠️ Veuillez répondre à au moins une question.")
    else:
        with st.spinner("✍️ L'IA écrit votre création..."):
            prompt = f"Langue : {lang}. Activité : {activity}. "
            prompt += "Crée un texte adapté aux enfants (6–14 ans). Style positif et créatif.\n"
            prompt += f"Auteur : {author}\n"
