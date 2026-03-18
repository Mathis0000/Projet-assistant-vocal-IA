#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP 3 Main - Voice Assistant Pipeline Complet
Intègre ASR + NLU + Dialogue + NLG + TTS
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
import json
from datetime import datetime

# Importer components
from asr_component import create_asr, WhisperASR
from nlu_component import NLUComponent
from dialogue_manager import DialogueManager
from nlg_component import NLGComponent
from tts_component import create_tts

# ============================================================================
# VOICE ASSISTANT CLASS
# ============================================================================

class VoiceAssistant:
    """Assistant vocal complet intégrant tout le pipeline"""

    def __init__(self, asr_type="whisper", tts_type="coqui", language="fr"):
        """
        Initialiser assistant vocal

        Args:
            asr_type: Type ASR ("whisper" ou "wav2vec2")
            tts_type: Type TTS ("coqui" ou "pyttsx3")
            language: Langue (fr, en, etc.)
        """
        print("=" * 80)
        print("[ASSISTANT] Initialisation Voice Assistant")
        print("=" * 80)

        self.language = language

        # Initialiser components
        print("\n[INIT] Chargement components...")

        try:
            self.asr = create_asr(asr_type, model_size="base")
        except Exception as e:
            print(f"[ERROR] ASR échoué: {e}")
            self.asr = None

        try:
            self.nlu = NLUComponent()
        except Exception as e:
            print(f"[ERROR] NLU échoué: {e}")
            self.nlu = None

        try:
            self.dialogue = DialogueManager()
        except Exception as e:
            print(f"[ERROR] Dialogue échoué: {e}")
            self.dialogue = None

        try:
            self.nlg = NLGComponent()
        except Exception as e:
            print(f"[ERROR] NLG échoué: {e}")
            self.nlg = None

        try:
            self.tts = create_tts(tts_type, language=language)
        except Exception as e:
            print(f"[ERROR] TTS échoué: {e}")
            self.tts = None

        print("\n[INIT] Assistant vocal prêt ✓")
        self.conversation_history = []

    def process_audio_file(self, audio_path: str) -> str:
        """
        Traiter fichier audio complet

        Args:
            audio_path: Chemin fichier WAV

        Returns:
            Réponse texte
        """
        print("\n" + "=" * 80)
        print(f"[PROCESSING] Fichier: {audio_path}")
        print("=" * 80)

        # ===== ÉTAPE 1: ASR =====
        print("\n[STEP 1/5] ASR - Reconnaissance vocale...")
        if not self.asr:
            print("[ERROR] ASR non disponible")
            return ""

        transcript, confidence = self.asr.transcribe_file(audio_path, self.language)
        if not transcript:
            print("[ERROR] Transcription échouée")
            return ""

        print(f"  Transcript: '{transcript}'")
        print(f"  Confidence: {confidence:.2%}")

        # ===== ÉTAPE 2: NLU =====
        print("\n[STEP 2/5] NLU - Compréhension du langage...")
        if not self.nlu:
            print("[ERROR] NLU non disponible")
            return ""

        nlu_result = self.nlu.process(transcript)
        intent = nlu_result['intent']
        entities = nlu_result['entities']

        print(f"  Intent: {intent} (confiance: {nlu_result['confidence']:.2%})")
        print(f"  Entities: {entities}")

        # ===== ÉTAPE 3: Dialogue =====
        print("\n[STEP 3/5] Dialogue - Gestion contexte...")
        if not self.dialogue:
            print("[ERROR] Dialogue non disponible")
            return ""

        dialogue_result = self.dialogue.process_intent(intent, entities)
        action = dialogue_result['action']

        print(f"  Action: {action.get('type', 'unknown')}")
        print(f"  Message interne: {action.get('message', '')}")

        # ===== ÉTAPE 4: NLG =====
        print("\n[STEP 4/5] NLG - Génération texte...")
        if not self.nlg:
            print("[ERROR] NLG non disponible")
            return ""

        response_text = self.nlg.generate_response(action)
        print(f"  Réponse: '{response_text}'")

        # ===== ÉTAPE 5: TTS =====
        print("\n[STEP 5/5] TTS - Synthèse vocale...")
        if self.tts:
            try:
                output_wav = "assistant_response.wav"
                self.tts.synthesize(response_text, output_wav)
                print(f"  Audio généré: {output_wav}")
                self._play_audio(output_wav)
            except Exception as e:
                print(f"[WARNING] TTS échoué: {e}")
        else:
            print("[WARNING] TTS non disponible, réponse texte seulement")

        # Sauvegarder conversation
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'user_input': transcript,
            'intent': intent,
            'assistant_response': response_text
        })

        return response_text

    def _play_audio(self, wav_path: str):
        """Jouer un fichier WAV via sounddevice"""
        try:
            import sounddevice as sd
            import soundfile as sf
            data, sr = sf.read(wav_path)
            print(f"  [PLAY] Lecture audio...")
            sd.play(data, sr)
            sd.wait()
        except Exception as e:
            print(f"[WARNING] Lecture audio échouée: {e}")

    def run_mic_loop(self, duration=5):
        """
        Boucle principale: enregistre le micro, joue la réponse audio.
        Appuyer sur Entrée pour parler, Ctrl+C pour quitter.

        Args:
            duration: Durée d'enregistrement en secondes
        """
        if not self.asr or not hasattr(self.asr, 'transcribe_microphone'):
            print("[ERROR] Microphone / ASR non disponible")
            return

        print("\n" + "=" * 80)
        print("[ASSISTANT] Mode vocal actif")
        print(f"  Appuyez sur Entrée pour parler ({duration}s), Ctrl+C pour quitter")
        print("=" * 80)

        while True:
            try:
                input("\n[Entrée pour parler...]")

                # Enregistrement
                transcript = self.asr.transcribe_microphone(duration=duration)
                if not transcript:
                    print("[WARNING] Rien entendu, réessayez.")
                    continue

                print(f"\n[VOUS]      '{transcript}'")

                # NLU
                nlu_result = self.nlu.process(transcript)
                intent = nlu_result['intent']
                entities = nlu_result['entities']
                print(f"[NLU]       intent={intent} ({nlu_result['confidence']:.0%})")

                # Dialogue
                dialogue_result = self.dialogue.process_intent(intent, entities)

                # NLG
                response_text = self.nlg.generate_response(dialogue_result['action'])
                print(f"[ASSISTANT] '{response_text}'")

                # TTS + lecture
                if self.tts:
                    self.tts.synthesize(response_text, "assistant_response.wav")
                    self._play_audio("assistant_response.wav")

                self.conversation_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'user_input': transcript,
                    'intent': intent,
                    'assistant_response': response_text
                })

            except KeyboardInterrupt:
                print("\n[ASSISTANT] Au revoir!")
                self.save_transcript()
                break

    def save_transcript(self, output_file: str = "conversation.json"):
        """
        Sauvegarder transcription conversation

        Args:
            output_file: Chemin fichier de sortie
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)

        print(f"[SAVED] Conversation sauvegardée: {output_file}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\n" + "=" * 80)
    print("[TP 3] PROJET INTÉGRATEUR - ASSISTANT VOCAL SIMPLE")
    print("=" * 80)

    # Créer assistant
    assistant = VoiceAssistant(
        asr_type="whisper",
        tts_type="coqui",
        language="fr"
    )

    # Boucle micro → réponse audio
    assistant.run_mic_loop(duration=5)


if __name__ == "__main__":
    main()
