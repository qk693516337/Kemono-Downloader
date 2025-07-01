# 🛠️ KemonoDownloader Refactor Notes

## Overview

The project was previously a large monolithic App Script, which made it difficult to maintain and scale. This version introduces a cleaner and more modular file structure to improve readability, separation of concerns, and future extensibility.

**⚠️ Note:** Due to the ongoing refactor, some features may not work as expected. The code has been reorganized into a more maintainable layout, but certain logic or dependencies might still require updates to fully function in this new structure.

---

## 📁 Project Structure

```plaintext
KemonoDownloader/
├── main.py                      # Entry point of the application
├── requirements.txt             # Python dependencies
├── assets/                      # Static files like icons
│   └── Kemono.ico
├── data/                        # Persistent user data and config
│   ├── creators.json
│   ├── Known.txt
│   └── cookies.txt
├── logs/                        # Logging output
│   └── uncaught_exceptions.log
└── src/                         # Main application source code
    ├── __init__.py
    ├── ui/                      # UI components
    │   ├── __init__.py
    │   ├── main_window.py
    │   └── dialogs/
    │       ├── __init__.py
    │       ├── ConfirmAddAllDialog.py
    │       ├── CookieHelpDialog.py
    │       ├── DownloadExtractedLinksDialog.py
    │       ├── DownloadFinishedDialog.py
    │       └── ... (other dialogs)
    ├── core/                    # Core logic and app engine
    │   ├── __init__.py
    │   ├── manager.py
    │   ├── workers.py
    │   └── api_client.py
    ├── services/                # Download services and tools
    │   ├── __init__.py
    │   ├── drive_downloader.py
    │   └── multipart_downloader.py
    ├── utils/                   # Utility/helper functions
    │   ├── __init__.py
    │   ├── file_utils.py
    │   ├── network_utils.py
    │   └── text_utils.py
    ├── config/                  # Configuration and constants
    │   ├── __init__.py
    │   └── constants.py
    └── i18n/                    # Internationalization (translation)
        ├── __init__.py
        └── translator.py
```

---

## ✅ Goals of This Refactor

- Improve **modularity** and make each component responsible for a specific domain.
- Enable easier **testing**, debugging, and maintenance.
- Prepare the codebase for future **feature expansion**.
- Make UI and business logic **loosely coupled**.

---

## 🚧 Known Issues

- Some features are currently broken or untested in this structure.
- Further work is required to:
  - Hook up UI components with new logic paths.
  - Validate and migrate old script logic into proper services/core modules.
  - Ensure settings and cookies persist correctly through the new configuration and data layers.

---

## 📌 Next Steps

- Review and test all dialogs and UI flows.
- Validate downloader services and API integrations.
- Reconnect UI with backend logic through the `core/manager.py`.
- Add unit tests and logging as needed.

---

## 📣 Found a Bug or Issue?

If you find something broken or not working as expected:

- **Open an issue** on the repository so it can be tracked.
- Or **let me know directly** — feedback is super helpful during this refactor!

Thanks for your patience and support during this restructuring!
