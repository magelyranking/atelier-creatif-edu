import streamlit as st
from openai import OpenAI
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import tempfile
import textwrap
import datetime

# =========================
# I18N COMPLET (libellés principaux)
# =========================
I18N = {
    "fr": {"title": "Atelier Créatif — EDU", "generate": "Générer", "download": "Télécharger en PDF"},
    "en": {"title": "Creative Workshop — EDU", "generate": "Generate", "download": "Download PDF"},
    "es": {"title": "Taller Creativo — EDU", "generate": "Generar", "download": "Descargar en PDF"},
    "de": {"title": "Kreativwerkstatt — EDU", "generate": "Generieren", "download": "Als PDF herunterladen"},
    "it": {"title": "Laboratorio Creativo — EDU", "generate": "Genera", "download": "Scarica in PDF"},
}

# =========================
# QPACK COMPLET (questions par langue/activité)
# =========================
QPACK = {
    "fr": {
        "histoire": ["Héros/héroïne","Lieu","Objectif","Obstacle","Allié","Fin"],
        "saynette": ["Personnages","Lieu","Conflit","Accessoire","Moment fort","Fin"],
        "poeme": ["Sujet","Émotion","Forme","Strophe","Dernier vers","Mot-clé"],
        "chanson": ["Thème","Émotion","Style","Refrain","Tempo","Point de vue"],
        "libre": ["Idée","Lieu","Objet","Allié","Obstacle","Fin"]
    },
    "en": {
        "histoire": ["Hero/Heroine","Place","Goal","Obstacle","Ally","Ending"],
        "saynette": ["Characters","Place","Conflict","Prop","Highlight","Ending"],
        "poeme": ["Theme","Emotion","Form","Stanza","Last line","Keyword"],
        "chanson": ["Theme","Emotion","Style","Chorus","Tempo","Point of view"],
        "libre": ["Idea","Place","Object","Ally","Obstacle","Ending"]
    },
    "es": {
        "histoire": ["Héroe/Heroína","Lugar","Objetivo","Obstáculo","Aliado","Final"],
        "saynette": ["Personajes","Lugar","Conflicto","Accesorio","Momento clave","Final"],
        "poeme": ["Tema","Emoción","Forma","Estrofa","Último verso","Palabra clave"],
        "chanson": ["Tema","Emoción","Estilo","Estribillo","Tempo","Punto de vista"],
        "libre": ["Idea","Lugar","Objeto","Aliado","Obstáculo","Final"]
    },
    "de": {
        "histoire": ["Held/Heldin","Ort","Ziel","Hindernis","Verbündeter","Ende"],
        "saynette": ["Figuren","Ort","Konflikt","Requisite","Höhepunkt","Ende"],
        "poeme": ["Thema","Gefühl","Form","Strophe","Letzte Zeile","Schlüsselwort"],
        "chanson": ["Thema","Gefühl","Stil","Refrain","Tempo","Perspektive"],
        "libre": ["Idee","Ort","Objekt","Verbündeter","Hindernis","Ende"]
    },
    "it": {
        "histoire": ["Eroe/Eroina","Luogo","Obiettivo","Ostacolo","Alleato","Finale"],
        "saynette": ["Personaggi","Luogo","Conflitto","Accessorio","Momento clou","Finale"],
        "poeme": ["Tema","Emozione","Forma","Strofa","Ultimo verso","Parola chiave"],
        "chanson": ["Tema","Emozione","Stile","Ritornello","Tempo","Punto di vista"],
        "libre": ["Idea","Luogo","Oggetto","Alleato","Ostacolo","Finale"]
    }
}

# =========================
# INTERFACE STREAMLIT
# =========================
st.set_page_config(page_title="Atelier Créatif EDU", page_icon="🎨")
st.title("🎨 Atelier Créatif — EDU Multilingue")

api_key = st.text_input("🔑 Votre clé OpenAI (elle reste locale)", type="password")

if api_key:
    client = OpenAI(api_key=api_key)

    lang = st.selectbox("🌍 Langue / Language", list(I18N.keys()))
    activity = st.radio("📚 Activité", list(QPACK[lang].keys()))

    st.write("### ✏️ Réponds aux questions :")
    answers = []
    for q in QPACK[lang][activity]:
        a = st.text_input(q)
        if a:
            answers.append(a)

    if st.button(I18N[lang]["generate"]):
        qs = "\n".join([f"- {q}: {a}" for q, a in zip(QPACK[lang][activity], answers)])
        prompt = f"""
        Langue: {lang}. Activité: {activity}.
        Écris un texte créatif, positif et adapté pour enfants/ados.
        Voici les éléments donnés:
        {qs}
        """

        response = client.responses.create(model="gpt-4.1-mini", input=prompt)
        story = response.output_text

        st.subheader("📖 Votre création")
        st.write(story)

        # Génération PDF avec couverture + multi-pages
        tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        c = canvas.Canvas(tmpfile.name, pagesize=A4)
        width, height = A4

        # Page de couverture
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width/2, height-4*cm, "🎨 Atelier Créatif — EDU")
        c.setFont("Helvetica", 16)
        c.drawCentredString(width/2, height-6*cm, f"Activité : {activity} ({lang})")
        c.setFont("Helvetica-Oblique", 12)
        c.drawCentredString(width/2, height-7*cm, f"Date : {datetime.date.today().strftime('%d/%m/%Y')}")
        c.showPage()

        # Pages suivantes (texte)
        c.setFont("Helvetica", 12)
        margin = 2*cm
        max_width = int((width - 2*margin) / 7)  # approx char per line
        y = height - margin

        for line in story.split("\n"):
            wrapped = textwrap.wrap(line, max_width)
            for wline in wrapped:
                if y < margin:
                    c.showPage()
                    c.setFont("Helvetica", 12)
                    y = height - margin
                c.drawString(margin, y, wline)
                y -= 15
            y -= 10

        c.save()

        with open(tmpfile.name, "rb") as f:
            st.download_button(I18N[lang]["download"], f, file_name="creation.pdf")
