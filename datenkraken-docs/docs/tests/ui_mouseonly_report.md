# UI Usability Test Report (Mouse Only)

**Tester profile:** External user, not familiar with the UI beforehand.  
**Date:** YYYY-MM-DD  
**Scope:** Verify that all functions can be executed with mouse only.  

---

## Test Results

| Test ID | Scenario              | Steps (mouse only)                                   | Expected Result                                | Outcome | Notes |
|---------|-----------------------|------------------------------------------------------|------------------------------------------------|---------|-------|
| TC-01   | Expand side menu      | Click arrow to expand/collapse                       | Menu expands/collapses correctly               | ✅ | Works intuitively |
| TC-02   | Select room/overview  | Click a room or “Overview” in side menu              | Correct page is displayed                      | ✅ | No confusion, clear feedback |
| TC-03   | Select sensor         | Dropdown → Click sensor parameter                    | Graph updates to selected parameter            | ✅ | Dropdown easy to use |
| TC-04   | Select past days      | Dropdown → Choose number of past days                | Graph updates to chosen time range             | ✅ | User understood immediately |
| TC-05   | Fullscreen/Save plot  | Click fullscreen or “Save as PNG” button             | Graph fullscreen OR PNG saved                  | ✅ | PNG saved without issue |
| TC-06   | Adjust Y-axis range   | Drag min/max handles of Y-slider                     | Y-axis updates accordingly                     | ✅ | Clear interaction |
| TC-07   | Adjust X-axis range   | Drag handles of X-slider                             | X-axis updates accordingly                     | ✅ | No problem |
| TC-08   | Graph interactions    | Zoom-in / Save / Pan / Reset axes (toolbar)          | All functions work correctly                   | ✅ | All actions worked as expected |
| TC-09   | Enlarge selected zone | Drag to mark zone on graph → Release                 | Marked zone zooms in                           | ✅ | Intuitive |
| TC-10   | Open overview page    | Click “Overview”                                     | Overview page displayed                        | ✅ | Easy to find |

---

## Summary

- ✅ **All 10 test cases passed.**
- The external user (no prior knowledge of the UI) could execute all functions without assistance.  
- No issues were reported.  
- The UI is **intuitive and fully operable with mouse only**.  
