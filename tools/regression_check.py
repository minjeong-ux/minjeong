"""환각 회귀 테스트: 모델 출력이 기대 핵심값을 포함하고 금지 표현을 포함하지 않는지 자동 판정한다.

사용법: python3 tools/regression_check.py tests/regression_cases.json tests/sample_outputs
  - 출력 폴더에는 케이스 ID별로 <ID>.txt 파일(모델 응답 원문)을 저장해 둔다.
"""
import json
import sys
from pathlib import Path


def judge(case, output):
    missing = [s for s in case["must_include"] if s not in output]
    banned = [s for s in case["must_not_include"] if s in output]
    if banned:
        return "Fail", f"금지 표현 포함: {banned}"
    if missing:
        # 기대 A인데 핵심값 없이 보류만 했다면 환각은 아니지만 과소응답
        if case["expected"] == "A" and "확인 필요" in output:
            return "Pass-B*", f"과소응답(핵심값 누락: {missing})"
        return "Fail", f"핵심값 누락: {missing}"
    return f"Pass-{case['expected']}", ""


def main():
    cases_path, outputs_dir = Path(sys.argv[1]), Path(sys.argv[2])
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    passed = 0
    print("| ID | 유형 | 기대 | 판정 | 비고 |")
    print("|---|---|---|---|---|")
    for case in cases:
        out_file = outputs_dir / f"{case['id']}.txt"
        if not out_file.exists():
            verdict, note = "미실행", "출력 파일 없음"
        else:
            verdict, note = judge(case, out_file.read_text(encoding="utf-8"))
        passed += verdict.startswith("Pass") and not verdict.endswith("*")
        print(f"| {case['id']} | {case['category']} | {case['expected']} | {verdict} | {note} |")
    print(f"\nPass율: {passed}/{len(cases)} = {passed / len(cases):.0%}")
    sys.exit(0 if passed == len(cases) else 1)


if __name__ == "__main__":
    main()
