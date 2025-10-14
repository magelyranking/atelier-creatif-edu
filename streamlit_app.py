import streamlit as st
from openai import OpenAI
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import tempfile
from datetime import datetime
import os, csv
import pandas as pd
from pathlib import Path

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
        "subtitle": "Créez facilement des histoires, poèmes, chansons ou saynettes pour vos élèves (6–14 ans).",
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
        "identify": "👤 Identification (Nom ou email)",
        "activities": {
            "Histoire": "📖 Histoire",
            "Saynette": "🎭 Saynette",
            "Poème": "✒️ Poème",
            "Chanson": "🎵 Chanson",
            "Libre": "✨ Libre"
        }
    },
    "EN": {
        "title": "🎨 Creative Workshop — EDU",
        "subtitle": "Easily create stories, poems, songs or skits for students (6–14).",
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
        "identify": "👤 Identification (Name or email)",
        "activities": {
            "Histoire": "📖 Story",
            "Saynette": "🎭 Skit",
            "Poème": "✒️ Poem",
            "Chanson": "🎵 Song",
            "Libre": "✨ Free"
        }
    },
    "ES": {
        "title": "🎨 Taller Creativo — EDU",
        "subtitle": "Crea fácilmente historias, poemas, canciones o escenitas para alumnos (6–14).",
        "choose_lang": "🌍 Elige el idioma y la actividad",
        "author": "✍️ Autor",
        "author_name": "Nombre del autor:",
        "answer": "📝 Responde a las preguntas",
        "hint": "💡 Usa las sugerencias haciendo clic o añade tu propia idea.",
        "generate": "🪄 Generar texto",
        "pdf_dl": "⬇️ Descargar en PDF",
        "carousel_prompt": "Selecciona una imagen",
        "tagline": "✨ Crea una historia mágica con tus alumnos",
        "result_title": "✨ Aquí está tu creación:",
        "need_answers": "⚠️ Responde al menos a una pregunta.",
        "writing": "⏳ Espere, su obra está en construcción...",
        "tries_left": "Te quedan {n} de 5 intentos.",
        "secure_api": "💡 Tu clave OpenAI está segura en Streamlit Cloud (Secrets).",
        "inspirations": "🎬 Inspiraciones",
        "default_author": "Mi clase",
        "identify": "👤 Identificación (Nombre o correo)",
        "activities": {
            "Histoire": "📖 Historia",
            "Saynette": "🎭 Escenita",
            "Poème": "✒️ Poema",
            "Chanson": "🎵 Canción",
            "Libre": "✨ Libre"
        }
    },
    "DE": {
        "title": "🎨 Kreativwerkstatt — EDU",
        "subtitle": "Erstelle leicht Geschichten, Gedichte, Lieder oder Sketche für Schüler (6–14).",
        "choose_lang": "🌍 Wähle die Sprache und Aktivität",
        "author": "✍️ Autor",
        "author_name": "Name des Autors:",
        "answer": "📝 Beantworte die Fragen",
        "hint": "💡 Nutze die Vorschläge per Klick oder füge deine eigene Idee hinzu.",
        "generate": "🪄 Text generieren",
        "pdf_dl": "⬇️ Als PDF herunterladen",
        "carousel_prompt": "Wähle ein Bild",
        "tagline": "✨ Erstelle eine magische Geschichte mit deinen Schülern",
        "result_title": "✨ Hier ist deine Erstellung:",
        "need_answers": "⚠️ Bitte beantworte mindestens eine Frage.",
        "writing": "⏳ Bitte warten, dein Werk wird erstellt...",
        "tries_left": "Du hast noch {n} von 5 Versuchen.",
        "secure_api": "💡 Dein OpenAI-Schlüssel ist in Streamlit Cloud (Secrets) gesichert.",
        "inspirations": "🎬 Inspirationen",
        "default_author": "Meine Klasse",
        "identify": "👤 Identifikation (Name oder E-Mail)",
        "activities": {
            "Histoire": "📖 Geschichte",
            "Saynette": "🎭 Sketch",
            "Poème": "✒️ Gedicht",
            "Chanson": "🎵 Lied",
            "Libre": "✨ Frei"
        }
    },
    "IT": {
        "title": "🎨 Laboratorio Creativo — EDU",
        "subtitle": "Crea facilmente storie, poesie, canzoni o scenette per studenti (6–14).",
        "choose_lang": "🌍 Scegli la lingua e l’attività",
        "author": "✍️ Autore",
        "author_name": "Nome dell’autore:",
        "answer": "📝 Rispondi alle domande",
        "hint": "💡 Usa i suggerimenti con un clic oppure aggiungi la tua idea.",
        "generate": "🪄 Genera il testo",
        "pdf_dl": "⬇️ Scarica in PDF",
        "carousel_prompt": "Seleziona un’immagine",
        "tagline": "✨ Crea una storia magica con i tuoi studenti",
        "result_title": "✨ Ecco la tua creazione:",
        "need_answers": "⚠️ Rispondi ad almeno una domanda.",
        "writing": "⏳ Attendere, la tua opera è in costruzione...",
        "tries_left": "Ti restano {n} tentativi su 5.",
        "secure_api": "💡 La tua chiave OpenAI è protetta in Streamlit Cloud (Secrets).",
        "inspirations": "🎬 Ispirazioni",
        "default_author": "La mia classe",
        "identify": "👤 Identificazione (Nome o Email)",
        "activities": {
            "Histoire": "📖 Storia",
            "Saynette": "🎭 Scenetta",
            "Poème": "✒️ Poesia",
            "Chanson": "🎵 Canzone",
            "Libre": "✨ Libero"
        }
    }
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
user_id = st.text_input("", "", key="user_id_input")
if not user_id:
    st.warning("⚠️ Merci d’entrer votre nom/email pour continuer.")
    st.stop()

# Initialiser quota individuel
if f"essais_{user_id}" not in st.session_state:
    st.session_state[f"essais_{user_id}"] = 0

# Fonction log
def log_usage(user_id: str, lang: str, activity: str, essais: int):
    """Log l'utilisation dans logs.csv (crée le fichier si besoin)."""
    log_file = Path("logs.csv")
    file_exists = log_file.exists()

    # Colonnes toujours les mêmes
    headers = ["timestamp", "user_id", "lang", "activity", "essais"]

    with open(log_file, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # écrire l'entête si le fichier est nouveau
        if not file_exists:
            writer.writerow(headers)
        # écrire la ligne
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user_id if user_id else "inconnu",
            lang,
            activity,
            essais
        ])

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

# Sélecteur de langue (radio avec 5 options)
lang = st.radio(
    LABELS[st.session_state.get("lang", "FR")]['choose_lang'],
    options=["FR", "EN", "ES", "DE", "IT"],
    format_func=lambda x: {
        "FR": "🇫🇷 Français",
        "EN": "🇬🇧 English",
        "ES": "🇪🇸 Español",
        "DE": "🇩🇪 Deutsch",
        "IT": "🇮🇹 Italiano"
    }[x],
    horizontal=True,
    index=["FR", "EN", "ES", "DE", "IT"].index(st.session_state.get("lang", "FR"))
)
st.session_state.lang = lang
lang = st.session_state.lang

# =========================
# ACTIVITÉS traduites
# =========================
activities = ["Histoire", "Saynette", "Poème", "Chanson", "Libre"]

cols = st.columns(len(activities))
for i, act in enumerate(activities):
    label = LABELS[lang]["activities"][act]  # traduction
    if cols[i].button(label, key=f"act_{act}"):
        st.session_state.activity = act

if "activity" not in st.session_state:
    st.session_state.activity = "Histoire"

activity = st.session_state.activity


# =========================
# CHAMP AUTEUR
# =========================
st.markdown(f"### {LABELS[lang]['author']}")
author = st.text_input(LABELS[lang]["author_name"], LABELS[lang]["default_author"], key="author_input")

# =========================
# QPACK COMPLET (questions + suggestions)
# =========================
QPACK = {
    "FR": {
        "Histoire": [
            {"q": "Héros/héroïne ?", "sug": ["Fillette curieuse", "Garçon inventeur", "Chat qui parle"]},
            {"q": "Lieu principal ?", "sug": ["Cour d’école", "Forêt magique", "Bus scolaire"]},
            {"q": "Objectif ?", "sug": ["Retrouver un trésor", "Aider un ami", "Gagner un concours"]},
            {"q": "Obstacle ?", "sug": ["Orage", "Rival jaloux", "Labyrinthe"]},
            {"q": "Allié ?", "sug": ["Meilleure amie", "Professeur", "Écureuil"]},
            {"q": "Ton de l’histoire ?", "sug": ["Drôle", "Mystérieux", "Épique"]},
            {"q": "Fin souhaitée ?", "sug": ["Heureuse", "Morale", "Surprenante"]},
        ],
        "Saynette": [
            {"q": "Personnages ?", "sug": ["Deux amis", "Prof et élève", "Frères/soeurs"]},
            {"q": "Lieu ?", "sug": ["Cantine", "Bus", "Gymnase"]},
            {"q": "Conflit ?", "sug": ["Quiproquo", "Objet perdu", "Concours raté"]},
            {"q": "Style théâtral ?", "sug": ["Vaudeville", "Drame", "Comédie", "Comédie musicale"]},
            {"q": "Nombre de scènes ?", "sug": ["1", "2", "3"]},
            {"q": "Objet central ?", "sug": ["Un ballon", "Une lettre", "Un gâteau"]},
            {"q": "Fin ?", "sug": ["Réconciliation", "Leçon", "Gag final"]},
        ],
        "Poème": [
            {"q": "Sujet du poème ?", "sug": ["Amitié", "Nature", "Courage"]},
            {"q": "Ambiance ?", "sug": ["Joyeuse", "Rêveuse", "Épique"]},
            {"q": "Style poétique ?", "sug": ["Alexandrin", "Rimes libres", "Haïku"]},
            {"q": "Nombre de strophes ?", "sug": ["2", "3", "4"]},
            {"q": "Émotion principale ?", "sug": ["Douceur", "Rire", "Inspiration"]},
            {"q": "Image centrale ?", "sug": ["Étoile", "Arbre", "Rivière"]},
            {"q": "Public cible ?", "sug": ["6-8 ans", "9-11 ans", "12-14 ans"]},
        ],
        "Chanson": [
            {"q": "Thème ?", "sug": ["Voyage scolaire", "Fête de fin d’année", "Étoiles"]},
            {"q": "Tempo ?", "sug": ["Lent", "Modéré", "Rapide"]},
            {"q": "Style musical ?", "sug": ["Pop", "Jazz", "Rap", "Folk"]},
            {"q": "Sujet du refrain ?", "sug": ["Amitié", "La classe", "Un rêve"]},
            {"q": "Nombre de couplets ?", "sug": ["2", "3", "4"]},
            {"q": "Ambiance ?", "sug": ["Joyeuse", "Nostalgique", "Festive"]},
            {"q": "Public cible ?", "sug": ["6-8 ans", "9-11 ans", "12-14 ans"]},
        ],
        "Libre": [
            {"q": "Type de texte ?", "sug": ["Lettre", "Journal", "Dialogue"]},
            {"q": "Sujet ?", "sug": ["Un secret", "Une découverte", "Un défi"]},
            {"q": "Ton ?", "sug": ["Humoristique", "Poétique", "Émouvant"]},
            {"q": "Lieu ?", "sug": ["École", "Maison", "Forêt"]},
            {"q": "Personnages ?", "sug": ["Un ami", "Un professeur", "Un animal"]},
            {"q": "Objectif ?", "sug": ["Amuser", "Émouvoir", "Faire réfléchir"]},
            {"q": "Style narratif ?", "sug": ["Réaliste", "Imaginaire", "Fantastique"]},
        ],
    },
    "EN": {
        "Histoire": [
            {"q": "Hero/heroine?", "sug": ["Curious girl", "Inventor boy", "Talking cat"]},
            {"q": "Main setting?", "sug": ["Schoolyard", "Magic forest", "School bus"]},
            {"q": "Goal?", "sug": ["Find a treasure", "Help a friend", "Win a contest"]},
            {"q": "Obstacle?", "sug": ["Storm", "Jealous rival", "Maze"]},
            {"q": "Ally?", "sug": ["Best friend", "Teacher", "Squirrel"]},
            {"q": "Tone of the story?", "sug": ["Funny", "Mysterious", "Epic"]},
            {"q": "Desired ending?", "sug": ["Happy", "Moral", "Surprising"]},
        ],
        "Saynette": [
            {"q": "Characters?", "sug": ["Two friends", "Teacher & student", "Siblings"]},
            {"q": "Place?", "sug": ["Cafeteria", "Bus", "Gym"]},
            {"q": "Conflict?", "sug": ["Misunderstanding", "Lost item", "Failed contest"]},
            {"q": "Theatrical style?", "sug": ["Vaudeville", "Drama", "Comedy", "Musical"]},
            {"q": "Number of scenes?", "sug": ["1", "2", "3"]},
            {"q": "Central object?", "sug": ["A ball", "A letter", "A cake"]},
            {"q": "Ending?", "sug": ["Reconciliation", "Lesson", "Final gag"]},
        ],
        "Poème": [
            {"q": "Poem topic?", "sug": ["Friendship", "Nature", "Courage"]},
            {"q": "Mood?", "sug": ["Cheerful", "Dreamy", "Epic"]},
            {"q": "Poetic style?", "sug": ["Alexandrine", "Free verse", "Haiku"]},
            {"q": "Number of stanzas?", "sug": ["2", "3", "4"]},
            {"q": "Main emotion?", "sug": ["Gentleness", "Laughter", "Inspiration"]},
            {"q": "Central image?", "sug": ["Star", "Tree", "River"]},
            {"q": "Target audience?", "sug": ["6-8 years", "9-11 years", "12-14 years"]},
        ],
        "Chanson": [
            {"q": "Song theme?", "sug": ["School trip", "Year-end party", "Stars"]},
            {"q": "Tempo?", "sug": ["Slow", "Medium", "Fast"]},
            {"q": "Musical style?", "sug": ["Pop", "Jazz", "Rap", "Folk"]},
            {"q": "Chorus about?", "sug": ["Friendship", "The class", "A dream"]},
            {"q": "Number of verses?", "sug": ["2", "3", "4"]},
            {"q": "Mood?", "sug": ["Joyful", "Nostalgic", "Festive"]},
            {"q": "Target audience?", "sug": ["6-8 years", "9-11 years", "12-14 years"]},
        ],
        "Libre": [
            {"q": "Text type?", "sug": ["Letter", "Diary", "Dialogue"]},
            {"q": "Topic?", "sug": ["A secret", "A discovery", "A challenge"]},
            {"q": "Tone?", "sug": ["Humorous", "Poetic", "Emotional"]},
            {"q": "Place?", "sug": ["School", "Home", "Forest"]},
            {"q": "Characters?", "sug": ["A friend", "A teacher", "An animal"]},
            {"q": "Purpose?", "sug": ["Entertain", "Move", "Make think"]},
            {"q": "Narrative style?", "sug": ["Realistic", "Imaginary", "Fantastic"]},
        ],
    },
    "ES": {
        "Histoire": [
            {"q": "¿Héroe/heroína?", "sug": ["Niña curiosa", "Niño inventor", "Gato que habla"]},
            {"q": "¿Lugar principal?", "sug": ["Patio escolar", "Bosque mágico", "Autobús escolar"]},
            {"q": "¿Meta?", "sug": ["Encontrar un tesoro", "Ayudar a un amigo", "Ganar un concurso"]},
            {"q": "¿Obstáculo?", "sug": ["Tormenta", "Rival celoso", "Laberinto"]},
            {"q": "¿Aliado?", "sug": ["Mejor amigo", "Profesor", "Ardilla"]},
            {"q": "¿Tono de la historia?", "sug": ["Divertido", "Misterioso", "Épico"]},
            {"q": "¿Final deseado?", "sug": ["Feliz", "Con moraleja", "Sorprendente"]},
        ],
        "Saynette": [
            {"q": "¿Personajes?", "sug": ["Dos amigos", "Profesor y alumno", "Hermanos"]},
            {"q": "¿Lugar?", "sug": ["Comedor", "Autobús", "Gimnasio"]},
            {"q": "¿Conflicto?", "sug": ["Malentendido", "Objeto perdido", "Concurso fallido"]},
            {"q": "¿Estilo teatral?", "sug": ["Vaudeville", "Drama", "Comedia", "Musical"]},
            {"q": "¿Número de escenas?", "sug": ["1", "2", "3"]},
            {"q": "¿Objeto central?", "sug": ["Pelota", "Carta", "Pastel"]},
            {"q": "¿Final?", "sug": ["Reconciliación", "Lección", "Gag final"]},
        ],
        "Poème": [
            {"q": "¿Tema del poema?", "sug": ["Amistad", "Naturaleza", "Valor"]},
            {"q": "¿Ambiente?", "sug": ["Alegre", "Soñador", "Épico"]},
            {"q": "¿Estilo poético?", "sug": ["Alejandrino", "Verso libre", "Haiku"]},
            {"q": "¿Número de estrofas?", "sug": ["2", "3", "4"]},
            {"q": "¿Emoción principal?", "sug": ["Dulzura", "Risa", "Inspiración"]},
            {"q": "¿Imagen central?", "sug": ["Estrella", "Árbol", "Río"]},
            {"q": "¿Público objetivo?", "sug": ["6-8 años", "9-11 años", "12-14 años"]},
        ],
        "Chanson": [
            {"q": "¿Tema de la canción?", "sug": ["Viaje escolar", "Fiesta de fin de curso", "Estrellas"]},
            {"q": "¿Tempo?", "sug": ["Lento", "Medio", "Rápido"]},
            {"q": "¿Estilo musical?", "sug": ["Pop", "Jazz", "Rap", "Folk"]},
            {"q": "¿Estribillo sobre?", "sug": ["Amistad", "La clase", "Un sueño"]},
            {"q": "¿Número de estrofas?", "sug": ["2", "3", "4"]},
            {"q": "¿Ambiente?", "sug": ["Alegre", "Nostálgico", "Festivo"]},
            {"q": "¿Público objetivo?", "sug": ["6-8 años", "9-11 años", "12-14 años"]},
        ],
        "Libre": [
            {"q": "¿Tipo de texto?", "sug": ["Carta", "Diario", "Diálogo"]},
            {"q": "¿Tema?", "sug": ["Un secreto", "Un descubrimiento", "Un reto"]},
            {"q": "¿Tono?", "sug": ["Humorístico", "Poético", "Emotivo"]},
            {"q": "¿Lugar?", "sug": ["Escuela", "Casa", "Bosque"]},
            {"q": "¿Personajes?", "sug": ["Un amigo", "Un profesor", "Un animal"]},
            {"q": "¿Objetivo?", "sug": ["Divertir", "Emocionar", "Hacer pensar"]},
            {"q": "¿Estilo narrativo?", "sug": ["Realista", "Imaginario", "Fantástico"]},
        ],
    },
    "DE": {
        "Histoire": [
            {"q": "Held/Heldin?", "sug": ["Neugieriges Mädchen", "Erfinderjunge", "Sprechende Katze"]},
            {"q": "Hauptort?", "sug": ["Schulhof", "Zauberwald", "Schulbus"]},
            {"q": "Ziel?", "sug": ["Einen Schatz finden", "Einem Freund helfen", "Wettbewerb gewinnen"]},
            {"q": "Hindernis?", "sug": ["Sturm", "Eifersüchtiger Rivale", "Labyrinth"]},
            {"q": "Verbündeter?", "sug": ["Beste Freundin", "Lehrer", "Eichhörnchen"]},
            {"q": "Ton der Geschichte?", "sug": ["Lustig", "Geheimnisvoll", "Episch"]},
            {"q": "Gewünschtes Ende?", "sug": ["Glücklich", "Mit Moral", "Überraschend"]},
        ],
        "Saynette": [
            {"q": "Charaktere?", "sug": ["Zwei Freunde", "Lehrer & Schüler", "Geschwister"]},
            {"q": "Ort?", "sug": ["Kantine", "Bus", "Turnhalle"]},
            {"q": "Konflikt?", "sug": ["Missverständnis", "Verlorener Gegenstand", "Gescheiterter Wettbewerb"]},
            {"q": "Theaterstil?", "sug": ["Vaudeville", "Drama", "Komödie", "Musical"]},
            {"q": "Anzahl der Szenen?", "sug": ["1", "2", "3"]},
            {"q": "Zentrales Objekt?", "sug": ["Ball", "Brief", "Kuchen"]},
            {"q": "Ende?", "sug": ["Versöhnung", "Lehre", "Finaler Gag"]},
        ],
        "Poème": [
            {"q": "Thema des Gedichts?", "sug": ["Freundschaft", "Natur", "Mut"]},
            {"q": "Stimmung?", "sug": ["Fröhlich", "Träumerisch", "Episch"]},
            {"q": "Dichtungsstil?", "sug": ["Alexandriner", "Freier Vers", "Haiku"]},
            {"q": "Anzahl der Strophen?", "sug": ["2", "3", "4"]},
            {"q": "Hauptemotion?", "sug": ["Sanftheit", "Lachen", "Inspiration"]},
            {"q": "Zentrales Bild?", "sug": ["Stern", "Baum", "Fluss"]},
            {"q": "Zielgruppe?", "sug": ["6-8 Jahre", "9-11 Jahre", "12-14 Jahre"]},
        ],
        "Chanson": [
            {"q": "Thema des Liedes?", "sug": ["Klassenfahrt", "Abschlussfeier", "Sterne"]},
            {"q": "Tempo?", "sug": ["Langsam", "Mittel", "Schnell"]},
            {"q": "Musikstil?", "sug": ["Pop", "Jazz", "Rap", "Folk"]},
            {"q": "Refrain über?", "sug": ["Freundschaft", "Die Klasse", "Ein Traum"]},
            {"q": "Anzahl der Strophen?", "sug": ["2", "3", "4"]},
            {"q": "Stimmung?", "sug": ["Fröhlich", "Nostalgisch", "Festlich"]},
            {"q": "Zielgruppe?", "sug": ["6-8 Jahre", "9-11 Jahre", "12-14 Jahre"]},
        ],
        "Libre": [
            {"q": "Textart?", "sug": ["Brief", "Tagebuch", "Dialog"]},
            {"q": "Thema?", "sug": ["Ein Geheimnis", "Eine Entdeckung", "Eine Herausforderung"]},
            {"q": "Ton?", "sug": ["Humorvoll", "Poetisch", "Emotional"]},
            {"q": "Ort?", "sug": ["Schule", "Zuhause", "Wald"]},
            {"q": "Charaktere?", "sug": ["Ein Freund", "Ein Lehrer", "Ein Tier"]},
            {"q": "Ziel?", "sug": ["Unterhalten", "Bewegen", "Zum Nachdenken anregen"]},
            {"q": "Erzählstil?", "sug": ["Realistisch", "Fantastisch", "Imaginär"]},
        ],
    },
    "IT": {
        "Histoire": [
            {"q": "Eroe/eroina?", "sug": ["Ragazza curiosa", "Ragazzo inventore", "Gatto parlante"]},
            {"q": "Luogo principale?", "sug": ["Cortile della scuola", "Foresta magica", "Scuolabus"]},
            {"q": "Obiettivo?", "sug": ["Trovare un tesoro", "Aiutare un amico", "Vincere un concorso"]},
            {"q": "Ostacolo?", "sug": ["Tempesta", "Rivale geloso", "Labirinto"]},
            {"q": "Alleato?", "sug": ["Migliore amica", "Insegnante", "Scoiattolo"]},
            {"q": "Tono della storia?", "sug": ["Divertente", "Misterioso", "Epico"]},
            {"q": "Finale desiderato?", "sug": ["Felice", "Con morale", "Sorpresa"]},
        ],
        "Saynette": [
            {"q": "Personaggi?", "sug": ["Due amici", "Professore e studente", "Fratelli"]},
            {"q": "Luogo?", "sug": ["Mensa", "Autobus", "Palestra"]},
            {"q": "Conflitto?", "sug": ["Equivoco", "Oggetto perso", "Concorso fallito"]},
            {"q": "Stile teatrale?", "sug": ["Vaudeville", "Dramma", "Commedia", "Musical"]},
            {"q": "Numero di scene?", "sug": ["1", "2", "3"]},
            {"q": "Oggetto centrale?", "sug": ["Pallone", "Lettera", "Torta"]},
            {"q": "Finale?", "sug": ["Riconciliazione", "Lezione", "Gag finale"]},
        ],
        "Poème": [
            {"q": "Tema della poesia?", "sug": ["Amicizia", "Natura", "Coraggio"]},
            {"q": "Atmosfera?", "sug": ["Allegra", "Sognante", "Epica"]},
            {"q": "Stile poetico?", "sug": ["Alessandrino", "Verso libero", "Haiku"]},
            {"q": "Numero di strofe?", "sug": ["2", "3", "4"]},
            {"q": "Emozione principale?", "sug": ["Dolcezza", "Risata", "Ispirazione"]},
            {"q": "Immagine centrale?", "sug": ["Stella", "Albero", "Fiume"]},
            {"q": "Pubblico target?", "sug": ["6-8 anni", "9-11 anni", "12-14 anni"]},
        ],
        "Chanson": [
            {"q": "Tema della canzone?", "sug": ["Gita scolastica", "Festa di fine anno", "Stelle"]},
            {"q": "Tempo?", "sug": ["Lento", "Medio", "Veloce"]},
            {"q": "Stile musicale?", "sug": ["Pop", "Jazz", "Rap", "Folk"]},
            {"q": "Ritornello su?", "sug": ["Amicizia", "La classe", "Un sogno"]},
            {"q": "Numero di strofe?", "sug": ["2", "3", "4"]},
            {"q": "Atmosfera?", "sug": ["Allegra", "Nostalgica", "Festosa"]},
            {"q": "Pubblico target?", "sug": ["6-8 anni", "9-11 anni", "12-14 anni"]},
        ],
        "Libre": [
            {"q": "Tipo di testo?", "sug": ["Lettera", "Diario", "Dialogo"]},
            {"q": "Tema?", "sug": ["Un segreto", "Una scoperta", "Una sfida"]},
            {"q": "Tono?", "sug": ["Umoristico", "Poetico", "Emozionante"]},
            {"q": "Luogo?", "sug": ["Scuola", "Casa", "Foresta"]},
            {"q": "Personaggi?", "sug": ["Un amico", "Un insegnante", "Un animale"]},
            {"q": "Obiettivo?", "sug": ["Divertire", "Emozionare", "Far riflettere"]},
            {"q": "Stile narrativo?", "sug": ["Realistico", "Immaginario", "Fantastico"]},
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
from pathlib import Path

# =========================
# SECTION ADMIN (Accès protégé)
# =========================
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔒 Accès administrateur")

admin_code = st.sidebar.text_input("Code admin :", type="password")

if admin_code == os.environ.get("ADMIN_CODE", "1234"):
    st.sidebar.success("✅ Accès admin activé")

    log_file = Path("logs.csv")   # ✅ Défini avant de l’utiliser

    if log_file.exists():
        # Téléchargement CSV
        with open(log_file, "rb") as f:
            st.sidebar.download_button(
                label="⬇️ Télécharger les logs (CSV)",
                data=f,
                file_name="logs.csv",
                mime="text/csv",
                use_container_width=True
            )

        # Lecture du fichier log
        import pandas as pd
        df = pd.read_csv(log_file)

        st.sidebar.markdown("### 📊 Statistiques")

        # Nombre total d’essais
        total_essais = len(df)
        st.sidebar.metric("Nombre total d’essais", total_essais)

        # Vérifier colonnes avant affichage
        if "user_id" in df.columns and "essais" in df.columns:
            essais_user = df.groupby("user_id")["essais"].max().reset_index()
            essais_user = essais_user.rename(columns={"essais": "Nb essais"})
            st.sidebar.markdown("👤 Par utilisateur")
            st.sidebar.dataframe(essais_user, use_container_width=True, height=200)

        if "lang" in df.columns:
            essais_lang = df["lang"].value_counts().reset_index()
            essais_lang.columns = ["Langue", "Nb essais"]
            st.sidebar.markdown("🌍 Par langue")
            st.sidebar.dataframe(essais_lang, use_container_width=True, height=200)

        if "activity" in df.columns:
            essais_act = df["activity"].value_counts().reset_index()
            essais_act.columns = ["Activité", "Nb essais"]
            st.sidebar.markdown("🎭 Par activité")
            st.sidebar.dataframe(essais_act, use_container_width=True, height=200)

    else:
        st.sidebar.info("📂 Aucun log enregistré pour l’instant.")

else:
    if admin_code:
        st.sidebar.error("❌ Code incorrect")
