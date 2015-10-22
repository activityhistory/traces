# -*- coding: utf-8 -*-
"""
Traces: Activity Tracker
Copyright (C) 2015 Adam Rule
with Aurélien Tabard, Jonas Keper, Azeem Ghumman, and Maxime Guyaux

Inspired by Selfspy and Burrito
https://github.com/gurgeh/selfspy
https://github.com/pgbovine/burrito/

You should have received a copy of the GNU General Public License
along with Traces. If not, see <http://www.gnu.org/licenses/>.
"""

import os

from Cocoa import (NSEvent, NSKeyDown, NSKeyDownMask, NSKeyUp, NSKeyUpMask,
                   NSFlagsChanged, NSFlagsChangedMask, NSAlternateKeyMask,
                   NSCommandKeyMask, NSControlKeyMask, NSShiftKeyMask,
                   NSAlphaShiftKeyMask)

import config as cfg
import preferences
import utils_cocoa


SKIP_MODIFIERS = {"", "Shift_L", "Control_L", "Super_L", "Alt_L", "Super_R",
                    "Control_R", "Shift_R", "[65027]"}  # [65027] is AltGr in X

# Cocoa does not provide a good api to get the keycodes,
# therefore we have to provide our own.
KEYCODES = {
   u"\u0009": "Tab",
   u"\u001b": "Escape",
   u"\uf700": "Up",
   u"\uF701": "Down",
   u"\uF702": "Left",
   u"\uF703": "Right",
   u"\uF704": "F1",
   u"\uF705": "F2",
   u"\uF706": "F3",
   u"\uF707": "F4",
   u"\uF708": "F5",
   u"\uF709": "F6",
   u"\uF70A": "F7",
   u"\uF70B": "F8",
   u"\uF70C": "F9",
   u"\uF70D": "F10",
   u"\uF70E": "F11",
   u"\uF70F": "F12",
   u"\uF710": "F13",
   u"\uF711": "F14",
   u"\uF712": "F15",
   u"\uF713": "F16",
   u"\uF714": "F17",
   u"\uF715": "F18",
   u"\uF716": "F19",
   u"\uF717": "F20",
   u"\uF718": "F21",
   u"\uF719": "F22",
   u"\uF71A": "F23",
   u"\uF71B": "F24",
   u"\uF71C": "F25",
   u"\uF71D": "F26",
   u"\uF71E": "F27",
   u"\uF71F": "F28",
   u"\uF720": "F29",
   u"\uF721": "F30",
   u"\uF722": "F31",
   u"\uF723": "F32",
   u"\uF724": "F33",
   u"\uF725": "F34",
   u"\uF726": "F35",
   u"\uF727": "Insert",
   u"\uF728": "Delete",
   u"\uF729": "Home",
   u"\uF72A": "Begin",
   u"\uF72B": "End",
   u"\uF72C": "PageUp",
   u"\uF72D": "PageDown",
   u"\uF72E": "PrintScreen",
   u"\uF72F": "ScrollLock",
   u"\uF730": "Pause",
   u"\uF731": "SysReq",
   u"\uF732": "Break",
   u"\uF733": "Reset",
   u"\uF734": "Stop",
   u"\uF735": "Menu",
   u"\uF736": "User",
   u"\uF737": "System",
   u"\uF738": "Print",
   u"\uF739": "ClearLine",
   u"\uF73A": "ClearDisplay",
   u"\uF73B": "InsertLine",
   u"\uF73C": "DeleteLine",
   u"\uF73D": "InsertChar",
   u"\uF73E": "DeleteChar",
   u"\uF73F": "Prev",
   u"\uF740": "Next",
   u"\uF741": "Select",
   u"\uF742": "Execute",
   u"\uF743": "Undo",
   u"\uF744": "Redo",
   u"\uF745": "Find",
   u"\uF746": "Help",
   u"\uF747": "ModeSwitch"}


class KeyRecorder:

    def __init__(self, sniffer):
        self.sniffer = sniffer

    def start_key_listener(self):
        #TODO may only need the keydown mask, rather than all three
        mask = (NSKeyDownMask | NSKeyUpMask | NSFlagsChangedMask)
        NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(mask, self.key_handler)

    def key_handler(self, event):
        event_screenshots = preferences.getValueForPreference('eventScreenshots')
        if event_screenshots:
            self.sniffer.activity_tracker.take_screenshot()

        if event.type() == NSKeyDown:
            # get the modifier keys that were depressed when this key was pressed
            flags = event.modifierFlags()
            modifiers = []  # OS X api doesn't care it if is left or right
            if flags & NSControlKeyMask:
                modifiers.append('Ctrl')
            if flags & NSAlternateKeyMask:
                modifiers.append('Alt')
            if flags & NSCommandKeyMask:
                modifiers.append('Cmd')
            if flags & (NSShiftKeyMask | NSAlphaShiftKeyMask):
                modifiers.append('Shift')

            # TODO determine why we have to use keycodes here for enter and
            # backspace but can rely on the charachter list for the others
            # get the charachter of the pressed key
            character = event.charactersIgnoringModifiers()
            if event.keyCode() is 51:
                character = "Backspace"
            elif event.keyCode() is 36:
                character = "Enter"
            elif event.keyCode() is 39 and modifiers == ["Shift"]:
                 character = "\\\""
            elif event.keyCode() is 46 and modifiers == ["Cmd", "Shift"]:
                self.sniffer.delegate.showExperience_("Fake Notification")

            string = KEYCODES.get(character, character)

            if string in SKIP_MODIFIERS:
                return

            # write JSON object to keylog file
            text = '{"time": '+ str(cfg.NOW()) + ' , "key": "' + string + '" , "modifiers": ' + str(modifiers) + '}'
            utils_cocoa.write_to_file(text, cfg.KEYLOG)
