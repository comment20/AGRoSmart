import google.generativeai as genai
import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from Classifier.models import Prediction, CropPrediction
from .models import ChatMessage

# Configuration de Gemini avec le modèle stable
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

def get_gemini_response(user_message, is_first_message=False):
    """Appelle l'IA Gemini pour une réponse indépendante."""
    intro_instruction = ""
    if is_first_message:
        intro_instruction = "Présente-toi brièvement comme 'AGROsmart IA', créé par l'élève ingénieur TCHOUPE GERMAIN BOVAL."
    else:
        intro_instruction = "Ne mentionne plus ton créateur, réponds directement à la question."

    prompt = f"""
    Tu es 'AGROsmart IA', un assistant expert en agronomie et science des sols.
    {intro_instruction}
    
    CONSIGNES :
    1. Répondez de manière experte aux questions sur l'agriculture, les types de sols, les cultures et les techniques agricoles.
    2. Si l'utilisateur pose une question générale sur un type de sol (ex: 'Parle moi du sol argileux'), donne sa composition détaillée (azote, phosphore, potassium, structure) et les cultures adaptées.
    3. Présente tes réponses avec une mise en forme claire (utilise des listes à puces si nécessaire).
    4. Réponds de manière professionnelle, chaleureuse et en français.
    5. Reste strictement dans le domaine de l'agriculture.
    
    MESSAGE DE L'UTILISATEUR :
    "{user_message}"
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Désolé, je rencontre une petite difficulté technique : {str(e)}"

@csrf_exempt
@login_required
def send_message_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            if not user_message:
                return JsonResponse({'error': 'Message vide'}, status=400)

            # Vérifier s'il s'agit du premier message de la session
            message_count = ChatMessage.objects.filter(user=request.user).count()
            is_first_message = (message_count == 0)

            # Sauvegarder message utilisateur
            ChatMessage.objects.create(user=request.user, message=user_message, is_from_user=True)

            # Obtenir la réponse de l'IA
            bot_response = get_gemini_response(user_message, is_first_message)

            # Sauvegarder réponse bot
            ChatMessage.objects.create(user=request.user, message=bot_response, is_from_user=False)

            return JsonResponse({'message': bot_response})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def chat_history_api(request):
    messages = ChatMessage.objects.filter(user=request.user).order_by('timestamp')
    history = [{'id': m.id, 'message': m.message, 'is_from_user': m.is_from_user} for m in messages]
    return JsonResponse(history, safe=False)

@csrf_exempt
@login_required
def delete_message_api(request):
    """Supprime un message spécifique de l'historique."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            msg_id = data.get('message_id')
            ChatMessage.objects.get(id=msg_id, user=request.user).delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)

@csrf_exempt
@login_required
def clear_chat_history_api(request):
    """Efface tout l'historique de chat de l'utilisateur."""
    if request.method == 'POST':
        try:
            ChatMessage.objects.filter(user=request.user).delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)
