"""Script-grade eval answers with regex checks (no AI). evals file: [{"id","name","checks":[{"text","must"| "must_not": regex}]}]
A check may add "in": "code" to search only inside ```code blocks``` (so prose like "valueOrNull -> value" doesn't count).
Usage: python3 grade.py EVALS.json WORKSPACE_ITERATION_DIR  -> writes <eval>/<config>/run-1/grading.json + prints a table."""
import json, re, sys
from pathlib import Path

evals, ws = json.loads(Path(sys.argv[1]).read_text()), Path(sys.argv[2])
for ev in evals:
    for answer in sorted(ws.glob(f"eval-{ev['id']}-*/*/run-1/outputs/answer.md")):
        full, results = answer.read_text(), []
        code = "\n".join(re.findall(r"```\w*\n(.*?)```", full, re.S))
        for c in ev["checks"]:
            text = code if c.get("in") == "code" else full
            if "must" in c:
                m = re.search(c["must"], text, re.I | re.S)
                results.append({"text": c["text"], "passed": bool(m), "evidence": m[0][:120] if m else "not found"})
            else:
                m = re.search(c["must_not"], text, re.I | re.S)
                results.append({"text": c["text"], "passed": not m, "evidence": f"found: {m[0][:120]}" if m else "absent"})
        n = sum(r["passed"] for r in results)
        out = answer.parent.parent / "grading.json"
        out.write_text(json.dumps({"expectations": results, "summary": {"passed": n, "failed": len(results) - n,
                                   "total": len(results), "pass_rate": round(n / len(results), 3)}}, indent=1))
        print(f"{answer.parts[-5]:45} {answer.parts[-4]:14} {n}/{len(results)}")
