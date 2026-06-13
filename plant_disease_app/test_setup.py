"""
Script de test rapide pour vérifier que tout fonctionne
Exécutez avec: python test_setup.py
"""
import os
import sys

def check_setup():
    print("=" * 70)
    print("🔍 VÉRIFICATION DE LA CONFIGURATION")
    print("=" * 70)
    
    checks = []
    
    # 1. TensorFlow
    print("\n1️⃣  Vérification de TensorFlow...")
    try:
        import tensorflow as tf
        print(f"   ✅ TensorFlow {tf.__version__} installé")
        checks.append(True)
    except ImportError:
        print("   ❌ TensorFlow non installé")
        print("   📝 Installez avec: pip install tensorflow")
        checks.append(False)
    
    # 2. Dépendances
    print("\n2️⃣  Vérification des dépendances...")
    deps = ['PIL', 'numpy', 'django']
    all_deps_ok = True
    for dep in deps:
        try:
            __import__(dep if dep != 'PIL' else 'PIL')
            print(f"   ✅ {dep} installé")
        except ImportError:
            print(f"   ❌ {dep} non installé")
            all_deps_ok = False
    checks.append(all_deps_ok)
    
    # 3. Modèle ML
    print("\n3️⃣  Vérification du modèle ML...")
    model_path = os.path.join('..', 'model_2_deep_cnn.h5')
    if os.path.exists(model_path):
        size_mb = os.path.getsize(model_path) / (1024 * 1024)
        print(f"   ✅ Modèle trouvé: {model_path} ({size_mb:.1f} MB)")
        checks.append(True)
    else:
        print(f"   ❌ Modèle non trouvé: {model_path}")
        checks.append(False)
    
    # 4. Structure Django
    print("\n4️⃣  Vérification de la structure Django...")
    required_dirs = ['templates/detector', 'static', 'media', 'detector']
    all_dirs_ok = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"   ✅ {dir_path}/")
        else:
            print(f"   ❌ {dir_path}/ manquant")
            all_dirs_ok = False
    checks.append(all_dirs_ok)
    
    # 5. Fichiers clés
    print("\n5️⃣  Vérification des fichiers clés...")
    key_files = [
        'detector/ml_utils.py',
        'detector/views.py',
        'detector/urls.py',
        'templates/detector/home.html',
        'templates/detector/result.html',
        'plant_disease_app/settings.py'
    ]
    all_files_ok = True
    for file_path in key_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} manquant")
            all_files_ok = False
    checks.append(all_files_ok)
    
    # Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ")
    print("=" * 70)
    
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print(f"✅ Tous les tests réussis! ({passed}/{total})")
        print("\n🚀 Vous pouvez démarrer l'application:")
        print("   python manage.py runserver")
        print("\n🌐 Accédez à: http://127.0.0.1:8000/")
        return True
    else:
        print(f"⚠️  {passed}/{total} tests réussis")
        print("\n❌ Veuillez corriger les problèmes ci-dessus avant de continuer.")
        return False

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        success = check_setup()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        sys.exit(1)
