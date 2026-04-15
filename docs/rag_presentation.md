---
marp: true
author: Marcel Melzig
title: "RAG"
description: How to build a mini RAG with Python and SQLite
paginate: true
theme: uncover
class: invert
transition: drop
backgroundColor: #111
---


# Stand meines Projekts

1. App fragte Daten von einer API ab (OpenFoodFacts, Full Text Search)
2. App auf ORM und SQLite umgebaut

---

# RAG 

(Retrieval-Augmented Generation)

Eigene Daten = Retrieval Augmented
LLM = Generation  

---

## Warum?

LLM hat nur den Prompt und gelernte Muster zum Zeitpunkt X. 

Es hat **keine**:

    - Datenbank
    - Daten
    - Dokumente
    - Wissen

---

## Ziel 

Eine semantische Suche, die eine ausformulierte Antwort gibt.

"Finde mir Alternativen zu...", "Was hat viele Kalorien?"

---

## Wie baut man ein RAG?

1. Man braucht Daten (lokal, die API nützt nichts mehr)
2. Daten vorbereiten
3. Embeddings erzeugen, speichern -> Hyperraum
4. Embedding der Frage erzeugen
5. Distanz des Frage-Embeddings zu anderen Vektoren zeigt wie ähnlich Daten sind
6. Daten in Prompt einbauen und LLM Antwort formulieren lassen

---

# Prompt zeigen

--- 

# Code

`sqlite-rag`: Lib um ein RAG aufzusetzen

`nutrition_db_updater.py`

---

# Chunk

```
name: Redwood Coast Sriracha & Monterey Jack Cheese
brand: Redwood Coast
type: Sriracha Jack
categories: Dairies; Fermented foods; Fermented milk products; Cheeses
attributes: spicy; dairy; fermented
calories_per_100g: 210
fat_g: 18
protein_g: 12
carbs_g: 3
```

---

# Datenbank und Suche

Vectorsuche + FTS (Full Text Searc) + RRF (Reciprocal Rank Fusion)

---

# Prompt

- Modell läuft in `llama-cpp-python` lokal.
- Role Based Prompt
