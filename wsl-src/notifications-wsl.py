#!/usr/bin/env python3

# notification-wsl - capture notifications from dbus and pass them through to Windows

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

class NotificationWsl(dbus.service.Object):
    _id = 0

    @dbus.service.method("org.freedesktop.Notifications",
                          in_signature='susssasa{ss}i',
                          out_signature='u')
    def Notify(self, app_name, notification_id, app_icon,
               summary, body, actions, hints, expire_timeout):

        if not notification_id:
            self._id += 1
            notification_id = self._id

        print (f"""{summary}
{body}""")

        return notification_id

    @dbus.service.method("org.freedesktop.Notifications", in_signature='', out_signature='as')
    def GetCapabilities(self):
        return ("body")

    @dbus.service.signal('org.freedesktop.Notifications', signature='uu')
    def NotificationClosed(self, id_in, reason_in):
        pass

    @dbus.service.method("org.freedesktop.Notifications", in_signature='u', out_signature='')
    def CloseNotification(self, id):
        pass

    @dbus.service.method("org.freedesktop.Notifications", in_signature='', out_signature='ssss')
    def GetServerInformation(self):
      return ("notification-wsl", "http://www.arkane-systems.net/", "0.1.0", "1")

def entrypoint():
    DBusGMainLoop(set_as_default = True)

    session_bus = dbus.SessionBus()
    name = dbus.service.BusName("org.freedesktop.Notifications", session_bus)
    nw = NotificationWsl(session_bus, '/org/freedesktop/Notifications')

    context = GLib.MainLoop().get_context()

    while True:
        context.iteration(True)

entrypoint()

# import os
# import subprocess
# import sys
# import _thread
# import time
# from html.entities import name2codepoint as n2cp
# import re

# # ===== CONFIGURATION DEFAULTS =====
# #
# # See helpstring below for what each setting does

# DEFAULT_NOTIFY_TIMEOUT = 3000 # milliseconds
# MAX_NOTIFY_TIMEOUT = 5000 # milliseconds
# NOTIFICATION_MAX_LENGTH = 100 # number of characters
# STATUS_UPDATE_INTERVAL = 2.0 # seconds
# STATUS_COMMAND = ["/bin/sh", "%s/.statusline.sh" % os.getenv("HOME")]
# USE_STATUSTEXT=True
# QUEUE_NOTIFICATIONS=True

# # dwm
# def update_text(text):
#     # Get first line
#     first_line = text.splitlines()[0] if text else ''
#     subprocess.call(["xsetroot", "-name", first_line])

# # ===== CONFIGURATION END =====

# def _getconfigvalue(configmodule, name, default):
#     if hasattr(configmodule, name):
#         return getattr(configmodule, name)
#     return default

# def readconfig(filename):
#     import imp
#     try:
#         config = imp.load_source("config", filename)
#     except Exception as e:
#         print(f"Error: failed to read config file {filename}")
#         print(e)
#         sys.exit(2)

#     for setting in ("DEFAULT_NOTIFY_TIMEOUT", "MAX_NOTIFY_TIMEOUT", "NOTIFICATION_MAX_LENGTH", "STATUS_UPDATE_INTERVAL",
#                     "STATUS_COMMAND", "USE_STATUSTEXT", "QUEUE_NOTIFICATIONS", "update_text"):
#         if hasattr(config, setting):
#             globals()[setting] = getattr(config, setting)

# def strip_tags(value):
#   "Return the given HTML with all tags stripped."
#   return re.sub(r'<[^>]*?>', '', value)

# # from http://snipplr.com/view/19472/decode-html-entities/
# # also on http://snippets.dzone.com/posts/show/4569
# def substitute_entity(match):
#   ent = match.group(3)
#   if match.group(1) == "#":
#     if match.group(2) == '':
#       return unichr(int(ent))
#     elif match.group(2) == 'x':
#       return unichr(int('0x'+ent, 16))
#   else:
#     cp = n2cp.get(ent)
#     if cp:
#       return unichr(cp)
#     else:
#       return match.group()

# def decode_htmlentities(string):
#   entity_re = re.compile(r'&(#?)(x?)(\w+);')
#   return entity_re.subn(substitute_entity, string)[0]

# # List of not shown notifications.
# # Array of arrays: [id, text, timeout in s]
# # 0th element is being displayed right now, and may change
# # Replacements of notification happens att add
# # message_thread only checks first element for changes
# notification_queue = []
# notification_queue_lock = _thread.allocate_lock()

# def add_notification(notif):
#     with notification_queue_lock:
#         for index, n in enumerate(notification_queue):
#             if n[0] == notif[0]: # same id, replace instead of queue
#                 n[1:] = notif[1:]
#                 return

#         notification_queue.append(notif)

# def next_notification(pop = False):
#     # No need to be thread safe here. Also most common scenario
#     if not notification_queue:
#         return None

#     with notification_queue_lock:
#         if QUEUE_NOTIFICATIONS:
#             # If there are several pending messages, discard the first 0-timeouts
#             while len(notification_queue) > 1 and notification_queue[0][2] == 0:
#                 notification_queue.pop(0)
#         else:
#             while len(notification_queue) > 1:
#                 notification_queue.pop(0)

#         if pop:
#             return notification_queue.pop(0)
#         else:
#             return notification_queue[0]

# def get_statustext(notification = ''):
#     output = ''
#     try:
#         if not notification:
#             command = STATUS_COMMAND
#         else:
#             command = STATUS_COMMAND + [notification]

#         p = subprocess.Popen(command, stdout=subprocess.PIPE)

#         output = p.stdout.read()
#     except:
#         sys.stderr.write("%s: could not read status message (%s)\n"
#                          % (sys.argv[0], ' '.join(STATUS_COMMAND)))

#     # Error - STATUS_COMMAND didn't exist or delivered empty result
#     # Fallback to notification only
#     if not output:
#         output = notification

#     return output

# def message_thread(dummy):
#     last_status_update = 0
#     last_notification_update = 0
#     current_notification_text = ''

#     while 1:
#         notif = next_notification()
#         current_time = time.time()
#         update_status = False

#         if notif:
#             if notif[1] != current_notification_text:
#                 update_status = True

#             elif current_time > last_notification_update + notif[2]:
#                 # If requested timeout is zero, notification shows until
#                 # a new notification arrives or a regular status mesasge
#                 # cleans it
#                 # This way is a bit risky, but works. Keep an eye on this
#                 # when changing code
#                 if notif[2] != 0:
#                     update_status = True

#                 # Pop expired notification
#                 next_notification(True)
#                 notif = next_notification()

#             if update_status == True:
#                 last_notification_update = current_time

#         if current_time > last_status_update + STATUS_UPDATE_INTERVAL:
#             update_status = True

#         if update_status:
#             if notif:
#                 current_notification_text = notif[1]
#             else:
#                 current_notification_text = ''

#             if USE_STATUSTEXT:
#                 update_text(get_statustext(current_notification_text))
#             else:
#                 if current_notification_text != '':
#                     update_text(current_notification_text)

#             last_status_update = current_time

#         time.sleep(0.1)

# ------------------------------- CLASS -
#     _id = 0

#     @dbus.service.method("org.freedesktop.Notifications",
#                          in_signature='susssasa{ss}i',
#                          out_signature='u')
#     def Notify(self, app_name, notification_id, app_icon,
#                summary, body, actions, hints, expire_timeout):
#         if (expire_timeout < 0) or (expire_timeout > MAX_NOTIFY_TIMEOUT):
#             expire_timeout = DEFAULT_NOTIFY_TIMEOUT

#         if not notification_id:
#             self._id += 1
#             notification_id = self._id

#         text = (f"{summary} {body}").strip()
#         add_notification( [notification_id,
#                           text[:NOTIFICATION_MAX_LENGTH],
#                           int(expire_timeout) / 1000.0] )
#         return notification_id

# if __name__ == '__main__':
#     for curarg in sys.argv[1:]:
#         if curarg in ('-v', '--version'):
#             print(f"{sys.argv[0]} CURVERSION")
#             sys.exit(1)
#         elif curarg in ('-h', '--help'):
#             print(f"  Usage: {sys.argv[0]} [-h] [--help] [-v] [--version] [configuration file]\n"
#                    "    -h, --help:    Print this help and exit\n"
#                    "    -v, --version: Print version and exit\n"
#                    "\n"
#                    "  Configuration:\n"
#                    "    A file can be read to set the configuration.\n"
#                    "    This configuration file must be written in valid python,\n"
#                    "    which will be read if the filename is given on the command line.\n"
#                    "    You do only need to set the variables you want to change, and can\n"
#                    "    leave the rest out.\n"
#                    "\n"
#                    "    Below is an example of a configuration which sets the defaults.\n"
#                    "\n"
#                    "      # Default time a notification is show, unless specified in notification\n"
#                    "      DEFAULT_NOTIFY_TIMEOUT = 3000 # milliseconds\n"
#                    "      \n"
#                    "      # Maximum time a notification is allowed to show\n"
#                    "      MAX_NOTIFY_TIMEOUT = 5000 # milliseconds\n"
#                    "      \n"
#                    "      # Maximum number of characters in a notification.\n"
#                    "      NOTIFICATION_MAX_LENGTH = 100 # number of characters\n"
#                    "      \n"
#                    "      # Time between regular status updates\n"
#                    "      STATUS_UPDATE_INTERVAL = 2.0 # seconds\n"
#                    "      \n"
#                    "      # Command to fetch status text from. We read from stdout.\n"
#                    "      # Each argument must be an element in the array\n"
#                    "      # os must be imported to use os.getenv\n"
#                    "      import os\n"
#                    "      STATUS_COMMAND = ['/bin/sh', '%s/.statusline.sh' % os.getenv('HOME')]\n"
#                    "\n"
#                    "      # Always show text from STATUS_COMMAND? If false, only show notifications\n"
#                    "      USE_STATUSTEXT=True\n"
#                    "      \n"
#                    "      # Put incoming notifications in a queue, so each one is shown.\n"
#                    "      # If false, the most recent notification is shown directly.\n"
#                    "      QUEUE_NOTIFICATIONS=True\n"
#                    "      \n"
#                    "      # update_text(text) is called when the status text should be updated\n"
#                    "      # If there is a pending notification to be formatted, it is appended as\n"
#                    "      # the final argument to the STATUS_COMMAND, e.g. as $1 in default shellscript\n"
#                    "\n"
#                    "      # dwm statusbar update\n"
#                    "      import subprocess\n"
#                    "      def update_text(text):\n"
#                    "          subprocess.call(['xsetroot', '-name', text])\n")
#             sys.exit(1)
#         else:
#             readconfig(curarg)

# --------------------

#     # We must use contexts and iterations to run threads
#     # http://www.jejik.com/articles/2007/01/python-gstreamer_threading_and_the_main_loop/
#     # Calling threads_init is not longer needed
#     # https://wiki.gnome.org/PyGObject/Threading
#     #GLib.threads_init()
#     _thread.start_new_thread(message_thread, (None,))
