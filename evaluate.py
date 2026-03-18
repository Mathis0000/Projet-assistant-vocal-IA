#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP 3 Evaluation - Tester et évaluer componants
WER, Intent accuracy, etc.
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict

# ============================================================================
# EVALUATION METRICS
# ============================================================================

def calculate_wer(reference: str, hypothesis: str) -> float:
    """
    Calculer Word Error Rate

    Args:
        reference: Texte référence
        hypothesis: Texte hypothèse ASR

    Returns:
        WER en pourcentage
    """
    ref_words = reference.upper().split()
    hyp_words = hypothesis.upper().split()

    if len(ref_words) == 0:
        return 0.0 if len(hyp_words) == 0 else 1.0

    # Calcul simple (pas de dynamic programming)
    # Vraiment, utiliser python-Levenshtein pour prod
    matches = sum(1 for r, h in zip(ref_words, hyp_words) if r == h)
    errors = len(ref_words) - matches

    wer = (errors / len(ref_words)) * 100
    return wer


def evaluate_asr(test_cases: List[Tuple[str, str]]) -> Dict:
    """
    Évaluer composant ASR

    Args:
        test_cases: Liste (fichier_audio, référence_texte)

    Returns:
        Dict avec statistiques WER
    """
    from asr_component import create_asr

    print("=" * 80)
    print("[EVALUATION] ASR Component")
    print("=" * 80)

    asr = create_asr("whisper", model_size="base")

    wers = []
    for audio_file, reference in test_cases:
        if not Path(audio_file).exists():
            print(f"[SKIP] Fichier not found: {audio_file}")
            continue

        hypothesis, _ = asr.transcribe_file(audio_file)
        wer = calculate_wer(reference, hypothesis)
        wers.append(wer)

        print(f"\nFile: {audio_file}")
        print(f"  Reference: '{reference}'")
        print(f"  Hypothesis: '{hypothesis}'")
        print(f"  WER: {wer:.2f}%")

    if wers:
        avg_wer = np.mean(wers)
        print(f"\n[RESULTS]")
        print(f"  Average WER: {avg_wer:.2f}%")
        print(f"  Min WER: {np.min(wers):.2f}%")
        print(f"  Max WER: {np.max(wers):.2f}%")
        print(f"  Status: {'PASS' if avg_wer < 20 else 'FAIL'} (requirement < 20%)")

    return {
        'average_wer': np.mean(wers) if wers else 100,
        'wers': wers
    }


def evaluate_nlu(test_cases: List[Tuple[str, str, Dict]]) -> Dict:
    """
    Évaluer composant NLU

    Args:
        test_cases: Liste (texte, intent_attendu, entities_attendues)

    Returns:
        Dict avec statistiques accuracy
    """
    from nlu_component import NLUComponent

    print("\n" + "=" * 80)
    print("[EVALUATION] NLU Component")
    print("=" * 80)

    nlu = NLUComponent()

    correct_intents = 0
    total_tests = len(test_cases)

    for text, expected_intent, expected_entities in test_cases:
        result = nlu.process(text)
        predicted_intent = result['intent']

        is_correct = predicted_intent == expected_intent
        correct_intents += is_correct

        print(f"\nText: '{text}'")
        print(f"  Expected: {expected_intent}, Predicted: {predicted_intent}")
        print(f"  Status: {'OK' if is_correct else 'FAIL'}")

    accuracy = (correct_intents / total_tests) * 100
    print(f"\n[RESULTS]")
    print(f"  Intent Accuracy: {accuracy:.2f}%")
    print(f"  Status: {'PASS' if accuracy >= 80 else 'FAIL'} (requirement >= 80%)")

    return {
        'accuracy': accuracy,
        'correct': correct_intents,
        'total': total_tests
    }


# ============================================================================
# TEST CASES
# ============================================================================

ASR_TEST_CASES = [
    # (audio_file, reference_text)
    # À remplir avec vos fichiers
]

NLU_TEST_CASES = [
    ("Bonjour", "greeting", {}),
    ("Quel est le temps à Paris?", "weather", {'location': ['paris']}),
    ("Quelle heure est-il?", "time", {}),
    ("5 plus 3", "math", {'number': ['5', '3']}),
    ("Raconte une blague", "joke", {}),
    ("Je suis perdu", "unknown", {}),
]


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\n" + "=" * 80)
    print("[EVALUATION] TP 3 Components")
    print("=" * 80)

    # Évaluer NLU
    nlu_results = evaluate_nlu(NLU_TEST_CASES)

    print("\n" + "=" * 80)
    print("[SUMMARY]")
    print("=" * 80)
    print(f"\nNLU Accuracy: {nlu_results['accuracy']:.2f}%")
    print(f"  Status: {'PASS' if nlu_results['accuracy'] >= 80 else 'FAIL'}")

    # Sauvegarder résultats
    results = {
        'nlu': nlu_results,
        'asr': {'average_wer': None, 'note': 'Aucun fichier audio fourni'}
    }
    with open("evaluate_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("\n[SAVED] evaluate_results.json")


if __name__ == "__main__":
    main()
