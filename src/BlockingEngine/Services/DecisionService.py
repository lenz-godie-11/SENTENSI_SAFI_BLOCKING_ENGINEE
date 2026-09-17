
# ruff: noqa: N999

from BlockingEngine.Blocking.models import BlockingDecision


class DecisionService:
    """
    Handles persistence of decisions produced by the Blocking Engine.

    Database operations are isolated here so that the core blocking
    workflow does not need to know how Django's ORM stores decisions.
    """

    @staticmethod
    def SaveDecision(Content: str, Decision: dict) -> BlockingDecision:
        """
        Save a completed blocking decision to the database.

        The service receives an already-evaluated decision and persists
        the final result produced by the blocking rules.
        """

        return BlockingDecision.objects.create(
            Content=Content,
            Action=Decision["action"],
            Reason=Decision["reason"],
            Confidence=Decision.get("confidence"),
        )