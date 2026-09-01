# Réduire la charge cognitive

*Traduction française de [reducing-cognitive-load.md](reducing-cognitive-load.md).*

Un apprenant qui se demande lequel des onze menus pourrait contenir
« insérer une image » consacre son attention à l'interface plutôt qu'à
l'écriture. Chaque menu, barre d'outils ou volet de barre latérale visible
mais sans rapport avec la tâche est quelque chose qu'un débutant doit au
moins regarder et écarter avant de trouver ce dont il a réellement besoin.
Le rôle de LOUIM est de retirer cette surcharge pour une leçon donnée, sans
retirer la fonctionnalité de façon permanente.

## Les trois surfaces qui comptent le plus

En pratique, trois choses génèrent l'essentiel du bruit visuel qu'un
débutant rencontre, et les commandes de menu de LOUIM (voir le
[guide de l'enseignant](../teacher-guide.fr.md)) visent précisément
celles-ci. Les menus sans rapport avec la leçon du jour sont des candidats
courants à masquer tôt. Outils et Format ▸ Styles en sont des exemples
fréquents. Configurer les menus les retire entièrement de la barre plutôt
que de simplement laisser un menu vide, ce qui est tout ce que Outils ▸
Personnaliser peut faire seul. Les boutons de barre d'outils pour des
fonctionnalités pas encore introduites peuvent disparaître aussi : mettre
`"hide_toolbar_buttons_with_menus": true` dans un modèle fait que masquer un
menu masque aussi automatiquement les icônes de barre d'outils
correspondantes, de sorte qu'un débutant ne voit jamais une icône Insérer un
tableau dans la barre d'outils pour une fonctionnalité dont le menu entier a
disparu. Les volets de la barre latérale qui ne font pas partie de la leçon
en cours peuvent eux aussi être retirés de la section `sidebar` d'un modèle,
comme le volet Galerie ou Styles, pour que la barre latérale elle-même ait
moins de volets concurrents.

## Réduire la charge n'est pas retirer une fonctionnalité

Cette distinction compte autant sur le plan pédagogique que technique.
Chaque application est non cumulative et chaque masquage est enregistré de
sorte que Restaurer tous les menus puisse le défaire exactement (voir
[ui-element-model.fr.md](../ui-element-model.fr.md)). Un modèle qui masque
Outils cette semaine n'est pas une décision permanente. C'est un choix
propre à cette leçon, révisable dès que la leçon avance. C'est pourquoi les
modèles de départ de LOUIM se présentent en progression level-1, level-2,
full plutôt qu'en un seul « Writer simplifié » figé. La charge devrait
diminuer tôt et être réintroduite délibérément, pas rester minimale pour
toujours. Voir
[designing-progressive-writer-courses.fr.md](designing-progressive-writer-courses.fr.md).

## Une mise en garde : ne pas trop masquer

Retirer trop crée un autre type de friction. Un apprenant qui a besoin
d'Insertion ▸ Tableau mais ne trouve aucun menu Insertion doit demander au
lieu d'explorer. Les modèles level-1 fournis sont un point de départ, pas
une règle. Gardez ce dont une leçon a réellement besoin, et utilisez
Enregistrer la disposition comme modèle pour capturer votre propre version
ajustée une fois que vous avez trouvé le bon équilibre pour une classe
donnée.
