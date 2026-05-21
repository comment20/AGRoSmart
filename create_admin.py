import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SoilClassifier.settings')
django.setup()

from django.contrib.auth.models import User

# Paramètres de votre compte admin
username = 'admin'
email = 'bovalgermaintchoupe@gmail.com'
password = 'Boval#@disco1' # CHANGEZ-LE ENSUITE !

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Superutilisateur '{username}' créé avec succès !")
else:
    print(f"Le superutilisateur '{username}' existe déjà.")
