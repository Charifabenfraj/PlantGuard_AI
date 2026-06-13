"""
Utilitaires pour le Machine Learning
Gestion du modèle TensorFlow et prédictions
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Réduire les logs TensorFlow

import numpy as np
from PIL import Image
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Variable globale pour le modèle (chargé une seule fois)
_model = None


def load_model():
    """
    Charge le modèle TensorFlow
    Le modèle est chargé une seule fois et gardé en mémoire
    """
    global _model
    
    if _model is None:
        try:
            import tensorflow as tf
            model_path = str(settings.ML_BEST_MODEL)
            
            if not os.path.exists(model_path):
                logger.error(f"Modèle introuvable: {model_path}")
                return None
            
            logger.info(f"Chargement du modèle: {model_path}")
            _model = tf.keras.models.load_model(model_path)
            logger.info("✅ Modèle Transfer Learning chargé avec succès!")
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle: {e}")
            return None
    
    return _model


def preprocess_image(image_path):
    """
    Prétraite l'image pour le modèle
    - Ouvre l'image
    - Redimensionne à IMG_SIZE x IMG_SIZE
    - Convertit en array numpy
    - Normalise entre 0 et 1
    - Ajoute la dimension batch
    
    Args:
        image_path: Chemin vers l'image
        
    Returns:
        np.array: Image prétraitée prête pour la prédiction
    """
    try:
        # Ouvrir et convertir en RGB
        img = Image.open(image_path).convert('RGB')
        
        # Redimensionner
        img = img.resize((settings.IMG_SIZE, settings.IMG_SIZE))
        
        # Convertir en array et normaliser
        img_array = np.array(img, dtype=np.float32) / 255.0
        
        # Ajouter dimension batch
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
        
    except Exception as e:
        logger.error(f"Erreur lors du prétraitement: {e}")
        raise


def predict_disease(image_path, temperature=1.0):
    """
    Fait la prédiction de la maladie sur une image
    
    Args:
        image_path: Chemin vers l'image à analyser
        temperature: Facteur de lissage (1.0 = normal, >1.0 = moins confiant, <1.0 = plus confiant)
        
    Returns:
        dict: Dictionnaire contenant:
            - prediction: Nom de la maladie prédite
            - confidence: Pourcentage de confiance (0-100)
            - top_predictions: Liste des 3 meilleures prédictions
    """
    try:
        # Charger le modèle
        model = load_model()
        if model is None:
            raise Exception("Le modèle n'a pas pu être chargé")
        
        # Prétraiter l'image
        img_array = preprocess_image(image_path)
        
        # Logs de debug
        logger.info(f"Image shape: {img_array.shape}, min: {img_array.min():.3f}, max: {img_array.max():.3f}")
        
        # Faire la prédiction
        predictions = model.predict(img_array, verbose=0)
        
        # Appliquer temperature scaling pour calibrer la confiance
        if temperature != 1.0:
            predictions = np.exp(np.log(predictions + 1e-10) / temperature)
            predictions = predictions / np.sum(predictions, axis=-1, keepdims=True)
        
        # Logs de debug
        logger.info(f"Predictions sum: {predictions.sum():.3f}, max: {predictions.max():.3f}, min: {predictions.min():.6f}")
        
        # Classe prédite
        predicted_class_idx = int(np.argmax(predictions[0]))
        confidence = float(predictions[0][predicted_class_idx] * 100)
        
        # Top 3 des prédictions
        top_3_idx = np.argsort(predictions[0])[-3:][::-1]
        top_predictions = []
        
        for idx in top_3_idx:
            class_name = settings.CLASS_NAMES[int(idx)]
            class_confidence = float(predictions[0][int(idx)] * 100)
            
            top_predictions.append({
                'class': class_name,
                'confidence': round(class_confidence, 2)
            })
        
        # Logs détaillés
        logger.info(f"Top prediction: {settings.CLASS_NAMES[predicted_class_idx]} ({confidence:.2f}%)")
        logger.info(f"Top 3: {[f'{p['class']}: {p['confidence']}%' for p in top_predictions]}")
        
        # Détection des confusions connues (maladies similaires)
        confusion_warning = None
        CONFUSION_PAIRS = {
            'Tomato_Spider_mites_Two_spotted_spider_mite': [
                'Tomato__Target_Spot',
                'Tomato_Septoria_leaf_spot'
            ],
            'Tomato__Target_Spot': [
                'Tomato_Spider_mites_Two_spotted_spider_mite',
                'Tomato_Septoria_leaf_spot'
            ],
            'Tomato_Septoria_leaf_spot': [
                'Tomato_Spider_mites_Two_spotted_spider_mite',
                'Tomato__Target_Spot'
            ],
            'Tomato_Early_blight': ['Tomato_Late_blight'],
            'Tomato_Late_blight': ['Tomato_Early_blight'],
        }
        
        # Si confiance très élevée mais maladie confusable
        if confidence > 95.0 and settings.CLASS_NAMES[predicted_class_idx] in CONFUSION_PAIRS:
            similar_diseases = CONFUSION_PAIRS[settings.CLASS_NAMES[predicted_class_idx]]
            confusion_warning = {
                'message': 'Cette maladie peut être confondue avec d\'autres maladies similaires.',
                'similar_diseases': similar_diseases
            }
            logger.warning(f"⚠️ Confusion possible avec: {similar_diseases}")
        
        result = {
            'prediction': settings.CLASS_NAMES[predicted_class_idx],
            'confidence': round(confidence, 2),
            'top_predictions': top_predictions,
            'confusion_warning': confusion_warning,
            'all_predictions': {
                settings.CLASS_NAMES[i]: round(float(predictions[0][i] * 100), 2)
                for i in range(len(settings.CLASS_NAMES))
            }
        }
        
        logger.info(f"✅ Prédiction réussie: {result['prediction']} ({result['confidence']}%)")
        return result
        
    except Exception as e:
        logger.error(f"Erreur lors de la prédiction: {e}")
        raise


def get_disease_info(class_name):
    """
    Retourne des informations sur une maladie
    
    Args:
        class_name: Nom de la classe de maladie
        
    Returns:
        dict: Informations sur la maladie
    """
    # Extraction du nom de la plante et de la maladie
    parts = class_name.split('_')
    
    if 'healthy' in class_name.lower():
        status = "Saine"
        severity = "Aucune"
        color = "success"
    else:
        status = "Malade"
        severity = "Moyenne à Élevée"
        color = "danger"
    
    # Déterminer la plante
    if 'Tomato' in class_name:
        plant = "Tomate"
    elif 'Potato' in class_name:
        plant = "Pomme de terre"
    elif 'Pepper' in class_name:
        plant = "Poivron"
    else:
        plant = "Inconnue"
    
    return {
        'plant': plant,
        'status': status,
        'severity': severity,
        'color': color,
        'full_name': class_name.replace('_', ' ')
    }
