# Feuille de route de développement

*Traduction française de [roadmap.md](roadmap.md).*

## Jalon 0.1

Création du projet

- Dépôt Git
- Documentation
- GitHub
- Modèles initiaux

---

## Jalon 0.2

Documentation complète

- Vision
- Architecture
- Principes de conception
- Format des modèles
- Moteur de découverte
- Espace de travail
- Normes de codage
- Guide du développeur

---

## Jalon 0.3

Première extension

- OXT installable
- Menu Outils
- Boîte de dialogue « Hello LOUIM »

---

## Jalon 0.4

Moteur de découverte

- Découvrir les menus de Writer
- Découvrir les barres d'outils
- Découvrir les barres latérales
- Découvrir les commandes

---

## Jalon 0.5

Gestionnaire de profils

- Modèle de données interne
- Enregistrer un profil
- Charger un profil

---

## Jalon 0.6

Gestionnaire de modèles

- Importer un modèle
- Exporter un modèle
- Exporter l'interface active

---

## Jalon 0.7

Moteur d'application

- Masquer les menus
- Restaurer les menus
- Appliquer un profil

---

## Version 1.0

Version stable pour Writer

---

## Version 2.0

Calc

---

## Version 3.0

Impress

---

## Version 4.0

Draw

---

## Version 4.1 – 4.2

Stabilisation

- Corriger les constats d'audit inter-applications : messages liés à la
  mauvaise application, confirmation de restauration localisée, état des
  menus d'extension/barre latérale se combinant entre modules
- Déplacer la référence de vérité de GitHub vers GitLab, avec publications
  automatisées par étiquette
- Réconcilier une divergence d'historique causée pendant le déménagement
  (4.2.0)
- Corriger le nom de fichier de l'artefact de version (4.2.1) et une
  régression `NameError` dans l'adaptateur de menus d'extension (4.2.2) ; ce
  dernier point a reçu un test de garde statique permanent

---

## Version 4.3

Configurer les menus

- Boîte de dialogue intégrée pour supprimer un menu principal intégré entier,
  ce que Outils ▸ Personnaliser ne sait pas faire
- Protéger Fichier, Édition et Aide pour qu'ils ne puissent jamais être
  masqués, refermant une faille de verrouillage de la barre de menus

---

## Phase actuelle — Maintenance

Depuis la v4.3.0 (2026-08-30), le projet se considère mature et stable (voir
[HANDOFF.fr.md](../HANDOFF.fr.md)). Les quatre objectifs allant du jalon 0.3
à la version 4.0 sont livrés, et l'état au jour le jour vit désormais dans
`CHANGELOG.md` et `HANDOFF.md` plutôt que dans de nouveaux jalons numérotés
ici. Les points ouverts sont suivis comme une liste de tâches dans les
« Tâches pour la prochaine session » de PROJECT.md, pas comme des jalons de
feuille de route. L'interface à onglets Notebookbar est délibérément hors du
périmètre de LOUIM ; elle appartient au projet séparé LONBM.
