# Moteur de découverte

*Traduction française de [discovery-engine.md](discovery-engine.md).*

Le principe 4 de la [constitution du projet](project-constitution.md) (non
traduite) exige que LOUIM découvre l'interface active de LibreOffice plutôt
que de travailler à partir d'une liste codée en dur. Un arbre de menus figé
se périme au fil des versions et des langues de LibreOffice, et il ne peut
pas voir ce qu'une extension ou la propre personnalisation d'un enseignant a
ajouté. Il n'existe pas de classe unique `DiscoveryEngine` pour cela. La
« découverte » est une fonction `discover_*` dans chaque adaptateur, et elles
suivent toutes la même forme. Ce document les recense, et sert aussi de
référence pour `tools/discover-menus.py`.

## Le modèle général

Chaque fonction `discover_*` lit la configuration active de LibreOffice,
jamais une table intégrée. Elle renvoie des identifiants indépendants de la
langue, identifiants de commande UNO, URL de ressource de barre d'outils,
identifiants de volet, ou noms de nœud de menu d'extension, comme clé
principale, et associe un libellé lisible résolu séparément, uniquement pour
l'affichage. Les libellés ne sont jamais persistés dans un modèle `.louim` ;
voir [ui-element-model.fr.md](ui-element-model.fr.md). Chaque fonction prend
un contexte de composant UNO (`ctx`) et un `module` optionnel, `WRITER` par
défaut, afin que la même fonction fonctionne depuis l'intérieur de
l'extension (`XSCRIPTCONTEXT.getComponentContext()`) ou depuis une connexion
socket externe utilisée par les outils de développement et les tests.

## Ce que découvre chaque adaptateur

`discover_top_level_menus(ctx, module)`, dans `menubar.py`, renvoie les menus
principaux du module dans l'ordre de la barre de menus.

`discover_menu_items(ctx, module)`, aussi dans `menubar.py`, renvoie l'arbre
imbriqué complet : chaque élément de menu à chaque profondeur, avec un
`path` donnant la chaîne des parents et un `depth`. Elle lit depuis le défaut
d'usine, donc elle montre l'arbre complet quelle que soit la personnalisation
actuelle. C'est ainsi qu'on trouve l'identifiant UNO d'un élément qu'on
souhaite masquer.

`discover_toolbars(ctx, module)`, dans `toolbars.py`, renvoie les barres
d'outils du module via `getUIElementsInfo(TOOLBAR)`.

`discover_sidebar_decks(ctx, module)`, dans `sidebar.py`, renvoie les volets
de la barre latérale dont le `ContextList` les affiche dans ce module.

`discover_addon_menus(ctx, module)`, dans `addons.py`, renvoie les menus
principaux apportés par des extensions visibles dans ce module, en excluant
le menu propre à LOUIM.

Il n'existe pas de fonction `discover_toolbar_items`. Le masquage des
boutons de barre d'outils (`toolbaritems.py`) réutilise `discover_toolbars`
pour déterminer quelles barres d'outils inspecter, puis parcourt directement
le conteneur de configuration de chacune (`_collect_commands`) quand elle a
besoin de la liste complète des commandes.

## Résolution des libellés

La configuration UI de la barre de menus laisse généralement le `Label`
d'une entrée vide. LibreOffice résout le texte affiché au moment du rendu,
et le fait encore plus systématiquement quand aucun cadre de document n'est
ouvert, exactement la situation dans laquelle tournent les outils de
développement en mode headless. `menubar._command_labels` interroge
directement le service `UICommandDescription`, indexé par le service
document du module, pour obtenir de vrais libellés corrects dans la bonne
langue même sans rien d'ouvert. `_label_for` préfère le `Label` propre à une
entrée quand il est présent et se rabat sur cette recherche sinon, en
retirant les marqueurs mnémotechniques comme `~`. Ceci a été vérifié contre
une instance en service sans aucun document ouvert : 11 menus principaux sur
11 et 553 éléments de menu sur 553 ont résolu de vrais noms.

## L'export, c'est de la découverte plus une comparaison de visibilité

Une fonction `*_visibility` dans chaque adaptateur s'appuie sur sa fonction
de découverte pour répondre à une question différente : à quoi ressemble
l'interface actuelle, éventuellement personnalisée à la main, sous forme de
modèle ? Elle compare l'état actuel au défaut d'usine et renvoie la même
forme identifiant-vers-booléen qu'utilise un fichier `.louim`.
`saver.build_current_template` appelle les cinq fonctions `*_visibility` et
assemble le résultat. C'est ce qui s'exécute quand un enseignant clique sur
« Enregistrer la disposition comme modèle... ».

## Outil de développement

`tools/discover-menus.py [--tree]` se connecte à une instance headless
jetable (voir les règles de sécurité dans [CLAUDE.md](../CLAUDE.md), non
traduit) et affiche les menus, les barres d'outils et les menus d'extension
avec leurs identifiants UNO. Avec `--tree`, il affiche aussi l'arbre complet
des menus imbriqués. C'est le moyen pratique de trouver un identifiant à
mettre dans un modèle.
