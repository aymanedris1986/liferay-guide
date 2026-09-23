# Transcript notes

## Skill / guide reads
1. Read `liferay-guide/SKILL.md`
2. Glob skill folder
3. Read `references/liferay-demo.md`
4. `guide.py search guest picklist`; `show objects#picklists`; `show objects "Traps"`
5. `guide.py show permissions#guest`; `show forms "Traps"`; `show objects "How it connects"`
6. ToolSearch: loaded chrome-devtools new_page, evaluate_script, take_screenshot, list_pages, close_page, take_snapshot, fill, click, navigate_page

## Chrome calls (pageIds)
7. `new_page` http://localhost:8080/web/guest (background) → **pageId 10** (mine; the user's tabs at the time were 1,3,4,5,6,7,8)
8. `evaluate_script` page 10: session check → signed in as test@liferay.com, siteId 20125
9. `evaluate_script` page 10: GET DEMO_STATUS by ERC (not found), then **POST create picklist** → 200
10. Bash: made the outputs dir, appended to the scratchpad ledger (`liferay-demo-ledger.md`)
11. `evaluate_script` page 10 → error: browser reconnected, page ids changed
12. `new_page` http://localhost:8080/web/guest, isolatedContext="guest-check" → **pageId 19** (mine). The list showed my earlier tab renumbered as **pageId 13** (the only localhost:8080 tab; the user had none before)
13. `evaluate_script` page 13 (admin): 3 GETs without CSRF → all 403 (confirmed signed in)
14. `evaluate_script` page 19 (Guest): 3 GETs without CSRF → all 403
15. `evaluate_script` page 13 (admin): 3 GETs with x-csrf-token → 200, 200, 200 (3 entries)
16. `evaluate_script` page 19 (Guest): 4 GETs with x-csrf-token → 403 x4, empty body
17. `evaluate_script` page 19: injected DOM-only demo form (fetch-populated select plus markup select) → fetch 403, 0 options vs 4
18. `take_screenshot` page 19 → outputs/02-guest-empty-select.png
19. `evaluate_script` page 13: injected DOM-only demo form → fetch 200, 3 options
20. `take_screenshot` page 13 → outputs/01-admin-select-populated.png
21. Read both screenshots to check them
22. `evaluate_script` page 13: removed the injected DOM, **DELETE picklist 35972** → 204; GET by ERC → 404; search "Demo" → none left
23. `list_pages` → confirmed 13 and 19 are still my localhost tabs
24. `close_page` 19; `close_page` 13

Pages touched: 10 (later renumbered 13), 19. No other tab was navigated, reloaded or closed.

## Items created / deleted
| Item | Created | Deleted |
|---|---|---|
| Picklist `Demo Status`, id 35972, ERC `DEMO_STATUS`, entries 35973 (draft), 35974 (active), 35975 (closed) | step 9, POST → 200 | step 22, DELETE → 204, verified 404 |
| DOM-only demo form overlays (not persisted) | steps 17, 19 | removed or discarded with the tabs, steps 22/24 |

No roles, permissions, settings or pages were changed.
