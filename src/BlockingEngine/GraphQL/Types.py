# ruff: noqa: N999

import graphene


class BlockingDecisionType(graphene.ObjectType):
    """
    GraphQL representation of a blocking decision.

    This type defines the data that external clients are allowed to
    receive from the Blocking Engine without exposing the Django model
    implementation directly.
    """

    id = graphene.ID()
    content = graphene.String()
    allowed = graphene.Boolean()
    action = graphene.String()
    reason = graphene.String()
    confidence = graphene.Float()