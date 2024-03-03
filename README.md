# CLÉEB - Cartographie des Luttes pour l'Écologie, l'Environnement et la Biodiversité

## En Développement

Ce projet est en cours de développement. Il n'est pas encore prêt pour une utilisation en production.

## Description du projet

CLÉEB est une initiative visant à cartographier et mettre en lumière les diverses actions, luttes et initiatives en
faveur de l'écologie, de l'environnement et de la biodiversité. Le projet vise à offrir une plateforme inclusive pour
répertorier et visualiser les différentes initiatives, événements, projets communautaires, manifestations et autres
actions militantes à travers des cartes informatives.

Réalisé pour [Les Écologistes - Lorraine](https://lorraine.lesecologistes.fr/)

## Objectif

L'objectif principal de CLÉEB est de fournir un outil interactif et informatif permettant de :

- Visualiser géographiquement les actions et les initiatives écologiques à travers des cartes.
- Favoriser la diffusion d'informations sur les combats pour l'écologie et l'environnement.
- Encourager la participation citoyenne en répertoriant les initiatives locales.
- Sensibiliser et mobiliser la communauté autour des enjeux écologiques et de préservation de la biodiversité.

## Comment contribuer

Ce projet est ouvert à la contribution de tous. Si vous souhaitez participer, vous pouvez :

- Ajouter de nouvelles initiatives ou événements à la carte.
- Proposer des améliorations pour rendre l'interface plus conviviale.
- Suggérer des fonctionnalités pour enrichir l'expérience utilisateur.

N'hésitez pas à ouvrir une issue ou à soumettre une demande de fusion (pull request) pour discuter de vos idées ou modifications.

## Lancement des tests

Pour que les tests fonctionnent, ils est nécessaire de préparer un template POSTGRES qui permet d'activer
les extensions `postgis`.
Pour celà, lancer les commandes suivantes dans l'inteface de `psql` :

```sql
CREATE DATABASE "cleeb-test-db-template";
```
```bash
\c cleeb-test-db-template
```
```sql
CREATE EXTENSION postgis;
UPDATE pg_database SET datistemplate = TRUE WHERE datname = 'cleeb-test-db-template';
```

## Licence

Ce projet est sous licence [MIT](https://opensource.org/licenses/MIT) - voir le fichier `LICENSE` pour plus de détails.

