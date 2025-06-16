import numpy as np
import requests
class ConditionVol:
    def __init__(self, altitude_m, mach, angle_deg, delta_isa=0):
        self.altitude_m = altitude_m          # Altitude en mètres
        self.mach = mach                      # Nombre de Mach
        self.angle_deg = angle_deg            # Angle d'attaque (°)
        self.delta_isa = delta_isa            # Écart par rapport à l'atmosphère standard (K ou °C)

        # Calcul des paramètres atmosphériques
        self.temperature_K, self.densite_kgm3, self.viscosite_kgms = self._calculer_parametres_isa()

    def _calculer_parametres_isa(self):
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

