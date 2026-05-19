from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page_view, name='landing'),
    path('home/', views.home, name='home'),
    path('upload-image/', views.upload_image_view, name='upload_image'),
    path('my-history/', views.my_history, name='my_history'),
    path('historique/', views.prediction_history, name='historique'),
    path('export-csv/', views.export_history_csv, name='export_history_csv'),
    path('export-pdf/', views.export_history_pdf, name='export_history_pdf'),
    path('delete-prediction/<int:prediction_id>/', views.delete_prediction, name='delete_prediction'),
    path('signup/', views.signup_view, name='signup'),
    path('connexion/', views.login_view, name='connexion'),
    path('api/dashboard-data/', views.dashboard_data, name='dashboard_data'),
    path('api/crop-dashboard-data/', views.crop_dashboard_data, name='crop_dashboard_data'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/agro/', views.logout_view, name='agro_logout'),
    path('result/', views.result, name='result'),
    path('selection/', views.selection_view, name='selection'),
    path('price-dashboard/', views.price_dashboard_view, name='price_dashboard'),
    path('analyze-characteristics/', views.analyze_characteristics_view, name='analyze_characteristics'),
    path('crop-result/', views.crop_result_view, name='crop_result'),
]