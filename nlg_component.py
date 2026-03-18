#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP 3 Component 4 - NLG (Natural Language Generation)
Template-based response generation
"""

from typing import Dict, List
import random

# ============================================================================
# RESPONSE TEMPLATES
# ============================================================================

RESPONSE_TEMPLATES = {
    "greeting": [
        "Bonjour {user_name}, enchanté! Comment puis-je vous aider?",
        "Salut {user_name}! À votre service.",
        "Bienvenue {user_name}! Que puis-je faire pour vous?"
    ],

    "weather": [
        "À {location}, il devrait faire {weather} demain.",
        "Pour {location}, prévisions: {weather}.",
        "Le temps à {location} sera {weather}.",
    ],

    "time": [
        "Il est actuellement {time}.",
        "L'heure actuelle est {time}.",
        "Nous sommes à {time}.",
    ],

    "math": [
        "Le résultat est {result}.",
        "Cela fait {result}.",
        "La réponse est {result}.",
    ],

    "joke": [
        "{joke_text}",
    ],

    "unknown": [
        "Je n'ai pas bien compris.",
        "Pouvez-vous répéter s'il vous plaît?",
        "Pourriez-vous reformuler votre question?",
    ],

    "farewell": [
        "Au revoir {user_name}! À bientôt.",
        "À bientôt {user_name}!",
        "Bye {user_name}!",
    ]
}

# ============================================================================
# NLG COMPONENT
# ============================================================================

class NLGComponent:
    """Natural Language Generation"""

    def __init__(self):
        """Initialiser NLG"""
        self.templates = RESPONSE_TEMPLATES
        print("[NLG] Component initialisé ✓")

    def generate_response(self, action_dict: Dict) -> str:
        """
        Générer réponse naturelle à partir d'action

        Args:
            action_dict: Dict avec type, message, variables

        Returns:
            Texte réponse formatée
        """
        action_type = action_dict.get('type', 'unknown')

        # Si message pré-généré fourni, l'utiliser
        if 'message' in action_dict:
            return action_dict['message']

        # Sinon utiliser templates
        if action_type not in self.templates:
            action_type = 'unknown'

        # Choisir template aléatoire
        templates = self.templates[action_type]
        template = random.choice(templates)

        # Extraire variables et formatter
        response = self._format_template(template, action_dict)

        return response

    def _format_template(self, template: str, variables: Dict) -> str:
        """
        Formatter template avec variables

        Args:
            template: Template string avec {placeholders}
            variables: Dict des variables

        Returns:
            String formatée
        """
        try:
            response = template.format(**variables)
        except KeyError:
            # Si une clé manque, retourner template tel quel
            response = template

        return response


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("[TEST] NLG Component")
    print("=" * 80)

    nlg = NLGComponent()

    # Test cases
    test_actions = [
        {
            'type': 'greeting',
            'user_name': 'Alice'
        },
        {
            'type': 'weather',
            'location': 'Paris',
            'weather': 'nuageux'
        },
        {
            'type': 'time',
            'time': '15h30'
        },
        {
            'type': 'math',
            'result': 42
        },
        {
            'type': 'joke',
            'joke_text': "C'est l'histoire d'un mur qui tombe. Pas de perte!"
        }
    ]

    print("\n[TESTS]")
    for action in test_actions:
        response = nlg.generate_response(action)
        print(f"\nAction type: {action['type']}")
        print(f"Response: {response}")
