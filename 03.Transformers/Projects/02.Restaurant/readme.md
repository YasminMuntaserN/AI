# 🍽️ AI-Powered Restaurant Customer Engagement System

## 📌 Project Overview
This project demonstrates how modern NLP and Transformer-based AI can enhance a restaurant’s digital experience.  
It integrates multiple intelligent modules that work together to recommend meals, understand customer questions, and generate responses.

The system is divided into three major components:

1. Meal Recommendation Engine  
2. Semantic Search (Name / Similarity Finder)  
3. Chatbot Question-Answering System  
4. Language Model Fine-Tuning Module  

Each section applies a different AI technique, forming a practical end-to-end learning project.

---

## 🧩 System Architecture (Conceptual)
The workflow looks like this:

Customer Interaction  
→ Embedding / Similarity Processing  
→ Retrieval / Recommendation  
→ Response Generation

Different modules activate depending on the task.

---

## 🍛 1️⃣ Meal Recommendation Engine (Find Meals)
### Purpose
Suggest meals similar to ones previously ordered by a customer.

### Core Concept
This module relies on **vector similarity** rather than keyword matching.  
Meals are represented numerically in a similarity matrix created earlier.

### Workflow
1. Load dataset of meals
2. Load cosine similarity matrix
3. Convert meal name → index
4. Compare similarity scores
5. Sort highest matches
6. Display top recommendations

### Techniques Used
- Vector similarity scoring
- Averaging similarities for multi-order profiles
- Visualization of ranking results

### Why It Matters
This mimics real recommender systems used by streaming or shopping platforms.

---

## 🔎 2️⃣ Semantic Search (Find Name / Similar Items)
### Purpose
Enable intelligent lookup by meaning rather than exact wording.

### Core Concept
Text queries are converted into **embeddings** — numerical vectors representing semantic meaning.

Similar meanings → closer vectors → faster retrieval.

### Tools Used
- Multilingual sentence embedding model
- Vector index structure for fast lookup

### Workflow
1. Convert text → embedding
2. Normalize vector
3. Search index
4. Retrieve closest stored item

### Why It Matters
Handles varied phrasing and language structure gracefully.

---

## 🤖 3️⃣ Chatbot Question-Answering System
### Purpose
Automatically answer customer questions about meals.

### Core Concept
Combines embedding similarity with indexed QA pairs.

Instead of generating answers from scratch, the system retrieves the closest matching known answer.

### Workflow
1. Encode user question
2. Search semantic index
3. Locate nearest stored question
4. Return linked answer

### Advantages
- Fast
- Reliable
- Requires minimal compute
- Ideal for domain-specific assistants

---

## 🧠 4️⃣ Language Model Fine-Tuning
### Purpose
Adapt a general language model to restaurant-specific text.

### Core Concept
A pretrained model already understands language broadly.  
Fine-tuning reshapes it toward domain vocabulary and structure.

### Training Pipeline
1. Tokenization (text → numeric tokens)
2. Dataset chunking
3. Training configuration
4. Iterative weight adjustment
5. Model checkpoint saving

### Key Learning Principles
- Epoch repetition improves adaptation
- Small batch sizes manage memory
- Padding ensures uniform sequence length

### Outcome
The model better understands menu terminology and structure.

---

## 🧰 Technologies & Libraries
- Transformers ecosystem
- Sentence embeddings
- Vector similarity indexing
- Numerical computing tools
- Visualization tools

---