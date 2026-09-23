**In short:** A **Display Page Template** is *one* layout that Liferay renders for *every* item of a content type, and each item automatically gets its own URL. A **Page Template** is a starting layout that gets *copied* into a new page when someone creates it by hand. For 40 HR policies that each need their own page, use a **Display Page Template**. The guide lists "building one page per article by hand" as a common mistake.

## The difference

| | Display Page Template ([templates.html#display](templates.html#display)) | Page Template ([templates.html#pagetemplate](templates.html#pagetemplate)) |
|---|---|---|
| What it templates | "The full page around one item, with a generated URL" | "A starting layout copied into new pages" |
| Bound to | A content type + subtype (e.g. Web Content of structure *HR Policy*, or Documents of document type *Policy*) | Nothing. It's just a saved layout in a page template set |
| How many pages you get | One template, unlimited URLs. Every policy gets a page automatically | One page each time an editor clicks "Add page" and picks it |
| Content on the page | Fragments **mapped to the current item**, so the title, body and dates come from the policy itself | Whatever the editor types or drops into that particular page |
| After you edit the template | Every policy page changes, because it's one layout rendered live | **Nothing changes on existing pages.** "Copy, not link" |
| In navigation? | No. Display pages sit outside the navigation tree ([pages.html](pages.html) "Pages that are not in the navigation tree") and are reached through the item's URL | Yes. It becomes a normal content page in the tree |
| Reach for it when | "Each article/record needs its own permalink" | "Editors keep rebuilding the same page shape" |

The guide's one-line version ([templates.html](templates.html) "Which one, in one line each"): *Every item needs a URL → Display Page Template. Same starting layout for new pages → Page Template.*

## What you'd build for the 40 policies

This is the guide's "canonical index + detail pattern" ([collections.html](collections.html) "How it connects"):

```
/policies ──▶ Content page (normal page, in the menu)
   └── Collection Display ──▶ dynamic collection "HR Policies"
          └── policy-row fragment (title, department, effective date)
                 │ each row links to…
/…/<policy-url> ──▶ Display Page Template bound to the Policy type
   └── fragments mapped to the current policy
```

You still need to decide what a "policy" is stored as. The display page template binds to that type:

- **They're files (PDFs/Word) with some metadata** → a **Document Type "Policy"** (owner, department, effective date) in Documents & Media. Bind the display page template to `FileEntry` + the Policy document type. The guide describes this setup directly: a display page template "gives each file a landing page instead of a bare download", and a dynamic collection filtered by type/category builds the "Policies & Manuals" page ([documents-media.html](documents-media.html) "Listing documents").
- **They're written in Liferay as prose** → **Web Content** with an *HR Policy* structure. Bind to `JournalArticle` + that structure's key. Editors also get preview, scheduling and version rollback ([decision-guide.html](decision-guide.html) tie-breakers #2 and #5).
- **They have an approval status, review cycle or links to other records** → an **Object** with an attachment field ([documents-media.html](documents-media.html) "The common intranet question": "If there's an approval flow, a status, or a link to another record, go with an Object").

Display pages and collections work with all three. Pick the type by how the data is owned and changed, not by how it's shown.

## What goes wrong if you pick a Page Template instead

1. **You hand-build and hand-maintain 40 pages.** Each one is a copy. The guide says so plainly: "500 news articles = 1 display page template + 1 collection for the index. Not 500 hand-built pages. If anyone on the project is creating pages per record, this is the fix."
2. **Design changes don't propagate.** Editing a page template "does not change pages already created from it." A new footer note or layout tweak means 40 manual edits.
3. **Policy #41 means building another page.** Someone has to create it and link it into the index. With a display page, adding the document or article is the whole job: the URL exists and the collection lists it.
4. **The content is stuck in the page, not stored as items.** The policy text or file lives inside each page's fragments, so it can't be filtered by department or category in a collection *(the consequence is my inference; the guide doesn't state it)*.

Going the other way, a Display Page Template is the wrong tool for a one-off page like the `/policies` index or an "About HR" page. It has no URL of its own without an item, and it isn't in navigation. Those are normal content pages (built from a Page Template if editors keep recreating the same shape).

## Traps that apply here

- **Default template per type.** "Only one template per contentType+contentSubtype can be the default; that default is what an item's URL uses when no template is named in the path." Mark your Policy display page template as default (`"defaultTemplate": true` in an initializer), or policy URLs won't render through it ([templates.html#display](templates.html#display)).
- **Bind to the right subtype.** For Web Content the subtype is the *structure key*. For Documents it's the optional document type. If you use an Object, the class name is `com.liferay.object.model.ObjectDefinition#<id>` (use the `[$OBJECT_DEFINITION_CLASS_NAME:<Name>$]` token in an initializer). Plain `ObjectEntry` "matches nothing" ([templates.html#display](templates.html#display)).
- **Empty list, no error.** If staff lack VIEW on the policies, the index collection returns 200 with an empty list. That's permission gate 3 ([permissions.html](permissions.html) "The three independent gates"). Your admin view will look fine, so test as a regular site member. Grant to **Site Member**, the guide's home for "our intranet's staff" grants ([permissions.html](permissions.html) "The model in one diagram").
- **Master page vs page template.** If what you really want is a shared header/footer that updates everywhere, that's a **Master Page Template** ([templates.html#master](templates.html#master)), which is a live link. A page template won't do that.

## Connects to

- [templates.html#display](templates.html#display): binding, the initializer JSON, mapping to the current item
- [collections.html](collections.html): the `/policies` index
- [documents-media.html](documents-media.html): Document Types for policy files
- [decision-guide.html](decision-guide.html): the Web Content vs Object tie-breakers

Want me to build this in your local Liferay so you can see it? I'd set up a Demo Policy type, a Demo display page template and a Demo `/policies` index with two or three sample policies, then check them as a non-admin user.
