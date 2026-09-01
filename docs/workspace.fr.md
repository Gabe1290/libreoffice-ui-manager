# Espace de travail (Workspace)

*Traduction française de [workspace.md](workspace.md).*

La [constitution du projet](project-constitution.md) (non traduite), au
principe 5, liste `Workspace` comme l'un des trois objets du Modèle, aux
côtés de `Profile` et `UIElement`. Aucun des trois n'existe comme classe dans
le code livré (voir [ADR 0004](adr/0004-workspace-concept.fr.md) pour le
raisonnement complet). Ce document explique ce qui joue le rôle de
`Workspace` à sa place, puisque la question à laquelle il était censé
répondre, quelle application et quel document LOUIM est en train de traiter,
est réelle et doit toujours trouver une réponse.

## Ce à quoi un Workspace aurait dû répondre

Un objet Workspace aurait dû savoir quelle application LibreOffice est
active en ce moment, où vit la configuration d'interface de cette
application (quels nœuds de configuration, quel nœud d'état de fenêtre), et
où les fichiers d'état de LOUIM pour cette application devraient être lus et
écrits.

## Ce qui répond à ces questions à sa place

Quelle application est active trouve sa réponse à chaque appel, pas dans un
état de session conservé. `module_for_document(doc)`, dans
[`src/louim/adapters/modules.py`](../src/louim/adapters/modules.py), examine
le document actuellement ouvert par LibreOffice via
`doc.supportsService(...)` et renvoie le `Module` correspondant.
`extension.py` appelle cette fonction au début de chaque point d'entrée
d'application, de restauration et d'export. Il n'y a rien à garder
synchronisé si l'utilisateur change de document entre deux appels, car rien
n'est mis en cache.

Où vit la configuration trouve sa réponse dans le descripteur `Module`
lui-même. Ses champs `doc_service`, `windowstate_node`, et les groupes de
contexte de la barre latérale et des menus d'extension sont exactement les
identifiants par application qu'un objet Workspace aurait autrement dû
rechercher. Voir
[architecture.fr.md](architecture.fr.md#srclouimadaptersmodulespy--le-descripteur-module).

Où vivent les fichiers d'état trouve sa réponse dans l'assistant propre
`state_path(ctx, module)` de chaque adaptateur. Il demande au service
`PathSubstitution` de LibreOffice le répertoire du profil utilisateur et y
ajoute un nom de fichier indexé par module, comme
`louim-toolbar-state-writer.json` ou `louim-sidebar-state-calc.json`. Il n'y
a pas de notion partagée de « répertoire de l'espace de travail ». L'état de
chaque surface est indépendant, ce qui correspond à la façon dont chaque
surface s'applique et se restaure indépendamment.

## Pourquoi cela suffit

Un objet `Workspace` aurait dû être créé, conservé quelque part, et tenu à
jour à mesure que l'utilisateur passait d'une fenêtre Writer, Calc, Impress
ou Draw ouverte à une autre. C'est de l'état supplémentaire qui pourrait se
périmer ou fuir. Dériver le module à neuf depuis le document actif à chaque
appel élimine toute cette catégorie de bogue, au prix d'une vérification
`supportsService` bon marché par point d'entrée. C'est le même compromis que
décrit `architecture.md` pour `Profile` et `UIElement` : la couche Modèle de
la constitution s'est transformée en recherches sans état contre la
configuration active propre de LibreOffice, avec pour seule donnée
persistante le modèle lui-même, un simple dictionnaire.

## Réserve concernant plusieurs documents

Comme « l'espace de travail » se dérive à chaque appel plutôt que d'être
suivi, LOUIM n'a aucune notion de « l'espace de travail Writer » comme quelque
chose qu'on pourrait inspecter indépendamment d'un document Writer
actuellement ouvert. Si aucun document Writer, Calc, Impress ou Draw n'est
le composant actif quand un point d'entrée s'exécute, `module_for_document`
renvoie `None` et il n'y a rien pour le point d'entrée sur quoi agir. Cela
correspond à la façon dont l'extension est réellement utilisée, via des
commandes de menu invoquées depuis l'intérieur de l'application qu'elles
concernent, et cela n'a pas eu besoin de changer depuis la v1.0.
