"""
Utilitaires pour gérer les fichiers pickle
Sauvegarde et chargement de données ML (résultats, statistiques, cache)
"""
import pickle
import json
import os
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PickleHandler:
    """
    Gestionnaire de fichiers pickle pour sauvegarder/charger des données
    """
    
    @staticmethod
    def save_pickle(data, filepath, compress=False):
        """
        Sauvegarde des données dans un fichier pickle
        
        Args:
            data: Données à sauvegarder (dict, list, object, etc.)
            filepath: Chemin du fichier pickle
            compress: Si True, utilise le protocole de compression
            
        Returns:
            bool: True si succès
        """
        try:
            # Créer le dossier si nécessaire
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            protocol = pickle.HIGHEST_PROTOCOL if compress else pickle.DEFAULT_PROTOCOL
            
            with open(filepath, 'wb') as f:
                pickle.dump(data, f, protocol=protocol)
            
            file_size = os.path.getsize(filepath) / 1024  # Ko
            logger.info(f"✅ Pickle sauvegardé: {filepath} ({file_size:.2f} Ko)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde pickle: {e}")
            return False
    
    @staticmethod
    def load_pickle(filepath):
        """
        Charge des données depuis un fichier pickle
        
        Args:
            filepath: Chemin du fichier pickle
            
        Returns:
            Les données chargées (ou None si erreur)
        """
        try:
            if not os.path.exists(filepath):
                logger.warning(f"Fichier pickle introuvable: {filepath}")
                return None
            
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            
            logger.info(f"✅ Pickle chargé: {filepath}")
            return data
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement pickle: {e}")
            return None
    
    @staticmethod
    def pickle_to_json(pickle_filepath, json_filepath=None):
        """
        Convertit un fichier pickle en JSON (pour inspection)
        
        Args:
            pickle_filepath: Chemin du fichier pickle
            json_filepath: Chemin du fichier JSON (optionnel)
            
        Returns:
            dict: Données converties
        """
        data = PickleHandler.load_pickle(pickle_filepath)
        if data is None:
            return None
        
        # Sauvegarder en JSON si chemin fourni
        if json_filepath:
            try:
                with open(json_filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)
                logger.info(f"✅ JSON créé: {json_filepath}")
            except Exception as e:
                logger.error(f"❌ Erreur conversion JSON: {e}")
        
        return data


class PredictionCache:
    """
    Cache de prédictions pour éviter de recalculer
    Utilise pickle pour persistance
    """
    
    def __init__(self, cache_file='prediction_cache.pkl'):
        self.cache_file = cache_file
        self.cache = self._load_cache()
    
    def _load_cache(self):
        """Charge le cache depuis le fichier pickle"""
        cache = PickleHandler.load_pickle(self.cache_file)
        return cache if cache else {}
    
    def _save_cache(self):
        """Sauvegarde le cache dans le fichier pickle"""
        PickleHandler.save_pickle(self.cache, self.cache_file)
    
    def get_cache_key(self, image_path, model_key):
        """Génère une clé de cache basée sur le fichier et le modèle"""
        import hashlib
        
        # Hash du contenu de l'image
        with open(image_path, 'rb') as f:
            image_hash = hashlib.md5(f.read()).hexdigest()
        
        return f"{image_hash}_{model_key}"
    
    def get(self, image_path, model_key):
        """
        Récupère une prédiction du cache
        
        Returns:
            dict: Résultat de prédiction (ou None si pas en cache)
        """
        cache_key = self.get_cache_key(image_path, model_key)
        
        if cache_key in self.cache:
            logger.info(f"🔍 Prédiction trouvée dans le cache")
            return self.cache[cache_key]
        
        return None
    
    def set(self, image_path, model_key, result):
        """
        Ajoute une prédiction au cache
        
        Args:
            image_path: Chemin de l'image
            model_key: Clé du modèle utilisé
            result: Résultat de prédiction
        """
        cache_key = self.get_cache_key(image_path, model_key)
        
        self.cache[cache_key] = {
            'result': result,
            'timestamp': datetime.now().isoformat(),
            'model': model_key
        }
        
        self._save_cache()
        logger.info(f"💾 Prédiction ajoutée au cache")
    
    def clear(self):
        """Vide le cache"""
        self.cache = {}
        self._save_cache()
        logger.info("🗑️ Cache vidé")
    
    def get_stats(self):
        """Retourne des statistiques sur le cache"""
        return {
            'total_predictions': len(self.cache),
            'cache_file': self.cache_file,
            'file_exists': os.path.exists(self.cache_file),
            'file_size_kb': os.path.getsize(self.cache_file) / 1024 if os.path.exists(self.cache_file) else 0
        }


class ModelResultsExporter:
    """
    Exporte les résultats de modèles ML dans différents formats
    """
    
    @staticmethod
    def export_results(results, output_dir='exports'):
        """
        Exporte les résultats dans plusieurs formats
        
        Args:
            results: Dictionnaire de résultats
            output_dir: Dossier de sortie
            
        Returns:
            dict: Chemins des fichiers créés
        """
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        files_created = {}
        
        # 1. Pickle (format natif Python)
        pickle_file = os.path.join(output_dir, f'results_{timestamp}.pkl')
        if PickleHandler.save_pickle(results, pickle_file, compress=True):
            files_created['pickle'] = pickle_file
        
        # 2. JSON (format lisible)
        json_file = os.path.join(output_dir, f'results_{timestamp}.json')
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)
            files_created['json'] = json_file
        except Exception as e:
            logger.error(f"Erreur export JSON: {e}")
        
        # 3. TXT (format simple)
        txt_file = os.path.join(output_dir, f'results_{timestamp}.txt')
        try:
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("RÉSULTATS DE PRÉDICTION\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                
                for key, value in results.items():
                    f.write(f"{key}: {value}\n")
            
            files_created['txt'] = txt_file
        except Exception as e:
            logger.error(f"Erreur export TXT: {e}")
        
        logger.info(f"✅ Résultats exportés: {len(files_created)} fichiers créés")
        return files_created


def save_training_history(history, filepath='training_history.pkl'):
    """
    Sauvegarde l'historique d'entraînement d'un modèle
    
    Args:
        history: Objet History de Keras
        filepath: Chemin du fichier pickle
    """
    history_dict = {
        'history': history.history,
        'params': history.params,
        'epoch': history.epoch
    }
    
    return PickleHandler.save_pickle(history_dict, filepath)


def load_training_history(filepath='training_history.pkl'):
    """
    Charge l'historique d'entraînement depuis un pickle
    
    Args:
        filepath: Chemin du fichier pickle
        
    Returns:
        dict: Historique d'entraînement
    """
    return PickleHandler.load_pickle(filepath)
