# manica_vinted

Un skill Claude pour vendre un stock de vêtements sur Vinted à partir d'un simple dossier de photos.

## Le problème

Créer une annonce Vinted à la main, c'est une quinzaine de gestes : titre, description, catégorie dans une arborescence à trois niveaux, marque, taille, état, couleur, matière, prix, format de colis, photo. Pour deux cents vêtements, c'est plusieurs jours.

## Ce que fait le skill

Claude prend en charge tout sauf deux gestes :

1. Il trie et recadre les photos, retire les bandes noires des captures Android
2. Il identifie chaque vêtement en lisant des planches-contact
3. Il crée les annonces en **brouillons pré-remplis** via l'API Vinted
4. Il produit un tableau récapitulatif avec un lien direct par fiche
5. Il range les photos une fois les annonces en ligne

Il reste à faire, pour chaque fiche : **glisser la photo, cocher la couleur**.

Ces deux gestes ne sont pas un oubli. L'upload de fichier n'est pas accessible aux sessions Cowork, et Vinted ne conserve pas la couleur sur un brouillon — même son propre bouton « Sauvegarder le brouillon » l'efface.

## Installation

Copier `skills/vinted-publication/` dans le dossier des skills de Claude Cowork ou Claude Code.

## Usage

Connecter le dossier de photos, ouvrir un onglet Vinted connecté, puis :

> Prépare-moi 20 fiches Vinted à partir des photos du dossier

## Chiffres

Éprouvé sur un stock réel de 218 photos : 197 annonces créées, 76 vendues.

## Contenu

```
skills/vinted-publication/
├── SKILL.md                    la méthode
├── reference/api-vinted.md     endpoints, identifiants, limites
└── scripts/
    ├── recadrer.py
    └── planche_contact.py
```

## Avertissement

Ce skill s'appuie sur l'API interne de Vinted, non documentée et susceptible de changer sans préavis. Il ne publie jamais rien tout seul : il ne crée que des brouillons, la publication reste un geste humain.
