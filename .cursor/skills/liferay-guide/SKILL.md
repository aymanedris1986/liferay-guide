---
name: liferay-guide
description: >-
  Answer questions about the Liferay Component Guide (this repo's src/*.html
  pages, DXP 2026.Q2) and put it into practice. Use it to explain a page,
  section or subsection (objects, picklists, collections, fragments, display
  page templates, master pages, style books, client extensions, site
  initializers, permissions/Guest access, workflow, headless APIs and more),
  to build a worked example of a section live in the local Liferay at
  localhost:8080 by driving Chrome DevTools MCP, and to turn a business
  scenario ("we need leave requests with approval", "a news section editors
  manage", "a public form") into a recommendation of which Liferay components
  to use and how they wire together. Use it whenever the user mentions the
  guide, a Liferay component or concept, asks "what should I use for…",
  "show me / demo / build an example of…", or describes a Liferay feature they
  need to build, even if they don't mention the guide by name.
---

# liferay-guide

This repo is a hand-written guide to Liferay DXP **2026.Q2** (classic CMS by default). The pages are in `src/<slug>.html`, and `build.sh` wraps them in the shared shell. Each page has the same shape: what it is, when to use it, when not to, how it connects, and the traps. Trap notes cover failures that happen *silently* (200 OK, wrong result). They are the guide's most valuable content, so bring the relevant ones into every answer.

The user asks for one of three things. Often it's a mix, for example a scenario followed by "now build it".

1. **Explain**: a page, section or subsection.
2. **Demonstrate**: an example, ideally built live in Liferay through Chrome.
3. **Advise**: a scenario → which components cover it.

`<skill-dir>` is the directory this `SKILL.md` lives in (`.cursor/skills/liferay-guide`).

## Finding content: use the script, not raw HTML

`scripts/guide.py` reads `src/` and prints clean text with link targets kept as `[page#anchor]`:

```bash
python <skill-dir>/scripts/guide.py toc               # all pages + sections + anchors
python <skill-dir>/scripts/guide.py toc objects       # one page
python <skill-dir>/scripts/guide.py show objects#picklists
python <skill-dir>/scripts/guide.py show fragments "Traps"
python <skill-dir>/scripts/guide.py search guest 403  # sections containing all terms
```

Start with `toc` or `search` when you don't know where something lives. Then `show` the section, and **also `show` the page's "Traps" and "How it connects" sections**, because that is where the non-obvious answer usually is. Follow `[page#anchor]` links when the answer depends on them. For example, a fragment question that touches fetching data leads to `permissions#guest`.

## Sources: guide first, extras flagged

Answer from the guide and cite it as `page.html#anchor` (for example `objects.html#picklists`) so the user can jump there. If you add something the guide doesn't say, whether from Liferay docs, context7 or your own knowledge, label it inline as *(not in the guide)*. The guide makes version-specific claims that differ from generic Liferay docs, such as feature flags, ERC vs numeric IDs, and classic vs new CMS. When they conflict, go with the guide for this workspace and mention the conflict. If the guide doesn't cover a topic at all, say so plainly before going further.

If you notice the guide contradicting itself or containing a broken snippet, mention it in one line. Don't fix the docs unless asked.

## Mode 1: Explain a section

Shape the answer like this:

- **In short:** one or two sentences in plain language.
- **What it is / how it works:** the guide's substance, condensed. Keep its code/JSON snippets when they carry the meaning.
- **Use it when / don't use it when:** only if the section has this.
- **Traps:** the ones from this page (and linked pages) that apply to the question.
- **Connects to:** 2–4 links onward.
- End with a one-line offer: *"Want me to build this in your local Liferay so you can see it?"* That offer is the bridge to Mode 2 and is what makes the skill more than a reader.

Answer the question asked. If they ask about a subsection, don't summarise the whole page.

## Mode 2: Demonstrate: build it live in Liferay

"Example" or "demo" means **showing the section working in the real product**, not re-opening the guide in a browser. Drive **Chrome DevTools MCP** (`user-chrome-devtools`: `new_page`, `list_pages`, `navigate_page`, `take_snapshot`, `click`, `fill`, `fill_form`, `evaluate_script`, `take_screenshot`, `close_page`) to create the thing in the local DXP, place it where it shows up, and prove the behaviour the section describes. That includes the trap, when the section is about one. A trap you watched happen is worth more than a paragraph about it.

Do **not** use `cursor-ide-browser` for these demos: it is a different cookie jar, has no isolated Guest context, and is not the user's Chrome (where Liferay and unrelated tabs already live).

Read [liferay-demo.md](liferay-demo.md) before you touch Chrome. It has the environment facts, verified admin URLs, the in-page API recipe, and the safety rules. The short version:

1. **Plan in chat first.** List what you will create, all prefixed `Demo`, and what the user will see at the end. **Ask before creating anything**; reading needs no permission.
2. **Open your own tab** with `new_page`. Never navigate, reload or close tabs you didn't open. The user has unrelated work open in that browser.
3. **Build through the admin UI** when the point is to show *how an editor or admin does it*: navigate, `take_snapshot`, `click`, `fill`. Use in-page `fetch` against the headless APIs for tedious setup, or when the section itself is about the API. Say which you're doing.
4. **Show the result:** take a screenshot at each milestone (saved under `.cursor/skills/liferay-guide-workspace/`), then look at the rendered page. For anything public, **verify as Guest** in an isolated context, because signed-in admin views hide exactly the traps the guide warns about.
5. **Report:** what you built (with IDs/URLs), what it proves, and which guide section it illustrates. Then offer cleanup and do it when asked (see the reference for deletion order).

If Chrome MCP or the instance isn't available, fall back to a written example: the exact UI click-path or the `curl`/JSON payloads. Say that it wasn't executed.

## Mode 3: Advise: scenario → components

The guide's backbone is **data → shape → placement** (`index.html`), plus the cross-cutting concerns of permissions, APIs and repeatability. Decompose the scenario along those lines:

1. **Store:** where does each kind of data live? Use `decision-guide` "I need to store some data" and the **Web Content vs Object tie-breakers** (ask them in order; the first "yes" wins).
2. **Show:** how does it reach a page? Collections, display page templates, fragments, master pages (`decision-guide` "I need to show it on a page", `templates`).
3. **Logic:** validation, actions, approvals, notifications (`workflow`, `objects` "Validation and logic", `client-extensions`). Apply the **cost ladder**: recommend the cheapest rung that satisfies the need, and say why the pricier option isn't needed.
4. **Who sees it:** roles, Guest access, per-entry permissions (`permissions`).
5. **Repeatable:** what goes in the site initializer, and what stays a manual step (`decision-guide` "repeatable", `site-initializers`).

Output format:

```
## Recommendation
<2-3 sentences: the stack in plain words>

| Need (from the scenario) | Use | Why (guide) | Not this, because |
|---|---|---|---|
| ... | [Object](objects.html) | ... | Web Content: ... |

## How it wires together
<small ASCII chain, e.g. Object → Dynamic collection → Collection Display fragment → Content page (on Master)>

## Traps for this scenario
<only the ones that actually bite this design, each with its guide link>

## Open questions
<the facts that would change the recommendation, e.g. "Is it submitted by visitors?">

Next step: I can build a Demo version of this in your local Liferay.
```

Tie every row to the scenario's words. Only raise a question when the answer changes the recommendation. If a tie-breaker is genuinely undecided, show both branches briefly.

## Things to keep straight (the guide stresses these)

- "Template", "Collection" and "Structure" each mean several unrelated things. Name which one you mean (`templates`, `collections`, `index` "Three vocabularies").
- Classic CMS is the default on 2026.Q2. The new object-based CMS sits behind the `CMS` flag (LPD-17564). Don't mix the two for one content type.
- The admin's view hides permission problems. "Works for me" isn't verification; Guest is (`permissions#guest`).
- Editing a fragment in the library doesn't update pages that already use it.
