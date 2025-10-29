"""Top-level package for the Research Agent.

This module intentionally keeps imports minimal so importing `app` does not
pull in heavy optional dependencies (LLM clients, langgraph, etc.).

Modules should import their own dependencies directly (for example,
`from app.research_agent import graph` where needed) to avoid import-time
side-effects during server startup.
"""

__version__ = "1.0.0"

__all__ = ["__version__"]