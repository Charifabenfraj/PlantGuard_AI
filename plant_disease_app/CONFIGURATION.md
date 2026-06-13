# Configuration du Projet Django - Plant Disease Detection

## 📁 Structure du Projet

```
D:\4BI8\Projects\plants_disease_detection\
├── .venv\                                    # Environnement virtuel Python
│
├── PlantVillage\                             # Dataset original
│
├── dataset_preprocessed\                     # Dataset préparé (train/val/test)
│   ├── train\
│   ├── val\
│   └── test\
│
├── plant_disease_project.ipynb               # Notebook d'entraînement des modèles
│
├── best_model_3_transfer_learning.h5         # Meilleur modèle (à déplacer si besoin)
├── model_2_deep_cnn.h5                      # Modèles entraînés
│
└── plant_disease_app\                        # 🎯 APPLICATION DJANGO
    ├── manage.py                             # Script principal Django
    │
    ├── plant_disease_app\                    # Configuration Django
    │   ├── settings.py                       # ✅ CONFIGURÉ
    │   ├── urls.py
    │   ├── wsgi.py
    │   └── asgi.py
    │
    ├── templates\                            # 📄 Templates HTML
    ├── static\                               # 🎨 CSS, JS, images statiques
    ├── media\                                # 📤 Uploads utilisateurs
    ├── models\                               # 🤖 Modèles ML (à créer si besoin)
    │
    ├── .env.example                          # Variables d'environnement (exemple)
    └── db.sqlite3                            # Base de données SQLite
```

## ✅ Corrections Effectuées dans settings.py

### 1. **Chemins Corrigés**
```python
BASE_DIR = Path(__file__).resolve().parent.parent
# Pointe vers: D:\4BI8\Projects\plants_disease_detection\plant_disease_app\

PROJECT_ROOT = BASE_DIR.parent  
# Pointe vers: D:\4BI8\Projects\plants_disease_detection\
```

### 2. **Configuration des Fichiers Statiques**
```python
STATIC_URL = '/static/'                    # URL d'accès aux fichiers statiques
STATIC_ROOT = BASE_DIR / 'staticfiles'     # Collectés par collectstatic (production)
STATICFILES_DIRS = [BASE_DIR / 'static']   # Dossier static en développement
```

### 3. **Configuration des Fichiers Média (Uploads)**
```python
MEDIA_URL = '/media/'                      # URL d'accès aux uploads
MEDIA_ROOT = BASE_DIR / 'media'            # Dossier de stockage des uploads
```

### 4. **Configuration des Templates**
```python
TEMPLATES = [
    {
        'DIRS': [BASE_DIR / 'templates'],  # Dossier templates
        ...
    }
]
```

### 5. **Configuration Machine Learning**
```python
ML_MODELS_DIR = PROJECT_ROOT / 'models'
ML_BEST_MODEL = PROJECT_ROOT / 'best_model_3_transfer_learning.h5'
DATASET_DIR = PROJECT_ROOT / 'PlantVillage'
PREPROCESSED_DATASET_DIR = PROJECT_ROOT / 'dataset_preprocessed'

IMG_SIZE = 256
NUM_CLASSES = 15
CLASS_NAMES = [...]  # 15 classes de maladies
```

## 🚀 Prochaines Étapes

### 1. Installer les dépendances (si ce n'est pas fait)
```bash
cd D:\4BI8\Projects\plants_disease_detection
.venv\Scripts\activate
pip install django djongo tensorflow pillow
```

### 2. Créer une application Django pour la détection
```bash
cd plant_disease_app
python manage.py startapp detector
```

### 3. Ajouter 'detector' dans INSTALLED_APPS (settings.py)
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    ...
    'detector',  # Ajouter ceci
]
```

### 4. Créer les migrations et la base de données
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Créer un superutilisateur
```bash
python manage.py createsuperuser
```

### 6. Lancer le serveur
```bash
python manage.py runserver
```

Accéder à: http://127.0.0.1:8000/

## 📝 Configuration MongoDB (Optionnel)

Si vous souhaitez utiliser MongoDB au lieu de SQLite:

1. **Créer un fichier .env** (copier .env.example)
```bash
copy .env.example .env
```

2. **Installer python-decouple**
```bash
pip install python-decouple
```

3. **Modifier settings.py** pour utiliser les variables d'environnement:
```python
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
```

## 🔐 Sécurité

⚠️ **IMPORTANT:**
- Le SECRET_KEY actuel est pour le développement
- En production, générez une nouvelle clé et stockez-la dans .env
- Ajoutez `.env` dans .gitignore pour ne pas exposer vos secrets
- Changez `DEBUG = False` en production
- Configurez `ALLOWED_HOSTS` avec vos domaines

## 📦 Dépendances Principales

```
Django==6.0.2
djongo (si MongoDB)
tensorflow==2.x
pillow
numpy
opencv-python
```

## 🎯 Structure Recommandée pour l'App 'detector'

```
detector/
├── views.py           # Vues pour upload et prédiction
├── models.py          # Modèles Django (historique des prédictions)
├── forms.py           # Formulaires (upload d'image)
├── urls.py            # Routes de l'app
├── utils.py           # Fonctions ML (load_model, predict)
└── templates/
    └── detector/
        ├── index.html
        ├── predict.html
        └── result.html
```

## 📞 Support

Pour toute question sur la configuration, référez-vous à:
- Documentation Django: https://docs.djangoproject.com/
- Documentation TensorFlow: https://www.tensorflow.org/tutorials
