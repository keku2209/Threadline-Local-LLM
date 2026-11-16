import json
import os
import pickle
import re
from functools import lru_cache
from pathlib import Path
from typing import TypedDict

from dotenv import load_dotenv
from langgraph.graph import END, StateGraph
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline

from .models import Comment, Post

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")
MODEL_NAME = os.getenv("LOCAL_MODEL_NAME", "google/flan-t5-small")
MAX_COMMENTS_FOR_LLM = int(os.getenv("MAX_COMMENTS_FOR_LLM", "18"))
MAX_INPUT_CHARS_PER_COMMENT = int(os.getenv("MAX_INPUT_CHARS_PER_COMMENT", "350"))


class PipelineState(TypedDict):
    comments: list[str]
    cleaned_comments: list[str]
    summary: str


@lru_cache(maxsize=1)
def _local_generator():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    return pipeline("text2text-generation", model=model, tokenizer=tokenizer, device=-1)


def _generate(prompt: str, max_new_tokens: int = 180) -> str:
    result = _local_generator()(prompt, max_new_tokens=max_new_tokens,
                                do_sample=False, truncation=True)
    return str(result[0]["generated_text"]).strip()


def _clean_text(text: str) -> str:
    text = re.sub(r"https?://\S+|www\.\S+", "", text)
    return re.sub(r"\s+", " ", text).strip()


def _clean_node(state: PipelineState) -> dict:
    return {"cleaned_comments": [_clean_text(text) for text in state["comments"]]}


def _summarize_node(state: PipelineState) -> dict:
    return {"summary": "\n".join(state["cleaned_comments"][:MAX_COMMENTS_FOR_LLM])}


def _pipeline():
    graph = StateGraph(PipelineState)
    graph.add_node("clean_comments", _clean_node)
    graph.add_node("summarize", _summarize_node)
    graph.set_entry_point("clean_comments")
    graph.add_edge("clean_comments", "summarize")
    graph.add_edge("summarize", END)
    return graph.compile()


PIPELINE = _pipeline()


def _sentiment_model():
    with (ROOT / "model_pickle").open("rb") as model_file:
        return pickle.load(model_file)


def _safe_json(text: str) -> dict:
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.I)
    try:
        value = json.loads(text)
        return value if isinstance(value, dict) else {}
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            try:
                value = json.loads(text[start:end + 1])
                return value if isinstance(value, dict) else {}
            except json.JSONDecodeError:
                pass
    return {}


def _fallback_analysis(title: str, comments: list[str]) -> dict:
    positive = {"good", "useful", "help", "helpful", "agree", "hope", "better",
                "benefit", "progress", "great", "support"}
    negative = {"bad", "harm", "cheating", "risk", "worse", "problem",
                "against", "wrong", "poor", "disagree"}
    scores = [sum(w in t.lower().split() for w in positive)
              - sum(w in t.lower().split() for w in negative) for t in comments]
    labels = ["Positive" if s > 0 else "Negative" if s < 0 else "Neutral" for s in scores]
    counts = {x: labels.count(x) for x in ("Positive", "Negative", "Neutral")}
    overall = ("Mixed" if counts["Positive"] and counts["Negative"]
               else max(counts, key=counts.get) if comments else "Neutral")
    return {
        "summary": (f"The discussion is about {title}. It contains {len(comments)} "
                    f"comments with different responses. The sentiment results show "
                    f"{overall.lower()} reactions. This is a basic fallback summary."),
        "overall_sentiment": overall,
        "themes": ["discussion responses", "practical impact", "different perspectives"],
        "consensus": "The comments show a range of perspectives; no clear consensus was established.",
        "disagreements": [], "viewpoints": [], "arguments_for": [],
        "arguments_against": [], "important": []
    }


def _analyze_with_local_model(title: str, body: str, comments: list[str]) -> dict:
    sampled = comments[:MAX_COMMENTS_FOR_LLM]
    discussion = "\n".join(
        f"{i}: {text[:MAX_INPUT_CHARS_PER_COMMENT]}" for i, text in enumerate(sampled)
    )
    prompt = (
        "Analyze this online discussion using only the comments as evidence. "
        "Return ONLY one valid JSON object with keys: summary (2-3 short sentences), "
        "overall_sentiment (Positive, Negative, Neutral, or Mixed), themes (up to 3 strings), "
        "consensus (one short sentence), disagreements (up to 2 strings), "
        "viewpoints (objects with name, description, comment_indices), "
        "arguments_for (objects with argument, comment_index), "
        "arguments_against (objects with argument, comment_index), "
        "important (objects with index, reason). Use zero-based comment indices. "
        "Use empty arrays when unsure. Do not invent facts.\n"
        f"POST TITLE: {title[:250]}\nPOST BODY: {body[:400]}\n"
        f"COMMENTS:\n{discussion}\nJSON:"
    )
    return _safe_json(_generate(prompt, max_new_tokens=220))


def analyze_discussion(post: Post, comments: list[Comment]) -> dict:
    valid_comments = [c for c in comments if c.body and c.body.strip()]
    if not valid_comments:
        raise ValueError("This post has no comments to analyze")
    texts = [c.body.replace("\n", " ").strip() for c in valid_comments]
    state = PIPELINE.invoke({"comments": texts, "cleaned_comments": [], "summary": ""})

    provider = f"{MODEL_NAME} (local pretrained inference) + LangGraph + VADER"
    try:
        result = _analyze_with_local_model(post.title, post.body or "", state["cleaned_comments"])
        if not result.get("summary"):
            raise ValueError("Local model did not return a usable summary")
    except Exception as err:
        print(f"[AI_SERVICE] Local model failed; using fallback: {type(err).__name__}: {err}",
              flush=True)
        result = _fallback_analysis(post.title, state["cleaned_comments"])
        provider = f"Local rule-based fallback + VADER (model: {MODEL_NAME})"

    try:
        vader = _sentiment_model()
        labels = []
        for text in state["cleaned_comments"]:
            compound = vader.polarity_scores(text)["compound"]
            labels.append("Positive" if compound >= 0.05 else
                          "Negative" if compound <= -0.05 else "Neutral")
    except Exception as err:
        print(f"[AI_SERVICE] VADER model unavailable: {type(err).__name__}: {err}", flush=True)
        fallback = result.get("overall_sentiment", "Neutral")
        if fallback not in ("Positive", "Negative", "Neutral"):
            fallback = "Neutral"
        labels = [fallback] * len(texts)

    counts = {x: labels.count(x) for x in ("Positive", "Negative", "Neutral")}
    total = len(labels)
    overall = ("Mixed" if counts["Positive"] and counts["Negative"]
               else max(counts, key=counts.get) if total else "Neutral")

    def valid_index(i):
        return isinstance(i, int) and 0 <= i < len(valid_comments)

    viewpoints = []
    for vp in result.get("viewpoints", []) or []:
        if not isinstance(vp, dict) or not isinstance(vp.get("comment_indices", []), list):
            continue
        indices = vp.get("comment_indices", [])
        ids = list(dict.fromkeys(valid_comments[i].id for i in indices
                                 if valid_index(i) and valid_comments[i].id))
        if ids:
            sentiments = [labels[i] for i in indices if valid_index(i)]
            sentiment = ("Mixed" if len(set(sentiments)) > 1 else
                         sentiments[0] if sentiments else "Neutral")
            viewpoints.append({
                "name": str(vp.get("name", "Viewpoint")),
                "description": str(vp.get("description", "")),
                "comment_ids": ids, "sentiment_summary": sentiment
            })

    def map_arguments(key):
        mapped = []
        for item in result.get(key, []) or []:
            if isinstance(item, dict) and valid_index(item.get("comment_index")):
                idx = item["comment_index"]
                mapped.append({"text": str(item.get("argument", "")),
                               "comment_id": valid_comments[idx].id, "supporting_ids": []})
        return mapped

    important = []
    for item in result.get("important", []) or []:
        if isinstance(item, dict) and valid_index(item.get("index")):
            idx = item["index"]
            important.append({"comment_id": valid_comments[idx].id,
                              "reason": str(item.get("reason", ""))})

    agreement = max(counts.values()) / total if total else 0.0
    disagreement = 1.0 - agreement if total else 0.0
    polarization = (min(counts["Positive"], counts["Negative"]) / total
                    if total and counts["Positive"] and counts["Negative"] else 0.0)
    themes = result.get("themes", [])
    disagreements = result.get("disagreements", [])
    if not isinstance(themes, list): themes = []
    if not isinstance(disagreements, list): disagreements = []

    return {
        "post_id": post.id,
        "summary": str(result.get("summary", state["summary"])),
        "overall_sentiment": overall,
        "sentiment_counts": {"positive": counts["Positive"], "negative": counts["Negative"],
                             "neutral": counts["Neutral"]},
        "sentiment_percentages": {
            key.lower(): round(value / total * 100, 1) if total else 0.0
            for key, value in counts.items()
        },
        "themes": [str(x) for x in themes[:5]],
        "viewpoints": viewpoints,
        "consensus": str(result.get("consensus", "")),
        "disagreements": [str(x) for x in disagreements[:4]],
        "arguments_for": map_arguments("arguments_for"),
        "arguments_against": map_arguments("arguments_against"),
        "important_comments": important,
        "discussion_quality": {
            "agreement_level": round(agreement, 2),
            "disagreement_level": round(disagreement, 2),
            "polarization": round(polarization, 2),
            "substantive_discussion": round(min(1.0, total / 5.0), 2)
        },
        "comments_analyzed": total,
        "ai_provider": provider
    }
