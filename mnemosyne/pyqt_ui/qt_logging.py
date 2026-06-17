import os


_QT_POINTER_DISPATCH_RULE = "qt.pointer.dispatch=false"
_QT_POINTER_DISPATCH_CATEGORY = "qt.pointer.dispatch"


def suppress_spurious_qt_pointer_dispatch_logs():
    """Hide noisy Qt pointer-dispatch warnings with no target window.

    Must run before Qt initialises logging.
    """
    rules = os.environ.get("QT_LOGGING_RULES", "")
    existing_rules = [rule.strip() for rule in rules.split(";") if rule.strip()]

    if any(rule.startswith(_QT_POINTER_DISPATCH_CATEGORY) for rule in existing_rules):
        return

    existing_rules.append(_QT_POINTER_DISPATCH_RULE)
    os.environ["QT_LOGGING_RULES"] = ";".join(existing_rules)
