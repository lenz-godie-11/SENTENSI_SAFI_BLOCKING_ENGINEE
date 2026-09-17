# ruff: noqa: N999, I001

import logging

from BlockingEngine.Core.Exceptions import (
    DetectionError,
    InvalidContentError,
)
from BlockingEngine.Rules.BlockingRules import BlockingRules
from BlockingEngine.Services.DetectionService import DetectionService
from BlockingEngine.Services.DecisionService import DecisionService


Logger = logging.getLogger("BlockingEngine")


class BlockingService:
    """
    Coordinates the complete Blocking Engine workflow.

    GraphQL interacts with this service instead of communicating
    directly with the detection model, business rules, or database.

    Logging records operational events without logging the submitted
    content itself, protecting user data from appearing in application logs.
    """

    def __init__(self):
        # Detection is isolated behind a service boundary so the future
        # ML implementation can replace the current detector cleanly.
        self.DetectionService = DetectionService()

    def EvaluateContent(self, Content: str) -> dict:
        """
        Evaluate submitted content and produce a final decision.
        """

        self._ValidateContent(Content)

        try:
            DetectionResult = self.DetectionService.Detect(Content)

        except Exception as Exc:
            # Do not log the actual submitted content. User-generated
            # messages may contain sensitive or private information.
            Logger.exception(
                "Content detection failed."
            )

            raise DetectionError(
                "Content detection failed."
            ) from Exc

        Decision = BlockingRules.Evaluate(
            DetectionResult
        )

        SavedDecision = DecisionService.SaveDecision(
            Content,
            Decision,
        )

        Logger.info(
            "Content evaluation completed: action=%s reason=%s",
            Decision["action"],
            Decision["reason"],
        )

        return {
            "id": SavedDecision.id,
            "content": Content,
            **Decision,
        }

    @staticmethod
    def _ValidateContent(Content: str) -> None:
        """
        Validate content before sending it to detection.
        """

        if not isinstance(Content, str):
            raise InvalidContentError(
                "Content must be a string."
            )

        if not Content.strip():
            raise InvalidContentError(
                "Content cannot be empty."
            )