# UI Usability Test (Mouse Only)

This document lists all mouse-only test cases for the current UI.  
Goal: Every feature must be operable without using a keyboard.

| Test ID | Scenario              | Steps (mouse only)                                                        | Expected Result                                          | Status |
|---------|-----------------------|---------------------------------------------------------------------------|----------------------------------------------------------|--------|
| TC-01   | Expand side menu      | Click on the arrow icon to expand/collapse the side menu                  | Menu expands/collapses correctly                         | ✅ |
| TC-02   | Select room/overview  | In the side menu, click on a room or on “Overview”                        | Correct page is displayed, active item highlighted       | ✅ |
| TC-03   | Select sensor         | In a room view, open the dropdown and click a sensor parameter            | Graph updates to selected parameter                      | ✅ |
| TC-04   | Select past days      | Open the dropdown for time selection and choose number of past days       | Graph updates to chosen time range                       | ✅ |
| TC-05   | Fullscreen/Save plot  | Click fullscreen button OR “Save as PNG” button                           | Graph is shown fullscreen OR PNG is saved locally        | ✅ |
| TC-06   | Adjust Y-axis range   | Drag min/max handles of the axis range bar with the mouse                 | Y-axis range updates accordingly                         | ✅ |
| TC-07   | Adjust X-axis range   | Drag handles of the time range bar with the mouse                         | X-axis range updates accordingly                         | ✅ |
| TC-08   | Graph interactions    | Use zoom-in, save as picture, pan, reset axes (via toolbar buttons)       | Graph responds correctly to each action                  | ✅ |
| TC-09   | Enlarge selected zone | Drag to mark a zone on the graph, then release                            | Marked zone is zoomed into / enlarged view shown         | ✅ |
| TC-10   | Open overview page    | From the side menu, click “Overview”                                      | Overview page is displayed with summary data             | ✅ |
