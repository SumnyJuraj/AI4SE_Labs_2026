import json
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from openai import OpenAI
from src.config import OPENAI_API_KEY, CONSOLIDATOR_MODEL
from src.state import (
    GraphState,
    Requirement,
    BlacklistedRequirement,
    ExtractedRequirement,
    AuditFeedback
)

class ConsolidationResult(BaseModel):
    requirements: List[Requirement] = Field(
        description="Consolidated, deduplicated requirements with unique IDs, full descriptions, priorities, and source traces"
    )
    blacklisted: List[BlacklistedRequirement] = Field(
        description="Requirements that were discarded due to conflict, impossibility, obsolete nature, or being nonsensical"
    )

def consolidator_node(state: GraphState) -> dict:
    """
    LLM Node 2 (ANS1, ANS4):
    Uses CONSOLIDATOR_MODEL (e.g. gpt-5.6-luna) to merge, deduplicate, prioritize,
    trace, and resolve conflicts from raw requirements.
    Also handles feedback loop revisions from the Critic node (ANS3).
    """
    raw_reqs: List[ExtractedRequirement] = state.get("raw_requirements", [])
    audit_feedback: AuditFeedback = state.get("audit_feedback")
    iteration = state.get("iteration", 0) + 1
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    # Prepare summarized input for consolidation
    # Group raw requirements into a structured text representation
    raw_items_formatted = []
    for i, r in enumerate(raw_reqs, 1):
        raw_items_formatted.append(
            f"Item #{i}:\n- Title: {r.title}\n- Source: {r.source_file}\n- Description: {r.description}\n- Context: {r.context}\n"
        )
    raw_text = "\n".join(raw_items_formatted)
    
    feedback_section = ""
    if audit_feedback and not audit_feedback.approved:
        issues_str = "\n".join(f"- {issue}" for issue in audit_feedback.issues)
        suggestions_str = "\n".join(f"- {sug}" for sug in audit_feedback.suggestions)
        feedback_section = f"""
=== CRITICAL AUDITOR FEEDBACK FROM PREVIOUS ITERATION (Must be resolved!) ===
The Quality Critic identified the following shortcomings that you MUST fix in this iteration:
Issues:
{issues_str}

Actionable Suggestions:
{suggestions_str}
=============================================================================
"""

    prompt = f"""You are a Principal Software Architect and Requirements Engineering Lead consolidating a software specification for the Evergreen Open Source Integrated Library System (ILS).

You are given a raw corpus of {len(raw_reqs)} candidate requirement statements extracted from interviews, emails, minutes, and draft specifications.

{feedback_section}

Your tasks to satisfy output specifications:
1. Deduplication & Semantic Merging (OS3): Identify all semantically overlapping or duplicate requirements and merge them into coherent, single requirements.
2. Unique Identifiers (OS2): Assign clean, structured unique IDs (e.g. REQ-CAT-001, REQ-REP-001, REQ-CIR-001, REQ-SYS-001, REQ-SEC-001).
3. Traceability (OS4): Every single requirement MUST list ALL source files from which it was derived. Do NOT lose source file associations during merging!
4. Clear Title & Paragraph Explanation (OS5): Every requirement must have a concise, descriptive title and a paragraph-long explanation (at least 3-5 sentences) detailing the required behavior, edge cases, and user expectations.
5. MoSCoW Prioritization (OS6): Assign each requirement one of: 'Must Have', 'Should Have', 'Could Have', or 'Won't Have'. Provide a short architectural rationale.
6. Consistency & Terminology (OS7): Ensure uniform terminology across all requirements (e.g., patron, bibliographic record, copy/item, holding branch, circulating vs in-transit). Resolve any contradictions.
7. Completeness (OS8): Ensure all legitimate needs from the input corpus are represented.
8. Blacklist Section (OS9): If any extracted statement is found to be directly contradicting core library principles, technically nonsensical, out-of-scope for the software, or explicitly rejected during meetings/interviews, place it into the 'blacklisted' list. Give a clear, explicit 'reason_for_discarding' and list the source files where it was mentioned.

=== RAW CANDIDATE REQUIREMENTS LIST ===
{raw_text}
=== END OF RAW CANDIDATE REQUIREMENTS ===
"""

    print(f"[Consolidator Node] Running consolidation iteration {iteration} using model: {CONSOLIDATOR_MODEL}...")
    try:
        completion = client.beta.chat.completions.parse(
            model=CONSOLIDATOR_MODEL,
            messages=[
                {"role": "system", "content": "You are an elite Software Requirements Engineer specializing in specification refinement, consistency enforcement, and traceability."},
                {"role": "user", "content": prompt}
            ],
            response_format=ConsolidationResult,
            max_completion_tokens=8000
        )
        result: ConsolidationResult = completion.choices[0].message.parsed
        reqs = result.requirements
        blacklisted = result.blacklisted
    except Exception as e:
        print(f"[Consolidator Node] Beta parse fallback due to: {e}. Using JSON completion...")
        resp = client.chat.completions.create(
            model=CONSOLIDATOR_MODEL,
            messages=[
                {"role": "system", "content": "Return valid JSON matching the schema with 'requirements' and 'blacklisted' lists."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_completion_tokens=8000
        )
        data = json.loads(resp.choices[0].message.content)
        reqs = [Requirement(**item) for item in data.get("requirements", [])]
        blacklisted = [BlacklistedRequirement(**item) for item in data.get("blacklisted", [])]
    
    log_msg = (
        f"[Consolidator Node] Iteration {iteration}: Formed {len(reqs)} consolidated requirements "
        f"and {len(blacklisted)} blacklisted items using {CONSOLIDATOR_MODEL} (LLM node 2 - ANS1, ANS4)."
    )
    print(log_msg)
    
    return {
        "consolidated_requirements": reqs,
        "blacklisted_requirements": blacklisted,
        "iteration": iteration,
        "logs": state.get("logs", []) + [log_msg]
    }
