"""
Script de debug pour analyser les prédictions du modèle
"""
import os
import sys
import django

# Configuration Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plant_disease_app.settings')
django.setup()

import numpy as np
import tensorflow as tf
from django.conf import settings
from detector.ml_utils import load_model, preprocess_image

def analyze_prediction(image_path):
    """Analyse détaillée d'une prédiction"""
    print("="*70)
    print("🔍 ANALYSE DÉTAILLÉE DE LA PRÉDICTION")
    print("="*70)
    
    # 1. Charger le modèle
    print("\n1️⃣ Chargement du modèle...")
    model = load_model()
    if model is None:
        print("❌ Erreur : Le modèle n'a pas pu être chargé")
        return
    print(f"✅ Modèle chargé : {settings.ML_BEST_MODEL}")
    
    # 2. Vérifier l'image
    print(f"\n2️⃣ Analyse de l'image...")
    if not os.path.exists(image_path):
        print(f"❌ Image introuvable : {image_path}")
        return
    print(f"✅ Image trouvée : {image_path}")
    
    # 3. Prétraitement
    print(f"\n3️⃣ Prétraitement...")
    img_array = preprocess_image(image_path)
    print(f"   Shape: {img_array.shape}")
    print(f"   Min value: {img_array.min():.4f}")
    print(f"   Max value: {img_array.max():.4f}")
    print(f"   Mean value: {img_array.mean():.4f}")
    
    # 4. Prédiction brute
    print(f"\n4️⃣ Prédiction brute (avant softmax si applicable)...")
    predictions = model.predict(img_array, verbose=0)
    
    print(f"   Shape des prédictions: {predictions.shape}")
    print(f"   Somme des probabilités: {predictions.sum():.4f}")
    print(f"   Min probabilité: {predictions.min():.6f}")
    print(f"   Max probabilité: {predictions.max():.6f}")
    
    # 5. Top 5 des prédictions
    print(f"\n5️⃣ Top 5 des prédictions :")
    top_5_idx = np.argsort(predictions[0])[-5:][::-1]
    
    for rank, idx in enumerate(top_5_idx, 1):
        class_name = settings.CLASS_NAMES[idx]
        confidence = predictions[0][idx] * 100
        print(f"   {rank}. {class_name:50s} : {confidence:6.2f}%")
    
    # 6. Distribution des probabilités
    print(f"\n6️⃣ Distribution complète :")
    sorted_idx = np.argsort(predictions[0])[::-1]
    
    for idx in sorted_idx:
        class_name = settings.CLASS_NAMES[idx]
        confidence = predictions[0][idx] * 100
        bar_length = int(confidence / 2)  # Scale pour affichage
        bar = "█" * bar_length
        print(f"   {class_name:50s} : {confidence:6.2f}% {bar}")
    
    # 7. Statistiques
    print(f"\n7️⃣ Statistiques :")
    probs = predictions[0]
    print(f"   Entropie: {-np.sum(probs * np.log(probs + 1e-10)):.4f}")
    print(f"   Écart-type: {probs.std():.4f}")
    print(f"   Différence 1er-2ème: {abs(probs[top_5_idx[0]] - probs[top_5_idx[1]]) * 100:.2f}%")
    
    # 8. Diagnostic
    print(f"\n8️⃣ Diagnostic :")
    max_conf = predictions[0].max()
    if max_conf > 0.99:
        print("   ⚠️  ALERTE : Confiance extrêmement élevée (>99%)")
        print("   Cela peut indiquer :")
        print("   - Image très claire et typique de la maladie")
        print("   - Ou surapprentissage (overfitting)")
    elif max_conf > 0.95:
        print("   ✅ Confiance très élevée (95-99%)")
    elif max_conf > 0.80:
        print("   ✅ Bonne confiance (80-95%)")
    else:
        print("   ⚠️  Confiance faible (<80%)")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python test_prediction_debug.py <chemin_image>")
        print("\nExemple:")
        print("  python test_prediction_debug.py media/leaf.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    analyze_prediction(image_path)
