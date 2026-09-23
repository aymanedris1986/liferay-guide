## Recommendation

Leave requests are **data**, so they go in an **Object** (`LeaveRequest`) related to a **Department** object. Employees submit through a **Form Container**, a **Kaleo workflow** handles the manager's approve/reject, and the HR report is a **Collection Display over Department** that shows an **Aggregation (SUM) field** of leave days, so nothing is added up in the browser. Open vacancies are **prose that HR writes, schedules and revises**, so they are **structured Web Content** (a `Vacancy` structure). They are listed through a **dynamic collection**, and each vacancy gets its own URL from a **Display Page Template**. Everything runs on the classic 2026.Q2 stack, and all of it except the leave-request entries themselves can go in a site initializer.

| Need (from the scenario) | Use | Why (guide) | Not this, because |
|---|---|---|---|
| "employees submit leave requests (type, start/end date, days)" | [Object](objects.html) `LeaveRequest`: `leaveType` = Picklist, `startDate`/`endDate` = Date, `days` = Integer, plus an optional AutoIncrement `requestNumber` ("LV-00042") | `decision-guide.html` lists leave requests by name as the Object example. Tie-breakers 1 and 3 apply: staff submit it, and HR needs to sum typed values ([decision-guide](decision-guide.html)) | Web Content keeps its fields in generic DDM tables, so you can't aggregate or validate across fields |
| Leave "type" (annual, sick, unpaid…) | [Picklist](objects.html#picklists) `LEAVE_TYPE` | A fixed option list that HR can edit without a deploy | Options hard-coded in a fragment can't be changed by HR |
| "end after start", sane day counts | [Validation, Expression Builder](objects.html) (`endDate >= startDate`, `days > 0`) | Validations can reject a save. Actions can't, because they run after commit ([objects](objects.html), "Validation and logic") | Object action or CET: too late or too expensive for this check |
| "per department" | [Department object](objects.html#relationships) with a oneToMany `departmentLeaveRequests`, `deletionType: prevent` | Tie-breaker 4: an employee points at a department that has its own life. Leave requests are valuable records, so a department shouldn't be deletable while they exist | A picklist `department` field: an Aggregation needs a relationship to sum across, and a picklist doesn't give you one |
| The submit screen | [Form Container](forms.html) bound to `LeaveRequest`, with `INPUTS-select-from-list` for type and department, `INPUTS-date-input`, `INPUTS-numeric-input` | This is the strategic 2026.Q2 path, and the data lands in the Object ([forms](forms.html)) | The Forms application (DDM) has been in maintenance mode since 2024.Q4, and Kaleo Forms is flagged for removal |
| "their manager approves or rejects" | [Kaleo workflow](workflow.html#kaleo) attached to `LeaveRequest`. Base it on Single Approver's shape: `review` → approve / reject | A human in the loop is exactly what Kaleo is for ([workflow](workflow.html), "Pick the right mechanism") | Object action: no human step. A standalone "Approve" action + button: you would rebuild the task inbox, rejection loop and audit trail yourself |
| Telling the manager and employee | Messages about the *review* ("you have a task", "rejected"): **Kaleo notifications** in the XML. The *data* message ("your leave is approved"): an `onAfterUpdate` **notification object action** + an email [notification template](workflow.html#notifications) with a `conditionExpression` | Rule of thumb from [workflow.html#two-notifications](workflow.html#two-notifications) | Teams/SMS would need a notificationType CET, which isn't needed unless email or the bell isn't enough |
| "HR wants a page showing total leave days used per department" | [Aggregation field](objects.html#aggregation) `totalLeaveDays` (SUM of `days` over the relationship) on Department, rendered by a [Collection Display](collections.html) using the built-in Department collection provider | Computed server-side and independent of entry-level permissions, so it's correct for whoever views it ([objects](objects.html) Traps; [collections](collections.html) Traps) | Fetching `/o/c/leaverequests` and adding up in JS: the total depends on the viewer's VIEW grants and silently goes wrong. A Custom Element CET dashboard costs more than the need justifies (cost ladder) |
| "public 'Open vacancies' page that HR writes and updates themselves (job description, requirements, apply link)" | Structured [Web Content](web-content.html) + [Content Structure](content-structures.html) `Vacancy`: title, department (or a category), description (rich text), requirements (rich text), apply link (link/text field) | Tie-breakers 1–2: staff write it, and HR will want to preview, schedule, set an **expiration date** so a vacancy closes itself, and roll back. The main value is prose (tie-breaker 5) | Object: no compare/restore versions, no display/expiration dates, no translation UI on classic 2026.Q2 |
| The vacancies list + one page per job | [Dynamic collection](collections.html) filtered to the `Vacancy` structure → Collection Display with a vacancy card fragment, linking to a [Display Page Template](templates.html#display) bound to the structure | The canonical index + detail pattern ([collections](collections.html)): one template, unlimited URLs | Hand-built page per vacancy: "never build these by hand" |
| Filtering vacancies by department | [Categories](taxonomy.html) vocabulary "Department" + a Collection Filter fragment | Categories cut across types and HR can manage them | A structure field filter works only inside that one structure and gives visitors no filter UI |
| Shared header/footer on intranet and public pages | [Master Page Template](templates.html#master) with a DropZone | One frame, every page | Copying header/footer fragments into every page |
| Who sees what | [Roles & permissions](permissions.html): see "Who sees it" below | Object entries are private by default; web content is Guest-VIEW by default | — |

**Who sees it** ([permissions.html](permissions.html))

- **LeaveRequest**: grant `ADD_OBJECT_ENTRY` on `com.liferay.object#[$OBJECT_DEFINITION_ID:LeaveRequest$]` to *Site Member* (the intranet staff, not Guest). **Don't** grant VIEW broadly. The Owner role already lets each employee see their own requests. Give a regular **HR** role VIEW on `[$OBJECT_DEFINITION_CLASS_NAME:LeaveRequest$]` at `"scope": "1"`. This is the first of the guide's three routes for "only the requester and their manager can see this" (permissions.html, "Per-entry permissions").
- **Department**: VIEW for HR (and Site Member if everyone may see department names in the form's picker, which the select-from-list input needs anyway).
- **Intranet pages** (Request leave, My requests, HR report): public page set, with page VIEW removed from Guest and given to Site Member (HR report page: HR role only). **Don't use private pages.** `private: true` is deprecated since 2024.Q4 and off on new installs ([pages.html](pages.html)).
- **Vacancies**: public pages with Guest VIEW. Web content gives Guest VIEW on new articles by default, so this works without extra grants, as long as the folder is viewable too.

## How it wires together

```
LEAVE (intranet, Site Members)
  Picklist LEAVE_TYPE ─┐
  Department (Object) ─┼─oneToMany─▶ LeaveRequest (Object, company scope)
     └─ totalLeaveDays   │               ▲  validations: endDate >= startDate, days > 0
        (Aggregation SUM │               │
         of days)        │   "Request leave" page ─ Form Container ─ inputs ─ submit
                         │               │  POST → status PENDING
                         │               ▼
                         │   Kaleo "Leave Approval" ─ review task → manager
                         │        approve ─▶ approved      reject ─▶ back to employee
                         │        (Kaleo notifications: task assigned / rejected)
                         │               │ onAfterUpdate, condition leaveStatus == "approved"
                         │               ▼
                         │   notification action → email template "Your leave is approved"
                         ▼
  "HR report" page ─ Collection Display (provider: Department) ─ card: name + totalLeaveDays

VACANCIES (public, Guest)
  Structure "Vacancy" ─▶ articles written by HR (workflow optional, expiration dates)
     ─▶ dynamic collection "Open vacancies" ─▶ Collection Display + filter by Department category
     ─▶ each card links to ─▶ Display Page Template "Vacancy" (/…/senior-accountant)

All pages sit on one Master Page (header, nav, footer, DropZone).

REPEATABLE: site initializer
  list-type-definitions/, object-definitions/, object-relationships/, object-fields/, object-actions/,
  notification-templates/, workflow-definitions/, roles.json, resource-permissions.json,
  ddm-structures/ (Vacancy), ddm-templates/, taxonomy-vocabularies/, display-page-templates/,
  master-pages/, fragments/, layouts/
  NOT in source: leave-request entries (runtime data), and real vacancy articles
  (HR owns them; see traps)
```

Nothing above needs custom code until the manager-routing question below. Everything up to it is on the no-deploy rungs of the [cost ladder](decision-guide.html).

## Traps for this scenario

- **"Their manager" is a scripted assignment, and scripting is off by default.** Kaleo's "the requester's manager" assignment is `<scripted-assignment>` (Groovy), disabled since 2024.Q3 and unavailable on SaaS. The guide's scriptless options are role assignments, resource-action assignments, separate definitions per case, or a `workflowAction` CET ([workflow.html#kaleo](workflow.html#kaleo)). Turning scripting on is a portal-wide decision; raise it with the team, don't flip it quietly ([workflow.html#groovy](workflow.html#groovy)).
- **Nobody holds the assigned role → requests pend forever.** After deploying the definition, check that every role it assigns to has a real member in the right scope ([workflow.html](workflow.html) Traps).
- **The workflow status is not your state field.** Kaleo owns the system `status` (pending/approved/denied). If you add a business picklist (`leaveStatus`), it's independent, and the approval email's `conditionExpression` has to test something the approval actually changes. Either the reviewer sets it or a `workflowAction` CET updates it on approval ([objects.html](objects.html) "A state field is not the workflow status"; [workflow.html](workflow.html) worked example). **Never name a field `status`**, since it's reserved, and in an initializer a reserved name rolls back the entire site.
- **"Total days used" must count approved leave only.** The Aggregation sums whatever the relationship holds, and the guide doesn't say whether an aggregation can filter by workflow status or a picklist value. *(Not in the guide: Liferay's aggregation fields do offer filters on the related object's fields; check on your bundle whether that covers workflow status or only your own `leaveStatus` field. That's another reason to keep `leaveStatus` in step.)* Also, aggregations serialize as strings and aren't indexed, so the HR list can't be sorted by the total.
- **"My requests" lists will look short.** Once the workflow is attached, a new request is created PENDING, and a collection only shows approved items. An employee's list of their own requests won't show the ones waiting for approval ([objects.html](objects.html) "Workflow changes what 'created' means"; [workflow.html](workflow.html) "Status and visibility"). Tell users that, or show pending requests some other way.
- **`onAfterUpdate` fires on every update**, including updates your own action makes. Always set a `conditionExpression` ([workflow.html](workflow.html) Traps).
- **FK naming on the child.** The relationship creates `r_departmentLeaveRequests_c_departmentId` on LeaveRequest. If anything writes it by hand with the wrong key, the value is ignored and you get an orphaned request with a 200 response ([objects.html#relationships](objects.html#relationships), [forms.html](forms.html) Traps). The select-from-list input avoids this.
- **"I can see my test request" proves nothing.** Owner lets the author see it. Test as a second employee, as HR, and as Guest on the vacancies page ([permissions.html#guest](permissions.html#guest)).
- **Grant scope.** Use `"scope": "1"` in `resource-permissions.json`. `"3"` only sets defaults for future entries and reports success anyway ([permissions.html#scope](permissions.html#scope)).
- **Don't seed real vacancies in `journal-articles/`.** Every reprovision writes a new version from source and silently overwrites what HR typed ([web-content.html](web-content.html) "In source control"). Seed a demo vacancy at most.
- **Expired vacancies vanish without an error.** That's the feature you want, but it's also the first thing to check when "a vacancy is missing" ([web-content.html](web-content.html) Traps). Also, an article created as Basic Web Content won't show up in the Vacancy-filtered collection, and its structure can't be changed afterwards.
- **Page changes need a reprovision** of initializer-owned pages, and a re-run can wipe editor changes on those pages. Keep HR editing *articles*, not the vacancies page layout ([pages.html](pages.html) Traps).

## Open questions

1. **Who exactly is "their manager"?** This is the one that changes the design:
   - *One approver role per department is acceptable* (for example, a "Leave Approver" role whose holders pick up any request) → a plain role assignment in Kaleo, no code.
   - *It must be each employee's own line manager* → either enable scripting (a portal-wide call; not on SaaS) or a `workflowAction` CET / resource-action assignment. With a resource-action assignment, something (for example an `onAfterAdd` objectAction CET) grants UPDATE on each new entry to that requester's manager. *(The per-entry grant route is my inference from the guide's building blocks, not a recipe the guide gives.)* Also check where the manager relationship lives today (Liferay users/organizations, or an HR system).
2. **Are departments already Liferay Organizations?** If so, relating LeaveRequest to the Organization system object may beat a custom Department object. Note that relationships to system objects only show up over the headless APIs, not in their admin UI ([objects.html#system-objects](objects.html#system-objects)).
3. **Is "days" entered by the employee or calculated?** The guide's Formula field covers arithmetic over *numeric* fields only, so a date-difference calculation isn't a documented no-code option. Keep it as an entered Integer with a validation, unless working days/holidays need a `objectValidationRule` CET.
4. **Do vacancies need HR approval before going public, or translation (Arabic/English)?** Either one confirms Web Content (Kaleo on the Vacancy folder, the translation UI). If instead "apply" should become an in-Liferay application form, add a `JobApplication` Object with a public Form Container (Guest ADD only, never company-scope VIEW; see [forms.html](forms.html) "Public forms").
5. **Does anything need to leave Liferay** (payroll/HR system on approval)? That's the point where an `objectAction` CET earns its cost ([client-extensions.html#microservice](client-extensions.html#microservice)).

Next step: I can build a Demo version of this in your local Liferay (Demo Department, Demo LeaveRequest + form + workflow, Demo HR report, and a Demo Vacancy structure with a display page). I'd confirm the list with you before creating anything.
