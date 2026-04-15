#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP 3 Component 1 - ASR (Automatic Speech Recognition)
Convertit audio (microphone/fichier) en texte français
Options: Whisper ou Wav2Vec2
"""

import os
import sys
import torch
import torchaudio
import numpy as np
import soundfile as sf
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Ajouter ffmpeg (imageio-ffmpeg) au PATH
try:
    import imageio_ffmpeg
    _ffmpeg_dir = str(Path(imageio_ffmpeg.get_ffmpeg_exe()).parent)
    _ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    # Créer un lien nommé ffmpeg.exe si nécessaire
    _ffmpeg_link = Path(_ffmpeg_dir) / "ffmpeg.exe"
    if not _ffmpeg_link.exists():
        import shutil
        shutil.copy(_ffmpeg_exe, str(_ffmpeg_link))
    if _ffmpeg_dir not in os.environ.get("PATH", ""):
        os.environ["PATH"] = _ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
except ImportError:
    pass

# ============================================================================
# ASR USING WHISPER (RECOMMENDED)
# ============================================================================

class WhisperASR:
    """Wrapper Whisper pour ASR robuste multilingue"""

    def __init__(self, model_size="base"):
        """
        Args:
            model_size: "tiny" (~39MB), "base" (~140MB),
                       "small" (~466MB), "medium" (~1.5GB)
        """
        try:
            import whisper
            self.whisper = whisper
        except ImportError:
            raise ImportError("Installer: pip install openai-whisper")

        self.model_size = model_size
        print(f"[ASR] Chargement Whisper {model_size}...")
        self.model = whisper.load_model(model_size)
        print(f"[ASR] Whisper {model_size} charge OK")

    def transcribe_file(self, audio_path, language="fr"):
        """
        Transcrire fichier audio

        Args:
            audio_path: Chemin vers fichier WAV/MP3
            language: Code langue (fr, en, es, etc.)

        Returns:
            transcript: Texte transcrit
            confidence: Score confiance (0-1)
        """
        print(f"[ASR] Transcription de {audio_path}...")

        try:
            # Transcriber avec Whisper
            result = self.model.transcribe(
                audio_path,
                language=language,
                fp16=False  # CPU mode
            )

            transcript = result["text"].strip()
            segments = result.get("segments", [])
            if segments and "confidence" in segments[0]:
                confidence = np.mean([seg["confidence"] for seg in segments])
            elif segments and "avg_logprob" in segments[0]:
                # Convertir log-prob en score 0-1
                confidence = float(np.clip(np.exp(np.mean([seg["avg_logprob"] for seg in segments])), 0, 1))
            else:
                confidence = 1.0 if transcript else 0.0

            print(f"[ASR] Transcription: '{transcript}'")
            print(f"[ASR] Confiance: {confidence:.2%}")

            return transcript, confidence

        except Exception as e:
            print(f"[ERROR] Erreur transcription: {e}")
            return "", 0.0

    def transcribe_microphone(self, duration=5, sr=16000):
        """
        Enregistrer du microphone et transcrire

        Args:
            duration: Durée enregistrement (secondes)
            sr: Sample rate (16000 Hz)

        Returns:
            transcript: Texte transcrit
        """
        print(f"[ASR] Enregistrement microphone ({duration}s)...")

        try:
            import sounddevice as sd
        except ImportError:
            print("[ERROR] Installer: pip install sounddevice")
            return ""

        # Enregistrer
        print("[ASR] Écoute active...")
        audio = sd.rec(int(duration * sr), samplerate=sr, channels=1, dtype=np.float32)
        sd.wait()

        # Sauvegarder temporairement dans un dossier sans accents
        import tempfile
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_wav = tmp.name
        tmp.close()
        sf.write(temp_wav, audio, sr)

        # Transcrire
        transcript, _ = self.transcribe_file(temp_wav, language="fr")

        # Nettoyer
        Path(temp_wav).unlink(missing_ok=True)

        return transcript


# ============================================================================
# ASR USING WAV2VEC2 (ALTERNATIVE)
# ============================================================================

class Wav2Vec2ASR:
    """ASR utilisant Wav2Vec2 fine-tuned"""

    def __init__(self, model_name="facebook/wav2vec2-large-xlsr-53-french"):
        """
        Args:
            model_name: Modèle Hugging Face
        """
        from transformers import pipeline

        print(f"[ASR] Chargement Wav2Vec2 {model_name}...")
        self.asr = pipeline(
            "automatic-speech-recognition",
            model=model_name,
            device=-1  # CPU
        )
        print(f"[ASR] Wav2Vec2 chargé ✓")

    def transcribe_file(self, audio_path):
        """
        Args:
            audio_path: Chemin fichier WAV

        Returns:
            transcript, confidence
        """
        print(f"[ASR] Transcription de {audio_path}...")

        try:
            result = self.asr(audio_path)
            transcript = result["text"].strip()

            print(f"[ASR] Transcription: '{transcript}'")
            return transcript, 0.85  # Approximation

        except Exception as e:
            print(f"[ERROR] {e}")
            return "", 0.0


# ============================================================================
# FACTORY ET HELPERS
# ============================================================================

def create_asr(asr_type="whisper", **kwargs):
    """
    Factory pour créer ASR component

    Args:
        asr_type: "whisper" ou "wav2vec2"
        **kwargs: Arguments additionnels

    Returns:
        ASR instance
    """
    if asr_type == "whisper":
        return WhisperASR(**kwargs)
    elif asr_type == "wav2vec2":
        return Wav2Vec2ASR(**kwargs)
    else:
        raise ValueError(f"ASR type non supporté: {asr_type}")


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("[TEST] ASR Component")
    print("=" * 80)

    # Créer ASR (Whisper par défaut)
    asr = create_asr("whisper", model_size="base")

    # Tester sur les 5 fichiers audio du projet
    # (fichier, référence texte attendu)
    audio_files = [
        (Path(__file__).parent / "bonjour.wav",            "Bonjour, ceci est un test."),
        (Path(__file__).parent / "assistant.wav",          "Je suis votre assistant vocal."),
        (Path(__file__).parent / "demain.wav",             "À demain!"),
        (Path(__file__).parent / "assistant_response.wav", "Bonjour utilisateur, je suis votre assistant vocal. Comment puis-je vous aider?"),
        (Path(__file__).parent / "longue.wav", "Ceci est une phrase plus longue pour tester la synthèse vocale en français."), 
    ]

    def calculate_wer(reference, hypothesis):
        ref = reference.upper().split()
        hyp = hypothesis.upper().split()
        if not ref:
            return None
        matches = sum(1 for r, h in zip(ref, hyp) if r == h)
        return ((len(ref) - matches) / len(ref)) * 100

    print("\n[TESTS]")
    for audio_file, reference in audio_files:
        if not audio_file.exists():
            print(f"\n[SKIP] Fichier introuvable: {audio_file.name}")
            continue

        transcript, conf = asr.transcribe_file(str(audio_file))
        wer = calculate_wer(reference, transcript)
        print(f"\nFichier: {audio_file.name}")
        print(f"  Transcript: '{transcript}'")
        print(f"  Confidence: {conf:.2%}")
        if wer is not None:
            print(f"  WER: {wer:.2f}%")
