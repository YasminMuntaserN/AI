# 🏨 Adding Artificial Intelligence to the 4Z Hotel using LLaMA and RAG

## 📌 Project Overview
This project demonstrates how to build an **AI-powered hotel assistant** for the **4Z Hotel** using a **local Large Language Model (LLaMA)** enhanced with **Retrieval-Augmented Generation (RAG)**.

The assistant can:
- Answer questions in **English and Arabic**
- Work **offline (no internet required)**
- Provide **accurate answers based only on hotel data**
- Avoid hallucinations by saying *"I do not know"* when information is missing

The core idea is to combine a powerful language model with a **Vector Store** that contains the hotel’s knowledge.

---

## 🎯 Project Goals
- Understand what **LLaMA** is and how it can be used
- Run a **local LLaMA model** on limited hardware
- Improve answers using **Prompt Engineering**
- Customize a general model to answer **hotel-specific questions**
- Implement **RAG (Retrieval-Augmented Generation)**
- Build and use a **Vector Store** for semantic search

---

## 🤖 What is LLaMA?
**LLaMA (Large Language Model Meta AI)** is a family of large language models developed by **Meta**.

LLaMA models are designed for Natural Language Processing (NLP) tasks such as:
- Text generation
- Question answering
- Text summarization
- Translation
- Conversational AI

### Important Notes
- A model name like **8B** means *8 billion parameters*
- **Instruct** models are optimized for chat and instructions
- LLaMA models can be:
  - Used online
  - Or run locally using formats like **GGUF**

---

## ❓ Why Was the Base Model Not Enough?
A raw LLaMA model:
- Is very smart, but **general-purpose**
- Has **no knowledge about the 4Z Hotel**
- May guess answers or give incorrect information


❌ Fine-tuning the model is expensive and complex

✅ A better solution is **RAG**

---

## 🧠 Prompt Engineering
Prompt Engineering is the process of **carefully designing inputs** to guide the model’s behavior.

In this project we used:
- **System Prompts** to define strict rules
- Language control (Arabic vs English)
- Instructions to avoid explanations
- Context-aware questions

This resulted in:
- Shorter answers
- More accurate responses
- Consistent output style

---

## 🚀 What is RAG (Retrieval-Augmented Generation)?
**RAG** is a technique that enhances language models by **retrieving relevant information before generating an answer**.

Instead of relying only on the model’s memory:
1. We search for relevant hotel data
2. We pass this data as *context* to the model
3. The model answers using the provided information

📌 The model does NOT memorize hotel data
📌 It reads it dynamically at question time

---

## 🔄 How RAG Works in This Project
The pipeline used in this project:

1. Load hotel data (TXT / CSV files)
2. Split text into small chunks
3. Convert each chunk into numerical **embeddings**
4. Store embeddings in a **Vector Store**
5. When a user asks a question:
   - Create an embedding for the question
   - Retrieve the most similar text chunks
   - Send them as context to LLaMA
6. Generate the final answer

---

## 📦 What is a Vector Store?
A **Vector Store** is a database that stores numerical representations (embeddings) of text.

Unlike keyword search:
- It searches by **meaning**, not exact words

We used:
- **Sentence Transformers** to create embeddings
- **FAISS (Facebook AI Similarity Search)** for fast similarity search

This is ideal for **unstructured text data**.

---

## 🔢 What is an Embedding?
An **embedding** is a list of numbers that represents the *semantic meaning* of text.

For example:
- "Is there a swimming pool?"
- "Does the hotel have a pool?"

➡️ These two sentences will have **very similar embeddings**

---

## 🧱 Role of LangChain
**LangChain** simplifies building applications with Large Language Models.

In this project, it helped with:
- Connecting the LLM with the Vector Store
- Managing prompts and context
- Implementing retrieval pipelines

We used **RetrievalQA**, which:
1. Retrieves relevant documents
2. Injects them into a prompt template
3. Sends everything to the LLM
4. Returns a clean answer

---

## 🗂 Why GGUF Models?
GGUF is a modern format for running LLMs locally.

Advantages:
- Optimized for CPU usage
- Lower memory requirements
- Works without internet
- Ideal for local and edge deployments

---

## 🏨 What Can the Assistant Do Now?
✔ Answer hotel-specific questions
✔ Provide accurate phone numbers, services, prices
✔ Respond in Arabic or English
✔ Work fully offline
✔ Avoid hallucinations
✔ Say "I do not know" when data is missing

---

## 📖 Key Terms Summary

| Term | Description |
|----|----|
| LLM | Large Language Model |
| LLaMA | Meta’s language model |
| Prompt | Input instructions for the model |
| System Prompt | High-level behavior rules |
| RAG | Retrieval + Generation technique |
| Embedding | Numerical representation of meaning |
| Vector Store | Database of embeddings |
| FAISS | Fast similarity search engine |
| Retriever | Component that fetches relevant text |
| Context | Information sent with the question |
| GGUF | Local LLM file format |

---

## 🏁 Conclusion
This project shows how hotel data can be transformed into an **intelligent AI assistant** using:
- LLaMA
- RAG
- Vector Stores

Without retraining the model, and without internet access, we achieved:
- Accurate answers
- Safe responses
- A scalable architecture

This approach can be applied to **any business or domain**, not just hotels.

---

✨ End of README

