# Building a demo in the local Liferay (Chrome DevTools MCP)

The goal is to **show a guide section working in the real product**: create the thing, place it where it appears, and demonstrate the behaviour (or the trap) the section describes. The user should be able to open the same URLs afterwards and see it.

## Contents
1. Environment
2. Safety rules
3. Starting a session
4. Driving the admin UI
5. Calling the headless APIs from the page
6. Verifying as Guest
7. Verified admin URLs
8. Demo recipes by guide section
9. Cleanup

## 1. Environment

| | |
|---|---|
| Portal | `http://localhost:8080` (DXP 2026.Q2.11, workspace `D:\C81\Badael\working\intranet\badael-intranet`) |
| Admin login | `test@liferay.com` / `test` (from the workspace README) |
| Default site | Guest: numeric id `20125`, friendly URL `/web/guest`. Discover other sites at runtime; don't assume a Badael site exists |
| Guide pages | `file:///D:/C81/Badael/liferay-guide/<slug>.html#<anchor>`, only if the user wants the doc opened next to the demo |

If `http://localhost:8080` doesn't answer, say so and fall back to a written example. Don't try to start the bundle yourself unless asked; startup takes minutes and the README describes it.

## 2. Safety rules

The browser is the user's own Chrome, with unrelated tabs open (trading charts, Figma, chats) and possibly their own Liferay session.

- **Only use tabs you opened** with `new_page`. Keep their page IDs and pass `pageId` explicitly on every call. Never `navigate_page`, reload or `close_page` any other tab. Before closing one of yours, run `list_pages` and check the ID still points at the URL you opened.
- **Ask before any write.** In one message, list what you will create and where. Reads (navigating, snapshots, GET calls) need no confirmation.
- **Name everything `Demo …`**, and give it an ERC starting with `DEMO_` where the resource has one. That makes demo items obvious to editors and safe to clean up.
- **Keep a ledger**: after each create, append a line to `<scratchpad>/liferay-demo-ledger.md` (type, name, id/ERC, URL). Cleanup uses it.
- **Never touch shared settings as a side effect**: instance settings, feature flags, existing roles and their permissions, the Guest site's existing pages, or anything not named `Demo`. If the demo *needs* one of these (for example a Guest VIEW permission to show `permissions#guest`), ask for that specifically, and record the original value so you can restore it.
- Don't sign out. It would sign the user out of their own tabs, because cookies are shared. Use an isolated context for Guest checks (§6).

## 3. Starting a session

```
new_page  url=http://localhost:8080/web/guest   → remember pageId
evaluate_script  () => ({signedIn: Liferay.ThemeDisplay.isSignedIn(),
                         user: Liferay.ThemeDisplay.getUserEmailAddress?.(),
                         siteId: Liferay.ThemeDisplay.getScopeGroupId(),
                         companyId: Liferay.ThemeDisplay.getCompanyId()})
```

If not signed in, go to `http://localhost:8080/c/portal/login` in your tab, `take_snapshot`, `fill` the email/password fields, and `click` Sign In.

## 4. Driving the admin UI

Use the UI when the lesson is "this is how an editor/admin does it":

- `navigate_page` to a URL from §7. Then `take_snapshot` to get element `uid`s, and use `click`, `fill` or `fill_form`. Take a fresh snapshot after anything that re-renders; uids from an old snapshot go stale.
- Liferay forms often save via a primary button labelled *Save*, *Publish* or *Create*. After saving, snapshot again and look for the success toast or a validation message. Don't assume it worked.
- Modals are usually in-page Clay modals. Some legacy dialogs are iframes; if the snapshot doesn't show their fields, say so and use the API route for that step.
- The **content page editor** (adding fragments to a page) is drag-heavy. Search the fragment in the left *Fragments and Widgets* panel, then use `drag` onto the drop target, or check the snapshot for a keyboard/"Add" affordance. Page-composition REST is gated by off-by-default flags on 2026.Q2 (see `headless-apis` "Feature flags"). The editor is the realistic path, so be patient with it and take a screenshot after each placement. Publish the page when done.
- `take_screenshot` at each milestone, with `filePath` in the scratchpad (for example `<scratchpad>/demo-01-object-published.png`), and mention the files in the report.

## 5. Calling the headless APIs from the page

Use this for bulk setup (seed entries), or when the section *is* about the API. It runs as the signed-in admin, with the session cookie plus the CSRF token, exactly as the guide's `headless-apis` "Authentication" table describes for browser JS:

```js
async () => {
  const api = async (method, path, body) => {
    const r = await fetch(path, {method, headers: {
      'x-csrf-token': Liferay.authToken, 'Content-Type': 'application/json', Accept: 'application/json'},
      body: body ? JSON.stringify(body) : undefined});
    const text = await r.text();
    let json; try { json = JSON.parse(text); } catch { json = text.slice(0, 500); }
    return {status: r.status, json};
  };
  // example: create a picklist
  return await api('POST', '/o/headless-admin-list-type/v1.0/list-type-definitions', {
    externalReferenceCode: 'DEMO_STATUS', name_i18n: {en_US: 'Demo Status'},
    listTypeEntries: [{key: 'draft', name_i18n: {en_US: 'Draft'}}, {key: 'active', name_i18n: {en_US: 'Active'}}]});
}
```

Pass `waitForStableDom: false` for pure API calls. Always report the status code. The guide's error table (`headless-apis` "Error codes") explains what 404 and an empty 200 *really* mean here. Use it when a call surprises you, and treat that as part of the demo. The spec for any module is at `/o/<module>/v1.0/openapi.json`, and the API Explorer is at `/o/api`.

Some keys to remember from the guide: `headless-admin-site` and `headless-admin-fragment` take the **site ERC**, while `headless-delivery`, `headless-admin-content` and `headless-admin-taxonomy` take the **numeric siteId**. An object must be **published** (`POST …/object-definitions/{id}/publish`) before `/o/c/<plural>` exists.

## 6. Verifying as Guest

A demo of anything public isn't finished until Guest has seen it:

```
new_page  url=<public page URL>  isolatedContext="guest-check"
```

The isolated context has no cookies, so it *is* an anonymous visitor. Take a snapshot or screenshot, and `evaluate_script` to check that real values are present and placeholders like `{{` are absent. For API-level checks, run `fetch` from that Guest tab without the CSRF header, and compare with the admin result. That side-by-side (admin 200 with data, Guest 403 / empty / 0) is how you show `permissions#guest`, `objects#picklists` and `objects#guest-count` in practice.

## 7. Verified admin URLs

Prefix: `http://localhost:8080/group/guest/~/control_panel/manage?p_p_id=` (use a different site's friendly URL in place of `guest` for site-scoped apps on that site).

| App | p_p_id |
|---|---|
| Objects | `com_liferay_object_web_internal_object_definitions_portlet_ObjectDefinitionsPortlet` |
| Web Content (articles, structures, templates tabs) | `com_liferay_journal_web_portlet_JournalPortlet` |
| Documents and Media | `com_liferay_document_library_web_portlet_DLAdminPortlet` |
| Fragments | `com_liferay_fragment_web_portlet_FragmentPortlet` |
| Collections | `com_liferay_asset_list_web_portlet_AssetListPortlet` |
| Page Templates (masters, display pages, page templates) | `com_liferay_layout_page_template_admin_web_portlet_LayoutPageTemplatesPortlet` |
| Pages | `com_liferay_layout_admin_web_portlet_GroupPagesPortlet` |
| Style Books | `com_liferay_style_book_web_internal_portlet_StyleBookPortlet` |
| Categories / Tags | `com_liferay_asset_categories_admin_web_portlet_AssetCategoriesAdminPortlet` / `com_liferay_asset_tags_admin_web_portlet_AssetTagsAdminPortlet` |
| Segments | `com_liferay_segments_web_internal_portlet_SegmentsPortlet` |
| Forms (Forms app) | `com_liferay_dynamic_data_mapping_form_web_portlet_DDMFormAdminPortlet` |
| Templates (widget/info templates) | `com_liferay_template_web_internal_portlet_TemplatePortlet` |
| Notification Templates | `com_liferay_notification_web_internal_portlet_NotificationTemplatesPortlet` |
| Process Builder (workflow) | `com_liferay_portal_workflow_web_portlet_ControlPanelWorkflowPortlet` |
| Roles | `com_liferay_roles_admin_web_portlet_RolesAdminPortlet` |
| Users | `com_liferay_users_admin_web_portlet_UsersAdminPortlet` |
| Sites | `com_liferay_site_admin_web_portlet_SiteAdminPortlet` |
| Client Extensions | `com_liferay_client_extension_web_internal_portlet_ClientExtensionAdminPortlet` |
| Instance Settings | `com_liferay_configuration_admin_web_portlet_InstanceSettingsPortlet` |
| Service Access Policy | `com_liferay_portal_security_service_access_policy_web_portlet_SAPPortlet` |
| OAuth 2 Administration | `com_liferay_oauth2_provider_web_internal_portlet_OAuth2AdminPortlet` |

Picklists: the ID isn't verified yet. Open the Applications menu (grid icon, top right) → Picklists, or create picklists over the API (§5). If you find the ID, add it here.

## 8. Demo recipes by guide section

These are starting points. Adapt them to what the user asked, and keep each demo to the smallest build that shows the point.

| Guide section | Build | What it proves |
|---|---|---|
| `objects` + `objects#picklists` | Picklist `Demo Status` → object `Demo Request` (text, date, picklist field) → publish → 3 entries | Object = table + REST API: show `/o/c/demorequests` returning the entries |
| `objects#relationships` | Two objects, one-to-many, entry with related record; `?nestedFields=` | Relationships are real data, which Web Content can't do |
| `objects#picklists` trap / `permissions#guest` | Call the list-type endpoint as admin and as Guest | Guest 403 on the picklist, which is why public forms render empty selects |
| `collections` (dynamic/manual) | Dynamic collection of `Demo` entries or articles → Collection Display on a `Demo` content page | "List of latest N" updates itself; add an entry and reload |
| `templates#display` | Display page template for the object/structure, mapped fields | One template, a URL per item: open two items' URLs |
| `templates#master` | Master with header/footer fragments + drop zone; a page using it | Change the master, and every page follows |
| `fragments` (editables, config, `#js`) | Custom fragment in a `Demo` fragment set with an editable and a config option; place it; edit inline | Where content enters a fragment; library edits don't update placed copies (edit, then show the old placement) |
| `web-content` + `content-structures` + `web-content-templates` | Structure `Demo News` → FreeMarker template → 2 articles → Web Content Display or collection | Structure = fields, template = look, article = data |
| `theme-design#stylebook` | Duplicate a style book as `Demo`, change the primary colour token, apply it to a demo page | Tokens restyle without deploys |
| `taxonomy` | Vocabulary `Demo Topics` + categories, tag articles, filter a collection by category | Categories cut across types |
| `workflow` / `#actions` / `#notifications` | Single Approver on the `Demo` object; submit an entry, see *Pending*, approve in My Workflow Tasks | Status lifecycle without code |
| `personalization` | Segment (for example "signed-in users"), a second experience on a `Demo` page; compare Guest vs admin | Same URL, different content |
| `headless-apis` | Live calls from §5: filter/sort/fields/nestedFields, the `actions` block, ERC vs numeric 404 | The conventions and error meanings, observed |
| `forms` | Form Container fragment mapped to the `Demo` object on a public page; submit as Guest | Entry created; check Guest needs ADD permission (ask before granting) |

For CET and site-initializer sections, a live build means a Gradle deploy from the workspace, which is outside this browser flow. Show what is already deployed (Client Extensions admin, and the pages and fragments the initializer created). Then give the source-tree example from the guide, and offer to do the real deploy as a separate step.

## 9. Cleanup

Offer cleanup at the end of every demo, and do it when the user agrees. Work through the ledger in **reverse dependency order**:

1. Pages, then display page templates, masters and page templates
2. Collections, then fragments, then fragment sets
3. Object entries, then object definitions (unpublished or deleted), then picklists
4. Articles, then templates, then structures; categories, then vocabularies
5. Restore any setting you changed, to the recorded original value

Delete only items that appear in the ledger. Then report what was removed, and anything that was left in place and why.
