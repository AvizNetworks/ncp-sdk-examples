"""File access tools for file-agent."""

from typing import Any, Dict, List, Optional
from ncp import tool, Files


@tool
def list_all_files(file_type: Optional[str] = None) -> Dict[str, Any]:
    """List all files accessible to this agent — both project files and admin files.

    Project files are scoped to the current project. Admin files are organization-wide
    and accessible to all agents. Each result includes a 'source' field indicating
    whether the file is from 'project' or 'admin'.

    Args:
        file_type: Optional MIME type to filter by (e.g. "text/csv", "application/json").

    Returns:
        Dictionary with:
        - project_files: files belonging to the current project
        - admin_files: organization-wide admin files
        - total_count: total number of accessible files
        - has_project_context: whether a project context is active
    """
    files = Files()
    project = files.list_project_files(file_type=file_type)
    admin = files.list_admin_files(file_type=file_type)
    return {
        "project_files": project,
        "admin_files": admin,
        "total_count": len(project) + len(admin),
        "has_project_context": len(project) > 0 or file_type is not None,
    }


@tool
def read_file_by_name(filename: str, source: str = "auto") -> Dict[str, Any]:
    """Read the full content of a file by its filename.

    Searches project files first (if in a project context), then admin files.
    Use source='project' or source='admin' to restrict which scope is searched.

    Args:
        filename: Exact filename to look up (e.g. "config.csv", "policy.txt").
        source: Where to search — 'auto' (project first, then admin), 'project', or 'admin'.

    Returns:
        Dictionary with:
        - filename: the file name
        - source: where it was found ('project' or 'admin')
        - content: the file content as a string
        - error: present if the file could not be found or read
    """
    files = Files()

    # Determine which scope to search
    found_in = None
    file_info = None

    if source in ("auto", "project"):
        for f in files.list_project_files():
            if f["filename"] == filename:
                found_in = "project"
                file_info = f
                break

    if found_in is None and source in ("auto", "admin"):
        for f in files.list_admin_files():
            if f["filename"] == filename:
                found_in = "admin"
                file_info = f
                break

    if file_info is None:
        return {
            "filename": filename,
            "error": f"File '{filename}' not found in accessible {source} files.",
        }

    content = files.read_file(file_info["file_id"], source=found_in)
    return {
        "filename": filename,
        "source": found_in,
        "file_id": file_info["file_id"],
        "file_type": file_info.get("file_type"),
        "file_size_bytes": file_info.get("file_size_bytes"),
        "content": content,
    }


@tool
def read_file_by_id(file_id: int, source: str = "project") -> Dict[str, Any]:
    """Read the content of a file using its numeric file ID.

    Use list_all_files first to discover file IDs.

    Args:
        file_id: The numeric file ID from list_all_files results.
        source: Scope the file belongs to — 'project' or 'admin'.

    Returns:
        Dictionary with:
        - file_id: the file ID
        - filename: the file name
        - source: scope used
        - content: the file content as a string
        - error: present if the file could not be found or read
    """
    files = Files()
    info = files.get_file_info(file_id, source=source)
    if "error" in info:
        return {"file_id": file_id, "source": source, "error": info["error"]}

    content = files.read_file(file_id, source=source)
    return {
        "file_id": file_id,
        "filename": info.get("filename"),
        "source": source,
        "file_type": info.get("file_type"),
        "file_size_bytes": info.get("file_size_bytes"),
        "content": content,
    }


@tool
def get_file_info(file_id: int, source: str = "project") -> Dict[str, Any]:
    """Get metadata for a file without reading its content.

    Useful for checking file size, type, and upload time before reading.

    Args:
        file_id: The numeric file ID.
        source: Scope the file belongs to — 'project' or 'admin'.

    Returns:
        Dictionary with file metadata: file_id, filename, file_type,
        file_size_bytes, uploaded_at, uploader_username, source.
        Contains 'error' key if file is not found.
    """
    files = Files()
    return files.get_file_info(file_id, source=source)
