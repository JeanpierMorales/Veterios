from django.urls import path
from . import views

urlpatterns = [
    # Al entrar a la web, cargamos Quienes Somos por defecto
    path('', views.quienes_somos, name='index'), 
    
    path('quienes-somos/', views.quienes_somos, name='quienes_somos'),
    path('ofertas/', views.ofertas, name='ofertas'),
    path('login/', views.login_view, name='login'),
    

    # ESTAS SON LAS QUE FALTAN:
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),


    # Rutas Admin
    path('admin/dashboard/', views.dashboard_admin, name='dashboard_admin'),
    path('admin/gestion-citas/', views.gestion_citas, name='gestion_citas'),
]