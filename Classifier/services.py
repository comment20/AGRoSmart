import os
import requests
import pandas as pd
import numpy as np
from django.conf import settings
import re
import unicodedata

class SoilClassificationService:
    API_URL = "https://tchoupe-soilclassifier-svm.hf.space" # API SVM sur Hugging Face

    @classmethod
    def predict_soil(cls, image_path):
        """Envoie l'image à l'API FastAPI SVM sur Hugging Face et récupère la prédiction."""
        try:
            if not os.path.exists(image_path):
                print(f"ERREUR : Le fichier image n'existe pas : {image_path}")
                return None, None

            with open(image_path, 'rb') as img:
                files = {'file': (os.path.basename(image_path), img, 'image/jpeg')}
                print(f"Tentative de connexion à l'API SVM sur {cls.API_URL}/predict...")
                response = requests.post(f"{cls.API_URL}/predict", files=files, timeout=15)
                
            if response.status_code == 200:
                data = response.json()
                print(f"Succès API SVM : {data}")
                # Retourne (type_de_sol, confiance)
                return data.get('soil_type', 'Inconnu'), data.get('confidence', 'N/A')
            else:
                print(f"Erreur API SVM (Status {response.status_code}): {response.text}")
        except requests.exceptions.ConnectionError:
            print(f"ERREUR : Impossible de se connecter à l'API SVM sur {cls.API_URL}. L'API est-elle lancée ?")
        except requests.exceptions.Timeout:
            print(f"ERREUR : Timeout lors de l'appel à l'API SVM sur {cls.API_URL}.")
        except Exception as e:
            print(f"Erreur inattendue lors de la connexion API SVM : {e}")
        return None, None

class CropRecommendationService:
    API_URL = "https://tchoupe-crop-recommendation-api.hf.space" # API Culture sur Hugging Face

    @classmethod
    def predict_crop(cls, data):
        """Envoie les données physico-chimiques à l'API FastAPI Culture sur Hugging Face."""
        try:
            payload = {
                'nitrogen': data['nitrogen'],
                'phosphorus': data['phosphorus'],
                'potassium': data['potassium'],
                'temperature': data['temperature'],
                'humidity': data['humidity'],
                'ph': data['ph'],
                'rainfall': data['rainfall']
            }
            response = requests.post(f"{cls.API_URL}/predict", json=payload, timeout=10)
            if response.status_code == 200:
                return response.json().get('predicted_crop', 'Erreur')
        except Exception as e:
            print(f"Erreur connexion API Culture : {e}")
        return None

class PricePredictionService:
    MODEL_DIR = os.path.join(settings.BASE_DIR, 'model_prevision')
    API_URL = "https://tchoupe-api-prevision.hf.space"
    
    @staticmethod
    def normalize_string(s):
        if not s: return ""
        s = unicodedata.normalize('NFD', s)
        s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
        s = s.lower()
        return re.sub(r'[^a-z]', '', s)

    @classmethod
    def get_available_models(cls):
        """Récupère les modèles via l'API."""
        try:
            response = requests.get(f"{cls.API_URL}/models", timeout=5)
            if response.status_code == 200:
                filenames = response.json().get('available_models', [])
                models = []
                for filename in filenames:
                    parts = filename.replace('.pkl', '').split('_')
                    if len(parts) >= 4:
                        models.append({'product': parts[2], 'dept': parts[3], 'file': filename})
                return models
        except Exception as e:
            print(f"Erreur modèles API : {e}")
        return []

    @classmethod
    def get_predictions(cls, product, department, months=6):
        """Appelle l'API et extrait les prix pour le graphique."""
        try:
            params = {
                'product': product,
                'department': department,
                'months': months
            }
            response = requests.get(f"{cls.API_URL}/predict", params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Nouvelle structure : data['forecast'] est une liste de {"date":..., "price":...}
                forecast_list = data.get('forecast', [])
                # On extrait juste les prix pour le graphique Django
                return [item['price'] for item in forecast_list]
            else:
                print(f"API Error: {response.status_code}")
        except Exception as e:
            print(f"Erreur connexion API ML : {e}")
        return None

    @classmethod
    def get_historical_data(cls, product, region=None, department=None):
        # On utilise le CSV local qui est toujours dans Django
        csv_path = os.path.join(cls.MODEL_DIR, 'global_file.csv')
        if not os.path.exists(csv_path): return None
        df = pd.read_csv(csv_path)
        mask = (df['Product'] == product)
        if department: mask &= (df['Department'] == department)
        elif region: mask &= (df['Region'] == region)
        filtered_df = df[mask].sort_values('date')
        if filtered_df.empty: return None
        return {
            'dates': filtered_df['date'].tolist(),
            'prices': filtered_df['price_per_kg'].tolist()
        }
