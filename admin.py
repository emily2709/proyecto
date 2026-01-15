# modulo1/admin.py - VERSIÓN CORREGIDA
from django.contrib import admin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    # ✅ Usa nombres SIN prefijo "usuario_"
    list_display = ['id', 'nombre', 'apellido_paterno', 
                    'email', 'telefono', 'activo', 'creado']
    
    list_display_links = ['id', 'nombre']
    
    search_fields = ['nombre', 'apellido_paterno', 'email', 'telefono']
    
    list_filter = ['activo', 'creado']
    
    ordering = ['-creado']
    
    # ✅ Fieldsets con nombres SIN prefijo
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellido_paterno', 'apellido_materno')
        }),
        ('Información de Contacto', {
            'fields': ('email', 'telefono')
        }),
        ('Cuenta y Seguridad', {
            'fields': ('password', 'user', 'activo'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('creado', 'actualizado')
    