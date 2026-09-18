import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.ai.gemini_service import make_decision


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_CASES_FILE = PROJECT_ROOT / "candidate_pack" / "sample_test_cases.json"


FALLBACK_CASES = [
    {
        "id": "S01",
        "message": "My package arrived damaged yesterday and the order value was ₹3500.",
        "expected_action": "REQUEST_PHOTOS",
    },
    {
        "id": "S02",
        "message": "The item is unopened, non-food, worth ₹1200, and I want to return it 10 days after delivery.",
        "expected_action": "APPROVE_RETURN",
    },
    {
        "id": "S03",
        "message": "My order was dispatched 9 days ago but has still not arrived.",
        "expected_action": "OPEN_SHIPPING_INVESTIGATION",
    },
    {
        "id": "S04",
        "message": "I ordered strawberry flavor but received chocolate flavor. This happened 2 days ago.",
        "expected_action": "REPLACE_CORRECT_ITEM",
    },
    {
        "id": "S05",
        "message": "I want to return this.",
        "expected_action": "NEEDS_MORE_INFORMATION",
    },
]


def load_test_cases():
    if not TEST_CASES_FILE.exists():
        print("sample_test_cases.json not found.")
        print("Using the supplied evaluation cases defined in this runner.")
        return FALLBACK_CASES

    try:
        data = json.loads(
            TEST_CASES_FILE.read_text(encoding="utf-8")
        )
    except Exception as exc:
        print(f"Could not read sample_test_cases.json: {exc}")
        print("Using the supplied evaluation cases defined in this runner.")
        return FALLBACK_CASES

    if isinstance(data, list):
        cases = data
    elif isinstance(data, dict):
        cases = (
            data.get("cases")
            or data.get("test_cases")
            or data.get("samples")
            or []
        )
    else:
        cases = []

    normalized = []

    for index, case in enumerate(cases, start=1):
        case_id = (
            case.get("id")
            or case.get("case_id")
            or f"S{index:02d}"
        )

        message = (
            case.get("message")
            or case.get("ticket")
            or case.get("ticket_message")
        )

        expected_action = (
            case.get("expected_action")
            or case.get("expected")
            or case.get("expected_decision")
        )

        if message and expected_action:
            normalized.append(
                {
                    "id": case_id,
                    "message": message,
                    "expected_action": expected_action,
                }
            )

    if normalized:
        return normalized

    print("Could not extract evaluation cases from the supplied JSON.")
    print("Using the supplied evaluation cases defined in this runner.")
    return FALLBACK_CASES


def main():
    cases = load_test_cases()

    print("=" * 70)
    print("MaxsorLabs AI Decision Assistant - Evaluation")
    print("=" * 70)
    print()

    passed = 0

    for case in cases:
        case_id = case["id"]
        message = case["message"]
        expected = case["expected_action"]

        print(f"Running {case_id}...")
        print(f"Ticket: {message}")

        try:
            result = make_decision(message)

            actual = result["action"]
            sources = result.get("sources", [])
            confidence = result.get("confidence", 0)

            if actual == expected:
                status = "PASS"
                passed += 1
            else:
                status = "FAIL"

            print(f"Expected:   {expected}")
            print(f"Actual:     {actual}")
            print(f"Confidence: {confidence:.2f}")
            print(f"Sources:    {', '.join(sources) or 'None'}")
            print(f"Result:     {status}")

        except Exception as exc:
            print(f"Result:     ERROR")
            print(f"Error:      {exc}")
            status = "ERROR"

        print("-" * 70)

    total = len(cases)

    print()
    print("=" * 70)
    print(f"Evaluation complete: {passed}/{total} passed")
    print("=" * 70)

    if passed == total:
        print("ALL TEST CASES PASSED")
        return 0

    print("SOME TEST CASES FAILED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())