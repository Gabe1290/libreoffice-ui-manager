# LOUIM — Passation de développement

*Traduction française de [HANDOFF.md](HANDOFF.md).*

**Objet.** Statut courant / passation pour reprendre le travail sur n'importe
quel ordinateur.
**Pratique à suivre sur chaque machine du projet :** en fin de session, mettre
à jour ce fichier, puis `git commit` + `git push` ; au démarrage, faire
`git pull` et le lire en premier.

_Dernière mise à jour : 2026-09-01._

## État : **mature et stable.**

LOUIM (LibreOffice UI Manager) est le produit fonctionnel — il simplifie les
**menus et barres d'outils classiques** à partir d'un modèle `.louim`. Il est
activement utilisable et installé. L'état au jour le jour vit dans
l'historique git, `CHANGELOG.md`, et `docs/`.

## Hébergement

- **GitLab (origin) :** `gitlab.com/gthullen-group/libreoffice-ui-manager` —
  celui qui **fait foi**. Le développement, les tickets et les publications
  automatisées se passent ici.
- **GitHub (dépôt distant `github`) :**
  `github.com/Gabe1290/libreoffice-ui-manager` — un **simple miroir public**.
  Pas de CI là-bas ; ne pas y développer directement.
- CI : `.gitlab-ci.yml` (compilation → tests unitaires → construction du
  `.oxt` ; sur les étiquettes de version, publication de la Release avec le
  `.oxt` attaché). **Au vert.**

### Mise en miroir (à faire à chaque publication)

Pousser `main` **et** les étiquettes vers **les deux** dépôts distants :

```sh
git push origin main && git push github main
git push origin vX.Y.Z && git push github vX.Y.Z
```

Seule la CI de GitLab réagit à l'étiquette (elle construit et publie la
Release) ; GitHub se contente de stocker les commits/étiquettes mirorés.
**Ne jamais commiter directement sur GitHub** — cela a provoqué une vraie
divergence une fois : du travail poussé directement sur le miroir GitHub n'a
jamais atteint GitLab, si bien que les deux `4.1.0` ont divergé et ont dû être
réconciliés par fusion en **v4.2.0** (2026-08). Gardez-les synchronisés pour
éviter que cela se reproduise.

## Travaux récents (2026-09)

- **Plan de remplissage de la documentation, terminé.** Les 16 fichiers vides
  sous `docs/` sont écrits (le plan dans
  `docs/documentation-fill-plan.md`, commencé le 2026-08-31 sur une autre
  machine, en listait bien 16 dans le détail de ses niveaux 1 à 3, même si sa
  propre ligne de résumé plus haut les sous-comptait à 14). A suivi le même
  choix que ce plan avait fait : documenter le schéma `Module` tel que
  réellement construit, et non le modèle d'objets Workspace/UIElement jamais
  implémenté (voir `docs/adr/0004-workspace-concept.md`). Les documents de
  statut périmés (`PROJECT.md`, `docs/roadmap.md`, `docs/development-log.md`,
  ce fichier) sont désormais à jour par rapport à la v4.3.0 également.
  `docs/documentation-fill-plan.md` est laissé en place comme trace, avec ses
  cases cochées.
- **Traduction française.** Traduction complète en français de tous les
  documents ci-dessus, avec un suffixe `.fr.md`, effectuée en gardant un style
  aussi naturel que possible plutôt qu'une traduction mot à mot.

## Travaux récents (2026-06)

- La boîte de dialogue Enregistrer place par défaut les modèles des
  enseignants dans **`Documents/LOUIM templates`** (persiste après
  réinstallation).
- Migration de GitHub vers GitLab ; toutes les URL du projet repointées ;
  ajout de `.gitlab-ci.yml`.
- Piège : **garder `.gitlab-ci.yml` en ASCII pur** (un tiret cadratin dans un
  commentaire rend le YAML invalide sur GitLab).

## Projet compagnon

L'**interface à onglets (Notebookbar)** est gérée par une extension
**séparée**, **LONBM**
(`gitlab.com/gthullen-group/libreoffice-notebookbar-manager`) — c'est là que
se trouve le développement actif (et un blocage ouvert) en ce moment ; voir
son `HANDOFF.md`. LONBM possède le réglage `ToolbarMode` (variante active) ;
LOUIM n'y touche pas.

## Construction / tests

```sh
python -m pytest -q          # (ou : python -m unittest discover -s tests)
python tools/build.py        # -> dist/louim.oxt
```

## Publication

Entièrement automatisée par `.gitlab-ci.yml` (étapes construction → release).
Pour publier une version :

1. Augmenter le `<version>` dans `extension/description.xml` et ajouter une
   section `## [X.Y.Z]` à `CHANGELOG.md` (avec un lien
   `[X.Y.Z]: .../tags/vX.Y.Z` correspondant en bas de page).
2. Commiter, pousser, puis étiqueter et pousser l'étiquette :
   `git tag -a vX.Y.Z -m "..." && git push origin vX.Y.Z`.

Le pipeline déclenché par l'étiquette construit ensuite le `.oxt`, le dépose
dans le registre générique de paquets, extrait la section CHANGELOG de cette
version comme notes de version, et crée la Release GitLab avec le `.oxt`
attaché — aucune étape manuelle dans l'interface. Éprouvé de bout en bout sur
la v4.1.1 (2026-08-03). Une publication par étiquette : ne pas créer la
release à la main en plus (release-cli renvoie une erreur si elle existe
déjà).

## Installation / où vivent les choses

- Installeur : `dist/louim.oxt` → **Outils ▸ Gestionnaire d'extensions ▸
  Ajouter…**.
- Modèles utilisateur : **`Documents/LOUIM templates`** (persistent après
  réinstallation).
- Sécurité : ne jamais exécuter de tests en direct contre son propre
  LibreOffice en service — utiliser un profil isolé jetable (voir le
  `HANDOFF.md` de LONBM pour le montage).
