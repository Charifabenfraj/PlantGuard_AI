"""
Views supplémentaires pour la gestion des modèles
Permet de comparer, changer et gérer plusieurs modèles ML
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from .model_manager import get_model_manager
from .ml_utils import predict_disease
from .pickle_utils import PickleHandler, ModelResultsExporter
import os
import logging

logger = logging.getLogger(__name__)


def models_list(request):
    """
    Affiche la liste de tous les modèles disponibles
    """
    try:
        manager = get_model_manager()
        models = manager.list_models()
        current_model = manager.get_current_model_info()
        
        context = {
            'models': models,
            'current_model': current_model,
            'title': 'Modèles Disponibles'
        }
        
        return render(request, 'detector/models_list.html', context)
        
    except Exception as e:
        logger.error(f"Erreur liste modèles: {e}")
        return render(request, 'detector/error.html', {'error': str(e)})


def switch_model(request):
    """
    API pour changer le modèle actif
    """
    if request.method == 'POST':
        model_key = request.POST.get('model_key')
        
        if not model_key:
            return JsonResponse({'error': 'model_key requis'}, status=400)
        
        try:
            manager = get_model_manager()
            manager.switch_model(model_key)
            current_model = manager.get_current_model_info()
            
            return JsonResponse({
                'success': True,
                'message': f"Modèle changé: {current_model['name']}",
                'current_model': current_model
            })
            
        except Exception as e:
            logger.error(f"Erreur changement modèle: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Méthode POST requise'}, status=405)


def compare_models(request):
    """
    Compare tous les modèles sur une même image
    """
    if request.method == 'POST':
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'Aucune image fournie'}, status=400)
        
        image = request.FILES['image']
        
        # Sauvegarder temporairement l'image
        from django.core.files.storage import default_storage
        temp_path = default_storage.save(f'temp_compare/{image.name}', image)
        full_path = os.path.join(settings.MEDIA_ROOT, temp_path)
        
        try:
            manager = get_model_manager()
            results = manager.compare_models(full_path)
            
            # Nettoyer le fichier temporaire
            default_storage.delete(temp_path)
            
            # Optionnel: Exporter les résultats en pickle
            if request.POST.get('export', '').lower() == 'true':
                exporter = ModelResultsExporter()
                export_files = exporter.export_results(results)
                results['export_files'] = export_files
            
            return JsonResponse({
                'success': True,
                'results': results
            })
            
        except Exception as e:
            logger.error(f"Erreur comparaison modèles: {e}")
            # Nettoyer en cas d'erreur
            if default_storage.exists(temp_path):
                default_storage.delete(temp_path)
            return JsonResponse({'error': str(e)}, status=500)
    
    # GET: Afficher le formulaire de comparaison
    return render(request, 'detector/compare_models.html', {
        'title': 'Comparer les Modèles'
    })


def model_stats(request):
    """
    Affiche les statistiques des modèles
    """
    try:
        manager = get_model_manager()
        
        stats = {
            'available_models': len(manager.available_models),
            'loaded_models': len(manager.models),
            'current_model': manager.get_current_model_info(),
            'models_list': manager.list_models()
        }
        
        # Vérifier si un fichier pickle de stats existe
        pickle_stats_file = os.path.join(settings.PROJECT_ROOT, 'model_stats.pkl')
        if os.path.exists(pickle_stats_file):
            pickle_stats = PickleHandler.load_pickle(pickle_stats_file)
            stats['pickle_stats'] = pickle_stats
        
        context = {
            'stats': stats,
            'title': 'Statistiques des Modèles'
        }
        
        return render(request, 'detector/model_stats.html', context)
        
    except Exception as e:
        logger.error(f"Erreur stats modèles: {e}")
        return render(request, 'detector/error.html', {'error': str(e)})


def save_model_stats_pickle(request):
    """
    API pour sauvegarder les stats des modèles en pickle
    """
    if request.method == 'POST':
        try:
            manager = get_model_manager()
            
            filepath = os.path.join(settings.PROJECT_ROOT, 'model_stats.pkl')
            manager.save_model_stats(filepath)
            
            return JsonResponse({
                'success': True,
                'message': f'Stats sauvegardées: {filepath}',
                'filepath': filepath
            })
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde stats: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Méthode POST requise'}, status=405)


def predict_with_model(request):
    """
    Prédiction avec un modèle spécifique
    Permet de choisir le modèle dans le formulaire
    """
    if request.method == 'POST':
        if 'image' not in request.FILES:
            return render(request, 'detector/home.html', {
                'error': 'Veuillez sélectionner une image.'
            })
        
        image = request.FILES['image']
        model_key = request.POST.get('model_key', None)
        use_cache = request.POST.get('use_cache', 'false').lower() == 'true'
        
        # Sauvegarder l'image
        from django.core.files.storage import default_storage
        file_path = default_storage.save(f'uploads/{image.name}', image)
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        
        try:
            # Faire la prédiction avec le modèle spécifié
            result = predict_disease(full_path, model_key=model_key, use_cache=use_cache)
            
            # Ajouter des infos supplémentaires
            from .ml_utils import get_disease_info
            disease_info = get_disease_info(result['prediction'])
            
            context = {
                'prediction': result['prediction'],
                'confidence': result['confidence'],
                'top_predictions': result['top_predictions'],
                'model_used': result.get('model_used', 'Unknown'),
                'disease_info': disease_info,
                'image_url': settings.MEDIA_URL + file_path,
                'from_cache': use_cache and 'cache' in str(result)
            }
            
            return render(request, 'detector/result.html', context)
            
        except Exception as e:
            logger.error(f"Erreur prédiction: {e}")
            # Nettoyer le fichier en cas d'erreur
            if default_storage.exists(file_path):
                default_storage.delete(file_path)
            return render(request, 'detector/home.html', {
                'error': f'Erreur lors de la prédiction: {str(e)}'
            })
    
    # GET: Afficher le formulaire avec choix de modèle
    try:
        manager = get_model_manager()
        models = manager.list_models()
        
        return render(request, 'detector/home.html', {
            'models': models,
            'show_model_selector': True
        })
    except Exception as e:
        return render(request, 'detector/home.html', {
            'error': f'Erreur chargement modèles: {str(e)}'
        })
