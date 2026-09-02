# GNOME Shortcut Manager

**English** | [한국어](README_ko.md)

`gnome_shortcut_manager.sh` is an interactive Bash utility that registers executable files and user scripts as `.desktop` shortcuts in the GNOME application menu and on the desktop.

It provides English and Korean interfaces and handles executable validation, icon discovery, execute permissions, GNOME trust metadata, and application database refreshes.

## Tkinter GUI

`app.py` provides the same management workflow in a Python/Tkinter desktop window. The Bash utility remains available.

- A searchable list and details for user `.desktop` files
- A shared form for registration and editing
- Checkboxes for `--no-sandbox`, terminal execution, and the Desktop copy
- Read-only Electron/Chromium sandbox environment diagnosis without launching the app
- Asynchronous nearby-image discovery plus system and custom icon selection
- Desktop copy creation, synchronization, deletion, and Allow Launching trust metadata
- Preservation of unsupported fields in externally created `.desktop` files
- English and Korean interfaces

Install Tkinter on Ubuntu if necessary:

```bash
sudo apt install python3-tk
```

Run the GUI and unit tests:

```bash
python3 app.py
python3 -m unittest discover -v
```

See [`design.md`](design.md) for the screen and workflow design.

## Features

### English and Korean interface

- Choose `English` or `한국어` when the script starts.
- Press Enter without entering a choice to use English, the default language.
- Apply the selected language to menus, prompts, warnings, errors, and icon descriptions for the current session.
- Manage interface strings by text ID in English and Korean.

```bash
define_text \
    "app_title" \
    "GNOME Shortcut Manager" \
    "그놈 단축 아이콘 관리자"
```

The language choice is not saved. The selection screen appears each time the script starts.

### Shortcut registration

- Verify that the executable or script exists.
- Reject directories when an executable file is required.
- Offer to apply `chmod +x` when execute permission is missing.
- Accept optional execution arguments such as `--no-sandbox` separately from the executable path and automatically append `%u`.
- Suggest a default application name based on the file name.
- Configure terminal mode, description, and application category.
- Create a `.desktop` file in `~/.local/share/applications`.
- Optionally create the same shortcut on the GNOME desktop.

Supported categories are `Utility`, `Development`, `Game`, `Network`, `AudioVideo`, `Office`, and `System`.

Execution options are entered separately from the executable path. Enter only additional arguments such as `--no-sandbox`; the manager appends `%u` automatically:

```text
Executable: /opt/bruno/bruno.AppImage
Additional execution options: --no-sandbox
Generated Exec value: "/opt/bruno/bruno.AppImage" --no-sandbox %u
```

If the options already contain `%f`, `%F`, `%u`, or `%U`, the manager preserves that field code without adding another `%u`. These field codes pass one file, multiple files, one URL/URI, or multiple URLs/URIs, respectively.

Terminal mode controls whether GNOME opens a terminal for the command. Use `Terminal=true` for CLI tools and interactive scripts; GUI applications such as AppImages normally use `Terminal=false`.

### Icon selection

Icons can be selected through the following workflow:

1. Search for image files up to three directory levels below the executable's directory.
2. Select one of the detected images.
3. Select one of 82 predefined system icons.
4. Enter the full path to a custom icon file.

The automatic search recognizes these file extensions:

```text
.png  .svg  .ico  .xpm  .jpg  .jpeg
```

The system icon list uses names commonly provided by Freedesktop-compatible Ubuntu and GNOME icon themes. The rendered appearance can vary with the installed theme.

- General: executables, terminals, settings, games, internet, office, and development
- Tools and documents: calculator, editor, archives, system monitor, logs, and PDF
- Internet and communications: server, Wi-Fi, Ethernet, VPN, email, chat, and Bluetooth
- Files and storage: disks, USB drives, remote folders, downloads, pictures, and videos
- Multimedia: graphics, cameras, music, headphones, speakers, and microphones
- System and security: locks, authentication, users, input devices, printers, and batteries

### Shortcut editing

Select any `.desktop` file in the user application directory by number and edit the following properties:

- Application name
- Executable path
- Additional execution options (`%u` remains automatic)
- Icon
- Terminal mode
- Desktop shortcut presence (`true` when the matching file exists, otherwise `false`)

The Desktop shortcut item can be toggled before saving. Changing it from `false` to `true` copies the updated `.desktop` file to the Desktop; changing it from `true` to `false` removes the Desktop copy. When it remains `true`, saved changes are synchronized to the existing copy.

Changing only the executable path preserves its current additional options. The execution-options item can replace or clear those arguments independently; pressing Enter clears the additional arguments while the automatically managed `%u` remains. Older manager-created shortcuts that do not contain a file/URI field code are normalized with `%u` when opened for editing and then saved.

### Listing and deletion

- Display the application name, executable command, and icon.
- Mark entries created by this utility with `[manager-created]`.
- Show the application name and file name before requesting deletion confirmation.
- Remove the matching files from both the application menu and desktop after confirmation.

> Caution: the list can contain every user `.desktop` file in `~/.local/share/applications`, not only files created by this utility. Verify the application name and path before deleting an entry.

### GNOME integration

After a shortcut is created or changed, the script performs the following operations when their supporting commands are available:

- Add execute permission to the `.desktop` file.
- Set the GIO `metadata::trusted` attribute to the exact string `true` so DING treats Desktop copies as allowed to launch.
- Run `update-desktop-database`.
- Refresh the user GTK icon cache.
- Trigger directory update events for GNOME Shell and DING.

If an optional command is unavailable, only that integration step is skipped. The basic shortcut operation continues.

## Requirements

- A GNOME desktop environment
- Bash 4 or later for associative array support
- Standard GNU/Linux commands: `find`, `sed`, `awk`, `grep`, `cut`, and `realpath`
- Optional integration commands: `xdg-user-dir`, `gio`, `update-desktop-database`, and `gtk-update-icon-cache`

## Installation and startup

Move to the directory containing the script, grant execute permission, and run it:

```bash
cd /path/to/shortcut
chmod +x gnome_shortcut_manager.sh
./gnome_shortcut_manager.sh
```

You can also run the script through Bash without changing its permissions:

```bash
bash gnome_shortcut_manager.sh
```

## Usage examples

All examples below use the English interface. Press Enter at the language prompt to select English by default.

### Example 1: Start the manager in English

```text
$ ./gnome_shortcut_manager.sh
======================================================
          Select Language / 언어 선택
======================================================

  1) English
  2) 한국어 (Korean)

Select (1-2, default: 1):

======================================================
                GNOME Shortcut Manager
======================================================

Choose an action:

  1) Register a new executable shortcut
  2) Edit a registered app shortcut
  3) Delete a registered app shortcut
  4) View all registered apps
  0) Exit
```

### Example 2: Register an executable

The following example registers `/opt/my-tool/run.sh` as a utility that runs in a terminal. The system icon number should be selected from the list displayed on your system.

```text
$ ./gnome_shortcut_manager.sh
Select (1-2, default: 1):

Choose an action:
  1) Register a new executable shortcut
  2) Edit a registered app shortcut
  3) Delete a registered app shortcut
  4) View all registered apps
  0) Exit

Select (0-4): 1
Enter the full path to the executable (cancel: q): /opt/my-tool/run.sh
Additional execution options (optional; %u is added automatically, e.g. --no-sandbox):
App name (default: 'Run'): My Tool

Choose an icon selection method:
  1) Choose from 82 recommended system icons
  2) Enter a custom icon file path
Select (1-2, default: 1): 1
Choose a system icon (1-82): 2
✔ Selected system icon: utilities-terminal

Does this app need to run in a terminal? (y/N): y
App description/comment (optional; Enter for default): My terminal tool
Choose a category (1-7, default: 1): 1
Also create the shortcut on the Desktop? (Y/n): y

✔ 'My Tool' was registered successfully!
```

Registration normally creates these files:

```text
~/.local/share/applications/my-tool.desktop
~/Desktop/my-tool.desktop
```

The generated `.desktop` file has the following structure:

```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=My Tool
Comment=My terminal tool
Exec="/opt/my-tool/run.sh" %u
Icon=utilities-terminal
Terminal=true
Categories=Utility;
StartupNotify=true
X-Created-By=shortcut-manager
```

### Example 3: Use a custom icon file

Choose option `2` in the icon selection menu and enter an absolute image path:

```text
Choose an icon selection method:
  1) Choose from 82 recommended system icons
  2) Enter a custom icon file path
Select (1-2, default: 1): 2
Enter the full path to an icon image: /opt/my-tool/assets/icon.png
```

If the file exists, its absolute path is stored in the `.desktop` file's `Icon` field.

### Example 4: Edit a registered shortcut

Choose option `2` from the main menu, then select the application and property to edit:

```text
Select (0-4): 2

--- Registered Apps (~/.local/share/applications) ---
   1) My Tool                   [manager-created]
      ├─ Executable: "/opt/my-tool/run.sh" %u
      └─ Icon: utilities-terminal

Choose an app to edit (1-1, cancel: 0): 1

  1) Change app name
  2) Change executable path
  3) Change execution options (current: none)
  4) Change icon
  5) Toggle terminal mode
  6) Toggle Desktop shortcut (current: false)
  7) Save changes
  0) Cancel editing

Choose an item to edit (0-7): 3
Enter additional execution options (current: none; Enter to clear; %u is automatic): --no-sandbox
```

After changing the desired properties, choose option `7` to save them. In this example, the saved command becomes:

```ini
Exec="/opt/my-tool/run.sh" --no-sandbox %u
```

### Example 5: List and delete shortcuts

Choose option `4` from the main menu to inspect registered shortcuts:

```text
Select (0-4): 4

--- Registered Apps (~/.local/share/applications) ---
   1) My Tool                   [manager-created]
      ├─ Executable: "/opt/my-tool/run.sh" %u
      └─ Icon: utilities-terminal
```

To delete a shortcut, choose option `3` and confirm with `y`:

```text
Select (0-4): 3
Choose an app to delete (1-1, cancel: 0): 1
⚠ Delete the 'My Tool' (my-tool.desktop) shortcut?
Confirm (y/N): y
✔ 'My Tool' deleted!
```

## Generated paths

| Purpose | Default path |
|---|---|
| GNOME application menu | `~/.local/share/applications/*.desktop` |
| Desktop | The result of `xdg-user-dir DESKTOP`, or `~/Desktop` |
| User icon cache | `~/.local/share/icons` |

Application names are converted to lowercase file IDs. A name without ASCII letters or digits can produce a file named `app-<random-number>.desktop`.

## Notes

- Executable paths and custom icon paths must refer to existing files.
- Searching for nearby icons can take time when the executable is stored in a large directory tree.
- GNOME can display a fallback icon when the active theme does not provide a selected system icon name.
- Desktop icon visibility depends on the GNOME extension or DING configuration.
- The script manages the current user's application directory, not the system-wide application directory.
