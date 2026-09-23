#!/usr/bin/env bash
#
# build.sh — wrap each src/<slug>.html body in the shared shell (head, topbar, sidebar).
# Run from the repo root:  bash build.sh
#
set -o errexit
set -o nounset
set -o pipefail

# group|slug|nav label   — order here is the order in the sidebar
PAGES=(
	"Start here|index|Overview & map"
	"Start here|decision-guide|What should I use?"
	"Content|web-content|Web Content (articles)"
	"Content|content-structures|Content Structures"
	"Content|web-content-templates|Web Content Templates"
	"Content|documents-media|Documents & Media"
	"Content|taxonomy|Categories, Tags & Assets"
	"Pages & layout|pages|Pages & page types"
	"Pages & layout|fragments|Fragments"
	"Pages & layout|collections|Collections"
	"Pages & layout|templates|All template types"
	"Pages & layout|theme-design|Themes & style books"
	"Pages & layout|personalization|Segments & experiences"
	"Data & logic|objects|Objects"
	"Data & logic|forms|Forms"
	"Data & logic|workflow|Workflow & notifications"
	"Data & logic|permissions|Roles & permissions"
	"Extend & integrate|client-extensions|Client extensions"
	"Extend & integrate|widgets-modules|Widgets & OSGi modules"
	"Extend & integrate|headless-apis|Headless APIs"
	"Extend & integrate|site-initializers|Site initializers"
)

meta() {
	# meta <file> <key>  -> value from "<!--key: value-->" on any of the first 3 lines
	head -3 "$1" | sed -n "s/^<!--$2: \(.*\)-->$/\1/p" | head -1
}

nav_for() {
	local current="$1" last_group="" group slug label
	for entry in "${PAGES[@]}"; do
		IFS='|' read -r group slug label <<< "${entry}"
		if [[ "${group}" != "${last_group}" ]]; then
			[[ -n "${last_group}" ]] && printf '\t\t\t</ul>\n'
			printf '\t\t\t<h4>%s</h4>\n\t\t\t<ul>\n' "${group}"
			last_group="${group}"
		fi
		if [[ "${slug}" == "${current}" ]]; then
			printf '\t\t\t\t<li><a aria-current="page" href="%s.html">%s</a></li>\n' "${slug}" "${label}"
		else
			printf '\t\t\t\t<li><a href="%s.html">%s</a></li>\n' "${slug}" "${label}"
		fi
	done
	printf '\t\t\t</ul>\n'
}

built=0

for entry in "${PAGES[@]}"; do
	IFS='|' read -r _group slug _label <<< "${entry}"
	src="src/${slug}.html"

	if [[ ! -f "${src}" ]]; then
		printf 'MISSING %s\n' "${src}" >&2
		continue
	fi

	title=$(meta "${src}" title)
	subtitle=$(meta "${src}" subtitle)

	{
		cat <<HEAD
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${title} · Liferay Component Guide</title>
<meta name="description" content="${subtitle}">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="topbar">
	<strong><a href="index.html">Liferay Component Guide</a></strong>
	<span>DXP 2026.Q2 &middot; what each piece is, and when to reach for it</span>
</header>
<div class="shell">
	<nav class="sidebar" aria-label="Components">
HEAD
		nav_for "${slug}"
		cat <<MID
	</nav>
	<main id="main">
		<h1>${title}</h1>
		<p class="lede">${subtitle}</p>
MID
		tail -n +3 "${src}"
		cat <<FOOT
		<footer class="pagefoot">
			Part of the <a href="index.html">Liferay Component Guide</a>.
			Not sure which component fits? Start at <a href="decision-guide.html">What should I use?</a>
		</footer>
	</main>
</div>
</body>
</html>
FOOT
	} > "${slug}.html"

	built=$((built + 1))
done

printf 'built %d pages\n' "${built}"
