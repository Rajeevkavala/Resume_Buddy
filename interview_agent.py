"""Interview Q&A generation using local LLM + RAG (simplified placeholder).

This module abstracts:
- Retrieval from vector store
- Prompt building for a local HF model (transformers pipeline)

For performance and licensing reasons, default to a small instruct model; user can override.
"""
from __future__ import annotations
from typing import List

from embedding_utils import VectorStore, load_embedding_model, embed_query

try:
    from transformers import pipeline  # type: ignore
except Exception:  # pragma: no cover
    pipeline = None  # type: ignore

DEFAULT_GEN_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"  # Could be swapped for a smaller model.

SYSTEM_PROMPT = "You are an expert career coach helping to interview candidates based on their resume."


def build_context(store: VectorStore, query: str, top_k: int = 4) -> str:
    model = load_embedding_model(store.model_name)
    q_emb = embed_query(query, model)
    results = store.search(q_emb, top_k=top_k)
    ctx = []
    for _, dist, text in results:
        ctx.append(f"[Chunk d={dist:.2f}]\n{text}")
    return "\n\n".join(ctx)


def _ensure_pipeline(model_name: str):
    if not pipeline:
        raise RuntimeError("transformers not installed. Add to requirements.txt")
    return pipeline("text-generation", model=model_name, device_map="auto", max_new_tokens=512)


def generate_interview_questions(store: VectorStore, num_questions: int = 5, model_name: str = DEFAULT_GEN_MODEL) -> List[str]:
    ctx = build_context(store, "key achievements and responsibilities")
    prompt = (f"{SYSTEM_PROMPT}\nUsing the resume context below, craft {num_questions} concise, role-relevant interview questions.\n" \
              f"Resume Context:\n{ctx}\nQuestions:")
    gen = _ensure_pipeline(model_name)
    out = gen(prompt)[0]['generated_text']
    # crude split
    lines = [l.strip('- ').strip() for l in out.split('\n') if l.strip()]
    questions = []
    for l in lines:
        if l.lower().startswith('question') or l[:2].isdigit() or l.startswith('1.'):
            questions.append(l.split(':',1)[-1].strip())
        elif len(questions) < num_questions and len(l) < 140 and l.endswith('?'):
            questions.append(l)
        if len(questions) >= num_questions:
            break
    return questions[:num_questions]


def generate_sample_answers(store: VectorStore, questions: List[str], model_name: str = DEFAULT_GEN_MODEL) -> List[str]:
    ctx = build_context(store, "professional experience and achievements")
    gen = _ensure_pipeline(model_name)
    answers: List[str] = []
    for q in questions:
        prompt = (f"{SYSTEM_PROMPT}\nResume Context:\n{ctx}\nQuestion: {q}\nProvide a strong, concise sample answer (2-3 sentences). Answer:")
        out = gen(prompt)[0]['generated_text']
        ans = out.split('Answer:')[-1].strip()
        answers.append(ans)
    return answers
