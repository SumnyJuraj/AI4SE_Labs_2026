from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

class DocumentItem(BaseModel):
    file_path: str
    file_name: str
    content: str

class ExtractedRequirement(BaseModel):
    title: str = Field(description="Short descriptive name of candidate requirement")
    description: str = Field(description="Detailed explanation of the requirement")
    source_file: str = Field(description="The exact filename this was extracted from")
    context: str = Field(description="Relevant quote or context snippet from the text", default="")

class Requirement(BaseModel):
    id: str = Field(description="Unique requirement ID (e.g., REQ-001, REQ-FIN-001)")
    title: str = Field(description="Short descriptive name of the requirement")
    description: str = Field(description="Paragraph-long explanation describing the software capability and behavior")
    priority: str = Field(description="Priority: Must Have, Should Have, Could Have, or Won't Have")
    category: str = Field(description="Functional category or subsystem", default="General")
    source_documents: List[str] = Field(description="List of source file names from which this requirement was derived")
    rationale: Optional[str] = Field(description="Reasoning for priority and architectural relevance", default="")

class BlacklistedRequirement(BaseModel):
    id: str = Field(description="Unique blacklist ID (e.g., BLK-001)")
    title: str = Field(description="Short descriptive title of the discarded requirement")
    description: str = Field(description="Explanation of what was proposed")
    reason_for_discarding: str = Field(description="Clear explanation why it was discarded (e.g. conflicting, nonsensical, out-of-scope)")
    source_documents: List[str] = Field(description="Source file names where the discarded requirement was mentioned")

class AuditFeedback(BaseModel):
    approved: bool = Field(description="True if the requirements meet all OS1-OS9 criteria, False if revisions are needed")
    score: int = Field(description="Quality score from 0 to 100", default=100)
    issues: List[str] = Field(description="List of specific issues, inconsistencies, duplicates, or gaps detected", default_factory=list)
    suggestions: List[str] = Field(description="Actionable guidance for the Consolidator node to resolve issues", default_factory=list)

class GraphState(TypedDict):
    input_dir: str
    documents: List[DocumentItem]
    raw_requirements: List[ExtractedRequirement]
    consolidated_requirements: List[Requirement]
    blacklisted_requirements: List[BlacklistedRequirement]
    audit_feedback: Optional[AuditFeedback]
    iteration: int
    final_document: str
    graph_data: Dict[str, Any]
    logs: List[str]
