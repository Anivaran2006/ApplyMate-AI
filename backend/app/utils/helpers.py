"""
ApplyMate AI – General Helper Utilities
"""

import csv
import io
from datetime import datetime, timezone
from typing import Any, Dict, List


def utcnow() -> datetime:
    """Return timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def paginate(query_result: list, page: int, page_size: int) -> Dict[str, Any]:
    """Compute pagination metadata for a list."""
    total = len(query_result)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "items": query_result[start:end],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


def generate_csv(rows: List[Dict], fieldnames: List[str]) -> str:
    """Generate a CSV string from a list of dicts."""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def truncate(text: str, max_len: int = 100) -> str:
    """Truncate text with ellipsis."""
    if not text:
        return ""
    return text if len(text) <= max_len else text[:max_len - 3] + "..."
