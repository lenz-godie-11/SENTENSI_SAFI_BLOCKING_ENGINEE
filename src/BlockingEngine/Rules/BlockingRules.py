# ruff: noqa: N999


class BlockingRules:
    """
    Contains the business rules that convert a detection result
    into a final BLOCK or ALLOW decision.

    Keeping these rules separate from the detection service means
    the ML model only identifies content while the Blocking Engine
    decides what action should be taken.
    """

    @staticmethod
    def Evaluate(DetectionResult: dict) -> dict:
        """
        Evaluate a detection result and return the final action.
        """

        Label = DetectionResult.get("label")
        Confidence = DetectionResult.get("confidence")

        if Label == "offensive":
            return {
                "allowed": False,
                "action": "BLOCK",
                "reason": "OFFENSIVE_CONTENT",
                "confidence": Confidence,
            }

        return {
            "allowed": True,
            "action": "ALLOW",
            "reason": "SAFE_CONTENT",
            "confidence": Confidence,
        }