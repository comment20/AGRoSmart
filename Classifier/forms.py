from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class SoilImageForm(forms.Form):
    image = forms.ImageField(
        label="",
        widget=forms.ClearableFileInput(attrs={
            'accept': 'image/*',
            'class': 'custom-file-input',
            'id': 'imageUpload'
        })
    )
    
class SoilCharacteristicsForm(forms.Form):
    temperature = forms.FloatField(label="Température (°C)")
    ph = forms.FloatField(label="pH du sol")
    humidity = forms.FloatField(label="Humidité (%)")
    nitrogen = forms.FloatField(label="Azote (N) (kg/ha)")
    potassium = forms.FloatField(label="Potassium (K) (kg/ha)")
    phosphorus = forms.FloatField(label="Phosphore (P) (kg/ha)")
    rainfall = forms.FloatField(label="Précipitations (mm)")

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].error_messages = {'required': ''}

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Nom d\'utilisateur'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'})
        }

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['placeholder'] = 'Mot de passe'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirmer le mot de passe'
        for field_name in self.fields:
            self.fields[field_name].error_messages = {'required': ''}
