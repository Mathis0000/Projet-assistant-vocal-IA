#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP 3 Component 2 - NLU (Natural Language Understanding)
Intent classification + Entity extraction
"""

import re
import numpy as np
from typing import Dict, List, Tuple

# ============================================================================
# INTENT DEFINITIONS
# ============================================================================

INTENTS = {
    "greeting": {
        "keywords": ["bonjour", "salut", "allo", "coucou", "au revoir", "à bientôt"],
        "description": "Salutation"
    },
    "weather": {
        "keywords": ["météo", "temps", "pluie", "soleil", "nuage", "température"],
        "description": "Demande météo"
    },
    "time": {
        "keywords": ["heure", "quelle heure", "l'heure", "maintenant"],
        "description": "Demande heure"
    },
    "math": {
        "keywords": ["calcul", "plus", "moins", "multiplié", "divisé", "combien"],
        "description": "Calcul mathématique"
    },
    "joke": {
        "keywords": ["blague", "rire", "drôle", "rigolo", "marrant"],
        "description": "Demande blague"
    }
}

# ============================================================================
# ENTITY PATTERNS
# ============================================================================

ENTITY_PATTERNS = {
    "location": {
        "pattern": r"\b(paris|lyon|marseille|toulouse|nice|bordeaux|lille|strasbourg|nantes|montpellier)\b",
        "type": "city"
    },
    "time_expression": {
        "pattern": r"\b(demain|aujourd'hui|ce soir|ce matin|lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)\b",
        "type": "temporal"
    },
    "number": {
        "pattern": r"\b(\d+)\b",
        "type": "numeric"
    }
}

# ============================================================================
# NLU COMPONENT
# ============================================================================

class NLUComponent:
    """Natural Language Understanding: Intent + Entity Extraction"""

    def __init__(self):
        """Initialiser NLU"""
        self.intents = INTENTS
        self.entity_patterns = ENTITY_PATTERNS
        print("[NLU] Component initialisé ✓")
        print(f"[NLU] Intents supportés: {list(INTENTS.keys())}")

    def classify_intent(self, text: str) -> Tuple[str, float]:
        """
        Classifier intent à partir du texte

        Args:
            text: Texte utilisateur

        Returns:
            (intent_name, confidence)
        """
        text_lower = text.lower()

        # Scorer chaque intent
        scores = {}
        for intent_name, intent_data in self.intents.items():
            keywords = intent_data["keywords"]

            # Compter matches
            matches = sum(1 for kw in keywords if kw in text_lower)

            # Confiance proportionnelle aux matches
            confidence = min(matches / len(keywords), 1.0)
            scores[intent_name] = confidence

        # Trouver best intent
        best_intent = max(scores, key=scores.get)
        best_confidence = scores[best_intent]

        # Si confiance trop basse, retourner "unknown"
        if best_confidence < 0.15:
            best_intent = "unknown"
            best_confidence = 0.0

        return best_intent, best_confidence

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extraire entités du texte

        Args:
            text: Texte utilisateur

        Returns:
            Dict des entités trouvées
        """
        entities = {}
        text_lower = text.lower()

        for entity_name, pattern_data in self.entity_patterns.items():
            pattern = pattern_data["pattern"]
            matches = re.findall(pattern, text_lower)

            if matches:
                entities[entity_name] = matches

        return entities

    def process(self, text: str) -> Dict:
        """
        Processus complet NLU

        Args:
            text: Texte utilisateur

        Returns:
            Dict avec intent, confidence, entities
        """
        intent, confidence = self.classify_intent(text)
        entities = self.extract_entities(text)

        result = {
            'text': text,
            'intent': intent,
            'confidence': confidence,
            'entities': entities
        }

        return result


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("[TEST] NLU Component")
    print("=" * 80)

    nlu = NLUComponent()

    # Test cases
    test_sentences = [
        "Bonjour, comment allez-vous?",
        "Quel est le temps à Paris aujourd'hui?",
        "Quelle heure est-il maintenant?",
        "5 plus 3 égal combien?",
        "Raconte-moi une blague drôle",
        "Blablabla xyz"
    ]

    print("\n[TESTS]")
    for sentence in test_sentences:
        result = nlu.process(sentence)
        print(f"\nTexte: '{sentence}'")
        print(f"  Intent: {result['intent']} (confiance: {result['confidence']:.2%})")
        print(f"  Entities: {result['entities']}")
