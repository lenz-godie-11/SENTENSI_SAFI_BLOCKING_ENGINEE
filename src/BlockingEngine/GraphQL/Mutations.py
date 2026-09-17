# ruff: noqa: N999

import graphene

from BlockingEngine.Core.Exceptions import BlockingEngineError
from BlockingEngine.GraphQL.Types import BlockingDecisionType
from BlockingEngine.Services.BlockingService import BlockingService


class EvaluateContent(graphene.Mutation):
    """
    GraphQL mutation responsible for evaluating submitted content.

    The mutation acts as the API boundary of the Blocking Engine.
    Business logic remains inside BlockingService, while this layer
    is responsible for translating domain failures into API errors.
    """

    class Arguments:
        # GraphQL requires content so clients cannot submit an
        # evaluation request without providing the text to inspect.
        content = graphene.String(required=True)

    Output = BlockingDecisionType

    @staticmethod
    def mutate(root, info, content):
        """
        Submit content to the Blocking Engine and return its decision.
        """

        try:
            # Keep all blocking logic inside the service layer.
            # GraphQL should not perform detection or business rules.
            Decision = BlockingService().EvaluateContent(content)

        except BlockingEngineError as Exc:
            # Domain errors are intentionally exposed as controlled
            # GraphQL errors instead of leaking internal implementation
            # details such as database or model exceptions.
            raise BlockingEngineError(str(Exc)) from Exc

        return BlockingDecisionType(
            id=Decision["id"],
            content=Decision["content"],
            allowed=Decision["allowed"],
            action=Decision["action"],
            reason=Decision["reason"],
            confidence=Decision["confidence"],
        )


class Mutation(graphene.ObjectType):
    """
    Root GraphQL mutation container.

    Additional Blocking Engine operations can be added here later
    without changing the existing API structure.
    """

    evaluate_content = EvaluateContent.Field()
