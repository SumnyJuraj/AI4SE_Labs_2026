import json
from typing import List
from pydantic import BaseModel, Field
from openai import OpenAI
from src.config import OPENAI_API_KEY, CRITIC_MODEL, MAX_FEEDBACK_ITERATIONS
from src.state import GraphState, Requirement, BlacklistedRequirement, AuditFeedback

class AuditResult(BaseModel):
    approved: bool = Field(description="True if quality standards OS1-OS9 are adequately met, False if revisions are required")
    score: int = Field(description="Audit quality score between 0 and 100")
    issues: List[str] = Field(description="Specific issues, inconsistencies, duplicates, or missing traces discovered", default_factory=list)
    suggestions: List[str] = Field(description="Concrete suggestions for the Consolidator node to fix these issues", default_factory=list)

def critic_node(state: GraphState) -> dict:
    """
    LLM Node 3 (ANS1, ANS4) & Feedback Loop Trigger (ANS3):
    Uses CRITIC_MODEL (e.g. gpt-6-luna) to perform deep automated quality auditing
    against all Output Specifications (OS1-OS9).
    If flaws exist and iteration < MAX_FEEDBACK_ITERATIONS, loops back to Consolidator.
    """
    reqs: List[Requirement] = state.get("consolidated_requirements", [])
    blacklisted: List[BlacklistedRequirement] = state.get("blacklisted_requirements", [])
    iteration = state.get("iteration", 1)
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    # Format requirements for review
    formatted_reqs = []
    for r in reqs:
        formatted_reqs.append(
            f"- [{r.id}] {r.title} ({r.priority}) [Sources: {', '.join(r.source_documents)}]\n  Description: {r.description}\n"
        )
    reqs_text = "\n".join(formatted_reqs)
    
    formatted_blk = []
    for b in blacklisted:
        formatted_blk.append(
            f"- [{b.id}] {b.title} [Sources: {', '.join(b.source_documents)}]\n  Reason: {b.reason_for_discarding}\n  Description: {b.description}\n"
        )
    blk_text = "\n".join(formatted_blk) if formatted_blk else "No items currently blacklisted."
    
    prompt = f"""You are the Lead Requirements Auditor and Chief Systems Architect conducting an independent audit of a consolidated software requirements document for the Evergreen ILS.

You must rigorously check the requirements against these specifications:
- OS2 (Unique ID): Every requirement has a distinct, valid ID (e.g., REQ-001 or REQ-CAT-001). No duplicates or missing IDs.
- OS3 (No duplicates): No semantic duplicates or near-identical requirements split into separate entries.
- OS4 (Tracing): Every requirement explicitly cites its source document(s). No empty source lists.
- OS5 (Descriptions): Every requirement has a short title and a substantial paragraph-long explanation (not just 1 brief sentence).
- OS6 (Priority): Every requirement has a clear priority (Must Have, Should Have, Could Have, or Won't Have).
- OS7 (Consistency): Consistent vocabulary (Evergreen ILS concepts), no conflicting requirements.
- OS8 (Completeness): Core subsystems (cataloging, reporting, circulation/patrons, item transfers, deletions/purging) should all be covered.
- OS9 (Blacklist): Conflicting, nonsensical, or out-of-scope items must be placed in the blacklist with clear reasoning.

Iteration Number: {iteration} of max allowed {MAX_FEEDBACK_ITERATIONS}.

=== CONSOLIDATED REQUIREMENTS UNDER REVIEW ===
{reqs_text}

=== BLACKLISTED ITEMS UNDER REVIEW ===
{blk_text}
=== END OF REVIEW DATA ===

Audit Rules:
- If this is iteration 1 and there are semantic duplicates, incomplete descriptions, or empty source traces, be strict: set approved=False, list the exact issues and actionable suggestions.
- If the quality is already high or if minor improvements can be made without failing, or if max iterations ({MAX_FEEDBACK_ITERATIONS}) is reached, set approved=True.
"""

    print(f"[Critic Node] Conducting automated audit (Iteration {iteration}) using reasoning model: {CRITIC_MODEL}...")
    try:
        completion = client.beta.chat.completions.parse(
            model=CRITIC_MODEL,
            messages=[
                {"role": "system", "content": "You are a meticulous Requirements Engineering Quality Auditor evaluating compliance with strict software engineering standards."},
                {"role": "user", "content": prompt}
            ],
            response_format=AuditResult,
            max_completion_tokens=6000
        )
        feedback: AuditResult = completion.choices[0].message.parsed
    except Exception as e:
        print(f"[Critic Node] Beta parse fallback due to: {e}. Using JSON completion...")
        resp = client.chat.completions.create(
            model=CRITIC_MODEL,
            messages=[
                {"role": "system", "content": "Return valid JSON matching the schema with 'approved', 'score', 'issues', and 'suggestions'."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_completion_tokens=4000
        )
        data = json.loads(resp.choices[0].message.content)
        feedback = AuditResult(**data)
    
    # If we hit max iterations, force approval so the network terminates cleanly
    if iteration >= MAX_FEEDBACK_ITERATIONS and not feedback.approved:
        print(f"[Critic Node] Max feedback iterations ({MAX_FEEDBACK_ITERATIONS}) reached. Approving with current notes.")
        feedback.approved = True
        feedback.suggestions.append("Proceeding to final build as maximum feedback iteration count was reached.")
    
    audit_data = AuditFeedback(
        approved=feedback.approved,
        score=feedback.score,
        issues=feedback.issues,
        suggestions=feedback.suggestions
    )
    
    log_msg = (
        f"[Critic Node] Audit completed: Approved={audit_data.approved}, Score={audit_data.score}/100, "
        f"Issues Found={len(audit_data.issues)} (LLM node 3 - ANS1, ANS3, ANS4)."
    )
    print(log_msg)
    
    return {
        "audit_feedback": audit_data,
        "logs": state.get("logs", []) + [log_msg]
    }

def should_continue_feedback_loop(state: GraphState) -> str:
    """
    Conditional Edge router for LangGraph (ANS3):
    Determines whether to loop back to the Consolidator node or proceed to Document Builder.
    """
    feedback = state.get("audit_feedback")
    iteration = state.get("iteration", 1)
    
    if feedback and not feedback.approved and iteration < MAX_FEEDBACK_ITERATIONS:
        print(f"[Routing] Feedback loop triggered: Critic requested revisions (Iteration {iteration}). Looping back to Consolidator...")
        return "loop_back_to_consolidator"
    
    print(f"[Routing] Audit passed or iteration limit reached. Proceeding to Document Builder.")
    return "proceed_to_builder"
