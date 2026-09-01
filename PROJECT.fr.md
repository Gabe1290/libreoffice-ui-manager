# Gestionnaire d'interface LibreOffice — PROJET

*Traduction française de [PROJECT.md](PROJECT.md).*

## Mission

LOUIM est une extension éducative pour LibreOffice, conçue pour simplifier progressivement l'interface de LibreOffice Writer.

Elle aide les enseignants à réduire la charge cognitive en n'affichant que les outils nécessaires à l'étape d'apprentissage en cours.

LOUIM est un outil pédagogique, pas un outil de verrouillage.

## Jalon actuel

**Version 4.3.0 — boîte de dialogue Configurer les menus + correction du verrouillage File/Edition/Aide
(2026-08-30). État : mature et stable.** [HANDOFF.fr.md](HANDOFF.fr.md) est le
document de référence pour le suivi au jour le jour ; pensez à le mettre à jour aussi si cette section change.

LOUIM pilote les quatre applications principales de LibreOffice, Writer, Calc, Impress et
Draw, à partir d'un même moteur paramétré par module (`src/louim/adapters/modules.py`).
Un descripteur `Module` regroupe les identifiants propres à chaque application : service
document, nœud d'état de fenêtre, noms d'application pour la barre latérale, contextes
des menus d'extension et substitutions de groupe de contexte partagé pour la barre latérale.
Chaque adaptateur prend un paramètre `module` (Writer par défaut), et l'extension
dirige l'application, la restauration et l'export selon le document actif.
Impress et Draw forment les deux moitiés complémentaires du groupe de barre latérale
`DrawImpress`. Des modèles de départ sont fournis pour les quatre applications. Une
boîte de dialogue « Configurer les menus... » permet à un enseignant de supprimer un menu
principal entier depuis l'application elle-même, ce que Outils ▸ Personnaliser ne
permet pas. Trois menus, Fichier, Édition et Aide, ne peuvent jamais être supprimés,
ce qui referme une faille où masquer tous les menus entraînait aussi la disparition du
menu de LOUIM lui-même.

Le développement a quitté GitHub pour GitLab en version 4.1.x
(`gitlab.com/gthullen-group/libreoffice-ui-manager` fait désormais foi), GitHub
n'étant conservé que comme simple miroir. Les versions v1.0.0 à v4.3.0 sont
étiquetées et publiées, et 110 tests unitaires hors ligne passent. Voir
[docs/architecture.fr.md](docs/architecture.fr.md) pour la conception technique
actuelle, réécrite le 2026-09-01 pour refléter ce qui est réellement livré plutôt
que le plan initial d'organisation en couches Modèle/Moteur/Interface.

## Résolu

Le point d'entrée Python intégré se résout et s'exécute correctement ; le moteur
est bien relié au menu, comme vérifié.

Causes profondes corrigées :

- Le manifeste de l'extension n'enregistrait pas les scripts Python. Ajout d'une
  entrée de fichier `framework-script` pour le dossier `python/` dans
  `extension/META-INF/manifest.xml`.
- L'URL du script de menu était mal formée. La forme correcte pour un script
  intégré est
  `vnd.sun.star.script:<dossier-oxt>/python/louim/extension.py$hello?language=Python&location=user:uno_packages`
  (le premier segment du chemin est le nom du dossier `.oxt` déployé ; le `$`
  précède le nom de la fonction).
- La construction produit désormais un nom de fichier stable, `dist/louim.oxt`
  (sans numéro de version), afin que le nom du dossier déployé dans l'URL du
  script reste constant d'une version à l'autre. Le numéro de version reste
  dans `extension/description.xml`.

Piège opérationnel découvert : un enregistrement à moitié effectué (par exemple
installer via l'interface graphique puis lancer `unopkg add` pendant que
LibreOffice tourne) laisse le dépôt d'extensions utilisateur incohérent, et un
démarrage complet ultérieur *purge* le paquet pendant la synchronisation — ce qui
se traduit par une erreur `KeyError : '<oxt>'` venant de `pythonscript.py`.
Solution : fermer LibreOffice, puis lancer `unopkg add dist/louim.oxt` une seule
fois, proprement.

Vérifié en mode headless via le fournisseur de scripts : l'URI du menu se résout
et s'exécute correctement.

## Décision actuelle

L'extension intégrée fonctionne, donc on poursuit avec un empaquetage `.oxt`
propre. La macro de développement autonome (`tools/dev-macro/louim_hello.py` +
`tools/install-dev-macro.sh`) reste un moyen rapide de tester des extraits UNO
en dehors du paquet.

## Tâches pour la prochaine session

Actualisé le 2026-09-01. Les points 1 et 2 ci-dessous ont été partiellement
traités par la vérification en direct de la v4.3.0. Le point 3 a en réalité été
résolu lors du travail « L'export capture les éléments de menu + les boutons de
barre d'outils », mais cette liste n'avait jamais été mise à jour pour le dire
jusqu'à maintenant.

1. Test manuel complet de bout en bout dans une vraie fenêtre Writer, en une
   seule fois : installer `dist/louim.oxt`, appliquer « Getting Started »,
   vérifier que la barre d'outils Dessin s'affiche et que Rechercher/Insertion
   ont disparu, ajouter une entrée `sidebar` masquant `GalleryDeck` et vérifier
   qu'elle quitte bien la barre latérale, vérifier que « Enregistrer la
   disposition comme modèle... » fonctionne dans les deux sens, et confirmer
   que Restaurer redonne tout. La v4.3.0 a vérifié en direct la boîte de
   dialogue Configurer les menus sur des profils jetables anglais et français,
   mais pas cette liste complète en une seule passe.
2. Vérifier à l'écran l'interface en allemand et en italien sur un LibreOffice
   non anglophone. L'anglais et le français ont été vérifiés en direct pour la
   boîte de dialogue Configurer les menus en v4.3.0 ; la cohérence des chaînes
   et des formats entre les quatre langues est testée automatiquement, mais
   l'allemand et l'italien n'ont pas été vérifiés visuellement à l'écran.
3. Fait : décider si l'export depuis l'application doit aussi capturer les
   éléments de menu imbriqués. `menu_visibility` dans menubar.py capture
   désormais chaque élément imbriqué masqué, pas seulement les menus
   principaux, depuis le travail « L'export capture les éléments de menu + les
   boutons de barre d'outils » ci-dessous.
4. Ajouter un `description.xml` / `description.txt` localisé pour le
   Gestionnaire d'extensions. Toujours en anglais uniquement.

## Fait — correction du verrouillage Fichier/Édition/Aide (après la 4.3.0, 2026-08-30)

Décocher tous les menus dans la nouvelle boîte de dialogue Configurer les menus,
ou un modèle écrit à la main marquant tous les menus à `false`, produisait une
barre de menus vide. Le menu de LOUIM lui-même est fusionné dans cette barre,
ancré après Aide, donc il disparaissait aussi : plus de Restaurer tous les
menus, plus de Choisir un modèle, aucun moyen de revenir en arrière sinon
`soffice --safe-mode` ou la suppression de la configuration de barre de menus
du profil. Reproduit sur un profil jetable.

Correction : `menubar.PROTECTED_MENUS` (Fichier `.uno:PickList`, Édition
`.uno:EditMenu`, Aide `.uno:HelpMenu`) est forcé visible en tout début
d'`apply_menu_profile`, de sorte qu'un modèle marquant l'un d'eux à `false` soit
outrepassé plutôt qu'obéi. La boîte de dialogue affiche les trois menus cochés
et grisés, pour que la contrainte soit visible plutôt qu'un contournement
silencieux. Les textes d'aide ont été mis à jour dans les quatre langues. 110
tests hors ligne passent, dont un nouveau test où un profil marquant les
quatre menus à false se réduit exactement à Fichier/Édition/Aide.

## Fait — Version v4.3.0 : boîte de dialogue Configurer les menus

Outils ▸ Personnaliser permet de retirer des éléments de menu individuels mais
pas un menu principal intégré entier. Il n'y a pas de case à cocher de
visibilité pour cela, et Supprimer est réservé aux menus que l'on a créés
soi-même. Le moteur de LOUIM savait déjà supprimer une entrée de menu
complètement ; ceci ajoute la manière de le demander depuis l'application.

Une nouvelle boîte de dialogue « Configurer les menus... »
(`src/louim/ui/menu_picker.py`) affiche une case à cocher par menu principal,
construite à l'exécution à partir de `UnoControlDialogModel`, avec des libellés
résolus via `UICommandDescription` pour correspondre à la langue de
l'utilisateur. `menubar.top_level_choices()` lit la liste depuis la
configuration d'usine plutôt que depuis la barre de menus active, de sorte
qu'un menu déjà masqué par LOUIM apparaît toujours et peut être rétabli ;
`merge_top_level_choices()` superpose les cases cochées à un instantané
`menu_visibility` en direct sans faire réapparaître les éléments masqués
individuellement. « Apply Template... » a été renommé « Choisir un modèle... »
dans les quatre langues.

Vérifié en direct sur des profils jetables, en anglais et en français, jamais
sur un LibreOffice en service. 107 tests hors ligne passent.

## Fait — Versions v4.1.0 à v4.2.2 : infrastructure + corrections d'audit

La v4.1.0 a livré une série de corrections issues d'un audit : la boîte de
dialogue « mauvaise application » nomme désormais l'application du *modèle*
plutôt que celle dans laquelle on se trouve déjà, la confirmation de
restauration nomme l'application active dans les quatre langues au lieu de
toujours dire Writer, et les fichiers d'état des menus d'extension/barre
latérale enregistrent désormais à la fois la valeur d'avant masquage et ce que
LOUIM a écrit, de sorte que restaurer dans une application se combine avec un
masquage encore appliqué dans une autre au lieu de l'écraser (les anciens
fichiers d'état restent compris). « Enregistrer la disposition actuelle » a
aussi cessé d'exporter les barres d'outils contextuelles comme visibles.

À la même époque, le développement a déménagé vers GitLab
(`gitlab.com/gthullen-group/libreoffice-ui-manager`) qui fait désormais foi,
avec un pipeline CI de publication automatisé par étiquette de version. GitHub
n'est conservé que comme simple miroir ; ne jamais développer directement là-bas
(voir [HANDOFF.fr.md](HANDOFF.fr.md)). Ce déménagement a provoqué une véritable
divergence en v4.2.0 : du travail a atterri directement sur le miroir GitHub
pendant que GitLab devenait la référence, produisant deux `4.1.0` différents.
Cela a été réconcilié en fusionnant le `4.1.0` de GitHub, les corrections
d'audit ci-dessus plus `tools/verify-restore.py`, dans l'historique de GitLab.

La v4.2.1 a corrigé un problème de publication : la CI publiait l'artefact de
version sous un nom de fichier versionné (`louim-<version>.oxt`), mais
`Addons.xcu` code en dur `louim.oxt` dans chaque URL de script, donc installer
l'artefact versionné cassait chaque commande de menu avec
`KeyError : 'louim.oxt'`. La CI publie désormais toujours le nom de fichier
stable `louim.oxt`, le numéro de version ne vivant plus que dans le chemin du
registre.

La v4.2.2 a corrigé un bogue de code : `state_path` dans `addons.py` utilisait
`uno.fileUrlToSystemPath`, mais avait perdu son `import uno` local lorsque le
module est passé aux imports paresseux en 4.2.0, donc appliquer tout modèle
masquant un menu d'extension plantait avec `NameError`. Corrigé, et
accompagné d'un nouveau test de garde statique (`tests/test_uno_imports.py`)
qui échoue hors ligne si une fonction utilise `uno` ou `unohelper` sans import
accessible dans sa portée, afin que cette classe précise de bogue ne puisse
plus atteindre la CI en silence.

## Fait (vérifié sur une instance isolée) — L'export capture les boutons masqués via Personnaliser

Correction : un modèle enregistré ne remasquait pas les icônes de barre d'outils
qu'un enseignant avait retirées via Outils ▸ Personnaliser. Personnaliser ne
supprime pas un bouton — il met sa propriété ``IsVisible`` à False
(``toolbar:visible="false"`` dans la configuration) tout en le laissant dans la
barre d'outils. L'export comparait la *présence*, donc il ratait ces cas.
Désormais `toolbar_item_visibility` compare la **visibilité** via
`_visible_commands` (sensible à IsVisible), donc un bouton masqué de l'une ou
l'autre manière est capturé comme `toolbaritems` à `false`. Vérifié sur un
profil jetable : un masquage par IsVisible=False a été capturé par l'export et
remasqué en réappliquant le modèle. 64 tests passent (2 nouveaux).

## Fait (vérifié sur une instance isolée) — Restauration et réduction des icônes de barre d'outils avec les menus

Corrige une lacune : les icônes de barre d'outils retirées n'étaient pas
restaurées en appliquant un autre modèle (par ex. `writer-full`), car l'élagage
ne défaisait que les propres changements suivis par LOUIM.

- `apply_toolbar_items` / `restore_toolbar_items` sont désormais **non
  cumulatifs sur toutes les barres d'outils** : chaque application (et
  restauration) réinitialise d'abord *chaque* barre d'outils personnalisée à
  sa définition d'usine, puis retire les boutons masqués par le profil — donc
  appliquer n'importe quel modèle restaure les icônes retirées par LOUIM *ou*
  à la main via Outils ▸ Personnaliser. Cela reflète la façon dont la barre de
  menus est reconstruite depuis la configuration d'usine.
- `menu_command_descendants` (`menubar.py`) + `hidden_toolbar_commands`
  (`toolbaritems.py`) : avec `hide_toolbar_buttons_with_menus`, masquer un menu
  principal entier retire désormais aussi les boutons de barre d'outils des
  fonctionnalités qu'il contenait.
- L'indicateur a été ajouté à `writer-level-1` / `writer-level-2`, afin qu'ils
  réduisent les icônes en cohérence avec leurs menus réduits.

Vérifié sur une instance headless jetable : appliquer level-1 a retiré le
bouton de barre d'outils d'une fonctionnalité du menu Insertion ; appliquer
writer-full l'a restauré ; et un retrait manuel non suivi a été restauré par
une simple application. 62 tests passent (3 nouveaux).

## Fait (vérifié sur une instance isolée) — L'export capture les éléments de menu + les boutons de barre d'outils

« Enregistrer la disposition comme modèle... » capture désormais l'interface
**élément par élément**, pas seulement les menus principaux — de sorte qu'un
enseignant puisse retoucher à la main via Outils ▸ Personnaliser et exporter
un profil « débutant » fidèle.

- `menu_visibility` (`menubar.py`) a été réécrite : elle parcourt l'arbre de
  configuration d'usine face à la barre de menus active et enregistre chaque
  menu principal (true/false) plus chaque élément imbriqué retiré comme
  `false`. Consciente de la hiérarchie parent-enfant, donc les enfants d'un
  menu déjà masqué ne sont pas listés en double. Les fonctions pures
  `_export_walk` / `_collect_command_set` sont testées avec des conteneurs
  factices.
- `toolbar_item_visibility` (`toolbaritems.py`) enregistre les boutons de
  barre d'outils retirés comme `toolbaritems` à `false`.
- `assemble_template` a gagné un emplacement `toolbaritems` (émis seulement
  s'il n'est pas vide) ; `build_current_template` relie les deux.

Aller-retour **vérifié** sur une instance headless jetable : après avoir
masqué un menu principal, un élément imbriqué et un bouton de barre d'outils,
l'export a capturé les trois (et laissé les menus visibles à `true`). 59 tests
unitaires passent (5 nouveaux).

## Fait (vérifié sur une instance isolée) — Masquage des boutons de barre d'outils (moteur d'application v5)

Les modèles peuvent désormais amincir les icônes *à l'intérieur* des barres
d'outils, pas seulement masquer des barres d'outils entières, de sorte qu'un
profil simplifié retire les boutons des fonctionnalités qu'il a supprimées.
`src/louim/adapters/writer/toolbaritems.py` :

- `toolbaritems` (modèle) — une correspondance commande → booléen ; les
  boutons des commandes marquées `false` sont retirés de chaque barre d'outils
  qui les contient.
- `hide_toolbar_buttons_with_menus` (modèle, booléen) — si vrai, chaque
  commande masquée dans `menus` perd aussi son bouton de barre d'outils (le
  comportement demandé « réduire les menus → réduire les icônes »).
  `hidden_commands_for(template)` est la fonction pure d'assistance qui fait
  l'union des deux sources.
- Réutilise le `_prune_hidden` récursif de la barre de menus : chaque barre
  d'outils concernée est réinitialisée à sa définition d'usine puis élaguée,
  enregistrée dans `louim-toolbaritem-state.json` pour que la restauration
  revienne exactement en arrière. Seules les barres d'outils contenant
  effectivement une commande masquée sont touchées (vérification
  d'appartenance économe via `getDefaultSettings`).

Relié à l'application/restauration de l'extension, à l'outil de développement
`apply-template.py`, au chargeur, et à `docs/template-format.md`. Logique pure
testée unitairement (54 tests passent). **Vérifié** sur une instance headless
jetable : masquer une commande de la barre Standard l'a fait disparaître
(53 → 52 boutons) et la restauration l'a ramenée (→ 53) ; le chemin
d'auto-correspondance avec les menus a été exercé.

## Fait — Localisation : anglais, français, allemand, italien

L'interface propre de LOUIM est désormais traduite. Le moteur était déjà
indépendant de la langue (il s'appuie sur les identifiants de commande UNO /
URL de ressource, jamais sur des libellés localisés), donc seules les
surfaces propres à LOUIM nécessitaient du travail :

- `src/louim/i18n.py` — tables de chaînes pour en/fr/de/it, un `translator(lang)`
  pur (repli sur l'anglais pour une clé ou une langue manquante),
  `normalize_lang` ("fr-FR" → "fr", non pris en charge → "en"), et
  `office_language(ctx)` qui lit `ooLocale` depuis la configuration L10N de
  l'application (import `uno` paresseux).
- `extension.py` — chaque titre de boîte de dialogue, corps de message et
  chaîne de sélecteur de fichier provient désormais du traducteur, choisi
  selon la langue active de l'application.
- `extension/Addons.xcu` — chaque titre d'élément de menu porte des valeurs
  `xml:lang` pour en-US/fr/de/it (Apply Template, Save Current Layout,
  Restore Full Menus, Hello). Le nom du menu principal reste la marque
  « LibreOffice UI Manager ».
- Tests : 48 passent (10 nouveaux) — cohérence des clés/langues, **cohérence
  du nombre de paramètres `%`** entre les langues (pour que le formatage `%`
  ne puisse pas échouer), comportement de repli, normalisation de la locale.
  Vérifié que les chaînes fr/de/it s'affichent avec les bons accents et
  guillemets.

Non localisé (délibérément, faible valeur) : le nom d'affichage du
`description.xml` du Gestionnaire d'extensions (une marque) et le texte de
`description.txt`.

## Fait — Libellés de découverte (vérifié) + export allégé

- **Les libellés de menu** se résolvent désormais via le service
  `UICommandDescription` (`menubar.py` `_command_labels` / `_label_for`), donc
  `discover-menus.py` affiche de vrais noms même sans document ouvert (la
  configuration de la barre de menus laisse `Label` vide). **Vérifié** sur
  l'instance isolée : 11/11 menus principaux et 553/553 éléments de menu ont
  résolu de vrais noms.
- **Export allégé** : `curate_toolbars` (dans `toolbars.py`) réduit la carte
  `toolbars` exportée aux barres d'outils Writer courantes plus tout ce qui
  est explicitement masqué, au lieu des quelque 58 barres d'outils de l'état
  de fenêtre, afin que les modèles enregistrés restent lisibles. Fonction
  pure, testée unitairement.
- `toolbars.py` a été refactorisé pour importer `uno` paresseusement (comme
  `menubar.py`/`sidebar.py`) afin que `curate_toolbars` soit testable hors
  ligne. Suite : 38 tests passent (5 nouveaux).

## Fait (vérifié sur une instance isolée) — Masquage des volets de la barre latérale (moteur d'application v4)

Vérifié le 2026-06-20 sur un **LibreOffice headless jetable** (son propre
profil `UserInstallation` + port 2003, arrêté via son propre socket — la
session de l'utilisateur n'a jamais été touchée, conformément aux règles de
sécurité). Masquer `GalleryDeck` a retiré l'entrée `WriterVariants` de son
`ContextList` (`shows_in_writer` → False) et la restauration a rendu la liste
identique, octet pour octet. Les **libellés** de menu ont été vérifiés au
cours du même essai : 11/11 menus principaux et 553/553 éléments de menu
résolvent de vrais noms via `UICommandDescription`.

L'essai a aussi **découvert un bogue** : `setPropertyValue("ContextList", tuple(...))`
levait « inappropriate property value » — le gestionnaire de configuration a
besoin d'une séquence de chaînes explicitement typée. `_set_context_list` a été
corrigée pour passer `uno.Any("[]string", ...)` via `uno.invoke` (le même
idiome que l'adaptateur de barre de menus). C'est exactement le genre de
défaut que la vérification headless est censée détecter.

Détails de conception :

`src/louim/adapters/writer/sidebar.py` masque/affiche des volets entiers de la
barre latérale (Propriétés, Styles, Galerie, Navigateur, …), à l'image
d'addons.py : un volet apparaît dans Writer quand son `ContextList` (sous
`org.openoffice.Office.UI.Sidebar/Content/DeckList/<deckId>`) contient une
entrée Writer ; LOUIM retire les entrées Writer (en sauvegardant l'original
dans `louim-sidebar-state.json`) pour le masquer, et les réécrit pour
restaurer. La nouvelle section `sidebar` d'un modèle fait correspondre un
identifiant de volet à un booléen.

- `discover_sidebar_decks` / `sidebar_visibility` lisent les volets actifs ;
  reliés à l'application/restauration de l'extension, aux deux outils de
  développement, à l'exportateur, au chargeur, et à `docs/template-format.md`.
- La logique d'analyse/édition de `ContextList` (`shows_in_writer`,
  `strip_writer`, avec un repli "any" → applications non-Writer) est en
  **Python pur** (sidebar.py importe `uno` paresseusement), donc elle est
  testée unitairement en CI : 33 tests passent (12 nouveaux).

La conception a été établie **hors ligne** en lisant les définitions de volets
installées dans `share/registry/main.xcd` (identifiants de volets + format de
`ContextList`) — aucun LibreOffice en service n'a été touché, conformément aux
règles de sécurité. **Pas encore vérifié via l'interface graphique** ; l'application
a besoin d'être confirmée sur un Writer réel ou jetable (voir tâche 2).

## Fait — Masquage d'éléments de sous-menu (moteur d'application v3)

`apply_menu_profile` masque désormais des commandes à **n'importe quelle
profondeur**, pas seulement les menus principaux. La carte `menus` d'un
modèle peut lister un élément individuel (`.uno:InsertPagebreak`) ou une
entrée profonde de sous-menu, et il est retiré ; un menu masqué retire
toujours tout ce qu'il contient. La forme de la carte `menus` est inchangée
(commande → booléen), donc le chargeur et les modèles existants n'ont pas
besoin de changer.

Mécanisme (validé en direct avant l'écriture du code, puis de bout en bout) :

- Réinitialiser à la barre de menus d'usine (`removeSettings`), puis prendre
  un **clone modifiable** via `getSettings(MENUBAR, True)` — qui produit
  l'arbre par défaut complet avec des `ItemDescriptorContainer` imbriqués
  modifiables uniquement parce qu'on a réinitialisé d'abord (sinon il ne
  renvoie que la couche de personnalisation).
- `_prune_hidden` parcourt l'arbre en profondeur d'abord et fait
  `removeByIndex` sur chaque entrée dont la commande est marquée `False` (en
  retirant par ordre d'index décroissant pour que les indices restants ne se
  décalent pas), en récursant dans les sous-menus des entrées survivantes.
- `replaceSettings` + `store`. Non cumulatif, comme le comportement des menus
  principaux qu'il remplace — l'ancien chemin construction-depuis-le-défaut-
  puis-createSettings a disparu, et `menubar.py` n'importe plus `uno` (donc la
  logique d'élagage est testée unitairement en CI).

Découverte : la nouvelle `discover_menu_items(ctx)` renvoie l'arbre complet
des menus sous forme de liste plate avec `command`/`label`/`path`/`depth`
(553 commandes dans Writer) ; exposée via `tools/discover-menus.py --tree`
afin que les enseignants puissent trouver l'identifiant UNO de n'importe quel
élément. Documentation mise à jour. Tests : 21 passent (6 nouveaux tests
d'élagage avec conteneurs factices).

**Vérifié en direct** contre un Writer en service : masquer
`.uno:InsertPagebreak` fait passer Insertion de 34 à 33 éléments avec le menu
et les 10 autres menus principaux intacts ; un profil vide réinitialise (le
saut de page revient) ; masquer un menu principal et un élément imbriqué
ensemble fonctionne ; la restauration ramène les 11 menus complets.

## Fait — Export de modèle + Dessin activé en level-1 (moteur d'application v2.1)

Trois changements motivés par les retours de terrain :

- **La barre d'outils Dessin s'affiche en level-1.** L'application des barres
  d'outils est désormais **non cumulative** (annule d'abord les précédents
  changements de barre d'outils de LOUIM, comme la barre de menus) avec une
  sémantique de forçage honnête : `true` affiche une barre d'outils (même une
  masquée par défaut, par ex. Dessin), `false` la masque, `toolbars` vide
  (writer-full) réinitialise aux préférences de l'utilisateur. Remplace la
  règle précédente « true ne force jamais », qui ne pouvait pas satisfaire
  « afficher Dessin pour les débutants ». Les modèles fournis ne gèrent que
  les barres d'outils basculables ordinaires ; lister une barre *contextuelle*
  (`tableobjectbar`) comme `true` l'épinglerait ouverte — documenté dans
  `docs/template-format.md`.
- **Export / créer ses propres modèles.** Nouveau
  `src/louim/template/saver.py` (`assemble_template`, `save_template`,
  `build_current_template`) qui capture l'interface active dans un `.louim`.
  Instantanés de visibilité ajoutés à chaque adaptateur (`menu_visibility`,
  `toolbar_visibility`, `addon_visibility`). Nouveau point d'entrée
  d'extension `export_template` + menu « Save Current Layout as Template... »
  (`extension/Addons.xcu`), plus `tools/export-template.py`. Les modèles sont
  du JSON brut, modifiable dans n'importe quel éditeur de texte (section de
  documentation ajoutée).
- Tests : 15 passent (suite d'aller-retour de sauvegarde ajoutée).

**Vérifié en direct** contre un Writer en service (`tools/_verify_tmp.py`,
jetable) : l'application des menus en masque 7 et en garde 4, et la
restauration ramène les 11 ; les barres d'outils level-1 forcent Dessin
**activé** (était désactivé) et masquent Rechercher, et writer-full +
restauration donnent un solde net nul ; l'export capture 11 menus + 58 barres
d'outils, enregistre, et se recharge proprement via le chargeur. Le chemin
d'application/restauration des menus est donc désormais aussi vérifié en
direct (auparavant uniquement en headless via le fournisseur de scripts).

## Fait — Masquage/restauration de barres d'outils (moteur d'application v2)

`src/louim/adapters/writer/toolbars.py` étend le moteur au-delà de la barre
de menus jusqu'aux barres d'outils entières, en suivant le schéma
d'addons.py (nœud de configuration + fichier d'état dans le profil
utilisateur, restaurable après redémarrage) :

- `discover_toolbars(ctx)` — liste les barres d'outils Writer sous la forme
  `{"resource": "private:resource/toolbar/standardbar", "label": "Standard"}`
  via `getUIElementsInfo(TOOLBAR)` de la configuration UI du module.
- `apply_toolbar_profile(ctx, toolbars)` — pour chaque URL de ressource
  marquée `false`, met `Visible=false` dans
  `org.openoffice.Office.UI.WriterWindowState/UIElements/States`, en créant
  l'élément d'état si Writer n'en avait jamais enregistré un. Sauvegarde
  l'état d'avant LOUIM (`Visible` d'origine, ou « n'existait pas ») dans
  `louim-toolbar-state.json`.
- `restore_toolbars(ctx)` — rejoue l'état sauvegardé exactement, y compris en
  supprimant un élément que LOUIM avait dû créer.

Relié à `extension.py` (apply_template / restore_menus) et aux deux outils de
développement (`discover-menus.py`, `apply-template.py`). La section
`toolbars` d'un modèle est désormais validée par le chargeur et documentée
dans `docs/template-format.md`. Tests : 10 passent (validation de la section
barre d'outils ajoutée). La construction intègre l'adaptateur dans
`dist/louim.oxt`.

**Vérifié en direct** contre un Writer en service (`tools/verify-toolbars.py`) :
masquer `standardbar`/`colorbar` bascule le drapeau `Visible` persisté et la
restauration reproduit exactement l'état d'origine pour les deux. Réserve :
les deux barres d'outils testées avaient déjà une entrée d'état de fenêtre,
donc seul le chemin de *mise à jour* est vérifié en direct ; le chemin de
*création puis suppression* (sans entrée préalable) est couvert dans le code
mais pas encore exercé contre une instance en service.

Les vraies URL de ressource de barre d'outils Writer ont été confirmées par la
découverte (les libellés reviennent vides lors d'une découverte sans cadre de
document ouvert — une lacune uniquement d'affichage, les identifiants sont
corrects). Courantes pour les profils : `standardbar` (Standard),
`textobjectbar` (Formatage), `findbar` (Rechercher), `tableobjectbar`
(Tableau), `insertbar` (Insertion), `drawbar` (Dessin).

### Les modèles de départ portent désormais des entrées de barre d'outils

Les trois modèles fournis partagent les six mêmes clés de barre d'outils avec
des valeurs adaptées à chaque niveau : level-1 masque Rechercher/Insertion/
Tableau/Dessin (garde Standard + Formatage), level-2 réaffiche Insertion/
Tableau/Rechercher (masque toujours Dessin), writer-full affiche tout.
Partager le même jeu de clés signifie que passer à un profil plus léger
démasque ce qu'un profil plus lourd avait masqué, puisque les applications de
barre d'outils sont cumulatives via le fichier d'état (contrairement aux
menus, qui se reconstruisent depuis le défaut d'usine à chaque application).

Une correction de sémantique s'est révélée nécessaire : une entrée de barre
d'outils `true` ne fait désormais que *démasquer* une barre d'outils
précédemment masquée par LOUIM — elle ne force plus `Visible=true`, ce qui
aurait épinglé une barre contextuelle (Tableau, Dessin) ouverte en dehors de
son contexte. Cela correspond à addons.py.

Vérifié de bout en bout en direct contre un Writer en service : appliquer
level-1 puis writer-full renvoie chaque barre d'outils à son état d'origine
exact (solde net nul), et une barre d'outils masquée *avant* que LOUIM
n'intervienne reste masquée malgré une entrée `true` (pas de forçage
d'affichage).

## Fait — Moteur d'application relié à l'interface de l'extension

Le menu « LibreOffice UI Manager » pilote désormais le moteur directement
(sans socket ni outil de développement) :

- `apply_template` (`src/louim/extension.py`) — ouvre un sélecteur de fichier
  pour un `.louim`, le charge et le valide via le Gestionnaire de modèles,
  puis appelle `apply_menu_profile` + `apply_addon_profile`. Rapporte ce qui a
  été masqué.
- `restore_menus` — appelle `restore_default_menus` + `restore_addon_menus`.
- Entrées de menu ajoutées à `extension/Addons.xcu` : « Apply Template... »,
  « Restore Full Menus », un séparateur, et l'entrée existante
  « Hello LOUIM ».
- `extension.py` ajoute `python/` à `sys.path` afin que le paquet `louim`
  intégré s'importe de la même façon que pour les outils de développement et
  les tests.

Construit et empaqueté proprement (`python tools/build.py` → `dist/louim.oxt`
contient les points d'entrée et les trois modèles de départ) ; les tests du
chargeur passent toujours. Pas encore vérifié via l'interface graphique
(pas d'affichage dans cet environnement) — voir tâche 1.

Le sélecteur de fichier filtre par *emplacement*, pas par motif de nom de
fichier : les modèles de départ intégrés vivent dans des sous-dossiers par
application (`templates/writer/`, `templates/calc/`, …) et le sélecteur
s'ouvre directement dans le sous-dossier de l'application active
(`_templates_dir_url`), donc par exemple Writer n'affiche que les modèles
Writer. Ceci utilise le `FilePicker` **natif** parce que (a) la boîte de
dialogue native filtre fiablement par dossier mais ignore silencieusement les
motifs génériques par préfixe comme `writer-*.louim`, et (b) l'`OfficeFilePicker`
capable de motifs génériques rencontre un défaut d'affichage de liste sous
Skia sur un Linux verrouillé (les noms de fichiers ne s'affichent pas à des
largeurs plus grandes) et les enseignants dans ce cas ne peuvent pas changer
le comportement par défaut. L'emplacement déployé se résout via le
`PackageInformationProvider` (`_package_url`, partagé avec
`_ensure_package_path`) ; au mieux, en repliant vers la racine des modèles
puis vers le dernier emplacement du sélecteur si un dossier ne peut pas être
résolu.

La boîte de dialogue **Enregistrer** se place ailleurs par défaut : dans
`<Mes documents>/LOUIM templates` (`_documents_save_url`, via la substitution
de chemin `$(work)`, créé au premier usage). Les modèles créés par les
enseignants doivent persister, et le cache d'extension par utilisateur est
vidé à chaque réinstallation/mise à jour — donc enregistrer là-bas les
perdrait silencieusement.

## État du moteur (vérifié en headless)

- **Moteur de découverte v0** — `src/louim/adapters/writer/menubar.py`
  `discover_top_level_menus(ctx)` lit les menus principaux actifs de Writer
  comme identifiants de commande UNO. Outil de développement :
  `tools/discover-menus.py`.
- **Gestionnaire de modèles (chargement)** — `src/louim/template/loader.py`
  `load_template(path)` analyse et valide les fichiers `.louim`. Testé
  unitairement en CI.
- **Moteur d'application v0** — même adaptateur : `apply_menu_profile(ctx, menus)`
  masque les menus principaux qu'un modèle marque `false` (toujours dérivé du
  défaut d'usine, donc idempotent), et `restore_default_menus(ctx)` revient à
  la barre de menus complète intégrée. Outil de développement :
  `tools/apply-template.py`.

  Vérifié : appliquer `writer-level-1.louim` réduit la barre de menus de
  Writer exactement à Fichier/Édition/Format/Aide, et la restauration ramène
  les 11 menus, laissant le profil propre.

- **Moteur d'application v1 (menus d'extension)** —
  `src/louim/adapters/writer/addons.py` gère les menus apportés par
  *d'autres* extensions (par ex. Dmaths), qui sont fusionnés séparément de la
  barre de menus intégrée et repérés par nom de nœud de configuration dans la
  section `addons` d'un modèle. `apply_addon_profile` les masque en retirant
  Writer du `Context` de chaque menu d'extension (en sauvegardant l'original
  dans un fichier d'état du profil utilisateur) ; `restore_addon_menus`
  réécrit les originaux. Prend effet pour les fenêtres Writer nouvellement
  ouvertes. Vérifié dans l'interface graphique : Dmaths se masque et se
  restaure. Le menu propre de LOUIM est toujours exclu.

  Remarque : les changements de menu d'extension persistent via
  `commitChanges()` de la configuration ; un LibreOffice en service normal les
  écrit sur disque. (Tuer brutalement une instance headless juste après un
  commit peut perdre la dernière écriture — pertinent seulement pour les
  bancs de test.)

## Correction connue

Le menu propre de l'extension ne s'affichait pas car son entrée `Addons.xcu`
n'avait pas de `Context`. Les versions récentes de LibreOffice en exigent un
pour les menus d'extension de premier niveau. Corrigé en liant le menu LOUIM
aux modules de document Writer. Confirmé dans l'interface graphique : le menu
« LibreOffice UI Manager » s'affiche et « Hello LOUIM » ouvre la boîte de
dialogue.

## Invite de reprise

Continuer LOUIM à partir de PROJECT.md (ou de sa traduction, PROJECT.fr.md).
