import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Configuration de la page
st.set_page_config(page_title="IA Note Vocale", page_icon="🎙️", layout="centered")

# --- GESTION DES CLÉS API ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key and "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]

if not api_key:
    st.error("❌ Clé API Google manquante.")
    st.stop()

# --- CONFIGURATION GEMINI ---
MODEL_ID = "gemini-2.5-pro" 
client = genai.Client(api_key=api_key)

# Prompt dynamique pour s'adapter à la langue
SYSTEM_PROMPT = (
    "Analyse le fichier audio fourni. "
    "1. Détecte la langue principale parlée dans l'audio. "
    "2. Rédige l'INTÉGRALITÉ de ta réponse (y compris les titres des sections) dans cette même langue. "
    "3. Structure ta réponse ainsi : "
    "   - Un titre signifiant 'Transcription' dans la langue détectée, suivi d'un séparateur, puis du texte transcrit"
    "   - Un titre signifiant 'Résumé' dans la langue détectée, puis un séparateur. "
    "     Résume le contenu de manière logique et articulée. "
    "   - Un titre signifiant 'Nuances' dans la langue détectée. suivi d'un séparateur"
    "     Challenge l'idée présentée en t'appuyant sur la littérature scientifique."
    "     CRITÈRE DE STYLE : Adapte ton niveau de vocabulaire et d'élocution à celui entendu dans l'audio. "
    "     CRITÈRE DE FORME : Ne mentionne jamais 'l'orateur', 'l'utilisateur' ou 'la personne'. Énonce les idées et faits directement. "
    "     Cite les sources scientifiques consensuelles qui appuient le contenu. "
)

# --- INTERFACE UTILISATEUR ---
st.title("🎙️ Analyseur de Note Vocale")
st.markdown("Enregistrez votre voix ou glissez un fichier audio pour obtenir une analyse.")

col1, col2 = st.columns(2)

# 1. Source Micro
with col1:
    audio_mic = st.audio_input("Enregistrer (Micro)")

# 2. Source Upload
with col2:
    audio_file = st.file_uploader("Uploader un fichier", type=["mp3", "wav", "m4a", "ogg"])

# Logique de sélection de la source audio
final_audio_bytes = None
mime_type = "audio/wav" # Par défaut

if audio_mic:
    final_audio_bytes = audio_mic.read()
    mime_type = "audio/wav" # Le micro Streamlit sort généralement du WAV
elif audio_file:
    final_audio_bytes = audio_file.read()
    mime_type = audio_file.type # Récupère le type réel (ex: audio/mpeg)

# --- TRAITEMENT ---
if final_audio_bytes:
    # Petit indicateur de ce qui est analysé
    st.info(f"Fichier prêt à l'analyse ({mime_type})")
    
    if st.button("⚡ Lancer l'analyse", type="primary"):
        with st.spinner("Analyse en cours avec Gemini 2.5 Flash..."):
            try:
                response = client.models.generate_content(
                    model=MODEL_ID,
                    contents=[
                        types.Content(
                            role="user",
                            parts=[
                                types.Part.from_bytes(
                                    data=final_audio_bytes,
                                    mime_type=mime_type 
                                ),
                                types.Part.from_text(text=SYSTEM_PROMPT),
                            ]
                        )
                    ]
                )
                
                st.success("Analyse terminée !")
                st.markdown("### 📝 Résultat")
                st.markdown(response.text)
                
                st.download_button(
                    label="Télécharger le rapport",
                    data=response.text,
                    file_name="analyse_vocale.md",
                    mime="text/markdown"
                )

            except Exception as e:
                st.error(f"Une erreur est survenue : {e}")








