# 🤖 Chatbot System for E-Commerce Users (GPT-2)

## 📌 Overview
This section of the project focuses on building an **intelligent chatbot assistant** for an e-commerce store.  
The chatbot helps users by answering common questions related to the store such as:
- Store availability
- Delivery and shipping
- Payments
- Returns and refunds
- Customer support

Since **GPT-2 does not have prior knowledge about our specific store**, we fine-tune it on a **custom Question–Answer (Q&A) dataset** related to the e-commerce platform.

---

## 🎯 Objectives
The main goals of this chatbot system are:
1. Provide automated customer support for the e-commerce store
2. Reduce the need for human customer service
3. Demonstrate fine-tuning a Transformer model for domain-specific dialogue
4. Enable natural language interaction with users

---

## 🧠 Why GPT-2?
GPT-2 is a **Transformer-based causal language model** that:
- Predicts the next word based on previous context
- Is well-suited for conversational tasks
- Can be fine-tuned on custom datasets
- Generates human-like text responses

Although GPT-2 is a general model, fine-tuning allows it to adapt to **store-specific knowledge**.

---

## 🗂️ Dataset Description
- Dataset type: **Question & Answer (Q&A)**
- File format: CSV (compressed as ZIP)
- Columns:
  - `question` → User question
  - `answer` → Correct store response

This dataset represents common customer inquiries related to the e-commerce store.

---

## 🔄 Data Loading & Preparation
Steps performed:
1. Mounted Google Drive to access project files
2. Extracted the Q&A dataset from a ZIP file
3. Loaded the CSV file using Hugging Face `datasets`
4. Converted data into a format compatible with Transformers

---

## 🔤 Tokenization
We used the **GPT-2 tokenizer** to:
- Convert text into token IDs
- Apply padding and truncation
- Ensure a fixed input length (`max_length = 128`)

Because GPT-2 does not have a padding token, the **end-of-sentence (EOS) token** was used instead.

---

## 🤖 Model Training (Fine-Tuning GPT-2)
The chatbot was trained using:
- Model: `gpt2`
- Task: **Causal Language Modeling**
- Epochs: 20
- Batch size: 4
- Learning rate: 5e-5

### Key Components Used:
- `AutoModelForCausalLM`
- `DataCollatorForLanguageModeling`
- `TrainingArguments`
- `Trainer`

---

## 💾 Saving the Model
After training:
- The fine-tuned GPT-2 model was saved locally
- The tokenizer was saved alongside the model

This allows reuse of the chatbot **without retraining**.

---

## 💬 Chatbot Inference
A custom function was created to generate responses:
- Accepts a user question
- Encodes the input text
- Generates a response using the fine-tuned GPT-2 model
- Decodes the output into readable text

### Example Questions Tested:
- “Do you have a physical store?”
- “Any physical store?”
- “How can I contact customer support?”
- “What payment methods do you accept?”

---

## ✅ Results
- The chatbot can answer store-related questions automatically
- Similar questions produce consistent responses
- The model demonstrates effective domain adaptation through fine-tuning

---

## ⚠️ Limitations
- GPT-2 may generate short or generic responses
- Some repetition can occur
- The quality depends on the size and quality of the Q&A dataset

---

## 🧩 Role of Transformers
Transformers enabled:
- Context-aware language understanding
- Natural language generation
- Custom fine-tuning for domain-specific dialogue
- Scalable conversational AI for e-commerce platforms
