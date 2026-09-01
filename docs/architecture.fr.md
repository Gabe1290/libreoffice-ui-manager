# Architecture

*Traduction française de [architecture.md](architecture.md).*

Ce document décrit l'architecture telle que livrée en v4.3.0, pas le plan
initial dans [project-constitution.md](project-constitution.md) (non traduit).
Construire le vrai système a simplifié l'organisation en couches
Modèle/Moteur/Interface d'origine. Les [ADR](adr/) expliquent pourquoi chaque
simplification a eu lieu.

## Vue d'ensemble

LOUIM n'a pas d'objet « moteur central » et pas de modèle interne persistant.
Un petit ensemble de modules adaptateurs, un par surface d'interface,
communiquent directement avec la configuration propre de LibreOffice : la
barre de menus, les barres d'outils, les boutons de barre d'outils, les
volets de la barre latérale, et les menus d'extension. Chaque fonction
d'adaptateur est paramétrée par un descripteur `Module`
(`src/louim/adapters/modules.py`) au lieu d'être dupliquée par application,
de sorte qu'un seul chemin de code pilote Writer, Calc, Impress et Draw. Les
modèles sont le seul modèle persistant. Ce sont de simples dictionnaires
JSON, validés au chargement et assemblés à l'enregistrement ; il n'y a pas de
classe « Profil » en mémoire derrière eux. `extension.py` est le seul
endroit qui parle à la fois au cadre de script de LibreOffice et aux
adaptateurs, et il reste mince : de la colle pour points d'entrée, pas une
couche de logique métier.

## Composants principaux

### `src/louim/adapters/modules.py` — le descripteur `Module`

Un `Module` regroupe la poignée d'identifiants qui diffèrent entre les
applications LibreOffice : le nom du service document, le nœud de
configuration d'état de fenêtre, les noms de groupe d'application `ContextList`
de la barre latérale, et les noms de service `Context` des menus d'extension.
`WRITER`, `CALC`, `IMPRESS` et `DRAW` sont les quatre instances. `MODULES`
fait correspondre les chaînes `"application"` des modèles à ces instances, et
`module_for_document(doc)` choisit la bonne pour la fenêtre active via
`supportsService`. Ce fichier est purement des données, sans import `uno`,
donc il est importable et testé unitairement sans LibreOffice.

### `src/louim/adapters/writer/` — les adaptateurs

Le nom du paquet est historique (Writer était la seule application en v1).
Chaque fonction ici prend un paramètre `module`, `WRITER` par défaut, et
fonctionne pour n'importe quelle application.

`menubar.py` gère la barre de menus elle-même :
`private:resource/menubar/menubar` dans la configuration UI du module. Elle
découvre les menus principaux et l'arbre complet des éléments imbriqués.
Appliquer un profil de visibilité réinitialise à la configuration d'usine,
puis retire récursivement chaque commande marquée `false` à n'importe quelle
profondeur (`_prune_hidden`). Elle applique aussi `PROTECTED_MENUS`, Fichier,
Édition et Aide, de sorte qu'un profil ne puisse jamais retirer le menu
d'ancrage propre à LOUIM. `toolbaritems.py` réutilise cette logique
d'élagage, puisque les listes de boutons de barre d'outils vivent dans le
même type de conteneur de configuration.

`toolbars.py` gère la visibilité de barres d'outils entières via la
configuration `org.openoffice.Office.UI.<Module>WindowState/UIElements/States`.
C'est un mécanisme différent de la barre de menus : un drapeau `Visible` par
URL de ressource de barre d'outils plutôt qu'un arbre à élaguer.

`toolbaritems.py` masque des boutons individuels à l'intérieur des barres
d'outils.

`sidebar.py` gère les volets de la barre latérale comme Propriétés, Styles et
Galerie, via le `ContextList` de chaque volet sous
`org.openoffice.Office.UI.Sidebar/Content/DeckList`. La logique d'édition de
liste (`shows_in_module`, `strip_module`, `merge_context_list`) est
indépendante d'`uno` et testée unitairement. Le `ContextList` d'un volet est
une configuration partagée, donc la restauration se combine avec ce qu'un
autre `Module` a pu changer entre-temps au lieu de l'écraser purement et
simplement.

`addons.py` gère les menus apportés par d'autres extensions, fusionnés
séparément de la barre de menus intégrée via
`org.openoffice.Office.Addons/AddonUI/OfficeMenuBar` et sa propriété
`Context`. Elle suit la même approche de restauration compositionnelle que
`sidebar.py`, pour la même raison : `Context` est aussi une configuration
partagée.

Chaque adaptateur suit à peu près la même forme. Une fonction pure de
découverte ou d'instantané n'a pas besoin d'`uno` pour tester sa logique.
Une fonction d'application est non cumulative, toujours reconstruite depuis
le défaut d'usine ou l'état d'avant LOUIM plutôt qu'empilée sur la dernière
application. Une fonction de restauration revient en arrière à l'aide d'un
fichier d'état JSON par module dans le profil utilisateur
(`louim-<surface>-state-<app>.json`).

### `src/louim/template/` — le Gestionnaire de modèles

Python pur, aucun import `uno` nulle part dans ce paquet. `loader.py` analyse
et valide un fichier `.louim` : vérifie la forme JSON, vérifie `version` face
à `TEMPLATE_VERSION` (rejette tout ce qui est plus récent que ce que ce
LOUIM prend en charge), vérifie `application` face à
`SUPPORTED_APPLICATIONS`, et vérifie que chaque section de visibilité est une
simple correspondance chaîne vers booléen. `saver.py` en est le miroir.
`assemble_template` construit le dictionnaire du modèle à partir des cartes
de visibilité, `build_current_template` appelle la fonction d'instantané de
chaque adaptateur pour un module donné et assemble le résultat, et
`save_template` écrit du JSON formaté.

### `src/louim/extension.py` — la colle des points d'entrée

Ce module expose `g_exportedScripts` pour le fournisseur de scripts de
LibreOffice : sélecteurs de fichiers, boîtes de messages, et les commandes
d'application/restauration/export reliées à
`org.louim.libreoffice-ui-manager.menu` dans `extension/Addons.xcu`. Il
dirige selon `module_for_document(doc)`, de sorte que les mêmes entrées de
menu fonctionnent dans chacune des quatre applications. C'est la seule couche
qui capture `Exception` de façon large. Tout ce qui est en dessous laisse les
erreurs se propager afin que les tests puissent les capturer.

### `src/louim/ui/menu_picker.py` — la boîte de dialogue Configurer les menus

Construit une boîte de dialogue avec une case à cocher par menu, à
l'exécution, à partir de `UnoControlDialogModel`, en tirant les libellés de
`UICommandDescription` pour qu'ils correspondent à la langue de LibreOffice
de l'utilisateur. `menubar.top_level_choices()` fournit la liste depuis le
défaut d'usine, de sorte qu'un menu déjà masqué par LOUIM apparaît toujours
et peut être rétabli. `menubar.merge_top_level_choices()` superpose les choix
de la boîte de dialogue à un instantané `menu_visibility()` complet sans
faire réapparaître les éléments qui avaient été masqués individuellement.

### `src/louim/i18n.py`

Une fonction pure `translator(lang)` sur des tables de chaînes pour
l'anglais, le français, l'allemand et l'italien, avec un repli sur l'anglais
et une cohérence du nombre de paramètres `%` imposée par les tests entre les
langues. `office_language(ctx)` lit la langue d'interface active de
LibreOffice pour choisir quelle table utiliser.

## Comment un modèle traverse le système

La découverte lit l'interface active et renvoie des identifiants
indépendants de la langue. L'export capture l'état actuel sous forme de
cartes identifiant-vers-booléen et les assemble dans un dictionnaire de
modèle, que `extension.export_template` écrit via un sélecteur de fichier.
Le chargement analyse et valide un fichier `.louim` dans cette même forme de
dictionnaire. L'application appelle la fonction `apply_*` de chaque
adaptateur avec la section correspondante du modèle ; chaque application est
non cumulative, donc appliquer deux modèles de suite ne les empile jamais,
le second l'emporte purement et simplement. La restauration revient en
arrière pour chaque surface à l'aide de son propre fichier d'état,
indépendamment du modèle appliqué en dernier.

## Ce qui a changé par rapport à la conception initiale

La constitution du projet (principe 5) envisageait trois couches : Modèle
(Workspace, Profile, UIElement), Moteur (moteur de découverte, gestionnaire
de modèles, moteur d'application), et Interface, avec un moteur central qui
ne touche jamais LibreOffice directement. En pratique, il n'y a pas d'objet
`Workspace` (voir [ADR 0004](adr/0004-workspace-concept.fr.md)) ni de classe
`UIElement` unifiée couvrant les menus, les barres d'outils, les boutons de
barre d'outils, les volets de la barre latérale et les menus d'extension
(voir [ADR 0003](adr/0003-ui-element-model.fr.md)). Il n'y a pas non plus de
moteur central séparé ; `extension.py` appelle les adaptateurs directement.
L'isolement voulu par la constitution est obtenu d'une autre façon : chaque
adaptateur garde son import `uno` paresseux, donc la logique pure (analyse,
validation, édition de listes, élagage) est testée unitairement sans
LibreOffice, et seuls les corps de fonction minces qui appellent les API UNO
ont besoin d'une instance en service.

Le moteur de découverte et le moteur d'application que nomme la constitution
existent bel et bien. Ils vivent simplement comme des fonctions réparties
entre les adaptateurs, une paire découverte/application par surface, plutôt
que comme des classes autonomes. Voir
[discovery-engine.fr.md](discovery-engine.fr.md) et
[ui-element-model.fr.md](ui-element-model.fr.md).
