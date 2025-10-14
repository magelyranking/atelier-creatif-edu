import streamlit as st
from openai import OpenAI
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import tempfile
from datetime import datetime
import os, csv

# =========================
# CONFIG APP
# =========================
st.set_page_config(
    page_title="Atelier Créatif — EDU",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =========================
# CSS GLOBAL
# =========================
st.markdown(
    """
    <style>
    .main .block-container {
        max-width: 880px;
        padding-left: 1rem;
        padding-right: 1rem;
        margin: auto;
    }
    .question-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 10px 14px;
        margin: 6px 0 2px 0;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        font-size: 16px;
        line-height: 1.4em;
    }
    .suggestion-btn {
        background: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #91d5ff !important;
        border-radius: 20px;
        padding: 6px 14px;
        font-size: 14px;
    }
    .suggestion-btn:hover {
        background: #e6f7ff !important;
        color: #000000 !important;
    }
    div[role="radiogroup"] > label {
        background: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #91d5ff !important;
        border-radius: 20px;
        padding: 6px 14px;
    }
    div[role="radiogroup"] > label[data-checked="true"] {
        background: #1890ff !important;
        color: #ffffff !important;
        border: 1px solid #1890ff !important;
    }
    input[type="text"] {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    input::placeholder {
        color: #666 !important;
        opacity: 1 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# OPENAI
# =========================
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    st.error("⚠️ Aucune clé API trouvée. Ajoutez OPENAI_API_KEY dans les Secrets Streamlit Cloud.")
    st.stop()
client = OpenAI(api_key=api_key)

# =========================
# LABELS UI
# =========================
LABELS = {
    "FR": {
        "title": "🎨 Atelier Créatif — EDU",
        "subtitle": "Créez facilement des histoires, poèmes, chansons ou saynettes pour vos élèves (6–14 ans). Répondez aux questions ➝ téléchargez en PDF ✨",
        "choose_lang": "🌍 Choisissez la langue et l’activité",
        "author": "✍️ Auteur",
        "author_name": "Nom de l’auteur :",
        "answer": "📝 Répondez aux questions",
        "hint": "💡 Utilisez les suggestions en cliquant dessus ou ajoutez votre idée.",
        "generate": "🪄 Générer le texte",
        "pdf_dl": "⬇️ Télécharger en PDF",
        "carousel_prompt": "Sélectionne une image",
        "tagline": "✨ Crée une histoire magique avec tes élèves",
        "result_title": "✨ Voici votre création :",
        "need_answers": "⚠️ Veuillez répondre à au moins une question.",
        "writing": "⏳ Veuillez patienter, votre œuvre est en construction...",
        "tries_left": "Il vous reste {n} essai(s) sur 5.",
        "secure_api": "💡 Votre clé OpenAI est sécurisée via Streamlit Cloud (Secrets).",
        "inspirations": "🎬 Inspirations",
        "default_author": "Ma classe",
        "identify": "👤 Identification (Nom ou Email)"
    },
    "EN": {
        "title": "🎨 Creative Workshop — EDU",
        "subtitle": "Easily create stories, poems, songs or skits for students (6–14). Answer the prompts ➝ download as PDF ✨",
        "choose_lang": "🌍 Choose the language and activity",
        "author": "✍️ Author",
        "author_name": "Author’s name:",
        "answer": "📝 Answer the questions",
        "hint": "💡 Use the suggestions by clicking them or add your own idea.",
        "generate": "🪄 Generate text",
        "pdf_dl": "⬇️ Download PDF",
        "carousel_prompt": "Pick an image",
        "tagline": "✨ Create a magical story with your students",
        "result_title": "✨ Here is your creation:",
        "need_answers": "⚠️ Please answer at least one question.",
        "writing": "⏳ Please wait, your creation is being written...",
        "tries_left": "You have {n} of 5 tries left.",
        "secure_api": "💡 Your OpenAI key is secured via Streamlit Cloud (Secrets).",
        "inspirations": "🎬 Inspirations",
        "default_author": "My class",
        "identify": "👤 Identification (Name or Email)"
    },
    # Ajoute ES, DE, IT pareil...
}

# =========================
# ETAT INITIAL
# =========================
if "lang" not in st.session_state:
    st.session_state.lang = "FR"
lang = st.session_state.lang

# =========================
# TITRE + IDENTIFICATION
# =========================
st.markdown(f"<h1 style='text-align:center;color:#ff69b4'>{LABELS[lang]['title']}</h1>", unsafe_allow_html=True)
st.caption(LABELS[lang]["subtitle"])
st.info(LABELS[lang]["secure_api"])

st.markdown(f"### {LABELS[lang]['identify']}")
user_id = st.text_input("", "")
if not user_id:
    st.warning("⚠️ Merci d’entrer votre nom/email pour continuer.")
    st.stop()

# Initialiser quota individuel
if f"essais_{user_id}" not in st.session_state:
    st.session_state[f"essais_{user_id}"] = 0

# Fonction log
def log_usage(user, lang, activity, essais):
    with open("logs.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), user, lang, activity, essais])

# =========================
# INSPIRATIONS (CARROUSEL)
# =========================
st.markdown("## " + LABELS[lang]["inspirations"])
images = [
    {"file": "slide1.jpg", "caption": LABELS[lang]["tagline"]},
    {"file": "slide2.jpg", "caption": "🎭"},
    {"file": "slide4.jpg", "caption": "🎵"},
]
slider_val = st.slider(LABELS[lang]["carousel_prompt"], 1, len(images), 1)
current = images[slider_val - 1]
st.image(current["file"], use_container_width=True, caption=current["caption"])

# =========================
# LANGUE + ACTIVITÉ
# =========================
st.markdown(f"### {LABELS[lang]['choose_lang']}")
lang_buttons = {"🇫🇷 FR": "FR", "🇬🇧 EN": "EN"}
cols = st.columns(len(lang_buttons))
for i, (label, code) in enumerate(lang_buttons.items()):
    if cols[i].button(label):
        st.session_state.lang = code
        st.rerun()
lang = st.session_state.lang

activities = ["Histoire", "Saynette", "Poème", "Chanson", "Libre"]
cols = st.columns(len(activities))
for i, act in enumerate(activities):
    if cols[i].button(act):
        st.session_state.activity = act
if "activity" not in st.session_state:
    st.session_state.activity = "Histoire"
activity = st.session_state.activity

# =========================
# CHAMP AUTEUR
# =========================
st.markdown(f"### {LABELS[lang]['author']}")
author = st.text_input(LABELS[lang]["author_name"], LABELS[lang]["default_author"])

# =========================
# CHAMP AUTEUR
# =========================
st.markdown(f"### {LABELS[lang]['author']}")
author = st.text_input(LABELS[lang]["author_name"], "Ma classe")

# =========================
# QPACK COMPLET (questions + suggestions)
# =========================
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
            {"q": "Personnages ?", "sug": ["Deux amis", "Prof et élève", "Frères/soeurs"]},
            {"q": "Lieu ?", "sug": ["Cantine", "Bus", "Gymnase"]},
            {"q": "Conflit ?", "sug": ["Quiproquo", "Objet perdu", "Concours raté"]},
        ],
        "Poème": [
            {"q": "Sujet du poème ?", "sug": ["Amitié", "Nature", "Courage"]},
            {"q": "Ambiance ?", "sug": ["Joyeuse", "Rêveuse", "Épique"]},
            {"q": "Rimes ?", "sug": ["Croisées", "Embrassées", "Libres"]},
        ],
        "Chanson": [
            {"q": "Thème de la chanson ?", "sug": ["Voyage scolaire", "Fête de fin d’année", "Étoiles"]},
            {"q": "Rythme ?", "sug": ["Vif", "Modéré", "Lent"]},
            {"q": "Refrain sur…", "sug": ["L’amitié", "La classe", "Le rêve"]},
        ],
        "Libre": [
            {"q": "Type de texte ?", "sug": ["Lettre", "Journal", "Dialogue"]},
            {"q": "Sujet ?", "sug": ["Un secret", "Une découverte", "Un défi"]},
            {"q": "Ton ?", "sug": ["Humoristique", "Poétique", "Émouvant"]},
        ],
    },
    "EN": {
        "Histoire": [
            {"q": "Hero/heroine?", "sug": ["Curious girl", "Inventor boy", "Talking cat"]},
            {"q": "Setting?", "sug": ["Schoolyard", "Magic forest", "School bus"]},
            {"q": "Goal?", "sug": ["Find a treasure", "Help a friend", "Win a contest"]},
            {"q": "Obstacle?", "sug": ["Storm", "Jealous rival", "Maze"]},
            {"q": "Ally?", "sug": ["Best friend", "Teacher", "Squirrel"]},
        ],
        "Saynette": [
            {"q": "Characters?", "sug": ["Two friends", "Teacher & student", "Siblings"]},
            {"q": "Place?", "sug": ["Cafeteria", "Bus", "Gym"]},
            {"q": "Conflict?", "sug": ["Misunderstanding", "Lost item", "Failed contest"]},
        ],
        "Poème": [
            {"q": "Poem topic?", "sug": ["Friendship", "Nature", "Courage"]},
            {"q": "Mood?", "sug": ["Cheerful", "Dreamy", "Epic"]},
            {"q": "Rhyme scheme?", "sug": ["Crossed", "Enclosed", "Free verse"]},
        ],
        "Chanson": [
            {"q": "Song theme?", "sug": ["School trip", "Year-end party", "Stars"]},
            {"q": "Tempo?", "sug": ["Fast", "Medium", "Slow"]},
            {"q": "Chorus about…", "sug": ["Friendship", "The class", "A dream"]},
        ],
        "Libre": [
            {"q": "Text type?", "sug": ["Letter", "Diary", "Dialogue"]},
            {"q": "Topic?", "sug": ["A secret", "A discovery", "A challenge"]},
            {"q": "Tone?", "sug": ["Humorous", "Poetic", "Touching"]},
        ],
    },
    "ES": {
        "Histoire": [
            {"q": "¿Héroe/heroína?", "sug": ["Niña curiosa", "Niño inventor", "Gato que habla"]},
            {"q": "¿Lugar?", "sug": ["Patio escolar", "Bosque mágico", "Autobús escolar"]},
            {"q": "¿Meta?", "sug": ["Encontrar un tesoro", "Ayudar a un amigo", "Ganar un concurso"]},
            {"q": "¿Obstáculo?", "sug": ["Tormenta", "Rival celoso", "Laberinto"]},
            {"q": "¿Aliado?", "sug": ["Mejor amigo", "Profesor", "Ardilla"]},
        ],
        "Saynette": [
            {"q": "¿Personajes?", "sug": ["Dos amigos", "Profesor y alumno", "Hermanos"]},
            {"q": "¿Lugar?", "sug": ["Comedor", "Autobús", "Gimnasio"]},
            {"q": "¿Conflicto?", "sug": ["Malentendido", "Objeto perdido", "Concurso fallido"]},
        ],
        "Poème": [
            {"q": "¿Tema del poema?", "sug": ["Amistad", "Naturaleza", "Valor"]},
            {"q": "¿Ambiente?", "sug": ["Alegre", "Soñador", "Épico"]},
            {"q": "¿Rima?", "sug": ["Cruzada", "Abrazada", "Verso libre"]},
        ],
        "Chanson": [
            {"q": "¿Tema de la canción?", "sug": ["Viaje escolar", "Fiesta de fin de curso", "Estrellas"]},
            {"q": "¿Ritmo?", "sug": ["Rápido", "Medio", "Lento"]},
            {"q": "Estribillo sobre…", "sug": ["La amistad", "La clase", "El sueño"]},
        ],
        "Libre": [
            {"q": "¿Tipo de texto?", "sug": ["Carta", "Diario", "Diálogo"]},
            {"q": "¿Tema?", "sug": ["Un secreto", "Un descubrimiento", "Un reto"]},
            {"q": "¿Tono?", "sug": ["Humorístico", "Poético", "Emotivo"]},
        ],
    },
    "DE": {
        "Histoire": [
            {"q": "Held/Heldin?", "sug": ["Neugieriges Mädchen", "Erfinderjunge", "Sprechende Katze"]},
            {"q": "Ort?", "sug": ["Schulhof", "Zauberwald", "Schulbus"]},
            {"q": "Ziel?", "sug": ["Einen Schatz finden", "Einem Freund helfen", "Wettbewerb gewinnen"]},
            {"q": "Hindernis?", "sug": ["Sturm", "Eifersüchtiger Rivale", "Labyrinth"]},
            {"q": "Verbündeter?", "sug": ["Beste Freundin", "Lehrer", "Eichhörnchen"]},
        ],
        "Saynette": [
            {"q": "Charaktere?", "sug": ["Zwei Freunde", "Lehrer & Schüler", "Geschwister"]},
            {"q": "Ort?", "sug": ["Kantine", "Bus", "Turnhalle"]},
            {"q": "Konflikt?", "sug": ["Missverständnis", "Verlorener Gegenstand", "Gescheiterter Wettbewerb"]},
        ],
        "Poème": [
            {"q": "Thema des Gedichts?", "sug": ["Freundschaft", "Natur", "Mut"]},
            {"q": "Stimmung?", "sug": ["Fröhlich", "Träumerisch", "Episch"]},
            {"q": "Reimschema?", "sug": ["Kreuzreim", "Umarmender Reim", "Freier Vers"]},
        ],
        "Chanson": [
            {"q": "Thema des Liedes?", "sug": ["Klassenfahrt", "Abschlussfeier", "Sterne"]},
            {"q": "Tempo?", "sug": ["Schnell", "Mittel", "Langsam"]},
            {"q": "Refrain über…", "sug": ["Freundschaft", "Die Klasse", "Einen Traum"]},
        ],
        "Libre": [
            {"q": "Textart?", "sug": ["Brief", "Tagebuch", "Dialog"]},
            {"q": "Thema?", "sug": ["Ein Geheimnis", "Eine Entdeckung", "Eine Herausforderung"]},
            {"q": "Ton?", "sug": ["Humorvoll", "Poetisch", "Berührend"]},
        ],
    },
    "IT": {
        "Histoire": [
            {"q": "Eroe/eroina?", "sug": ["Ragazza curiosa", "Ragazzo inventore", "Gatto parlante"]},
            {"q": "Luogo?", "sug": ["Cortile della scuola", "Foresta magica", "Scuolabus"]},
            {"q": "Obiettivo?", "sug": ["Trovare un tesoro", "Aiutare un amico", "Vincere un concorso"]},
            {"q": "Ostacolo?", "sug": ["Tempesta", "Rivale geloso", "Labirinto"]},
            {"q": "Alleato?", "sug": ["Migliore amica", "Insegnante", "Scoiattolo"]},
        ],
        "Saynette": [
            {"q": "Personaggi?", "sug": ["Due amici", "Professore e studente", "Fratelli"]},
            {"q": "Luogo?", "sug": ["Mensa", "Autobus", "Palestra"]},
            {"q": "Conflitto?", "sug": ["Equivoco", "Oggetto perso", "Concorso fallito"]},
        ],
        "Poème": [
            {"q": "Tema della poesia?", "sug": ["Amicizia", "Natura", "Coraggio"]},
            {"q": "Atmosfera?", "sug": ["Allegra", "Sognante", "Epica"]},
            {"q": "Schema di rima?", "sug": ["Alternata", "Chiusa", "Verso libero"]},
        ],
        "Chanson": [
            {"q": "Tema della canzone?", "sug": ["Gita scolastica", "Festa di fine anno", "Stelle"]},
            {"q": "Tempo?", "sug": ["Veloce", "Medio", "Lento"]},
            {"q": "Ritornello su…", "sug": ["L'amicizia", "La classe", "Un sogno"]},
        ],
        "Libre": [
            {"q": "Tipo di testo?", "sug": ["Lettera", "Diario", "Dialogo"]},
            {"q": "Tema?", "sug": ["Un segreto", "Una scoperta", "Una sfida"]},
            {"q": "Tono?", "sug": ["Umoristico", "Poetico", "Emozionante"]},
        ],
    },
}
# =========================
# Placeholders multilingues
# =========================
placeholders = {
    "FR": "Votre idée ou une suggestion…",
    "EN": "Your idea or a suggestion…",
    "ES": "Tu idea o una sugerencia…",
    "DE": "Deine Idee oder ein Vorschlag…",
    "IT": "La tua idea o un suggerimento…",
}
# =========================
# AFFICHAGE QUESTIONS
# =========================
st.markdown(f"### {LABELS[lang]['answer']}")
st.caption(LABELS[lang]["hint"])

placeholders = {
    "FR": "Votre idée ou une suggestion…",
    "EN": "Your idea or a suggestion…",
    "ES": "Tu idea o una sugerencia…",
    "DE": "Deine Idee oder ein Vorschlag…",
    "IT": "La tua idea o un suggerimento…",
}

answers = []
questions = QPACK.get(lang, QPACK["FR"]).get(activity, [])
progress = st.progress(0)

for i, q in enumerate(questions, start=1):
    st.markdown(f"<div class='question-card'><b>{i}. {q['q']}</b></div>", unsafe_allow_html=True)
    key_text = f"answer_{activity}_{lang}_{i}"
    cols = st.columns(len(q["sug"]))
    for j, sug in enumerate(q["sug"]):
        if cols[j].button(sug, key=f"btn_{activity}_{lang}_{i}_{j}"):
            st.session_state[key_text] = sug
    val = st.text_input(" ", key=key_text, label_visibility="collapsed", placeholder=placeholders.get(lang, "Votre idée ou une suggestion…"))
    answers.append(val)
    progress.progress(int(i / max(1, len(questions)) * 100))

# Afficher quota
st.caption(LABELS[lang]["tries_left"].format(n=max(0, 5 - st.session_state[f"essais_{user_id}"])))

# =========================
# GENERATION TEXTE + PDF
# =========================
if st.button(LABELS[lang]["generate"], use_container_width=True, type="primary"):
    if not any(answers):
        st.error(LABELS[lang]["need_answers"])
    else:
        if st.session_state[f"essais_{user_id}"] >= 5:
            st.warning("🚫 Vous avez atteint vos 5 essais gratuits.")
        else:
            st.session_state[f"essais_{user_id}"] += 1
            log_usage(user_id, lang, activity, st.session_state[f"essais_{user_id}"])
            with st.spinner(LABELS[lang]["writing"]):
                try:
                    prompt = f"Langue : {lang}. Activité : {activity}. Auteur : {author}\n"
                    prompt += "Crée un texte adapté aux enfants (6–14 ans), positif, créatif et bienveillant.\n"
                    if activity == "Poème":
                        prompt += "Forme poétique simple et rythmée; 8–16 vers max.\n"
                    elif activity == "Chanson":
                        prompt += "Couplets courts + refrain simple et mémorisable.\n"
                    elif activity == "Saynette":
                        prompt += "Petit dialogue théâtral (2–4 personnages), 6–12 répliques.\n"
                    elif activity == "Histoire":
                        prompt += "Structure courte: début, problème, solution, fin heureuse.\n"

                    for k, a in enumerate(answers, 1):
                        if a:
                            prompt += f"Q{k}: {a}\n"

                    # OpenAI
                    resp = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Tu es un assistant créatif pour enfants."},
                            {"role": "user", "content": prompt},
                        ],
                        temperature=0.9,
                        max_tokens=700,
                    )
                    story = resp.choices[0].message.content.strip()

                    # Résultat
                    st.success(LABELS[lang]["result_title"])
                    st.markdown(f"<div class='result-box'>{story}</div>", unsafe_allow_html=True)

                    # Export PDF
                    def create_pdf(text: str) -> str:
                        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                        c = canvas.Canvas(tmp_file.name, pagesize=A4)
                        width, height = A4
                        c.setFont("Helvetica-Bold", 22)
                        c.drawCentredString(width/2, height - 4*cm, "Atelier Créatif — EDU")
                        c.setFont("Helvetica", 16)
                        c.drawCentredString(width/2, height - 5*cm, activity)
                        c.setFont("Helvetica-Oblique", 10)
                        c.drawCentredString(width/2, height - 6*cm, datetime.now().strftime("%d/%m/%Y"))
                        c.showPage()
                        c.setFont("Helvetica", 12)
                        y = height - 3*cm
                        for line in text.split("\n"):
                            parts = [line[i:i+90] for i in range(0, len(line), 90)] if line else [""]
                            for sub in parts:
                                c.drawString(2*cm, y, sub)
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
                            label=LABELS[lang]["pdf_dl"],
                            data=f,
                            file_name="atelier_creatif.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                except Exception as e:
                    st.error(f"❌ Erreur OpenAI : {e}")
