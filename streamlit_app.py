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
    .suggestion-btn:hover { background: #bae7ff; }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------
# OPENAI
# -----------------------
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    st.error("⚠️ Aucune clé API trouvée. Ajoutez OPENAI_API_KEY dans les Secrets Streamlit Cloud.")
    st.stop()
client = OpenAI(api_key=api_key)

# -----------------------
# LABELS UI (TRADUCTIONS)
# -----------------------
LABELS = {
    "FR": {
        "choose_activity": "🌍 Choisissez la langue et l’activité",
        "author": "✍️ Auteur",
        "author_name": "Nom de l’auteur :",
        "answer": "📝 Répondez aux questions",
        "hint": "💡 Utilisez les suggestions en cliquant dessus ou ajoutez votre idée.",
        "generate": "🪄 Générer le texte",
        "tagline": "✨ Crée une histoire magique avec tes élèves"
    },
    "EN": {
        "choose_activity": "🌍 Choose the language and activity",
        "author": "✍️ Author",
        "author_name": "Author’s name:",
        "answer": "📝 Answer the questions",
        "hint": "💡 Use the suggestions by clicking them or add your own idea.",
        "generate": "🪄 Generate text",
        "tagline": "✨ Create a magical story with your students"
    },
    "ES": {
        "choose_activity": "🌍 Elige el idioma y la actividad",
        "author": "✍️ Autor",
        "author_name": "Nombre del autor:",
        "answer": "📝 Responde a las preguntas",
        "hint": "💡 Usa las sugerencias haciendo clic o añade tu propia idea.",
        "generate": "🪄 Generar texto",
        "tagline": "✨ Crea una historia mágica con tus alumnos"
    },
    "DE": {
        "choose_activity": "🌍 Wähle die Sprache und Aktivität",
        "author": "✍️ Autor",
        "author_name": "Name des Autors:",
        "answer": "📝 Beantworte die Fragen",
        "hint": "💡 Nutze die Vorschläge oder füge deine eigene Idee hinzu.",
        "generate": "🪄 Text generieren",
        "tagline": "✨ Erstelle eine magische Geschichte mit deinen Schülern"
    },
    "IT": {
        "choose_activity": "🌍 Scegli la lingua e l’attività",
        "author": "✍️ Autore",
        "author_name": "Nome dell’autore:",
        "answer": "📝 Rispondi alle domande",
        "hint": "💡 Usa i suggerimenti facendo clic o aggiungi la tua idea.",
        "generate": "🪄 Genera il testo",
        "tagline": "✨ Crea una storia magica con i tuoi studenti"
    }
}

# Libellés des activités (les codes d’activité restent FR pour la logique)
ACTIVITY_LABELS = {
    "FR": {"Histoire": "📚 Histoire", "Saynette": "🎭 Saynette", "Poème": "✒️ Poème", "Chanson": "🎵 Chanson", "Libre": "✨ Libre"},
    "EN": {"Histoire": "📚 Story", "Saynette": "🎭 Skit", "Poème": "✒️ Poem", "Chanson": "🎵 Song", "Libre": "✨ Free"},
    "ES": {"Histoire": "📚 Historia", "Saynette": "🎭 Escenita", "Poème": "✒️ Poema", "Chanson": "🎵 Canción", "Libre": "✨ Libre"},
    "DE": {"Histoire": "📚 Geschichte", "Saynette": "🎭 Sketch", "Poème": "✒️ Gedicht", "Chanson": "🎵 Lied", "Libre": "✨ Frei"},
    "IT": {"Histoire": "📚 Storia", "Saynette": "🎭 Scenetta", "Poème": "✒️ Poesia", "Chanson": "🎵 Canzone", "Libre": "✨ Libero"},
}

# -----------------------
# TITRE
# -----------------------
st.markdown("<h1 style='text-align: center; color: #ff69b4;'>🎨 Atelier Créatif — EDU</h1>", unsafe_allow_html=True)
st.info("💡 Votre clé OpenAI est sécurisée via Streamlit Cloud (Secrets).")

# Par défaut, langue = FR (avant tout usage de LABELS)
if "lang" not in st.session_state:
    st.session_state.lang = "FR"
lang = st.session_state.lang

# -----------------------
# CARROUSEL IMAGES
# -----------------------
st.markdown("## 🎬 Inspirations")
images = [
    {"file": "slide1.jpg", "caption": LABELS[lang]["tagline"]},
    {"file": "slide2.jpg", "caption": "🎭"},
    {"file": "slide4.jpg", "caption": "🎵"},
]
if "carousel_index" not in st.session_state:
    st.session_state.carousel_index = 0

slider_val = st.slider(
    "Sélectionne une image",
    min_value=1, max_value=len(images),
    value=st.session_state.carousel_index + 1,
    key="carousel_slider"
)
st.session_state.carousel_index = slider_val - 1
current = images[st.session_state.carousel_index]
if os.path.exists(current["file"]):
    st.image(current["file"], use_container_width=True, caption=current["caption"])
else:
    st.warning(f"Image introuvable : {current['file']}")

c1, _, c3 = st.columns([1,6,1])
with c1:
    if st.button("⬅️"):
        st.session_state.carousel_index = (st.session_state.carousel_index - 1) % len(images)
        st.session_state.carousel_slider = st.session_state.carousel_index + 1
with c3:
    if st.button("➡️"):
        st.session_state.carousel_index = (st.session_state.carousel_index + 1) % len(images)
        st.session_state.carousel_slider = st.session_state.carousel_index + 1

# -----------------------
# LANGUE & ACTIVITÉ
# -----------------------
st.markdown(f"### {LABELS[lang]['choose_activity']}")

# Choix langue
lang_buttons = {"🇫🇷 FR": "FR", "🇬🇧 EN": "EN", "🇪🇸 ES": "ES", "🇩🇪 DE": "DE", "🇮🇹 IT": "IT"}
cols = st.columns(len(lang_buttons))
for i, (label, code) in enumerate(lang_buttons.items()):
    if cols[i].button(label):
        st.session_state.lang = code
        st.rerun()
lang = st.session_state.lang  # rafraîchi après clic

# Choix activité (libellés traduits)
if "activity" not in st.session_state:
    st.session_state.activity = "Histoire"
activity = st.session_state.activity

cols = st.columns(5)
ACTS = ["Histoire", "Saynette", "Poème", "Chanson", "Libre"]
for i, act in enumerate(ACTS):
    if cols[i].button(ACTIVITY_LABELS[lang][act]):
        st.session_state.activity = act
        activity = act

# -----------------------
# AUTEUR
# -----------------------
st.markdown(f"### {LABELS[lang]['author']}")
author = st.text_input(LABELS[lang]['author_name'], "Ma classe")

# -----------------------
# QPACK (questions/suggestions) – 5 activités × 5 langues
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

# -----------------------
# QUESTIONS + SUGGESTIONS (sécurisé)
# -----------------------
st.markdown(f"### {LABELS[lang]['answer']}")
st.caption(LABELS[lang]['hint'])

answers = []
questions = QPACK.get(lang, QPACK["FR"]).get(activity, [])
progress = st.progress(0)

for i, q in enumerate(questions, start=1):
    with st.container():
        st.markdown(f"<div class='card'><b>{i}. {q['q']}</b></div>", unsafe_allow_html=True)

        # valeur par défaut
        if f"q{i}" not in st.session_state:
            st.session_state[f"q{i}"] = ""

        # champ lié à session_state
        val = st.text_input("", key=f"q{i}")

        # suggestions
        sug_cols = st.columns(len(q["sug"]))
        for j, sug in enumerate(q["sug"]):
            if sug_cols[j].button(sug, key=f"sug{i}_{j}"):
                st.session_state[f"q{i}"] = sug
                val = sug

        answers.append(val)

    progress.progress(int(i / max(1, len(questions)) * 100))

# -----------------------
# GÉNÉRATION + PDF
# -----------------------
if st.button(LABELS[lang]["generate"], use_container_width=True, type="primary"):
    if not any(answers):
        st.error("⚠️ Veuillez répondre à au moins une question.")
    else:
        with st.spinner("✍️ L'IA écrit votre création..."):
            # texte affiché de l'activité dans la langue choisie
            activity_display = ACTIVITY_LABELS[lang][activity]

            prompt = (
                f"Langue: {lang}. Activité: {activity_display}. "
                f"Crée un texte adapté aux enfants (6–14 ans), positif et créatif.\n"
                f"Auteur: {author}\n"
            )
            for idx, a in enumerate(answers, 1):
                if a:
                    prompt += f"Q{idx}: {a}\n"

            try:
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Tu es un assistant créatif pour enfants."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.9,
                    max_tokens=350,
                )
                story = resp.choices[0].message.content.strip()

                st.success("✨ Voici votre création :")
                st.markdown(
                    f"<div style='background:#fff0f6; padding:15px; border-radius:10px;'>{story}</div>",
                    unsafe_allow_html=True
                )

                # PDF
                def create_pdf(text):
                    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                    c = canvas.Canvas(tmp_file.name, pagesize=A4)
                    width, height = A4

                    c.setFont("Helvetica-Bold", 22)
                    c.drawCentredString(width/2, height - 4*cm, "Atelier Créatif — EDU")
                    c.setFont("Helvetica", 16)
                    c.drawCentredString(width/2, height - 5*cm, activity_display)
                    c.setFont("Helvetica-Oblique", 10)
                    c.drawCentredString(width/2, height - 6*cm, datetime.now().strftime("%d/%m/%Y"))

                    # Page texte
                    c.showPage()
                    c.setFont("Helvetica", 12)
                    y = height - 3*cm
                    for line in text.split("\n"):
                        for sub in [line[i:i+90] for i in range(0, len(line), 90)]:
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
                        label="⬇️ Télécharger en PDF",
                        data=f,
                        file_name="atelier_creatif.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"❌ Erreur OpenAI : {e}")
