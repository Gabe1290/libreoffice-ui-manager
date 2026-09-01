# Glossaire

*Traduction française de [glossary.md](glossary.md).*

Termes utilisés dans les documents, le code et les fichiers `.louim` de
LOUIM.

**Fichier `.louim` / modèle.** Un fichier JSON décrivant quelles parties de
l'interface d'une application LibreOffice sont affichées ou masquées. Le
schéma complet est dans [template-format.md](template-format.md) (non
traduit). On en applique un avec Choisir un modèle, on en produit un avec
Enregistrer la disposition comme modèle, ou on l'édite simplement à la main
dans n'importe quel éditeur de texte.

**Application / module.** Quelle application LibreOffice cible un modèle,
`writer`, `calc`, `impress`, ou `draw`, stocké dans le champ
`"application"` d'un modèle. En interne, chaque application est représentée
par un descripteur `Module` (`src/louim/adapters/modules.py`) qui regroupe
les identifiants dont LOUIM a besoin pour agir dessus. Voir
[architecture.fr.md](architecture.fr.md).

**Identifiant de commande UNO.** Le nom interne, indépendant de la langue,
que LibreOffice utilise pour une commande de menu, comme `.uno:InsertMenu`
ou `.uno:InsertPagebreak`. C'est ce que les fichiers `.louim` stockent au
lieu du libellé visible d'un menu, afin qu'un modèle fonctionne dans
n'importe quelle langue de LibreOffice. Voir
[ADR 0001](adr/0001-use-uno-command-ids.fr.md). On peut en trouver un pour
une commande avec `tools/discover-menus.py --tree`, un outil de
développement ; voir [developer-guide.fr.md](developer-guide.fr.md).

**URL de ressource de barre d'outils.** L'identifiant d'une barre d'outils
entière, comme `private:resource/toolbar/standardbar`, utilisé comme clé de
la section `toolbars`. C'est un espace de noms différent d'un identifiant de
commande UNO : une barre d'outils entière a une URL de ressource, tandis que
les boutons à l'intérieur ont des identifiants de commande, utilisés dans
`toolbaritems`.

**Volet (volet de la barre latérale).** Un panneau de la barre latérale,
comme Propriétés, Styles, Galerie, ou Navigateur. Identifié par un
identifiant de volet, comme `GalleryDeck`, dans la section `sidebar` d'un
modèle.

**Menu d'extension.** Un menu principal apporté par une extension autre que
LOUIM, par exemple Dmaths, qui ne fait pas partie de la barre de menus
intégrée de LibreOffice. Identifié par son nom de nœud de configuration dans
la section `addons` d'un modèle. Le menu propre à LOUIM ne peut jamais être
masqué de cette façon.

**Profil.** Terme informel pour désigner les réglages à l'intérieur d'un
modèle `.louim`. Ce n'est pas une classe ou un objet dans le code ; voir
[ADR 0004](adr/0004-workspace-concept.fr.md). Le dictionnaire du modèle
*est* le profil.

**Appliquer / Restaurer.** Appliquer met l'interface en conformité avec un
modèle, et c'est toujours non cumulatif : cela part des réglages par défaut
de LibreOffice, ou pour la barre latérale et les menus d'extension, de ce à
quoi l'interface ressemblait avant que LOUIM n'y touche, et cela ne s'empile
jamais sur le modèle précédent. Restaurer rétablit tout ce que LOUIM a
changé exactement comme c'était avant, indépendamment du modèle appliqué en
dernier, le cas échéant.

**Découverte.** Lire l'interface active de LibreOffice, quels menus, barres
d'outils, volets et menus d'extension existent en ce moment, plutôt que de
travailler à partir d'une liste codée en dur. Voir
[discovery-engine.fr.md](discovery-engine.fr.md) et
[ADR 0002](adr/0002-discovery-engine.fr.md).

**Niveau (level-1 / level-2 / full).** Pas un concept de LOUIM dans le
code, juste la convention de nommage que les modèles de départ fournis
utilisent pour une progression allant d'une interface minimale (level-1) à
une intermédiaire (level-2) jusqu'à tout (full). Voir le
[guide de l'enseignant](teacher-guide.fr.md).

**Configurer les menus.** La boîte de dialogue intégrée pour retirer des
menus principaux entiers sans éditer un fichier `.louim` à la main. Voir le
guide de l'enseignant.

**Menus protégés.** Fichier, Édition et Aide, les trois menus principaux
que LOUIM ne masquera jamais, que ce soit depuis un modèle ou depuis
Configurer les menus. [PROJECT.md](../PROJECT.md) explique pourquoi cette
règle existe.

**LOUIM.** LibreOffice UI Manager, ce projet. À ne pas confondre avec
LONBM (LibreOffice Notebookbar Manager), un projet compagnon distinct qui
gère le mode d'interface à onglets « Notebookbar ». LOUIM reste
délibérément en dehors de cela. Voir [HANDOFF.fr.md](../HANDOFF.fr.md).
