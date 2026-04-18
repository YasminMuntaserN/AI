# Service Center Customer Satisfaction via Face Emotion Recognition

## Project Overview

This project integrates Artificial Intelligence into a service‑center
environment to estimate customer satisfaction **without surveys**.\
Instead of questionnaires, facial images captured by cameras are
analyzed to infer emotional states such as anger, happiness, or
neutrality.\
The task is framed as an **image classification problem** and solved
using a Vision Transformer (ViT) model fine‑tuned on facial‑emotion
data.

-   Vision Transformers (ViT) are transformer‑based neural networks
    designed for image understanding tasks.\
-   FER2013 dataset is used to train the model for facial emotion
    recognition.

------------------------------------------------------------------------

## Objectives

1.  Explore available ViT models on Hugging Face.
2.  Understand how to use pretrained and fine‑tuned ViT models.
3.  Explore and preprocess the FER2013 dataset.
4.  Fine‑tune ViT for facial emotion classification.
5.  Evaluate and deploy the trained model for prediction.

------------------------------------------------------------------------

## Technologies & Libraries

-   Python
-   PyTorch
-   Hugging Face Transformers
-   Hugging Face Datasets
-   NumPy, Pandas
-   Matplotlib / Seaborn

------------------------------------------------------------------------

## Background

### Vision Transformer (ViT)

The Vision Transformer applies transformer architecture to images by
splitting them into patches and encoding them as tokens.\
It was introduced by Google and trained on large datasets like
ImageNet‑21k (\~14M images, 21k classes).\
It is commonly used as a feature extractor or fine‑tuned for
classification tasks.

Sources:\
- https://arxiv.org/abs/2010.11929\
- https://huggingface.co/docs/transformers/model_doc/vit\
- https://www.image-net.org/index.php

------------------------------------------------------------------------

### FER2013 Dataset

FER2013 is a benchmark dataset for facial emotion recognition containing
grayscale 48×48 images labeled with 7 emotions: - Anger, Disgust, Fear,
Happiness, Sadness, Surprise, Neutral

Images are stored as pixel strings converted back into arrays during
preprocessing.

Source:\
- https://www.kaggle.com/datasets/msambare/fer2013

------------------------------------------------------------------------

## Workflow Summary

### 1️⃣ Model Exploration

-   Loaded pretrained ViT models:
    -   Feature extractor (`vit-base-patch16-224-in21k`)
    -   Image classifier (`vit-base-patch16-224`)
-   Observed pretrained classifier does not correctly classify emotions
    → requires fine‑tuning.

### 2️⃣ Data Preparation

-   Extracted FER2013 CSV
-   Converted pixel strings → arrays
-   Reshaped into images
-   Converted grayscale → RGB format
-   Split dataset:
    -   Training
    -   Validation
    -   Testing
-   Balanced classes through sampling

### 3️⃣ Dataset Conversion

-   Converted processed data into Hugging Face Dataset format
-   Generated `pixel_values` using `ViTImageProcessor`
-   Saved datasets to disk for reuse

### 4️⃣ Model Fine‑Tuning

-   Built custom classification model:
    -   Base ViT encoder
    -   Dropout layer
    -   Linear classifier head
-   Training performed with Hugging Face Trainer
-   Evaluated using accuracy metric

Sources: - https://huggingface.co/docs/transformers/training\
- https://huggingface.co/docs/evaluate

### 5️⃣ Evaluation

-   Computed test accuracy
-   Generated confusion matrix for error analysis

### 6️⃣ Deployment Usage

-   Saved trained model
-   Built function to classify new images
-   Output predicted emotion label

------------------------------------------------------------------------

## Project Structure

    photos/
    datasets/
    train_dataset/
    val_dataset/
    test_dataset/
    preprocessed_* datasets
    model/
    README.md

------------------------------------------------------------------------

## Key Learnings

-   Transformers can be applied beyond NLP into vision tasks.
-   Pretrained models often require domain fine‑tuning.
-   Data preprocessing quality heavily impacts performance.
-   Balanced datasets improve classification fairness.

------------------------------------------------------------------------

## Future Improvements

-   Use larger GPU resources for full dataset training
-   Try ViT variants or CNN‑Transformer hybrids
-   Real‑time camera integration
-   Privacy‑preserving deployment strategies

------------------------------------------------------------------------

## References

-   ViT Paper: https://arxiv.org/abs/2010.11929\
-   Hugging Face ViT Docs:
    https://huggingface.co/docs/transformers/model_doc/vit\
-   Hugging Face Trainer Docs:
    https://huggingface.co/docs/transformers/training\
-   FER2013 Dataset: https://www.kaggle.com/datasets/msambare/fer2013\
-   ImageNet: https://www.image-net.org/index.php
