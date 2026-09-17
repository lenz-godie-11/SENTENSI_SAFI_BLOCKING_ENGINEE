# ruff: noqa: N999

from BlockingEngine.Core.Exceptions import (
    DetectionError,
    InvalidContentError,
)
from BlockingEngine.Rules.BlockingRules import BlockingRules
from BlockingEngine.Services.DecisionService import DecisionService
from BlockingEngine.Services.DetectionService import DetectionService


class BlockingService:
    """
    Coordinates the complete Blocking Engine workflow.

    GraphQL interacts with this service instead of communicating
    directly with the detection model, business rules, or database.

    This keeps the application boundary clean and makes each
    internal component independently replaceable.
    """

    def __init__(self):
        # The detection component is isolated behind a service boundary.
        # This allows the real ML model to be integrated later without
        # changing the rest of the blocking workflow.
        self.DetectionService = DetectionService()

    def EvaluateContent(self, Content: str) -> dict:
        """
        Evaluate submitted content and produce a final decision.

        The workflow is intentionally kept in one orchestration layer:

        1. Validate the submitted content.
        2. Request a detection result.
        3. Apply blocking business rules.
        4. Persist the final decision.
        5. Return a normalized result to the caller.
        """

        self._ValidateContent(Content)

        try:
            DetectionResult = self.DetectionService.Detect(Content)
        except Exception as Exc:
            # Detection failures are converted into a domain-specific
            # error so callers do not receive implementation details.
            raise DetectionError("Content detection failed.") from Exc

        Decision = BlockingRules.Evaluate(DetectionResult)

        SavedDecision = DecisionService.SaveDecision(
            Content,
            Decision,
        )

        return {
            "id": SavedDecision.id,
            "content": Content,
            **Decision,
        }

    @staticmethod
    def _ValidateContent(Content: str) -> None:
        """
        Validate content before sending it to the detection component.

        Validation belongs at the service boundary because every API
        entry point should follow the same content requirements.
        """

        if not isinstance(Content, str):
            raise InvalidContentError("Content must be a string.")

        if not Content.strip():
            raise InvalidContentError("Content cannot be empty.")
