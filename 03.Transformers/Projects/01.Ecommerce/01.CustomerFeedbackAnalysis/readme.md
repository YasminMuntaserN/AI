# 📦 Customer Feedback Analysis using Transformers (RoBERTa)

## 📌 Project Overview
This project applies **Transformer-based models** to enhance an **e-commerce platform** by automatically analyzing customer feedback.  
The main objective is to classify customer reviews into **Negative**, **Neutral**, or **Positive** sentiments using **RoBERTa**, a powerful Transformer model.

The system helps online stores:
- Understand customer opinions
- Improve decision-making
- Enhance customer experience using AI-driven insights

---

## 🎯 Project Goals
The project focuses on using **Transformers** to:
1. Automatically classify customer reviews (Sentiment Analysis)
2. Improve response speed to customer feedback
3. Enable intelligent decision-making for e-commerce platforms
4. Demonstrate the power of pre-trained Transformer models

---

## 🧠 Why Transformers?
Traditional NLP models struggle with understanding context.  
**Transformers**, especially **RoBERTa**, solve this by:
- Using **self-attention** to understand word relationships
- Capturing long-range dependencies
- Processing text in parallel for better performance

This makes them ideal for sentiment analysis tasks.

---

## 🗂️ Project Structure
```
CustomerFeedbackAnalysis/
│
├── ProductsReviews.zip
    ├── ProductsReviews.csv
├── roberta_base_fine_tuned/ this will be generated 
│   ├── model.safetensors
│   ├── config.json
│   ├── tokenizer files
│
├── CustomerFeedbackAnalysis.ipynb
├── UseModel.ipynb
├── UsePretrainedModel.ipynb
└── README.md
```

---

## 📊 Dataset Description
- Source: Customer product reviews
- Columns used:
  - `reviews.text` → Review content
  - `sentiment` → Original sentiment label

### Sentiment Classes
| Sentiment | Class ID |
|----------|---------|
| Negative | 0 |
| Neutral  | 1 |
| Positive | 2 |

---

## 🔄 Data Preprocessing
Steps performed:
1. Selected relevant columns (`reviews.text`, `sentiment`)
2. Converted sentiment labels into numerical classes
3. Balanced the dataset (300 samples total)
4. Split data into:
   - 80% Training
   - 20% Testing (using stratified sampling)

---

## 🔤 Tokenization
We used **RoBERTa Tokenizer** to:
- Convert text into tokens
- Generate `input_ids`
- Create `attention_mask`
- Ensure consistency between training and inference

---

## 🤖 Model 1: Fine-Tuned RoBERTa
We fine-tuned `roberta-base` for **3-class sentiment classification**.

### Training Setup
- Model: `RobertaForSequenceClassification`
- Epochs: 8
- Batch size: 2
- Evaluation strategy: per epoch
- Metric: Accuracy

### Training Tools
- `Trainer`: Handles the full training loop
- `TrainingArguments`: Controls training behavior
- `accuracy_score`: Measures classification accuracy

---

## 📈 Model Evaluation
The model was evaluated on:
- Training set
- Validation set
- Entire dataset

### Results
| Metric | Accuracy |
|------|---------|
| Train Accuracy | ~81% |
| Validation Accuracy | ~59% |
| Overall Accuracy | ~77% |

⚠️ Neutral sentiment is the hardest class to predict due to ambiguous language.

---

## 💾 Saving the Model
After training, the model and tokenizer were saved locally so they can be reused without retraining.

---

## 🔍 Model Inference (UseModel.ipynb)
The fine-tuned model is loaded and used to classify new customer reviews.

### Example Predictions
| Text | Prediction |
|----|-----------|
| "Awesome product" | Positive |
| "It's okay" | Neutral |
| "Not worth the money" | Negative |

---

## 🚀 Model 2: Pretrained Twitter RoBERTa
To improve performance, a **pre-trained sentiment model** was tested:

```
cardiffnlp/twitter-roberta-base-sentiment
```

### Why This Model?
- Trained on **58+ million tweets**
- No additional training required
- Strong generalization ability

### Result
- Accuracy improved to **~64%**
- Faster and more reliable inference

---

## ⚖️ Model Comparison
| Model | Training Required | Accuracy |
|----|------------------|---------|
| Fine-Tuned RoBERTa | Yes | ~59% (Validation) |
| Pretrained RoBERTa | No | ~64% |

---

## 🧩 Role of Transformers in This Project
Transformers enabled:
- Context-aware sentiment detection
- Understanding of word relationships
- Efficient large-scale text processing
- Transfer learning using pre-trained models

Without Transformers, this level of performance would not be possible.

---


