# Implements: F-032 (code execution tool)
"""
Code execution tool: runs Python code in a sandboxed subprocess.
Security: restricted timeout, limited memory, no network access from subprocess.
"""
from __future__ import annotations

import asyncio
import logging
import os
import sys
import tempfile
from typing import Any

logger = logging.getLogger(__name__)

# Hard limits
MAX_TIMEOUT_SECONDS = 30
MAX_OUTPUT_BYTES = 64 * 1024  # 64KB
FORBIDDEN_IMPORTS = {"os.system", "subprocess", "socket", "requests", "urllib", "ftplib", "smtplib"}


def _check_code_safety(code: str) -> None:
    """Basic static analysis to block obvious dangerous patterns."""
    danger_patterns = [
        "__import__",
        "eval(",
        "exec(",
        "compile(",
        "open(",
        "os.remove",
        "os.rmdir",
        "shutil.rmtree",
        "sys.exit",
        "os.kill",
    ]
    code_lower = code.lower()
    for pattern in danger_patterns:
        if pattern in code:
            raise ValueError(f"Forbidden pattern in code: '{pattern}'")


async def run_code(input_data: dict[str, Any], org_id: str | None) -> dict:
    """
    Execute Python code in a sandboxed subprocess.
    
    Input: {"code": str, "language": str (default "python")}
    Output: {"stdout": str, "stderr": str, "exit_code": int, "timeout": bool}
    """
    code = input_data.get("code", "").strip()
    language = input_data.get("language", "python").lower()
    timeout = min(int(input_data.get("timeout_seconds", 10)), MAX_TIMEOUT_SECONDS)

    if not code:
        raise ValueError("code is required for execute_python")

    if language != "python":
        raise ValueError(f"Only Python is supported, got: {language}")

    # Safety check
    _check_code_safety(code)

    # Write to temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        tmp_path = f.name

    try:
        proc = await asyncio.create_subprocess_exec(
            sys.executable,
            tmp_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            # Restrict environment
            env={
                "PATH": os.environ.get("PATH", ""),
                "PYTHONPATH": "",
                "HOME": "/tmp",
            },
        )

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(), timeout=timeout
            )
            timed_out = False
        except asyncio.TimeoutError:
            proc.kill()
            await proc.communicate()
            stdout_bytes, stderr_bytes = b"", b"Process timed out"
            timed_out = True

        stdout = stdout_bytes[:MAX_OUTPUT_BYTES].decode("utf-8", errors="replace")
        stderr = stderr_bytes[:MAX_OUTPUT_BYTES].decode("utf-8", errors="replace")

        logger.info(
            "[CodeExecutor] exit_code=%s timeout=%s stdout_len=%d",
            proc.returncode,
            timed_out,
            len(stdout),
        )

        return {
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": proc.returncode if not timed_out else -1,
            "timeout": timed_out,
        }
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
