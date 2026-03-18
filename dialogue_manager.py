#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP 3 Component 3 - Dialogue Manager
State machine + context tracking
"""

from typing import Dict, List, Tuple
from enum import Enum

# ============================================================================
# DIALOGUE STATES
# ============================================================================

class DialogueState(Enum):
    """États du dialogue"""
    START = "start"
    GREETING = "greeting"
    LISTENING = "listening"
    PROCESSING = "processing"
    RESPONDING = "responding"
    END = "end"

# ============================================================================
# DIALOGUE MANAGER
# ============================================================================

class DialogueManager:
    """Gestion du dialogue et suivi du contexte"""

    def __init__(self):
        """Initialiser dialogue manager"""
        self.state = DialogueState.START
        self.context = {
            'turn_count': 0,
            'user_name': 'Utilisateur',
            'last_intent': None,
            'last_location': None,
            'last_query': None,
            'conversation_history': []
        }
        print("[Dialogue] Manager initialisé ✓")

    def update_context(self, intent: str, entities: Dict[str, List[str]]):
        """
        Mettre à jour contexte avec information nouvelle

        Args:
            intent: Intent détecté
            entities: Entités extraites
        """
        self.context['turn_count'] += 1
        self.context['last_intent'] = intent

        # Mettre à jour location si présente
        if 'location' in entities and entities['location']:
            self.context['last_location'] = entities['location'][0]

        # Mettre à jour query
        self.context['last_query'] = {
            'intent': intent,
            'entities': entities
        }

    def process_intent(self, intent: str, entities: Dict[str, List[str]]) -> Dict:
        """
        Traiter intent et retourner action

        Args:
            intent: Intent détecté
            entities: Entités extraites

        Returns:
            Dict avec action et état suivant
        """
        # Mettre à jour contexte
        self.update_context(intent, entities)

        # Dispatcher selon intent
        if intent == "greeting":
            action = self._handle_greeting()
            next_state = DialogueState.GREETING

        elif intent == "weather":
            action = self._handle_weather(entities)
            next_state = DialogueState.RESPONDING

        elif intent == "time":
            action = self._handle_time()
            next_state = DialogueState.RESPONDING

        elif intent == "math":
            action = self._handle_math(entities)
            next_state = DialogueState.RESPONDING

        elif intent == "joke":
            action = self._handle_joke()
            next_state = DialogueState.RESPONDING

        else:
            action = self._handle_unknown()
            next_state = DialogueState.LISTENING

        # Mettre à jour état
        self.state = next_state

        return {
            'action': action,
            'next_state': next_state,
            'context': self.context.copy()
        }

    def _handle_greeting(self) -> Dict:
        """Traiter salutation"""
        return {
            'type': 'greeting',
            'message': f"Bonjour {self.context['user_name']}! Je suis votre assistant vocal. Comment puis-je vous aider?",
            'action': 'listen'
        }

    def _handle_weather(self, entities: Dict) -> Dict:
        """
        Traiter demande météo

        Exemple de context tracking:
        - User 1: "Météo à Paris"  → location = Paris
        - User 2: "Et demain?"      → Utiliser Paris du contexte
        """
        location = None

        # Chercher location dans entities
        if 'location' in entities and entities['location']:
            location = entities['location'][0]

        # Fallback sur contexte si pas d'entité
        elif self.context['last_location']:
            location = self.context['last_location']

        else:
            location = "votre région"

        # Template réponse
        message = f"À {location}, il devrait faire beau demain."

        return {
            'type': 'weather',
            'message': message,
            'location': location,
            'action': 'speak'
        }

    def _handle_time(self) -> Dict:
        """Traiter demande heure"""
        from datetime import datetime

        now = datetime.now()
        hour = now.hour
        minute = now.minute

        message = f"Il est actuellement {hour}h{minute:02d}."

        return {
            'type': 'time',
            'message': message,
            'action': 'speak'
        }

    def _handle_math(self, entities: Dict) -> Dict:
        """Traiter calcul simple"""
        numbers = entities.get('number', [])

        if len(numbers) >= 2:
            # Parser simple : additionner les nombres trouvés
            total = sum(int(n) for n in numbers)
            message = f"Le résultat est {total}."
        else:
            message = "Je n'ai pas assez de nombres pour calculer."

        return {
            'type': 'math',
            'message': message,
            'action': 'speak'
        }

    def _handle_joke(self) -> Dict:
        """Traiter demande blague"""
        jokes = [
            "Pourquoi les plongeurs plongent-ils toujours en arrière? Parce que sinon ils tombent dans le bateau!",
            "Quel est le comble pour un électricien? De ne pas être au courant!",
            "Comment appelle-t-on un chat tombé dans un pot de peinture le jour de Noël? Un chat-peint de Noël!",
            "Qu'est-ce qui est jaune et qui attend? Jonathan!"
        ]

        import random
        joke = random.choice(jokes)

        return {
            'type': 'joke',
            'message': joke,
            'action': 'speak'
        }

    def _handle_unknown(self) -> Dict:
        """Traiter intent inconnu"""
        return {
            'type': 'unknown',
            'message': "Je n'ai pas bien compris. Pouvez-vous reformuler?",
            'action': 'listen'
        }

    def reset(self):
        """Réinitialiser le dialogue"""
        self.state = DialogueState.START
        self.context = {
            'turn_count': 0,
            'user_name': 'Utilisateur',
            'last_intent': None,
            'last_location': None,
            'last_query': None,
            'conversation_history': []
        }
        print("[Dialogue] Reset ✓")


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("[TEST] Dialogue Manager")
    print("=" * 80)

    dm = DialogueManager()

    # Simulation conversation
    test_turns = [
        ("greeting", {}),
        ("weather", {'location': ['Paris']}),
        ("weather", {}),  # Devrait réutiliser Paris du contexte
        ("time", {}),
        ("joke", {})
    ]

    print("\n[SIMULATION]")
    for intent, entities in test_turns:
        result = dm.process_intent(intent, entities)
        print(f"\nTurn {dm.context['turn_count']}:")
        print(f"  Intent: {intent}")
        print(f"  Message: {result['action']['message']}")
        print(f"  Context location: {dm.context['last_location']}")
