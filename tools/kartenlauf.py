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

PROMPT = """You are implementing exactly one task card of the game project py-noita-claude
(Python, pygame-ce). Follow the card literally.

Rules:
- Edit only these files: {targets}. Create them if they do not exist.
- The read-only files are your context. Never change tests in tests/spec/.
- Code, names and comments in English; every text the player sees in German.
- Keep existing behaviour working; prefer small, focused changes.
- The card is done when this command passes: {verify}

Card:

{card}
"""

RETRY = """The verification failed. Fix the code (only in {targets}) so it passes.
Command: {verify}

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
            context = [
                p for p in _paths(_field(text, "Zu lesender Kontext")) if (ROOT / p).is_file()
            ]
            cards[head.group(1)] = Card(
                key=head.group(1),
                title=head.group(2).strip(),
                text=text,
                deps=_expand(_field(text, "Abhängigkeiten")),
                targets=_paths(_field(text, "Ziel-Dateien")),
                context=context,
                verify=verify[0] if verify else "",
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


def run(
    cmd: list[str] | str, *, timeout: float | None = None, check: bool = False
) -> tuple[int, str]:
    proc = subprocess.run(
        cmd,
        check=False,
        cwd=ROOT,
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
        allowed = any(path == t or path.startswith(t.rstrip("/") + "/") for t in card.targets)
        protected = any(path == p or path.startswith(p) for p in PROTECTED)
        if allowed and not protected:
            continue
        reverted.append(path)
        if git("ls-files", path):
            git("checkout", "--", path)
        else:
            (ROOT / path).unlink(missing_ok=True)
    return reverted


def reset_card(before: set[str]) -> None:
    git("reset", "--hard", "-q")
    for path in changed_files() - before:
        (ROOT / path).unlink(missing_ok=True)


def aider(card: Card, message: str, args: argparse.Namespace, log: Path) -> int:
    cmd = [
        args.aider,
        "--model", args.model,
        "--model-settings-file", str(MODEL_SETTINGS),
        "--edit-format", args.format,
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
    for ctx in card.context:
        if ctx not in card.targets:
            cmd += ["--read", ctx]
    cmd += ["--message", message]
    env = {**os.environ, "OLLAMA_API_BASE": args.ollama}
    try:
        proc = subprocess.run(
            cmd, check=False, cwd=ROOT, env=env, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=args.timeout * 60,
        )  # fmt: skip
        log.write_text((proc.stdout or "") + (proc.stderr or ""), encoding="utf-8")
        return proc.returncode
    except subprocess.TimeoutExpired:
        log.write_text("Zeitüberschreitung", encoding="utf-8")
        return -1


def do_card(card: Card, args: argparse.Namespace) -> tuple[str, int, str]:
    """Return (status, attempts, note)."""
    branch = f"card/{card.key}"
    git("checkout", "-q", args.lauf)
    git("branch", "-D", branch, check=False)
    git("checkout", "-q", "-b", branch)
    before = changed_files()
    message = PROMPT.format(targets=", ".join(card.targets), verify=card.verify, card=card.text)
    note = ""
    for attempt in range(1, args.versuche + 1):
        log = LOG_DIR / f"{card.key}-{attempt}.log"
        code = aider(card, message, args, log)
        outside = revert_outside(card, before)
        if code == -1:
            note = f"Aider-Zeitlimit ({args.timeout} min)"
            continue
        ok, output = verify(card)
        log.write_text(log.read_text(encoding="utf-8") + "\n\n=== Prüfung ===\n" + output, "utf-8")
        if ok:
            git("add", "--", *[t for t in card.targets if (ROOT / t).exists()])
            if run(["git", "diff", "--cached", "--quiet"])[0] != 0:
                git("commit", "-q", "-m", f"Karte {card.key}: {card.title}")
            git("checkout", "-q", args.lauf)
            git("merge", "-q", "--no-ff", branch, "-m", f"Merge Karte {card.key}")
            extra = f" (zurückgesetzt außerhalb: {', '.join(outside)})" if outside else ""
            return "fertig", attempt, extra.strip()
        note = shorten(output, 400).splitlines()[-1] if output.strip() else "rot"
        message = RETRY.format(
            targets=", ".join(card.targets), verify=card.verify, output=shorten(output)
        )
    reset_card(before)
    git("checkout", "-q", args.lauf)
    return "gescheitert", args.versuche, note


# --------------------------------------------------------------------------- main


def prepare_git(args: argparse.Namespace) -> None:
    if git("status", "--porcelain", "--untracked-files=no"):
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
    parser.add_argument("--model", default="ollama_chat/qwen3.5:9b")
    parser.add_argument("--ollama", default="http://127.0.0.1:11434")
    parser.add_argument("--aider", default="aider")
    parser.add_argument("--basis", default="master", help="Zweig, von dem der Lauf abzweigt")
    parser.add_argument("--lauf", default="ollama-card-run", help="Sammelzweig des Laufs")
    parser.add_argument(
        "--format", default="diff", help="Aider-Bearbeitungsformat: diff oder whole"
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
