# Guide du développeur

*Traduction française de [developer-guide.md](developer-guide.md).*

Un guide pratique pour travailler sur le code de LOUIM. Pour le raisonnement
derrière la conception, lisez [architecture.fr.md](architecture.fr.md). Pour
les conventions de style, lisez
[coding-standards.fr.md](coding-standards.fr.md). Et avant d'exécuter quoi
que ce soit contre une vraie instance de LibreOffice, lisez les règles de
sécurité dans [CLAUDE.md](../CLAUDE.md) (non traduit).

## Installation

```sh
git clone <dépôt>
cd libreoffice-ui-manager
pip install pytest
```

Il n'y a pas d'autre dépendance. Le code n'a besoin que de la bibliothèque
standard Python plus `uno`/`unohelper`, qui viennent de l'installation de
LibreOffice elle-même et ne sont importés paresseusement que là où c'est
réellement nécessaire (voir la section sur les imports paresseux dans
coding-standards.fr.md).

## Exécuter la suite de tests

```sh
python -m pytest -q
```

Les quelque 110 tests s'exécutent hors ligne, sans besoin de LibreOffice.
Ils couvrent le chargement, l'enregistrement et la validation des modèles ;
les fonctions pures d'édition de listes et de chaînes de chaque adaptateur,
comme l'élagage des menus, l'édition de `ContextList`, l'édition de
`Context`, et le tri des barres d'outils ; la cohérence des clés i18n et des
paramètres `%` entre les quatre langues ; et un garde-fou statique,
`tests/test_uno_imports.py`, qui détecte un nom `uno` utilisé sans import
accessible dans la même fonction. Ce dernier point est exactement la classe
de bogue qui ne se révèle jamais qu'en direct, jamais dans un test hors
ligne autrement.

## Construire l'extension

```sh
python tools/build.py
```

Cela produit `dist/louim.oxt` avec un nom de fichier stable qui ne porte
jamais de numéro de version. La section « Résolu » de PROJECT.md explique
pourquoi cela compte pour l'URL du script. La construction exclut
`__pycache__` et `*.pyc` ; un fichier compilé périmé laissé dans le dossier
`python/` intégré peut casser le démarrage de l'extension.

Installez-la via le Gestionnaire d'extensions de LibreOffice, Outils ▸
Gestionnaire d'extensions ▸ Ajouter, contre `dist/louim.oxt`. Fermez
LibreOffice d'abord si vous réinstallez. PROJECT.md décrit le `KeyError`
qu'une réinstallation à moitié effectuée peut sinon provoquer.

## Vérification en direct

Ne jamais tester contre votre propre LibreOffice en service. Voir les règles
de sécurité dans CLAUDE.md. Utilisez les outils dans `tools/` contre une
instance headless jetable avec son propre profil `UserInstallation` :

```sh
soffice --headless --norestore \
  -env:UserInstallation=file:///tmp/louim-test-profile \
  --accept="socket,host=localhost,port=2002;urp;"
```

`tools/discover-menus.py [--tree]` liste les menus, barres d'outils et menus
d'extension avec leurs identifiants UNO ; `--tree` montre l'arbre complet des
menus imbriqués. `tools/apply-template.py <fichier.louim>` applique un
profil, ou utilisez `--restore` pour le défaire.
`tools/export-template.py <sortie.louim>` capture l'interface active.

## Ajouter une nouvelle surface d'interface

Supposons que vous ajoutiez un sixième type d'élément masquable, en suivant
le modèle dans [ui-element-model.fr.md](ui-element-model.fr.md) et
[ADR 0003](adr/0003-ui-element-model.fr.md).

Commencez par un nouveau module sous `src/louim/adapters/writer/` — le nom
du dossier est historique, il n'est pas spécifique à Writer. Importez `uno`
paresseusement, à l'intérieur des corps de fonction plutôt qu'au niveau du
module. Écrivez une fonction `discover_<surface>(ctx, module=WRITER)` qui
lit la configuration active, et une fonction d'instantané
`<surface>_visibility(ctx, module=WRITER)` pour l'export. Puis écrivez
`apply_<surface>_profile(ctx, <surface>, module=WRITER, path=None)`, non
cumulative comme chaque adaptateur existant, écrivant un fichier d'état via
un assistant `state_path(ctx, module)`, et
`restore_<surface>s(ctx, module=WRITER, path=None)` pour revenir en arrière à
partir de ce fichier d'état.

Ensuite, ajoutez la nouvelle section aux appels de
`loader._validate_bool_map` dans `template/loader.py`, et à
`saver.assemble_template` et `build_current_template`. Reliez le tout aux
points d'entrée d'application, de restauration et d'export de
`extension.py`. Documentez la section dans
[template-format.md](template-format.md) (non traduit) et ajoutez une ligne
à ui-element-model.md. Testez unitairement la logique pure avec des
conteneurs factices, le modèle utilisé dans
`tests/test_menubar_prune.py`, plutôt que contre une instance en service.

## Ajouter une nouvelle application LibreOffice

Cela ne devrait nécessiter aucun changement dans la logique des adaptateurs
elle-même, selon [ADR 0004](adr/0004-workspace-concept.fr.md). Ajoutez une
nouvelle instance `Module` à `src/louim/adapters/modules.py` avec les
identifiants propres à l'application : `doc_service`, `windowstate_node`,
`deck_apps`/`other_deck_apps`, `addon_contexts`/`other_addon_contexts`, et
`deck_group_subs` si l'application partage un groupe de contexte de barre
latérale avec une autre application, comme Impress et Draw partagent
`"DrawImpress"`. Ajoutez-la à `MODULES` et à
`loader.SUPPORTED_APPLICATIONS`, puis ajoutez des modèles de départ sous
`templates/<app>/`. `module_for_document` reconnaît automatiquement la
nouvelle application via `supportsService` ; rien dans `extension.py` n'a
besoin de changer.

## Flux de travail pour l'internationalisation

Toute nouvelle chaîne visible par l'utilisateur dans `extension.py` ou
`ui/menu_picker.py` a besoin d'une clé ajoutée aux quatre tables de langue
dans `src/louim/i18n.py` (anglais, français, allemand, italien), avec des
paramètres `%` correspondants — un test impose la cohérence du nombre de
paramètres, de sorte qu'une incohérence fasse échouer la CI plutôt que de
provoquer une erreur `%` en production. Récupérez la chaîne via le
traducteur (`office_language(ctx)` puis `translator(lang)`) ; ne codez jamais
l'anglais en dur. Un nouvel élément de menu, par opposition à une chaîne de
boîte de dialogue, a aussi besoin de titres `xml:lang` pour les quatre
langues dans `extension/Addons.xcu`.

Les modèles `.louim` eux-mêmes n'ont jamais besoin de traduction. Ils
stockent des identifiants UNO, pas des libellés ; voir
[ADR 0001](adr/0001-use-uno-command-ids.fr.md).

## Publication

Voir [HANDOFF.fr.md](../HANDOFF.fr.md). GitLab fait foi, avec un pipeline de
publication automatisé par étiquette de version ; le dépôt distant `origin`
de ce clone n'est qu'un simple miroir GitHub sans CI. Augmentez
`extension/description.xml`, ajoutez une section à CHANGELOG.md, commitez,
étiquetez `vX.Y.Z`, et poussez l'étiquette. La CI de GitLab construit et
publie le `.oxt` en Release automatiquement.
