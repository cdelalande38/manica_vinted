# API Vinted — création de brouillons

Tout s'exécute **dans l'onglet Vinted connecté**, via l'outil JavaScript du navigateur. Les cookies de session portent l'authentification.

## Jeton CSRF

Absent des balises `<meta>`. Il est enfoui dans le HTML de la page :

```js
const h = document.documentElement.innerHTML;
window.__csrf = (h.match(/CSRF_TOKEN\\?":\\?"([0-9a-f-]{36})/) || [])[1];
```

À réextraire après chaque navigation. Sans lui : `403 access_denied`.

## Créer un brouillon

`POST /api/v2/item_upload/drafts` — la charge utile est enveloppée dans `draft`, pas `item`.

```js
const d = {
  title: "Robe noire à petites fleurs blanches",
  description: "Robe noire imprimée petites fleurs blanches...",
  catalog_id: 1554,
  brand_id: 1,              // 1 = Sans marque
  package_size_id: 1,       // 1 = Petit, 2 = Moyen, 3 = Grand
  currency: "EUR",
  price: 1,
  is_unisex: false,
  item_attributes: [
    { code: "condition", ids: [3] },   // 3 = Bon état
    { code: "size",      ids: [629] }  // 629 = 10 ans
  ],
  assigned_photos: []
};
const r = await fetch('/api/v2/item_upload/drafts', {
  method: 'POST',
  headers: { 'content-type': 'application/json', accept: 'application/json', 'x-csrf-token': window.__csrf },
  body: JSON.stringify({ draft: d })
});
const id = (await r.json()).draft.id;
```

## Ajouter la matière

Le `POST` initial ignore `material`. Il faut un `PUT` juste après :

```js
d.id = id;
d.item_attributes.push({ code: 'material', ids: [44] });   // 44 = Coton
await fetch('/api/v2/item_upload/drafts/' + id, {
  method: 'PUT',
  headers: { 'content-type': 'application/json', accept: 'application/json', 'x-csrf-token': window.__csrf },
  body: JSON.stringify({ draft: d })
});
```

## Couleur : impossible sur un brouillon

`color1_id` est ignoré au `POST` comme au `PUT`, et l'attribut `color` n'existe pas. Le formulaire Vinted lui-même l'efface quand on clique « Sauvegarder le brouillon ». C'est une limite du produit — la couleur doit être cochée à la main au moment de publier.

## Lire un article

`GET /api/v2/item_upload/items/{id}` → `is_draft`, `color1_id`, `item_attributes`, `photos`, `catalog_id`, `package_size_id`.

Sert à vérifier ce qui a réellement été publié plutôt que de se fier au déclaratif.

## Inventaire du compte

`GET /api/v2/wardrobe/{user_id}/items?per_page=96&page=N&order=newest_first`

Le paramètre `status` est ignoré : il faut tout charger et filtrer à la main. `pagination.total_entries` donne le total, `per_page` plafonne à 96.

- `is_draft` → brouillon
- `is_closed` + `item_closing_action === 'sold'` → vendu
- sinon → en vente

## Envoi de photo

`POST /api/v2/photos` en `multipart/form-data`, champs `photo[type]=item` et `photo[file]`. Fonctionne, mais suppose de disposer des octets **dans la page** — inaccessible depuis une session Cowork. Documenté pour mémoire.

Variantes rejetées : `photo[type]=item_photo` (400), `type`/`file` à plat (400), `/api/v2/item_upload/photos` (404).

## Identifiants

### Tailles enfant
| Taille | id |
|---|---|
| 6 ans / 116 cm | 625 |
| 7 ans / 122 cm | 626 |
| 8 ans / 128 cm | 627 |
| 9 ans / 134 cm | 628 |
| 10 ans / 140 cm | 629 |
| 11 ans / 146 cm | 630 |
| 12 ans / 152 cm | 631 |

Suite continue — vérifier une valeur inconnue via `GET /api/v2/catalog/items?catalog_ids=1554&size_ids=N&per_page=2` et lire les titres renvoyés.

### État
Neuf avec étiquette 1 · Neuf sans étiquette 2 (à confirmer) · **Bon état 3**

### Couleurs
Noir 1 · Marron 2 · Gris 3 · Beige 4 · Fuchsia 5 · Violet 6 · Rouge 7 · Jaune 8 · Bleu 9 · Vert 10 · Orange 11 · Blanc 12 · Argenté 13 · Doré 14 · Multicolore 15 · Kaki 16 · Turquoise 17 · Crème 20 · Abricot 21 · Corail 22 · Bordeaux 23 · Rose 24 · Lila 25 · Bleu clair 26 · Marine 27 · Vert foncé 28 · Moutarde 29 · Menthe 30 · Transparence 32

### Matières
Coton 44 · Polyester 45 · Laine 46 · Viscose 48 · Soie 49 · Nylon 52 · Élasthanne 53 · Polaire 120 · Peluche 177 · Velours côtelé 299 · Denim 303 · Cuir 43 · Cuir synthétique 447 · Dentelle 455 · Maille 456 · Velours 466

### Catégories — Enfants > Vêtements pour filles

**Vinted exige une catégorie terminale** (sans sous-catégorie). Choisir un noeud
intermédiaire crée une fiche que l'utilisateur devra requalifier à la main — et
changer la catégorie dans le formulaire **remet à zéro tous les autres champs**.
C'est l'erreur la plus coûteuse du processus.

Les deux pièges rencontrés : `1249` (Pantalons et shorts) et `1521` (Vestes) sont
des **parents**, jamais des cibles valides.

#### Hauts

| Vêtement | id | Catégorie |
|---|---|---|
| T-shirt, débardeur, top (toutes manches) | **1535** | Chemises et t-shirts/T-shirts |
| Polo, robe polo | 1536 | Polos |
| Chemise | 1537 | Chemises |
| Chemise manches courtes | 1538 | Chemises manches courtes |
| Chemise manches longues | 1539 | Chemises manches longues |
| Chemise sans manches | 1540 | Chemises sans manches |
| Tunique, blouse ample | 1541 | Tuniques |

⚠️ `1539` est une **chemise**, pas un t-shirt à manches longues. Un t-shirt reste
en `1535` quelle que soit la longueur des manches.

#### Pulls et sweats

| Vêtement | id |
|---|---|
| Pull en maille | 1542 |
| Pull col V | 1543 |
| Sous-pull, col roulé | 1544 |
| Gilet zippé, veste polaire souple | 1548 |
| Boléro | 1549 |
| Sweat, sweat à capuche, gilet zippé à capuche | 1550 |
| Gilet boutonné, cardigan | 1551 |

#### Bas

| Vêtement | id |
|---|---|
| Jean coupe droite | 1559 |
| Jean slim ou skinny | **1560** |
| Pantalon pattes d'éléphant | 1562 |
| Legging, pantalon souple près du corps, simili cuir | 1565 |
| Salopette, robe salopette | 1568 |
| Short, pantacourt | 1250 |
| Sarouel | 2079 |
| Pantalon de ville, chino | 1880 (Autres) |

**Pantalon de jogging → `1253` Vêtements de sport**, pas `1880`. C'est le choix
retenu sur ce compte.

#### Robes et jupes

| Vêtement | id |
|---|---|
| Robe courte | 1554 |
| Robe longue | 1553 |
| Jupe | 1248 |

#### Nuit et bain

| Vêtement | id |
|---|---|
| Combinaison pyjama une pièce | 1596 |
| Pyjama deux pièces, ensemble t-shirt + short | 1597 |
| Chemise de nuit | 1598 |
| Maillot une pièce | 1590 |
| Maillot deux pièces | 1592 |
| Peignoir | 1593 |

#### Vêtements d'extérieur

| Vêtement | id |
|---|---|
| Blazer | 2544 |
| Bomber, blouson aviateur | **2545** |
| Veste en jean | 2546 |
| Veste polaire, sherpa | 2547 |
| Doudoune | 2548 |
| Coupe-vent, veste légère zippée | **2549** |
| Veste sans manches | 1518 |
| Parka | 2541 |
| Duffle-coat | 2540 |
| Caban | 2542 |
| Trench | 2543 |
| Imperméable | 2558 |

#### Divers

| Vêtement | id |
|---|---|
| Justaucorps, legging de sport, jogging, brassière | 1253 |
| Rien ne convient | 1254 (Autres) |

### Vérifier qu'une catégorie est terminale

À faire **systématiquement** avant de créer un lot :

```js
const r = await fetch('/api/v2/item_upload/catalogs', { headers: { accept: 'application/json' } });
const j = await r.json();
const plat = [];
(function walk(l, p) {
  l.forEach(n => {
    const chemin = p + ' > ' + n.title;
    plat.push({ id: n.id, chemin, enfants: (n.catalogs || []).length });
    if (n.catalogs && n.catalogs.length) walk(n.catalogs, chemin);
  });
})(j.catalogs, '');

// les identifiants qu'on s'apprête à utiliser
const prevus = [1535, 1550, 1554, 1560, 1253];
plat.filter(f => prevus.includes(f.id) && f.enfants > 0)
    .map(f => 'NON-FEUILLE : ' + f.id + ' ' + f.chemin);
```

Toute ligne renvoyée est une catégorie à remplacer avant de lancer les créations.

### Lister les feuilles d'une branche

```js
plat.filter(f => /Vêtements pour filles/.test(f.chemin) && f.enfants === 0)
    .map(f => f.id + '\t' + f.chemin.split(' > ').slice(3).join('/'));
```

Même méthode pour les garçons ou les femmes : changer le filtre de chemin.

## Limites

- **Débit** : ~10 créations rapprochées puis `429`. Espacer de 2,2 s, par vagues de 5.
- **Titres** : trop de majuscules → `validation_error`.
- **Modification d'une annonce publiée** : `PUT /api/v2/item_upload/items/{id}` renvoie `403`. Passer par le formulaire.
