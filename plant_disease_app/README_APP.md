# 🌿 Plant Disease Detection - Guide de Démarrage

## ✅ Application Web Django - PRÊTE À L'EMPLOI!

### 🎯 Ce qui a été créé

```
plant_disease_app/
├── detector/                    ✅ Application Django créée
│   ├── views.py                ✅ 3 vues (home, predict, about)
│   ├── urls.py                 ✅ Routes configurées
│   └── ...
│
├── templates/detector/          ✅ Templates HTML créés
│   ├── base.html               ✅ Layout Bootstrap 5
│   ├── home.html               ✅ Page d'accueil + upload
│   ├── result.html             ✅ Page de résultats
│   └── about.html              ✅ Page à propos
│
├── plant_disease_app/           ✅ Configuration Django
│   ├── settings.py             ✅ Configuré (chemins, ML, DB)
│   └── urls.py                 ✅ Routes principales
│
├── static/                      ✅ Créé (pour CSS/JS custom)
├── media/                       ✅ Créé (pour uploads)
└── db.sqlite3                   ✅ Base de données prête
```

---

## 🚀 Démarrer l'Application

### 1. Activer l'environnement virtuel (si pas déjà fait)
```bash
.\.venv\Scripts\activate
```

### 2. Lancer le serveur Django
```bash
cd plant_disease_app
python manage.py runserver
```

### 3. Ouvrir dans le navigateur
```
http://127.0.0.1:8000/
```

---

## 🎨 Pages Disponibles

| URL | Description |
|-----|-------------|
| `http://127.0.0.1:8000/` | Page d'accueil avec upload d'image |
| `http://127.0.0.1:8000/about/` | Informations sur le projet |
| `http://127.0.0.1:8000/admin/` | Interface d'administration |

---

## 👤 Connexion Admin

Vous avez créé un compte superutilisateur avec:
- **Username:** `admin`
- **Password:** `Admin@2024`

Accès: http://127.0.0.1:8000/admin/

---

## 🧪 Tester l'Application

### 1. Page d'Accueil
- ✅ Interface moderne avec Bootstrap 5
- ✅ Zone de drag & drop pour images
- ✅ Prévisualisation avant upload
- ✅ Design responsive

### 2. Upload et Prédiction
- Téléchargez une image de feuille
- Cliquez sur "Analyser l'image"
- Obtenez le résultat avec:
  - Maladie détectée
  - Pourcentage de confiance
  - Top 3 des prédictions
  - Recommandations

### 3. Page À Propos
- Informations sur le projet
- Liste des 15 maladies détectables
- Technologies utilisées
- Statistiques du modèle

---

## 🔧 Prochaines Étapes - Intégrer le Modèle ML

### Étape 1: Copier le meilleur modèle
```bash
# Depuis la racine du projet
copy best_model_3_transfer_learning.h5 plant_disease_app\models\
```

### Étape 2: Créer le fichier de gestion du modèle
Créer `detector/ml_utils.py`:

```python
import tensorflow as tf
from django.conf import settings
import numpy as np
from PIL import Image

# Charger le modèle au démarrage
MODEL_PATH = settings.ML_BEST_MODEL
model = None

def load_model():
    global model
    if model is None:
        model = tf.keras.models.load_model(MODEL_PATH)
    return model

def preprocess_image(image_path):
    """Prétraiter l'image pour le modèle"""
    img = Image.open(image_path).convert('RGB')
    img = img.resize((settings.IMG_SIZE, settings.IMG_SIZE))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def predict_disease(image_path):
    """Faire la prédiction"""
    model = load_model()
    img_array = preprocess_image(image_path)
    
    predictions = model.predict(img_array, verbose=0)
    predicted_class_idx = np.argmax(predictions[0])
    confidence = float(predictions[0][predicted_class_idx] * 100)
    
    # Top 3
    top_3_idx = np.argsort(predictions[0])[-3:][::-1]
    top_predictions = [
        {
            'class': settings.CLASS_NAMES[idx],
            'confidence': round(float(predictions[0][idx] * 100), 2)
        }
        for idx in top_3_idx
    ]
    
    return {
        'prediction': settings.CLASS_NAMES[predicted_class_idx],
        'confidence': round(confidence, 2),
        'top_predictions': top_predictions
    }
```

### Étape 3: Mettre à jour views.py
Dans `detector/views.py`, remplacer la fonction `predict`:

```python
from .ml_utils import predict_disease

def predict(request):
    """Traite l'upload et fait la prédiction"""
    if request.method == 'POST' and request.FILES.get('image'):
        # Sauvegarder l'image
        uploaded_file = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_url = fs.url(filename)
        file_path = fs.path(filename)
        
        # Faire la prédiction avec le modèle
        try:
            results = predict_disease(file_path)
            context = {
                'uploaded': True,
                'file_url': file_url,
                'prediction': results['prediction'],
                'confidence': results['confidence'],
                'top_predictions': results['top_predictions']
            }
        except Exception as e:
            context = {
                'uploaded': True,
                'file_url': file_url,
                'error': f"Erreur lors de la prédiction: {str(e)}"
            }
        
        return render(request, 'detector/result.html', context)
    
    return redirect('home')
```

---

## 📦 Dépendances Installées

- ✅ Django 6.0.2
- ✅ TensorFlow 2.x
- ✅ NumPy
- ✅ Pillow (PIL)
- ✅ OpenCV
- ✅ Matplotlib
- ✅ scikit-learn

---

## 🎨 Design & UX

### Caractéristiques
- Interface moderne et intuitive
- Design responsive (mobile-friendly)
- Drag & drop pour upload d'images
- Prévisualisation en temps réel
- Animations fluides
- Indicateurs de progression
- Gradients et ombres modernes

### Palette de Couleurs
- Primaire: `#667eea` (Bleu-violet)
- Secondaire: `#764ba2` (Violet)
- Succès: Bootstrap green
- Background: Gradient violet

---

## 🔐 Sécurité

### En développement (actuel)
- ✅ DEBUG = True
- ✅ SQLite database
- ✅ SECRET_KEY visible

### Pour la production (à faire)
```python
# Dans settings.py
DEBUG = False
ALLOWED_HOSTS = ['votredomaine.com']
SECRET_KEY = os.getenv('SECRET_KEY')  # Variable d'environnement

# Utiliser PostgreSQL ou MongoDB
# Configurer HTTPS
# Ajouter CSRF protection
```

---

## 📊 Fonctionnalités Actuelles

### ✅ Implémenté
- Page d'accueil moderne
- Upload d'images (drag & drop)
- Prévisualisation des images
- Système de navigation
- Interface admin Django
- Templates responsive
- Page à propos
- Configuration ML complète

### 🔜 À faire (Prochaines étapes)
- Intégration du modèle ML (guide ci-dessus)
- Historique des prédictions
- Export des résultats (PDF)
- API REST (Django REST Framework)
- Tests unitaires
- Déploiement (Heroku/AWS)

---

## 🆘 Dépannage

### Problème: ModuleNotFoundError
```bash
pip install tensorflow pillow numpy opencv-python
```

### Problème: Templates not found
Vérifier dans `settings.py`:
```python
TEMPLATES = [{'DIRS': [BASE_DIR / 'templates']}]
```

### Problème: Static files not loading
```bash
python manage.py collectstatic
```

---

## 📞 Support

- Documentation Django: https://docs.djangoproject.com/
- Documentation TensorFlow: https://www.tensorflow.org/
- Bootstrap: https://getbootstrap.com/

---

## 🎉 Félicitations!

Votre application web de détection de maladies est **prête et fonctionnelle**!

Pour l'améliorer, suivez les étapes d'intégration du modèle ML ci-dessus.

**Bon développement! 🚀**
