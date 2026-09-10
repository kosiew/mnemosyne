# Plugin development checklist

What to do each time you modify an existing plugin or create a new one.

## 1. Edit in the repo

Work on `mnemosyne/example_plugins/<name>.py`. That is the copy under version
control.

## 2. Copy to the live plugin directory

Nothing takes effect until the file is in the directory the running application
actually imports from:

```sh
cp mnemosyne/example_plugins/<name>.py \
   ~/Library/CloudStorage/OneDrive-Personal/Library/Mnemosyne/plugins/
```

Diff first if the installed copy might have drifted:

```sh
diff mnemosyne/example_plugins/<name>.py \
     ~/Library/CloudStorage/OneDrive-Personal/Library/Mnemosyne/plugins/<name>.py
```

The plugin directory is `<data_dir>/plugins`, resolved at startup by
`execute_user_plugin_dir()` in `mnemosyne/libmnemosyne/__init__.py`. The repo's
own `dot_mnemosyne2/plugins/` is empty and is not what the application uses.

## 3. Restart Mnemosyne

Plugins are imported once at startup. There is no reload.

## 4. For a new plugin, also enable it

Mnemosyne only activates what is listed in the `active_plugins` key of
`config.db` in the data directory. Either:

- tick it in Configure -> Plugins (the choice is persisted), or
- self-activate at import time, the way `random_future_revision.py` does:

  ```python
  plugin = register_user_plugin(MyPlugin)
  plugin.activate()
  ```

Plain `register_user_plugin(MyPlugin)` — what `grade_button_interval_tooltips.py`
does — only makes the plugin *available*, not active.

## 5. If the plugin replaces a GUI component

Declare it in `gui_for_component` for every study mode it should apply to —
`ScheduledForgottenNew`, `NewOnly`, `CramAll`, `CramRecent` — and set
`supported_API_level = 3`.

## 6. Tests

Keep display and formatting logic in module-level pure functions so
`tests/test_*.py` can import and exercise them without Qt. See
`tests/test_grade_button_interval_tooltips.py` for the import dance needed to
load a plugin module without a real component manager.

## Gotchas

- Import errors in a plugin are caught and turned into an error dialog, so a
  typo simply makes the plugin silently absent rather than crashing the app.
- The live plugin directory lives inside OneDrive, so give sync a moment to
  settle before restarting.
