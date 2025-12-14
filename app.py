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
MODEL_ID = "gemini-2.5-pro" # J'ai corrigé "2.5" qui n'existe pas encore publiquement, 2.0 Flash est le standard actuel rapide
client = genai.Client(api_key=api_key)

# Prompt dynamique
SYSTEM_PROMPT = """
Tu es un analyste expert doté d'une capacité de synthèse et de mise en forme impeccable.
Ta tâche est d'analyser le fichier audio fourni et de générer un rapport structuré et visuellement agréable.

### CONSIGNES DE LANGUE :
1. Détecte la langue dominante de l'audio.
2. Rédige l'INTÉGRALITÉ de ta réponse dans cette langue.

### STRUCTURE ET MISE EN FORME (Markdown strict) :

**1. 📝 [Titre "Transcription" dans la langue détectée]**
> Utilise le format de citation (block quote avec le symbole '>') pour afficher la transcription. 
> Cela doit créer un bloc visuel distinct pour le texte brut.

---

**2. ⚡ [Titre "Synthèse Exécutive" dans la langue détectée]**
* Organise le résumé sous forme de **listes à puces**.
* Utilise du **gras** pour mettre en évidence les idées maîtresses au début de chaque puce.
* Le résumé doit être articulé et logique.

---

**3. 🧠 [Titre "Analyse & Nuances Scientifiques" dans la langue détectée]**
* Challenge les idées présentées.
* Cite des **sources scientifiques consensuelles** ou des modèles théoriques pour appuyer ou nuancer les propos.
* Adopte une approche critique mais constructive.

### CRITÈRES DE STYLE :
* **Tonalité adaptative** : Le niveau de vocabulaire doit s'aligner sur celui de l'audio.
* **Directivité** : Ne mentionne JAMAIS "l'orateur". Présente les faits directement.
"""

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

# Logique de sélection
final_audio_bytes = None
mime_type = "audio/wav"

if audio_mic:
    final_audio_bytes = audio_mic.read()
    mime_type = "audio/wav"
elif audio_file:
    final_audio_bytes = audio_file.read()
    mime_type = audio_file.type

# --- TRAITEMENT (MODIFIÉ POUR LE STREAMING) ---
if final_audio_bytes:
    st.info(f"Fichier prêt à l'analyse ({mime_type})")
    
    if st.button("⚡ Lancer l'analyse", type="primary"):
        st.markdown("### 📝 Résultat")
        
        # Création d'un conteneur vide pour le flux
        response_placeholder = st.empty()
        full_response_text = ""

        try:
            # Appel API en mode STREAM
            response_stream = client.models.generate_content_stream(
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
            
            # Boucle pour afficher les morceaux (chunks) au fur et à mesure
            for chunk in response_stream:
                if chunk.text:
                    full_response_text += chunk.text
                    # On ajoute un petit curseur "▌" pour l'effet visuel
                    response_placeholder.markdown(full_response_text + "▌")
            
            # Affichage final propre (sans le curseur)
            response_placeholder.markdown(full_response_text)
            
            st.success("Analyse terminée !")
            
            # Le bouton de téléchargement utilise le texte complet assemblé
            st.download_button(
                label="Télécharger le rapport",
                data=full_response_text,
                file_name="analyse_vocale.md",
                mime="text/markdown"
            )

        except Exception as e:
            st.error(f"Une erreur est survenue : {e}")
