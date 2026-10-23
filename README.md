# <PLOTPERMIT (B-REG-09>

> Fill this top section from your Examate project card on Day 1. Replace every line in angle brackets.

## Problem
Construction site engineers and small builders in Tamil Nadu may struggle to find the correct building regulations in lengthy documents. Rules, amendments, and circulars can be difficult to search while working at a construction site. PlotPermit aims to make this information easier to access through a mobile-friendly assistant. It will provide concise answers with references to the relevant source documents.

## Who it is for
- Site engineers working on residential construction projects in Tirunelveli, Tamil Nadu.
- Small builders who need quick access to building regulations

## Signature feature
A mobile-first building-rules assistant with concise answers, source references, and a Lite mode for low-bandwidth connections.

## Hardest problem (my interview story)
The main challenge is helping users find accurate answers across lengthy building-rule documents and amendments while keeping responses short, fast, and supported by sources. The solution needs to retrieve the relevant information and show where the answer came from, even when the user has a slow internet connection.

## Dataset
|Source| Link| Documents| Pages| Licence / terms
Tamil Nadu Combined Development and Building Rules, 2019| To verify| To verify| To verify| To verify
Relevant Government Orders and amendments| To verify| To verify| To verify| To verify
DTCP circulars and related official documents| To verify| To verify| To verify| To verify
| <name> | <url> | <n> | <n> | <licence> |

## 10 real questions
See [docs/QUESTIONS.md](docs/QUESTIONS.md).

## Run it
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env                                 # Windows: copy .env.example .env
uvicorn app.main:app --reload
curl localhost:8000/health
```

## Live link
<Added in Week 2>
