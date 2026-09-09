// À coller dans la console d'un onglet Vinted connecté, ou à exécuter via
// l'outil JavaScript du navigateur.
//
// Vérifie qu'une liste d'identifiants de catégories est utilisable :
// Vinted refuse les catégories qui ont des sous-catégories, et corriger une
// catégorie dans le formulaire remet à zéro tous les autres champs de la fiche.
//
// Modifier `PREVUS` puis exécuter. Toute ligne « NON-FEUILLE » est à remplacer.

const PREVUS = [1535, 1550, 1554, 1560, 1253];

const r = await fetch('/api/v2/item_upload/catalogs', { headers: { accept: 'application/json' } });
const j = await r.json();

const plat = [];
(function walk(liste, parent) {
  liste.forEach(n => {
    const chemin = parent + ' > ' + n.title;
    plat.push({ id: n.id, chemin, enfants: (n.catalogs || []).length });
    if (n.catalogs && n.catalogs.length) walk(n.catalogs, chemin);
  });
})(j.catalogs, '');

const index = Object.fromEntries(plat.map(f => [f.id, f]));

const rapport = PREVUS.map(id => {
  const f = index[id];
  if (!f) return `INCONNU     ${id}`;
  if (f.enfants > 0) {
    const feuilles = plat
      .filter(x => x.chemin.startsWith(f.chemin + ' > ') && x.enfants === 0)
      .map(x => `${x.id} ${x.chemin.split(' > ').pop()}`);
    return `NON-FEUILLE ${id} ${f.chemin}\n            → au choix : ${feuilles.join(' | ')}`;
  }
  return `ok          ${id} ${f.chemin}`;
});

rapport.join('\n');
