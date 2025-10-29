import importlib, sys
try:
    import langchain
    print('langchain package:', getattr(langchain, '__version__', 'version attr missing'))
except Exception as e:
    print('Failed to import langchain:', e)

try:
    mod = importlib.import_module('langchain.chat_models')
    print('langchain.chat_models module file:', getattr(mod, '__file__', 'no __file__'))
    print('\nAvailable names in langchain.chat_models:')
    for name in sorted(dir(mod)):
        print(name)
except Exception as e:
    print('Error importing langchain.chat_models:', type(e).__name__, e)
    import traceback; traceback.print_exc()
