"""CLI internal documentation generator and viewer."""

from __future__ import annotations

import re
from typing import Annotated, Any, TypedDict

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class ParamDoc(TypedDict, total=False):
    name: str
    flag: str
    description: str
    default: str | None
    required: bool
    is_argument: bool


class SubcommandDoc(TypedDict):
    name: str
    description: str


class ExampleDoc(TypedDict):
    command: str
    description: str


class CommandDoc(TypedDict, total=False):
    name: str
    title: str
    description: str
    usage: str
    summary: str
    arguments: list[dict[str, Any]]
    options: list[dict[str, Any]]
    subcommands: list[dict[str, Any]]
    examples: list[dict[str, Any]]
    notes: str | None


_CATALOG_CACHE: dict[int, dict[str, dict[str, Any]]] = {}


def clear_docs_cache() -> None:
    """Clear internal CLI documentation cache."""
    _CATALOG_CACHE.clear()


def strip_rich_markup(text: str) -> str:
    """Remove Rich styling markup tags while preserving bracketed text."""
    return re.sub(
        r"\[/?(?:bold|dim|italic|underline|blink|reverse|strike|cyan|green|yellow|magenta|red|blue|white|black|default)(?:\s+[^\]]+)?\]",
        "",
        text,
        flags=re.IGNORECASE,
    )


def parse_docstring(doc: str | None) -> dict[str, Any]:
    """Parse a command docstring into structured description, examples, and notes."""
    if not doc:
        return {"description": "", "examples": [], "notes": None}

    plain = strip_rich_markup(doc).strip()

    # Split by known section headers (handles indentation)
    parts = re.split(
        r"\n(?=[ \t]*(?:Examples|Notes?|Common Workflows|Direct CLI Invocations):\s*)",
        plain,
        flags=re.IGNORECASE,
    )
    description = parts[0].strip()
    examples: list[dict[str, str]] = []
    notes: str | None = None

    for section in parts[1:]:
        section = section.strip()
        header_match = re.match(
            r"^[ \t]*(Examples|Notes?|Common Workflows):\s*(.*)",
            section,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if not header_match:
            continue
        header = header_match.group(1).lower()
        content = header_match.group(2).strip()

        if header in ("examples", "common workflows"):
            for line in content.split("\n"):
                line = line.strip()
                if not line:
                    continue
                if line.startswith(("•", "-")):
                    line = line.lstrip("•- ").strip()
                match = re.match(r"^(?:\$\s*)?([^#]+?)(?:\s+#\s*(.*))?$", line)
                if match:
                    cmd_str = match.group(1).strip()
                    if cmd_str.startswith("$"):
                        cmd_str = cmd_str[1:].strip()
                    desc_str = match.group(2).strip() if match.group(2) else ""
                    if cmd_str and not cmd_str.endswith(":"):
                        examples.append(
                            {
                                "command": cmd_str,
                                "description": desc_str or f"Execute {cmd_str}",
                            }
                        )
        elif header.startswith("note"):
            notes = " ".join(
                line.strip() for line in content.split("\n") if line.strip()
            )

    return {"description": description, "examples": examples, "notes": notes}


def extract_cli_metadata(
    app: typer.Typer | None = None,
    force_refresh: bool = False,
) -> dict[str, dict[str, Any]]:
    """Extract CLI command catalog dynamically from Typer/Click application tree."""
    if app is None:
        from cli.main import app as main_app

        app = main_app

    app_id = id(app)
    if not force_refresh and app_id in _CATALOG_CACHE:
        return _CATALOG_CACHE[app_id]

    click_group = typer.main.get_command(app)
    catalog: dict[str, dict[str, Any]] = {
        "overview": {
            "title": "Cornerstone CLI Overview",
            "description": "Unified command-line interface for application development, builds, database operations, and template configuration.",
            "usage": "python3 -m cli [COMMAND] [OPTIONS]",
            "summary": "Cornerstone integrates Vue 3 (frontend) and Python / pywebview (backend). The CLI provides tools to run the dev environment, build production bundles, manage the SQLite database, inspect runtime stats, and rebrand the template.",
        }
    }

    if hasattr(click_group, "commands") and isinstance(click_group.commands, dict):
        command_items = list(click_group.commands.items())
    else:
        cmd_name = click_group.name or "main"
        command_items = [(cmd_name, click_group)]

    for cmd_name, cmd in command_items:
        doc_raw = cmd.help or (cmd.callback.__doc__ if cmd.callback else None)
        doc_info = parse_docstring(doc_raw)

        # Determine short summary & title
        short_desc = cmd.short_help or (
            doc_info["description"].split("\n")[0]
            if doc_info["description"]
            else cmd_name
        )
        short_desc = strip_rich_markup(short_desc).strip()
        title = f"{cmd_name} - {short_desc}"

        # Subcommands if group
        subcommands: list[dict[str, str]] = []
        is_group = hasattr(cmd, "commands") and bool(cmd.commands)
        if is_group:
            for sub_name, sub_cmd in cmd.commands.items():
                sub_doc_raw = sub_cmd.help or (
                    sub_cmd.callback.__doc__ if sub_cmd.callback else None
                )
                sub_doc = parse_docstring(sub_doc_raw)
                sub_short = sub_cmd.short_help or (
                    sub_doc["description"].split("\n")[0]
                    if sub_doc["description"]
                    else ""
                )
                sub_short = strip_rich_markup(sub_short).strip()
                subcommands.append(
                    {
                        "name": sub_name,
                        "description": sub_short,
                    }
                )

        # Arguments and options
        arguments: list[dict[str, Any]] = []
        options: list[dict[str, Any]] = []
        usage_args: list[str] = []

        for param in getattr(cmd, "params", []):
            param_type = getattr(param, "param_type_name", None)
            if param_type == "argument":
                name = param.name.upper() if param.name else "ARG"
                if getattr(param, "nargs", 1) == -1:
                    name += "..."
                usage_args.append(name if param.required else f"[{name}]")
                arguments.append(
                    {
                        "name": name,
                        "description": param.help or "",
                        "required": bool(param.required),
                    }
                )
            elif param_type == "option":
                opts = list(getattr(param, "opts", []))
                # Skip Click/Typer internal options like --help or shell completion
                if param.name in (
                    "help",
                    "install_completion",
                    "show_completion",
                ) or any(
                    opt in ("--help", "-h", "--install-completion", "--show-completion")
                    for opt in opts
                ):
                    continue

                flag_str = " / ".join(opts) if opts else f"--{param.name}"
                default_val = getattr(param, "default", None)
                if default_val is ... or default_val is None:
                    default_str = "None"
                elif isinstance(default_val, (list, tuple)) and len(default_val) == 0:
                    default_str = "[]"
                elif isinstance(default_val, str) and default_val == "":
                    default_str = "''"
                else:
                    default_str = str(default_val)
                options.append(
                    {
                        "flag": flag_str,
                        "description": param.help or "",
                        "default": default_str,
                    }
                )

        # Build usage string
        usage_parts = ["python3 -m cli", cmd_name]
        if is_group:
            usage_parts.append("[SUBCOMMAND]")
        if usage_args:
            usage_parts.extend(usage_args)
        if options or (not usage_args and not is_group):
            usage_parts.append("[OPTIONS]")

        cmd_dict: dict[str, Any] = {
            "name": cmd_name,
            "title": title,
            "description": doc_info["description"],
            "usage": " ".join(usage_parts),
        }
        if arguments:
            cmd_dict["arguments"] = arguments
        if options or not is_group:
            cmd_dict["options"] = options
        if subcommands:
            cmd_dict["subcommands"] = subcommands
        if doc_info["examples"]:
            cmd_dict["examples"] = doc_info["examples"]
        if doc_info["notes"]:
            cmd_dict["notes"] = doc_info["notes"]

        catalog[cmd_name] = cmd_dict

    _CATALOG_CACHE[app_id] = catalog
    return catalog


def generate_markdown_doc(
    topic: str | None = None,
    app: typer.Typer | None = None,
) -> str:
    """Generate Markdown documentation for all or a specific CLI topic."""
    catalog = extract_cli_metadata(app)
    if topic:
        topic_key = topic.lower().strip()
        if topic_key not in catalog:
            available = ", ".join(f"`{k}`" for k in catalog if k != "overview")
            return f"# Topic Not Found\n\nNo documentation found for topic `{topic}`. Available topics: {available}."

        doc = catalog[topic_key]
        md_lines = [f"# {doc['title']}", "", doc["description"], ""]
        if "usage" in doc:
            md_lines.extend(["### Usage", f"```bash\n{doc['usage']}\n```", ""])

        if doc.get("arguments"):
            md_lines.extend(["### Arguments", ""])
            for arg in doc["arguments"]:
                req = "*(required)*" if arg.get("required") else "*(optional)*"
                md_lines.append(f"- `{arg['name']}` {req}: {arg['description']}")
            md_lines.append("")

        if doc.get("options"):
            md_lines.extend(["### Options", ""])
            for opt in doc["options"]:
                md_lines.append(
                    f"- `{opt['flag']}`: {opt['description']} (default: `{opt.get('default', 'None')}`)"
                )
            md_lines.append("")

        if doc.get("subcommands"):
            md_lines.extend(["### Subcommands", ""])
            for sub in doc["subcommands"]:
                md_lines.append(f"- `{topic_key} {sub['name']}`: {sub['description']}")
            md_lines.append("")

        if doc.get("examples"):
            md_lines.extend(["### Examples", ""])
            for ex in doc["examples"]:
                md_lines.append(f"**{ex['description']}**")
                md_lines.append(f"```bash\n{ex['command']}\n```")
                md_lines.append("")

        if doc.get("notes"):
            md_lines.extend(["### Notes", doc["notes"], ""])

        return "\n".join(md_lines)

    # Full documentation
    md_lines = [
        "# Cornerstone CLI Documentation",
        "",
        catalog["overview"]["summary"],
        "",
        "## Quick Start Workflow",
        "",
        "```bash",
        "# 1. Setup development environment and install dependencies",
        "python3 -m cli setup",
        "",
        "# 2. Rebrand the application template (optional)",
        'python3 -m cli init "My App" --description "Desktop app description"',
        "",
        "# 3. Start development environment with hot reloading",
        "python3 -m cli dev",
        "",
        "# 4. Check system stats and database status",
        "python3 -m cli stats",
        "python3 -m cli db info",
        "",
        "# 5. Build production executable",
        "python3 -m cli build",
        "```",
        "",
        "## Commands Catalog",
        "",
    ]

    for key, doc in catalog.items():
        if key == "overview":
            continue
        md_lines.append(f"### `{key}` - {doc['title']}")
        md_lines.append(f"{doc['description']}")
        md_lines.append("")
        md_lines.append(f"**Usage:** `{doc.get('usage', '')}`")
        md_lines.append("")
        if doc.get("examples"):
            md_lines.append("**Examples:**")
            for ex in doc["examples"]:
                md_lines.append(f"- `{ex['command']}` - {ex['description']}")
            md_lines.append("")

    return "\n".join(md_lines)


def render_rich_docs(
    topic: str | None = None,
    app: typer.Typer | None = None,
) -> None:
    """Render interactive Rich-formatted CLI documentation to the terminal."""
    catalog = extract_cli_metadata(app)
    if topic:
        topic_key = topic.lower().strip()
        if topic_key not in catalog:
            console.print(
                f"[bold red]Error:[/bold red] Unknown documentation topic '[bold yellow]{topic}[/bold yellow]'."
            )
            available = [k for k in catalog if k != "overview"]
            console.print(f"Available topics: [cyan]{', '.join(available)}[/cyan]")
            raise typer.Exit(code=1)

        doc = catalog[topic_key]
        console.print()
        console.print(
            Panel(
                f"[bold green]{doc['title']}[/bold green]\n[dim]{doc['description']}[/dim]",
                border_style="cyan",
            )
        )

        if "usage" in doc:
            console.print(
                f"[bold cyan]Usage:[/bold cyan] [yellow]{doc['usage']}[/yellow]\n"
            )

        if doc.get("arguments"):
            table = Table(title="[bold]Arguments[/bold]", show_header=True)
            table.add_column("Argument", style="cyan")
            table.add_column("Required", style="magenta")
            table.add_column("Description", style="white")
            for arg in doc["arguments"]:
                table.add_row(
                    arg["name"],
                    "Yes" if arg.get("required") else "No",
                    arg["description"],
                )
            console.print(table)
            console.print()

        if doc.get("options"):
            table = Table(title="[bold]Options[/bold]", show_header=True)
            table.add_column("Option", style="cyan")
            table.add_column("Default", style="yellow")
            table.add_column("Description", style="white")
            for opt in doc["options"]:
                table.add_row(
                    opt["flag"], str(opt.get("default", "")), opt["description"]
                )
            console.print(table)
            console.print()

        if doc.get("subcommands"):
            table = Table(title="[bold]Subcommands[/bold]", show_header=True)
            table.add_column("Subcommand", style="cyan")
            table.add_column("Description", style="white")
            for sub in doc["subcommands"]:
                table.add_row(f"{topic_key} {sub['name']}", sub["description"])
            console.print(table)
            console.print()

        if doc.get("examples"):
            console.print("[bold green]Examples & Recipes:[/bold green]")
            for ex in doc["examples"]:
                console.print(f"  [bold]•[/bold] [white]{ex['description']}[/white]")
                console.print(f"    [cyan]$ {ex['command']}[/cyan]\n")

        if doc.get("notes"):
            console.print(
                Panel(
                    f"[bold yellow]Note:[/bold yellow] {doc['notes']}",
                    border_style="yellow",
                )
            )
        return

    # Full overview
    console.print()
    console.print(
        Panel(
            "[bold cyan]Cornerstone CLI - Interactive Documentation[/bold cyan]\n"
            "[dim]A developer-friendly CLI for desktop app creation, management, and build automation.[/dim]",
            border_style="cyan",
        )
    )

    # Workflow guide table
    workflow_table = Table(
        title="[bold green]Common Workflows & Quick Start[/bold green]",
        show_header=True,
    )
    workflow_table.add_column("Step", style="cyan", width=6)
    workflow_table.add_column("Action", style="yellow", width=25)
    workflow_table.add_column("Command", style="green")

    workflow_table.add_row("1", "Setup environment", "python3 -m cli setup")
    workflow_table.add_row(
        "2",
        "Rebrand template (optional)",
        'python3 -m cli init "My App" -d "Description"',
    )
    workflow_table.add_row("3", "Run dev environment", "python3 -m cli dev")
    workflow_table.add_row(
        "4",
        "Inspect runtime & stats",
        "python3 -m cli stats   # or python3 -m cli info",
    )
    workflow_table.add_row(
        "5", "Manage database", "python3 -m cli db info # or db test, db query"
    )
    workflow_table.add_row("6", "Build desktop binary", "python3 -m cli build")
    console.print(workflow_table)
    console.print()

    # Commands list table
    commands_table = Table(
        title="[bold blue]Commands Catalog & Examples[/bold blue]", show_header=True
    )
    commands_table.add_column("Command", style="cyan", no_wrap=True)
    commands_table.add_column("Description", style="white")
    commands_table.add_column("Example Usage", style="green")

    for key, cmd_doc in catalog.items():
        if key == "overview":
            continue
        first_ex = (
            cmd_doc["examples"][0]["command"]
            if cmd_doc.get("examples")
            else cmd_doc.get("usage", "")
        )
        commands_table.add_row(key, cmd_doc["description"], first_ex)

    console.print(commands_table)
    console.print()
    console.print(
        "[dim]Tip: Run [bold cyan]python3 -m cli docs <command>[/bold cyan] for detailed documentation on any specific command (e.g. [cyan]python3 -m cli docs db[/cyan] or [cyan]python3 -m cli docs init[/cyan]).[/dim]\n"
    )


def docs_command(
    topic: Annotated[
        str | None,
        typer.Argument(
            help="Optional command or topic name (e.g., 'dev', 'db', 'init', 'build', 'setup', 'stats', 'info').",
        ),
    ] = None,
    as_markdown: Annotated[
        bool,
        typer.Option(
            "--markdown",
            "-m",
            help="Output documentation in raw Markdown format.",
        ),
    ] = False,
    as_json: Annotated[
        bool,
        typer.Option(
            "--json",
            "-j",
            help="Output documentation as structured JSON.",
        ),
    ] = False,
) -> None:
    """
    Browse comprehensive CLI documentation, commands catalog, and usage examples.

    [bold green]Examples:[/bold green]
      [cyan]$ python3 -m cli docs[/cyan]                  # View full documentation guide
      [cyan]$ python3 -m cli docs db[/cyan]               # View database command documentation
      [cyan]$ python3 -m cli docs init[/cyan]             # View template rebranding guide
      [cyan]$ python3 -m cli docs --markdown[/cyan]       # Output documentation in Markdown format
      [cyan]$ python3 -m cli docs stats --json[/cyan]      # Output topic details as JSON
    """
    if as_json:
        catalog = extract_cli_metadata()
        if topic:
            topic_key = topic.lower().strip()
            if topic_key not in catalog:
                console.print_json(data={"error": f"Topic '{topic}' not found."})
                raise typer.Exit(code=1)
            console.print_json(data={topic_key: catalog[topic_key]})
        else:
            console.print_json(data=catalog)
        return

    if as_markdown:
        md_text = generate_markdown_doc(topic)
        console.print(md_text, markup=False)
        return

    render_rich_docs(topic)
