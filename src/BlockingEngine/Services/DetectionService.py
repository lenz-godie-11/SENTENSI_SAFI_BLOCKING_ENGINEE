# ruff: noqa: N999

from typing import ClassVar

from BlockingEngine.Core.Exceptions import DetectionError


class DetectionService:
    """
    Defines the contract between the Blocking Engine and the
    content-detection component.

    The detection implementation can be replaced by the actual ML model
    later without changing the rest of the Blocking Engine.
    """

    SUPPORTED_LABELS: ClassVar[frozenset[str]] = frozenset(
        {"safe", "offensive"}
    )

    MIN_CONFIDENCE = 0.0
    MAX_CONFIDENCE = 1.0

    def Detect(self, Content: str) -> dict:
        """
        Run content detection and return a validated detection result.

        The current implementation is a temporary detector used until
        the production ML model is integrated.
        """

        DetectionResult = {
            "label": "safe",
            "confidence": 1.0,
        }

        return self._ValidateResult(DetectionResult)

    @classmethod
    def _ValidateResult(cls, DetectionResult: dict) -> dict:
        """
        Validate the contract returned by the detection component.

        Invalid results are rejected before they reach the blocking rules.
        """

        if not isinstance(DetectionResult, dict):
            raise DetectionError(
                "Detection result must be a dictionary."
            )

        RequiredFields = {
            "label",
            "confidence",
        }

        MissingFields = RequiredFields - DetectionResult.keys()

        if MissingFields:
            Missing = ", ".join(sorted(MissingFields))

            raise DetectionError(
                f"Detection result is missing required field(s): {Missing}."
            )

        Label = DetectionResult["label"]
        Confidence = DetectionResult["confidence"]

        if Label not in cls.SUPPORTED_LABELS:
            raise DetectionError(
                f"Unsupported detection label: {Label}."
            )

        if isinstance(Confidence, bool) or not isinstance(
            Confidence,
            (int, float),
        ):
            raise DetectionError(
                "Detection confidence must be numeric."
            )

        if not cls.MIN_CONFIDENCE <= Confidence <= cls.MAX_CONFIDENCE:
            raise DetectionError(
                "Detection confidence must be between 0.0 and 1.0."
            )

        return {
            "label": Label,
            "confidence": float(Confidence),
        }
