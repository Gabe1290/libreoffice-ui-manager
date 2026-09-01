# Utiliser LOUIM à l'école primaire

*Traduction française de [using-louim-in-primary-schools.md](using-louim-in-primary-schools.md).*

Les jeunes apprenants bénéficient le plus d'une barre de menus petite et
stable. Lire onze libellés de menu est déjà une tâche en soi avant qu'un
enfant de sept ans n'arrive à « insérer une image ». Voici quelques
remarques propres à cette tranche d'âge, en complément du
[guide de l'enseignant](../teacher-guide.fr.md) général.

## Aller plus loin que level-1 si nécessaire

Le modèle fourni `writer-level-1` garde Fichier, Édition, Format et Aide.
Cela reste quatre menus et une barre d'outils de formatage. Pour un usage
très précoce en primaire, il est courant d'aller plus loin. Configurer les
menus peut retirer Format aussi, ne laissant que Fichier, Édition et Aide,
si une leçon consiste purement à taper des mots et à enregistrer.
Enregistrez le résultat comme votre propre modèle, quelque chose comme
`writer-primary-1.louim`, plutôt que de modifier le fichier fourni, afin que
les modèles de départ d'origine restent disponibles comme référence.

## Les icônes plutôt que la recherche dans les menus

Les élèves de primaire naviguent souvent par icône de barre d'outils avant
de savoir lire les libellés de menu de façon fiable. Mettre
`"hide_toolbar_buttons_with_menus": true`, déjà réglé dans les modèles
fournis, garde la barre d'outils synchronisée avec les menus masqués, de
sorte qu'un jeune apprenant ne voit jamais une icône de barre d'outils pour
une fonctionnalité dont le menu a disparu. Ce genre d'incohérence, où un
bouton semble familier mais ne fonctionne plus comme avant, vaut la peine
d'être évité délibérément à cet âge.

## Une classe, un modèle partagé

Plutôt que de personnaliser par élève, la plupart des classes de primaire
tirent le plus de valeur d'un modèle unique et partagé, appliqué au début de
chaque séance. La cohérence compte plus que le rythme individuel à cet âge,
et faire passer tout le monde avec Choisir un modèle prend quelques
secondes. Enregistrez-le dans `Documents/LOUIM templates` sur les machines
de la classe pour qu'il survive entre les séances et les mises à jour de
LibreOffice.

## Restaurer est un filet de sécurité, pas une menace

Si un jeune apprenant, ou un clic curieux, se retrouve quelque part
d'inattendu, Restaurer tous les menus revient toujours à un état connu.
Rien n'est jamais perdu, car LOUIM ne masque jamais que l'interface, jamais
le contenu ni les fichiers. Il vaut la peine de le dire directement aux
élèves : ce que LOUIM change dans ce qu'ils voient n'est ni une punition ni
un verrou, et un enseignant, ou éventuellement l'élève lui-même, peut
toujours tout ramener.
