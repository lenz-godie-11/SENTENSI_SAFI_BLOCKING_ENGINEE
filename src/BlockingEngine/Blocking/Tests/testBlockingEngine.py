from unittest.mock import patch

from django.test import TestCase

from BlockingEngine.Blocking.models import BlockingDecision
from BlockingEngine.Core.Exceptions import InvalidContentError
from BlockingEngine.Rules.BlockingRules import BlockingRules
from BlockingEngine.Services.BlockingService import BlockingService


class BlockingRulesTest(TestCase):
    """
    Tests the business rules that convert a detection result
    into the final ALLOW or BLOCK action.
    """

    def test_safe_content_is_allowed(self):
        """
        Verify that a safe detection result produces an ALLOW decision.
        """

        # Simulate a safe result that would normally come from the ML model.
        DetectionResult = {
            "label": "safe",
            "confidence": 0.97,
        }

        Decision = BlockingRules.Evaluate(DetectionResult)

        # Safe content must be permitted.
        self.assertTrue(Decision["allowed"])

        # The final action must be ALLOW.
        self.assertEqual(Decision["action"], "ALLOW")

        # The decision must contain the standardized safe-content reason.
        self.assertEqual(
            Decision["reason"],
            "SAFE_CONTENT",
        )

    def test_offensive_content_is_blocked(self):
        """
        Verify that an offensive detection result produces a BLOCK decision.
        """

        # Simulate an offensive result returned by the future ML model.
        DetectionResult = {
            "label": "offensive",
            "confidence": 0.94,
        }

        Decision = BlockingRules.Evaluate(DetectionResult)

        # Offensive content must never be allowed.
        self.assertFalse(Decision["allowed"])

        # The final action must be BLOCK.
        self.assertEqual(Decision["action"], "BLOCK")

        # The decision must contain the standardized blocking reason.
        self.assertEqual(
            Decision["reason"],
            "OFFENSIVE_CONTENT",
        )


class BlockingServiceTest(TestCase):
    """
    Tests the complete BlockingService workflow.

    The real ML model is replaced with a controlled test result
    so the Blocking Engine can be tested independently.
    """

    @patch(
        "BlockingEngine.Services.BlockingService.DetectionService.Detect"
    )
    def test_offensive_content_is_blocked_and_saved(
        self,
        MockDetect,
    ):
        """
        Verify that offensive content is blocked and persisted.
        """

        # Simulate the result that will eventually come from the ML model.
        MockDetect.return_value = {
            "label": "offensive",
            "confidence": 0.94,
        }

        Result = BlockingService().EvaluateContent(
            "This is offensive test content"
        )

        # Verify the decision returned to the caller.
        self.assertFalse(Result["allowed"])
        self.assertEqual(Result["action"], "BLOCK")
        self.assertEqual(
            Result["reason"],
            "OFFENSIVE_CONTENT",
        )

        # The decision should also be persisted in the database.
        self.assertEqual(
            BlockingDecision.objects.count(),
            1,
        )

        SavedDecision = BlockingDecision.objects.first()

        # Verify the persisted action.
        self.assertEqual(
            SavedDecision.Action,
            "BLOCK",
        )

        # Verify the persisted reason.
        self.assertEqual(
            SavedDecision.Reason,
            "OFFENSIVE_CONTENT",
        )

    def test_empty_content_is_rejected(self):
        """
        Verify that an empty string is rejected before detection.
        """

        # No content should reach the detection layer.
        with self.assertRaises(InvalidContentError):
            BlockingService().EvaluateContent("")

        # Invalid input must not create a database decision.
        self.assertEqual(
            BlockingDecision.objects.count(),
            0,
        )

    def test_whitespace_content_is_rejected(self):
        """
        Verify that content containing only whitespace is rejected.
        """

        # Whitespace has no meaningful content and should not be
        # forwarded to the detection component.
        with self.assertRaises(InvalidContentError):
            BlockingService().EvaluateContent("   ")

        # Invalid input must not create a database decision.
        self.assertEqual(
            BlockingDecision.objects.count(),
            0,
        )

    def test_non_string_content_is_rejected(self):
        """
        Verify that non-string input is rejected at the service boundary.
        """

        # The Blocking Engine accepts textual content only.
        with self.assertRaises(InvalidContentError):
            BlockingService().EvaluateContent(None)

        # Invalid input must not create a database decision.
        self.assertEqual(
            BlockingDecision.objects.count(),
            0,
        )
