"""Scrape leancode.co sections into markdown. Usage: .venv/bin/python scrape.py glossary"""
import re, subprocess, sys, time
from pathlib import Path
from bs4 import BeautifulSoup
from markdownify import markdownify

BASE = "https://leancode.co"
UA = "flutter-knowledge-scraper (personal study; 1 req/s)"


def get(url):
    # curl instead of urllib: python.org macOS builds lack CA certs
    return subprocess.run(["curl", "-sfL", "-A", UA, "--max-time", "30", url],
                          capture_output=True, text=True, check=True).stdout


def extract(html):
    soup = BeautifulSoup(html, "html.parser")
    title = soup.h1.get_text(strip=True).removesuffix(" - LeanCode")
    meta = soup.find("meta", attrs={"name": "description"})
    desc = (meta["content"] if meta else "").replace('"', "'")
    # body lives in the container right after the <header> banner; TOC <nav> sits inside it
    body = soup.h1.find_parent("header").find_next_sibling("div")
    for tag in body.find_all(["nav", "script", "style", "svg", "button"]):
        tag.decompose()
    # blog: promo cards, author CTA, rating widget, sidebar
    for tag in body.find_all(class_=re.compile(r"^styles_(articleWrapper|sidebar)__")):
        if not tag.decomposed and not tag.find_parent("section"):  # article text is section > wrapper
            tag.decompose()
    # related glossary terms from the "See also" block
    related = sorted({a["href"].rsplit("/", 1)[-1] for a in soup.select('a[href^="/glossary/"]')
                      if a["href"].count("/") == 2})
    # embeds are often only in the Next.js JSON payload, so scan raw html
    ids = dict.fromkeys(re.findall(r"youtube(?:-nocookie)?\.com/(?:embed/|watch\?v=)([\w-]{11})", html))
    videos = [f"https://youtu.be/{i}" for i in ids]
    md = markdownify(str(body), heading_style="ATX", code_language="dart")
    md = re.sub(r"\]\(/", f"]({BASE}/", md)  # absolute links
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    return title, desc, related, md, videos


def main(section):
    urls = re.findall(r"<loc>([^<]+)</loc>", get(f"{BASE}/sitemap.xml"))
    urls = [u for u in urls if u.startswith(f"{BASE}/{section}/")]
    out = Path("leancode") / section
    out.mkdir(parents=True, exist_ok=True)
    for i, url in enumerate(urls, 1):
        slug = url.rstrip("/").rsplit("/", 1)[-1]
        f = out / f"{slug}.md"
        if f.exists():
            continue
        err = None
        for attempt in range(3):
            try:
                title, desc, related, md, videos = extract(get(url))
            except Exception as e:
                md, err = "", e
            # server sometimes returns the shell without the article body; retry
            if len(md) > 400:
                break
            time.sleep(3)
        else:
            print(f"FAIL {url}: {err if not md else 'empty body'}")
            continue
        related = [r for r in related if r != slug]
        f.write_text(f'---\ntitle: "{title}"\nsource: {url}\ndescription: "{desc}"\n'
                     f"related: [{', '.join(related)}]\nvideos: [{', '.join(videos)}]\n---\n\n# {title}\n\n{md}\n")
        print(f"[{i}/{len(urls)}] {slug}")
        time.sleep(1)
    # index: one line per page, cheap for an agent to scan
    lines = []
    for f in sorted(out.glob("*.md")):
        if f.name == "INDEX.md":
            continue
        t = re.search(r'^title: "(.*)"', f.read_text(), re.M).group(1)
        d = re.search(r'^description: "(.*)"', f.read_text(), re.M).group(1)
        lines.append(f"- [{t}]({f.name}) — {d}")
    (out / "INDEX.md").write_text(f"# LeanCode {section} ({len(lines)})\n\n" + "\n".join(lines) + "\n")


if __name__ == "__main__":
    main(sys.argv[1])
