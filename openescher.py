from pathlib import Path
import ollama

MODEL = "qwen3:8b"
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


TOOLS = [ls, cat, head, tail, more]
FUNCTIONS = {fn.__name__: fn for fn in TOOLS}

messages = [
    {
        "role": "system",
        "content": (
            f"You are a coding assistant. The project root is {PROJECT_ROOT}. "
            "Use the provided read-only tools when you need to inspect project files. "
            "Paths must be relative to the project root. Never claim to have read a file "
            "unless a tool returned its contents."
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
                tools=TOOLS,
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
