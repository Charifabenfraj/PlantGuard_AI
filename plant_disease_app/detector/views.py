from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
import os
import logging
from .ml_utils import predict_disease, get_disease_info

logger = logging.getLogger(__name__)

# Importer TensorFlow (sera utilisé dans ml_utils)
try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False


def home(request):
    """Page d'accueil avec formulaire d'upload"""
    context = {
        'tf_available': TF_AVAILABLE,
        'num_classes': settings.NUM_CLASSES,
    }
    return render(request, 'detector/home.html', context)


def predict(request):
    """Traite l'upload et fait la prédiction"""
    if request.method == 'POST' and request.FILES.get('image'):
        # Sauvegarder l'image uploadée
        uploaded_file = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_url = fs.url(filename)
        file_path = fs.path(filename)
        
        try:
            # Faire la prédiction avec le modèle ML réel
            logger.info(f"Analyse de l'image: {filename}")
            results = predict_disease(file_path)
            
            # Obtenir des infos supplémentaires sur la maladie
            disease_info = get_disease_info(results['prediction'])
            
            context = {
                'uploaded': True,
                'file_url': file_url,
                'filename': filename,
                'prediction': results['prediction'],
                'confidence': results['confidence'],
                'top_predictions': results['top_predictions'],
                'confusion_warning': results.get('confusion_warning'),
                'disease_info': disease_info,
                'success': True
            }
            
            logger.info(f"Prédiction réussie: {results['prediction']}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la prédiction: {e}")
            context = {
                'uploaded': True,
                'file_url': file_url,
                'filename': filename,
                'error': True,
                'error_message': f"Erreur lors de l'analyse: {str(e)}",
                'tf_available': TF_AVAILABLE
            }
        
        return render(request, 'detector/result.html', context)
    
    # Si pas de POST ou pas d'image, rediriger vers l'accueil
    messages.warning(request, "Veuillez télécharger une image")
    return redirect('detector:home')


def about(request):
    """Page à propos du projet"""
    context = {
        'classes': settings.CLASS_NAMES,
        'num_classes': settings.NUM_CLASSES,
        'img_size': settings.IMG_SIZE,
    }
    return render(request, 'detector/about.html', context)

