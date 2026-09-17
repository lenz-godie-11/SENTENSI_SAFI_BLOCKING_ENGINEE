

# ruff: noqa: N999

from unittest.mock import patch

from django.test import TestCase

from BlockingEngine.Blocking.models import BlockingDecision
from BlockingEngine.Rules.BlockingRules import BlockingRules
from BlockingEngine.Services.BlockingService import BlockingService


class BlockingRulesTest(TestCase):
    """
    Tests the business rules that convert a detection result
    into the final ALLOW or BLOCK action.

    These tests do not depend on the ML model because the rules
    only need a standardized detection result.
    """

    def test_safe_content_is_allowed(self):
        """
        Verify that safe detection results produce an ALLOW decision.
        """

        # Simulate the result that will eventually come from the ML model.
        DetectionResult = {
            "label": "safe",
            "confidence": 0.97,
        }

        # Send the simulated result through the business rules.
        Decision = BlockingRules.Evaluate(DetectionResult)

        # Verify that the content is permitted.
        self.assertTrue(Decision["allowed"])

        # Verify the action returned by the blocking rules.
        self.assertEqual(Decision["action"], "ALLOW")

        # Verify the standardized reason for allowing the content.
        self.assertEqual(
            Decision["reason"],
            "SAFE_CONTENT",
        )

    def test_offensive_content_is_blocked(self):
        """
        Verify that offensive detection results produce a BLOCK decision.
        """

        # Simulate an offensive result from the future ML component.
        DetectionResult = {
            "label": "offensive",
            "confidence": 0.94,
        }

        # Evaluate the simulated detection result.
        Decision = BlockingRules.Evaluate(DetectionResult)

        # Offensive content must not be allowed.
        self.assertFalse(Decision["allowed"])

        # The engine must return BLOCK as the final action.
        self.assertEqual(Decision["action"], "BLOCK")

        # Verify the standardized blocking reason.
        self.assertEqual(
            Decision["reason"],
            "OFFENSIVE_CONTENT",
        )


class BlockingServiceTest(TestCase):
    """
    Tests the complete BlockingService workflow.

    The real ML model is intentionally not used here. Instead,
    DetectionService is mocked so that we can test the Blocking
    Engine independently from the teammate's ML implementation.
    """

    @patch(
        "BlockingEngine.Services.BlockingService.DetectionService.Detect"
    )
    def test_offensive_content_is_blocked_and_saved(
        self,
        MockDetect,
    ):
        """
        Verify that offensive content is blocked and the decision
        is correctly persisted in the database.
        """

        # Control the detection result returned during this test.
        # This represents what the real ML model will return later.
        MockDetect.return_value = {
            "label": "offensive",
            "confidence": 0.94,
        }

        # Send content through the complete BlockingService workflow.
        Result = BlockingService().EvaluateContent(
            "This is offensive test content"
        )

        # Verify the final decision returned by the service.
        self.assertFalse(Result["allowed"])
        self.assertEqual(Result["action"], "BLOCK")
        self.assertEqual(
            Result["reason"],
            "OFFENSIVE_CONTENT",
        )

        # Verify that the final decision was persisted.
        self.assertEqual(
            BlockingDecision.objects.count(),
            1,
        )

        # Retrieve the decision created during the test.
        SavedDecision = BlockingDecision.objects.first()

        # Verify that the database contains the correct action.
        self.assertEqual(
            SavedDecision.Action,
            "BLOCK",
        )

        # Verify that the database contains the correct reason.
        self.assertEqual(
            SavedDecision.Reason,
            "OFFENSIVE_CONTENT",
        )
