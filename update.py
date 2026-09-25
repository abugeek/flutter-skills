"""One-command refresh: fetch sources -> diff -> regenerate -> staleness scan -> compile checks -> UPDATE_REPORT.md.
The model only needs to read UPDATE_REPORT.md.  Usage: python3 update.py [--no-fetch] [--no-checks]"""
import hashlib, json, re, subprocess, sys
from datetime import date
from pathlib import Path

import fetch_sources

ROOT = Path(__file__).parent
SRC, SKILLS, GEN = ROOT / "sources", ROOT / ".claude/skills", ROOT / "generated"
MANIFEST = GEN / "source-manifest.json"  # committed, so CI (without sources/) can still diff against the last run


def snapshot():
    return {str(p.relative_to(SRC)): hashlib.sha1(p.read_bytes()).hexdigest()
            for p in SRC.rglob("*") if p.is_file()} if SRC.exists() else {}


def load_packages():
    f = SRC / "packages.json"
    return json.loads(f.read_text()) if f.exists() else {}


def frontmatter(md):
    m = re.match(r"---\n(.*?)\n---", md, re.S)
    return dict(re.findall(r"^(\w+): (.+)$", m[1], re.M)) if m else {}


# ---------- generators (no AI) ----------

def gen_breaking_changes():
    idx = SRC / "flutter_breaking/_index.json"
    if not idx.exists():
        return 0
    rows = []
    for e in json.loads(idx.read_text()):
        f = SRC / f"flutter_breaking/{e['slug']}.md"
        text = f.read_text() if f.exists() else ""
        guide = text.split("## Migration guide", 1)[-1].split("\n## ", 1)[0] if "## Migration guide" in text else ""
        summary = next((l.strip() for l in guide.split("\n\n") if l.strip() and not l.lstrip().startswith(("```", ":::", "<"))), "")
        if not summary or summary.startswith(("*", "-", "|", "#")):  # guide opens with a list/table -> use page description
            d = re.search(r"^description: >?-?\s*\n?((?:\s+.+\n)+|.+)", text, re.M)
            summary = d[1] if d else summary
        summary = re.sub(r"\s+", " ", summary).strip()[:300]
        before = after = ""
        if m := re.search(r"```dart diff\n(.*?)```", guide, re.S):  # diff style
            lines = m[1].splitlines()
            before = "\n".join(l[1:].strip() for l in lines if l.startswith("-"))
            after = "\n".join(l[1:].strip() for l in lines if l.startswith("+"))
        else:  # "Code before migration:" / "Code after migration:" style
            blocks = re.findall(r"(?:before|after) migration[^\n]*\n+```dart\n(.*?)```", guide, re.S | re.I)
            if len(blocks) >= 2:
                before, after = blocks[0].strip(), blocks[1].strip()
        if re.search(r"(isn't|not|aren't) (be )?supported by `?dart fix|`?dart fix`? (can't|cannot|doesn't)", text, re.I):
            fix = "no"
        elif re.search(r"dart fix", text, re.I):
            fix = "yes"
        else:
            fix = "unstated"
        rows.append((e, summary, before, after, fix))
    out = ["# Flutter breaking changes & migrations (generated)", "",
           f"Generated {date.today()} from docs.flutter.dev/release/breaking-changes by `update.py`. Do not edit by hand.",
           "Run `dart fix --apply` first (column `dart fix`), then fix the rest manually.", ""]
    for e, summary, before, after, fix in rows:
        out += [f"## {e['version']} · {e['title']}", f"dart fix: {fix} · https://docs.flutter.dev/release/breaking-changes/{e['slug']}", "", summary, ""]
        if before.strip() and after.strip():
            cut = lambda c: "\n".join(c.splitlines()[:8])
            out += ["```dart", "// before", cut(before), "// after", cut(after), "```", ""]
    GEN.mkdir(exist_ok=True)
    (GEN / "flutter-breaking-changes.md").write_text("\n".join(out))
    return len(rows)


def gen_versions(pk):
    if not pk:
        return
    fl = pk.get("_flutter_stable", {})
    out = ["# Current package versions (generated)", "",
           f"Generated {date.today()} from pub.dev by `update.py`. Flutter stable {fl.get('version')} / Dart {fl.get('dart')} ({fl.get('released')}).", "",
           "| package | version | published | likes | downloads/30d | note |", "|---|---|---|---|---|---|"]
    for name, v in sorted((k, v) for k, v in pk.items() if not k.startswith("_")):
        stale = v["published"] and v["published"] < str(date.today().year - 2)
        note = "DISCONTINUED" if v["discontinued"] else ("no release in 2+ years" if stale else "")
        out.append(f"| {name} | {v['version']} | {v['published']} | {v['likes']} | {v['downloads_30d']} | {note} |")
    GEN.mkdir(exist_ok=True)
    (GEN / "package-versions.md").write_text("\n".join(out) + "\n")


def gen_index():
    skills = []
    for f in sorted(SKILLS.glob("*/SKILL.md")):
        if f.parent.name == "flutter-skills-index":
            continue
        fm = frontmatter(f.read_text())
        refs = sorted(p.name for p in (f.parent / "references").glob("*.md")) if (f.parent / "references").exists() else []
        skills.append((fm.get("name", f.parent.name), fm.get("description", ""), refs))
    body = ["---", "name: flutter-skills-index",
            "description: Index of all Flutter/Dart skills in this repo and which one to load for a task - architecture, folder structure, state management, Dart style, testing, performance, migrations, local data, lints. Use this first when a Flutter task is broad or you are unsure which Flutter skill applies.",
            "---", "", "# Flutter skills index (generated by `update.py` from each skill's frontmatter)", "",
            "Load the ONE most specific skill; load a second only if the task clearly spans both.", ""]
    for name, desc, refs in skills:
        short = desc.split(" Use this")[0]
        body.append(f"- **{name}**: {short}" + (f" (references: {', '.join(refs)})" if refs else ""))
    body += ["", "Generated data (always current): `generated/package-versions.md`, `generated/flutter-breaking-changes.md`."]
    d = SKILLS / "flutter-skills-index"
    d.mkdir(exist_ok=True)
    (d / "SKILL.md").write_text("\n".join(body) + "\n")
    return len(skills)


# ---------- checks (no AI) ----------

def stale_versions(pk):
    """Find 'pkg X.Y' mentions in skills whose major (or minor for 0.x) differs from pub.dev latest."""
    hits = []
    for f in SKILLS.rglob("*.md"):
        for m in re.finditer(r"`?\b([a-z][a-z0-9_]+)`? v?(\d+)\.(\d+)", f.read_text()):
            name, major, minor = m[1], int(m[2]), int(m[3])
            latest = (pk.get(name) or {}).get("version")
            if not latest:
                continue
            lmaj, lmin = map(int, latest.split(".")[:2])
            if major != lmaj or (major == 0 and minor != lmin):
                hits.append(f"{f.relative_to(ROOT)}: `{name} {major}.{minor}` but pub.dev latest is {latest}")
    return sorted(set(hits))


def run(cmd, cwd):
    r = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)
    tail = "\n".join((r.stdout + r.stderr).strip().splitlines()[-6:])
    return r.returncode == 0, tail


def main():
    fetch = "--no-fetch" not in sys.argv
    if MANIFEST.exists():
        m = json.loads(MANIFEST.read_text())
        before, old_versions = m["files"], m["packages"]
    else:
        before, old_versions = snapshot(), {k: v["version"] for k, v in load_packages().items() if not k.startswith("_")}
    if fetch:
        fetch_sources.main()
    after, pk = snapshot(), load_packages()
    changed = sorted(k for k in after if k in before and after[k] != before[k] and k != "packages.json")
    added = sorted(set(after) - set(before))
    removed = sorted(set(before) - set(after))
    bumps = [f"{k}: {old_versions[k]} → {v['version']}" for k, v in pk.items()
             if not k.startswith("_") and k in old_versions and old_versions[k] != v["version"]]
    GEN.mkdir(exist_ok=True)
    MANIFEST.write_text(json.dumps({"files": after, "packages": {k: v["version"] for k, v in pk.items() if not k.startswith("_")}}, indent=0, sort_keys=True))
    n_breaking = gen_breaking_changes()
    gen_versions(pk)
    n_skills = gen_index()
    stale = stale_versions(pk)
    checks = []
    if "--no-checks" not in sys.argv:
        checks = [("dart snippets", *run("dart pub get >/dev/null && dart analyze", ROOT / "checks/dart")),
                  ("flutter snippets", *run("flutter pub get >/dev/null && dart analyze && flutter test", ROOT / "checks/flutter"))]
    fl = pk.get("_flutter_stable", {})
    r = [f"# Update report {date.today()}", "",
         f"Flutter stable {fl.get('version')} / Dart {fl.get('dart')}. Skills indexed: {n_skills}. Breaking-change entries: {n_breaking}.", "",
         "## Action needed" if (changed or added or removed or bumps or stale or not all(c[1] for c in checks)) else "## Nothing to do - all current", ""]
    if checks:
        r += ["### Compile checks"] + [f"- {'✅' if ok else '❌'} {name}" + ("" if ok else f"\n```\n{tail}\n```") for name, ok, tail in checks] + [""]
    if stale:
        r += ["### Skills mentioning outdated major versions"] + [f"- {s}" for s in stale] + [""]
    if bumps:
        r += ["### Package version bumps since last run (check changelogs of majors only)"] + [f"- {b}" for b in bumps] + [""]
    if changed or added or removed:
        r += ["### Source docs changed (read ONLY these, with `git diff --no-index` or a diff tool)"] + \
             [f"- changed: sources/{c}" for c in changed] + [f"- new: sources/{a}" for a in added] + [f"- removed: sources/{x}" for x in removed] + [""]
    (ROOT / "UPDATE_REPORT.md").write_text("\n".join(r) + "\n")
    print("\n".join(r))


if __name__ == "__main__":
    main()
