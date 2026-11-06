"""Unattended card run: let a local Ollama model implement the S-cards one after another.

For every card in docs/plan/phase-*.md (in dependency order) the script

1. branches ``card/<ID>`` off the run branch (default ``ollama-card-run``, created from
   ``master`` on the first start),
2. starts Aider with the card text; only the card's target files are editable, the
   context files are read-only,
3. runs ruff and the card's verification command; on red it hands the error output back
   to Aider (up to ``--versuche`` attempts),
4. on green commits on the card branch and merges it into the run branch (``--no-ff``),
   on failure resets the card's changes, notes the card and skips cards that depend on it.

Progress lives in ``tasks/kartenlauf/stand.json`` (the run resumes where it stopped), the
report in ``tasks/kartenlauf/bericht.md`` and one log per attempt in
``tasks/kartenlauf/logs/``. The folder is kept out of git via ``.git/info/exclude``.

Nothing is pushed. Start (from the project folder):

    uv run python tools/kartenlauf.py --max 3          # trial run with the next 3 cards
    uv run python tools/kartenlauf.py --bis 17:00      # stop starting new cards at 17:00
    uv run python tools/kartenlauf.py --trocken        # only print the order
"""

from __future__ import annotations

import argparse
import ast
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "plan"
WORK = ROOT / "tasks" / "kartenlauf"
STATE_FILE = WORK / "stand.json"
REPORT_FILE = WORK / "bericht.md"
LOG_DIR = WORK / "logs"
MODEL_SETTINGS = ROOT / "tools" / "kartenlauf.model-settings.yml"

# Never touched by the run (project rules).
PROTECTED = ("CHANGELOG.md", "pyproject.toml", "uv.lock", "native/", "tests/spec/", "docs/")

CARD_HEADER = re.compile(r"^## ([A-G]\d\d) — (.+)$", re.MULTILINE)
CARD_ID = re.compile(r"`([A-G]\d\d)`(?:\s*–\s*`([A-G]\d\d)`)?")
BACKTICK = re.compile(r"`([^`]+)`")
CONTEXT_ITEM = re.compile(r"`([^`]+)`(?:\s*\(((?:[^()]|\([^()]*\))*)\))?")
CONTRACT_ID = re.compile(r"V(\d+)([a-z]?)(?:\s*[–-]\s*`?V(\d+)`?)?")
HEADING = re.compile(r"^(#{1,4}) (.+)$", re.MULTILINE)
SMALL_SOURCE = 20_000  # bytes; larger read-only sources are passed as an outline
CHARS_PER_TOKEN = 3.3

PROMPT = """You are implementing exactly one task card of the game project py-noita-claude
(Python, pygame-ce). Follow the card literally.

Rules:
- Edit only these files: {targets}. Create them if they do not exist.
- The read-only files are your context. Never change tests in tests/spec/.
- Code, names and comments in English; every text the player sees in German.
- Keep existing behaviour working; prefer small, focused changes.
- Placeholders that raise NotImplementedError("Card {key}") belong to this card: replace
  their body in place. Never write a second definition of a function, class or constant
  that already exists in the file; change the existing one.
- Add every import you use.
- The card is done when this command passes: {verify}
{stubs}
Card:

{card}
"""

RETRY = """The verification failed. Fix the code (only in {targets}) so it passes.
Command: {verify}
Edit the existing definitions; do not add duplicates. Remove any duplicate you created.

Output (shortened):

{output}
"""


# --------------------------------------------------------------------------- cards


@dataclass
class Card:
    key: str
    title: str
    text: str
    deps: list[str]
    targets: list[str]
    context: list[str]
    verify: str
    hints: dict[str, str] = field(default_factory=dict)  # context path -> "(…)" hint
    order: int = 0


def _field(text: str, name: str) -> str:
    match = re.search(rf"^- \*\*{name}:\*\*(.*)$", text, re.MULTILINE)
    return match.group(1).strip() if match else ""


def _expand(spec: str) -> list[str]:
    keys: list[str] = []
    for first, last in CARD_ID.findall(spec):
        if last and first[0] == last[0]:
            keys += [f"{first[0]}{n:02d}" for n in range(int(first[1:]), int(last[1:]) + 1)]
        else:
            keys.append(first)
    return keys


def _paths(spec: str) -> list[str]:
    out = []
    for token in BACKTICK.findall(spec):
        token = token.strip()
        if "/" in token and not token.startswith("-") and " " not in token:
            out.append(token)
    return out


def load_cards() -> dict[str, Card]:
    cards: dict[str, Card] = {}
    for path in sorted(PLAN.glob("phase-*.md")):
        source = path.read_text(encoding="utf-8")
        heads = list(CARD_HEADER.finditer(source))
        for i, head in enumerate(heads):
            end = heads[i + 1].start() if i + 1 < len(heads) else len(source)
            text = source[head.start() : end].split("\n---", 1)[0].strip()
            verify = BACKTICK.findall(_field(text, "Verifikation"))
            hints = {
                path: hint
                for path, hint in CONTEXT_ITEM.findall(_field(text, "Zu lesender Kontext"))
                if "/" in path and " " not in path and (ROOT / path).is_file()
            }
            context = list(hints)
            cards[head.group(1)] = Card(
                key=head.group(1),
                title=head.group(2).strip(),
                text=text,
                deps=_expand(_field(text, "Abhängigkeiten")),
                targets=_paths(_field(text, "Ziel-Dateien")),
                context=context,
                verify=verify[0] if verify else "",
                hints=hints,
            )
    return cards


def topo_order(cards: dict[str, Card]) -> list[Card]:
    """Dependencies first; among ready cards the plan order (phase letter, number)."""
    done: set[str] = set()
    pending = sorted(cards)
    ordered: list[Card] = []
    while pending:
        ready = [k for k in pending if all(d in done or d not in cards for d in cards[k].deps)]
        if not ready:
            raise SystemExit(f"Kreis in den Abhängigkeiten: {pending}")
        key = ready[0]
        pending.remove(key)
        done.add(key)
        cards[key].order = len(ordered)
        ordered.append(cards[key])
    return ordered


# --------------------------------------------------------------------------- helpers


# The project's post-commit hook asks interactively for a SemVer bump (reading the
# console) and amends CHANGELOG.md; the card run must neither block nor touch the
# changelog, so it sets the hook's own skip flag and never hands out the console.
GIT_ENV = {**os.environ, "GIT_CHANGELOG_RUNNING": "1"}


def run(
    cmd: list[str] | str, *, timeout: float | None = None, check: bool = False
) -> tuple[int, str]:
    proc = subprocess.run(
        cmd,
        check=False,
        cwd=ROOT,
        env=GIT_ENV,
        stdin=subprocess.DEVNULL,
        shell=isinstance(cmd, str),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    output = (proc.stdout or "") + (proc.stderr or "")
    if check and proc.returncode != 0:
        raise SystemExit(f"Befehl fehlgeschlagen: {cmd}\n{output}")
    return proc.returncode, output


def git(*args: str, check: bool = True) -> str:
    return run(["git", *args], check=check)[1].strip()


def changed_files() -> set[str]:
    """Tracked files with changes plus untracked files (paths relative to ROOT)."""
    out = run(["git", "status", "--porcelain", "--untracked-files=all"], check=True)[1]
    return {line[3:].strip().strip('"') for line in out.splitlines() if len(line) > 3}


def keep_awake(on: bool) -> None:
    """Windows: keep the computer from sleeping while the run is active."""
    if os.name != "nt":
        return
    import ctypes

    es_continuous, es_system_required = 0x80000000, 0x00000001
    flags = es_continuous | (es_system_required if on else 0)
    ctypes.windll.kernel32.SetThreadExecutionState(flags)


def now() -> dt.datetime:
    return dt.datetime.now().astimezone()


def shorten(text: str, limit: int = 6000) -> str:
    return text if len(text) <= limit else text[:1500] + "\n…\n" + text[-(limit - 1500) :]


# --------------------------------------------------------------------------- state


@dataclass
class State:
    cards: dict[str, dict] = field(default_factory=dict)

    @classmethod
    def load(cls) -> State:
        if STATE_FILE.is_file():
            return cls(json.loads(STATE_FILE.read_text(encoding="utf-8")))
        return cls()

    def save(self) -> None:
        STATE_FILE.write_text(json.dumps(self.cards, indent=2, ensure_ascii=False), "utf-8")

    def status(self, key: str) -> str:
        return self.cards.get(key, {}).get("status", "")


def write_report(state: State, ordered: list[Card]) -> None:
    counts: dict[str, int] = {}
    rows = []
    for card in ordered:
        entry = state.cards.get(card.key)
        if not entry:
            continue
        counts[entry["status"]] = counts.get(entry["status"], 0) + 1
        minutes = entry.get("seconds", 0) / 60
        note = entry.get("note", "").replace("|", "/").replace("\n", " ")[:160]
        rows.append(
            f"| `{card.key}` | {entry['status']} | {entry.get('attempts', 0)} | {minutes:.1f} | {note} |"
        )
    summary = ", ".join(f"{k}: {v}" for k, v in sorted(counts.items()))
    REPORT_FILE.write_text(
        "# Kartenlauf-Bericht\n\n"
        f"Stand: {now():%Y-%m-%d %H:%M} · {summary} · offen: "
        f"{len(ordered) - sum(counts.values())}\n\n"
        "| Karte | Status | Versuche | Minuten | Hinweis |\n| --- | --- | --- | --- | --- |\n"
        + "\n".join(rows)
        + "\n",
        encoding="utf-8",
    )


# --------------------------------------------------------------------------- one card


def verify(card: Card) -> tuple[bool, str]:
    outputs = []
    py_targets = [t for t in card.targets if t.endswith(".py") and (ROOT / t).is_file()]
    if py_targets:
        # Safe automatic fixes first (imports, sorting, formatting); then the real check.
        run(["uv", "run", "ruff", "check", "--fix", *py_targets], timeout=300)
        run(["uv", "run", "ruff", "format", *py_targets], timeout=300)
        code, out = run(["uv", "run", "ruff", "check", *py_targets], timeout=300)
        outputs.append(out)
        if code != 0:
            return False, "\n".join(outputs)
    code, out = run(card.verify, timeout=1800)
    outputs.append(out)
    return code == 0, "\n".join(outputs)


def revert_outside(card: Card, before: set[str]) -> list[str]:
    """Undo every change Aider made outside the card's target files."""
    reverted = []
    for path in sorted(changed_files() - before):
        if "tools/kartenlauf." in path:  # the run's own files may be updated meanwhile
            continue
        allowed = any(path == t or path.startswith(t.rstrip("/") + "/") for t in card.targets)
        protected = any(path == p or path.startswith(p) for p in PROTECTED)
        if allowed and not protected:
            continue
        reverted.append(path)
        restore(path)
    return reverted


def restore(path: str) -> None:
    """Put ``path`` back to its state in HEAD; delete it if HEAD does not know it.

    Aider stages files it creates (even with --no-auto-commits), so a new file can be in
    the index without being in HEAD. Errors are logged, never fatal for the run.
    """
    run(["git", "reset", "-q", "HEAD", "--", path])
    try:
        if run(["git", "cat-file", "-e", f"HEAD:{path}"])[0] == 0:
            run(["git", "checkout", "HEAD", "--", path])
        else:
            (ROOT / path).unlink(missing_ok=True)
    except OSError as error:
        print(f"    Konnte {path} nicht zurücksetzen: {error}", flush=True)


def reset_card(before: set[str]) -> None:
    """Undo what this card changed; earlier uncommitted changes (e.g. the script) stay."""
    for path in changed_files() - before:
        if "tools/kartenlauf." in path:
            continue
        restore(path)


# --------------------------------------------------------------------------- context
#
# A small local model has a small context window. Instead of whole files the run sends
# only what the card points at: the card's own test functions, the contract sections
# it names (`V0b`, „Phrase“) and an outline of large read-only sources.


def _hint_ids(hint: str) -> list[str]:
    ids = []
    for num, letter, last in CONTRACT_ID.findall(hint):
        if last:
            ids += [f"V{n}" for n in range(int(num), int(last) + 1)]
        else:
            ids.append(f"V{num}{letter}")
    return ids


def _headings(text: str) -> list[re.Match[str]]:
    """Markdown headings outside fenced code blocks."""
    fences = [m.start() for m in re.finditer(r"^```", text, re.MULTILINE)]
    spans = list(zip(fences[::2], fences[1::2], strict=False))
    return [h for h in HEADING.finditer(text) if not any(a < h.start() < b for a, b in spans)]


def _md_sections(text: str, hint: str) -> str | None:
    """Sections whose heading names one of the hint's contract ids or quoted phrases."""
    ids = _hint_ids(hint)
    phrases = re.findall(r"„([^“]+)“", hint)
    heads = _headings(text)
    picked = []
    for i, head in enumerate(heads):
        title = head.group(2)
        if len(head.group(1)) == 1:  # the document title names all its contracts
            continue
        hit = any(re.search(rf"(?<![\w]){re.escape(i_)}(?![\w])", title) for i_ in ids)
        hit = hit or any(p.lower() in title.lower() for p in phrases)
        if not hit:
            continue
        level = len(head.group(1))
        end = len(text)
        for nxt in heads[i + 1 :]:
            if len(nxt.group(1)) <= level:
                end = nxt.start()
                break
        picked.append((head.start(), end))
    if not picked:
        return None
    merged: list[tuple[int, int]] = []
    for start, end in sorted(picked):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    return "\n\n".join(text[a:b].strip() for a, b in merged)


def _test_excerpt(source: str, card_key: str) -> str:
    """Imports, the card's test functions and the module-level helpers they use."""
    tree = ast.parse(source)
    prefix = f"test_{card_key.lower()}_"
    named: dict[str, ast.stmt] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            named[node.name] = node
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for t in targets:
                if isinstance(t, ast.Name):
                    named[t.id] = node
    wanted = [n for n in named if n.startswith(prefix)]
    seen: set[str] = set()
    while wanted:
        name = wanted.pop()
        if name in seen:
            continue
        seen.add(name)
        for sub in ast.walk(named[name]):
            if isinstance(sub, ast.Name) and sub.id in named and sub.id not in seen:
                wanted.append(sub.id)
    keep = [
        n for n in tree.body
        if isinstance(n, (ast.Import, ast.ImportFrom)) or n in {named[k] for k in seen}
    ]  # fmt: skip
    return "\n\n".join(ast.get_source_segment(source, n) or "" for n in keep)


def _outline(source: str) -> str:
    """Signatures, docstring first lines and constants of a large Python module."""
    tree = ast.parse(source)
    lines: list[str] = []

    def add(node: ast.AST, indent: str) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            seg = (ast.get_source_segment(source, node) or "").split("\n")
            head = next((i for i, line in enumerate(seg) if line.rstrip().endswith(":")), 0)
            lines.append(indent + "\n".join(seg[: head + 1]).strip())
            doc = ast.get_docstring(node)
            if doc:
                lines.append(indent + '    """' + doc.splitlines()[0] + '"""')
            lines.append(indent + "    ...")
        elif isinstance(node, ast.ClassDef):
            lines.append(f"{indent}class {node.name}:")
            for sub in node.body:
                add(sub, indent + "    ")
        elif isinstance(node, (ast.Assign, ast.AnnAssign)) and not indent.strip():
            seg = ast.get_source_segment(source, node) or ""
            lines.append(seg if len(seg) < 200 else seg[:200] + " …")
        elif isinstance(node, ast.AnnAssign) and indent:
            lines.append(indent + (ast.get_source_segment(source, node) or ""))

    for node in tree.body:
        add(node, "")
    return "\n".join(lines)


def build_context(card: Card) -> tuple[list[str], Path | None, int]:
    """Return (files for --read, bundle file or None, estimated prompt tokens)."""
    reads: list[str] = []
    parts: list[str] = []
    for path, hint in card.hints.items():
        if path in card.targets:
            continue
        text = (ROOT / path).read_text(encoding="utf-8", errors="replace")
        if path.startswith("tests/") and path.endswith(".py"):
            parts.append(f"## {path} (nur die Tests dieser Karte)\n\n```python\n"
                         f"{_test_excerpt(text, card.key)}\n```")  # fmt: skip
        elif path.endswith(".md"):
            excerpt = _md_sections(text, hint)
            label = "Auszug" if excerpt else "vollständig"
            parts.append(f"## {path} ({label})\n\n{excerpt or text}")
        elif path.endswith(".py") and len(text.encode()) > SMALL_SOURCE:
            parts.append(f"## {path} (Gliederung)\n\n```python\n{_outline(text)}\n```")
        else:
            reads.append(path)
    bundle = None
    if parts:
        bundle = WORK / "kontext" / f"{card.key}.md"
        bundle.parent.mkdir(parents=True, exist_ok=True)
        bundle.write_text(f"# Kontext für Karte {card.key}\n\n" + "\n\n".join(parts), "utf-8")
    chars = sum((ROOT / p).stat().st_size for p in [*card.targets, *reads] if (ROOT / p).is_file())
    chars += bundle.stat().st_size if bundle else 0
    chars += len(card.text) + 2000
    return reads, bundle, int(chars / CHARS_PER_TOKEN)


def model_setting(model: str, key: str) -> str:
    """Value of ``key`` in the settings entry of ``model`` ("" if missing)."""
    text = MODEL_SETTINGS.read_text(encoding="utf-8")
    for entry in re.split(r"^- ", text, flags=re.MULTILINE):
        if re.match(rf"name:\s*{re.escape(model)}\s*$", entry, re.MULTILINE):
            match = re.search(rf"^\s*{key}:\s*(\S+)", entry, re.MULTILINE)
            return match.group(1) if match else ""
    return ""


def model_ctx(model: str) -> int:
    """num_ctx of ``model`` in the model settings file (entries start with "- name:")."""
    text = MODEL_SETTINGS.read_text(encoding="utf-8")
    for entry in re.split(r"^- ", text, flags=re.MULTILINE):
        if re.match(rf"name:\s*{re.escape(model)}\s*$", entry, re.MULTILINE):
            match = re.search(r"num_ctx:\s*(\d+)", entry)
            if match:
                return int(match.group(1))
    return 8192  # Ollama's default when the model has no entry


# qwen3-coder mangled the file name line of the whole format (it created a file "}");
# its diff edits work, so it always uses its own format.
NO_WHOLE_MODELS = frozenset({"ollama_chat/qwen3-coder:30b"})
WHOLE_LIMIT = 12_000  # bytes; small files are rewritten whole (more reliable for small models)


def edit_format(card: Card, wanted: str, model: str) -> str:
    """auto: small files whole, large files in the model's format from the settings file."""
    if wanted != "auto":
        return wanted
    sizes = [(ROOT / t).stat().st_size for t in card.targets if (ROOT / t).is_file()]
    if all(size <= WHOLE_LIMIT for size in sizes) and model not in NO_WHOLE_MODELS:
        return "whole"
    return model_setting(model, "edit_format") or "diff"


def stub_list(card: Card) -> str:
    """Name the placeholders of this card with file and line, so the model edits them."""
    marker = re.compile(rf'NotImplementedError\(".*?\b{card.key}\b')
    found = []
    for target in card.targets:
        path = ROOT / target
        if not path.is_file() or not target.endswith(".py"):
            continue
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        owner = ""
        for number, line in enumerate(lines, 1):
            match = re.match(r"\s*(?:def|class) (\w+)", line)
            if match:
                owner = f"{match.group(1)} (Zeile {number})"
            if marker.search(line) and owner:
                found.append(f"- {target}: {owner}")
    if not found:
        return ""
    return (
        "\nPlaceholders of this card (replace their bodies in place):\n" + "\n".join(found) + "\n"
    )


def aider(card: Card, message: str, args: argparse.Namespace, log: Path) -> int:
    cmd = [
        args.aider,
        "--model", args.model,
        "--model-settings-file", str(MODEL_SETTINGS),
        "--edit-format", edit_format(card, args.format, args.model),
        "--timeout", str(args.timeout * 60),
        "--no-auto-commits", "--no-dirty-commits", "--no-auto-lint",
        "--yes-always", "--no-suggest-shell-commands", "--no-detect-urls",
        "--no-gitignore", "--no-show-model-warnings",
        "--no-check-update", "--no-show-release-notes", "--analytics-disable",
        "--no-stream", "--no-pretty", "--no-fancy-input",
        "--map-tokens", "0",
        "--chat-history-file", str(log.with_suffix(".chat.md")),
        "--input-history-file", str(WORK / "aider-input.txt"),
    ]  # fmt: skip
    for target in card.targets:
        cmd += ["--file", target]
    reads, bundle, tokens = build_context(card)
    for ctx in reads:
        cmd += ["--read", ctx]
    if bundle:
        cmd += ["--read", str(bundle.relative_to(ROOT))]
    cmd += ["--message", message]
    # Windows: without UTF-8 output Aider crashes on the first non-cp1252 character and
    # then hangs until the time limit.
    env = {
        **os.environ,
        "OLLAMA_API_BASE": args.ollama,
        "PYTHONUTF8": "1",
        "PYTHONIOENCODING": "utf-8",
    }
    chat = log.with_suffix(".chat.md")
    chat.unlink(missing_ok=True)  # Aider appends to an existing history file
    deadline = time.monotonic() + args.timeout * 60
    limit = model_ctx(args.model)
    with log.open("w", encoding="utf-8") as out:
        out.write(f"Kontext: ca. {tokens} Tokens von {limit} (num_ctx)\n")
        out.flush()
        if tokens > limit * 0.85:  # leave room for thinking and the answer
            return AIDER_TOO_BIG
        proc = subprocess.Popen(
            cmd, cwd=ROOT, env=env, stdin=subprocess.DEVNULL, stdout=out,
            stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace",
        )  # fmt: skip
        while proc.poll() is None:
            time.sleep(5)
            if crashed(chat) or crashed(log):
                proc.kill()
                proc.wait()
                return AIDER_CRASH
            if time.monotonic() > deadline:
                proc.kill()
                proc.wait()
                out.write("\nZeitüberschreitung\n")
                return AIDER_TIMEOUT
    return AIDER_CRASH if crashed(chat) or crashed(log) else proc.returncode


AIDER_TIMEOUT = -1
AIDER_CRASH = -2
AIDER_TOO_BIG = -3


def crashed(path: Path) -> bool:
    """Aider printed a Python traceback (it does not exit by itself afterwards)."""
    if not path.is_file():
        return False
    return "Traceback (most recent call last)" in path.read_text(encoding="utf-8", errors="replace")


def _subject(card: Card) -> str:
    title = re.sub(r"\(`V[^)]*\)", "", card.title).replace("`", "").strip()
    return title if len(title) <= 60 else title[:57].rstrip() + "..."


def commit_message(card: Card) -> str:
    """Conventional Commits (the project's commit-msg hook insists on it)."""
    return f"feat(karte-{card.key.lower()}): {_subject(card)}"


def merge_message(card: Card) -> str:
    return f"chore(kartenlauf): Karte {card.key} übernehmen"


PATH_TOKEN = re.compile(r"[\w.\-]+(?:[/\\][\w.\-]+)+\.\w+")


def hide_paths(message: str, card: Card) -> str:
    """Keep Aider from pulling files into the chat because the message names them.

    Aider adds every repository file mentioned in the message as an editable file (with
    --yes-always without asking). That doubled the prompt and overflowed the context.
    Target files stay as they are; every other path loses its folders and extension.
    """
    targets = {t.replace("\\", "/") for t in card.targets}

    def repl(match: re.Match[str]) -> str:
        path = match.group(0).replace("\\", "/")
        if path in targets or not (ROOT / path).exists():
            return match.group(0)
        return f"{Path(path).stem} (Kontext)"

    return PATH_TOKEN.sub(repl, message)


def do_card(card: Card, args: argparse.Namespace) -> tuple[str, int, str]:
    """Return (status, attempts, note)."""
    branch = f"card/{card.key}"
    git("checkout", "-q", args.lauf)
    git("branch", "-D", branch, check=False)
    git("checkout", "-q", "-b", branch)
    before = changed_files()
    ok, _ = verify(card)
    if ok:  # e.g. done by hand or by an earlier, interrupted run
        git("checkout", "-q", args.lauf)
        return "fertig", 0, "war schon grün"
    message = hide_paths(
        PROMPT.format(
            targets=", ".join(card.targets),
            verify=card.verify,
            card=card.text,
            key=card.key,
            stubs=stub_list(card),
        ),
        card,
    )
    note = ""
    for attempt in range(1, args.versuche + 1):
        log = LOG_DIR / f"{card.key}-{attempt}.log"
        code = aider(card, message, args, log)
        outside = revert_outside(card, before)
        if code == AIDER_CRASH:
            reset_card(before)
            git("checkout", "-q", args.lauf)
            return (
                "abgebrochen",
                attempt,
                f"Aider abgestürzt, siehe {log.name} / {log.stem}.chat.md",
            )
        if code == AIDER_TOO_BIG:
            reset_card(before)
            git("checkout", "-q", args.lauf)
            first = log.read_text(encoding="utf-8").splitlines()[0]
            return "gescheitert", attempt, f"Kontext zu groß: {first}"
        if code == AIDER_TIMEOUT:
            note = f"Aider-Zeitlimit ({args.timeout} min)"
            continue
        ok, output = verify(card)
        log.write_text(log.read_text(encoding="utf-8") + "\n\n=== Prüfung ===\n" + output, "utf-8")
        if ok:
            git("add", "--", *[t for t in card.targets if (ROOT / t).exists()])
            if run(["git", "diff", "--cached", "--quiet"])[0] != 0:
                code, out = run(["git", "commit", "-q", "-m", commit_message(card)])
                if code != 0:
                    return "abgebrochen", attempt, "Commit abgelehnt: " + shorten(out, 300)
            git("checkout", "-q", args.lauf)
            code, out = run(["git", "merge", "-q", "--no-ff", branch, "-m", merge_message(card)])
            if code != 0:
                return "abgebrochen", attempt, "Merge fehlgeschlagen: " + shorten(out, 300)
            extra = f" (zurückgesetzt außerhalb: {', '.join(outside)})" if outside else ""
            return "fertig", attempt, extra.strip()
        note = shorten(output, 400).splitlines()[-1] if output.strip() else "rot"
        message = hide_paths(
            RETRY.format(
                targets=", ".join(card.targets), verify=card.verify, output=shorten(output)
            ),
            card,
        )
    reset_card(before)
    git("checkout", "-q", args.lauf)
    return "gescheitert", args.versuche, note


# --------------------------------------------------------------------------- main


def prepare_git(args: argparse.Namespace) -> None:
    current = git("branch", "--show-current")
    if current.startswith("card/"):
        # The previous run was interrupted (e.g. Ctrl+C): drop that card's half-done edits.
        print(f"Räume den abgebrochenen Zweig {current} auf.", flush=True)
        dirty = run(["git", "status", "--porcelain", "--untracked-files=no"], check=True)[1]
        for line in dirty.splitlines():
            path = line[3:].strip().strip('"')
            if path and "tools/kartenlauf." not in path:
                restore(path)
        git("checkout", "-q", args.lauf)
    dirty = run(["git", "status", "--porcelain", "--untracked-files=no"], check=True)[1]
    # Changes to the run's own files may stay uncommitted; they travel along on checkout.
    others = [ln for ln in dirty.splitlines() if ln.strip() and "tools/kartenlauf." not in ln]
    if others:
        raise SystemExit("Es gibt nicht committete Änderungen. Bitte erst committen oder stashen.")
    exclude = ROOT / ".git" / "info" / "exclude"
    rule = "tasks/kartenlauf/"
    if rule not in exclude.read_text(encoding="utf-8", errors="replace"):
        with exclude.open("a", encoding="utf-8") as fh:
            fh.write(f"\n{rule}\n")
    if not git("branch", "--list", args.lauf):
        git("branch", args.lauf, args.basis)
    git("checkout", "-q", args.lauf)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--model", default="ollama_chat/qwen3-coder:30b")
    parser.add_argument("--ollama", default="http://127.0.0.1:11434")
    parser.add_argument("--aider", default="aider")
    parser.add_argument("--basis", default="master", help="Zweig, von dem der Lauf abzweigt")
    parser.add_argument("--lauf", default="ollama-card-run", help="Sammelzweig des Laufs")
    parser.add_argument(
        "--format",
        default="auto",
        help="Aider-Bearbeitungsformat: auto (whole bis 12 KB je Ziel-Datei, sonst diff), diff, whole",
    )
    parser.add_argument("--versuche", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=40, help="Minuten je Aider-Aufruf")
    parser.add_argument("--max", type=int, default=0, help="höchstens so viele Karten")
    parser.add_argument("--bis", default="", help="Uhrzeit HH:MM, danach keine neue Karte")
    parser.add_argument("--nur", default="", help="nur diese Karten, z. B. A01,A02")
    parser.add_argument("--neu", action="store_true", help="gescheiterte Karten erneut versuchen")
    parser.add_argument("--trocken", action="store_true", help="nur die Reihenfolge zeigen")
    args = parser.parse_args()
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]

    cards = load_cards()
    ordered = topo_order(cards)
    if args.trocken:
        for card in ordered:
            print(f"{card.key}  deps={','.join(card.deps) or '-'}  ziel={','.join(card.targets)}")
        print(f"{len(ordered)} Karten")
        return 0

    WORK.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)
    prepare_git(args)
    state = State.load()
    only = {k.strip().upper() for k in args.nur.split(",") if k.strip()}
    deadline = None
    if args.bis:
        hour, minute = (int(x) for x in args.bis.split(":"))
        deadline = now().replace(hour=hour, minute=minute, second=0)

    keep_awake(True)
    started = 0
    try:
        for card in ordered:
            status = state.status(card.key)
            if status == "fertig" or (status == "gescheitert" and not args.neu):
                continue
            if only and card.key not in only:
                continue
            if args.max and started >= args.max:
                break
            if deadline and now() >= deadline:
                print(f"Zeitgrenze {args.bis} erreicht.")
                break
            blocked = [d for d in card.deps if d in cards and state.status(d) != "fertig"]
            if blocked:
                state.cards[card.key] = {"status": "übersprungen", "note": f"wartet auf {blocked}"}
                continue
            if not card.verify or not card.targets:
                state.cards[card.key] = {"status": "gescheitert", "note": "Karte unvollständig"}
                continue
            started += 1
            print(f"[{now():%H:%M}] {card.key} — {card.title}", flush=True)
            t0 = time.monotonic()
            result, attempts, note = do_card(card, args)
            state.cards[card.key] = {
                "status": result,
                "attempts": attempts,
                "seconds": round(time.monotonic() - t0),
                "note": note,
                "when": f"{now():%Y-%m-%d %H:%M}",
            }
            print(f"    -> {result} nach {attempts} Versuch(en)", flush=True)
            if result == "abgebrochen":
                print(f"Lauf gestoppt: {note}. Die Karte bleibt offen.", flush=True)
                del state.cards[card.key]
                break
            state.save()
            write_report(state, ordered)
    finally:
        keep_awake(False)
        # Skipped cards are re-evaluated on the next start.
        for key in [k for k, v in state.cards.items() if v["status"] == "übersprungen"]:
            del state.cards[key]
        state.save()
        write_report(state, ordered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
