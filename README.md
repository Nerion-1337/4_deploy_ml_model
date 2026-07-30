# 🚀 Déploiement de Modèle ML : API Futurisys

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-316192?logo=postgresql&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-Testing-green?logo=pytest)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=github-actions&logoColor=white)
![Render](https://img.shields.io/badge/Deploy-Render-black?logo=render)

## 📖 Contexte du Projet
Ce projet a été réalisé en tant que Freelance en Machine Learning pour l'entreprise **Futurisys**.
L'objectif est de mettre en production un modèle de Machine Learning permettant d'**anticiper les besoins en consommation d'énergie de bâtiments** (Projet 3). 

À la demande d'Aurélien, Directeur Technique, ce dépôt contient un *Proof of Concept* (POC) complet incluant :
- Une **API REST** robuste développée avec FastAPI.
- Une validation stricte des données entrantes via **Pydantic**.
- Une traçabilité complète des prédictions (Inputs/Outputs) sauvegardées dans une base de données **PostgreSQL**.
- Une suite de tests unitaires et fonctionnels via **Pytest**.
- Un pipeline **CI/CD** automatisant les tests et le déploiement.

---

## 🏗️ Architecture Technique
- **Backend / API** : FastAPI, Uvicorn
- **Base de données** : PostgreSQL (Local via Docker / Production via Render)
- **ORM** : SQLAlchemy
- **Machine Learning** : Scikit-Learn, Pandas, PyArrow
- **Gestionnaire de paquets** : `uv`
- **Hébergement Cloud** : Render (Base de données + Web Service)

---

## ⚙️ Prérequis
Pour exécuter ce projet localement, vous devez avoir installé :
- [Python 3.11+](https://www.python.org/downloads/)
- [uv](https://github.com/astral-sh/uv) (Gestionnaire de dépendances ultra-rapide)
- [Docker & Docker Compose](https://www.docker.com/) (Pour la base de données locale)

---

## 🚀 Installation & Exécution en Local

### 1. Cloner le dépôt

- git clone ➡️ [https://github.com/Nerion-1337/4_deploy_ml_model.git](https://github.com/Nerion-1337/4_deploy_ml_model.git)
- cd 4_deploy_ml_model

### 2. Configurer les variables d'environnement

```Bash
DATABASE_URL=postgresql://postgres:super_password_123@localhost:5432/futurisys_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=super_password_123
POSTGRES_DB=futurisys_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```
### 3. Installer les dépendances
```bash
uv sync
```
### 4. Démarrer la base de données (Local)
```bash
docker-compose up -d
```
### 5. Initialiser la base de données
```bash
uv run python data/insert_data.py
```
### 6. Lancer l'API
```bash
uv run uvicorn app.main:app --reload
```
### 7. Tests & Qualité du Code (CI) 🧪
```bash
uv run python -m pytest --cov=app --cov-report=term-missing -W ignore
```

---
## 🌍 Déploiement en Production (CD)

Le projet est entièrement automatisé pour la production.
Si les tests GitHub Actions passent avec succès (Vert), un Deploy Hook est déclenché vers Render qui met l'API à jour automatiquement.

**📍 Testez l'API en direct ici (Swagger UI)** : 👉 [Lien vers mon API en production](https://futurisys-api.onrender.com/docs)

*Note : La première requête peut prendre une minute le temps que le serveur gratuit sorte de sa veille.*

---
### Projet réalisé dans le cadre du parcours Ingénieur IA - OpenClassrooms.