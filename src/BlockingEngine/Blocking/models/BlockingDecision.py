




from django.db import models


class BlockingDecision(models.Model):
    """
    Stores the final decision made by the Blocking Engine.

    The detection model is responsible for identifying the content
    and returning a detection result. This model stores the decision
    produced after that result passes through the blocking rules.
    """

    class Action(models.TextChoices):
        # Defines the two possible actions supported by the engine.
        ALLOW = "ALLOW", "Allow"
        BLOCK = "BLOCK", "Block"

    class Reason(models.TextChoices):
        # Provides a standardized reason for every blocking decision.
        OFFENSIVE_CONTENT = "OFFENSIVE_CONTENT", "Offensive content"
        SAFE_CONTENT = "SAFE_CONTENT", "Safe content"
        UNKNOWN = "UNKNOWN", "Unknown"

    Content = models.TextField(
        help_text="The content evaluated by the Blocking Engine.",
    )

    Action = models.CharField(
        max_length=10,
        choices=Action.choices,
        help_text="The final action taken by the Blocking Engine.",
    )

    Reason = models.CharField(
        max_length=50,
        choices=Reason.choices,
        help_text="The reason behind the blocking decision.",
    )

    Confidence = models.FloatField(
        null=True,
        blank=True,
        help_text="Confidence returned by the detection component.",
    )

    CreatedAt = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the decision was created.",
    )

    def __str__(self):
        return f"{self.Action}: {self.Reason}"