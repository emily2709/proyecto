
from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_protect
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.utils import timezone
from .models import Usuario
import random
import string
import logging

logger = logging.getLogger(__name__)



def home(request):
    """Página principal"""
    return render(request, 'home.html')

@csrf_protect
def iniciar(request):
    
    if request.user.is_authenticated:
        next_url = request.GET.get('next', 'home')
        return redirect(next_url)
    
  
    next_url = request.GET.get('next', 'home')
    
    if request.method == 'POST':
        username_or_email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        next_url = request.POST.get('next', 'home')  
        
        if not username_or_email or not password:
            messages.error(request, 'Por favor, completa todos los campos')
            return render(request, 'iniciar.html', {'next': next_url})
        
        logger.info(f"Intento de login con: {username_or_email}")
        
      
        user = authenticate(request, username=username_or_email, password=password)
        
      
        if user is None:
            try:
               
                user_by_email = User.objects.get(email__iexact=username_or_email)
                user = authenticate(request, username=user_by_email.username, password=password)
            except User.DoesNotExist:
                user = None
                logger.warning(f"No se encontró usuario con email: {username_or_email}")
        
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f'¡Bienvenido {user.username}!')
           
                return redirect(next_url)
                
            else:
                messages.error(request, 'Tu cuenta está desactivada. Contacta al administrador.')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
        
    
        return render(request, 'iniciar.html', {'next': next_url})
    
  
    return render(request, 'iniciar.html', {'next': next_url})

@csrf_protect
def recuperar(request):
    """Vista de recuperación de contraseña - ÚNICA Y FUNCIONAL"""
    
   
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        
        
        if not email:
            messages.error(request, '❌ Por favor ingresa un email válido.')
            return render(request, 'recuperar.html')
        
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, '❌ Formato de email inválido.')
            return render(request, 'recuperar.html')
        
        logger.info(f"Solicitud de recuperación para email: {email}")
        
        try:
          
            usuario_django = None
            
         
            try:
                usuario_django = User.objects.get(email__iexact=email, is_active=True)
                logger.info(f"Usuario encontrado en Django Auth: {usuario_django.username}")
            except User.DoesNotExist:
              
                try:
                    usuario_personalizado = Usuario.objects.get(usuario_email__iexact=email)
                    logger.info(f"Usuario encontrado en modelo personalizado: {usuario_personalizado.usuario_nombre}")
                    
                    
                    
                except Usuario.DoesNotExist:
                    usuario_personalizado = None
            
       
            if not usuario_django and not usuario_personalizado:
                messages.error(request, 
                    '❌ No existe ningún usuario registrado con ese email.<br>'
                    'Verifica que esté escrito correctamente.'
                )
                return render(request, 'recuperar.html', {'email_usuario': email})
            
           
            if not usuario_django and usuario_personalizado:
                username = usuario_personalizado.usuario_email.split('@')[0]
            
                usuario_django, created = User.objects.get_or_create(
                    username=username,
                    email=usuario_personalizado.usuario_email,
                    defaults={
                        'first_name': usuario_personalizado.usuario_nombre,
                        'password': make_password('temporal123'),
                        'is_active': True
                    }
                )
                if created:
                    logger.info(f"Usuario creado automáticamente en Django Auth: {username}")
            
          
            caracteres = string.ascii_letters + string.digits + "!@#$%&"
            nueva_contraseña = ''.join(random.choices(caracteres, k=12))
            
            logger.info(f"Generada nueva contraseña para: {usuario_django.username}")
            
          
            usuario_django.set_password(nueva_contraseña)
            usuario_django.save()
            
            try:
                usuario_personalizado = Usuario.objects.get(usuario_email__iexact=email)
                usuario_personalizado.usuario_password = make_password(nueva_contraseña)
                usuario_personalizado.save()
                logger.info(f"Contraseña actualizada también en modelo Usuario personalizado")
            except Usuario.DoesNotExist:
                logger.warning(f"Usuario no encontrado en modelo Usuario para {email}")
            
     
            subject = '🔐 Nueva Contraseña - IMCU CARBÓN PLAY'
            
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px; }}
                    .header {{ background: #007bff; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .password-box {{ background: #f8f9fa; border: 2px dashed #007bff; padding: 15px; text-align: center; font-size: 24px; font-weight: bold; margin: 20px 0; }}
                    .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>🔐 IMCU CARBÓN PLAY</h2>
                        <h3>Recuperación de Contraseña</h3>
                    </div>
                    
                    <p>Hola <strong>{usuario_django.username}</strong>,</p>
                    
                    <p>Has solicitado una nueva contraseña para tu cuenta.</p>
                    
                    <div class="password-box">
                        {nueva_contraseña}
                    </div>
                    
                    <p><strong>Instrucciones:</strong></p>
                    <ol>
                        <li>Inicia sesión con la contraseña de arriba</li>
                        <li>Ve a tu perfil de usuario</li>
                        <li>Cambia la contraseña por una de tu preferencia</li>
                    </ol>
                    
                    <p><strong>⚠️ Importante:</strong></p>
                    <ul>
                        <li>Esta contraseña es temporal</li>
                        <li>Cambiala inmediatamente después de ingresar</li>
                        <li>Si no solicitaste este cambio, contacta al administrador</li>
                    </ul>
                    
                    <div class="footer">
                        <p>🏢 IMCU CARBÓN PLAY<br>
                        📧 {settings.DEFAULT_FROM_EMAIL}<br>
                        ⏰ {timezone.now().strftime('%d/%m/%Y %H:%M')}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            plain_message = f"""Hola {usuario_django.username},

Has solicitado una nueva contraseña para tu cuenta en IMCU CARBÓN PLAY.

Tu nueva contraseña es: {nueva_contraseña}

Instrucciones:
1. Inicia sesión con esta contraseña
2. Ve a tu perfil
3. Cambia la contraseña por una más fácil de recordar

Importante:
- Esta contraseña es temporal
- Cámbiala inmediatamente después de ingresar
- Si no solicitaste este cambio, contacta al administrador

--
IMCU CARBÓN PLAY
{settings.DEFAULT_FROM_EMAIL}
{timezone.now().strftime('%d/%m/%Y %H:%M')}"""
            
            try:
                send_mail(
                    subject,
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [usuario_django.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                
                logger.info(f"Email de recuperación enviado a {usuario_django.email}")
                
                messages.success(
                    request,
                    f'✅ <strong>¡Contraseña enviada con éxito!</strong><br><br>'
                    f'👤 <strong>Usuario:</strong> {usuario_django.username}<br>'
                    f'📧 <strong>Email:</strong> {usuario_django.email}<br><br>'
                    f'📨 <em>La nueva contraseña ha sido enviada a tu correo.<br>'
                    f'Revisa también la carpeta de spam si no lo ves.</em>'
                )
                
            except Exception as e:
                logger.error(f"Error enviando email: {str(e)}")
                messages.error(
                    request,
                    f'❌ <strong>Error al enviar el email</strong><br><br>'
                    f'🔧 <em>Error técnico: {str(e)}<br>'
                    f'Por favor, contacta al administrador.</em>'
                )
                
        except Exception as e:
            logger.error(f"Error en recuperación: {str(e)}")
            messages.error(
                request,
                f'❌ <strong>Error en el proceso de recuperación</strong><br><br>'
                f'🔧 <em>Detalle: {str(e)}</em>'
            )
        
        return render(request, 'recuperar.html')
    
   
    return render(request, 'recuperar.html')


@csrf_protect
def registrar_usuario(request):

    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        apellido_paterno = request.POST.get('apellido_paterno', '').strip()
        apellido_materno = request.POST.get('apellido_materno', '').strip()
        email = request.POST.get('email', '').strip().lower()
        telefono = request.POST.get('telefono', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        
     
        errors = []
        
        if not all([nombre, apellido_paterno, email, telefono, password]):
            errors.append('Todos los campos son obligatorios excepto apellido materno')
        
        if password != password2:
            errors.append('Las contraseñas no coinciden')
        
        if len(password) < 8:
            errors.append('La contraseña debe tener al menos 8 caracteres')
        
        try:
            validate_email(email)
        except ValidationError:
            errors.append('Email inválido')
        
  
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        

        if User.objects.filter(email__iexact=email).exists():
            errors.append('Este email ya está registrado en el sistema')
        
    
        if Usuario.objects.filter(usuario_email__iexact=email).exists():
            errors.append('Este email ya está registrado en usuarios personalizados')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'registrar.html', {
                'nombre': nombre,
                'apellido_paterno': apellido_paterno,
                'apellido_materno': apellido_materno,
                'email': email,
                'telefono': telefono,
            })
        
        try:
        
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=nombre,
                last_name=apellido_paterno,
                is_active=True
            )
            
           
            Usuario.objects.create(
                usuario_nombre=nombre,
                usuario_apellido_paterno=apellido_paterno,
                usuario_apellido_materno=apellido_materno,
                usuario_email=email,
                usuario_telefono=telefono,
                usuario_password=make_password(password),
            )
            
           
            login(request, user)
            messages.success(request, f'¡Registro exitoso {nombre}! Ya puedes acceder al sistema.')
            return redirect('home')
            
        except Exception as e:
            logger.error(f"Error en registro: {str(e)}")
            messages.error(request, f'Error en el registro: {str(e)}')
    
    return render(request, 'registrar.html')


def logout_view(request):
    """Cerrar sesión"""
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.success(request, f'Has cerrado sesión correctamente. ¡Hasta luego {username}!')
    else:
        messages.info(request, 'No hay sesión activa')
    
    return redirect('iniciar')



@login_required(login_url='iniciar')
def contacto(request):
    return render(request, 'contacto.html')

@login_required(login_url='iniciar')
def tutoriales(request):
    return render(request, 'tutoriales.html')



@staff_member_required
@login_required(login_url='iniciar')
def administracion_usuarios(request):
    """Vista principal de administración de usuarios - Usando tu modelo Usuario"""
  
    usuarios = Usuario.objects.all().order_by('-creado')  
    return render(request, 'admin_usuarios.html', {'usuarios': usuarios})

@staff_member_required
@login_required(login_url='iniciar')
def create_usuario(request):
    """Crear usuario desde administración personalizada"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        apellido_paterno = request.POST.get('apellido_paterno', '').strip()
        apellido_materno = request.POST.get('apellido_materno', '').strip()
        email = request.POST.get('email', '').strip().lower()
        telefono = request.POST.get('telefono', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        
        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden')
            return render(request, 'usuario.html')
        
        if Usuario.objects.filter(usuario_email__iexact=email).exists():
            messages.error(request, 'Este email ya está registrado')
            return render(request, 'usuario.html')
        
        try:
           
            Usuario.objects.create(
                usuario_nombre=nombre,
                usuario_apellido_paterno=apellido_paterno,
                usuario_apellido_materno=apellido_materno,
                usuario_email=email,
                usuario_telefono=telefono,
                usuario_password=make_password(password),
            )
            
            messages.success(request, f'Usuario {nombre} creado exitosamente')
            return redirect('administracion_usuarios')
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'usuario.html')

@staff_member_required
@login_required(login_url='iniciar')
def update_usuario(request, usuario_id):
    """Actualizar usuario"""
    try:
        usuario = get_object_or_404(Usuario, id=usuario_id)
        if request.method == 'POST':
            usuario.usuario_nombre = request.POST.get('nombre', '').strip()
            usuario.usuario_apellido_paterno = request.POST.get('apellido_paterno', '').strip()
            usuario.usuario_apellido_materno = request.POST.get('apellido_materno', '').strip()
            nuevo_email = request.POST.get('email', '').strip().lower()
            
    
            if nuevo_email != usuario.usuario_email and Usuario.objects.filter(usuario_email__iexact=nuevo_email).exclude(id=usuario_id).exists():
                messages.error(request, 'Este email ya está registrado por otro usuario')
            else:
                usuario.usuario_email = nuevo_email
            
            usuario.usuario_telefono = request.POST.get('telefono', '').strip()
            
            nueva_password = request.POST.get('password', '')
            if nueva_password:
                usuario.usuario_password = make_password(nueva_password)
            
            usuario.save()
            messages.success(request, f'Usuario {usuario.usuario_nombre} actualizado')
            return redirect('administracion_usuarios')
       
        context = {
            'usuario': usuario,
            'nombre': usuario.usuario_nombre,
            'apellido_paterno': usuario.usuario_apellido_paterno,
            'apellido_materno': usuario.usuario_apellido_materno or '',
            'email': usuario.usuario_email,
            'telefono': usuario.usuario_telefono or '',
        }
        return render(request, 'update_usuario.html', context)
        
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
        return redirect('administracion_usuarios')

@staff_member_required
@login_required(login_url='iniciar')
def delete_usuario(request, usuario_id):
    """Eliminar usuario"""
    if request.method == 'POST':
        try:
            usuario = get_object_or_404(Usuario, id=usuario_id)
            nombre = usuario.usuario_nombre
            usuario.delete()
            messages.success(request, f'Usuario {nombre} eliminado correctamente')
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuario no encontrado')
    return redirect('administracion_usuarios')

@staff_member_required
@login_required(login_url='iniciar')
def search_usuario(request):
    """Buscar usuarios"""
    query = request.GET.get('q', '')
    if query:
        usuarios = Usuario.objects.filter(
            models.Q(usuario_nombre__icontains=query) |
            models.Q(usuario_apellido_paterno__icontains=query) |
            models.Q(usuario_email__icontains=query) |
            models.Q(usuario_telefono__icontains=query)
        )
    else:
        usuarios = Usuario.objects.all()
    
    return render(request, 'search_usuario.html', {
        'usuarios': usuarios,
        'query': query,
        'total': usuarios.count()
    })



@staff_member_required
def verificar_usuarios(request):
    """Función de debug para ver todos los usuarios registrados"""
    usuarios_django = User.objects.all().values('id', 'username', 'email', 'is_active', 'date_joined')
    usuarios_personalizados = Usuario.objects.all().values('id', 'usuario_nombre', 'usuario_email', 'usuario_telefono', 'creado')
    
    context = {
        'django_users': list(usuarios_django),
        'personal_users': list(usuarios_personalizados),
        'total_django': usuarios_django.count(),
        'total_personal': usuarios_personalizados.count(),
    }
    

    return render(request, 'debug_usuarios.html', context)

