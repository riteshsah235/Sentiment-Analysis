
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class SentimentRequest(BaseModel):
    sentences: list[str]


POSITIVE = {
    "love", "loved", "lovely", "great", "excellent", "amazing",
    "awesome", "wonderful", "fantastic", "good", "happy", "joy",
    "joyful", "delighted", "best", "beautiful", "perfect",
    "enjoy", "enjoyed", "like", "liked", "pleased", "excited",
    "brilliant", "superb", "positive", "success", "successful",
    "recommend", "helpful", "thank", "thanks", "grateful",
    "impressive", "outstanding", "win", "won", "fun"
}

NEGATIVE = {
    "hate", "hated", "terrible", "awful", "horrible", "bad",
    "sad", "unhappy", "angry", "upset", "disappointed",
    "disappointing", "worst", "poor", "ugly", "boring",
    "annoying", "annoyed", "frustrated", "frustrating",
    "fail", "failed", "failure", "wrong", "broken", "useless",
    "pain", "painful", "fear", "scared", "worried", "stress",
    "stressed", "depressed", "miserable", "regret", "problem",
    "problems", "complaint", "complaints", "difficult"
}

NEGATIONS = {
    "not", "never", "no", "hardly", "isn't", "wasn't",
    "don't", "doesn't", "didn't", "cannot", "can't",
    "won't", "without"
}

INTENSIFIERS = {
    "very", "really", "extremely", "absolutely", "so",
    "incredibly", "too"
}


def analyze_sentiment(sentence: str) -> str:
    text = sentence.lower()
    words = re.findall(r"[a-z]+(?:'[a-z]+)?", text)

    # Handle common sentiment phrases.
    if any(p in text for p in [
        "looking forward to", "can't wait", "cannot wait",
        "thank you", "well done"
    ]):
        return "happy"

    if any(p in text for p in [
        "not good", "not great", "not happy", "not satisfied",
        "not impressed", "not worth", "no good",
        "very bad", "really bad", "waste of time"
    ]):
        return "sad"

    positive_score = 0
    negative_score = 0

    for i, word in enumerate(words):
        if word in POSITIVE:
            score = 1
            if i > 0 and words[i - 1] in INTENSIFIERS:
                score += 1

            if i > 0 and words[i - 1] in NEGATIONS:
                negative_score += score
            else:
                positive_score += score

        elif word in NEGATIVE:
            score = 1
            if i > 0 and words[i - 1] in INTENSIFIERS:
                score += 1

            if i > 0 and words[i - 1] in NEGATIONS:
                positive_score += score
            else:
                negative_score += score

    if positive_score > negative_score:
        return "happy"
    if negative_score > positive_score:
        return "sad"
    return "neutral"


@app.get("/")
def root():
    return {"status": "ok", "endpoint": "/sentiment"}


@app.post("/sentiment")
def sentiment(request: SentimentRequest):
    return {
        "results": [
            {
                "sentence": sentence,
                "sentiment": analyze_sentiment(sentence)
            }
            for sentence in request.sentences
        ]
    }
