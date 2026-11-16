# 🌿 Plant Disease Detection

A deep learning web application built with **Django and TensorFlow/Keras** to detect plant diseases from leaf images using image classification.

## 🚀 Key Features

- **Transfer Learning (MobileNetV2)** as the default model, achieving **94.47% accuracy**.
- Multi-model management with 4 trained models.
- Image upload and automatic disease prediction.
- Top 3 prediction results.
- Side-by-side model comparison.
- Model performance statistics with interactive charts.
- Prediction caching and results export (JSON, Pickle, TXT).

## 🧠 Models

| Model | Accuracy |
|---|---:|
| Transfer Learning (MobileNetV2) | **94.47%** |
| Transfer Learning V3 | **94.47%** |
| Simple CNN | 91.57% |
| Deep CNN | 4.86% |

## 🛠️ Technologies

- Python
- Django
- TensorFlow / Keras
- MobileNetV2
- HTML, CSS, JavaScript
- Chart.js
- NumPy

## ▶️ Run Locally

```bash
cd plant_disease_app
pip install -r requirements.txt
python manage.py runserver
```

Open: http://localhost:8000/

## 📊 Main Pages

- `/` – Plant disease prediction
- `/models/` – Model management
- `/models/compare/` – Model comparison
- `/models/stats/` – Performance statistics

## 📁 Documentation

See `GUIDE_INTEGRATION_MODELE.md` for detailed integration instructions and `test_integration.py` for automatic testing.

---

**Project Status:** Completed and tested  
**Best Model:** Transfer Learning (MobileNetV2)  
**Accuracy:** 94.47%
