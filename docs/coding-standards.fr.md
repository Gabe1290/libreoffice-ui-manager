# Normes de codage

*Traduction française de [coding-standards.md](coding-standards.md).*

Ces conventions décrivent ce que `src/louim/` fait réellement. Ce n'est pas
un guide de style aspirationnel. Si vous trouvez du code qui ne correspond
pas à l'une d'elles, c'est probablement un bogue à corriger plutôt qu'une
autorisation d'ignorer la règle.

## Imports `uno` paresseux

Les modules d'adaptateur n'importent pas `uno` ni `unohelper` au niveau du
module. Chaque fonction qui a réellement besoin d'une structure ou d'un
appel UNO l'importe localement :

```python
def _make_nodepath_arg(node):
    import uno
    arg = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
    ...
```

Cela garde la logique pure du même fichier, analyse, édition de listes et de
chaînes, élagage d'arbre, importable et testable unitairement sans qu'une
installation de LibreOffice soit présente. `tests/test_uno_imports.py`
impose cela de façon statique. Il parcourt chaque fonction dans `src/` et
échoue si `uno` ou `unohelper` est référencé sans import accessible dans la
portée de cette fonction, que ce soit au niveau du module ou localement.

Ce test existe à cause d'un vrai bogue. En v4.2.2, `addons.state_path`
utilisait `uno.fileUrlToSystemPath` après qu'un refactoring vers les imports
paresseux ait fait disparaître l'import de premier niveau ailleurs dans le
fichier. La suite de tests hors ligne passait quand même, puisque rien
n'exerçait ce chemin de code sans instance en service, et le code levait
`NameError` dès qu'il s'exécutait réellement.

## Gestion des exceptions : large seulement à la frontière avec la colle

`except Exception` apparaît à deux endroits, délibérément. Le premier est
les lectures individuelles de propriété ou de configuration UNO à
l'intérieur des adaptateurs, où une propriété manquante ou une ressource
inconnue devrait ignorer cet élément plutôt que d'interrompre toute une
passe de découverte ou d'application sur de nombreux éléments. Le second est
`extension.py`, la couche la plus externe, où une exception non capturée
surgirait sinon comme une boîte de dialogue d'erreur cryptique de
LibreOffice plutôt que le message propre de LOUIM.

Partout ailleurs, `template/loader.py`, `template/saver.py`, et les
fonctions d'assistance pures à l'intérieur des adaptateurs, les exceptions
se propagent. Les tests les capturent directement, par exemple
`TemplateError` depuis `load_template`. Les avaler à cet endroit ne ferait
que cacher de vrais bogues derrière des non-opérations silencieuses.

## Les docstrings de niveau module expliquent le raisonnement, pas la mécanique

Chaque module d'adaptateur s'ouvre sur un bloc de commentaires qui donne le
raisonnement dont un lecteur a besoin avant que le code ne prenne son sens :
quel nœud de configuration est modifié et pourquoi, ce qui est partagé
contre ce qui est propre à une application, pourquoi tel idiome UNO
particulier est nécessaire. Regardez le début de `sidebar.py` ou
`addons.py` pour ce modèle. Les docstrings de fonction suivent la même règle
à plus petite échelle. Elles expliquent un comportement non évident, comme
pourquoi une valeur de retour se combine plutôt que d'écraser, ou pourquoi
une opération doit être non cumulative, plutôt que de paraphraser la
signature de la fonction. Une fonction dont la docstring ne ferait que
répéter son nom et ses arguments n'en a probablement pas besoin.

## Application non cumulative, toujours

Chaque fonction `apply_*` se réinitialise à un état de référence connu avant
d'appliquer le profil actuel. Pour les menus, les barres d'outils et les
boutons de barre d'outils, cette référence est le défaut d'usine ; pour la
barre latérale et les menus d'extension, c'est l'état d'avant LOUIM (voir
ui-element-model.md pour savoir lequel s'applique où). Appliquer le modèle A
puis le modèle B donne toujours exactement B. Cela ne laisse jamais les
restes de A mélangés à B. C'est un invariant strict. Un nouvel adaptateur
qui empile des changements au lieu de réinitialiser d'abord est un bogue,
quelle que soit la façon dont il est testé.

## Fichiers d'état : un par surface, par module

Chaque fonction `restore_*` d'un adaptateur revient en arrière à l'aide d'un
fichier d'état JSON privé dans le profil utilisateur,
`louim-<surface>-state-<app>.json`, plutôt qu'en déduisant l'annulation à
partir du modèle actuel. C'est ce qui fait fonctionner Restaurer quel que
soit le modèle appliqué en dernier, le cas échéant, et c'est ce qui permet à
la barre latérale et aux menus d'extension de se combiner correctement quand
deux `Module` différents ont tous deux touché la même valeur de
configuration partagée. Voir `sidebar._restore_context_list` et
`addons._restore_context` pour ce modèle : une annulation exacte quand rien
d'autre n'a changé la valeur depuis, et un réajout compositionnel sinon.

## La logique pure est testée unitairement avec des conteneurs factices

La logique récursive de parcours d'arbre, comme `menubar._prune_hidden`,
`_collect_command_set`, et `_export_walk`, est testée contre de petits
objets factices construits à la main qui imitent la tranche pertinente de
l'interface de conteneur UNO : `getCount`, `getByIndex`, `removeByIndex`.
Aucune instance LibreOffice en service n'est jamais impliquée.
`tests/test_menubar_prune.py` montre ce modèle. C'est pourquoi toute la
suite de tests s'exécute en bien moins d'une seconde sans aucun LibreOffice
installé à proximité.

## Les identifiants portent la logique ; les libellés ne servent qu'à l'affichage

Chaque comparaison, chaque clé de dictionnaire, chaque champ de modèle
utilise un identifiant de commande UNO, une URL de ressource de barre
d'outils, un identifiant de volet, ou un nom de nœud de menu d'extension.
Les libellés n'existent que pour les outils de développement et la boîte de
dialogue Configurer les menus, pour montrer à un humain quelque chose de
lisible. Voir [ADR 0001](adr/0001-use-uno-command-ids.fr.md).

## `module=WRITER` comme valeur par défaut

Chaque signature de fonction d'adaptateur prend `module`, avec `WRITER` par
défaut. Ce n'est pas parce que Writer serait spécial sur le plan
architectural. C'est parce que Writer a été la première application prise
en charge, et les sites d'appel existants, y compris les outils de
développement, précèdent la prise en charge multi-applications. Le nouveau
code devrait toujours accepter `module` explicitement plutôt que de supposer
Writer. La valeur par défaut `WRITER` existe pour la compatibilité
ascendante avec les sites d'appel d'avant la v2.0, pas comme modèle à
copier.
