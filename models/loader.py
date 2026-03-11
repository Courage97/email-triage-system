# model/loader.py
# Handles MobileBERT model loading and caching
# Uses st.cache_resource so the model loads once and stays in memory

import os
import pickle
import streamlit as st

# Absolute path to the project root (one level up from this file's config/)
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH         = os.path.join(_ROOT, 'models', 'mobilebert')
LABEL_ENCODER_PATH = os.path.join(_ROOT, 'preprocessed_data', 'label_encoder.pkl')


@st.cache_resource(show_spinner=False)
def load_models():
    """
    Load MobileBERT model, tokenizer, and label encoder.
    Cached — only runs once per session.

    Returns:
        dict with keys: model, tokenizer, label_encoder, device
    """
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification

    # ── Label encoder ──────────────────────────────────────────────────────
    try:
        with open(LABEL_ENCODER_PATH, 'rb') as f:
            label_encoder = pickle.load(f)
    except FileNotFoundError:
        st.error(f"❌ label_encoder.pkl not found at: {LABEL_ENCODER_PATH}")
        st.stop()
    except Exception as e:
        st.error(f"❌ Failed to load label encoder: {e}")
        st.stop()

    # ── Device ─────────────────────────────────────────────────────────────
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    num_labels = len(label_encoder.classes_)

    # ── Model ──────────────────────────────────────────────────────────────
    try:
        model = AutoModelForSequenceClassification.from_pretrained(
            MODEL_PATH,
            num_labels=num_labels,
            ignore_mismatched_sizes=True
        )
        model.to(device)
        model.eval()
    except Exception as e:
        st.error(f"❌ Failed to load MobileBERT model from {MODEL_PATH}: {e}")
        st.stop()

    # ── Tokenizer ──────────────────────────────────────────────────────────
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    except Exception as e:
        st.error(f"❌ Failed to load tokenizer from {MODEL_PATH}: {e}")
        st.stop()

    return {
        'model':         model,
        'tokenizer':     tokenizer,
        'label_encoder': label_encoder,
        'device':        device,
    }


def get_device_label(models: dict) -> str:
    """Return a clean device string for display — e.g. 'CPU' or 'CUDA (GPU)'."""
    device = str(models['device'])
    if device == 'cpu':
        return 'CPU'
    elif device.startswith('cuda'):
        return 'CUDA (GPU)'
    return device.upper()


def get_num_labels(models: dict) -> int:
    """Return the number of output classes the model was trained on."""
    return len(models['label_encoder'].classes_)


def get_class_labels(models: dict) -> list:
    """Return the list of class label names from the label encoder."""
    return list(models['label_encoder'].classes_)