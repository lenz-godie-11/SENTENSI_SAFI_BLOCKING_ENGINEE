class BlockingEngineError(Exception):
    """
    Base exception for errors raised inside the Blocking Engine.

    Using a dedicated exception hierarchy prevents internal
    implementation errors from leaking directly to API clients.
    """


class InvalidContentError(BlockingEngineError):
    """
    Raised when submitted content does not satisfy the engine's
    basic input requirements.
    """


class DetectionError(BlockingEngineError):
    """
    Raised when the content detection component cannot produce
    a valid detection result.
    """
