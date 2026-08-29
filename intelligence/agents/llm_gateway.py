"""ThermalEye — Multi-Provider LLM Gateway with Zero-Failure Fallback.

Fallback Hierarchy:
1. NVIDIA NIM (meta/llama-3.1-70b-instruct) — Ultra-fast inference
2. Google Gemini (gemini-2.0-flash)
3. Groq (llama-3.1-70b-versatile)
4. Deterministic Rule-Based Fact Generator (100% Offline, Zero API Failures)

Invariant #1: "Deterministic Arithmetic Ranks, LLM Only Explains."
The LLM is strictly prohibited from altering classification categories, confidence
scores, or numbers. It only produces concise briefing text.
"""
import os
import json
from typing import Dict, Any, Optional

from shared.config import LLM_PROVIDERS


def synthesize_briefing_llm(
    cluster_id: str,
    category: str,
    confidence: float,
    evidence_chain: Dict[str, str],
    regulatory_recommendation: str,
    district_name: str
) -> str:
    """Generate an authoritative 2-sentence regulatory briefing."""
    fallback_text = (
        f"Thermal anomaly {cluster_id} in {district_name} is confirmed as a {category.replace('_', ' ').upper()} "
        f"({confidence*100:.1f}% confidence) based on {evidence_chain.get('temporal', '')}. "
        f"Action: {regulatory_recommendation}"
    )

    # 1. Try NVIDIA NIM (Primary)
    nim_key = os.environ.get("NVIDIA_NIM_KEY")
    if nim_key:
        try:
            from openai import OpenAI
            client = OpenAI(
                base_url=LLM_PROVIDERS["nvidia_nim"]["base_url"],
                api_key=nim_key,
                timeout=4.0
            )
            prompt = f"""You are ThermalEye, an AI thermal intelligence system for regulators.
Summarize the following verified thermal evidence into exactly 2 concise, professional sentences:
Cluster ID: {cluster_id}
Category: {category} ({confidence*100:.1f}% confidence)
District: {district_name}
Evidence: {json.dumps(evidence_chain)}
Action: {regulatory_recommendation}

Do not invent facts. Stay strictly within the evidence provided."""

            resp = client.chat.completions.create(
                model=LLM_PROVIDERS["nvidia_nim"]["model"],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.2
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"[llm] NVIDIA NIM failed ({e}) -> Trying Gemini...")

    # 2. Try Google Gemini (Fallback 1)
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        try:
            from openai import OpenAI
            client = OpenAI(
                base_url=LLM_PROVIDERS["gemini"]["base_url"],
                api_key=gemini_key,
                timeout=4.0
            )
            resp = client.chat.completions.create(
                model=LLM_PROVIDERS["gemini"]["model"],
                messages=[{
                    "role": "user",
                    "content": f"Summarize in 2 crisp sentences for regulatory inspector: {cluster_id} is {category} in {district_name}. Evidence: {evidence_chain}. Recommendation: {regulatory_recommendation}"
                }],
                max_tokens=150,
                temperature=0.2
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"[llm] Gemini failed ({e}) -> Trying Groq...")

    # 3. Try Groq (Fallback 2)
    groq_key = os.environ.get("GROQ_API_KEY")
    if groq_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_key, timeout=4.0)
            resp = client.chat.completions.create(
                model=LLM_PROVIDERS["groq"]["model"],
                messages=[{
                    "role": "user",
                    "content": f"Briefing in 2 sentences: {cluster_id} is {category} ({confidence:.0%}) in {district_name}. {evidence_chain} Action: {regulatory_recommendation}"
                }],
                max_tokens=150,
                temperature=0.2
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"[llm] Groq failed ({e}) -> Using deterministic fallback.")

    # 4. Deterministic Fallback (Offline Zero-Failure)
    return fallback_text
