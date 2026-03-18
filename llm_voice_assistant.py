#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline vocal avec LLM local (Ollama)
ASR (Whisper) -> LLM (Ollama) -> TTS (SAPI)
"""

import os
import sys
import requests
from pathlib import Path

# Ajouter ffmpeg (imageio-ffmpeg) au PATH
try:
    import imageio_ffmpeg
    _ffmpeg_dir = str(Path(imageio_ffmpeg.get_ffmpeg_exe()).parent)
    _ffmpeg_link = Path(_ffmpeg_dir) / "ffmpeg.exe"
    if not _ffmpeg_link.exists():
        import shutil
        shutil.copy(imageio_ffmpeg.get_ffmpeg_exe(), str(_ffmpeg_link))
    if _ffmpeg_dir not in os.environ.get("PATH", ""):
        os.environ["PATH"] = _ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
except ImportError:
    pass

from asr_component import WhisperASR
from tts_component import PytTTSSynthesizer

# ============================================================================
# CONFIGURATION
# ============================================================================

OLLAMA_URL = "http://localhost:11434"
MODEL = "phi3:mini"

SYSTEM_PROMPT = """Tu es un assistant vocal en français.
Réponds en une seule phrase courte et naturelle, sans aucune exception.
Tu parles toujours en français."""

# ============================================================================
# LLM CLIENT
# ============================================================================

def query_ollama(prompt: str, model: str = MODEL) -> str:
    """
    Envoyer une requête à Ollama et récupérer la réponse

    Args:
        prompt: Question de l'utilisateur
        model: Modèle à utiliser

    Returns:
        Réponse du LLM
    """
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "system": SYSTEM_PROMPT,
                "stream": False,
                "options": {
                    "num_predict": 60,  # max ~1 phrase
                    "stop": [".", "!", "?"]
                }
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json()["response"].strip()

    except requests.exceptions.ConnectionError:
        return "[ERREUR] Ollama non accessible. Lance: docker compose up -d"
    except requests.exceptions.Timeout:
        return "[ERREUR] Timeout - le modèle met trop de temps à répondre."
    except Exception as e:
        return f"[ERREUR] {e}"


def check_ollama() -> bool:
    """Vérifier qu'Ollama est accessible et que le modèle est disponible"""
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        models = [m["name"] for m in r.json().get("models", [])]
        if not any(MODEL.split(":")[0] in m for m in models):
            print(f"[INFO] Modèle '{MODEL}' non trouvé. Téléchargement...")
            print(f"  Lance: docker exec ollama ollama pull {MODEL}")
            return False
        return True
    except Exception:
        return False


# ============================================================================
# PIPELINE VOCAL
# ============================================================================

class LLMVoiceAssistant:
    """Pipeline vocal : ASR -> LLM (Ollama) -> TTS"""

    def __init__(self, model: str = MODEL):
        print("=" * 60)
        print("[INIT] LLM Voice Assistant")
        print("=" * 60)

        self.model = model

        # ASR
        print("[INIT] Chargement Whisper...")
        self.asr = WhisperASR(model_size="base")

        # TTS
        print("[INIT] Chargement TTS...")
        self.tts = PytTTSSynthesizer()

        # Vérifier Ollama
        if check_ollama():
            print(f"[INIT] Ollama OK - modèle: {model}")
        else:
            print(f"[WARNING] Ollama inaccessible ou modèle manquant")

        print("[INIT] Prêt ✓\n")

    def _play_audio(self, wav_path: str):
        """Jouer fichier audio"""
        try:
            import sounddevice as sd
            import soundfile as sf
            data, sr = sf.read(wav_path)
            sd.play(data, sr)
            sd.wait()
        except Exception as e:
            print(f"[WARNING] Lecture audio: {e}")

    def process_mic(self, duration: int = 5) -> str:
        """
        Enregistrer micro -> ASR -> LLM -> TTS -> lecture

        Args:
            duration: Durée enregistrement en secondes

        Returns:
            Réponse du LLM
        """
        # 1. ASR
        print(f"\n[MIC] Écoute ({duration}s)...")
        transcript = self.asr.transcribe_microphone(duration=duration)
        if not transcript:
            print("[ERROR] Transcription vide")
            return ""
        print(f"[ASR] '{transcript}'")

        # 2. LLM
        print(f"[LLM] Requête vers {self.model}...")
        response = query_ollama(transcript, self.model)
        print(f"[LLM] '{response}'")

        # 3. TTS + lecture
        print("[TTS] Synthèse...")
        self.tts.synthesize(response, "llm_response.wav")
        self._play_audio("llm_response.wav")

        return response

    def run(self):
        """Boucle interactive"""
        print("=" * 60)
        print("Assistant vocal LLM - Commandes: 'mic', 'quit'")
        print("=" * 60)

        while True:
            try:
                cmd = input("\n> ").strip().lower()

                if cmd in ["quit", "exit"]:
                    print("Au revoir!")
                    break
                elif cmd == "mic":
                    self.process_mic(duration=5)
                else:
                    print("[INFO] Commandes disponibles: mic, quit")

            except KeyboardInterrupt:
                print("\nInterruption.")
                break


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    assistant = LLMVoiceAssistant(model=MODEL)
    assistant.run()
