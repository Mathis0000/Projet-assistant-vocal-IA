#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP 3 Component 5 - TTS (Text-To-Speech)
Synthèse vocale française
Options: Coqui TTS ou pyttsx3 simple
"""

import numpy as np
import soundfile as sf
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# TTS USING COQUI (RECOMMENDED)
# ============================================================================

class CoquiTTS:
    """TTS utilisant Coqui (meilleure qualité)"""

    def __init__(self, language="fr", gpu=False):
        """
        Args:
            language: Code langue (fr, en, es, etc.)
            gpu: Utiliser GPU si disponible
        """
        try:
            from TTS.api import TTS
            self.TTS = TTS
        except ImportError:
            raise ImportError("Installer: pip install TTS")

        self.language = language
        self.gpu = gpu

        print(f"[TTS] Chargement Coqui TTS (langue: {language})...")

        # Sélectionner modèle selon langue
        if language == "fr":
            model_name = "tts_models/fr/cv/glow-tts"
        else:
            model_name = "tts_models/en/ljspeech/tacotron2-DDC"

        self.model = TTS(
            model_name=model_name,
            gpu=gpu,
            progress_bar=True
        )

        print(f"[TTS] Coqui TTS chargé ✓")

    def synthesize(self, text: str, output_path: str = "output.wav"):
        """
        Synthétiser texte en audio

        Args:
            text: Texte à synthétiser
            output_path: Chemin fichier sortie

        Returns:
            Chemin fichier généré
        """
        print(f"[TTS] Synthèse: '{text}'")

        try:
            self.model.tts_to_file(
                text=text,
                file_path=output_path
            )

            print(f"[TTS] Audio généré: {output_path} ✓")
            return output_path

        except Exception as e:
            print(f"[ERROR] Erreur synthèse: {e}")
            return None

    def speak(self, text: str):
        """
        Synthétiser et jouer audio

        Args:
            text: Texte à parler
        """
        wav_path = self.synthesize(text, "_temp_tts.wav")

        if wav_path:
            # Jouer audio
            self._play_audio(wav_path)

            # Nettoyer
            Path(wav_path).unlink(missing_ok=True)

    @staticmethod
    def _play_audio(wav_path: str):
        """Jouer fichier audio"""
        try:
            import sounddevice as sd
            import soundfile as sf

            data, sr = sf.read(wav_path)
            sd.play(data, sr)
            sd.wait()
            print(f"[TTS] Audio joué ✓")

        except ImportError:
            print("[INFO] Installer sounddevice: pip install sounddevice")
        except Exception as e:
            print(f"[ERROR] Erreur lecture audio: {e}")


# ============================================================================
# TTS USING PYTTSX3 (SIMPLE FALLBACK)
# ============================================================================

class PytTTSSynthesizer:
    """TTS simple utilisant SAPI Windows (win32com)"""

    def __init__(self, language="fr"):
        import win32com.client
        self.speaker = win32com.client.Dispatch("SAPI.SpVoice")
        self.speaker.Rate = 0
        self.speaker.Volume = 90
        print("[TTS] SAPI (win32com) initialisé ✓")

    def synthesize(self, text: str, output_path: str = "output.wav"):
        """
        Synthétiser texte en audio

        Args:
            text: Texte à synthétiser
            output_path: Chemin fichier sortie
        """
        import win32com.client
        print(f"[TTS] Synthèse (SAPI): '{text}'")

        tts = win32com.client.Dispatch("SAPI.SpVoice")
        stream = win32com.client.Dispatch("SAPI.SpFileStream")
        stream.Open(str(output_path), 3)
        tts.AudioOutputStream = stream
        tts.Speak(text)
        stream.Close()

        print(f"[TTS] Audio généré: {output_path} ✓")
        return output_path

    def speak(self, text: str):
        """Synthétiser et parler directement"""
        print(f"[TTS] Parole: '{text}'")
        self.speaker.Speak(text)


# ============================================================================
# FACTORY
# ============================================================================

def create_tts(tts_type="coqui", language="fr", **kwargs):
    """
    Factory pour créer TTS component

    Args:
        tts_type: "coqui" ou "pyttsx3"
        language: Code langue
        **kwargs: Arguments additionnels

    Returns:
        TTS instance
    """
    if tts_type == "coqui":
        try:
            return CoquiTTS(language=language, **kwargs)
        except:
            print("[WARNING] Coqui TTS échoué, fallback pyttsx3")
            return PytTTSSynthesizer(language=language)

    elif tts_type == "pyttsx3":
        return PytTTSSynthesizer(language=language)

    else:
        raise ValueError(f"TTS type non supporté: {tts_type}")


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("[TEST] TTS Component")
    print("=" * 80)

    # Créer TTS (essayer Coqui, fallback pyttsx3)
    tts = create_tts("coqui", language="fr")

    # Test textes
    test_texts = [
        "Bonjour, ceci est un test.",
        "Je suis votre assistant vocal.",
        "À demain!",
        "Ceci est une phrase plus longue pour tester la synthèse vocale en français."
    ]

    tts.synthesize(test_texts[0], "bonjour.wav")

    tts.synthesize(test_texts[1], "assistant.wav")

    tts.synthesize(test_texts[2], "demain.wav")

    tts.synthesize(test_texts[3], "longue.wav")
