#!/usr/bin/env python3
"""Navigate the Liferay Component Guide (src/*.html) as plain text.

  python guide.py toc                      # every page and its sections, with anchors
  python guide.py toc objects              # sections of one page
  python guide.py show objects#picklists   # one section as plain text (anchor or heading text)
  python guide.py show objects "Relationships"
  python guide.py show objects             # whole page
  python guide.py search picklist guest    # sections containing ALL terms, with a snippet

Run from anywhere; the guide root is found relative to this file, or pass --root.
Anchors that live on table cells (e.g. client-extensions#customelement) resolve to
the table row that holds them.
"""
import argparse
import html
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[4]  # .cursor/skills/liferay-guide/scripts/guide.py -> repo root


def read_pages(root):
	src = root / "src"
	if not src.is_dir():
		sys.exit(f"no src/ under {root}; pass --root <liferay-guide folder>")
	order = []
	build = root / "build.sh"
	if build.exists():
		order = re.findall(r'^\s*"[^|"]+\|([^|"]+)\|[^"]*"', build.read_text(encoding="utf-8"), re.M)
	files = {p.stem: p for p in src.glob("*.html")}
	slugs = [s for s in order if s in files] + sorted(set(files) - set(order))
	pages = {}
	for slug in slugs:
		raw = files[slug].read_text(encoding="utf-8")
		title = (re.search(r"<!--title: (.*?)-->", raw) or [None, slug])[1]
		pages[slug] = (title, raw)
	return pages


def to_text(fragment):
	t = re.sub(r"<(pre|div class=\"ascii\")[^>]*>", "\n```\n", fragment)
	t = re.sub(r"</pre>", "\n```\n", t)
	t = re.sub(r"<tr[^>]*>", "\n| ", t)
	t = re.sub(r"</t[dh]>", " | ", t)
	t = re.sub(r"<h([2-6])[^>]*>", lambda m: "\n\n" + "#" * int(m[1]) + " ", t)
	t = re.sub(r"<li[^>]*>", "\n- ", t)
	t = re.sub(r"<(p|br|div|h\d|table|ul|ol)[^>]*>", "\n", t)
	t = re.sub(r'<a [^>]*href="([^"#]*)(#[^"]*)?"[^>]*>(.*?)</a>',
		lambda m: f"{m[3]} [{(m[1] or '').replace('.html', '')}{m[2] or ''}]", t, flags=re.S)
	t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
	t = re.sub(r"<[^>]+>", "", t)
	t = html.unescape(t)
	t = re.sub(r"[ \t]+", " ", t)
	t = re.sub(r"\n\s*\n\s*\n+", "\n\n", t)
	return t.strip()


def sections(raw):
	"""Split a page body into (anchor, heading, html) at each <h2>."""
	parts = re.split(r"(?=<h2[\s>])", raw)
	out = [("", "(intro)", parts[0])]
	for part in parts[1:]:
		m = re.match(r'<h2(?:[^>]*id="([^"]+)")?[^>]*>(.*?)</h2>', part, re.S)
		out.append((m[1] or "", to_text(m[2]), part))
	return out


def sub_anchors(part):
	return re.findall(r'<(?:h3|td|tr|div)[^>]*id="([^"]+)"', part)


def cmd_toc(pages, only):
	for slug, (title, raw) in pages.items():
		if only and slug != only:
			continue
		print(f"{slug}.html  —  {title}")
		for anchor, heading, part in sections(raw)[1:]:
			tag = f"#{anchor}" if anchor else ""
			subs = sub_anchors(part)
			extra = f"   (anchors: {', '.join('#' + s for s in subs)})" if subs else ""
			print(f"    {heading}{'  ' + tag if tag else ''}{extra}")


def find_section(pages, slug, key):
	if slug not in pages:
		sys.exit(f"unknown page '{slug}'. Pages: {', '.join(pages)}")
	title, raw = pages[slug]
	if not key:
		return f"# {title}  ({slug}.html)\n\n" + to_text(raw)
	for anchor, heading, part in sections(raw):
		if key == anchor or key.lower() == heading.lower():
			return to_text(part)
	for anchor, heading, part in sections(raw):
		if key in sub_anchors(part):
			row = re.search(r'<tr[^>]*>(?:(?!</tr>).)*id="%s"(?:(?!</tr>).)*</tr>' % re.escape(key), part, re.S)
			block = part
			if row:
				table_start = part.rfind("<table", 0, row.start())
				header = re.search(r"<tr[^>]*>.*?</tr>", part[table_start:], re.S) if table_start >= 0 else None
				block = (header[0] if header and header.start() + table_start != row.start() else "") + row[0]
			return f"(in section: {heading})\n" + to_text(block)
	for anchor, heading, part in sections(raw):
		if key.lower() in heading.lower():
			return to_text(part)
	sys.exit(f"no section '{key}' in {slug}. Try: python guide.py toc {slug}")


def cmd_search(pages, terms):
	terms = [t.lower() for t in terms]
	hits = 0
	for slug, (title, raw) in pages.items():
		for anchor, heading, part in sections(raw):
			text = to_text(part)
			low = text.lower()
			if all(t in low for t in terms):
				hits += 1
				i = low.find(terms[0])
				snip = text[max(0, i - 120): i + 200].replace("\n", " ")
				ref = f"{slug}#{anchor}" if anchor else f'{slug} "{heading}"'
				print(f"{ref}\n    …{snip}…\n")
	if not hits:
		print("no section contains all of: " + ", ".join(terms))


def main():
	ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
	sub = ap.add_subparsers(dest="cmd", required=True)
	t = sub.add_parser("toc"); t.add_argument("page", nargs="?")
	s = sub.add_parser("show"); s.add_argument("ref"); s.add_argument("section", nargs="?")
	f = sub.add_parser("search"); f.add_argument("terms", nargs="+")
	a = ap.parse_args()
	sys.stdout.reconfigure(encoding="utf-8")
	pages = read_pages(a.root)
	if a.cmd == "toc":
		cmd_toc(pages, a.page and a.page.replace(".html", ""))
	elif a.cmd == "show":
		slug, _, anchor = a.ref.replace(".html", "").partition("#")
		print(find_section(pages, slug, anchor or a.section))
	else:
		cmd_search(pages, a.terms)


if __name__ == "__main__":
	main()
