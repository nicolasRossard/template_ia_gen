# PDF Summarizer with LLM

Template MVC pour résumer des documents PDF avec l'aide de modèles de langage (LLM) comme Ollama ou OpenAI.

## Architecture

Ce projet suit strictement le pattern **Model-View-Controller (MVC)** :

- **Model** : Contient la logique métier, l'extraction PDF, et les interfaces LLM
- **View** : Interfaces utilisateur (console + API FastAPI)
- **Controller** : Orchestration entre modèle et vue

## Fonctionnalités

1. **Extraction PDF** : Lit et extrait le texte des documents PDF avec PyPDF2
2. **Interface LLM générique** : Permet d'utiliser différents fournisseurs LLM
   - Support pour Ollama (API locale)
   - Support pour OpenAI
3. **Mode Console** : Interface utilisateur en ligne de commande
4. **Mode API** : API REST avec FastAPI

## Structure du projet

```
pdf_summarizer_project/
│
├── main.py                    # Point d'entrée principal
│
├── model/                     # Couche modèle (logique métier)
│   ├── pdf_extractor.py       # Extraction de texte des PDF
│   ├── llm_port.py            # Interface abstraite pour les LLM
│   ├── ollama_adapter.py      # Implémentation pour Ollama
│   ├── openai_adapter.py      # Implémentation pour OpenAI
│   └── pdf_summarizer.py      # Service qui combine extraction + LLM
│
├── view/                      # Couche vue (interfaces utilisateur)
│   ├── console_view.py        # Interface console
│   └── fastapi_app.py         # API REST avec FastAPI
│
├── controller/                # Couche contrôleur
│   └── summarizer_controller.py  # Orchestration du workflow
│
├── pyproject.toml             # Configuration du projet et dépendances
└── README.md                  # Documentation
```

## Installation

1. Cloner le dépôt
   ```bash
   git clone https://github.com/nicolasRossard/template_ia_gen.git
   cd template_ia_gen
   ```

2. Installer les dépendances
   ```bash
   # Avec pip
   pip install -e .
   
   # Ou avec uv
   uv pip install -e .
   ```

## Utilisation

### Mode Console

```bash
python main.py --mode console
```

Suivez les instructions pour entrer le chemin du PDF et choisir le fournisseur LLM.

### Mode API

```bash
python main.py --mode api --host 0.0.0.0 --port 8000
```

L'API sera disponible à l'adresse http://localhost:8000

#### Endpoints API

- `GET /` - Information sur l'API
- `POST /summarize` - Résume un document PDF

Exemple de requête pour `/summarize`:

```json
{
  "pdf_path": "/chemin/vers/document.pdf",
  "provider": "ollama",
  "model": "llama2",
  "temperature": 0.7,
  "max_tokens": 1000
}
```

## Développement

Pour installer les dépendances de développement:

```bash
# Avec pip
pip install -e ".[dev]"

# Ou avec uv
uv pip install -e ".[dev]"
```

## Prérequis

- Python 3.8+
- Pour Ollama: Une instance Ollama en cours d'exécution (par défaut sur http://localhost:11434)
- Pour OpenAI: Une clé API valide

## Licence

MIT
