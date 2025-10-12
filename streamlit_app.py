import streamlit as st
from openai import OpenAI
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
    body {
        background: #f0f8ff;
    }
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
    .suggestion-btn:hover {
        background: #bae7ff;
    }
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
    Créez facilement des <b>histoires, poèmes, chansons ou saynettes</b> pour vos élèves (6–14 ans).  
    Répondez aux questions ➝ téléchargez en <b>PDF</b> ✨
    </p>
    """,
    unsafe_allow_html=True
)

st.info("💡 Votre clé OpenAI est sécurisée via Streamlit Cloud (secrets).")

# -----------------------
# CLÉ OPENAI
# -----------------------
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    st.error("⚠️ Aucune clé API trouvée. Configurez OPENAI_API_KEY dans les secrets Streamlit Cloud.")
    st.stop()

client = OpenAI(api_key=api_key)

# -----------------------
# CARROUSEL IMAGES
# -----------------------
st.markdown("## 🎬 Inspirations")

images = [
    {"file": "slide1.jpg", "caption": "✨ Crée une histoire magique avec tes élèves"},
    {"file": "slide2.jpg", "caption": "🎭 Joue une saynette pleine d’émotion"},
    {"file": "slide4.jpg", "caption": "🎵 Compose une chanson collaborative"},
]

if "carousel_index" not in st.session_state:
    st.session_state.carousel_index = 0

img = images[st.session_state.carousel_index]
st.image(img["file"], use_column_width=True, caption=img["caption"])

col1, col2, col3 = st.columns([1,6,1])
with col1:
    if st.button("⬅️"):
        st.session_state.carousel_index = (st.session_state.carousel_index - 1) % len(images)
with col3:
    if st.button("➡️"):
        st.session_state.carousel_index = (st.session_state.carousel_index + 1) % len(images)

# -----------------------
# LANGUE & ACTIVITÉ
# -----------------------
st.markdown("### 🌍 Choisissez la langue et l’activité")

lang_buttons = {"🇫🇷 FR": "FR", "🇬🇧 EN": "EN", "🇪🇸 ES": "ES", "🇩🇪 DE": "DE", "🇮🇹 IT": "IT"}
cols = st.columns(len(lang_buttons))
for i, (label, code) in enumerate(lang_buttons.items()):
    if cols[i].button(label):
        st.session_state.lang = code

if "lang" not in st.session_state:
    st.session_state.lang = "FR"
lang = st.session_state.lang

act_buttons = {"📚 Histoire": "Histoire", "🎭 Saynette": "Saynette", "✒️ Poème": "Poème", "🎵 Chanson": "Chanson", "✨ Libre": "Libre"}
cols = st.columns(len(act_buttons))
for i, (label, code) in enumerate(act_buttons.items()):
    if cols[i].button(label):
        st.session_state.activity = code

if "activity" not in st.session_state:
    st.session_state.activity = "Histoire"
activity = st.session_state.activity

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
        # Ajoute Poème / Chanson / Libre comme avant...
    },
    # EN, ES, DE, IT -> traductions à compléter
}

st.markdown("### 📝 Répondez aux questions")

answers = []
questions = QPACK.get(lang, QPACK["FR"]).get(activity, [])
progress = st.progress(0)

for i, q in enumerate(questions, start=1):
    with st.container():
        st.markdown(f"<div class='card'><b>{i}. {q['q']}</b></div>", unsafe_allow_html=True)
        val = st.text_input("", key=f"q{i}")
        sug_cols = st.columns(len(q["sug"]))
        for j, sug in enumerate(q["sug"]):
            if sug_cols[j].button(sug, key=f"sug{i}_{j}"):
                val = sug
                st.session_state[f"q{i}"] = sug
        answers.append(val)
    progress.progress(int(i / len(questions) * 100))

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
            for i, a in enumerate(answers, 1):
                if a:
                    prompt += f"Q{i}: {a}\n"

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Tu es un assistant créatif pour enfants."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=700
            )

            story = response.choices[0].message.content.strip()

        st.success("✨ Voici votre création :")
        st.markdown(f"<div style='background:#fff0f6; padding:15px; border-radius:10px;'>{story}</div>", unsafe_allow_html=True)

        # -----------------------
        # EXPORT EN PDF
        # -----------------------
        def create_pdf(text):
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            c = canvas.Canvas(tmp_file.name, pagesize=A4)
            width, height = A4
            # Couverture
            c.setFont("Helvetica-Bold", 22)
            c.drawCentredString(width/2, height - 4*cm, "Atelier Créatif — EDU")
            c.setFont("Helvetica", 14)
            c.drawCentredString(width/2, height - 5*cm, activity)
            c.setFont("Helvetica-Oblique", 10)
            c.drawCentredString(width/2, height - 6*cm, datetime.now().strftime("%d/%m/%Y"))
            c.showPage()
            # Texte
            c.setFont("Helvetica", 12)
            y = height - 3*cm
            for line in text.split("\n"):
                for subline in [line[i:i+90] for i in range(0, len(line), 90)]:
                    c.drawString(2*cm, y, subline)
                    y -= 15
                    if y < 2*cm:
                        c.showPage()
                        c.setFont("Helvetica", 12)
                        y = height - 3*cm
            c.save()
            return tmp_file.name

        pdf_path = create_pdf(story)
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="⬇️ Télécharger en PDF",
                data=f,
                file_name="atelier_creatif.pdf",
                mime="application/pdf",
                use_container_width=True
            )
