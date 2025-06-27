import numpy as np
import os
import requests

"""
Module : ConditionVol

Ce module définit la classe ConditionVol, qui permet de calculer les **paramètres atmosphériques**
selon l'altitude, le Mach et un écart à l'atmosphère standard (ΔISA), en se basant sur le modèle ISA.

Fonctionnalités principales :
- Calcul de la température, densité et viscosité de l’air selon l'altitude.
- Affichage formaté des paramètres de vol.
- Calcul du nombre de Reynolds pour un profil donné.

Classes :
---------
ConditionVol:
    Représente une condition de vol (altitude, Mach, angle d’attaque, ΔISA) et calcule
    les paramètres nécessaires aux simulations aérodynamiques.

Attributs :
-----------
- altitude_m (float)       : Altitude de vol en mètres.
- mach (float)             : Nombre de Mach.
- angle_deg (float)        : Angle d’attaque en degrés.
- delta_isa (float)        : Ecart de température par rapport à l’atmosphère standard (K).
- temperature_K (float)    : Température réelle de l’air (K).
- densite_kgm3 (float)     : Densité de l’air (kg/m³).
- viscosite_kgms (float)   : Viscosité dynamique de l’air (kg/(m·s)).

Méthodes :
----------
- _calculer_parametres_isa() : Calcule T, ρ, μ en fonction de l’altitude et ΔISA.
- afficher()                 : Affiche les paramètres de vol calculés.
- calculer_reynolds(...)     : Calcule le nombre de Reynolds à partir des conditions de vol.
"""
class ConditionVol:
    def __init__(self, altitude_m, mach, angle_deg, delta_isa=0):
        self.altitude_m = altitude_m          # Altitude en mètres
        self.mach = mach                      # Nombre de Mach
        self.angle_deg = angle_deg            # Angle d'attaque (°)
        self.delta_isa = delta_isa            # Écart par rapport à l'atmosphère standard (K ou °C)

        # Calcul des paramètres atmosphériques
        self.temperature_K, self.densite_kgm3, self.viscosite_kgms = self._calculer_parametres_isa()

    def _calculer_parametres_isa(self):

        """
                Calcule les paramètres atmosphériques basés sur le modèle ISA (Standard Atmosphere).

                Le modèle ISA fournit des estimations de la température, pression, densité et viscosité
                de l'air en fonction de l'altitude. Cette méthode applique la formule de la troposphère
                si l'altitude est ≤ 11 000 m, sinon celle de la stratosphère (température constante).

                Returns:
                    T (float): Température de l'air en Kelvin.
                    rho (float): Densité de l'air en kg/m³.
                    mu (float): Viscosité dynamique de l'air en kg/(m·s).
                """
        # Constantes
        T0 = 288.15      # Température au sol (K)
        P0 = 101325      # Pression au sol (Pa)
        g = 9.80665      # Gravité (m/s²)
        R = 287.05       # Constante des gaz parfaits (J/kg·K)
        L = 0.0065       # Gradient thermique (K/m)

        if self.altitude_m <= 11000:
            # Troposphère : température diminue avec l'altitude
            T_ISA = T0 - L * self.altitude_m
            T = T_ISA + self.delta_isa
            P = P0 * ((T_ISA) / T0) ** (g / (R * L))
        else:
            # Stratosphère (T constante, P chute exponentiellement)
            T_ISA = 216.65
            T = T_ISA + self.delta_isa
            P = 22632.06 * np.exp(-g * (self.altitude_m - 11000) / (R * T))

        rho = P / (R * T)
        mu = 1.458e-6 * T**1.5 / (T + 110.4)  # Formule de Sutherland

        return T, rho, mu

    def afficher(self):
        print(f"Altitude        : {self.altitude_m} m")
        print(f"Mach            : {self.mach:.2f}")
        print(f"Angle d’attaque : {self.angle_deg}°")
        print(f"Delta ISA       : {self.delta_isa:+.1f} K")
        print(f"Température     : {self.temperature_K:.2f} K")
        print(f"Densité         : {self.densite_kgm3:.4f} kg/m³")
        print(f"Viscosité       : {self.viscosite_kgms:.6e} kg/m·s")


    def calculer_reynolds(self, vitesse_m_s, corde_m, viscosite_kgms, densite_kgm3):
        """
        Calcule le nombre de Reynolds autour d'une aile.

        Le nombre de Reynolds caractérise le régime d'écoulement (laminaire/turbulent) autour du profil.

        Args:
            vitesse_m_s (float): Vitesse de l’air en m/s.
            corde_m (float): Longueur de la corde de l’aile (caractéristique) en mètres.
            viscosite_kgms (float): Viscosité dynamique de l’air (kg/m·s).
            densite_kgm3 (float): Densité de l’air (kg/m³).

        Returns:
            float: Nombre de Reynolds.
        """
        return (densite_kgm3 * vitesse_m_s * corde_m) / viscosite_kgms

