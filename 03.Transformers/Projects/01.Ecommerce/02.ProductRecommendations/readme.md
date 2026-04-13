# 📦 User Product Recommendation System using Sentence Transformers

## 📌 Project Overview
This project demonstrates a **semantic product recommendation system** for an e-commerce platform.
It uses **Sentence Transformers (SBERT)** to generate **sentence embeddings** for products, allowing recommendations based on **meaning**, rather than exact keyword matches.

The system helps online stores:
- Suggest relevant products to customers based on their queries
- Enhance customer experience through AI-driven recommendations
- Improve search quality using semantic understanding

---

## 🎯 Project Goals
The main goals of this project are to:
1. Generate **semantic embeddings** for product information using Sentence Transformers
2. Provide **meaning-based product recommendations** for user queries
3. Demonstrate the use of **precomputed embeddings** for efficient inference
4. Build a scalable recommendation system for large e-commerce catalogs

---

## 🧠 Why Sentence Transformers?
Traditional keyword-based search fails when:
- User queries use different words than product descriptions
- Synonyms or paraphrasing are involved

**Sentence Transformers (SBERT)** solve this by:
- Generating embeddings for **entire sentences or product descriptions**
- Ensuring semantically similar text has **numerically close embeddings**
- Allowing **cosine similarity** to rank products by meaning

This makes them ideal for **semantic product recommendations**.

---

## 🗂️ Project Structure
```
ProductRecommendationSystem/
│
├── flipkart_com-ecommerce_sample.zip
l   ├── fipkart_com-ecommerce_sample.csv
├── embeddings.npy this will be generated 
├── ProductRecommendation.ipynb
├── UseModel.ipynb
└── README.md
```

---

## 📊 Dataset Description
- Source: Flipkart e-commerce product dataset
- Columns used:
  - `product_name` → Name of the product
  - `description` → Product description
  - `product_specifications` → Key-value pairs of technical specs

---

## 🔄 Data Preprocessing
Steps performed:
1. Loaded CSV dataset into Pandas DataFrame
2. Converted all columns to **strings** and **lowercase**
3. Extracted **key-value specifications** from `product_specifications` using regex
4. Removed **special characters**, keeping only letters and numbers
5. Combined all product info into a single column `combined_text`:
   ```
   combined_text = product_name + description + product_specifications
   ```

---

## 🔤 Sentence Embeddings
1. **Load Sentence Transformer model**
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-mpnet-base-v2')
```
2. **Generate embeddings for products**
```python
sentence_embeddings = model.encode(df['combined_text'].tolist())
```
- Each product is represented by a **768-dimensional numerical vector**
- Semantically similar products have **closer embeddings**

3. **Save embeddings for reuse**
```python
import numpy as np
np.save("embeddings.npy", sentence_embeddings)
```
- Avoids recomputation and improves **inference efficiency**

---

## 🤖 Product Recommendation
The recommendation system works by:
1. Taking **user input** as a query
2. Cleaning text (lowercase, remove special characters)
3. Generating **embedding for the query**
4. Calculating **cosine similarity** with all product embeddings
5. Returning **top N recommended products**

```python
from sklearn.metrics.pairwise import cosine_similarity
import re

def get_products(user_input, sentence_embeddings, model, df, num_recommendations=10):
    user_input = re.sub('[^A-Za-z0-9]+', ' ', user_input).lower()
    user_input_embedding = model.encode([user_input])
    similarities = cosine_similarity(user_input_embedding, sentence_embeddings)[0]
    top_indices = similarities.argsort()[::-1][:num_recommendations]
    return df.iloc[top_indices]['product_name']
```

---

## 📈 Example
```python
user_input = "bluetooth wireless headphones"
recommended_products = get_products(user_input, sentence_embeddings, model, df)

print("Recommendations for \"", user_input, "\" are:")
print(recommended_products)
```
- Returns **semantically closest products** based on user query
- Works even if product descriptions use different wording

---

## ⚖️ Key Features
- **Semantic search:** Finds products based on meaning, not exact words
- **Efficient inference:** Uses precomputed embeddings
- **Scalable:** Handles large product catalogs
- **Accurate recommendations:** Handles synonyms and paraphrased queries

---

## 🧩 Role of Transformers in This Project
Sentence Transformers enable:
- **Context-aware embeddings** of product text
- **Meaning-based similarity** search
- **Efficient large-scale recommendation**
- **Transfer learning** with pre-trained models

Without Transformers, this level of semantic recommendation would not be achievable.

---

## ✅ Conclusion
This project demonstrates how **Sentence Transformers** can enhance **product recommendations** in e-commerce platforms.  
By leveraging semantic embeddings, the system provides **accurate, scalable, and efficient recommendations** that improve the customer experience.

---
