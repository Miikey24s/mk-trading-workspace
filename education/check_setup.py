"""Validate local course state and numeric answer keys; does not evaluate teaching efficacy."""

import json
import re
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path


def check(condition, message):
    if not condition:
        raise ValueError(message)


def check_course(root, state):
    course = json.loads((root / "course.json").read_text(encoding="utf-8"))
    bank = json.loads((root / "assessments/course-checks.json").read_text(encoding="utf-8"))
    modules = course["modules"]
    lesson_ids = [lesson["id"] for module in modules for lesson in module["lessons"]]
    checks = {item["id"]: item for item in bank["items"]}
    check(len(modules) == 8 and len(lesson_ids) == 24, "Expected 8 modules / 24 lessons")
    check(len(set(lesson_ids)) == 24, "Duplicate course lesson IDs")
    check(len(checks) == len(bank["items"]) == 24, "Duplicate or missing course checks")
    check(set(checks) == set(lesson_ids), "Course / answer-key IDs differ")
    check(course["primary_language"] == "vi", "Wrong course language")
    check(course["english_role"] == "terminology_support_only", "English scope drift")
    check(course["version"] == state["course_version"], "Course version mismatch")
    check(course["guided_demo_starts_at"] == course["start_lesson"],
          "Guided demo should start alongside the first lesson")
    check(course["early_platform_orientation"] in lesson_ids, "Unknown platform orientation")
    check(course["live_practice_required_for_completion"] is False,
          "Real money must not be required for course completion")
    practice = state["practice_track"]
    check(practice["plan_file"] == course["practice_plan_file"], "Practice plan mismatch")
    check(practice["guided_demo"]["starts_at"] == course["guided_demo_starts_at"],
          "Demo start mismatch")
    trial = practice["live_trial"]
    check(trial["required_for_course_completion"] is False, "Live completion gate drift")
    check(trial["budget"]["cap_vnd"] > 0, "Invalid planning budget")
    limits = trial["proposed_limits"]
    check(0 < limits["planned_loss_per_trade_vnd"] <= limits["session_pause_loss_vnd"]
          <= limits["trial_pause_loss_vnd"] <= trial["budget"]["cap_vnd"],
          "Trial planning limits inconsistent")
    check(limits["loss_cap_guaranteed"] is False, "Stops cannot guarantee a loss cap")
    if trial["status"] == "planning_only":
        check(trial["implementation_authorization"] == "not_requested"
              and trial["started_on"] is None and not trial["tutor_external_actions"],
              "Planning approval must not imply external action")
    check(state["entry_assessment"]["status"] == "closed_sufficient_to_start",
          "Initial assessment should be closed")
    current = state["main_course"]["current_lesson_id"]
    check(current in lesson_ids, "Unknown current lesson")
    if state["pending_status"] == "ready_to_start":
        check(state["pending_activity"]["id"] == current, "Pending / current lesson mismatch")
        check(state["pending_activity"]["prompt_vi"] is None, "Unasked exercise set as pending")
    check(set(state["main_course"]["completed_lessons"]) <= set(lesson_ids),
          "Unknown completed lesson")
    check(set(state["main_course"]["completed_modules"]) <= {m["id"] for m in modules},
          "Unknown completed module")
    attempt_ids = [item["id"] for item in state["attempts"]]
    check(len(set(attempt_ids)) == len(attempt_ids), "Duplicate learner attempts")
    for skill, record in state["competencies"].items():
        check(set(record["evidence"]) <= set(attempt_ids), f"Missing evidence record: {skill}")

    docs = [root / name for name in
            ("README.md", "COURSE.md", "reference.md", "practice/workbook.md",
             "research/course-sources.md")]
    docs.append(root / course["practice_plan_file"])
    for module in modules:
        path = root / module["file"]
        content = path.read_text(encoding="utf-8")
        headers = re.findall(r"^## (M\d{2}-L\d{2}) —", content, re.MULTILINE)
        check(headers == [lesson["id"] for lesson in module["lessons"]],
              f"Lesson headers mismatch: {path.name}")
        check(content.count("**Bài thực hành:**") == 3, f"Missing practice: {path.name}")
        check(content.count("**Đạt khi:**") == 3, f"Missing rubric: {path.name}")
        docs.append(path)
    for path in docs:
        content = path.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)]+)\)", content):
            if target.startswith(("https://", "http://", "#")):
                continue
            local = (path.parent / target.split("#", 1)[0]).resolve()
            check(local.is_relative_to(root.resolve()), f"Link outside education: {target}")
            check(local.exists(), f"Broken local link in {path.name}: {target}")
    for item in checks.values():
        for field in ("hint_vi", "answer_vi", "rubric_vi"):
            check(bool(item[field].strip()), f"Empty {field}: {item['id']}")

    d = Decimal
    conversion = datetime(2026, 9, 10, 18) + timedelta(hours=7)
    raw_lots = (d(15) - d(3)) / (d(25) * d(10))
    rounded_lots = (raw_lots // d("0.01")) * d("0.01")
    numeric = {
        "M01-L01": {"net_usd": d(1000) * (d("1.1000") - d("1.1003"))},
        "M01-L03": {"equity_usd": d(500) - 12, "free_margin_usd": d(500) - 12 - 40,
                     "closed_balance_usd": d(500) - 12},
        "M02-L01": {"units_eur": d("0.03") * 100000,
                     "pips": (d("1.1020") - d("1.1000")) / d("0.0001"),
                     "gross_usd": d(3000) * (d("1.1020") - d("1.1000"))},
        "M02-L02": {"gross_usd": d(4000) * (d("1.1000") - d("1.1015"))},
        "M02-L03": {"net_usd": -d(6) - d("0.80") - d("0.20")},
        "M03-L01": {"raw_lots": raw_lots, "lots": rounded_lots,
                     "planned_loss_usd": rounded_lots * 25 * 10 + 3},
        "M03-L02": {"r1": d(15)/10, "r2": -d(10)/10, "r3": d(5)/10,
                     "total_r": (d(15)-10+5)/10},
        "M03-L03": {"drawdown_pct": (d(1200)-1080)/1200*100,
                     "total_return_pct": (d(1080)-1000)/1000*100},
        "M04-L03": {"hour_vn": d(conversion.hour), "day_vn": d(conversion.day)},
        "M05-L03": {"net_r": d(6)-4-10*d("0.25"),
                     "mean_r": (d(6)-4-10*d("0.25"))/10},
        "M06-L01": {"units": d("0.03") * 100000},
        "M07-L02": {"equity_usd": d(10000)-80-150-30,
                     "distance_to_floor_usd": d(10000)-80-150-30-9700},
        "M08-L02": {"net_r": d(1)-10*d("0.2")}
    }
    check({key for key, item in checks.items() if "numeric" in item} == set(numeric),
          "Unvalidated numeric exercise")
    count = 0
    for lesson, values in numeric.items():
        check(set(values) == set(checks[lesson]["numeric"]), f"Numeric fields: {lesson}")
        for name, calculated in values.items():
            check(calculated == d(checks[lesson]["numeric"][name]),
                  f"Wrong course key: {lesson}.{name}")
            count += 1

    worked = [
        (d(1000)*(d("1.1000")-d("1.1002")), d("-0.20")),
        (d(200)-4-20, d(176)),
        (d(2000)*(d("1.1050")-d("1.1020")), d(6)),
        (d(6)-d("0.40")-d("0.10"), d("5.50")),
        ((d(10)-2)/(20*10), d("0.04")),
        ((d(1100)-990)/1100*100, d(10)),
        ((d(1000)-800)/800*100, d(25)),
        (d(4)*2-6-10*d("0.1"), d(1)),
        (d(10000)-100-120-20, d(9760)),
        (d(10600)-1000, d(9600)),
        (d(1000)*d("1.1000")/20, d(55)),
        (d(1000)*(d("1.0980")-d("1.1000")), d(-2))
    ]
    for index, (actual, expected) in enumerate(worked):
        check(actual == expected, f"Worked example mismatch {index}")
    print(f"PASS: 8 modules, 24 lessons/keys/rubrics, internal links; "
          f"{count} numeric fields and {len(worked)} worked calculations.")


def main():
    root = Path(__file__).resolve().parent
    bank = json.loads((root / "assessments/entry-check.json").read_text(encoding="utf-8"))
    state = json.loads((root / "progress.json").read_text(encoding="utf-8"))
    items = {item["id"]: item for item in bank["items"]}
    check(len(items) == len(bank["items"]), "Duplicate exercise IDs")
    check(state["pending_exercise_id"] is None or state["pending_exercise_id"] in items,
          "Unknown pending exercise")
    allowed = {"not_assessed", "needs_practice", "supported", "independent", "retained"}
    for name, record in state["competencies"].items():
        check(record["status"] in allowed, f"Unknown status: {name}")
        if record["status"] != "not_assessed":
            check(bool(record["evidence"]), f"Missing evidence: {name}")
    for item in items.values():
        check(bool(item["prompt_en"]) and bool(item["prompt_vi"]), "Missing bilingual prompt")
        check(all(skill in state["competencies"] for skill in item["skills"]), "Unknown skill")

    def after_changes(data):
        return (Decimal(data["initial_vnd"])
                * (1 - Decimal(data["loss_pct"]) / 100)
                * (1 + Decimal(data["gain_pct"]) / 100))

    d1 = items["D01"]
    check(after_changes(d1["inputs"]) == d1["expected"]["final_balance_vnd"], "D01 key")
    check(after_changes(d1["transfer"]) == d1["transfer"]["expected_final_balance_vnd"], "D01 transfer key")
    d2 = items["D02"]["inputs"]
    net = d2["wins"] * d2["win_vnd"] - d2["losses"] * d2["loss_vnd"]
    net -= (d2["wins"] + d2["losses"]) * d2["fee_per_trade_vnd"]
    check(net == items["D02"]["expected"]["net_pnl_vnd"], "D02 key")
    check(items["D03"]["expected"]["next_heads_probability"] == 1 / 2, "D03 fair-coin key")
    d4 = items["D04"]
    delta = d4["inputs"]["final_usd"] - d4["inputs"]["initial_usd"]
    check(delta == d4["expected"]["change_usd"], "D04 amount key")
    check(Decimal(delta) / d4["inputs"]["initial_usd"] * 100 == d4["expected"]["change_pct"], "D04 percent key")
    check(delta < 0 and d4["expected"]["direction"] == "down", "D04 direction key")
    print("PASS: 4 archived entry items, 7 legacy answer-key checks and skill states.")
    check_course(root, state)
    print(f"Recorded learner attempts: {len(state['attempts'])}. Learning outcomes are not validated by this test.")


if __name__ == "__main__":
    main()
