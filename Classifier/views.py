import requests
import csv
from datetime import datetime
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template
from io import BytesIO
from xhtml2pdf import pisa
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomAuthenticationForm, SoilImageForm, SoilCharacteristicsForm, SignUpForm
from django.conf import settings
import os
import json
from collections import Counter
from .models import Prediction, CropPrediction
import numpy as np
import pickle

from .services import PricePredictionService, SoilClassificationService, CropRecommendationService
import pandas as pd

@login_required
def price_dashboard_view(request):
    # Charger les options pour les filtres depuis le CSV
    csv_path = os.path.join(settings.BASE_DIR, 'model_prevision', 'global_file.csv')
    df = pd.read_csv(csv_path)
    
    products = sorted(df['Product'].unique())
    regions = sorted(df['Region'].unique())
    departments = sorted(df['Department'].unique())
    
    # Récupérer les modèles réellement disponibles
    available_models = PricePredictionService.get_available_models()
    
    # Créer le mapping Région -> Départements pour le filtrage dynamique
    region_dept_mapping = df.groupby('Region')['Department'].unique().apply(list).to_dict()

    # Gérer la requête de prédiction (AJAX)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        product = request.GET.get('product')
        region = request.GET.get('region')
        department = request.GET.get('department')
        months = int(request.GET.get('months', 6))

        try:
            # Récupérer les données historiques
            historical = PricePredictionService.get_historical_data(product, region, department)
            
            if not historical:
                return JsonResponse({
                    'status': 'no_data',
                    'message': f"Le produit '{product}' n'est pas représenté dans le département '{department}'."
                })
            
            # Récupérer les données pour la carte (tous les marchés pour ce produit)
            # On prend la date la plus récente disponible dans le CSV pour ce produit
            latest_date = df[df['Product'] == product]['date'].max()
            map_data = df[(df['Product'] == product) & (df['date'] == latest_date)][
                ['market', 'latitude', 'longitude', 'price_per_kg', 'Department']
            ].dropna().to_dict(orient='records')
            
            # Récupérer les prévisions
            predictions = PricePredictionService.get_predictions(product, department, months)
            
            forecast_data = None
            if predictions:
                last_date = pd.to_datetime(historical['dates'][-1])
                future_dates = [(last_date + pd.DateOffset(months=i+1)).strftime('%Y-%m-%d') for i in range(months)]
                forecast_data = {
                    'dates': future_dates,
                    'prices': predictions
                }

            return JsonResponse({
                'status': 'success',
                'historical': historical,
                'forecast': forecast_data,
                'map_points': map_data
            })
        except Exception as e:
            print(f"--- ERREUR : {str(e)} ---")
            return JsonResponse({'status': 'error', 'message': str(e)})

    context = {
        'products': products,
        'regions': regions,
        'departments': departments,
        'available_models_json': json.dumps(available_models),
        'region_dept_mapping_json': json.dumps(region_dept_mapping)
    }
    return render(request, "price_dashboard.html", context)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('selection') # Redirige vers le hub

    if request.method == 'POST':
        login_form = CustomAuthenticationForm(request, data=request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('selection') # Redirige vers le hub
        signup_form = SignUpForm()
    else:
        login_form = CustomAuthenticationForm()
        signup_form = SignUpForm()
    
    login_form.fields['username'].widget.attrs.update({'placeholder': 'Nom d\'utilisateur'})
    login_form.fields['password'].widget.attrs.update({'placeholder': 'Mot de passe'})

    return render(request, 'connexion.html', {
        'login_form': login_form,
        'signup_form': signup_form
    })

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('selection') # Redirige vers le hub

    if request.method == 'POST':
        signup_form = SignUpForm(request.POST)
        if signup_form.is_valid():
            user = signup_form.save()
            login(request, user)
            return redirect('selection') # Redirige vers le hub
        login_form = CustomAuthenticationForm()
    else:
        login_form = CustomAuthenticationForm()
        signup_form = SignUpForm()

    login_form.fields['username'].widget.attrs.update({'placeholder': 'Nom d\'utilisateur'})
    login_form.fields['password'].widget.attrs.update({'placeholder': 'Mot de passe'})

    return render(request, 'connexion.html', {
        'login_form': login_form,
        'signup_form': signup_form
    })

def logout_view(request):
    logout(request)
    return redirect('connexion')

@login_required
def result(request):
    soil_type = request.session.get("soil_type")
    confidence = request.session.get("confidence")
    uploaded_image = request.session.get("uploaded_image")
    if not soil_type:
        return redirect("home")
    context = {
        'predicted_class': soil_type,
        'probability_percentage': confidence,
        'image_url': uploaded_image
    }
    return render(request, "result.html", context)

@user_passes_test(lambda u: u.is_staff)
def prediction_history(request):
    history = Prediction.objects.all()
    return render(request, 'historique.html', {'history': history})

@login_required
def my_history(request):
    history = Prediction.objects.filter(user=request.user)
    return render(request, 'historique.html', {'history': history})

@login_required
def export_history_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="prediction_history.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date et Heure', 'Nom de l\'image', 'Type de sol prédit', 'Confiance', 'Latitude', 'Longitude', 'Nom de la Localisation'])

    predictions = Prediction.objects.filter(user=request.user).order_by('timestamp')
    for prediction in predictions:
        writer.writerow([
            prediction.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            prediction.image_name,
            prediction.soil_type,
            f'{prediction.confidence:.2f}%',
            prediction.latitude if prediction.latitude is not None else '',
            prediction.longitude if prediction.longitude is not None else '',
            prediction.location_name if prediction.location_name is not None else ''
        ])
    return response

@login_required
def export_history_pdf(request):
    predictions = Prediction.objects.filter(user=request.user).order_by('timestamp')
    
    context = {
        'predictions': predictions,
    }
    
    template_path = 'history_pdf_template.html'
    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="prediction_history.pdf"'
    
    pisa_status = pisa.CreatePDF(
        html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


@user_passes_test(lambda u: u.is_staff)
def dashboard(request):
    # Données globales pour les types de sol
    soil_history_data = Prediction.objects.all()
    soil_types = [item.soil_type for item in soil_history_data]
    soil_type_counts = Counter(soil_types)

    # Données globales pour les types de culture
    crop_history_data = CropPrediction.objects.all()
    crop_types = [item.predicted_crop for item in crop_history_data]
    crop_type_counts = Counter(crop_types)

    # --- NOUVEAU : Répartition par localité ---
    # Récupérer toutes les localités uniques
    localities = list(Prediction.objects.values_list('location_name', flat=True).distinct()) + \
                 list(CropPrediction.objects.values_list('location_name', flat=True).distinct())
    # Nettoyer et filtrer les localités (enlever les None et doublons)
    localities = sorted(list(set([l for l in localities if l])))

    # Préparer les données par localité pour le JS
    locality_data = {}
    for loc in localities:
        # Sols dans cette localité
        loc_soils = Prediction.objects.filter(location_name=loc)
        loc_soil_counts = Counter([s.soil_type for s in loc_soils])
        
        # Cultures dans cette localité
        loc_crops = CropPrediction.objects.filter(location_name=loc)
        loc_crop_counts = Counter([c.predicted_crop for c in loc_crops])
        
        locality_data[loc] = {
            'soils': {
                'labels': list(loc_soil_counts.keys()),
                'data': list(loc_soil_counts.values())
            },
            'crops': {
                'labels': list(loc_crop_counts.keys()),
                'data': list(loc_crop_counts.values())
            }
        }

    context = {
        'soil_type_labels': list(soil_type_counts.keys()),
        'soil_type_data': list(soil_type_counts.values()),
        'crop_type_labels': list(crop_type_counts.keys()),
        'crop_type_data': list(crop_type_counts.values()),
        'localities': localities,
        'locality_data_json': json.dumps(locality_data)
    }
    return render(request, 'dashboard.html', context)

@user_passes_test(lambda u: u.is_staff)
def dashboard_data(request):
    history_data = Prediction.objects.all()
    soil_types = [item.soil_type for item in history_data]
    soil_type_counts = Counter(soil_types)

    data = {
        'labels': list(soil_type_counts.keys()),
        'data': list(soil_type_counts.values()),
    }
    return JsonResponse(data)

@user_passes_test(lambda u: u.is_staff)
def crop_dashboard_data(request):
    history_data = CropPrediction.objects.all()
    crop_types = [item.predicted_crop for item in history_data]
    crop_type_counts = Counter(crop_types)

    data = {
        'labels': list(crop_type_counts.keys()),
        'data': list(crop_type_counts.values()),
    }
    return JsonResponse(data)

@login_required
def upload_image_view(request):
    if request.method == "POST":
        form = SoilImageForm(request.POST, request.FILES)
        if form.is_valid():
            img_file = request.FILES["image"]
            
            # S'assurer que le dossier media existe (nécessaire sur Render car ignoré par Git)
            if not os.path.exists(settings.MEDIA_ROOT):
                os.makedirs(settings.MEDIA_ROOT)
                
            img_path = os.path.join(settings.MEDIA_ROOT, img_file.name)
            with open(img_path, "wb+") as f:
                for chunk in img_file.chunks():
                    f.write(chunk)
            
            try:
                soil_type, confidence = SoilClassificationService.predict_soil(img_path)
                print(f"DEBUG: Type de sol brut reçu de l'API: '{soil_type}'")

                if not soil_type:
                     raise Exception("L'API de classification n'a pas renvoyé de résultat.")

                # Dictionnaire de traduction complet et robuste
                soil_translation = {
                    'black': 'Sol Noir', 'black soil': 'Sol Noir',
                    'alluvial': 'Sol Alluvial', 'alluvial soil': 'Sol Alluvial',
                    'clay': 'Sol Argileux', 'clay soil': 'Sol Argileux',
                    'sandy clay': 'Sol Sablo-Argileux', 'sandy clay soil': 'Sol Sablo-Argileux',
                    'sandy loam': 'Sol Sablo-Limoneux', 'sandy loam soil': 'Sol Sablo-Limoneux',
                    'red': 'Sol Rouge', 'red soil': 'Sol Rouge',
                    'sandy': 'Sol Sableux', 'sandy soil': 'Sol Sableux', 'sand': 'Sol Sableux', 'pasir': 'Sol Sableux', 'sable': 'Sol Sableux',
                    'mountain': 'Sol de Montagne', 'mountain soil': 'Sol de Montagne',
                    'arid': 'Sol Aride', 'arid soil': 'Sol Aride',
                    'yellow': 'Sol Jaune', 'yellow soil': 'Sol Jaune',
                    'drought': 'Sol Aride', 'drought soil': 'Sol Aride',
                    'loamy': 'Sol Limoneux', 'loamy soil': 'Sol Limoneux', 'limoneux': 'Sol Limoneux', 'silt': 'Sol Limoneux',
                    'coal': 'Sol Charbonneux', 'coal soil': 'Sol Charbonneux', 'charbon': 'Sol Charbonneux',
                    'cinder': 'Sol de Cendres', 'cinder soil': 'Sol de Cendres', 'cendres': 'Sol de Cendres',
                    'chalky': 'Sol Calcaire', 'chalky soil': 'Sol Calcaire', 'calcaire': 'Sol Calcaire',
                    'andosol': 'Andosol', 'andosol soil': 'Andosol',
                    'humus': 'Humus', 'humus soil': 'Humus',
                    'laterite': 'Latérite', 'laterite soil': 'Latérite',
                    'mary': 'Sol Marneux', 'marly': 'Sol Marneux', 'marly soil': 'Sol Marneux',
                    'normal': 'Sol Normal', 'normal soil': 'Sol Normal',
                    'peat': 'Sol Tourbeux', 'peat soil': 'Tourbe', 'tourbe': 'Tourbe',
                    'entisol': 'Entisol', 'inceptisol': 'Inceptisol', 'mollisol': 'Mollisol',
                    'glacier': 'Glacier', 'rock': 'Roche/Cailloux', 'stony': 'Sol Pierreux',
                    'soil insects': 'Insectes du Sol'
                }
                
                # Nettoyage ultra-robuste : minuscule, remplace _ par espace, enlève les doubles espaces
                clean_soil = soil_type.lower().replace('_', ' ').strip()
                # On enlève aussi le mot "soil" à la fin s'il existe pour mieux matcher
                search_key = clean_soil.replace(' soil', '').strip()
                
                # Tentative de traduction avec plusieurs niveaux de sécurité
                soil_type_fr = soil_translation.get(search_key, 
                               soil_translation.get(clean_soil, 
                               soil_translation.get(soil_type.lower(), soil_type)))
                
                print(f"DEBUG: Brut='{soil_type}' | Clean='{clean_soil}' | Key='{search_key}' | Result='{soil_type_fr}'")

                # Gérer le cas où l'image n'est pas un sol
                if soil_type.lower() in ['image non sol', 'image_non_sol']:
                    form = SoilImageForm()
                    error_message = "Cette image n'est pas une image de sol, entrez une nouvelle image."
                    return render(request, "upload_image.html", {"form": form, "error_message": error_message})

                # Si c'est un sol, sauvegarder la prédiction (on garde la version FR pour l'affichage)
                lat = request.POST.get('latitude')
                lon = request.POST.get('longitude')
                
                Prediction.objects.create(
                    user=request.user,
                    image_name=img_file.name,
                    soil_type=soil_type_fr,
                    confidence=confidence,
                    latitude=float(lat) if lat and lat.strip() else None,
                    longitude=float(lon) if lon and lon.strip() else None,
                    location_name=request.POST.get('location_name') or None
                )
                
                # Préparer la page de résultat
                img_url = settings.MEDIA_URL + img_file.name
                request.session["soil_type"] = soil_type_fr
                request.session["confidence"] = confidence
                request.session["uploaded_image"] = img_url
                return redirect("result")

            except Exception as e:
                print(f"Erreur lors de la prédiction locale du sol: {e}")
                form = SoilImageForm()
                error_message = "Une erreur est survenue lors de l'analyse de l'image."
                return render(request, "upload_image.html", {"form": form, "error_message": error_message})
    else:
        form = SoilImageForm()
    return render(request, "upload_image.html", {"form": form})

@login_required
def delete_prediction(request, prediction_id):
    prediction = get_object_or_404(Prediction, id=prediction_id)
    # Allow staff to delete any prediction, otherwise check ownership
    if not request.user.is_staff and prediction.user != request.user:
        return HttpResponseForbidden("You are not allowed to delete this prediction.")
    if request.method == 'POST':
        prediction.delete()
        # Redirect to the appropriate history page based on user type
        if request.user.is_staff:
            return redirect('historique') # Redirect to admin history page
        else:
            return redirect('my_history') # Redirect to user's history page
    # If it's a GET request, just redirect to the appropriate history page
    if request.user.is_staff:
        return redirect('historique')
    else:
        return redirect('my_history')

def landing_page_view(request):
    return render(request, "landing.html")

@login_required
def analyze_characteristics_view(request):
    if request.method == 'POST':
        form = SoilCharacteristicsForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            
            # Créer le payload JSON pour l'API
            api_payload = {
                'temperature': data['temperature'],
                'ph': data['ph'],
                'humidity': data['humidity'],
                'nitrogen': data['nitrogen'],
                'potassium': data['potassium'],
                'phosphorus': data['phosphorus'],
                'rainfall': data['rainfall']
            }

            # Appeler l'API de prédiction de culture via le Service
            try:
                predicted_crop = CropRecommendationService.predict_crop(data)
                
                if not predicted_crop:
                    raise Exception("L'API de culture n'a pas renvoyé de résultat.")

                # Sauvegarder la prédiction de culture dans la base de données
                lat = request.POST.get('latitude')
                lon = request.POST.get('longitude')
                
                CropPrediction.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    temperature=data['temperature'],
                    ph=data['ph'],
                    humidity=data['humidity'],
                    nitrogen=data['nitrogen'],
                    potassium=data['potassium'],
                    phosphorus=data['phosphorus'],
                    rainfall=data['rainfall'],
                    predicted_crop=predicted_crop,
                    latitude=float(lat) if lat and lat.strip() else None,
                    longitude=float(lon) if lon and lon.strip() else None,
                    location_name=request.POST.get('location_name') or None
                )

                # Stocker le résultat dans la session et rediriger
                request.session['predicted_crop'] = predicted_crop
                return redirect('crop_result')

            except requests.exceptions.RequestException as e:
                # Gérer les erreurs réseau ou HTTP
                print(f"--- Erreur lors de l'appel à l'API de culture : {e} ---")
                # On pourrait rediriger vers une page d'erreur ou ré-afficher le formulaire avec un message
                pass

    else:
        form = SoilCharacteristicsForm()

    return render(request, 'analyze_characteristics.html', {'form': form})

@login_required
def crop_result_view(request):
    predicted_crop_en = request.session.get('predicted_crop', 'N/A')

    translation_dict = {
        'apple': 'Pomme', 'banana': 'Banane', 'blackgram': 'Haricot Urd', 'chickpea': 'Pois Chiche',
        'coconut': 'Noix de Coco', 'coffee': 'Café', 'cotton': 'Coton', 'grapes': 'Raisin',
        'jute': 'Jute', 'kidneybeans': 'Haricot Rouge', 'lentil': 'Lentille', 'maize': 'Maïs',
        'mango': 'Mangue', 'mothbeans': 'Haricot Mat', 'mungbean': 'Haricot Mungo',
        'muskmelon': 'Melon Cantaloup', 'orange': 'Orange', 'papaya': 'Papaye',
        'pigeonpeas': 'Pois d\'Angole', 'pomegranate': 'Grenade', 'rice': 'Riz',
        'watermelon': 'Pastèque'
    }

    # Traduire le nom de la culture, avec une valeur par défaut si non trouvé
    predicted_crop_fr = translation_dict.get(predicted_crop_en, predicted_crop_en)

    context = {
        'predicted_crop': predicted_crop_fr
    }
    return render(request, 'crop_result.html', context)

@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def selection_view(request):
    return render(request, 'selection.html')