from contextvars import ContextVar

# Global context variables
_session_id: ContextVar[str | None] = ContextVar("session_id", default=None)
_file_log_id: ContextVar[str | None] = ContextVar("file_log_id", default=None)

# ─────────────────────────────────────────────────────────── Accessors

def set_run_context(session_id: str | None = None, file_log_id: str | None = None) -> None:
    if session_id is not None:
        _session_id.set(session_id)
    if file_log_id is not None:
        _file_log_id.set(file_log_id)

def clear_run_context() -> None:
    _session_id.set(None)
    _file_log_id.set(None)

def get_session_id() -> str | None:
    return _session_id.get()

def get_file_log_id() -> str | None:
    return _file_log_id.get()

# ─────────────────────────────────────────────────────────── Propagation

def propagate_run_context_if_needed(obj: object) -> None:
    from app.providers.base_provider import BaseProvider
    try:
        from app.utilities.provider_mixin_injector import ProviderContextInjectorWrapper
    except ImportError:
        ProviderContextInjectorWrapper = None

    session_id = get_session_id()
    file_log_id = get_file_log_id()

    # Unwrap injector wrappers
    if ProviderContextInjectorWrapper and isinstance(obj, ProviderContextInjectorWrapper):
        for attr in ('_wrapped_instance', 'instance', '_wrapped', 'wrapped'):
            inner = getattr(obj, attr, None)
            if inner:
                propagate_run_context_if_needed(inner)
                return
        return

    # Only proceed for BaseProvider instances
    if not isinstance(obj, BaseProvider):
        return

    # Apply context
    if session_id and not getattr(obj, '_session_id', None):
        obj._session_id = session_id
    if file_log_id and not getattr(obj, '_file_log_id', None):
        obj._file_log_id = file_log_id

    # Propagate to subcomponents
    for attr_name in dir(obj):
        try:
            attr = getattr(obj, attr_name)
            if isinstance(attr, BaseProvider):
                propagate_run_context_if_needed(attr)
            elif isinstance(attr, list):
                for item in attr:
                    if isinstance(item, BaseProvider):
                        propagate_run_context_if_needed(item)
            elif isinstance(attr, dict):
                for item in attr.values():
                    if isinstance(item, BaseProvider):
                        propagate_run_context_if_needed(item)
        except Exception:
            continue

# ─────────────────────────────────────────────────────────── Patch BaseProvider

def _patch_base_provider_class():
    from app.providers.base_provider import BaseProvider
    from app.utilities.run_context import get_session_id, get_file_log_id

    orig_init = BaseProvider.__init__
    def wrapped_init(self, *args, **kwargs):
        orig_init(self, *args, **kwargs)
        propagate_run_context_if_needed(self)
    BaseProvider.__init__ = wrapped_init

    if hasattr(BaseProvider, 'run'):
        orig_run = BaseProvider.run
        def wrapped_run(self, *args, **kwargs):
            propagate_run_context_if_needed(self)
            session_id = get_session_id()
            file_log_id = get_file_log_id()
            if 'input' in kwargs and isinstance(kwargs['input'], dict):
                inp = kwargs['input']
                if session_id and not inp.get('session_id'):
                    inp['session_id'] = session_id
                if file_log_id and not inp.get('file_log_id'):
                    inp['file_log_id'] = file_log_id
            return orig_run(self, *args, **kwargs)
        BaseProvider.run = wrapped_run

_patch_base_provider_class()
