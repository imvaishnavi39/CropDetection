import os
import re
from typing import Dict, List, Tuple


def _normalize(text: str) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


FAQ: List[Tuple[List[str], str]] = [
    (
        ["hi", "hello", "hey", "hii", "hy"],
        "Hello! I'm CropCare AI assistant. Ask me about supported crops, how to upload, or how predictions work.",
    ),
    (
        ["how to use", "how do i use", "upload", "scan", "detect", "prediction"],
        "To use CropCare AI: go to Home -> upload a clear leaf image (JPG/PNG/GIF, <=5MB) -> click \"Analyze Image\". You'll see the disease name, confidence, and probabilities.",
    ),
    (
        ["supported crop", "crop variety", "which crops", "supported crops"],
        "This demo currently classifies leaf images into 4 labels (Healthy, Powdery Mildew, Rust, Leaf Spot). If you plug in your own trained model, you can support more crops and diseases.",
    ),
    (
        ["accuracy", "confidence", "how accurate", "reliable"],
        "The shown confidence is the model's probability estimate. For best results, upload a well-lit, close-up leaf image (no heavy blur). For production, retrain/validate with local crop datasets.",
    ),
    (
        ["treatment", "suggestion", "what to do", "recommendation"],
        "The results page includes general recommendations. For real-world use, always confirm with local agronomy guidance and consider region/crop-specific factors.",
    ),
    (
        ["contact", "support", "help"],
        "You can reach us via the Contact page. If you found an issue or have an improvement idea, the Feedback page is perfect too.",
    ),
]


def answer_local(message: str) -> Dict[str, str]:
    text = _normalize(message)
    if not text:
        return {"reply": "Please type a message and I'll help."}

    for keywords, reply in FAQ:
        if any(k in text for k in keywords):
            return {"reply": reply}

    return {
        "reply": (
            "I can help with: how to upload, what the labels mean, confidence/accuracy, "
            "supported crops, and next steps. Try asking: \"How do I upload an image?\""
        )
    }


def answer_message(message: str) -> Dict[str, str]:
    """
    Uses Gemini if GEMINI_API_KEY is set, otherwise falls back to a local FAQ.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        try:
            import google.generativeai as genai

            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel(
                "gemini-1.5-flash",
                system_instruction=(
                    "You are CropCare AI assistant for a crop disease detection demo website. "
                    "Be concise, helpful, and practical. "
                    "Do not claim medical certainty. "
                    "If asked for treatment, provide general best-practice guidance and advise consulting local agronomy experts."
                ),
            )
            resp = model.generate_content(message)
            text = getattr(resp, "text", "") or ""
            text = text.strip()
            if text:
                return {"reply": text}
        except Exception:
            # If Gemini fails (missing dependency, bad key, network), fall back to local FAQ.
            pass

    return answer_local(message)

