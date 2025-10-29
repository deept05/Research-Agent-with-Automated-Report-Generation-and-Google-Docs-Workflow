"""
Unit tests for research workflow graph.
"""
from app.research_agent.graph import ResearchWorkflow

def test_workflow_runs():
    wf = ResearchWorkflow({})
    result = wf.run({"query": "Quantum computing"})
    assert "summary" in result
