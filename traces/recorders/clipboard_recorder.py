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
import json
import threading
import datetime

from AppKit import *
from Foundation import *

import config as cfg
import preferences
import utils_cocoa


class ClipboardRecorder:

    def __init__(self, sniffer):
        self.sniffer = sniffer
        self.last_count = None

    # may not need to do the loop, testing on clicks and Cmd + C
    def start_clipboard_loop(self):
        self.clipTimer = threading.Timer(cfg.CLIPDELAY, self.continue_clipboard_loop)
        self.clipTimer.start()

    def continue_clipboard_loop(self):
        self.get_clipboard_contents()
        self.clipTimer = threading.Timer(cfg.CLIPDELAY, self.continue_clipboard_loop)
        self.clipTimer.start()

    def stop_clipboard_loop(self):
        if self.clipTimer:
            self.clipTimer.stop()

    def get_clipboard_contents(self):
        # only store data if we have new items
        recording = preferences.getValueForPreference('recording')
        if recording:
            clip = NSPasteboard.generalPasteboard()
            count =  clip.changeCount()
            if self.last_count == None:
                self.last_count = count
            elif count != self.last_count:
                self.last_count = count
                text = ""
                url = ""
                image = None
                path = ""

                items = clip.pasteboardItems()
                for i in items:
                    t = i.types()
                    # get the textual data
                    if 'public.utf8-plain-text' in t:
                        text = i.stringForType_('public.utf8-plain-text')
                    if 'public.url' in t:
                        url = i.stringForType_('public.url')
                    if 'public.url-name' in t:
                        url = i.stringForType_('public.url-name')
                    if 'public.file-url' in t:
                        url = i.stringForType_('public.file-url')
                    # get image data
                    if 'public.tiff' in t:
                        image = i.dataForType_('public.tiff')
                    if 'public.png' in t:
                        image = i.dataForType_('public.png')
                    if 'public.jpeg' in t:
                        image = i.dataForType_('public.jpeg')
                    # save image file if we have one
                    if image != None:
                        folder = os.path.join(cfg.CURRENT_DIR,"clipboard")
                        filename = datetime.datetime.now().strftime("%y%m%d-%H%M%S%f")
                        path = os.path.join(folder,""+filename+".jpg")
                        image.writeToFile_atomically_(path ,False)

                    # clean up text and url
                    text = json.dumps(text)
                    url = json.dumps(url)

                    # save to a clipboard file
                    tex = '{"time": '+ str(cfg.NOW()) + ' , "text": ' + text + ' , "url": ' + url + ' , "image": "' + path + '"}'
                    utils_cocoa.write_to_file(tex, cfg.CLIPLOG)
