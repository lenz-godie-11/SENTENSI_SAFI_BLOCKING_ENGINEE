


class DetectionService:
    """
    Provides a stable interface between the Blocking Engine
    and the content-detection component.

    The actual ML model will be integrated through this service later.
    Keeping this boundary separate allows the Blocking Engine to work
    independently from the model implementation.
    """

    def Detect(self, Content: str) -> dict:
        """
        Detect whether the provided content is offensive.

        This temporary implementation is used for development and
        testing until the actual ML detection model is integrated.
        """

        return {
            "label": "safe",
            "confidence": 1.0,
        }