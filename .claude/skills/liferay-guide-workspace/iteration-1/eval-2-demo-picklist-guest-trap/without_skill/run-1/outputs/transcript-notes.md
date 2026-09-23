# Transcript notes

## Guide reading (read-only, no modifications)
- Grep `picklist` in D:\C81\Badael\liferay-guide\src
- Read src/objects.html lines 76-95 (Guest picklist trap callout)
- Grep `id="guest"` in src/permissions.html (SAP gate 1 / VIEW gate 2)
- Read src/forms.html lines 125-136 (empty select trap)

## Liferay calls (Bash/curl)
1. GET / -> 200; GET list-type-definitions (admin); GET openapi.json (list-type paths)
2. **CREATED** picklist `ZZDEMO_GUEST_PICKLIST`, id **35976**, entries red / blue (ERCs ZZDEMO_RED, ZZDEMO_BLUE) via POST /o/headless-admin-list-type/v1.0/list-type-definitions
3. Admin GET by-ERC entries -> 200; Guest GET by-ERC entries / by-ERC definition / definitions list -> all 403 `<Forbidden/>`
4. Guest GET entries with Accept JSON -> 403 `{ }`; admin GET /list-type-definitions/35976/permissions -> 404 (no such endpoint)
5. GET /api/jsonws/company/get-companies (companyId 14298310999685); GET sap.sapentry/get-company-sap-entries -> no default policy covers headless-admin-list-type
6. **CREATED** SAP entry `ZZDEMO_LISTTYPE_GUEST`, id **35979**, default=true, enabled=true, signatures `ListTypeDefinitionResourceImpl#get*`, `ListTypeEntryResourceImpl#*`
7. Guest re-test: entries -> 404, definition -> 404, list -> 200 empty; nonexistent ERC -> 404 (same as ours)
8. GET role Guest (for roleId) plus attempted add-resource-permission (Guest VIEW, company scope, ListTypeDefinition) -> **DENIED by the permission classifier; not executed**
9. Attempted sap.sapentry/delete-sap-entry 35979 -> **DENIED by the permission classifier; not executed; SAP entry still exists**
10. **DELETED** picklist 35976 -> 204; later GET -> 404

## Chrome DevTools
- ToolSearch loaded chrome-devtools schemas
- new_page http://localhost:8080/ isolatedContext `zzdemo-guest` -> **pageId 20** (only page touched; pages 11,12,14-18 are the user's and were not touched)
- evaluate_script on page 20: Guest fetch of the picklist endpoints and an injected demo select (optionCount 1, placeholder only)
- take_screenshot page 20 -> outputs/guest-select-empty.png
- close_page 20

## Items still left behind
- SAP entry ZZDEMO_LISTTYPE_GUEST (id 35979): the user must delete it manually
