# ADR 0004 — Abandonner l'objet `Workspace` ; dériver le module actif à chaque appel

*Traduction française de [0004-workspace-concept.md](0004-workspace-concept.md).*

## Statut

Accepté, remplaçant l'objet de modèle `Workspace` dans
`docs/project-constitution.md`, principe 5. En vigueur depuis la prise en
charge de Calc en v2.0, qui a forcé à répondre concrètement, pour la
première fois, à la question « pour quelle application est cette
opération ? ».

## Contexte

La couche Modèle de la constitution nomme `Workspace` aux côtés de `Profile`
et `UIElement`. Implicitement, cela signifiait un objet suivant quelle
application et quel document LibreOffice LOUIM traite actuellement,
vraisemblablement créé une fois puis consulté, et tenu à jour, à mesure que
l'utilisateur se déplaçait entre les fenêtres.

Quand la prise en charge de Calc a été ajoutée, la question qui avait
réellement besoin d'une réponse était plus étroite : étant donné le document
qui est le composant actif en ce moment, quel `Module` s'applique ? C'est
une fonction pure du document lui-même, et elle peut recevoir une réponse à
neuf à chaque fois plutôt que d'être suivie.

## Décision

Pas d'objet `Workspace`. `module_for_document(doc)` dans
`src/louim/adapters/modules.py` examine le document actif via
`doc.supportsService(module.doc_service)` et renvoie le `Module`
correspondant à chaque appel. Les points d'entrée de `extension.py`
l'appellent au début de chaque application, restauration ou export, plutôt
que de le lire depuis un état conservé. Voir
[workspace.md](../workspace.md) pour la correspondance complète entre ce à
quoi un `Workspace` aurait répondu et ce qui y répond à sa place.

## Conséquences

Il n'y a pas d'état de session à garder synchronisé si l'utilisateur passe
d'un document Writer ouvert à un document Calc ouvert entre deux clics de
menu de LOUIM. Chaque clic redérive le module depuis zéro. Cela coûte une
vérification `supportsService` supplémentaire par appel de point d'entrée,
ce qui est négligeable, payé pour éviter toute une catégorie de bogues liés
à un espace de travail périmé. Si aucun document pris en charge n'est le
composant actif, `module_for_document` renvoie `None` et le point d'entrée
n'a rien sur quoi agir. Il n'y a pas de machine à états séparée « aucun
espace de travail sélectionné » à maintenir, juste une vérification de
`None`. Les fichiers d'état par module, comme
`louim-toolbar-state-writer.json`, donnent déjà à chaque opération limitée à
une application sa propre identité persistante sans avoir besoin d'un objet
`Workspace` pour les posséder. Voir [architecture.md](../architecture.md).

## Où cela vit dans le code

`module_for_document` dans `src/louim/adapters/modules.py`, appelé depuis
chaque point d'entrée dans `src/louim/extension.py`.
