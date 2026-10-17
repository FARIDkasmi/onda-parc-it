from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMINISTRATEUR = 'ADMIN', 'Administrateur'
        TECHNICIEN = 'TECH', 'Technicien'
        RESPONSABLE = 'RESP', 'Responsable'
        UTILISATEUR = 'USER', 'Utilisateur'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.UTILISATEUR,
        verbose_name="Rôle"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Téléphone"
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
