import os
import email
from email import policy
from pathlib import Path
from typing import List
from src.state import GraphState, DocumentItem

def parse_eml_file(file_path: Path) -> str:
    """Parses an .eml email file into readable text with headers and body."""
    try:
        with open(file_path, "rb") as f:
            msg = email.message_from_binary_file(f, policy=policy.default)
        
        headers = []
        for header in ["From", "To", "Cc", "Subject", "Date"]:
            val = msg.get(header)
            if val:
                headers.append(f"{header}: {val}")
        
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                if ctype == "text/plain":
                    body += part.get_content() + "\n"
        else:
            body = msg.get_content()
        
        header_text = "\n".join(headers)
        return f"{header_text}\n\n{body}".strip()
    except Exception as e:
        # Fallback to plain text read if email parsing fails
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

def parse_txt_file(file_path: Path) -> str:
    """Reads a plain text file."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read().strip()

def ingestion_node(state: GraphState) -> dict:
    """
    Deterministic Node (ANS2):
    Discovers and parses all corpus documents from the specified directory.
    Supports .txt and .eml formats recursively.
    """
    input_dir = Path(state.get("input_dir", "data/corpus"))
    if not input_dir.exists():
        raise FileNotFoundError(f"Corpus directory not found: {input_dir}")
    
    documents: List[DocumentItem] = []
    supported_extensions = {".txt", ".eml"}
    
    # Sort files for deterministic execution order
    all_files = sorted(list(input_dir.rglob("*")))
    
    for p in all_files:
        if p.is_file() and p.suffix.lower() in supported_extensions:
            if p.suffix.lower() == ".eml":
                content = parse_eml_file(p)
            else:
                content = parse_txt_file(p)
            
            if content.strip():
                # Store relative filename or stem for clean traceability
                rel_name = p.name
                documents.append(
                    DocumentItem(
                        file_path=str(p.resolve()),
                        file_name=rel_name,
                        content=content
                    )
                )
    
    log_msg = f"[Ingestion Node] Successfully ingested {len(documents)} documents from {input_dir} (Deterministic node - ANS2)."
    print(log_msg)
    
    return {
        "documents": documents,
        "logs": state.get("logs", []) + [log_msg]
    }
