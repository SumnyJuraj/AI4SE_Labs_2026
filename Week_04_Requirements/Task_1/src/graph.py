from langgraph.graph import StateGraph, START, END
from src.state import GraphState
from src.nodes.ingestion import ingestion_node
from src.nodes.extractor import extractor_node
from src.nodes.consolidator import consolidator_node
from src.nodes.critic import critic_node, should_continue_feedback_loop
from src.nodes.builder import builder_node

def create_requirements_graph() -> StateGraph:
    """
    Constructs the LangGraph requirements refinement workflow.
    
    Adheres strictly to all specifications:
    - ANS1: 3 agentic LLM nodes (extractor, consolidator, critic)
    - ANS2: 2 deterministic nodes (ingestion, builder)
    - ANS3: Feedback loop between critic and consolidator
    - ANS4: 3 different LLM models (gpt-4o-mini, gpt-5.6-luna, gpt-6-luna)
    - ANS5: Implemented in LangGraph
    """
    workflow = StateGraph(GraphState)
    
    # 1. Add Nodes
    workflow.add_node("ingestion", ingestion_node)       # ANS2: Deterministic
    workflow.add_node("extractor", extractor_node)       # ANS1 & ANS4: LLM 1 (gpt-4o-mini)
    workflow.add_node("consolidator", consolidator_node) # ANS1 & ANS4: LLM 2 (gpt-5.6-luna)
    workflow.add_node("critic", critic_node)             # ANS1 & ANS4: LLM 3 (gpt-6-luna)
    workflow.add_node("builder", builder_node)           # ANS2: Deterministic
    
    # 2. Add Fixed Edges
    workflow.add_edge(START, "ingestion")
    workflow.add_edge("ingestion", "extractor")
    workflow.add_edge("extractor", "consolidator")
    workflow.add_edge("consolidator", "critic")
    
    # 3. Add Conditional Edge for Feedback Loop (ANS3)
    workflow.add_conditional_edges(
        "critic",
        should_continue_feedback_loop,
        {
            "loop_back_to_consolidator": "consolidator",
            "proceed_to_builder": "builder"
        }
    )
    
    # 4. Finish
    workflow.add_edge("builder", END)
    
    return workflow.compile()
