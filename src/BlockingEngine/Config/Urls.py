# ruff: noqa: N999, I001

from django.contrib import admin
from django.urls import path
from graphene_django.views import GraphQLView

from BlockingEngine.GraphQL.Schema import Schema


urlpatterns = [
    path("admin/", admin.site.urls),

    # GraphQL is exposed through a single API boundary.
    # CSRF protection remains enabled through Django middleware.
    path(
        "graphql/",
        GraphQLView.as_view(
            graphiql=True,
            schema=Schema(),
        ),
    ),
]