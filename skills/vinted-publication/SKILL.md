---
name: vinted-publication
description: Publier en masse des vêtements sur Vinted à partir d'un dossier de photos. Crée l'arborescence de travail, recadre et renomme les photos, identifie chaque article visuellement, puis crée les annonces en brouillons pré-remplis via l'API Vinted (titre, description, catégorie, taille, état, matière, prix, format de colis). Déclencher quand l'utilisateur dit « publie ces vêtements sur Vinted », « prépare des fiches Vinted », « crée des brouillons Vinted », « trie mes photos de vêtements », ou mentionne un lot de photos de vêtements à vendre.
---

# Publication Vinted en masse

Transformer un dossier de photos de vêtements en annonces Vinted prêtes à publier.

## Le partage des rôles

Claude ne peut **pas** envoyer les photos dans le formulaire Vinted : l'outil d'upload navigateur est indisponible dans les sessions Cowork, et faire transiter les octets en base64 sature la conversation.

Le découpage qui fonctionne :

| Claude | L'utilisateur |
|---|---|
| Trie et recadre les photos | Glisse la photo dans la fiche |
| Identifie chaque vêtement | Coche la couleur |
| Crée les brouillons pré-remplis | Clique « Ajouter » |
| Range les photos après publication | |

Deux gestes par annonce au lieu d'une quinzaine.

## Arborescence

```
<dossier>/
├── a_publier/                  photos brutes non traitées
├── photos_pretes/              recadrées, brouillon créé, en attente
├── publiees/                   photos d'origine des articles en ligne
│   └── photos_retraitees/      versions recadrées envoyées à Vinted
├── LOT_A_PUBLIER.md            le lot en cours + liens des brouillons
├── ETAT_DES_LIEUX.md           inventaire vendus / en vente / brouillons
└── SUIVI_VINTED.md             historique des publications
```

Une photo ne vit que dans un seul dossier à la fois. Son emplacement dit son état.

## Déroulé

### 1. Recadrer

Les captures d'écran Android portent des bandes noires (barre d'état, barre de navigation) et une incrustation « X ans ». Le script `scripts/recadrer.py` détecte la zone utile par écart-type des lignes et rogne. Les photos prises à l'appareil en paysage doivent être pivotées.

**Toujours vérifier le résultat visuellement.** Le détecteur échoue sur les vêtements très uniformes (rendu trop court) — dans ce cas, rogner à pourcentage fixe (13 % en haut, 18 % en bas).

### 2. Identifier

Assembler des planches-contact de 5 photos avec `scripts/planche_contact.py`, puis les lire. Bien plus économe que d'ouvrir chaque image.

Noter pour chaque article : type de vêtement, couleur dominante, matière probable, taille (lisible sur l'incrustation), et si le colis doit passer en Moyen.

### 3. Nommer

`{taille}_{numero}_{description}.jpg` — par exemple `10ans_112_robe-noire-petites-fleurs.jpg`.

Le préfixe de taille fait que le tri alphabétique du dossier regroupe les tailles. La description doit correspondre au titre de l'annonce, sinon l'utilisateur ne retrouve pas la bonne photo au moment de la glisser.

### 4. Choisir la catégorie — l'étape critique

**Vinted n'accepte qu'une catégorie terminale.** Si le brouillon pointe sur un noeud
intermédiaire, l'utilisateur doit le corriger dans le formulaire — et ce changement
**remet à zéro tous les autres champs**. Une catégorie approximative annule donc tout
le travail de préparation sur cette fiche.

Avant de lancer les créations, passer la liste des identifiants prévus dans le
vérificateur de `reference/api-vinted.md` (« Vérifier qu'une catégorie est terminale »).
Toute catégorie ayant des enfants doit être remplacée.

Deux pièges fréquents côté filles : `1249` (Pantalons et shorts) et `1521` (Vestes)
sont des parents. Et `1539` désigne une **chemise** manches longues, pas un t-shirt —
un t-shirt reste en `1535` quelle que soit la longueur des manches.

Descendre au plus fin : jean slim en `1560` plutôt que `1559`, bomber en `2545`
plutôt qu'une catégorie générique de veste. La table complète est dans la référence.

### 5. Créer les brouillons

Voir `reference/api-vinted.md` pour les endpoints et le piège du CSRF.

Points de méthode :

- **Par vagues de 5 à 6**, avec 2,2 s entre chaque appel. Au-delà, Vinted renvoie `429 rate_limit_exceeded`.
- **Ne jamais relancer un appel qui a échoué en réseau** (`Failed to fetch`) sans vérifier d'abord si le brouillon a été créé : la requête peut avoir abouti côté serveur. C'est la cause classique de doublons.
- Vinted **ne stocke pas la couleur sur un brouillon**, même via son propre formulaire. Elle doit figurer dans le tableau récapitulatif pour que l'utilisateur la coche.
- La **matière**, elle, tient — mais seulement via un `PUT` après la création, pas dans le `POST` initial.

### 6. Livrer

Écrire `LOT_A_PUBLIER.md` : une ligne par fiche, avec le nom exact du fichier photo, le titre, la couleur à cocher, le format de colis et le lien direct vers le brouillon.

Signaler les articles qui se ressemblent (deux leggings noirs, deux robes à fleurs) en précisant que ce sont bien des articles distincts — sinon l'utilisateur croit à un doublon.

### 7. Ranger après publication

Vérifier le statut réel via l'API plutôt que de croire au déclaratif, puis déplacer :

- la photo brute de `a_publier/` vers `publiees/`
- la photo recadrée de `photos_pretes/` vers `publiees/photos_retraitees/`

Les fiches restées en brouillon gardent leurs photos en place.

## Conventions de rédaction

**Titre** — descriptif, sans majuscules superflues (Vinted refuse les titres trop capitalisés). « Robe noire à petites fleurs blanches », pas « ROBE NOIRE ».

**Description** — deux à trois phrases : le vêtement, un détail distinctif, la taille, l'état. Concret plutôt que commercial.

**Marque** — le nom réel si l'étiquette est lisible (accepter la bannière anti-contrefaçon de Vinted), sinon « Sans marque » (`brand_id: 1`). Le champ est obligatoire.

**Prix** — un prix unique pour tout le lot simplifie énormément. 1 € correspond au palier « bonne affaire ». Respecter scrupuleusement les prix que l'utilisateur a modifiés lui-même : ne jamais « corriger » un écart sans lui demander.

**Colis** — Petit par défaut. Moyen pour : ensembles deux pièces, salopettes, vestes, polaires, sweats épais, combinaisons pyjama.

## Pièges rencontrés

| Symptôme | Cause | Réponse |
|---|---|---|
| Deux fiches identiques | un `Failed to fetch` relancé | vérifier avant de relancer ; supprimer le brouillon vide |
| Brouillon vide à côté d'une annonce en ligne | l'utilisateur a créé une nouvelle fiche au lieu d'ouvrir le brouillon | rappeler d'ouvrir le lien du tableau |
| Couleur absente après publication | Vinted ne la garde pas sur un brouillon | la mettre dans le tableau |
| `429 rate_limit_exceeded` | plus de 10 créations rapprochées | attendre 60 s, reprendre par vagues de 5 |
| Photo rognée trop court | vêtement uni, faible contraste | rogner à pourcentage fixe |
| L'utilisateur ne trouve pas une photo | tri alphabétique ≠ ordre du tableau | préfixer par taille, le dire dans le fichier |
| L'utilisateur doit requalifier la catégorie, et tous les champs se vident | catégorie non terminale | vérifier `enfants === 0` avant de créer |

## Ne jamais faire

- Supprimer une annonce publiée. Fournir le lien, l'utilisateur supprime.
- Modifier le prix d'une annonce en ligne sans demande explicite.
- Publier un brouillon à la place de l'utilisateur.
