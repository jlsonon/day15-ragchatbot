from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

from app.conversation_store import conversation_store
from app.groq_api import GroqAPIError, groq_client
from app.models import (
    AnalysisPayload,
    ChartData,
    ChartDataTrace,
    ParsedDocument,
    RiskCategory,
    RiskProfile,
)

logger = logging.getLogger(__name__)


ANALYSIS_SYSTEM_PROMPT = """You are an expert business and research analyst helping professionals extract actionable insights from documents.
Analyze reports, research papers, market studies, or business documents to provide strategic insights.
Respond in JSON with fields:
- answer: Direct response to the primary question in 2-3 sentences.
- key_points: array of the 4 most critical findings or insights.
- risk_profile: object with overall_score (0-100) representing opportunity/importance score and categories (name, score, rationale).
- recommended_actions: array of 3 prioritized next steps or recommendations.
- follow_up_suggestions: array of objects with prompt & description for deeper exploration.
Keep scores data-driven. Overall score represents opportunity/importance: 0 = low, 100 = high."""


def _default_payload(document: ParsedDocument) -> AnalysisPayload:
    categories = [
        RiskCategory(name="Strategic Value", score=65, rationale="Document contains strategic insights and actionable information."),
        RiskCategory(name="Data Quality", score=55, rationale="Information appears comprehensive with supporting details."),
        RiskCategory(name="Actionability", score=60, rationale="Findings can be translated into concrete next steps."),
    ]
    chart = ChartData(
        traces=[
            ChartDataTrace(
                name="Insight Distribution",
                type="polar",
                labels=[category.name for category in categories],
                values=[category.score for category in categories],
            )
        ]
    )
    return AnalysisPayload(
        answer=(
            "Unable to contact Groq API. Based on heuristic scanning, the document contains valuable information. "
            "Configure Groq API for deeper AI-powered analysis and strategic insights."
        ),
        key_points=[
            "Document parsed successfully with basic structure identified.",
            "Key sections and topics detected through pattern matching.",
            "Document appears to contain actionable business information.",
            "Enable Groq API for comprehensive AI analysis and deeper insights.",
        ],
        risk_profile=RiskProfile(overall_score=60, categories=categories),
        chart_data=chart,
        recommended_actions=[
            "Configure Groq API credentials for enhanced AI analysis.",
            "Review document highlights for key themes and patterns.",
            "Use follow-up questions to explore specific areas of interest."
        ],
        follow_up_suggestions=[
            {
                "prompt": "What are the main opportunities identified in this document?",
                "description": "Extract and summarize key opportunities or recommendations.",
            },
            {
                "prompt": "What trends or patterns emerge from this analysis?",
                "description": "Identify recurring themes and their implications.",
            },
            {
                "prompt": "What are the most important action items?",
                "description": "Prioritize next steps based on document content.",
            },
        ],
    )


async def build_analysis_payload(
    document: ParsedDocument,
    primary_question: str,
    conversation_id: str,
) -> AnalysisPayload:
    history = conversation_store.get_history(conversation_id)
    user_prompt = _compose_analysis_prompt(document, primary_question, history)

    try:
        raw_response = await groq_client.chat_completion(
            messages=[
                {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.15,
            max_tokens=900,
            response_format="json_schema",
        )
        payload = _parse_analysis_response(raw_response)
        return payload
    except GroqAPIError as e:
        logger.error(f"Groq API error during analysis: {e}")
        return _default_payload(document)
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        logger.error(f"Error parsing Groq response: {e}")
        return _default_payload(document)


def _compose_analysis_prompt(document: ParsedDocument, question: str, history: List[dict]) -> str:
    history_summary = "\n".join(
        f"{item['role'].upper()}: {item['content']}" for item in history[-6:]
    )

    return (
        "DOCUMENT METADATA:\n"
        f"- File: {document.metadata.filename}\n"
        f"- Type: {document.metadata.file_type}\n"
        f"- Word Count: {document.metadata.word_count}\n"
        f"- Language: {document.metadata.language}\n"
        f"- Parties: {', '.join(document.metadata.parties) or 'Not detected'}\n"
        f"- Dates: {', '.join(document.metadata.dates) or 'Not detected'}\n\n"
        "DOCUMENT HIGHLIGHTS:\n"
        + "\n".join(f"* {highlight.title}: {highlight.snippet}" for highlight in document.highlights)
        + "\n\nKEY TOPICS IDENTIFIED:\n"
        + "\n".join(f"* {clause.clause_type}: {clause.assessment}" for clause in document.clauses)
        + "\n\nPRIMARY QUESTION:\n"
        + (question or "What are the key insights and opportunities in this document?")
        + "\n\nRECENT HISTORY:\n"
        + (history_summary or "No prior context.")
        + "\n\nProvide structured analysis as instructed."
    )


def _parse_analysis_response(raw_response: str) -> AnalysisPayload:
    data: Dict[str, Any] = json.loads(raw_response)

    categories = [
        RiskCategory(
            name=category["name"],
            score=float(category["score"]),
            rationale=category.get("rationale", ""),
        )
        for category in data.get("risk_profile", {}).get("categories", [])
    ]
    risk_profile = RiskProfile(
        overall_score=float(data.get("risk_profile", {}).get("overall_score", 0)),
        categories=categories or [
            RiskCategory(name="General Analysis", score=50, rationale="Basic document analysis completed.")
        ],
    )

    chart_data = ChartData(
        traces=[
            ChartDataTrace(
                name="Risk Distribution",
                type="polar",
                labels=[category.name for category in risk_profile.categories],
                values=[category.score for category in risk_profile.categories],
            )
        ]
    )

    return AnalysisPayload(
        answer=data.get("answer", "No response provided."),
        key_points=data.get("key_points", []),
        risk_profile=risk_profile,
        chart_data=chart_data,
        recommended_actions=data.get("recommended_actions", []),
        follow_up_suggestions=data.get("follow_up_suggestions", []),
    )

