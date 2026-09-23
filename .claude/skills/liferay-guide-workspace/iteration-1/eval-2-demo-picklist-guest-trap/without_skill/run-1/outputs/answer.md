I tested it on your local Liferay (localhost:8080). The outcome the page describes is real: a public select that fills itself from the picklist API ends up empty for an anonymous visitor. The explanation the page gives is only partly right, and I could not finish one test or one cleanup step (details below).

## What I did

1. **Created a throwaway picklist** as test@liferay.com: `ZZDEMO_GUEST_PICKLIST` (id 35976) with the entries `red` and `blue`. The admin account got **200** from `GET …/list-type-definitions/by-external-reference-code/ZZDEMO_GUEST_PICKLIST/list-type-entries`.

2. **Sent the same requests with no login (Guest), default setup:**

   | Request | Guest result |
   |---|---|
   | `…/by-external-reference-code/ZZDEMO_GUEST_PICKLIST/list-type-entries` | **403** `<Forbidden/>` |
   | `…/list-type-definitions/by-external-reference-code/ZZDEMO_GUEST_PICKLIST` | **403** |
   | `…/list-type-definitions` (list all) | **403** |

   So "Guest gets 403" is true on a stock instance.

3. **Why it's 403:** I listed the instance's Service Access Policies. Every policy that applies to logged-out users (ASSET_*, CAPTCHA, OBJECT_DEFAULT, SYSTEM_DEFAULT, COMMERCE_DEFAULT, …) leaves out the `headless-admin-list-type` resource classes. That 403 comes from the **Service Access Policy check (gate 1)**. Liferay turns the request away before it looks at any permission.

4. **Opened that gate for a test:** I added a temporary default Service Access Policy, `ZZDEMO_LISTTYPE_GUEST` (id 35979), that allows `ListTypeEntryResourceImpl#*` and `ListTypeDefinitionResourceImpl#get*`. Guest's results then changed:

   | Request | Guest result with the policy in place |
   |---|---|
   | `…/35976/list-type-entries` and the by-ERC entries URL | **404** `NOT_FOUND` (the same response as for a picklist that doesn't exist) |
   | `…/list-type-definitions?pageSize=50` | **200**, `items: []`, `totalCount: 0` |

   With the policy gate open, the permission check (gate 2) still hides the picklist. The failure just gets quieter: the list call returns 200 with nothing in it.

5. **Tested in a real browser as Guest:** I opened a logged-out tab of the site home page (`Liferay.ThemeDisplay.isSignedIn() === false`) and ran the kind of `fetch()` a custom form fragment would use to build a `<select>`. The select rendered with only `-- choose --` and no picklist options. Screenshot: `guest-select-empty.png`. The test policy was still active during this step, which is why the screenshot shows 404/200-empty rather than 403. Either way the visitor sees an empty dropdown.

## Verdict on the guide's wording

- **"Guest gets 403 on the list-type endpoint":** confirmed on a default instance. The cause is the Service Access Policy, not a missing permission.
- **"A company-scope VIEW grant does not lift it":** true as far as it goes. The policy check comes before any permission, so a VIEW grant on its own changes nothing. Once you add a policy, the response changes to 404, or 200 with an empty list. I **could not** test whether policy **plus** a Guest VIEW grant on `com.liferay.list.type.model.ListTypeDefinition` would return the options. My permission settings blocked granting Guest a permission, so that part of the claim is still unproven. The guide says "regardless of grants", which suggests no grant would help; I haven't shown that.
- **"Public forms end up with empty selects":** confirmed only for forms whose JavaScript fetches the picklist. I didn't build a native Form Container page with the `select-from-list` input. That input's options may come from the server rather than a fetch, and it may work fine for Guest. The guide's own advice (put the options in the fragment markup) sidesteps the problem either way.

## Cleanup (one item needs you)

- Picklist `ZZDEMO_GUEST_PICKLIST` (id 35976): **deleted** (DELETE returned 204, a later GET returned 404).
- My logged-out Chrome tab (page 20): **closed**. I didn't touch any of your other tabs.
- Service Access Policy `ZZDEMO_LISTTYPE_GUEST` (id 35979): **not deleted.** My permission settings blocked the delete call. It is a *default* policy, so anonymous users can currently reach the picklist API. The permission check still hides picklists from them (404 or an empty list), so nothing leaks, but you should remove it: **Control Panel → Security → Service Access Policy → ZZDEMO_LISTTYPE_GUEST → Delete**. Until then this instance won't reproduce the stock 403 behaviour.
