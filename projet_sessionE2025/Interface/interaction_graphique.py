import tkinter as tk
from typing import Optional, List


class FenetreInteraction:
    def __init__(self):
        self.root = None
        self.resultat = None

    def _centrer_et_placer_fenetre(self):
        self.root.update_idletasks()
        largeur = self.root.winfo_width()
        hauteur = self.root.winfo_height()
        ecran_largeur = self.root.winfo_screenwidth()
        ecran_hauteur = self.root.winfo_screenheight()
        x = (ecran_largeur // 2) - (largeur // 2)
        y = (ecran_hauteur // 2) - (hauteur // 2)
        self.root.geometry(f"+{x}+{y}")
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after_idle(self.root.attributes, "-topmost", False)

    def demander_choix(self, message: str, options: List[str]) -> str:
        self.resultat = None
        self.root = tk.Tk()
        self.root.title("Choix Utilisateur")

        label = tk.Label(self.root, text=message, font=("Arial", 12))
        label.pack(padx=20, pady=10)

        for option in options:
            bouton = tk.Button(self.root, text=option, width=15,
                               command=lambda opt=option: self._valider(opt))
            bouton.pack(pady=5)

        self._centrer_et_placer_fenetre()
        self.root.mainloop()
        return self.resultat

    def demander_texte(self, message: str) -> Optional[str]:
        self.resultat = None
        self.root = tk.Tk()
        self.root.title("Saisie requise")

        label = tk.Label(self.root, text=message, font=("Arial", 12))
        label.pack(padx=20, pady=10)

        champ_texte = tk.Entry(self.root, width=40)
        champ_texte.pack(pady=5)
        champ_texte.focus_set()  # Pour que l'utilisateur puisse taper directement

        # Valide sur clic ou touche Entrée
        bouton = tk.Button(self.root, text="Valider",
                           command=lambda: self._valider(champ_texte.get()))
        bouton.pack(pady=10)

        self.root.bind("<Return>", lambda event: self._valider(champ_texte.get()))  # Entrée pour valider

        self._centrer_et_placer_fenetre()

        self.root.mainloop()

        return self.resultat

    def msgbox(self, message: str, titre: str = "Message"):
        """Affiche un message d'information dans une boîte modale."""
        from tkinter import messagebox
        temp = tk.Tk()
        temp.withdraw()
        messagebox.showinfo(titre, message)
        temp.destroy()

    def _valider(self, valeur):
        self.resultat = valeur
        if self.root:
            self.root.quit()
            self.root.destroy()

    def demander_parametres(self, champs: dict) -> dict:
        """
        Affiche une fenêtre unique avec plusieurs champs de saisie définis dynamiquement.

        :param champs: dictionnaire sous forme {clé_variable: texte_du_label}
        :return: dictionnaire {clé_variable: valeur_float_ou_int}
        """
        import tkinter.messagebox as mbox
        self.root = tk.Tk()
        self.root.title("Saisie de paramètres")
        self.resultat = {}

        entrees = {}

        for key, label_text in champs.items():
            frame = tk.Frame(self.root)
            frame.pack(padx=20, pady=5)
            label = tk.Label(frame, text=label_text, width=40, anchor='w')
            label.pack(side="left")
            entry = tk.Entry(frame, width=15)
            entry.pack(side="right")
            entrees[key] = entry

        def valider():
            try:
                for key, entry in entrees.items():
                    texte = entry.get().strip()
                    # Cast en float par défaut, int si possible
                    valeur = float(texte)
                    if valeur.is_integer():
                        valeur = int(valeur)
                    self.resultat[key] = valeur
                self.root.quit()
                self.root.destroy()
            except ValueError:
                mbox.showerror("Erreur de saisie", "Veuillez entrer uniquement des nombres valides.")

        bouton = tk.Button(self.root, text="Valider", command=valider)
        bouton.pack(pady=10)

        self._centrer_et_placer_fenetre()
        self.root.mainloop()
        return self.resultat

