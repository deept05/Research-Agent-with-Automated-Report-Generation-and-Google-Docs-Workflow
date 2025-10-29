import importlib, pkgutil
mod = importlib.import_module('langchain.chat_models')
print('package path:', list(mod.__path__))
for finder, name, ispkg in pkgutil.iter_modules(mod.__path__):
    print('submodule:', name, 'ispkg=', ispkg)
