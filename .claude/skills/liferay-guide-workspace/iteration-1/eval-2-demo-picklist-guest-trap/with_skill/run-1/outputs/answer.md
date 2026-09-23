The guide is right about the part I tested. I ran it on your local DXP (localhost:8080): Guest can't read a picklist over REST, and a public form that fetches its options ends up with an empty `<select>`. This is the trap in `objects.html#picklists` (also `forms.html` Traps and `permissions.html#guest`).

## What I built

I used in-page `fetch` against the headless API, because the trap is about the API.

- **Picklist `Demo Status`** (ERC `DEMO_STATUS`, id `35972`) with three entries: `draft`, `active`, `closed`.

## What happened

I sent the same three GETs from two tabs. One was signed in as `test@liferay.com`. The other was an isolated Guest context with no cookies, i.e. a real anonymous visitor.

| Endpoint (`/o/headless-admin-list-type/v1.0/…`) | Admin | Guest |
|---|---|---|
| `list-type-definitions/35972/list-type-entries` | **200**, 3 entries | **403**, empty body |
| `list-type-definitions/by-external-reference-code/DEMO_STATUS/list-type-entries` | **200**, 3 entries | **403**, empty body |
| `list-type-definitions/35972` | **200** | **403**, empty body |
| `list-type-definitions?pageSize=1` | n/a | **403** |

Guest sent its own `x-csrf-token` (`Liferay.authToken`), exactly as a fragment's JS would. So the 403 isn't a missing-token problem.

**The form effect.** In both tabs I added a throwaway form to the page's DOM only; nothing was saved to the portal. It fills a Status `<select>` with the usual `fetch` of the picklist entries:

- **Admin** (`01-admin-select-populated.png`): HTTP 200, 3 options (Draft / Active / Closed). It works for you.
- **Guest** (`02-guest-empty-select.png`): HTTP 403, **0 options**. The select renders blank and its value is `""`, and the visitor sees no error. Next to it, a select with the options written into the markup shows all of them to Guest.

So a visitor gets a blank dropdown, submits `""`, and if the object accepts it the entry saves looking fine. Testing while signed in never shows this.

## One detail the guide doesn't mention

*(not in the guide)* My first admin attempt left out the `x-csrf-token` header, and admin got **403** too. Session-cookie headless calls need the token even for GET. If you reproduce this with a hand-written `fetch`, add the header, or you'll "prove" the trap for admin as well.

## What I did *not* verify

The guide also says a **company-scope VIEW grant doesn't fix this**. Testing that means changing the Guest role's permissions, which is a shared setting, so I left it alone. One clue points the guide's way *(my inference, not tested)*: Guest's 403s come back with an empty body, even on the plain list endpoint. That looks like the request is stopped at the Service Access Policy gate (`permissions.html#guest`, Gate 1) before any permission is checked. If so, a VIEW grant wouldn't change anything. If you'd like, I can grant it temporarily, re-run the Guest call, and restore the original value.

## The fix the guide recommends

Ship the options in the fragment markup, and let a fetch only *refresh* them (`forms.html` Traps). The "B" select in the Guest screenshot is that pattern.

## Cleanup (done)

- Picklist `Demo Status` (35972) deleted: DELETE → 204, then GET by ERC → 404. No `Demo` picklists are left.
- The injected demo forms existed only in the browser DOM and were removed or closed with the tabs.
- I closed the two tabs I had opened. Your other tabs weren't touched.
- I changed no roles, permissions or settings.

Screenshots: `01-admin-select-populated.png`, `02-guest-empty-select.png` (in this outputs folder).
