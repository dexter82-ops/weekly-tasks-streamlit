# 🗓️ Weekly Tasks — Streamlit

Gestion simple des **tâches hebdomadaires** (par jour, statut, priorité, effort, récurrence) avec persistance en CSV.
Pensée pour un déploiement facile sur **Streamlit Community Cloud**.

## ✨ Aperçu des fonctionnalités
- Vue **semaine** Lundi → Dimanche (ajout rapide, édition inline)
- **Statuts** : Backlog → This Week → In Progress → Done
- **Priorité** (1 = haute, 5 = basse) & **Effort** (points)
- **Récurrence** : None / Weekly / Biweekly / Monthly (création de la prochaine occurrence quand marqué *Done*)
- **Filtres** : texte, tags (`tag1;tag2`), jour, statut
- **Export / Import** CSV via la barre latérale
- Mini **indicateurs** (compteurs par statut)

## 🚀 Déploiement — Streamlit Community Cloud
1. **Fork** ce repo sur ton GitHub.
2. Va sur [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Sélectionne : `repo`: *ton_user/weekly-tasks-streamlit*, `branch`: **main**, `file`: **app.py**.
4. **Python version**: 3.11+ (par défaut OK).  
5. Clique **Deploy**. L'appli se lance et crée `data/tasks.csv` automatiquement.

> ⚠️ *Persistance sur Streamlit Cloud*: Le système de fichiers peut être ré-initialisé lors des re-déploiements. Pour un stockage robuste (multi-utilisateurs), migrer vers une base (SQLite/Postgres) ou un Google Sheet/Supabase. Tu peux mettre des clés/API dans `.streamlit/secrets.toml` (voir exemple).

## 🧑‍💻 Exécution locale
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## 🔒 Secrets (optionnel)
Créer un fichier **.streamlit/secrets.toml** (non versionné) pour y placer d'éventuelles clés (ex: Supabase).
Un exemple est fourni: `.streamlit/secrets.toml.example`.

## 📂 Structure
```
weekly-tasks-streamlit/
├─ app.py
├─ requirements.txt
├─ README.md
├─ LICENSE
├─ .gitignore
├─ .streamlit/
│  ├─ config.toml
│  └─ secrets.toml.example
└─ data/
   └─ tasks.csv
```

## 📝 Licence
MIT — libre d'utiliser/modifier. Voir `LICENSE`.