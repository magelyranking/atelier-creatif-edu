import streamlit as st
from openai import OpenAI
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import tempfile
from datetime import datetime

# -----------------------
# CONFIG APP
# -----------------------
st.set_page_config(
    page_title="Atelier Créatif — EDU",
    page_icon="🎨",
    layout="centered"
)

# -----------------------
# TITRE + INTRO
# -----------------------
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🎨 Atelier Créatif — EDU</h1>", unsafe_allow_html=True)
st.markdown("""
<p style="text-align: center; font-size:16px;">
Créez facilement des <b>histoires, poèmes, chansons ou saynettes</b> pour vos élèves (6–14 ans).  
Répondez aux questions ➝ téléchargez en <b>PDF</b> ✨
</p>
""", unsafe_allow_html=True)

st.info("💡 Votre clé OpenAI reste privée et n’est jamais partagée.")

# -----------------------
# CLÉ OPENAI
# -----------------------
import os

# Récupère la clé OpenAI depuis les "secrets" de Streamlit Cloud
api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    st.error("⚠️ Aucune clé API trouvée. Configurez OPENAI_API_KEY dans les secrets Streamlit Cloud.")
    st.stop()

client = OpenAI(api_key=api_key)

# -----------------------
# SLIDER D'IMAGES
# -----------------------
import time

# -----------------------
# CARROUSEL AVEC BOUTONS
# -----------------------
st.markdown("## 🎬 Inspirations")
images = [
    {"file": "https://raw.githubusercontent.com/magelyranking/atelier-creatif-edu/main/slide1.jpg",
     "caption": "✨ Crée une histoire magique avec tes élèves"},
    {"file": "https://raw.githubusercontent.com/magelyranking/atelier-creatif-edu/main/slide2.jpg",
     "caption": "🎭 Joue une saynette pleine d’émotion"},
    {"file": "https://raw.githubusercontent.com/magelyranking/atelier-creatif-edu/main/slide4.jpg",
     "caption": "🎵 Compose une chanson collaborative"},
]

# Initialisation
if "carousel_index" not in st.session_state:
    st.session_state.carousel_index = 0

# Affiche l’image actuelle
img = images[st.session_state.carousel_index]
st.markdown(
    f"""
    <div style='
        position: relative; 
        border-radius: 15px; 
        overflow: hidden; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.15); 
        margin-bottom: 20px;'>
        <img src='{img["file"]}' style='width:100%; border-radius:15px;'>
        <div style='
            position: absolute; 
            bottom: 10px; 
            left: 0; 
            width: 100%; 
            background: rgba(0,0,0,0.5); 
            color: white; 
            text-align: center; 
            padding: 8px; 
            font-size: 16px; 
            border-bottom-left-radius: 15px;
            border-bottom-right-radius: 15px;'>
            {img["caption"]}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Boutons navigation
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

# Sélection de la langue avec drapeaux
lang_col1, lang_col2, lang_col3, lang_col4, lang_col5 = st.columns(5)
if lang_col1.button("🇫🇷 FR"):
    lang = "FR"
if lang_col2.button("🇬🇧 EN"):
    lang = "EN"
if lang_col3.button("🇪🇸 ES"):
    lang = "ES"
if lang_col4.button("🇩🇪 DE"):
    lang = "DE"
if lang_col5.button("🇮🇹 IT"):
    lang = "IT"

# Valeur par défaut
if "lang" not in locals():
    lang = "FR"

# Sélection activité avec icônes
act_col1, act_col2, act_col3, act_col4, act_col5 = st.columns(5)
if act_col1.button("📚 Histoire"):
    activity = "📚 Histoire"
if act_col2.button("🎭 Saynette"):
    activity = "🎭 Saynette"
if act_col3.button("✒️ Poème"):
    activity = "✒️ Poème"
if act_col4.button("🎵 Chanson"):
    activity = "🎵 Chanson"
if act_col5.button("✨ Libre"):
    activity = "✨ Libre"

# Valeur par défaut
if "activity" not in locals():
    activity = "📚 Histoire"

# -----------------------
# QUESTIONS + SUGGESTIONS MULTILINGUES
# -----------------------
QPACK = {
    "FR": {
        "📚 Histoire": [
            {"q": "Héros/héroïne ?", "sug": ["Fillette curieuse", "Garçon inventeur", "Chat qui parle"]},
            {"q": "Lieu ?", "sug": ["Cour d’école", "Forêt magique", "Bus scolaire"]},
            {"q": "Objectif ?", "sug": ["Retrouver un trésor", "Aider un ami", "Gagner un concours"]},
            {"q": "Obstacle ?", "sug": ["Orage", "Rival jaloux", "Labyrinthe"]},
            {"q": "Allié ?", "sug": ["Meilleure amie", "Professeur", "Écureuil"]},
        ],
        "🎭 Saynette": [
            {"q": "Personnages ?", "sug": ["Deux amis", "Prof et élève", "Frères"]},
            {"q": "Lieu ?", "sug": ["Cantine", "Bus", "Gymnase"]},
            {"q": "Conflit ?", "sug": ["Quiproquo", "Objet perdu", "Concours raté"]},
            {"q": "Accessoire ?", "sug": ["Sac", "Affiche", "Téléphone"]},
            {"q": "Moment fort ?", "sug": ["Réplique culte", "Chute", "Impro"]},
        ],
        "✒️ Poème": [
            {"q": "Sujet ?", "sug": ["Pluie", "Montagne", "Amitié"]},
            {"q": "Émotion ?", "sug": ["Doux", "Drôle", "Mystérieux"]},
            {"q": "Forme ?", "sug": ["Alexandrin", "Rimes croisées", "Haïku", "Libre"]},
            {"q": "Strophe ?", "sug": ["Courte", "Moyenne", "Longue"]},
            {"q": "Dernier vers ?", "sug": ["Espoir", "Sourire", "Secret"]},
        ],
        "🎵 Chanson": [
            {"q": "Thème ?", "sug": ["Voyage", "École", "Amitié"]},
            {"q": "Émotion ?", "sug": ["Joie", "Nostalgie", "Courage"]},
            {"q": "Style ?", "sug": ["Rap", "Pop", "Jazz", "Folk"]},
            {"q": "Refrain ?", "sug": ["Mot répété", "Onomatopées", "Question/réponse"]},
            {"q": "Tempo ?", "sug": ["Lent", "Moyen", "Rapide"]},
        ],
        "✨ Libre": [
            {"q": "Idée libre ?", "sug": ["Dragon végétarien", "Ville sous l’eau", "Robot timide"]},
            {"q": "Lieu ?", "sug": ["Toit", "Forêt", "Plage"]},
            {"q": "Objet ?", "sug": ["Carnet", "Boussole", "Graine d’étoile"]},
            {"q": "Allié ?", "sug": ["Voisin", "Chat", "Caméraman"]},
            {"q": "Obstacle ?", "sug": ["Panne", "Temps limité", "Promesse"]},
        ],
    },
    "EN": {
        "📚 Histoire": [
            {"q": "Hero / Heroine?", "sug": ["Curious girl", "Inventor boy", "Talking cat"]},
            {"q": "Place?", "sug": ["Schoolyard", "Magic forest", "School bus"]},
            {"q": "Goal?", "sug": ["Find a treasure", "Help a friend", "Win a contest"]},
            {"q": "Obstacle?", "sug": ["Storm", "Jealous rival", "Maze"]},
            {"q": "Ally?", "sug": ["Best friend", "Teacher", "Squirrel"]},
        ],
        # ... même structure pour Saynette/Poem/Song/Free (traduit en anglais)
    },
    # Idem pour ES, DE, IT (tu peux remplir avec les packs traduits comme dans ton JS d’avant)
}

# -----------------------
# AFFICHAGE QUESTIONS
# -----------------------
st.markdown("### 📝 Répondez aux questions")
answers = []
questions = QPACK.get(lang, QPACK["FR"]).get(activity, [])
progress = st.progress(0)

for i, q in enumerate(questions, start=1):
    colA, colB = st.columns([3, 2])
    with colA:
        val = st.text_input(f"**{i}. {q['q']}**", key=f"q{i}")
    with colB:
        suggestion = st.selectbox("Suggestions", [""] + q["sug"], key=f"sug{i}")
        if suggestion:
            val = suggestion
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
        st.markdown(f"<div style='background:#f9f9f9; padding:15px; border-radius:10px;'>{story}</div>", unsafe_allow_html=True)

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

