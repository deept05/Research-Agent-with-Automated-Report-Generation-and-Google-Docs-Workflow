"""
LangGraph nodes for the research workflow.
"""
from typing import Dict, Any
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.research_agent.state import ResearchState
from app.research_agent.tools import WebSearchTool, ContentExtractor, RelevanceFilter
from app.utils.logger import app_logger
from app.config import settings


# Initialize tools
search_tool = WebSearchTool()
content_extractor = ContentExtractor()
relevance_filter = RelevanceFilter()

# Initialize LLM
llm = ChatOpenAI(
    model=settings.openai_model,
    temperature=0.3,
    api_key=settings.openai_api_key
)


def query_intake_node(state: ResearchState) -> Dict[str, Any]:
    """
    Initial node: validate and prepare the query.
    
    Args:
        state: Current research state
        
    Returns:
        Updated state
    """
    app_logger.info(f"[Query Intake] Processing query: {state['query']}")
    
    state["current_step"] = "query_intake"
    state["progress_messages"].append(f"Processing query: {state['query']}")
    
    # Validate query
    if not state["query"] or len(state["query"]) < 5:
        state["error_message"] = "Query too short or empty"
        return state
    
    app_logger.info(f"[Query Intake] Query validated for job {state['job_id']}")
    return state


def web_search_node(state: ResearchState) -> Dict[str, Any]:
    """
    Search the web for relevant information.
    
    Args:
        state: Current research state
        
    Returns:
        Updated state with search results
    """
    app_logger.info(f"[Web Search] Searching for: {state['query']}")
    
    state["current_step"] = "web_search"
    state["progress_messages"].append("Searching the web...")
    
    try:
        # Perform web search
        results = search_tool.search(state["query"], state["max_results"])
        state["raw_search_results"] = results
        
        app_logger.info(f"[Web Search] Found {len(results)} results")
        state["progress_messages"].append(f"Found {len(results)} search results")
        
    except Exception as e:
        app_logger.error(f"[Web Search] Error: {str(e)}")
        state["error_message"] = f"Search error: {str(e)}"
        state["raw_search_results"] = []
    
    return state


def content_filter_node(state: ResearchState) -> Dict[str, Any]:
    """
    Filter and rank search results by relevance.
    
    Args:
        state: Current research state
        
    Returns:
        Updated state with filtered results
    """
    app_logger.info("[Content Filter] Filtering search results")
    
    state["current_step"] = "content_filter"
    state["progress_messages"].append("Filtering relevant results...")
    
    try:
        results = state["raw_search_results"]
        filtered = relevance_filter.filter_results(results, state["query"])
        
        # Take top results
        state["filtered_results"] = filtered[:state["max_results"]]
        
        app_logger.info(f"[Content Filter] Kept {len(state['filtered_results'])} relevant results")
        state["progress_messages"].append(f"Filtered to {len(state['filtered_results'])} relevant sources")
        
    except Exception as e:
        app_logger.error(f"[Content Filter] Error: {str(e)}")
        state["error_message"] = f"Filter error: {str(e)}"
        state["filtered_results"] = state["raw_search_results"]
    
    return state


def content_extraction_node(state: ResearchState) -> Dict[str, Any]:
    """
    Extract full content from top search results.
    
    Args:
        state: Current research state
        
    Returns:
        Updated state with extracted content
    """
    app_logger.info("[Content Extraction] Extracting content from URLs")
    
    state["current_step"] = "content_extraction"
    state["progress_messages"].append("Extracting content from sources...")
    
    try:
        # Extract content from top 5 results
        urls = [r["url"] for r in state["filtered_results"][:5]]
        extracted = content_extractor.batch_extract(urls)
        
        state["extracted_content"] = extracted
        
        app_logger.info(f"[Content Extraction] Extracted {len(extracted)} pages")
        state["progress_messages"].append(f"Extracted content from {len(extracted)} sources")
        
    except Exception as e:
        app_logger.error(f"[Content Extraction] Error: {str(e)}")
        state["error_message"] = f"Extraction error: {str(e)}"
        state["extracted_content"] = []
    
    return state


def synthesizer_node(state: ResearchState) -> Dict[str, Any]:
    """
    Synthesize extracted content into a coherent summary using LLM.
    
    Args:
        state: Current research state
        
    Returns:
        Updated state with synthesized content
    """
    app_logger.info("[Synthesizer] Synthesizing research findings")
    
    state["current_step"] = "synthesizer"
    state["progress_messages"].append("Synthesizing findings...")
    
    try:
        # Prepare content for synthesis
        content_chunks = []
        for item in state["extracted_content"]:
            content_chunks.append(f"Source: {item['url']}\n{item['content'][:2000]}")
        
        combined_content = "\n\n---\n\n".join(content_chunks)
        
        # Create synthesis prompt
        synthesis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a research analyst. Synthesize the provided web content into a comprehensive, 
            well-structured analysis that answers the research query. Be objective, factual, and cite key findings."""),
            ("user", "Research Query: {query}\n\nWeb Content:\n{content}\n\nProvide a comprehensive synthesis.")
        ])
        
        chain = synthesis_prompt | llm
        response = chain.invoke({
            "query": state["query"],
            "content": combined_content[:15000]  # Limit token usage
        })
        
        state["synthesized_content"] = response.content
        
        app_logger.info("[Synthesizer] Synthesis completed")
        state["progress_messages"].append("Synthesized research findings")
        
    except Exception as e:
        app_logger.error(f"[Synthesizer] Error: {str(e)}")
        state["error_message"] = f"Synthesis error: {str(e)}"
        state["synthesized_content"] = "Error synthesizing content"
    
    return state


def citation_handler_node(state: ResearchState) -> Dict[str, Any]:
    """
    Generate citations for the research report.
    
    Args:
        state: Current research state
        
    Returns:
        Updated state with citations
    """
    app_logger.info("[Citation Handler] Generating citations")
    
    state["current_step"] = "citation_handler"
    state["progress_messages"].append("Generating citations...")
    
    try:
        citations = []
        accessed_date = datetime.now().strftime("%Y-%m-%d")
        
        for result in state["filtered_results"]:
            citation = {
                "title": result.get("title", "Unknown"),
                "url": result.get("url", ""),
                "source": result.get("source", ""),
                "accessed_date": accessed_date,
                "snippet": result.get("snippet", "")
            }
            citations.append(citation)
        
        state["citations"] = citations
        
        app_logger.info(f"[Citation Handler] Generated {len(citations)} citations")
        state["progress_messages"].append(f"Generated {len(citations)} citations")
        
    except Exception as e:
        app_logger.error(f"[Citation Handler] Error: {str(e)}")
        state["error_message"] = f"Citation error: {str(e)}"
        state["citations"] = []
    
    return state


def report_generator_node(state: ResearchState) -> Dict[str, Any]:
    """
    Generate the final research report in markdown format.
    
    Args:
        state: Current research state
        
    Returns:
        Updated state with complete report
    """
    app_logger.info("[Report Generator] Generating final report")
    
    state["current_step"] = "report_generator"
    state["progress_messages"].append("Generating final report...")
    
    try:
        # Generate report title
        title_prompt = ChatPromptTemplate.from_messages([
            ("system", "Generate a concise, professional title for this research report."),
            ("user", "Research Query: {query}")
        ])
        
        title_chain = title_prompt | llm
        title_response = title_chain.invoke({"query": state["query"]})
        state["report_title"] = title_response.content.strip('"')
        
        # Generate executive summary
        summary_prompt = ChatPromptTemplate.from_messages([
            ("system", "Create a brief executive summary (2-3 sentences) of the research findings."),
            ("user", "Research Query: {query}\n\nFindings: {synthesis}")
        ])
        
        summary_chain = summary_prompt | llm
        summary_response = summary_chain.invoke({
            "query": state["query"],
            "synthesis": state["synthesized_content"][:3000]
        })
        state["executive_summary"] = summary_response.content
        
        # Create report sections
        sections = [
            {
                "heading": "Executive Summary",
                "content": state["executive_summary"]
            },
            {
                "heading": "Research Findings",
                "content": state["synthesized_content"]
            },
            {
                "heading": "Key Sources",
                "content": "\n".join([f"- {r['title']}: {r['url']}" for r in state["filtered_results"][:5]])
            }
        ]
        state["report_sections"] = sections
        
        # Generate markdown report
        markdown = f"# {state['report_title']}\n\n"
        markdown += f"**Research Query:** {state['query']}\n\n"
        markdown += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        markdown += "---\n\n"
        
        for section in sections:
            markdown += f"## {section['heading']}\n\n{section['content']}\n\n"
        
        # Add citations if enabled
        if state["include_citations"] and state["citations"]:
            markdown += "## References\n\n"
            for i, citation in enumerate(state["citations"], 1):
                markdown += f"{i}. {citation['title']}. Retrieved {citation['accessed_date']} from {citation['url']}\n"
        
        state["report_markdown"] = markdown
        
        app_logger.info("[Report Generator] Report generated successfully")
        state["progress_messages"].append("Report generated successfully")
        
    except Exception as e:
        app_logger.error(f"[Report Generator] Error: {str(e)}")
        state["error_message"] = f"Report generation error: {str(e)}"
        state["report_markdown"] = f"# Error Generating Report\n\n{str(e)}"
    
    return state


def error_handler_node(state: ResearchState) -> Dict[str, Any]:
    """
    Handle errors and create error report.
    
    Args:
        state: Current research state
        
    Returns:
        Updated state with error handling
    """
    app_logger.error(f"[Error Handler] Handling error: {state.get('error_message', 'Unknown error')}")
    
    state["current_step"] = "error_handler"
    
    # Create error report
    error_report = f"# Research Report - Error\n\n"
    error_report += f"**Query:** {state['query']}\n\n"
    error_report += f"**Error:** {state['error_message']}\n\n"
    error_report += f"**Step Failed:** {state['current_step']}\n\n"
    error_report += "Please try again or contact support if the issue persists."
    
    state["report_markdown"] = error_report
    state["completed_at"] = datetime.now()
    
    return state