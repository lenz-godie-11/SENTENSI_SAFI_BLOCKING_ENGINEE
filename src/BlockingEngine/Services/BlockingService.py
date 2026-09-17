



from BlockingEngine.Rules.BlockingRules import BlockingRules
from BlockingEngine.Services.DetectionService import DetectionService
from BlockingEngine.Services.DecisionService import DecisionService


class BlockingService:
    """
    Coordinates the complete Blocking Engine workflow.

    GraphQL calls this service instead of interacting directly with
    the detection model, business rules, or database. This keeps the
    application's entry point independent from implementation details.
    """

    def __init__(self):
        # The detection component is isolated behind a service boundary
        # so the real ML model can be integrated later without changing
        # the rest of the Blocking Engine.
        self.DetectionService = DetectionService()

    def EvaluateContent(self, Content: str) -> dict:
        """
        Evaluate content, apply blocking rules, and persist the decision.

        The workflow is:
        1. Detect the content.
        2. Apply business rules.
        3. Save the final decision.
        4. Return the result to the caller.
        """

        DetectionResult = self.DetectionService.Detect(Content)

        Decision = BlockingRules.Evaluate(DetectionResult)

        # Persistence is handled by DecisionService so that database
        # operations remain separated from the core blocking logic.
        SavedDecision = DecisionService.SaveDecision(
            Content,
            Decision,
        )

        return {
            "id": SavedDecision.id,
            "content": Content,
            **Decision,
        }