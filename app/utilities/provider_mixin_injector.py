class ProviderContextInjectorWrapper:
    def __init__(self, provider, session_id=None, file_log_id=None):
        self._provider = provider
        self._injected_session_id = session_id
        self._injected_file_log_id = file_log_id

        if session_id:
            setattr(self._provider, "_session_id", session_id)
        if file_log_id:
            setattr(self._provider, "_file_log_id", file_log_id)
        if hasattr(self._provider, "propagate_file_log_id") and file_log_id:
            self._provider.propagate_file_log_id(file_log_id)

    def run(self, input: dict | None = None):
        input = input or {}
        input.setdefault("session_id", self._injected_session_id)
        input.setdefault("file_log_id", self._injected_file_log_id)

        # Inject into provider directly
        self._provider._session_id = self._injected_session_id
        self._provider._file_log_id = self._injected_file_log_id

        return self._provider.run(input=input)

    def __getattr__(self, attr):
        return getattr(self._provider, attr)
