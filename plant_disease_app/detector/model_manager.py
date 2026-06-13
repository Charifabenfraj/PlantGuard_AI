"""
Gestionnaire de modèles ML pour basculer entre différents modèles
Permet de charger, comparer et utiliser plusieurs modèles
"""
import os
import json
import pickle
from pathlib import Path
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Gestionnaire de modèles ML
    Permet de charger et gérer plusieurs modèles simultanément
    """
    
    def __init__(self):
        self.models = {}  # Cache des modèles chargés
        self.current_model_key = settings.DEFAULT_MODEL
        self.available_models = settings.AVAILABLE_MODELS
    
    def load_model(self, model_key=None):
        """
        Charge un modèle spécifique
        
        Args:
            model_key: Clé du modèle à charger (par défaut: DEFAULT_MODEL)
            
        Returns:
            Le modèle TensorFlow chargé
        """
        if model_key is None:
            model_key = self.current_model_key
        
        # Vérifier si le modèle est déjà en cache
        if model_key in self.models:
            logger.info(f"Modèle '{model_key}' déjà chargé (cache)")
            return self.models[model_key]
        
        # Vérifier que le modèle existe
        if model_key not in self.available_models:
            raise ValueError(f"Modèle '{model_key}' non disponible. Modèles disponibles: {list(self.available_models.keys())}")
        
        model_info = self.available_models[model_key]
        model_path = str(model_info['path'])
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modèle introuvable: {model_path}")
        
        try:
            import tensorflow as tf
            logger.info(f"Chargement du modèle: {model_info['name']} ({model_path})")
            
            model = tf.keras.models.load_model(model_path)
            self.models[model_key] = model
            
            logger.info(f"✅ Modèle chargé: {model_info['name']} - Accuracy: {model_info['accuracy']*100:.2f}%")
            return model
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle: {e}")
            raise
    
    def get_model(self, model_key=None):
        """Récupère un modèle (charge si nécessaire)"""
        return self.load_model(model_key)
    
    def switch_model(self, model_key):
        """
        Change le modèle actif
        
        Args:
            model_key: Clé du nouveau modèle à utiliser
        """
        if model_key not in self.available_models:
            raise ValueError(f"Modèle '{model_key}' non disponible")
        
        self.current_model_key = model_key
        logger.info(f"Modèle actif changé: {self.available_models[model_key]['name']}")
    
    def get_current_model_info(self):
        """Retourne les informations du modèle actif"""
        return {
            'key': self.current_model_key,
            **self.available_models[self.current_model_key]
        }
    
    def list_models(self):
        """Liste tous les modèles disponibles avec leurs infos"""
        models_list = []
        for key, info in self.available_models.items():
            models_list.append({
                'key': key,
                'name': info['name'],
                'accuracy': f"{info['accuracy']*100:.2f}%",
                'params': f"{info['params']:,}",
                'description': info['description'],
                'is_current': key == self.current_model_key,
                'exists': os.path.exists(str(info['path']))
            })
        return models_list
    
    def compare_models(self, image_path):
        """
        Compare les prédictions de tous les modèles sur une image
        
        Args:
            image_path: Chemin vers l'image à analyser
            
        Returns:
            dict: Résultats de tous les modèles
        """
        from .ml_utils import preprocess_image
        import numpy as np
        
        results = {}
        img_array = preprocess_image(image_path)
        
        for model_key, model_info in self.available_models.items():
            try:
                model = self.load_model(model_key)
                predictions = model.predict(img_array, verbose=0)
                
                predicted_idx = int(np.argmax(predictions[0]))
                confidence = float(predictions[0][predicted_idx] * 100)
                
                results[model_key] = {
                    'model_name': model_info['name'],
                    'prediction': settings.CLASS_NAMES[predicted_idx],
                    'confidence': round(confidence, 2),
                    'accuracy': model_info['accuracy']
                }
            except Exception as e:
                results[model_key] = {
                    'model_name': model_info['name'],
                    'error': str(e)
                }
        
        return results
    
    def save_model_stats(self, filepath='model_stats.pkl'):
        """
        Sauvegarde les statistiques des modèles dans un fichier pickle
        
        Args:
            filepath: Chemin du fichier pickle
        """
        stats = {
            'available_models': self.available_models,
            'current_model': self.current_model_key,
            'loaded_models': list(self.models.keys())
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(stats, f)
        
        logger.info(f"Statistiques sauvegardées: {filepath}")
    
    def load_model_stats(self, filepath='model_stats.pkl'):
        """
        Charge les statistiques des modèles depuis un fichier pickle
        
        Args:
            filepath: Chemin du fichier pickle
            
        Returns:
            dict: Statistiques chargées
        """
        if not os.path.exists(filepath):
            logger.warning(f"Fichier pickle introuvable: {filepath}")
            return None
        
        with open(filepath, 'rb') as f:
            stats = pickle.load(f)
        
        logger.info(f"Statistiques chargées: {filepath}")
        return stats


# Instance globale du gestionnaire de modèles
_model_manager = None

def get_model_manager():
    """Retourne l'instance unique du gestionnaire de modèles"""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager
