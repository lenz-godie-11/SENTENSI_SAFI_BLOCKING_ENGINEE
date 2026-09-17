# ruff: noqa: N999, I001

from django.contrib import admin
from django.urls import path
from graphene_django.views import GraphQLView

from BlockingEngine.GraphQL.Schema import Schema


urlpatterns = [
    path("admin/", admin.site.urls),

    # Exposes the Blocking Engine GraphQL API to external clients.
    path(
        "graphql/",
        GraphQLView.as_view(graphiql=True, schema=Schema()),
    ),
]