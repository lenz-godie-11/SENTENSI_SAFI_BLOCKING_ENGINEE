from unittest.mock import patch

from django.test import TestCase

from BlockingEngine.Blocking.models import BlockingDecision
from BlockingEngine.Core.Exceptions import (
    DetectionError,
    InvalidContentError,
)
from BlockingEngine.Rules.BlockingRules import BlockingRules
from BlockingEngine.Services.BlockingService import BlockingService
from BlockingEngine.Services.DetectionService import DetectionService


class BlockingRulesTest(TestCase):
    """
    Tests the business rules responsible for converting
    detection results into ALLOW or BLOCK decisions.
    """

    def test_safe_content_is_allowed(self):
        """
        Verify that a safe detection result produces an ALLOW decision.
        """

        DetectionResult = {
            "label": "safe",
            "confidence": 0.97,
        }

        Decision = BlockingRules.Evaluate(DetectionResult)

        self.assertTrue(Decision["allowed"])
        self.assertEqual(Decision["action"], "ALLOW")
        self.assertEqual(
            Decision["reason"],
            "SAFE_CONTENT",
        )

    def test_offensive_content_is_blocked(self):
        """
        Verify that an offensive detection result produces a BLOCK decision.
        """

        DetectionResult = {
            "label": "offensive",
            "confidence": 0.94,
        }

        Decision = BlockingRules.Evaluate(DetectionResult)

        self.assertFalse(Decision["allowed"])
        self.assertEqual(Decision["action"], "BLOCK")
        self.assertEqual(
            Decision["reason"],
            "OFFENSIVE_CONTENT",
        )


class BlockingServiceTest(TestCase):
    """
    Tests the complete BlockingService workflow.

    The real detection component is mocked so the Blocking Engine
    can be tested independently from the future ML implementation.
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

        MockDetect.return_value = {
            "label": "offensive",
            "confidence": 0.94,
        }

        Result = BlockingService().EvaluateContent(
            "This is offensive test content"
        )

        self.assertFalse(Result["allowed"])
        self.assertEqual(Result["action"], "BLOCK")
        self.assertEqual(
            Result["reason"],
            "OFFENSIVE_CONTENT",
        )

        self.assertEqual(
            BlockingDecision.objects.count(),
            1,
        )

        SavedDecision = BlockingDecision.objects.first()

        self.assertEqual(
            SavedDecision.Action,
            "BLOCK",
        )

        self.assertEqual(
            SavedDecision.Reason,
            "OFFENSIVE_CONTENT",
        )

    def test_empty_content_is_rejected(self):
        """
        Verify that empty content is rejected before detection.
        """

        with self.assertRaises(InvalidContentError):
            BlockingService().EvaluateContent("")

        self.assertEqual(
            BlockingDecision.objects.count(),
            0,
        )

    def test_whitespace_content_is_rejected(self):
        """
        Verify that whitespace-only content is rejected.
        """

        with self.assertRaises(InvalidContentError):
            BlockingService().EvaluateContent("   ")

        self.assertEqual(
            BlockingDecision.objects.count(),
            0,
        )

    def test_non_string_content_is_rejected(self):
        """
        Verify that non-string input is rejected at the service boundary.
        """

        with self.assertRaises(InvalidContentError):
            BlockingService().EvaluateContent(None)

        self.assertEqual(
            BlockingDecision.objects.count(),
            0,
        )


class DetectionServiceTest(TestCase):
    """
    Tests the detection contract.

    These tests ensure that malformed ML output cannot reach
    the BlockingRules layer.
    """

    def test_valid_detection_result_is_accepted(self):
        """
        Verify that a valid detection result is accepted and normalized.
        """

        DetectionResult = {
            "label": "safe",
            "confidence": 0.95,
        }

        Result = DetectionService._ValidateResult(
            DetectionResult
        )

        self.assertEqual(Result["label"], "safe")
        self.assertEqual(Result["confidence"], 0.95)

    def test_missing_detection_field_is_rejected(self):
        """
        Verify that incomplete detection output is rejected.
        """

        DetectionResult = {
            "label": "safe",
        }

        with self.assertRaises(DetectionError):
            DetectionService._ValidateResult(
                DetectionResult
            )

    def test_unsupported_label_is_rejected(self):
        """
        Verify that unsupported detection labels are rejected.
        """

        DetectionResult = {
            "label": "unknown",
            "confidence": 0.95,
        }

        with self.assertRaises(DetectionError):
            DetectionService._ValidateResult(
                DetectionResult
            )

    def test_confidence_above_one_is_rejected(self):
        """
        Verify that confidence values above 1.0 are rejected.
        """

        DetectionResult = {
            "label": "offensive",
            "confidence": 1.5,
        }

        with self.assertRaises(DetectionError):
            DetectionService._ValidateResult(
                DetectionResult
            )

    def test_negative_confidence_is_rejected(self):
        """
        Verify that negative confidence values are rejected.
        """

        DetectionResult = {
            "label": "safe",
            "confidence": -0.1,
        }

        with self.assertRaises(DetectionError):
            DetectionService._ValidateResult(
                DetectionResult
            )

    def test_non_numeric_confidence_is_rejected(self):
        """
        Verify that non-numeric confidence values are rejected.
        """

        DetectionResult = {
            "label": "safe",
            "confidence": "high",
        }

        with self.assertRaises(DetectionError):
            DetectionService._ValidateResult(
                DetectionResult
            )

    def test_boolean_confidence_is_rejected(self):
        """
        Verify that boolean values cannot be used as confidence scores.
        """

        DetectionResult = {
            "label": "safe",
            "confidence": True,
        }

        with self.assertRaises(DetectionError):
            DetectionService._ValidateResult(
                DetectionResult
            )
