# Windows 11 Shortcuts for macOS (Karabiner-Elements)

A complete [Karabiner-Elements](https://karabiner-elements.pqrs.org/) ruleset that makes a Mac feel like Windows 11. Built for macOS 15 Sequoia or newer (window snapping uses the native tiling shortcuts; tested on macOS 26).

**Philosophy:** the **Cmd key acts as the Win key** (on a PC keyboard, the Win key already lands on Cmd), and **Ctrl is your everyday shortcut key** (Ctrl+C/V/S/Z…), just like Windows. Terminals (Terminal, iTerm2, kitty, WezTerm, Warp, Ghostty, Alacritty), Emacs, VMs (Parallels, VMware, VirtualBox, UTM), and remote-desktop apps are excluded from the text-editing remaps, so Ctrl+C still interrupts a process in a shell and shortcuts pass through to VMs.

## Install

```sh
cp windows11.json ~/.config/karabiner/assets/complex_modifications/
```

Then in Karabiner-Elements → Complex Modifications → Add predefined rule → enable the rules under **"Windows 11 Shortcuts for macOS"**. Every rule is individually toggleable — disable any you don't like.

To modify the set, edit `generate.py` and run:

```sh
python3 generate.py windows11.json
"/Library/Application Support/org.pqrs/Karabiner-Elements/bin/karabiner_cli" --lint-complex-modifications windows11.json
```

## Window management

Snapping drives the native **Window → Move & Resize** menu via AppleScript (the virtual keyboard's synthetic Globe+Ctrl shortcuts are ignored by macOS tiling). The first use may prompt you to allow Karabiner to control "System Events" — click Allow.

| Windows 11 | Result on Mac |
|---|---|
| Win+Left / Win+Right | Snap window to left / right half |
| Win+Up | Maximize (Fill) |
| Win+Down | Minimize |
| Win+Shift+Down | Restore window to its pre-snap size |
| Win+Alt+Left / Win+Alt+Right | Snap to top-left / top-right quarter (+Shift for bottom corners) |
| Win+M | Minimize all windows of the current app |
| Alt+Space | Open the Window menu (window-control menu) |
| Ctrl+Win+Left/Right | Switch virtual desktop (Space) |
| Win+Ctrl+D | Create a new virtual desktop (Space) |
| Win+D | Show desktop |
| Win+Tab | Task View (Mission Control) |
| Alt+Tab / Alt+Shift+Tab | Switch apps forward / backward |

## System

| Windows 11 | Result on Mac |
|---|---|
| Win (tap alone) | Start menu (Spotlight) — hold Win for the Win+key shortcuts |
| Win+R | Run (Spotlight) |
| Win+A | Quick Settings (Control Center) |
| Win+N | Notification Center |
| Win+P | Display settings |
| Win+U | Accessibility settings |
| Win+E | New Finder window (Home folder) |
| Win+L | Lock screen |
| Win+I | System Settings |
| Win+S | Spotlight search |
| Win+Space | Switch input source (needs 2+ input sources) |
| Win+. | Emoji picker |
| Win+Shift+S | Snip region to clipboard |
| PrtScn | Screenshot toolbar (Snipping Tool) |
| Alt+PrtScn | Active window to clipboard |
| Win+PrtScn | Full screen to file |
| Ctrl+Esc | Spotlight (Start menu — Launchpad no longer exists on macOS 26) |
| Ctrl+Shift+Esc | Activity Monitor (Task Manager) |
| Ctrl+Alt+Delete | Force Quit dialog |
| Alt+F4 | Quit application |

## Editing & navigation (terminals excluded)

| Windows 11 | Result on Mac |
|---|---|
| Ctrl + A B C F I K L N O P R S T U V W X Z | Cmd + same letter (Shift passes through, so Ctrl+Shift+T/V/Z work) |
| Ctrl+Y | Redo (Cmd+Shift+Z) |
| Ctrl+Insert / Shift+Insert | Copy / Paste |
| Ctrl+Left/Right (+Shift) | Jump/select by word |
| Ctrl+Up/Down (+Shift) | Jump/select by paragraph |
| Ctrl+Backspace / Ctrl+Delete | Delete previous / next word |
| Home / End (+Shift) | Start / end of line |
| Ctrl+Home / Ctrl+End (+Shift) | Start / end of document |
| PageUp / PageDown | Move the cursor a page, Windows-style (Shift+PageUp/Down selects) |
| F3 / Shift+F3 | Find next / previous |
| F5 / Ctrl+F5 | Reload / hard reload |
| F11 | Full screen |
| Alt+Left / Alt+Right | Back / Forward |
| Ctrl+Plus / Minus / 0 | Zoom in / out / reset |

## File Explorer → Finder

| Windows 11 | Result on Mac |
|---|---|
| Delete | Move to Trash |
| Shift+Delete | Delete permanently (with confirmation) |
| F2 | Rename |
| Enter | Open selected item (separate rule — disable it if you prefer Finder's rename-on-Enter) |
| Alt+Enter | Get Info (Properties) |
| Alt+Up | Parent folder |
| Ctrl+Shift+N | New folder |

## If the Win key doesn't act like Win

The usual culprit is **macOS's own modifier remapping** (System Settings → Keyboard → Keyboard Shortcuts… → Modifier Keys), typically an old Ctrl↔Cmd swap from before Karabiner. These mappings are **per keyboard**, and they apply *upstream* of Karabiner — so a swap here scrambles which rules fire (e.g. Ctrl triggers the Win-key rules). Resetting one keyboard in the dropdown does not reset the others: go through **every keyboard listed** (a keyboard on a Logitech Bolt/Unifying dongle appears as "USB Receiver") and restore defaults on each.

To audit from the terminal — any entry that isn't self-identity is a leftover remap:

```sh
defaults -currentHost read -g | grep -A14 modifiermapping
```

Delete a stale entry (then unplug/replug the keyboard, or clear it live with `hidutil property --set '{"UserKeyMapping":[]}'`):

```sh
defaults -currentHost delete -g com.apple.keyboard.modifiermapping.<vendor>-<product>-0
```

If your keyboard genuinely runs a Mac layout (Keychron hardware switch on "Mac", a Logitech MX Keys without Logi Options+, the Mac's built-in keyboard, etc.) and sends Option from the Win-position key, fix that with a device-scoped Option↔Command swap in Karabiner's Simple Modifications for that keyboard only — swap left/right Option→Command and left/right Command→Option. Verify with Karabiner-EventViewer first (the Win-position key should report `left_command` after the swap); an OS-level swap looks identical from the app side. For the built-in Apple keyboard, target the device whose vendor/product IDs are 0.

## Things to know

- **Cmd+Tab is replaced** by Mission Control (Win+Tab behavior). Use Alt+Tab to switch apps. Disable the Win+Tab rule if you want native Cmd+Tab back.
- **Cmd+letter shortcuts are the Win-key layer now**: Cmd+S is Spotlight (save with Ctrl+S), Cmd+D shows the desktop, Cmd+I opens Settings (italics is Ctrl+I). If you don't want one of these, toggle off that single rule.
- **Cmd+arrows are window snapping**, so Cmd+Left/Right no longer jump to line start/end — that's what Home/End do now, like on Windows. In Finder, use Alt+Up instead of Cmd+Up for the parent folder.
- **Tapping Win alone opens Spotlight** (Start-menu behavior). The tap fires on press-and-release within 400ms; holding Win as a modifier is unaffected. Toggle off that one rule if you find it too eager.
- **No macOS equivalents exist** for: Win+V clipboard history (install [Raycast](https://raycast.com) or Maccy and bind it), Win+Shift+Left/Right move-window-to-other-display (drag, or use Rectangle), Win+number for Dock apps, Win+Ctrl+F4 close-desktop.
- **Menu-driven shortcuts** (window snapping, Win+A/N, Alt+Space, Win+Ctrl+D) run AppleScript against the frontmost app's menus, so they have a small delay and need the Accessibility permission Karabiner already requests.
- **VS Code / JetBrains integrated terminals**: the Ctrl remaps apply there (the exclusion list only covers dedicated terminal apps), so use Cmd+C to interrupt a process in an IDE terminal, or add the IDE's bundle ID to the exclusion list in `generate.py`.
