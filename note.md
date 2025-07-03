# 🛠️ KemonoDownloader Refactor Notes

## What's Going On

This project used to be one giant messy App Script. It worked, but it was hard to maintain or expand. So I cleaned it up and split everything into smaller, more manageable files to make it easier to read, update, and add new stuff later.

**⚠️ Heads up:** Since I'm still in the middle of refactoring things, some features might be broken or not working right now. The layout is better, but I still need to update some parts of the logic and dependencies.

---

## 📁 Folder Layout

```
KemonoDownloader/
├── main.py                      # Where the app starts
├── requirements.txt             # List of Python libraries used
├── assets/                      # Icons and other static files
│   └── Kemono.ico
├── data/                        # Stuff that gets saved (user config, cookies, etc.)
│   └── creators.json
├── logs/                        # Error logs and other output
│   └── uncaught_exceptions.log
└── src/                         # Main code lives here
    ├── __init__.py
    ├── ui/                      # UI-related code
    │   ├── __init__.py
    │   ├── main_window.py
    │   └── dialogs/
    │       ├── __init__.py
    │       ├── ConfirmAddAllDialog.py
    │       ├── CookieHelpDialog.py
    │       ├── DownloadExtractedLinksDialog.py
    │       ├── DownloadFinishedDialog.py
    │       └── ... (more dialogs)
    ├── core/                    # The brain of the app
    │   ├── __init__.py
    │   ├── manager.py
    │   ├── workers.py
    │   └── api_client.py
    ├── services/                # Downloading stuff happens here
    │   ├── __init__.py
    │   ├── drive_downloader.py
    │   └── multipart_downloader.py
    ├── utils/                   # Helper functions
    │   ├── __init__.py
    │   ├── file_utils.py
    │   ├── network_utils.py
    │   └── text_utils.py
    ├── config/                  # Constants and settings
    │   ├── __init__.py
    │   └── constants.py
    └── i18n/                    # Translations (if needed)
        ├── __init__.py
        └── translator.py
```

---

## ✅ Why Bother Refactoring?

- Everything’s now broken into smaller parts, so it’s easier to work with.
- Easier to test, fix, and add stuff.
- Prepping the project to grow without becoming a mess again.
- Separated the UI from the app logic so they don’t get tangled.

---

## 🚧 What’s Still Broken

- Some features don’t work yet or haven’t been tested since the changes.
- Still need to:
  - Reconnect the UI to the updated logic.
  - Move over some of the old script code into proper modules.
  - Make sure settings and cookies work properly in the new setup.

---

## 📌 To-Do List

- Test all the dialogs and UI stuff.
- Make sure the download services and API calls are working.
- Reconnect the UI with the new logic in `core/manager.py`.
- Add more logging and maybe some unit tests too.

---

## 🐞 Found a Bug?

If something's busted:

- Feel free to open an issue if you're using this.
- Or just message me. Feedback helps a lot while I’m still figuring things out.

Thanks for checking it out! Still a work in progress, but getting there.
