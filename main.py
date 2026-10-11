
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


POSITIVE_WORDS = {
    "love", "loved", "lovely", "great", "excellent", "amazing",
    "awesome", "wonderful", "fantastic", "good", "happy", "joy",
    "joyful", "delighted", "best", "beautiful", "perfect",
    "enjoy", "enjoyed", "like", "liked", "pleased", "excited",
    "brilliant", "superb", "positive", "success", "successful",
    "recommend", "helpful", "thank", "thanks", "grateful",
    "impressive", "outstanding", "win", "won", "fun", "nice",
    "favorite", "favourite", "smile", "smiling", "glad", "hopeful",
    "incredible", "satisfied", "pleasant", "cool", "delightful",
    "comfortable", "easy", "beautifully", "enjoyable", "cheerful",
    "thrilled", "proud", "peaceful", "kind", "better", "improved"
}

NEGATIVE_WORDS = {
    "hate", "hated", "terrible", "awful", "horrible", "bad",
    "sad", "unhappy", "angry", "upset", "disappointed",
    "disappointing", "worst", "poor", "ugly", "boring",
    "annoying", "annoyed", "frustrated", "frustrating",
    "fail", "failed", "failure", "wrong", "broken", "useless",
    "pain", "painful", "fear", "scared", "worried", "stress",
    "stressed", "depressed", "miserable", "regret", "problem",
    "problems", "complaint", "complaints", "difficult", "badly",
    "dislike", "disliked", "disgusting", "disaster", "annoy",
    "annoyance", "sadly", "unfortunately", "unpleasant", "confused",
    "confusing", "hard", "worse", "worried", "anxious", "nervous",
    "failures", "hateable", "frightened", "lonely", "hurt",
    "horrendous", "inferior", "mediocre", "inadequate"
}

NEGATIONS = {
    "not", "never", "no", "hardly", "isn't", "wasn't",
    "don't", "doesn't", "didn't", "cannot", "can't",
    "won't", "without"
}

POSITIVE_PHRASES = [
    "looking forward", "can't wait", "cannot wait",
    "thank you", "well done", "works perfectly",
    "very satisfied", "highly recommend", "love it",
    "good job", "feel better", "so happy"
]

NEGATIVE_PHRASES = [
    "not good", "not great", "not happy", "not satisfied",
    "not impressed", "not worth", "no good", "very bad",
    "really bad", "waste of time", "fed up", "sick of",
    "not working", "doesn't work", "does not work",
    "never again", "not recommend", "poor quality",
    "very disappointed", "feel terrible", "hate it"
]


def analyze_sentiment(sentence: str) -> str:
    text = sentence.lower()
    words = re.findall(r"[a-z]+(?:'[a-z]+)?", text)

    for phrase in NEGATIVE_PHRASES:
        if phrase in text:
            return "sad"

    for phrase in POSITIVE_PHRASES:
        if phrase in text:
            return "happy"

    positive_score = 0
    negative_score = 0

    for i, word in enumerate(words):
        previous = words[i - 1] if i > 0 else ""

        if word in POSITIVE_WORDS:
            if previous in NEGATIONS:
                negative_score += 1
            else:
                positive_score += 1

        elif word in NEGATIVE_WORDS:
            if previous in NEGATIONS:
                positive_score += 1
            else:
                negative_score += 1

    if positive_score > negative_score:
        return "happy"
    if negative_score > positive_score:
        return "sad"

    return "neutral"


@app.get("/")
def root():
    return {"status": "ok"}


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
