import argparse
import sys
from pathlib import Path
from src.graph import create_requirements_graph
from src.state import GraphState

def main():
    parser = argparse.ArgumentParser(
        description="Agentic Network for Software Requirements Refinement (LangGraph)"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="data/corpus",
        help="Path to input corpus directory containing .txt and .eml documents (default: data/corpus)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="requirements.md",
        help="Path to output markdown file (default: requirements.md)"
    )
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input directory '{args.input}' does not exist.", file=sys.stderr)
        sys.exit(1)
        
    print("=" * 70)
    print("  AGENTIC REQUIREMENTS REFINEMENT NETWORK (LangGraph)")
    print(f"  Input Directory : {input_path.resolve()}")
    print(f"  Output File     : {args.output}")
    print("=" * 70)
    
    app = create_requirements_graph()
    
    initial_state: GraphState = {
        "input_dir": str(input_path),
        "documents": [],
        "raw_requirements": [],
        "consolidated_requirements": [],
        "blacklisted_requirements": [],
        "audit_feedback": None,
        "iteration": 0,
        "final_document": "",
        "graph_data": {},
        "logs": []
    }
    
    result = app.invoke(initial_state)
    
    out_file = Path(args.output)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(result["final_document"])
        
    print("\n" + "=" * 70)
    print(f" Refinement Pipeline Finished Successfully!")
    print(f" Output SRS document written to: {out_file.resolve()}")
    print(f" Total Consolidated Requirements: {len(result['consolidated_requirements'])}")
    print(f" Total Blacklisted Proposals: {len(result['blacklisted_requirements'])}")
    print(f" Graph data saved to: requirements_graph.json")
    print("=" * 70)

if __name__ == "__main__":
    main()
