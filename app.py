import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Configuration de la page (Doit être la première commande Streamlit)
st.set_page_config(page_title="IA Note Vocale", page_icon="🎙️", layout="centered")

# --- GESTION DES CLÉS API ---
# En local, on charge depuis .env. 
# En production (Streamlit Cloud), on chargera depuis st.secrets
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Si la clé n'est pas dans le .env, on regarde dans les secrets de Streamlit
if not api_key and "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]

if not api_key:
    st.error("❌ Clé API Google manquante. Vérifiez vos variables d'environnement.")
    st.stop()

# --- CONFIGURATION GEMINI ---
MODEL_ID = "gemini-2.5-flash" 
client = genai.Client(api_key=api_key)

SYSTEM_PROMPT = (
    "Analyse le fichier audio fourni. "
    "1. Détecte la langue principale parlée dans l'audio. "
    "2. Rédige l'INTÉGRALITÉ de ta réponse (y compris les titres des sections) dans cette même langue. "
    "3. Structure ta réponse ainsi : "
    "   - Un titre signifiant 'Transcription' dans la langue détectée, suivi du texte transcrit. "
    "   - Un séparateur. "
    "   - Un titre signifiant 'Résumé' (ex: 'Summary' si anglais, 'Resumen' si espagnol) dans la langue détectée. "
    "     Résume le contenu de manière logique, concise, en citant les sources scientifiques consensuelles. "
    "   - Un titre signifiant 'Nuances' dans la langue détectée. "
    "     Challenge l'idée présentée en t'appuyant sur la littérature scientifique."
    " L'ensemble de ce que tu as produit doit refléter le niveau d'élocution de l'utilisateur"
)

# --- INTERFACE UTILISATEUR ---
st.title("🎙️ Analyseur de Note Vocale")
st.markdown("Enregistrez votre voix ou uploadez un fichier audio pour obtenir une transcription, un résumé et une analyse critique.")

# Widget d'enregistrement audio (Natif Streamlit)
audio_value = st.audio_input("Enregistrez votre note vocale")

if audio_value:
    # Lecture des bytes de l'audio enregistré
    audio_bytes = audio_value.read()
    
    # Bouton pour lancer l'analyse (optionnel, mais évite de recharger à chaque lecture)
    if st.button("⚡ Lancer l'analyse", type="primary"):
        with st.spinner("Analyse en cours avec Gemini 2.5 Flash..."):
            try:
                # Appel API Gemini (Direct Binaire)
                response = client.models.generate_content(
                    model=MODEL_ID,
                    contents=[
                        types.Content(
                            role="user",
                            parts=[
                                types.Part.from_bytes(
                                    data=audio_bytes,
                                    mime_type="audio/wav" # Streamlit audio_input sort généralement du WAV
                                ),
                                types.Part.from_text(text=SYSTEM_PROMPT),
                            ]
                        )
                    ]
                )
                
                # Affichage du résultat
                st.success("Analyse terminée !")
                st.markdown("### 📝 Résultat")
                st.markdown(response.text)
                
                # Option pour télécharger le résultat
                st.download_button(
                    label="Télécharger le rapport",
                    data=response.text,
                    file_name="analyse_vocale.md",
                    mime="text/markdown"
                )

            except Exception as e:
                st.error(f"Une erreur est survenue : {e}")

# Footer discret
st.markdown("---")

st.caption("Propulsé par Google Gemini 2.5 Flash & Streamlit")

