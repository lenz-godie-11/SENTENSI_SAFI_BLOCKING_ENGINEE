# ruff: noqa: N999

import graphene

from BlockingEngine.GraphQL.Mutations import Mutation


class Query(graphene.ObjectType):
    """
    Root GraphQL query container.

    The Blocking Engine currently exposes mutations for content
    evaluation. A query root is still required by GraphQL so the schema
    remains valid and can be extended with read operations later.
    """

    health = graphene.String(
        description="Returns the health status of the Blocking Engine."
    )

    def resolve_health(root, info):
        """
        Provide a lightweight endpoint for checking that GraphQL is alive.
        """

        return "Blocking Engine is running"


class Schema(graphene.Schema):
    """
    Defines the GraphQL schema exposed by the Blocking Engine.
    """

    def __init__(self):
        super().__init__(
            query=Query,
            mutation=Mutation,
        )