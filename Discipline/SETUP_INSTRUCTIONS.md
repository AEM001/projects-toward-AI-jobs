# Discipline Project Setup Instructions

To fully enable the Widget and Deep Linking features, please perform the following steps in Xcode:

## 1. Add Widget Extension
1. Go to **File > New > Target...**
2. Select **Widget Extension**.
3. Name it `DisciplineWidget`.
4. Make sure "Include Configuration Intent" is **unchecked** (we are using AppIntent, but manually implemented).

## 2. Share Files with Widget Target
Ensure the following files are members of **both** the main App target (`Discipline`) and the Widget Extension target (`DisciplineWidget`):
- `DisciplineTask.swift` (The Data Model)
- `DisciplineWidget.swift` (The Widget Code)
- `ToggleTaskIntent.swift` (The Interactivity Intent)

*Select the file in the Project Navigator, then check the boxes in the "Target Membership" panel on the right.*

## 3. Configure App Groups (Required for Data Sharing)
For the Widget to see the same data as the App, you must enable App Groups.
1. Select the **Discipline** target -> **Signing & Capabilities** -> **+ Capability** -> **App Groups**.
2. Add/select the group: `group.albert.Discipline.share`.
3. Select the **DisciplineWidgetExtension** target -> **Signing & Capabilities** -> **+ Capability** -> **App Groups**.
4. Select the *same* group: `group.albert.Discipline.share`.

**Note:** The code has already been configured to use `group.albert.Discipline.share` for data sharing between the app and widget.

## 4. Register URL Scheme (For Deep Linking)
To support opening the app from the widget:
1. Select the **Discipline** target -> **Info** tab.
2. Expand **URL Types**.
3. Click **+** to add a new URL Type.
4. Set **URL Schemes** to `discipline`.
5. (Optional) Set **Identifier** to your bundle ID.

Now, clicking the "+" on the widget will open `discipline://add` and focus the input field.
