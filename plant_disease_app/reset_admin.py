"""
Script pour créer ou réinitialiser le superutilisateur Django
Exécutez ce script avec: python reset_admin.py
"""
import os
import django

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plant_disease_app.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def reset_admin():
    """Créer ou réinitialiser le compte admin"""
    username = 'admin'
    email = 'admin@plantdisease.com'
    password = 'Admin@2024'
    
    print("=" * 60)
    print("🔐 Réinitialisation du compte administrateur")
    print("=" * 60)
    
    # Vérifier si l'utilisateur existe
    if User.objects.filter(username=username).exists():
        print(f"\n⚠️  L'utilisateur '{username}' existe déjà.")
        print("🔄 Mise à jour du mot de passe...")
        
        user = User.objects.get(username=username)
        user.set_password(password)
        user.email = email
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()
        
        print("✅ Mot de passe mis à jour avec succès!")
    else:
        print(f"\n📝 Création d'un nouveau superutilisateur...")
        
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        print("✅ Superutilisateur créé avec succès!")
    
    print("\n" + "=" * 60)
    print("📋 INFORMATIONS DE CONNEXION")
    print("=" * 60)
    print(f"🌐 URL Admin: http://127.0.0.1:8000/admin/")
    print(f"👤 Username: {username}")
    print(f"🔑 Password: {password}")
    print("=" * 60)
    print("\n⚠️  IMPORTANT: Changez ce mot de passe en production!")
    print("=" * 60)

if __name__ == '__main__':
    try:
        reset_admin()
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        print("Assurez-vous d'être dans le bon répertoire (plant_disease_app/)")
