
from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User 

class Usuario(models.Model):

    nombre = models.CharField("Nombre", max_length=100)
    apellido_paterno = models.CharField("Apellido Paterno", max_length=100)
    apellido_materno = models.CharField("Apellido Materno", max_length=100, blank=True, null=True)
    email = models.EmailField("Email", unique=True)
    telefono = models.CharField("Teléfono", max_length=20, blank=True, null=True)
    password = models.CharField("Contraseña", max_length=128)
    
    user = models.OneToOneField(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='usuario_personalizado'
    )
    
    activo = models.BooleanField("Activo", default=True)
    creado = models.DateTimeField("Fecha creación", auto_now_add=True)
    actualizado = models.DateTimeField("Fecha actualización", auto_now=True)
    
    class Meta:
        verbose_name = "Usuario Personal"
        verbose_name_plural = "Usuarios Personales"
        db_table = 'usuarios_personales'
        ordering = ['-creado']
    
    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno}"
    
    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2')):
            self.password = make_password(self.password)

        super().save(*args, **kwargs)
