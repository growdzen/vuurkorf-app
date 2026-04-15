"""
Shared in-memory stores for upload data and job state.
Keeps uploaded file bytes in memory so upload and process
always share the same data within a single Render instance.
"""

# file_store: job_id -> (bytes, extension)
file_store: dict[str, tuple[bytes, str]] = {}
