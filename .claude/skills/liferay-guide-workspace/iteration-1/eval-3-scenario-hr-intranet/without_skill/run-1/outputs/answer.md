# Badael HR intranet: which Liferay components to use for each part

Short version: the leave side is **data**, so it goes in **Objects**, with a Form Container, a Kaleo workflow and an Aggregation field. The vacancies side is **editorial content** that HR writes, so it goes in **Web Content** with a structure, a collection and a display page template. They are separate halves. What joins them is a shared idea of "Department" and one site initializer that builds both.

(Sources: the Liferay Component Guide pages `decision-guide`, `objects`, `forms`, `workflow`, `collections`, `permissions`, `web-content`, `content-structures`, `client-extensions`.)

---

## 1. At a glance

| Part | Component | Why |
|---|---|---|
| Leave request record | **Object** `LeaveRequest` (company scope) | The decision guide lists leave requests as its example of an Object. The records have typed fields, a status, validation, and they need to be summed |
| Leave type | **Picklist** `LEAVE_TYPE` (Annual, Sick, Unpaid…) | Admins can edit the list without a deploy |
| Department | **Object** `Department` + a oneToMany relationship `Department → LeaveRequests` | You need a relationship for a per-department SUM. A plain picklist can't be aggregated |
| Submit form | **Form Container** fragment bound to `LeaveRequest` | The strategic form path. The Forms app (DDM) has been in maintenance mode since 2024.Q4, and Kaleo Forms is deprecated |
| Manager approves/rejects | **Kaleo workflow** attached to the `LeaveRequest` object | Handles approval with a person in the loop, and puts tasks in "My Workflow Tasks" |
| Notifications | Workflow XML notifications, plus optionally an object action with a notification template | See section 3 |
| HR totals per department | **Aggregation field** (SUM of `days`) on `Department`, shown in a **Collection Display** | Liferay computes it on the server. No browser-side counting |
| Open vacancies (public) | **Web Content** + **Content Structure** `Vacancy` + dynamic **Collection** + **Display Page Template** | Staff write it, it's mostly prose, and HR needs to preview it, schedule it, set an expiry and restore old versions |

---

## 2. Leave requests: the data model (Objects)

**Object `LeaveRequest`** (company-scoped, so HR data survives site redeploys):

| Field | businessType | Notes |
|---|---|---|
| `requestNumber` | AutoIncrement | Gives "LR-00042" style IDs (prefix setting) |
| `leaveType` | Picklist → `LEAVE_TYPE` | |
| `startDate`, `endDate` | Date | |
| `days` | Integer (or Decimal for half days) | Must be numeric so it can be summed |
| relationship to `Department` | oneToMany from Department | Creates the FK `r_departmentLeaveRequests_c_departmentId` on LeaveRequest |
| (requester) | the entry's creator | No extra field needed. The Owner role gives the requester access to their own entries |

**Validation** (Expression Builder, works on SaaS): `endDate >= startDate`, `days > 0`. Validations can reject a save. Object actions can't, because they run after the commit.

**Naming traps:**
- **Do not** call any field `status`. It is reserved (so are `userId`, `userName` and others), and in a site initializer a reserved name rolls back the whole site.
- If you add a state picklist, give it a `defaultValue`, or it causes the same silent rollback.
- Settle the object name before you publish, because the name fixes the REST path `/o/c/leaverequests` and the table name.

**Object `Department`:**
- Fields: `name`, plus one Aggregation field `totalLeaveDays` (SUM over the relationship, field `days`).
- Seed the departments with a `batch` client extension or with `object-entries/` in the initializer (the guide has a `C_Department` batch example).
- Use `deletionType: prevent` on the relationship. Leave requests are valuable records, so a department that still has them can't be deleted.

---

## 3. Submission and approval

### Submit page (intranet, signed-in users)
A content page with a **Form Container** bound to `[$OBJECT_DEFINITION_CLASS_NAME:LeaveRequest$]`:
- `INPUTS-select-from-list` for `ObjectField_leaveType`
- `INPUTS-select-from-list` for the department relationship field. It gives the user a picker over Department entries.
- `INPUTS-date-input` ×2, `INPUTS-numeric-input` for `days`, `INPUTS-submit-button`

**Permissions:**
- Grant `ADD_OBJECT_ENTRY` on `com.liferay.object#[$OBJECT_DEFINITION_ID:LeaveRequest$]` to **Site Member** (or User). Do not grant it to Guest.
- Grant **VIEW** broadly to no one. New objects have no default grants, so each requester sees only their own entries (Owner). Give an HR regular role VIEW at company scope (`"scope": "1"`).
- Everyone who needs to read Department entries also needs VIEW on `Department`. This matters more because Aggregation values **ignore entry-level permissions**.

### Approval (Kaleo workflow)
Attach a workflow definition to the LeaveRequest object (Process Builder → Configuration). New submissions then arrive as **pending** instead of approved. Use the out-of-the-box **Single Approver** as your template: review task, approve goes to approved, reject goes to an update task sent back to the author (`<user/>`).

**The hard part is routing each request to the requester's own manager:**
- **Role assignment** (for example a site role "Line Manager"): no scripting needed. But every holder of the role sees every task, so it's too broad unless you only have a few managers.
- **Scripted assignment** (`<scripted-assignment>`, "the requester's manager"): the guide names this as the natural fit. But it's **Groovy**, which has been **disabled by default since 2024.Q3** and isn't available on SaaS at all. Turning it on is a portal-wide decision. Make that call explicitly and early.
- **Scriptless alternatives** from the guide: resource-action assignments (`UPDATE` on the item), separate definitions per case, or a **`workflowAction` CET** that decides and advances the task.

Pick one of these in the first sprint. Every later step depends on it.

**Check before go-live:** every assigned role must have at least one real user in scope. Otherwise requests sit pending forever and no error appears anywhere.

### Messages
- "You have a leave request to review" and "your request was rejected, please update" go in the **workflow XML** `<notification>` (`${userName}`, `<assignees/>`, the creator).
- "Your leave is approved" is a message about the data. It can go in an `onAfterUpdate` **object action** with a **notification template** (`[%LEAVEREQUEST_…%]` terms), always with a `conditionExpression` so it doesn't fire on every update.
- To send approved leave to an external HR or payroll system, use an `objectAction` CET on `onAfterUpdate` with a status condition. The guide gives exactly this example.

**Status caveat:**
- The workflow's system status (pending, approved, denied) and any state picklist you add (for example `leaveStatus`) are **independent** of each other.
- If HR totals must count **approved days only**, you need something the Aggregation can filter on. In practice that means a `leaveStatus` picklist kept in sync on approval: either the reviewer sets it, or a `workflowAction` CET updates it.
- Check the Aggregation field's filter options on your bundle. The guide doesn't document them.

---

## 4. HR "leave days per department" page

- The `Department.totalLeaveDays` Aggregation (SUM of `days`) is computed on the server, so the number is right whoever views it. Don't total leave days in browser JavaScript.
- Page: a **Collection Display** using the built-in **Department** object collection provider. The per-item fragment maps `ObjectField_name` and `ObjectField_totalLeaveDays` with `contextSource: "CollectionItem"`.
- **Restrict the page** to the HR role (page VIEW), and restrict VIEW on `Department` entries. Since aggregations ignore entry permissions, the page permission is what protects these numbers.

**Limitations:**
- Aggregations aren't indexed, so you can't sort or filter the list by the total.
- The value comes back as a string, so parse it before doing any arithmetic.
- An Aggregation has no time dimension. "Days used **this year**" or "by leave type" needs something else. Either use **Object Views** in the LeaveRequest admin app (columns, filters; the cheapest option), or build a **`customElement` CET** (React chart) that queries `/o/c/leaverequests?filter=…` through the headless API.
- Collections only show **approved** entries. That's fine for HR, but it means a "my pending requests" list for employees won't come from a Collection Display.

---

## 5. Public "Open vacancies" page (Web Content)

The guide's tie-breakers settle this. Staff write the content, the main value is prose, and HR wants preview, scheduling and rollback. So it goes in **Web Content**, not an Object.

- **Content Structure `Vacancy`:**
  - `jobTitle`: Text, keyword-indexed
  - `jobDescription`: Rich Text
  - `requirements`: Rich Text
  - `closingDate`: Date
  - `applyLink`: Text URL for an external ATS, or *Link to Page* if the apply page is on your site, because a page link survives renames
  - Rename the builder's random field references (`Text12345678`) **before** you write templates. Changing them later silently blanks every mapping.
- **Department**: a Global **"Department" vocabulary** (categories), required and single-valued on the Vacancy structure. HR can then filter by it, and visitors can use a **Collection Filter** fragment.
- **Expiry**: use Web Content's built-in **expiration date**, so a vacancy disappears from the list when it closes without anyone deleting it.
- **Listing** `/careers`: a dynamic collection "Open Vacancies" (Web Content, structure Vacancy, sorted by publish date), rendered by a **Collection Display** with a vacancy-card fragment. Set an `emptyCollectionConfig` message ("No open positions right now").
- **Detail page**: one **Display Page Template** bound to the Vacancy structure gives every vacancy its own URL (`/careers/<slug>`). Never build a page per job by hand.
- **Optional approval**: attach Single Approver to Web Content in that site, so an HR Manager approves before a vacancy goes live. The same Kaleo engine handles the leave workflow.
- **Public access**: Web Content gives Guest VIEW on new articles by default, so nothing extra is needed. Objects are the opposite.
- If later you want to **take applications inside Liferay** instead of an external apply link, add an `Application` Object with a public Form Container:
  - Guest gets `ADD_OBJECT_ENTRY` only, and **no** company-scope VIEW. VIEW would publish every applicant.
  - Ship any picklist options inside the form markup, because Guest gets a 403 on the list-type endpoint.

Note: classic Web Content has been in maintenance mode since 2026.Q1. It is fully supported and still the right choice for Badael.

---

## 6. How the pieces fit together

```
INTRANET SITE (members only)                                  PUBLIC SITE
─────────────────────────────                                 ───────────
/leave/new ── Form Container ──▶ Object LeaveRequest            /careers ── Collection Display
                                   │  (validation rules)                     └─ dynamic collection
                                   │                                             "Open Vacancies"
                                   ▼                                                  │
                           Kaleo workflow ──▶ manager task                             ▼
                           (approve / reject,  (My Workflow Tasks)     Web Content articles
                            XML notifications)                          (structure "Vacancy",
                                   │                                     Department category,
                                   ▼ approved                            expiration date)
                          object action ──▶ email / HR system CET                     │
                                   │                                                  ▼
                   Department ◀── oneToMany ──┘                      /careers/<slug> Display
                   totalLeaveDays = SUM(days)                        Page Template
                                   │
/hr/leave-by-department ── Collection Display (HR role only)
```

- **Department appears twice.** It's an Object for the leave data, because the relationship and aggregation need one, and a vocabulary for the vacancies, because web content filters on categories. That's acceptable. Keep the names and ERCs matching (for example `dept-hr`), or enable categorization on the object if you want one taxonomy across both.
- **Make it reproducible from source.** Put everything in one site initializer (or sibling CET projects):
  - `object-definitions/` + picklists
  - `resource-permissions.json` (use `"scope": "1"`; `"3"` grants nothing to existing entries)
  - the workflow XML in source control
  - `ddm-structures/Vacancy.xml` + templates
  - taxonomy vocabularies
  - pages, collections (`asset-list-entries.json`) and display page templates

  Real leave data is never kept in source.
- **No custom code is required** except in two places: routing to the requester's own manager if Groovy stays disabled, and any chart or external HR integration. Both are client extensions, not OSGi modules.

---

## 7. Traps to test for specifically

1. **Test as a real employee, manager and Guest, not as admin or the author.** Owner permissions make your own entries visible, so testing as yourself proves nothing.
2. **A pending entry is not a missing entry.** Once the workflow is attached, a POST creates `pending` entries, and collections hide them until someone approves.
3. **An `onAfterUpdate` action without a `conditionExpression` can loop** if it updates the same entry.
4. **Relationship FK key names:** the key is named for the parent and lives on the child. A wrong key is ignored and returns 200 with FK = 0, which leaves the leave request orphaned from its department.
5. **`paginationType` is case-sensitive** (`Numeric`, not `numeric`) in page definitions.
6. **Page composition changes need the site deleted and redeployed.** Company-scoped Objects and their entries survive that, so iterate on pages freely.
