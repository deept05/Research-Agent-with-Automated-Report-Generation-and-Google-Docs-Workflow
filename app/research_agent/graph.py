"""
LangGraph workflow definition for research agent.
"""
from langgraph.graph import StateGraph, END
from app.research_agent.state import ResearchState
from app.research_agent.nodes import (
    query_intake_node,
    web_search_node,
    content_filter_node,
    content_extraction_node,
    synthesizer_node,
    citation_handler_node,
    report_generator_node,
    error_handler_node
)
from app.utils.logger import app_logger


def should_continue(state: ResearchState) -> str:
    """
    Determine if workflow should continue or handle error.
    
    Args:
        state: Current research state
        
    Returns:
        Next node to execute
    """
    if state.get("error_message"):
        return "error_handler"
    return "continue"


def build_research_graph() -> StateGraph:
    """
    Build and compile the research workflow graph.
    
    Returns:
        Compiled LangGraph workflow
    """
    app_logger.info("Building research workflow graph")
    
    # Create graph
    workflow = StateGraph(ResearchState)
    
    # Add nodes
    workflow.add_node("query_intake", query_intake_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("content_filter", content_filter_node)
    workflow.add_node("content_extraction", content_extraction_node)
    workflow.add_node("synthesizer", synthesizer_node)
    workflow.add_node("citation_handler", citation_handler_node)
    workflow.add_node("report_generator", report_generator_node)
    workflow.add_node("error_handler", error_handler_node)
    
    # Set entry point
    workflow.set_entry_point("query_intake")
    
    # Add edges
    workflow.add_conditional_edges(
        "query_intake",
        should_continue,
        {
            "continue": "web_search",
            "error_handler": "error_handler"
        }
    )
    
    workflow.add_conditional_edges(
        "web_search",
        should_continue,
        {
            "continue": "content_filter",
            "error_handler": "error_handler"
        }
    )
    
    workflow.add_conditional_edges(
        "content_filter",
        should_continue,
        {
            "continue": "content_extraction",
            "error_handler": "error_handler"
        }
    )
    
    workflow.add_conditional_edges(
        "content_extraction",
        should_continue,
        {
            "continue": "synthesizer",
            "error_handler": "error_handler"
        }
    )
    
    workflow.add_conditional_edges(
        "synthesizer",
        should_continue,
        {
            "continue": "citation_handler",
            "error_handler": "error_handler"
        }
    )
    
    workflow.add_conditional_edges(
        "citation_handler",
        should_continue,
        {
            "continue": "report_generator",
            "error_handler": "error_handler"
        }
    )
    
    workflow.add_edge("report_generator", END)
    workflow.add_edge("error_handler", END)
    
    # Compile graph
    app = workflow.compile()
    
    app_logger.info("Research workflow graph compiled successfully")
    return app


# Create the compiled graph instance
research_graph = build_research_graph()