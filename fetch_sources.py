"""Fetch primary-source docs (raw markdown from publishers' GitHub repos) + package stats from pub.dev.
Usage: python3 fetch_sources.py   (stdlib only; uses curl for TLS)"""
import json, re, subprocess, time
from datetime import date
from pathlib import Path

GH = "https://raw.githubusercontent.com"
FLUTTER = f"{GH}/flutter/website/main/sites/docs/src/content"
RIVERPOD = f"{GH}/rrousselGit/riverpod/master/website/docs"
BLOC = f"{GH}/felangel/bloc/master/docs/src/content/docs"
VGV = "https://engineering.verygood.ventures"  # Very Good Ventures handbook (recommended by docs.flutter.dev); serves .md
DART = f"{GH}/dart-lang/site-www/main/src/content"

SOURCES = {
    "flutter": [f"{FLUTTER}/{p}.md" for p in [
        "app-architecture/guide", "app-architecture/recommendations", "app-architecture/concepts",
        "app-architecture/design-patterns", "app-architecture/case-study/index",
        "app-architecture/case-study/ui-layer", "app-architecture/case-study/data-layer",
        "app-architecture/case-study/dependency-injection", "app-architecture/case-study/testing", "data-and-backend/state-mgmt/options",
        "data-and-backend/state-mgmt/ephemeral-vs-app", "perf/best-practices", "perf/isolates",
        "perf/app-size", "perf/impeller", "perf/rendering-performance", "testing/overview", "release/whats-new"]],
    "riverpod": [f"{RIVERPOD}/{p}.mdx" for p in [
        "whats_new", "3.0_migration", "root/do_dont", "concepts2/providers", "concepts2/refs",
        "concepts2/consumers", "concepts2/auto_dispose", "concepts2/family", "concepts2/mutations",
        "concepts2/offline", "concepts2/retry", "concepts2/overrides", "concepts/about_code_generation",
        "how_to/testing", "how_to/select", "migration/from_change_notifier", "migration/from_state_notifier"]],
    "bloc": [f"{BLOC}/{p}.mdx" for p in [
        "architecture", "bloc-concepts", "flutter-bloc-concepts", "modeling-state",
        "naming-conventions", "testing", "migration", "faqs"]],
    # official reference implementation of the Flutter architecture guide
    "flutter_compass_app": [f"{GH}/flutter/samples/main/compass_app/app/lib/utils/{f}.dart" for f in ["command", "result"]],
    "vgv": [f"{VGV}/{p}.md" for p in [
        "architecture/architecture", "architecture/barrel_files", "architecture/ffca/overview",
        "architecture/ffca/project_structure", "architecture/ffca/presentation", "architecture/ffca/domain",
        "architecture/ffca/data", "development/code_style", "development/error_handling",
        "development/state_management/bloc_event_transformers", "development/state_management/bloc_state_handling",
        "development/testing/testing_best_practices", "development/testing/testing_golden_file",
        "development/ui/widgets", "development/ui/layouts", "general-practices/security_in_mobile_apps"]],
    "dart": [f"{DART}/{p}.md" for p in [
        "language/patterns", "language/pattern-types", "language/records", "language/class-modifiers",
        "language/extension-types", "language/dot-shorthands", "language/collections",
        "language/primary-constructors", "language/constructors", "effective-dart/style", "effective-dart/design",
        "resources/language/evolution"]],
}

# state-management candidates + packages the skills recommend (versions must be current)
PACKAGES = """flutter_bloc bloc bloc_test bloc_concurrency hydrated_bloc flutter_riverpod riverpod
riverpod_annotation riverpod_generator riverpod_lint hooks_riverpod provider signals get mobx
flutter_mobx flutter_hooks bloc_presentation freezed json_serializable dart_mappable equatable
copy_with_extension dio http go_router auto_route drift sqflite isar hive_ce shared_preferences
flutter_secure_storage patrol alchemist mocktail mockito very_good_analysis flutter_lints
leancode_lint widgetbook cached_network_image get_it injectable melos""".split()


BREAKING = f"{FLUTTER}/release/breaking-changes"
BREAKING_SINCE = (3, 27)  # keep ~2 years of migrations


def fetch_breaking(out):
    """Flutter breaking-change guides since BREAKING_SINCE -> sources/flutter_breaking/ + _index.json"""
    index = curl(f"{BREAKING}/index.md") or ""
    d = out / "flutter_breaking"
    d.mkdir(parents=True, exist_ok=True)
    entries, version = [], None
    links = dict(re.findall(r"^\[(.+?)\]: /release/breaking-changes/(\S+)$", index, re.M))
    for line in index.splitlines():
        if m := re.match(r"### Released in Flutter (\d+)\.(\d+)", line):
            version = (int(m[1]), int(m[2]))
        elif version and version >= BREAKING_SINCE and (m := re.match(r"\* \[(.+?)\]\[\]", line)) and m[1] in links:
            entries.append({"version": f"{version[0]}.{version[1]}", "title": m[1], "slug": links[m[1]]})
    for e in entries:
        text = curl(f"{BREAKING}/{e['slug']}.md")
        if text:
            (d / f"{e['slug']}.md").write_text(text)
    (d / "_index.json").write_text(json.dumps(entries, indent=1))
    print(f"breaking changes: {len(entries)} guides since {BREAKING_SINCE}")


def curl(url):
    r = subprocess.run(["curl", "-sfL", "--max-time", "30", url], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def clean_mdx(text, url):
    # inline code snippets the docs pull in via `import x from 'raw-loader!./file.dart'`
    for var, rel in re.findall(r"^import (\w+) from ['\"]raw-loader!([^'\"]+)['\"]", text, flags=re.M):
        code = curl(url.rsplit("/", 1)[0] + "/" + rel.removeprefix("./")) or ""
        code = re.sub(r"^\s*/\* SNIPPET (START|END) \*/\s*$\n?", "", code, flags=re.M)
        text = re.sub(r"<CodeBlock>\{\w*\(?" + var + r"\)?\}</CodeBlock>", f"```dart\n{code.strip()}\n```", text)
    text = re.sub(r"^import .*$\n?", "", text, flags=re.M)          # MDX imports
    text = re.sub(r"<(\w+)[^>]*/>", "", text)                         # self-closing JSX components
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def main():
    out = Path("sources")
    today = date.today().isoformat()
    for publisher, urls in SOURCES.items():
        (out / publisher).mkdir(parents=True, exist_ok=True)
        for url in urls:
            # path after the docs root, flattened: "perf/isolates.md" -> "perf__isolates"
            rel = re.split(r"/content/|/docs/|/lib/utils/|\.ventures/", url)[-1]
            name = rel.rsplit(".", 1)[0].replace("/", "__")
            text = curl(url)
            if not text:
                print(f"FAIL {url}")
                continue
            if url.endswith(".dart"):  # keep code verbatim so it still compiles
                (out / publisher / f"{name}.dart").write_text(f"// source: {url} | fetched: {today}\n{text}")
            else:
                (out / publisher / f"{name}.md").write_text(f"<!-- source: {url} | fetched: {today} -->\n\n{clean_mdx(text, url)}\n")
            print(f"ok {publisher}/{name}")

    fetch_breaking(out)

    stats = {}
    for pkg in PACKAGES:
        info = json.loads(curl(f"https://pub.dev/api/packages/{pkg}") or "{}")
        score = json.loads(curl(f"https://pub.dev/api/packages/{pkg}/score") or "{}")
        latest = info.get("latest", {})
        stats[pkg] = {
            "version": latest.get("version"),
            "published": (latest.get("published") or "")[:10],
            "likes": score.get("likeCount"),
            "downloads_30d": score.get("downloadCount30Days"),
            "points": score.get("grantedPoints"),
            "discontinued": info.get("isDiscontinued", False),
        }
        time.sleep(0.2)
    releases = json.loads(curl("https://storage.googleapis.com/flutter_infra_release/releases/releases_macos.json"))
    stable = next(r for r in releases["releases"] if r["hash"] == releases["current_release"]["stable"])
    stats["_flutter_stable"] = {"version": stable["version"], "dart": stable.get("dart_sdk_version"),
                                "released": stable["release_date"][:10]}
    (out / "packages.json").write_text(json.dumps(stats, indent=1))
    print(f"packages: {len(PACKAGES)}; flutter stable {stats['_flutter_stable']}")


if __name__ == "__main__":
    main()
