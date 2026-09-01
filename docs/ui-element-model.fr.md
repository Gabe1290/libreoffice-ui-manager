# Modèle des éléments d'interface

*Traduction française de [ui-element-model.md](ui-element-model.md).*

Voici comment LOUIM représente les éléments d'interface qu'il peut masquer et
afficher. Il n'existe pas de classe `UIElement` partagée (voir
[ADR 0003](adr/0003-ui-element-model.fr.md) pour savoir pourquoi), donc plutôt
que de documenter un seul type, ceci est une carte des cinq types d'élément.

Chaque type partage trois choses : un identifiant indépendant de la langue,
une visibilité booléenne, et un nom de section dans le format de modèle
`.louim` (le schéma JSON complet se trouve dans
[template-format.md](template-format.md), non traduit). Ce qui diffère, c'est
où LibreOffice stocke cette visibilité et comment elle se modifie.

## Menus (`menus`)

L'identifiant est un identifiant de commande UNO, comme `.uno:InsertMenu` ou
`.uno:InsertPagebreak`. Il fonctionne de la même façon pour un menu principal
ou un élément imbriqué à n'importe quelle profondeur.

Le stockage est l'arbre de configuration de la barre de menus à
`private:resource/menubar/menubar`, dans la configuration UI du module. Les
éléments imbriqués vivent dans l'`ItemDescriptorContainer` de chaque entrée.

L'édition est non cumulative et porte sur l'arbre entier. Appliquer un profil
réinitialise la barre de menus au défaut d'usine de LibreOffice, puis retire
récursivement chaque entrée dont la commande est marquée `false`
(`menubar._prune_hidden`). Masquer un parent retire tout ce qu'il contient,
donc un modèle n'a jamais besoin de lister individuellement les enfants d'un
menu masqué. Trois commandes ne peuvent jamais être masquées : Fichier,
Édition et Aide, suivies dans `PROTECTED_MENUS` et appliquées dans
`apply_menu_profile` quoi qu'un modèle demande.

Adaptateur : `src/louim/adapters/writer/menubar.py`.

## Barres d'outils (`toolbars`)

L'identifiant est une URL de ressource de barre d'outils, comme
`private:resource/toolbar/standardbar`.

Le stockage est un booléen `Visible` par ressource dans
`org.openoffice.Office.UI.<Module>WindowState/UIElements/States`. C'est la
même configuration que Affichage ▸ Barres d'outils modifie, ce qui explique
pourquoi basculer une barre d'outils là-bas survit à un redémarrage.

L'édition est non cumulative sur l'ensemble des barres d'outils. `true`
force réellement une barre d'outils visible, même une masquée par défaut
comme Dessin. `false` la masque. Une barre d'outils laissée hors du profil
revient à l'état dans lequel elle était avant que LOUIM n'y touche. Ne
marquez pas une barre d'outils contextuelle comme `tableobjectbar` à `true`
— cela l'épinglerait ouverte en dehors du contexte qui l'afficherait
normalement.

Adaptateur : `src/louim/adapters/writer/toolbars.py`.

## Boutons de barre d'outils (`toolbaritems`)

L'identifiant est un identifiant de commande UNO, le même espace de noms que
`menus`, puisqu'un bouton de barre d'outils et une entrée de menu pour la
même fonctionnalité partagent une commande.

Le stockage est le conteneur de configuration propre à chaque barre d'outils,
le même type d'arbre qu'utilise la barre de menus. C'est pourquoi l'élagage
des boutons de barre d'outils réutilise simplement `menubar._prune_hidden`
plutôt que de le réimplémenter.

L'édition est non cumulative sur l'ensemble des barres d'outils : chaque
application réinitialise d'abord chaque barre d'outils personnalisée à sa
définition d'usine, défaisant à la fois les propres changements antérieurs de
LOUIM et tout ce qu'un enseignant a retiré à la main via Outils ▸
Personnaliser, puis retire les commandes masquées par le profil actuel.

Un indicateur au niveau du modèle, `hide_toolbar_buttons_with_menus`, fait
l'union de cette section avec ce que `menus` masque. Masquer un menu retire
aussi les boutons de barre d'outils de chaque commande imbriquée à
l'intérieur (`menubar.menu_command_descendants`), de sorte qu'un menu réduit
et une barre d'outils réduite restent synchronisés sans avoir à lister
chaque commande deux fois.

Adaptateur : `src/louim/adapters/writer/toolbaritems.py`.

## Volets de la barre latérale (`sidebar`)

L'identifiant est un identifiant de volet, comme `GalleryDeck` ou
`PropertyDeck`.

Le stockage est le `ContextList` de chaque volet sous
`org.openoffice.Office.UI.Sidebar/Content/DeckList/<deckId>`, une liste de
chaînes de la forme `"Application, Contexte, ÉtatInitial"`. Un volet s'affiche
dans une application si son `ContextList` contient une entrée pour le groupe
de cette application ou pour le mot-clé générique `"any"`.

L'édition travaille sur une liste partagée. `DeckList` n'est pas une
configuration par application, donc masquer un volet depuis Writer modifie
la même liste où vit l'entrée de Calc. Masquer un volet retire les entrées de
groupe d'application de ce module, ou réécrit `"any"` pour ne couvrir que les
autres applications. Impress et Draw partagent en plus un groupe
`"DrawImpress"`, remplacé par l'application sœur lors du masquage, de sorte
que masquer un volet depuis Impress le laisse visible dans Draw. Comme la
liste est partagée, la restauration doit être prudente : si la liste
correspond encore exactement à ce que LOUIM a écrit en dernier, la
restauration rejoue l'original intact ; si un autre module l'a modifiée
entre-temps, la restauration ne réajoute que les propres entrées de ce
module au lieu d'écraser le masquage de l'autre module.

Adaptateur : `src/louim/adapters/writer/sidebar.py`.

## Menus d'extension (`addons`)

L'identifiant est un nom de nœud de configuration d'extension, comme
`org.openoffice.Office.addon.aide`. Ce sont des menus principaux apportés par
une extension, comme Dmaths, qui ne font pas partie de la barre de menus
intégrée.

Le stockage est une propriété `Context`, une liste de noms de service
document séparés par des virgules, sur chaque nœud sous
`org.openoffice.Office.Addons/AddonUI/OfficeMenuBar`. Un `Context` vide
signifie que le menu s'affiche dans chaque module.

L'édition suit la même forme de configuration partagée et de restauration
compositionnelle que les volets de la barre latérale, et pour la même
raison : `Context` est une seule valeur couvrant chaque application. LOUIM
ne retire que les services de ce module lors du masquage, et à la
restauration rejoue soit l'original tel quel, soit ne réajoute que les
services de ce module si quelque chose d'autre a changé la valeur
entre-temps. Le nœud du menu propre à LOUIM,
`org.louim.libreoffice-ui-manager.menu`, est toujours exclu — il ne peut
jamais se masquer lui-même.

Adaptateur : `src/louim/adapters/writer/addons.py`.

## Points communs aux cinq types

La découverte est toujours en direct, jamais une table codée en dur. Voir
[discovery-engine.fr.md](discovery-engine.fr.md) et
[ADR 0002](adr/0002-discovery-engine.fr.md). Les libellés proviennent de
`UICommandDescription`, sensible à la langue, tandis que les identifiants
viennent directement de la configuration propre de LibreOffice.

Un fichier d'état par surface, par module, vit dans le profil utilisateur
(`louim-<surface>-state-<app>.json`) et enregistre ce qu'il faut pour défaire
exactement ce que LOUIM a changé, indépendamment du modèle appliqué en
dernier.

Un identifiant laissé hors d'un modèle reste visible par défaut à
l'application, donc un modèle n'a besoin de nommer que ce qu'il masque.

Les libellés sont uniquement pour l'affichage. Aucun adaptateur n'écrit
jamais de libellé localisé dans un fichier `.louim` ; seul l'identifiant est
persisté. Voir le principe 3 dans
[project-constitution.md](project-constitution.md) (non traduit).
