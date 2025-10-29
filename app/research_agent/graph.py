"""
LangGraph workflow definition for research agent.
"""
"""LangGraph workflow definition for research agent.

This module tries to use langgraph when available. If langgraph is not
available or its API is incompatible (import errors like missing
CheckpointAt), we fall back to a lightweight sequential executor that
runs the same node functions in order. This keeps the project runnable
without requiring a specific langgraph version.
"""

from typing import Any, Dict

try:
    from langgraph.graph import StateGraph, END  # type: ignore
    LANGGRAPH_AVAILABLE = True
except Exception:
    StateGraph = None  # type: ignore
    END = None  # type: ignore
    LANGGRAPH_AVAILABLE = False

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

    # Try to build using langgraph if available. Do a runtime import/use inside
    # a try/except so any incompatibility inside langgraph (different versions
    # that raise import errors for internal symbols like CheckpointAt) will be
    # caught and we will fall back to the MinimalGraph implementation.
    try:
        if not (LANGGRAPH_AVAILABLE and StateGraph is not None):
            raise Exception("langgraph not available")

        # Create graph using langgraph
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

        # Add edges (conditional transitions)
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

        app_logger.info("Research workflow graph compiled successfully (langgraph)")
        return app
    except Exception as e:
        # Any exception when importing/using langgraph (including internal
        # import errors) will be handled here and the fallback executor used.
        app_logger.exception("langgraph import/use failed, falling back: %s", e)

    # Fallback: minimal sequential executor when langgraph is not usable
    app_logger.warning("langgraph unavailable or incompatible — using fallback executor")

    class MinimalGraph:
        def __init__(self):
            self.nodes = [
                query_intake_node,
                web_search_node,
                content_filter_node,
                content_extraction_node,
                synthesizer_node,
                citation_handler_node,
                report_generator_node,
            ]

        def invoke(self, state: Dict[str, Any]):
            # Run nodes sequentially, updating state dict
            for node in self.nodes:
                try:
                    result = node(state)
                    # nodes may return modified state or None
                    if isinstance(result, dict):
                        state.update(result)
                except Exception as e:
                    app_logger.error(f"Node {getattr(node, '__name__', str(node))} failed: {e}")
                    # call error handler
                    try:
                        error_handler_node(state)
                    except Exception:
                        pass
                    break
            # Build a simple report-like result
            return {
                "report_title": state.get("report_title", "Research Report"),
                "report_markdown": state.get("report_markdown", ""),
                "executive_summary": state.get("executive_summary", ""),
                "query": state.get("query", ""),
                "started_at": state.get("started_at"),
                "user_id": state.get("user_id"),
                "citations": state.get("citations", []),
            }

    return MinimalGraph()


# Create the compiled graph instance
research_graph = build_research_graph()