# openESHER - an open source Experimental System for Human-guided Engineering and Reasoning
# 
# Copyright (C) 2026 Robert Rohm
# 
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your option) 
# any later version. This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY 
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more 
# details. 
# 
# You should have received a copy of the GNU General Public License along with 
# this program. If not, see <http://www.gnu.org/licenses/>.


from pathlib import Path
import ollama
import subprocess

#MODEL = "qwen3:8b"
#MODEL = "devstral:latest"
#MODEL = "gemma4:latest"
MODEL = "gemma4:e4b"
PROJECT_ROOT = Path.cwd().resolve()
MAX_CHARS = 20_000
PAGE_SIZE = 40


def safe_path(path: str = ".") -> Path:
    """Resolve a project-relative path and reject paths outside the project."""
    candidate = (PROJECT_ROOT / path).resolve()

    try:
        candidate.relative_to(PROJECT_ROOT)
    except ValueError:
        raise ValueError("Path is outside the project directory.")

    return candidate


def create_file(file_path, content):
    """
    Writes content to a file after confirming with the user and ensuring the path is safe.

    :param file_path: The path to the file.
    :param content: The content to write to the file.
    """
    safe_file_path = safe_path(file_path)

    if safe_file_path.exists():
        raise ValueError("File already exists.")

    confirmation = input(f"Are you sure you want to write to {safe_file_path}? (yes/no): ").strip().lower()
    if confirmation == 'yes':
        with open(safe_file_path, 'w') as file:
            file.write(content)
        print(f"Content written to {safe_file_path}.")
    else:
        print("Operation cancelled by the user.")


def ls(path: str = ".") -> str:
    """List names in a project directory. Path is relative to the project root."""
    directory = safe_path(path)

    if not directory.is_dir():
        raise ValueError("Not a directory.")

    entries = []
    for item in sorted(directory.iterdir(), key=lambda p: p.name.lower()):
        kind = "dir" if item.is_dir() else "file"
        entries.append(f"{kind:4} {item.name}")

    return "\n".join(entries) or "(empty directory)"


def read_lines(path: str) -> list[str]:
    """Read a UTF-8 text file within the project directory."""
    file_path = safe_path(path)

    if not file_path.is_file():
        raise ValueError("Not a file.")

    return file_path.read_text(encoding="utf-8").splitlines()


def cat(path: str) -> str:
    """Read a text file. Output is capped to avoid huge responses."""
    text = "\n".join(read_lines(path))
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS] + "\n...[output truncated]"
    return text

def git_status() -> str:
    """Get Git status for the project directory."""
    try:
        # Run git status in the project root
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Git error: {e.stderr}"
    except FileNotFoundError:
        return "Git not found in PATH - ensure Git is installed and accessible"


def head(path: str, n: int = 10) -> str:
    """Show the first n lines of a project text file."""
    if not 1 <= n <= 200:
        raise ValueError("n must be between 1 and 200.")
    return "\n".join(read_lines(path)[:n])


def tail(path: str, n: int = 10) -> str:
    """Show the last n lines of a project text file."""
    if not 1 <= n <= 200:
        raise ValueError("n must be between 1 and 200.")
    return "\n".join(read_lines(path)[-n:])


def more(path: str, start_line: int = 1, n: int = PAGE_SIZE) -> str:
    """Show n lines starting at the 1-based line number start_line."""
    if start_line < 1 or not 1 <= n <= 200:
        raise ValueError("start_line must be >= 1 and n must be between 1 and 200.")

    lines = read_lines(path)
    start = start_line - 1
    page = lines[start : start + n]

    if not page:
        return "(no lines at that position)"

    numbered = [
        f"{line_no}: {line}"
        for line_no, line in enumerate(page, start=start_line)
    ]
    return "\n".join(numbered)

def main():
    TOOLS = [ls, cat, head, tail, more, git_status, create_file]
    FUNCTIONS = {fn.__name__: fn for fn in TOOLS}

    messages = [
        {
            "role": "system",
            "content": (
                f"You are a coding assistant. The project root is {PROJECT_ROOT}. "
                "Use the provided read-only tools when you need to inspect project files. "
                "Paths must be relative to the project root. Never claim to have read a file "
                "unless a tool returned its contents. "
                "Use the provided git_status tool for showing the git status of the project. "
                "Use the provided create_file tool to create new files and write text content into the new file."
            ),
        }
    ]

    print(f"Project root: {PROJECT_ROOT}")
    print("Type /quit to exit or /reset to clear the conversation.")

    while True:
        try:
            prompt = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if prompt.lower() in {"/quit", "/exit"}:
            break
        if prompt.lower() == "/reset":
            messages = messages[:1]
            print("Conversation cleared.")
            continue
        if not prompt:
            continue

        messages.append({"role": "user", "content": prompt})

        try:
            # A model can request a tool, receive its result, and then request
            # another tool. Limit rounds so the loop can't run indefinitely.
            for _ in range(8):
                response = ollama.chat(
                    model=MODEL,
                    messages=messages,
                    tools=TOOLS
                )

                messages.append(response.message)
                calls = response.message.tool_calls or []

                if not calls:
                    print(f"\nAssistant: {response.message.content}")
                    break

                for call in calls:
                    name = call.function.name
                    args = call.function.arguments or {}
                    function = FUNCTIONS.get(name)

                    if function is None:
                        result = f"Error: tool {name!r} is not available."
                    else:
                        try:
                            result = str(function(**args))
                        except Exception as exc:
                            result = f"Tool error: {exc}"

                    # Send the tool result back so the model can use it.
                    messages.append({
                        "role": "tool",
                        "tool_name": name,
                        "content": result,
                    })
            else:
                print("\nStopped after too many tool-call rounds.")

        except ollama.ResponseError as exc:
            print(f"\nOllama error: {exc.error}")
        except Exception as exc:
            print(f"\nCould not reach Ollama: {exc}")

if __name__ == "__main__":
    main()