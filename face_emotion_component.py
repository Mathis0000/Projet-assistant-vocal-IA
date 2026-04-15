#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Composant détection d'émotion faciale
Modèle entraîné sur FER2013 — 7 émotions, entrée 48x48 niveaux de gris
"""

import numpy as np
import cv2
from pathlib import Path

EMOTIONS = ["Colère", "Dégoût", "Peur", "Joie", "Tristesse", "Surprise", "Neutre"]
EMOTIONS_EN = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]
EMOTION_EMOJI = {
    "Colère":    "😠",
    "Dégoût":   "🤢",
    "Peur":      "😨",
    "Joie":      "😊",
    "Tristesse": "😢",
    "Surprise":  "😲",
    "Neutre":    "😐",
}
EMOTION_COLOR = {
    "Colère":    (60,  20,  20),
    "Dégoût":   (20,  60,  20),
    "Peur":      (40,  20,  60),
    "Joie":      (20,  50,  20),
    "Tristesse": (20,  30,  60),
    "Surprise":  (50,  40,  10),
    "Neutre":    (20,  40,  50),
}

MODEL_PATH = Path(__file__).parent / "tp2_model_fixed.keras"

# Haar cascade livré avec OpenCV
HAAR_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"


class FaceEmotionDetector:
    def __init__(self):
        self.model = None
        self.face_cascade = None
        self._load()

    def _load(self):
        # Chargement modèle Keras
        # Le modèle a été entraîné avec TF-Keras 2 (renorm dans BatchNormalization).
        # On utilise un custom_objects pour ignorer les paramètres inconnus de Keras 3.
        try:
            import tensorflow as tf
            from tensorflow.keras import layers, models

            # Architecture lue depuis le config du .keras (reconstruite manuellement
            # pour contourner l'incompatibilité quantization_config de Keras 3)
            def build_model():
                m = models.Sequential([
                    layers.Input(shape=(48, 48, 1)),
                    layers.Conv2D(32, (3,3), padding='same', activation='relu'),
                    layers.BatchNormalization(),
                    layers.Conv2D(32, (3,3), padding='same', activation='relu'),
                    layers.BatchNormalization(),
                    layers.MaxPooling2D(2,2),
                    layers.Dropout(0.25),
                    layers.Conv2D(64, (3,3), padding='same', activation='relu'),
                    layers.BatchNormalization(),
                    layers.Conv2D(64, (3,3), padding='same', activation='relu'),
                    layers.BatchNormalization(),
                    layers.MaxPooling2D(2,2),
                    layers.Dropout(0.25),
                    layers.Conv2D(128, (3,3), padding='same', activation='relu'),
                    layers.BatchNormalization(),
                    layers.MaxPooling2D(2,2),
                    layers.Dropout(0.25),
                    layers.Flatten(),
                    layers.Dense(256, activation='relu'),
                    layers.BatchNormalization(),
                    layers.Dropout(0.5),
                    layers.Dense(128, activation='relu'),
                    layers.Dropout(0.3),
                    layers.Dense(7, activation='softmax'),
                ])
                return m

            model = build_model()
            # Charger les poids depuis le .h5 extrait du .keras (zip)
            weights_h5 = Path(__file__).parent / "model.weights.h5"
            model.load_weights(str(weights_h5))
            self.model = model
        except Exception as e:
            raise RuntimeError(f"Impossible de charger {MODEL_PATH}: {e}")

        # Haar cascade pour la détection de visage
        self.face_cascade = cv2.CascadeClassifier(HAAR_PATH)
        if self.face_cascade.empty():
            raise RuntimeError("Haar cascade introuvable — vérifier l'installation d'OpenCV")

    def predict_frame(self, frame_bgr: np.ndarray):
        """
        Analyse une frame BGR (numpy array) et retourne une liste de détections.
        Chaque détection : {"bbox": (x,y,w,h), "emotion": str, "emoji": str,
                            "confidence": float, "scores": dict}
        """
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
        )
        results = []
        for (x, y, w, h) in faces:
            roi = gray[y:y+h, x:x+w]
            roi = cv2.resize(roi, (48, 48))
            roi = roi.astype("float32") / 255.0
            roi = np.expand_dims(roi, axis=(0, -1))  # (1, 48, 48, 1)

            preds = self.model.predict(roi, verbose=0)[0]
            idx = int(np.argmax(preds))
            emotion = EMOTIONS[idx]
            results.append({
                "bbox":       (x, y, w, h),
                "emotion":    emotion,
                "emoji":      EMOTION_EMOJI[emotion],
                "confidence": float(preds[idx]),
                "scores":     {EMOTIONS[i]: float(preds[i]) for i in range(len(EMOTIONS))},
            })
        return results

    def annotate_frame(self, frame_bgr: np.ndarray, detections: list) -> np.ndarray:
        """Dessine les boîtes et labels sur la frame."""
        out = frame_bgr.copy()
        for d in detections:
            x, y, w, h = d["bbox"]
            label = f'{d["emoji"]} {d["emotion"]} {d["confidence"]:.0%}'
            # Boîte cyan
            cv2.rectangle(out, (x, y), (x+w, y+h), (0, 229, 255), 2)
            # Fond label
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
            cv2.rectangle(out, (x, y-th-10), (x+tw+6, y), (0, 229, 255), -1)
            cv2.putText(out, label, (x+3, y-4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1, cv2.LINE_AA)
        return out


def create_detector() -> FaceEmotionDetector:
    return FaceEmotionDetector()
