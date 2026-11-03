"""Registry test: ``app.models`` must export every ORM model it defines.

Alembic's ``env.py`` imports the ``app.models`` package to fill ``Base.metadata`` for
autogenerate. A model module that the package does not import, or a model it does not list in
``__all__``, would be invisible to autogenerate. These tests discover the models from the
package's own submodules, so a new module is checked without editing this file.
"""

import importlib
import inspect
import pkgutil

import app.models
from app.db.database import Base


def _models_defined_in_package() -> set[type[Base]]:
    """Collect every ``Base`` subclass defined (not merely imported) in an ``app.models`` module.

    Returns:
        The set of model classes whose ``__module__`` is one of the package's submodules.
    """
    models: set[type[Base]] = set()
    for module_info in pkgutil.iter_modules(app.models.__path__):
        module = importlib.import_module(f"{app.models.__name__}.{module_info.name}")
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, Base) and obj is not Base and obj.__module__ == module.__name__:
                models.add(obj)
    return models


def _exported_models() -> set[type[Base]]:
    """Resolve the names listed in ``app.models.__all__`` to the objects the package exports.

    Returns:
        The set of objects named in ``__all__``.
    """
    return {getattr(app.models, name) for name in app.models.__all__}


def test_models_package_exports_every_model_defined_in_its_modules() -> None:
    assert _exported_models() == _models_defined_in_package()


def test_exported_models_cover_every_table_in_metadata() -> None:
    exported_tables = {model.__tablename__ for model in _exported_models()}

    assert exported_tables == set(Base.metadata.tables)
