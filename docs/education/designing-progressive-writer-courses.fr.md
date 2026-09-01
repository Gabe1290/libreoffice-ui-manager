# Concevoir des cours progressifs pour Writer

*Traduction française de [designing-progressive-writer-courses.md](designing-progressive-writer-courses.md).*

Voici un modèle pratique pour séquencer un cours Writer autour des modèles
de LOUIM, en s'appuyant sur le point de départ fourni
`writer-level-1`, `writer-level-2` et `writer-full`. Voir le
[guide de l'enseignant](../teacher-guide.fr.md) pour ce que chacun masque.

## Un squelette en trois étapes

Étape un, Getting Started (`writer-level-1`), ne garde que Fichier,
Édition, Format et Aide. Affichage, Insertion, Tableau et Outils sont
masqués, ainsi que les barres d'outils Rechercher et Insertion, tandis que
Dessin reste visible. Cela convient pour taper, faire du formatage de base
comme le gras et l'italique, et enregistrer et ouvrir des fichiers. Un
apprenant ici ne choisit pas encore entre onze menus, seulement quatre.

Étape deux, Basic Editing (`writer-level-2`), réaffiche Affichage,
Insertion et Tableau, tandis que Format ▸ Styles et Outils restent masqués.
Une fois qu'une classe est à l'aise avec les paragraphes et le formatage,
c'est un bon moment pour introduire l'insertion d'images et de tableaux et
l'usage d'Affichage, pour les marques de formatage ou le zoom, sans encore
exposer Outils ▸ Options, Macros, ou le système de styles.

Étape trois, Complete Writer (`writer-full`), affiche tout. C'est
l'équivalent de Restaurer tous les menus. À utiliser une fois que les
compétences fondamentales d'un cours sont établies et que l'objectif passe
à une utilisation autonome complète.

## Adapter le squelette à votre cours

Les trois niveaux fournis sont un défaut raisonnable, pas un programme
figé. Il y a deux façons de les adapter sans écrire de JSON à la main.
Configurer les menus, puis Enregistrer fonctionne pour une variante rapide.
Un cours qui veut Tableau disponible dès le premier jour mais pas
Insertion, par exemple, peut décocher juste Insertion, laisser Tableau
coché, et enregistrer sous `writer-level-1b.louim`. Enregistrer la
disposition comme modèle, après avoir ajusté les barres d'outils ou la
barre latérale à la main via Outils ▸ Personnaliser et le propre menu de la
barre latérale, convient à une étape qui a besoin de plus qu'un contrôle par
menu entier, comme masquer seulement le bouton de barre d'outils
Insertion ▸ Graphique tout en gardant le reste d'Insertion.

## Séquencer sur un trimestre

Parce que l'application est toujours non cumulative et que Restaurer
revient toujours aux vrais réglages par défaut, faire passer une classe
d'une étape à l'autre en cours de trimestre est un simple clic sur Choisir
un modèle dans un sens ou dans l'autre. Il n'y a aucun risque d'interface à
moitié ancienne, à moitié nouvelle, et aucun besoin de réinitialiser avant
de changer. Cela rend pratique de garder plusieurs modèles d'étape nommés,
`writer-level-1`, `writer-level-1b`, `writer-level-2`, et ainsi de suite,
dans `Documents/LOUIM templates`, et de faire passer une classe ou un élève
individuel entre eux à mesure que le cours progresse plutôt que de concevoir
une seule interface et de vivre avec pour tout le trimestre.
