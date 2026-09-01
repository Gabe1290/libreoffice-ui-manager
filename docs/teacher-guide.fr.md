# Guide de l'enseignant

*Traduction française de [teacher-guide.md](teacher-guide.md).*

Tout ce dont un enseignant a besoin pour utiliser LOUIM en classe, sans
toucher au code. Pour l'installation, consultez le [README](../README.md#install)
(non traduit). Ce guide couvre ce qu'il faut faire une fois l'extension
installée.

## Le menu

Une fois l'installation faite, chaque application prise en charge (Writer,
Calc, Impress, Draw) obtient un menu LibreOffice UI Manager avec quatre
commandes. **Configurer les menus** permet de cocher ou décocher des menus
principaux entiers. **Choisir un modèle** applique un fichier `.louim`,
fourni ou personnel. **Enregistrer la disposition comme modèle** capture
l'apparence actuelle de l'interface dans un fichier `.louim` que vous pouvez
réutiliser ou partager. **Restaurer tous les menus** annule tout ce que
LOUIM a changé, pour revenir aux réglages par défaut de LibreOffice.

## Le moyen le plus rapide de simplifier une interface

Pour la plupart des besoins en classe, vous n'avez jamais besoin de toucher
à un fichier `.louim`. Configurer les menus ouvre une boîte de dialogue
listant les menus principaux de l'application, Fichier, Édition, Affichage,
Insertion, Format, Tableau, Outils, et ainsi de suite, avec une case à
cocher chacun. Décocher un menu le fait disparaître entièrement de la barre
de menus. C'est plus fort que Outils ▸ Personnaliser de LibreOffice, qui
peut vider un menu intégré de ses éléments mais laisse toujours le menu
désormais vide sur la barre.

Fichier, Édition et Aide restent cochés quoi qu'il arrive et ne peuvent pas
être décochés. Ce sont des conventions universelles à travers toutes les
applications de bureau, et Aide est aussi l'endroit où vit le menu propre à
LOUIM, donc les garder signifie qu'il y a toujours un chemin de retour vers
Restaurer tous les menus.

La boîte de dialogue peut enregistrer son résultat comme modèle dans la
même étape. Un rangement de cinq secondes devient un profil réutilisable
pour la prochaine fois.

## Utiliser les modèles fournis

Chaque application est livrée avec trois modèles de départ dans
`templates/<application>/`. `<application>-level-1.louim`, appelé
« Getting Started », est l'interface la plus réduite. Il masque Affichage,
Insertion, Tableau et Outils, garde Fichier, Édition, Format et Aide, et
réduit les barres d'outils en conséquence. `<application>-level-2.louim`,
« Basic Editing », réaffiche Insertion, Affichage et Tableau pour les
apprenants prêts à les utiliser, tout en gardant Styles et Outils masqués.
`<application>-full.louim`, « Complete », affiche tous les menus. C'est
l'équivalent de Restaurer tous les menus, mais disponible comme modèle
depuis le sélecteur.

Choisir un modèle ouvre un sélecteur de fichier déjà placé dans le propre
dossier de modèles de l'application active, donc Writer n'affiche que les
modèles Writer et Calc seulement ceux de Calc. On ne peut pas appliquer par
accident un profil Calc à Writer.

Une progression type au fil d'un cours commence toute la classe sur
`writer-level-1`, fait passer des élèves ou tout le groupe à
`writer-level-2` une fois à l'aise avec les paragraphes et le formatage de
base, puis applique `writer-full`, ou clique sur Restaurer tous les menus,
une fois la phase d'apprentissage terminée.

## Créer son propre modèle

Il y a deux façons de faire, de la plus simple à la plus précise. La
première est Configurer les menus, puis Enregistrer : décochez les menus
dont vous ne voulez plus et enregistrez comme modèle. Cela fonctionne bien
pour les profils « retirer quelques menus entiers ». La seconde est de
mettre en place l'interface à la main puis d'utiliser Enregistrer la
disposition comme modèle. Utilisez Outils ▸ Personnaliser pour masquer des
boutons de barre d'outils ou des éléments de menu individuels plutôt que des
menus entiers, réorganisez les barres d'outils, masquez des volets de la
barre latérale via le propre menu de la barre latérale, puis exportez.
L'export de LOUIM capture tout cela : quels menus et éléments de menu
individuels sont visibles, quelles barres d'outils et boutons de barre
d'outils s'affichent, et quels volets de la barre latérale (Propriétés,
Styles, Galerie, etc.) sont présents, élément par élément plutôt que par
surfaces entières.

Les modèles s'enregistrent par défaut dans `Documents/LOUIM templates`, donc
ils survivent à une réinstallation de LibreOffice ou une mise à jour de
l'extension. Le stockage propre de l'extension, lui, ne survit pas.

## Modifier un fichier `.louim` à la main

Un modèle enregistré est du JSON simple et lisible, ouvrable dans n'importe
quel éditeur de texte. Voir [template-format.md](template-format.md) (non
traduit) pour la référence complète des champs. En résumé : chaque section
fait correspondre un identifiant à `true` pour l'afficher ou `false` pour le
masquer, et tout ce qui n'est pas mentionné reste affiché par défaut. Deux
choses à savoir avant d'éditer à la main. Les identifiants sont les noms de
commande internes propres à LibreOffice, comme `.uno:InsertMenu`, pas les
libellés de menu que vous voyez à l'écran. C'est ce qui fait qu'un modèle
fonctionne dans n'importe quelle langue de LibreOffice. Utilisez Choisir un
modèle après toute modification pour vérifier qu'il se charge toujours ; une
faute de frappe dans un identifiant est silencieusement ignorée plutôt que
signalée comme une erreur, donc l'élément reste simplement à son état par
défaut. Mettre `"hide_toolbar_buttons_with_menus": true` retire
automatiquement l'icône de barre d'outils de tout ce qui est masqué dans
`"menus"`, donc vous n'avez pas à masquer la même fonctionnalité deux fois.

## Restaurer

Restaurer tous les menus rétablit chaque surface que LOUIM a changée,
menus, barres d'outils, boutons de barre d'outils, volets de la barre
latérale et menus d'extension, exactement comme ils étaient avant que LOUIM
n'y touche, indépendamment du modèle appliqué en dernier, le cas échéant.
C'est toujours sûr de cliquer si quelque chose semble anormal.

## Questions fréquentes

Un modèle va-t-il casser si le LibreOffice d'un élève est dans une autre
langue ? Non. Les modèles ne stockent jamais de libellés de menu, seulement
les identifiants internes de LibreOffice, donc le même fichier `.louim`
fonctionne dans un LibreOffice anglais, français, allemand ou italien sans
changement.

J'ai appliqué un modèle, puis un autre. Se sont-ils combinés ? Non.
L'application n'est jamais cumulative. Les menus, barres d'outils et
boutons de barre d'outils du second modèle sont recalculés à neuf depuis les
préférences d'usine de LibreOffice, donc appliquer le modèle B après le
modèle A donne exactement B.

Est-ce que cela fonctionne pareil dans Calc, Impress et Draw ? Oui, les
mêmes quatre commandes de menu, le même format de modèle, le même
comportement. Seuls les noms de menu et le contenu des barres d'outils
diffèrent selon l'application, et chacune a ses propres modèles de départ
sous `templates/<application>/`.

Est-ce un outil de verrouillage ? Non, et [VISION.md](../VISION.md) (non
traduit) le dit explicitement. Rien de ce que LOUIM masque n'est supprimé.
Chaque fonctionnalité masquée n'est qu'à un clic de Restaurer tous les
menus, et un modèle est censé changer à mesure que les compétences d'un
apprenant grandissent, pas restreindre définitivement ce qu'il peut faire.
