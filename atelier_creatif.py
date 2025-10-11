import streamlit as st
from openai import OpenAI
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import tempfile
import os
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
api_key = st.text_input("🔑 Entrez votre clé OpenAI", type="password")

if not api_key:
    st.warning("Veuillez entrer votre clé OpenAI pour continuer.")
    st.stop()

client = OpenAI(api_key=api_key)

# -----------------------
# LANGUE & ACTIVITÉ
# -----------------------
st.markdown("### 🌍 Choisissez la langue et l’activité")

col1, col2 = st.columns(2)

with col1:
    lang = st.selectbox("Langue", ["FR", "EN", "ES", "DE", "IT"], index=0)

with col2:
    activity = st.selectbox(
        "Activité",
        ["📚 Histoire", "🎭 Saynette", "✒️ Poème", "🎵 Chanson", "✨ Libre"],
        index=0
    )

# -----------------------
# QUESTIONS SELON ACTIVITÉ
# -----------------------
st.markdown("### 📝 Répondez aux questions")

questions = {
    "📚 Histoire": ["Héros/héroïne ?", "Lieu ?", "Objectif ?", "Obstacle ?", "Allié ?"],
    "🎭 Saynette": ["Personnages ?", "Lieu ?", "Conflit ?", "Accessoire ?", "Moment fort ?"],
    "✒️ Poème": ["Sujet ?", "Émotion ?", "Forme ?", "Strophe ?", "Dernier vers ?"],
    "🎵 Chanson": ["Thème ?", "Émotion ?", "Style ?", "Refrain ?", "Tempo ?"],
    "✨ Libre": ["Idée libre ?", "Lieu ?", "Objet ?", "Allié ?", "Obstacle ?"]
}

answers = []
progress = st.progress(0)
total_q = len(questions[activity])

for i, q in enumerate(questions[activity], start=1):
    val = st.text_input(f"**{i}. {q}**")
    answers.append(val)
    progress.progress(int(i / total_q * 100))

# -----------------------
# GÉNÉRATION DU TEXTE
# -----------------------
if st.button("🪄 Générer le texte", use_container_width=True, type="primary"):
    if not any(answers):
        st.error("⚠️ Veuillez répondre à au moins une question.")
    else:
        with st.spinner("✍️ L'IA écrit votre création..."):
            # Construire le prompt
            prompt = f"Langue : {lang}. Activité : {activity}. "
            prompt += "Crée un texte pour des enfants de 6 à 14 ans. Style positif, adapté et créatif.\n"
            for i, a in enumerate(answers, 1):
                if a:
                    prompt += f"Q{i}: {a}\n"

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Tu es un assistant créatif pour les enfants."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=700
            )

            story = response.choices[0].message.content.strip()

        # AFFICHAGE
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

            # Texte principal
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

