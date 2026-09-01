# Pourquoi les interfaces progressives comptent

*Traduction française de [why-progressive-interfaces-matter.md](why-progressive-interfaces-matter.md).*

La barre de menus par défaut de LibreOffice Writer compte onze menus
principaux et plus de 550 commandes. Un apprenant qui l'ouvre pour la
première fois n'a pas besoin de savoir que Fichier contient Envoyer, ou que
Format a un sous-menu Styles, ou ce que fait Outils ▸ Macros. Mais tout cela
est là, en même temps, en concurrence pour l'attention avec la ou les deux
choses dont traite réellement la leçon en cours.

Le principe de LOUIM, énoncé dans [VISION.md](../../VISION.md) (non
traduit), est que l'interface devrait s'adapter à l'apprenant plutôt que
l'inverse. Concrètement, cela signifie qu'un enseignant décide de ce qui est
visible à chaque étape d'un cours, plutôt que de laisser un apprenant
filtrer visuellement l'application entière pour trouver ce qui compte
aujourd'hui.

## À quoi cela ressemble concrètement avec LOUIM

Configurer les menus permet à un enseignant de retirer l'encombrement de
premier niveau pour une première leçon en moins d'une minute. Décochez
Affichage, Insertion, Tableau et Outils, et la barre de menus passe de onze
menus à quatre. Voir le [guide de l'enseignant](../teacher-guide.fr.md) pour
la marche à suivre. Les modèles `*-level-1.louim` fournis encodent déjà une
première coupe raisonnable pour chaque application, donc démarrer ne
nécessite pas de concevoir une interface depuis zéro. Et parce qu'une
fonctionnalité masquée n'est qu'à un clic de Restaurer tous les menus,
simplifier une interface ne signifie pas la verrouiller. Voir
[reducing-cognitive-load.fr.md](reducing-cognitive-load.fr.md) pour en
savoir plus sur cette distinction.

## Pas un outil de verrouillage

La divulgation progressive est une technique pédagogique, pas un mécanisme
de contrôle d'accès. LOUIM n'a aucune notion de profil protégé par mot de
passe auquel un élève ne pourrait pas échapper. Un élève curieux qui ouvre
Outils ▸ Gestionnaire d'extensions, ou qui demande à un enseignant de
cliquer sur Restaurer tous les menus, peut toujours accéder à l'application
complète. L'objectif est de réduire ce qui se dispute l'attention, pas ce
qui est accessible.
