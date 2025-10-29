from dotenv import load_dotenv
import os
import traceback

# Load the project's .env explicitly so we see the same values the app would
env_path = r"C:\Users\vvrlu\OneDrive\Desktop\langchain-research-agent\.env"
load_dotenv(env_path)
print('Loaded .env from:', env_path)
print('OPENAI_API_KEY (repr):', repr(os.getenv('OPENAI_API_KEY')))
print('OPENAI_API_KEY truthy:', bool(os.getenv('OPENAI_API_KEY')))

try:
    # Ensure project root is on sys.path then import the project's LLMService to verify initialization
    import sys
    project_root = r"C:\Users\vvrlu\OneDrive\Desktop\langchain-research-agent"
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from app.services.llm_service import LLMService
    svc = LLMService()
    print('LLMService initialized. Model in use:', svc.model, 'LLM object:', type(svc.llm))
except Exception as e:
    print('LLMService init error:', type(e).__name__, str(e))
    traceback.print_exc()
