from django.contrib import admin
from django.urls import path
from modulo1 import views

urlpatterns = [
    
    # Páginas públicas
    path('', views.iniciar, name='iniciar'),  # Login como página principal
    path('home/', views.home, name='home'),  # Home después del login
    path('recuperar/', views.recuperar, name='recuperar'),
    path('recuperar-contrasena/', views.recuperar, name='recuperar_contrasena'),
    path('registrar/', views.registrar_usuario, name='registrar_usuario'),
    
    # Páginas protegidas (requieren login)
    path('logout/', views.logout_view, name='logout'),
    path('contacto/', views.contacto, name='contacto'),
    path('tutoriales/', views.tutoriales, name='tutoriales'),
    
    # ✅ CORREGIDO: Cambia 'admin-usuarios' por 'gestion-usuarios' para evitar conflicto
    path('gestion-usuarios/', views.administracion_usuarios, name='administracion_usuarios'),
    path('gestion-usuarios/crear/', views.create_usuario, name='create_usuario'),
    path('gestion-usuarios/editar/<int:usuario_id>/', views.update_usuario, name='update_usuario'),
    path('gestion-usuarios/eliminar/<int:usuario_id>/', views.delete_usuario, name='delete_usuario'),
    path('gestion-usuarios/buscar/', views.search_usuario, name='search_usuario'),
]