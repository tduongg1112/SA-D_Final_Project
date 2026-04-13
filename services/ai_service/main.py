from fastapi import FastAPI
from pydantic import BaseModel

from knowledge_base import PRODUCT_KNOWLEDGE

app = FastAPI(title="TechStore AI Service")


class ChatRequest(BaseModel):
    message: str


def match_products(message: str):
    message_lower = message.lower()
    matches = []
    for product in PRODUCT_KNOWLEDGE:
        if any(tag in message_lower for tag in product["tags"]):
            matches.append(product)
    return matches or PRODUCT_KNOWLEDGE[:2]


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/ai/chat/")
def ai_chat(payload: ChatRequest):
    matches = match_products(payload.message)
    recommendations = ", ".join(item["name"] for item in matches[:3])
    summaries = " ".join(item["summary"] for item in matches[:2])
    answer = (
        f"Based on '{payload.message}', I recommend starting with {recommendations}. "
        f"{summaries}"
    )
    return {
        "answer": answer,
        "matched_products": [item["name"] for item in matches[:3]],
    }
