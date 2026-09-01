# Journal de développement

*Traduction française de [development-log.md](development-log.md).*

**Note de statut (2026-09-01) :** ce journal s'est arrêté après sa première
session, à l'époque où le point d'entrée Python de l'extension ne s'exécutait
pas encore (jalon 0.3). Tout ce qui suit est historique, conservé pour garder
la trace des débuts du projet plutôt que comme document vivant. LOUIM a
depuis livré les versions v1.0.0 à v4.3.0, avec la prise en charge de Writer,
Calc, Impress et Draw, et il est mature et stable selon
[HANDOFF.md](../HANDOFF.md). Pour le statut actuel, utilisez
[HANDOFF.md](../HANDOFF.md) pour le statut courant mis à jour à chaque
session, [CHANGELOG.md](../CHANGELOG.md) pour l'historique par version que ce
journal n'a jamais développé, et [PROJECT.md](../PROJECT.md) pour le jalon
actuel et les tâches ouvertes.

## Session 1

### Vision du projet

LOUIM est une extension éducative pour LibreOffice.

Son but est de simplifier progressivement l'interface de LibreOffice pour
réduire la charge cognitive pendant l'apprentissage.

Ce n'est **pas** d'abord un outil de verrouillage ou d'administration.

Les enseignants peuvent créer et partager des modèles d'interface que les
élèves peuvent importer.

---

## Plateformes prises en charge

* Linux
* Windows
* macOS

---

## Périmètre de la version 1

* LibreOffice Writer uniquement
* Python
* Extension LibreOffice (.oxt)

---

## Décisions d'architecture

* Utiliser les identifiants de commande UNO en interne.
* Garder le code spécifique à LibreOffice isolé.
* Les modèles `.louim` restent indépendants de la langue.
* L'extension devrait à terme importer et exporter des configurations
  d'interface LibreOffice.

---

## État actuel du dépôt

Terminé :

* Documentation
* Structure du projet
* Système de construction
* Empaquetage initial de l'extension
* Documents d'architecture
* Feuille de route

Jalon actuel :

Jalon 0.3 — Première extension fonctionnelle.

Objectif :

```
Outils
    LibreOffice UI Manager...

↓

Hello LOUIM
```

Pas encore de personnalisation de l'interface.

---

## Problème actuel

L'extension s'empaquette correctement, mais le point d'entrée Python ne
s'exécute pas.

Causes les plus probables :

* Enregistrement Python à l'intérieur de l'extension
* Emplacement de script incorrect
* Utilisation de `XSCRIPTCONTEXT` à l'intérieur d'une extension

---

## Décision

Plutôt que de déboguer l'empaquetage immédiatement, créer d'abord une macro
Python fonctionnelle.

Séquence de développement :

1. Macro Python fonctionnelle
2. Boîte de dialogue Hello World
3. Empaqueter en extension
4. Ajouter un menu Outils
5. Poursuivre avec le moteur de découverte

---

## Prochaine session

1. Faire fonctionner une macro Python minimale.
2. Vérifier l'exécution de Python via UNO.
3. La convertir en extension installable.
4. Construire un flux de développement pour des tests rapides sans
   reconstruire le .oxt à chaque fois.

---

## Vision à long terme

LOUIM devrait devenir le gestionnaire d'interface éducatif de référence pour
LibreOffice.

Les enseignants devraient pouvoir créer et partager des interfaces Writer
progressives que les élèves peuvent charger d'un simple clic.
