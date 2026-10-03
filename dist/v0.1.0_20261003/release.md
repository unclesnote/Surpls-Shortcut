# Release Notes

## v0.1.0 (20261003)

- First release: a desktop app for creating and managing GNOME application shortcuts without editing .desktop files by hand
- Browse, search, edit, and delete the shortcuts in your applications menu, with a details panel and status labels that show at a glance which ones also have a Desktop copy
- Register an app by choosing its executable and adding command-line options; the %u field code is added automatically when needed
- Run command-line tools in a terminal, and turn on --no-sandbox with a security warning plus a read-only check of your sandbox environment for Electron/Chromium apps such as AppImages
- Pick an icon from images found next to the app, from common GNOME system icons, or from any file, with live previews everywhere an icon appears
- JPG, ICO, XPM, and other non-PNG icons now preview and display correctly: they are converted to PNG and saved in an icon_cache folder beside the app
- Optionally keep a copy of the shortcut on your Desktop; it is created, updated, and removed together with the menu entry and made launchable automatically
- Safer editing: a confirmation shows exactly which launcher files will be removed (your app and icon files are never deleted), settings the app does not manage are preserved, and you are warned if a shortcut changes elsewhere while you edit it
- English and Korean interface, and the window title shows the current version
