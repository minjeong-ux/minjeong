"""정책 JSON으로 환불액을 계산해 [확정 수치(담당자 기입)] 블록을 출력한다.

모델에게 계산을 맡기지 않기 위한 도구다. 결과를 입력 템플릿 v3에 그대로 붙여넣는다.

사용법: python3 tools/refund_calc.py policies/data_analysis_v3.json --done 1
"""
import argparse
import json
import math
from fractions import Fraction


def calc_refund(policy, done):
    fee = policy["fee"]
    total = policy["total_sessions"]
    if not 0 <= done <= total:
        raise ValueError(f"진행 회차는 0~{total} 사이여야 합니다: {done}")
    if done == 0:
        return fee, Fraction(1), policy["before_start_clause"]
    elapsed = Fraction(done, total)
    for bracket in policy["refund_brackets"]:
        # 경계값 처리: "1/3 경과 전"은 경과 비율이 1/3 미만일 때만 해당
        if elapsed < Fraction(bracket["elapsed_before"]):
            rate = Fraction(bracket["rate"])
            amount = fee * rate
            amount = math.floor(amount) if policy["rounding"] == "floor" else round(amount)
            return amount, rate, bracket["clause"]
    return 0, Fraction(0), policy["after_last_clause"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("policy")
    parser.add_argument("--done", type=int, required=True, help="환불 신청 시점까지 진행된 회차 수")
    args = parser.parse_args()

    with open(args.policy, encoding="utf-8") as f:
        policy = json.load(f)
    amount, rate, clause = calc_refund(policy, args.done)
    elapsed = Fraction(args.done, policy["total_sessions"])
    print("[확정 수치(담당자 기입)]")
    print(f"- 환불액: {amount:,}원")
    print(f"- 적용 구간/조항: {clause} (경과 {args.done}/{policy['total_sessions']}회 = {float(elapsed):.1%}, 환불률 {rate})")
    print(f"- 정책 버전: {policy['version']} ({policy['effective_date']} 시행, {policy['applies_by']} 기준)")


if __name__ == "__main__":
    main()
