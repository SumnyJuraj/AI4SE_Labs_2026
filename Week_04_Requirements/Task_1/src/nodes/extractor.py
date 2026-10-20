import json
from typing import List
from pydantic import BaseModel, Field
from openai import OpenAI
from src.config import OPENAI_API_KEY, EXTRACTOR_MODEL
from src.state import GraphState, ExtractedRequirement, DocumentItem

class ExtractionResult(BaseModel):
    requirements: List[ExtractedRequirement] = Field(
        description="List of extracted candidate requirements from the text"
    )

def extract_from_single_doc(client: OpenAI, doc: DocumentItem, model: str) -> List[ExtractedRequirement]:
    """Extract candidate software requirements from a single document using LLM."""
    prompt = f"""You are an expert Software Requirements Engineer extracting candidate requirements from project communications and notes.

Document Name: {doc.file_name}

=== Document Content ===
{doc.content}
=== End of Document ===

Instructions:
1. Thoroughly identify ALL software requirements, functional capabilities, business rules, system constraints, performance needs, user workflows, and reporting requirements described in this document.
2. For each requirement, provide:
   - title: concise descriptive title (e.g., 'Real-time Item Status Purging', 'Patron Balance Ledger')
   - description: detailed description of the capability needed by users or system administrators
   - source_file: must be exactly '{doc.file_name}'
   - context: brief quote or context sentence from the document supporting this requirement
3. Do not omit any subtle requirement (completeness is critical).
"""
    try:
        completion = client.beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system", "content": "You extract software requirements from raw documents with high fidelity and strict traceability."},
                {"role": "user", "content": prompt}
            ],
            response_format=ExtractionResult
        )
        return completion.choices[0].message.parsed.requirements
    except Exception as e:
        # Fallback to json mode if beta parse fails
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Return valid JSON with a 'requirements' list of objects having title, description, source_file, and context."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_completion_tokens=4000
            )
            data = json.loads(resp.choices[0].message.content)
            reqs = []
            for item in data.get("requirements", []):
                reqs.append(ExtractedRequirement(
                    title=item.get("title", "Untitled"),
                    description=item.get("description", ""),
                    source_file=doc.file_name,
                    context=item.get("context", "")
                ))
            return reqs
        except Exception as inner_e:
            print(f"[Extractor Node] Warning: Extraction failed for {doc.file_name}: {inner_e}")
            return []

def extractor_node(state: GraphState) -> dict:
    """
    LLM Node 1 (ANS1, ANS4):
    Uses EXTRACTOR_MODEL (e.g. gpt-4o-mini) to thoroughly extract candidate
    requirements from each document in the corpus.
    Ensures complete coverage (OS8) and initial source tracing (OS4).
    """
    documents = state.get("documents", [])
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    all_extracted: List[ExtractedRequirement] = []
    
    print(f"[Extractor Node] Starting parallel extraction across {len(documents)} documents using model: {EXTRACTOR_MODEL}...")
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_doc = {
            executor.submit(extract_from_single_doc, client, doc, EXTRACTOR_MODEL): doc
            for doc in documents
        }
        for future in as_completed(future_to_doc):
            doc = future_to_doc[future]
            try:
                extracted = future.result()
                print(f"  [Extracted {len(extracted)} reqs] from {doc.file_name}")
                all_extracted.extend(extracted)
            except Exception as exc:
                print(f"  [Extractor Error] {doc.file_name} generated an exception: {exc}")
    
    log_msg = f"[Extractor Node] Extracted {len(all_extracted)} raw requirements from {len(documents)} documents using {EXTRACTOR_MODEL} (LLM node 1 - ANS1, ANS4)."
    print(log_msg)
    
    return {
        "raw_requirements": all_extracted,
        "logs": state.get("logs", []) + [log_msg]
    }
