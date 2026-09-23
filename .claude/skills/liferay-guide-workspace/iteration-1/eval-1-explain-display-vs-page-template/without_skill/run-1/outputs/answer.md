**Use a Display Page Template.** For 40 policies that each need their own page, that's the tool. A Page Template is the wrong one here.

## The actual difference

| | Display Page Template | Page Template |
|---|---|---|
| What it templates | The **full page around one content item**, with a URL generated for each item | A **starting layout** that gets copied into a new page when an editor creates one |
| Bound to | A content type and subtype, e.g. Web Content + your "HR Policy" structure, or Document + a "Policy" document type | Nothing. It's just a layout in a page template set |
| How many pages you build | **One template.** Every item of that type automatically gets its own URL rendered through it | **One page per policy**, each created by hand from the template |
| Relationship to the pages | **Live.** Fragments are mapped to "the current item", so edit the template once and all 40 policy pages change | **Copy, not link.** Editing the template later does *not* change pages already created from it |
| Where it lives | Design → Page Templates → Display Page Templates | Design → Page Templates |

In the guide's words (`templates.html`), a Display Page Template is for when "each article/record needs its own permalink", and a Page Template is for when "editors keep rebuilding the same page shape." The decision guide says display pages give you "one template, unlimited URLs — never build these by hand."

## What goes wrong if you pick a Page Template

- **You'd build and maintain 40 pages by hand.** Every new policy means someone creates a page, and every retired policy leaves a page behind for someone to delete. The guide lists "building one page per news article by hand" as a common mistake.
- **Design changes don't carry over.** Templates are copied, not linked. If you change the layout or add a "Last reviewed" line after page 1 is built, you have to edit up to 40 pages one at a time. Over time the pages drift apart.
- **The content lives in two places.** The policy text ends up pasted into, or wired separately into, each page. Nothing ties "policy X" to "page X", so the page and the source content can fall out of sync.
- **Lists of policies are harder.** A collection's cards link to each item's display page. Hand-built pages aren't item URLs, so an automatic "All policies" index can't link to them cleanly.

(Going the other way, using a Display Page Template for a one-off page like the HR landing page, doesn't work either. There's no content item for it to render, so it has nothing to show.)

## The recommended setup for your 40 policies

1. **Store each policy as a content item.** Pick one:
   - **Structured Web Content** with an "HR Policy" Content Structure, if the policy is prose written and edited in Liferay (you get versioning, preview and scheduling).
   - **Documents & Media** with a "Policy" Document Type (owner, department, effective date), if the policy *is* a PDF. Display page templates also work for documents, bound to `FileEntry` plus optionally the document type, so each file gets a landing page instead of a bare download.
   - An **Object**, if policies need an approval status, a lifecycle or links to other records.
2. **Create one Display Page Template** bound to that type and subtype, and mark it as the default. Map its fragments to the item's fields: title, body, owner, effective date, download link.
3. **Build one normal content page** (e.g. `/policies`) with a **dynamic collection** filtered to that structure or document type, plus a category like HR. Each card links through to the policy's display page.

That gives you one template, one index page and 40 pages generated automatically. Policy 41 appears the moment it's published.

If you want HR pages to share a starting layout (landing, FAQ, contacts), a Page Template is still useful for those. The shared header and footer should go on a **Master Page Template**, because that is a live link.

Sources in the guide: `src/templates.html` (sections #display and #pagetemplate, plus the disambiguation table), `src/decision-guide.html`, `src/pages.html`, `src/documents-media.html`, `src/collections.html`.
