import subprocess
import tempfile
import os
from typing import TypedDict, Tuple, List

class CodingRoundState(TypedDict):
    user_code: str
    test_cases: List[Tuple[str, str]]
    passed_all: bool
    feedback: str

def evaluate_submission_node_local(state: CodingRoundState):
    code = state["user_code"]
    test_cases = state["test_cases"]
    feedback = []

    all_passed = True

    with tempfile.TemporaryDirectory() as tmpdir:
        user_code_path = os.path.join(tmpdir, "user_code.py")
        with open(user_code_path, "w") as f:
            f.write(code)

        for i, (inp, expected) in enumerate(test_cases):
            try:
                result = subprocess.run(
                    ["python", user_code_path],
                    input=inp,
                    capture_output=True,
                    text=True,
                    timeout=5  # prevent infinite loops
                )

                actual_output = result.stdout.strip()
                passed = actual_output == expected.strip()

                if not passed:
                    all_passed = False
                    feedback.append(f"❌ Test case {i+1} failed.\nInput: `{inp}`\nExpected: `{expected}`\nGot: `{actual_output}`")

                if result.stderr:
                    feedback.append(f"⚠️ Error during execution:\n{result.stderr.strip()}")

            except subprocess.TimeoutExpired:
                all_passed = False
                feedback.append(f"⏱️ Test case {i+1} timed out. Input: `{inp}`")

            except Exception as e:
                all_passed = False
                feedback.append(f"🚨 Error on test case {i+1}: {str(e)}")

    return {
        **state,
        "passed_all": all_passed,
        "feedback": "\n\n".join(feedback) if feedback else "✅ All test cases passed!"
    }


if __name__ == "__main__":
    test_state = {
        "user_code": """
n : int(input())
print(n * 3)
""",
        "test_cases": [
            ("2", "4"),
            ("5", "10"),
            ("0", "0"),
        ],
        "passed_all": False,
        "feedback": ""
    }

    result = evaluate_submission_node_local(test_state)

    print("Passed All:", result["passed_all"])
    print("Feedback:\n", result["feedback"])
