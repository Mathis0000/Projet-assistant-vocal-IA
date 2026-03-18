# Projet Alexa Local — Assistant Vocal Français

> TP3 — Projet intégrateur | Master 2 Intelligence Artificielle
> Université Clermont Auvergne

## Présentation

Ce projet implémente un assistant vocal **entièrement local** en français, fonctionnant sans API externe. Il reproduit le comportement d'un assistant de type Alexa/Siri en chaînant cinq composants NLP/Speech :

```
Microphone → ASR → NLU → Dialogue → NLG → TTS → Haut-parleur
```

Deux pipelines sont disponibles :
- **Pipeline classique** : modules NLU/dialogue/NLG faits maison
- **Pipeline LLM** : remplacement du dialogue par un modèle Ollama local (phi3:mini)

---

## Architecture

```
tp_noté/
├── asr_component.py        # Automatic Speech Recognition (Whisper / Wav2Vec2)
├── nlu_component.py        # Natural Language Understanding (intent + entités)
├── dialogue_manager.py     # Gestionnaire de dialogue et contexte
├── nlg_component.py        # Natural Language Generation (templates)
├── tts_component.py        # Text-To-Speech (Coqui TTS / SAPI fallback)
│
├── voice_assistant.py      # Pipeline principal (ASR → NLU → DM → NLG → TTS)
├── llm_voice_assistant.py  # Pipeline alternatif avec Ollama LLM
├── interface.py            # Interface web Streamlit
├── interface.ipynb         # Notebook Jupyter avec interface Streamlit intégrée
│
├── evaluate.py             # Évaluation WER (ASR) et accuracy (NLU)
└── docker-compose.yml      # Déploiement Ollama via Docker
```

---

## Composants

### 1. ASR — Reconnaissance vocale
**Fichier :** [asr_component.py](asr_component.py)

- **Whisper** (OpenAI) : modèles `tiny` → `base` → `small` → `medium`
- **Wav2Vec2** (Facebook/HuggingFace) : alternative basée sur transformers
- Sortie : transcription texte + score de confiance
- Langue : français

### 2. NLU — Compréhension du langage
**Fichier :** [nlu_component.py](nlu_component.py)

Classification par mots-clés pour 5 intentions :

| Intention | Exemples |
|-----------|---------|
| `greeting` | bonjour, salut, au revoir |
| `weather` | météo, temps, pluie, température |
| `time` | heure, maintenant |
| `math` | calcul, plus, moins, divisé |
| `joke` | blague, drôle, rigolo |

Extraction d'entités : **villes françaises**, **expressions temporelles**, **nombres**.

### 3. Dialogue Manager
**Fichier :** [dialogue_manager.py](dialogue_manager.py)

- Machine à états : `START → GREETING → LISTENING → PROCESSING → RESPONDING → END`
- Persistance du contexte : réutilisation de la dernière localisation, nom utilisateur
- Gestion de l'enchaînement conversationnel (ex : "Et demain ?" après avoir mentionné Paris)

### 4. NLG — Génération de réponses
**Fichier :** [nlg_component.py](nlg_component.py)

- Sélection aléatoire parmi plusieurs templates par intention
- Formatage dynamique des variables (`{location}`, `{time}`, `{result}`…)
- Dégradation gracieuse si une variable est manquante

### 5. TTS — Synthèse vocale
**Fichier :** [tts_component.py](tts_component.py)

- **Coqui TTS** (modèle `tts_models/fr/cv/glow-tts`) — prioritaire
- **Windows SAPI** (win32com) — fallback automatique si Coqui indisponible

---

## Installation

### Prérequis

- Python 3.9+
- FFmpeg (géré automatiquement via `imageio-ffmpeg`)
- (Optionnel) Docker pour le pipeline LLM

### Dépendances Python

```bash
pip install torch==2.0.0 --index-url https://download.pytorch.org/whl/cpu
pip install transformers==4.40.0 librosa==0.10.0 openai-whisper
pip install TTS soundfile sounddevice numpy scipy
pip install streamlit
```

### Pipeline LLM (optionnel)

```bash
docker compose up -d          # Démarre Ollama
docker exec ollama ollama pull phi3:mini  # Télécharge le modèle
```

---

## Utilisation

### Pipeline classique (ligne de commande)

```python
from voice_assistant import VoiceAssistant

assistant = VoiceAssistant()
assistant.process_audio_file("audio.wav")   # Depuis un fichier
assistant.run_mic_loop(duration=5)           # Depuis le micro
assistant.save_transcript("conversation.json")
```

### Pipeline LLM

```python
from llm_voice_assistant import LLMVoiceAssistant

assistant = LLMVoiceAssistant(model="phi3:mini")
assistant.run()
```

### Interface web Streamlit

```bash
streamlit run interface.py
```

Ouvre une interface cyberpunk avec orbe animée, visualisation du pipeline en temps réel et historique des conversations.

---

## Évaluation

```bash
python evaluate.py
```

Calcule et exporte dans `evaluate_results.json` :
- **WER** (Word Error Rate) pour l'ASR — seuil : < 20 %
- **Accuracy** de classification d'intention (NLU) — seuil : ≥ 80 %

---

## Flux de données — Exemple

```
Entrée : "Quel temps fait-il à Lyon demain ?"
   │
   ▼ ASR (Whisper)
"Quel temps fait-il à Lyon demain ?" — confiance : 0.94
   │
   ▼ NLU
intent: weather | entités: {location: "lyon", time: "demain"} | conf: 0.67
   │
   ▼ Dialogue Manager
action: {type: weather, location: "lyon", time: "demain"}
   │
   ▼ NLG
"À Lyon demain, il devrait faire beau avec 18°C."
   │
   ▼ TTS (Coqui)
→ assistant_response.wav  →  🔊 lecture audio
```

---

## Technologies utilisées

| Domaine | Bibliothèque / Modèle |
|---------|----------------------|
| ASR | OpenAI Whisper, Facebook Wav2Vec2 |
| NLP | Transformers (HuggingFace) |
| TTS | Coqui TTS (`glow-tts` français), Windows SAPI |
| LLM local | Ollama (`phi3:mini`) |
| Interface | Streamlit |
| Audio | librosa, sounddevice, soundfile |
| Infrastructure | Docker, docker-compose |
