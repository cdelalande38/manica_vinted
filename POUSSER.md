# Envoyer ce dépôt sur GitHub

Le dépôt est déjà initialisé : fichiers ajoutés, deux commits, branche `main`,
remote `origin` configuré sur https://github.com/cdelalande38/manica_vinted

## Avant tout : nettoyer un fichier de verrou

Le dossier partagé avec Claude n'autorise pas la suppression de fichiers, donc git y
a laissé des fichiers temporaires. Ils bloqueraient ta prochaine commande git :

```bash
cd ~/Téléchargements/habits/manica_vinted_repo
rm -f .git/HEAD.lock .git/objects/maintenance.lock
find .git/objects -name 'tmp_obj_*' -delete
```

## Puis pousser

```bash
git push -u origin main
```

Git demandera ton identifiant GitHub et un **token d'accès personnel** comme mot de passe
(GitHub n'accepte plus le mot de passe du compte) :
Settings → Developer settings → Personal access tokens → Fine-grained tokens,
avec la permission *Contents: Read and write* sur ce dépôt.

Si tu as déjà une clé SSH configurée, plus simple :

```bash
git remote set-url origin git@github.com:cdelalande38/manica_vinted.git
git push -u origin main
```

## Pourquoi pas moi

Je n'ai aucun identifiant GitHub dans cette session, et je ne manipule pas de token :
c'est un secret qui n'a pas à transiter par une conversation.

## Ensuite

Une licence serait utile sur un dépôt public — MIT si tu veux que le skill soit librement
réutilisable. Dis-le-moi et je l'ajoute.

Le dossier `manica_vinted/` (sans `_repo`) contient les mêmes fichiers mais un dépôt git
cassé, pour la même raison de permissions. Tu peux le supprimer.
