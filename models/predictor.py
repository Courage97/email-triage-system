# model/predictor.py
# Handles text cleaning and email classification inference
# Depends on: model/loader.py

import re
import time
import numpy as np


def clean_text(text: str) -> str:
    """
    Clean and normalize raw email text before tokenization.

    Steps:
        - Lowercase
        - Remove email addresses
        - Remove URLs
        - Strip HTML tags
        - Collapse whitespace

    Args:
        text: Raw email string

    Returns:
        Cleaned string
    """
    if not text:
        return ""
    text = str(text).lower()
    text = re.sub(r'\S+@\S+', '', text)           # remove emails
    text = re.sub(r'http\S+|www\S+', '', text)     # remove URLs
    text = re.sub(r'<.*?>', '', text)              # strip HTML tags
    text = re.sub(r'[^\w\s.,!?]', ' ', text)      # remove special chars
    text = re.sub(r'\s+', ' ', text).strip()       # collapse whitespace
    return text


def predict_email(text: str, models: dict) -> dict:
    """
    Run MobileBERT inference on an email string.

    Args:
        text:   Raw email text (subject + body combined)
        models: Dict returned by load_models()

    Returns:
        dict with keys:
            - category      (str)   predicted label
            - confidence    (float) 0.0 – 1.0
            - probabilities (np.ndarray) softmax scores for all classes
            - class_id      (int)   predicted class index
            - elapsed_ms    (str)   inference time in milliseconds
            - all_labels    (list)  ordered list of all class names
    """
    import torch

    cleaned = clean_text(text)

    # ── Tokenize ───────────────────────────────────────────────────────────
    encoding = models['tokenizer'](
        cleaned,
        add_special_tokens=True,
        max_length=128,
        padding='max_length',
        truncation=True,
        return_attention_mask=True,
        return_token_type_ids=True,
        return_tensors='pt'
    )

    input_ids      = encoding['input_ids'].to(models['device'])
    attention_mask = encoding['attention_mask'].to(models['device'])
    token_type_ids = encoding['token_type_ids'].to(models['device'])

    # ── Inference ──────────────────────────────────────────────────────────
    t0 = time.time()
    with torch.no_grad():
        outputs = models['model'](
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids
        )
        probs = torch.softmax(outputs.logits, dim=1)
        pred  = torch.argmax(probs, dim=1).item()
    elapsed_ms = f"{(time.time() - t0) * 1000:.0f}"

    # ── Extract results ────────────────────────────────────────────────────
    confidence  = float(probs[0][pred].item())
    all_probs   = probs[0].cpu().numpy()
    all_labels  = list(models['label_encoder'].classes_)
    label       = models['label_encoder'].inverse_transform([pred])[0]

    return {
        'category':      label,
        'confidence':    confidence,
        'probabilities': all_probs,
        'class_id':      pred,
        'elapsed_ms':    elapsed_ms,
        'all_labels':    all_labels,
    }


def build_probability_table(result: dict) -> list[dict]:
    """
    Convert raw probabilities into a sorted list of dicts for display.

    Args:
        result: Dict returned by predict_email()

    Returns:
        List of dicts sorted by probability descending:
            [{ 'category': str, 'probability': float, 'percentage': str }, ...]
    """
    rows = [
        {
            'category':    label,
            'probability': float(result['probabilities'][i]),
            'percentage':  f"{result['probabilities'][i] * 100:.2f}%",
        }
        for i, label in enumerate(result['all_labels'])
    ]
    return sorted(rows, key=lambda x: x['probability'], reverse=True)


def combine_subject_body(subject: str, body: str) -> str:
    """
    Merge subject and body into a single string for inference.
    Subject is weighted by prepending it twice so the model
    treats it as more important than body text.

    Args:
        subject: Email subject line
        body:    Email body text

    Returns:
        Combined string
    """
    subject = subject.strip()
    body    = body.strip()

    if subject and body:
        return f"{subject} {subject} {body}"
    elif subject:
        return subject
    elif body:
        return body
    return ""