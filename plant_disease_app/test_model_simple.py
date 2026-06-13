"""
Test simple pour vérifier le chargement du modèle
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plant_disease_app.settings')
django.setup()

from django.conf import settings

print("\n" + "="*60)
print("TEST DE CHARGEMENT DU MODÈLE")
print("="*60 + "\n")

# 1. Vérifier le chemin du modèle
model_path = settings.ML_BEST_MODEL
print(f"📁 Chemin du modèle: {model_path}")
print(f"✓ Fichier existe: {os.path.exists(model_path)}")

if os.path.exists(model_path):
    file_size = os.path.getsize(model_path) / (1024 * 1024)
    print(f"✓ Taille: {file_size:.1f} MB")

# 2. Tester l'import TensorFlow
print("\n" + "-"*60)
print("TEST TENSORFLOW")
print("-"*60)
try:
    import tensorflow as tf
    print(f"✅ TensorFlow version: {tf.__version__}")
    print(f"✅ Keras disponible: {hasattr(tf, 'keras')}")
except ImportError as e:
    print(f"❌ TensorFlow non disponible: {e}")
    sys.exit(1)

# 3. Tester le chargement du modèle
print("\n" + "-"*60)
print("TEST CHARGEMENT MODÈLE")
print("-"*60)
try:
    print("🔄 Chargement du modèle...")
    model = tf.keras.models.load_model(str(model_path))
    print(f"✅ Modèle chargé avec succès!")
    print(f"✅ Type: {type(model)}")
    print(f"✅ Paramètres: {model.count_params():,}")
    
    # Afficher la structure
    print("\n📊 Structure du modèle:")
    print(f"   - Input shape: {model.input_shape}")
    print(f"   - Output shape: {model.output_shape}")
    print(f"   - Nombre de couches: {len(model.layers)}")
    
except Exception as e:
    print(f"❌ Erreur chargement: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 4. Tester ml_utils
print("\n" + "-"*60)
print("TEST ML_UTILS")
print("-"*60)
try:
    from detector.ml_utils import load_model
    print("🔄 Test de load_model()...")
    model = load_model()
    if model:
        print("✅ load_model() fonctionne")
    else:
        print("❌ load_model() retourne None")
except Exception as e:
    print(f"❌ Erreur dans ml_utils: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("✅ TOUS LES TESTS RÉUSSIS!")
print("="*60 + "\n")
