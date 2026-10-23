"""Save a report as a project file."""

from typing import Any, Dict

from ncp import Files, tool
from ncp.data.files import FileUploadError


@tool
def save_report(name: str, content: str, scope: str = "project") -> Dict[str, Any]:
    """Save a text report as a file the user can open in the Files page.

    Args:
        name: File name with its extension, e.g. "bgp-findings.md".
        content: The report text.
        scope: "project" (the current project, any member) or "system" (the whole
            organization; admins only).

    Returns:
        Dictionary with the saved file's `ref`, `filename` and `status`, or `error`
        and `code` when the platform refused the upload (for example `forbidden`).
    """
    files = Files()
    try:
        row = files.upload(name, content.encode("utf-8"), scope=scope)
    except FileUploadError as err:
        return {"error": err.message, "code": err.code}
    status = files.wait_ready(row, timeout=30)
    return {"ref": row["ref"], "filename": row["filename"], "status": status}
