#!/usr/bin/env python3
"""Generate the Windows 11 -> macOS Karabiner-Elements ruleset."""
import json, sys

TERMINALS = [
    "^com\\.apple\\.Terminal$",
    "^com\\.googlecode\\.iterm2$",
    "^co\\.zeit\\.hyper$",
    "^net\\.kovidgoyal\\.kitty$",
    "^org\\.alacritty$",
    "^com\\.github\\.wez\\.wezterm$",
    "^dev\\.warp\\.Warp",
    "^com\\.mitchellh\\.ghostty$",
    "^org\\.gnu\\.Emacs$",
]
VMS_REMOTE = [
    "^com\\.vmware\\.fusion$",
    "^org\\.virtualbox\\.app\\.VirtualBoxVM$",
    "^com\\.parallels\\.desktop\\.console$",
    "^com\\.utmapp\\.UTM$",
    "^com\\.microsoft\\.rdc\\.macos$",
    "^com\\.realvnc\\.vncviewer$",
    "^com\\.citrix\\.receiver\\.icaviewer\\.mac$",
]

def unless(ids):
    return {"type": "frontmost_application_unless", "bundle_identifiers": ids}

COND_TEXT = [unless(TERMINALS + VMS_REMOTE)]   # text-editing rules: skip terminals & VMs
COND_GUI = [unless(VMS_REMOTE)]                # system rules: skip VMs/remote only
COND_FINDER = [{"type": "frontmost_application_if", "bundle_identifiers": ["^com\\.apple\\.finder$"]},
               unless(VMS_REMOTE)]
COND_EXCEL = [{"type": "frontmost_application_if", "bundle_identifiers": ["^com\\.microsoft\\.Excel$"]}]
COND_TEXT_NO_EXCEL = COND_TEXT + [unless(["^com\\.microsoft\\.Excel$"])]

def frm(key, mand=None, opt=None):
    f = {"key_code": key}
    mods = {}
    if mand: mods["mandatory"] = mand
    mods["optional"] = (opt or []) + ["caps_lock"]
    f["modifiers"] = mods
    return f

def key(k, mods=None):
    e = {"key_code": k}
    if mods: e["modifiers"] = mods
    return e

def m(from_, to, conds):
    man = {"type": "basic", "from": from_, "to": to if isinstance(to, list) else [to]}
    if conds: man["conditions"] = conds
    return man

def rule(desc, manipulators):
    return {"description": desc, "manipulators": manipulators}

rules = []

def menu_click(clause):
    # Synthetic fn(Globe)+Ctrl+arrow from the virtual keyboard does not trigger
    # macOS tiling, so drive the Window menu via AX instead.
    return {"shell_command":
            "osascript -e 'tell application \"System Events\" to tell "
            "(first application process whose frontmost is true) to click " + clause + "'"}

# ---------- Window management ----------

rules.append(rule("Alt+Space: open the Window menu (Windows window-control menu)", [
    m(frm("spacebar", ["option"]), menu_click('menu bar item "Window" of menu bar 1'), COND_GUI),
]))
rules.append(rule("Win+Ctrl+D: create a new virtual desktop (Space)", [
    m(frm("d", ["command", "control"]),
      {"shell_command": "osascript"
       " -e 'tell application \"Mission Control\" to launch'"
       " -e 'delay 0.4'"
       " -e 'tell application \"System Events\" to tell process \"Dock\" to click button 1 of group \"Spaces Bar\" of group 1 of group \"Mission Control\"'"
       " -e 'delay 0.3'"
       " -e 'tell application \"System Events\" to key code 53'"},
      COND_GUI),
]))
rules.append(rule("Ctrl+Win+Left/Right: switch virtual desktops (Spaces)", [
    m(frm("left_arrow", ["command", "control"]), key("left_arrow", ["left_control"]), COND_GUI),
    m(frm("right_arrow", ["command", "control"]), key("right_arrow", ["left_control"]), COND_GUI),
]))
rules.append(rule("Win+D: show desktop", [
    m(frm("d", ["command"]), {"apple_vendor_keyboard_key_code": "expose_desktop"}, COND_GUI + [unless(["^com\\.apple\\.finder$"])]),
]))

# ---------- Win-key system shortcuts ----------
rules.append(rule("Win alone: Start menu (Spotlight) — hold Win for Win+key shortcuts", [
    {"type": "basic",
     "from": {"key_code": kc, "modifiers": {"optional": ["any"]}},
     "to": [{"key_code": kc}],
     "to_if_alone": [{"apple_vendor_keyboard_key_code": "spotlight"}],
     "conditions": COND_GUI,
     "parameters": {"basic.to_if_alone_timeout_milliseconds": 400}}
    for kc in ("left_command", "right_command")
]))
rules.append(rule("Win+R: Run (Spotlight)", [
    m(frm("r", ["command"]), {"apple_vendor_keyboard_key_code": "spotlight"}, COND_GUI),
]))
rules.append(rule("Win+M: minimize all windows of current app", [
    m(frm("m", ["command"]), key("m", ["left_command", "left_option"]), COND_GUI),
]))
rules.append(rule("Win+A: Quick Settings (Control Center)", [
    m(frm("a", ["command"]),
      {"shell_command": "osascript -e 'tell application \"System Events\" to tell process \"ControlCenter\" to click menu bar item \"Control Center\" of menu bar 1'"},
      COND_GUI),
]))
rules.append(rule("Win+N: Notification Center", [
    m(frm("n", ["command"]),
      {"shell_command": "osascript -e 'tell application \"System Events\" to tell process \"ControlCenter\" to click menu bar item \"Clock\" of menu bar 1'"},
      COND_GUI),
]))
rules.append(rule("Win+P: display settings", [
    m(frm("p", ["command"]), {"shell_command": "open 'x-apple.systempreferences:com.apple.Displays-Settings.extension'"}, COND_GUI),
]))
rules.append(rule("Win+U: accessibility settings", [
    m(frm("u", ["command"]), {"shell_command": "open 'x-apple.systempreferences:com.apple.Accessibility-Settings.extension'"}, COND_GUI),
]))
rules.append(rule("Win+E: open File Explorer (new Finder window on Home)", [
    m(frm("e", ["command"]), {"shell_command": "open ~"}, COND_GUI),
]))
rules.append(rule("Win+L: lock screen", [
    m(frm("l", ["command"]), key("q", ["left_control", "left_command"]), None),
]))
rules.append(rule("Win+I: open Settings (System Settings)", [
    m(frm("i", ["command"]), {"shell_command": "open -b com.apple.systempreferences"}, COND_GUI),
]))
rules.append(rule("Win+Shift+S: snip region to clipboard", [
    m(frm("s", ["command", "shift"]), key("4", ["left_command", "left_shift", "left_control"]), COND_GUI),
]))
rules.append(rule("Win+S: search (Spotlight) — overrides Cmd+S save; use Ctrl+S to save", [
    m(frm("s", ["command"]), {"apple_vendor_keyboard_key_code": "spotlight"}, COND_GUI),
]))
rules.append(rule("Win+Space: switch input source (needs 2+ input sources enabled)", [
    m(frm("spacebar", ["command"]), key("spacebar", ["left_control"]), COND_GUI),
]))
rules.append(rule("Win+. (period): emoji picker", [
    m(frm("period", ["command"]), key("spacebar", ["left_control", "left_command"]), COND_GUI),
]))
rules.append(rule("Ctrl+Esc: Start menu (Spotlight)", [
    m(frm("escape", ["control"]), {"apple_vendor_keyboard_key_code": "spotlight"}, COND_GUI),
]))
rules.append(rule("Ctrl+Shift+Esc: Task Manager (Activity Monitor)", [
    m(frm("escape", ["control", "shift"]), {"shell_command": "open -a 'Activity Monitor'"}, COND_GUI),
]))
rules.append(rule("Ctrl+Alt+Delete: Force Quit dialog", [
    m(frm("delete_forward", ["control", "option"]), key("escape", ["left_command", "left_option"]), COND_GUI),
]))
rules.append(rule("Alt+F4: quit application", [
    m(frm("f4", ["option"]), key("w", ["left_command"]), [{"type": "frontmost_application_if", "bundle_identifiers": ["^com\\.apple\\.finder$"]}]),
    m(frm("f4", ["option"]), key("q", ["left_command"]), COND_GUI),
]))

# ---------- Excel ----------
rules.append(rule("Excel: F4 toggles absolute/relative references (Cmd+T)", [
    m(frm("f4"), key("t", ["left_command"]), COND_EXCEL),
]))


# ---------- Screenshots ----------
rules.append(rule("PrintScreen: Snipping Tool (screenshot toolbar); Alt+PrtScn: window to clipboard; Win+PrtScn: full screen to file", [
    m(frm("print_screen", ["command"]), key("3", ["left_command", "left_shift"]), COND_GUI),
    m(frm("print_screen", ["option"]), [key("4", ["left_command", "left_shift", "left_control"]), key("spacebar")], COND_GUI),
    m(frm("print_screen"), key("5", ["left_command", "left_shift"]), COND_GUI),
]))

# ---------- Ctrl -> Cmd standard shortcuts ----------
CTRL_LETTERS = ["a", "b", "c", "f", "i", "k", "l", "n", "o", "p", "r", "s", "t", "u", "v", "w", "x", "z"]
ctrl_manips = [m(frm(c, ["control"], ["shift"]), key(c, ["left_command"]), COND_TEXT) for c in CTRL_LETTERS]
ctrl_manips.append(m(frm("y", ["control"]), key("z", ["left_command", "left_shift"]), COND_TEXT))  # redo
rules.append(rule("Ctrl+letter → Cmd+letter: copy/paste/cut, undo/redo, select all, save, find, new, open, print, tabs, bold/italic/underline… (Shift passes through; terminals excluded)", ctrl_manips))

rules.append(rule("Ctrl+Insert / Shift+Insert: copy / paste", [
    m(frm("insert", ["control"]), key("c", ["left_command"]), COND_TEXT),
    m(frm("insert", ["shift"]), key("v", ["left_command"]), COND_TEXT),
]))

# ---------- Text navigation ----------
rules.append(rule("Ctrl+Arrows: word/paragraph navigation (Shift to select)", [
    m(frm("left_arrow", ["control"], ["shift"]), key("left_arrow", ["left_option"]), COND_TEXT),
    m(frm("right_arrow", ["control"], ["shift"]), key("right_arrow", ["left_option"]), COND_TEXT),
    m(frm("up_arrow", ["control"], ["shift"]), key("up_arrow", ["left_option"]), COND_TEXT),
    m(frm("down_arrow", ["control"], ["shift"]), key("down_arrow", ["left_option"]), COND_TEXT),
]))
rules.append(rule("Ctrl+Backspace / Ctrl+Delete: delete previous/next word", [
    m(frm("delete_or_backspace", ["control"]), key("delete_or_backspace", ["left_option"]), COND_TEXT),
    m(frm("delete_forward", ["control"]), key("delete_forward", ["left_option"]), COND_TEXT),
]))
rules.append(rule("Home/End: start/end of line; Ctrl+Home/End: start/end of document (Shift to select)", [
    m(frm("home", ["control"], ["shift"]), key("up_arrow", ["left_command"]), COND_TEXT),
    m(frm("end", ["control"], ["shift"]), key("down_arrow", ["left_command"]), COND_TEXT),
    m(frm("home", None, ["shift"]), key("left_arrow", ["left_command"]), COND_TEXT),
    m(frm("end", None, ["shift"]), key("right_arrow", ["left_command"]), COND_TEXT),
]))

rules.append(rule("PageUp/PageDown: move the cursor a page (Windows style; Shift to select works natively)", [
    m(frm("page_up"), key("page_up", ["left_option"]), COND_TEXT),
    m(frm("page_down"), key("page_down", ["left_option"]), COND_TEXT),
]))
rules.append(rule("F3 / Shift+F3: find next / previous", [
    m(frm("f3", ["shift"]), key("g", ["left_command", "left_shift"]), COND_TEXT_NO_EXCEL),
    m(frm("f3"), key("g", ["left_command"]), COND_TEXT_NO_EXCEL),
]))

# ---------- Browser ----------
rules.append(rule("Browser: F5 / Ctrl+F5 refresh, F11 full screen, Alt+Left/Right back/forward, Ctrl +/-/0 zoom", [
    m(frm("f5", ["control"]), key("r", ["left_command", "left_shift"]), COND_TEXT),
    m(frm("f5"), key("r", ["left_command"]), COND_TEXT),
    m(frm("f11"), key("f", ["left_control", "left_command"]), COND_TEXT),
    m(frm("left_arrow", ["option"]), key("open_bracket", ["left_command"]), COND_TEXT_NO_EXCEL),
    m(frm("right_arrow", ["option"]), key("close_bracket", ["left_command"]), COND_TEXT_NO_EXCEL),
    m(frm("equal_sign", ["control"], ["shift"]), key("equal_sign", ["left_command"]), COND_TEXT),
    m(frm("hyphen", ["control"]), key("hyphen", ["left_command"]), COND_TEXT),
    m(frm("0", ["control"]), key("0", ["left_command"]), COND_TEXT),
    m(frm("keypad_plus", ["control"]), key("equal_sign", ["left_command"]), COND_TEXT),
    m(frm("keypad_hyphen", ["control"]), key("hyphen", ["left_command"]), COND_TEXT),
]))

# ---------- Finder = File Explorer ----------
rules.append(rule("Explorer→Finder: Delete moves to Trash, Shift+Delete deletes permanently, F2 renames, Alt+Enter Get Info, Alt+Up parent folder", [
    m(frm("delete_forward", ["shift"]), key("delete_or_backspace", ["left_command", "left_option"]), COND_FINDER),
    m(frm("delete_forward"), key("delete_or_backspace", ["left_command"]), COND_FINDER),
    m(frm("f2"), key("return_or_enter"), COND_FINDER),
    m(frm("return_or_enter", ["option"]), key("i", ["left_command"]), COND_FINDER),
    m(frm("up_arrow", ["option"]), key("up_arrow", ["left_command"]), COND_FINDER),
]))
rules.append(rule("Explorer→Finder: Enter opens the selected item (rename with F2)", [
    m(frm("return_or_enter"), key("o", ["left_command"]), COND_FINDER),
]))

# ---------- Custom Utilities ----------
rules.append(rule("Ctrl+Alt+T: open Terminal", [
    m(frm("t", ["control", "option"]), {"shell_command": "open -a Terminal"}, COND_GUI),
]))

doc = {"title": "Windows 11 Shortcuts for macOS", "rules": rules}
out = sys.argv[1]
with open(out, "w") as f:
    json.dump(doc, f, indent=2)
print(f"wrote {out}: {len(rules)} rules, {sum(len(r['manipulators']) for r in rules)} manipulators")
