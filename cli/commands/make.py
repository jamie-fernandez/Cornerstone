"""Code generators for API bridge methods, Vue pages, and database models."""

from __future__ import annotations

import os
import re
from typing import Annotated

import typer
from rich.console import Console

from cli.common import PROJECT_ROOT

console = Console()
make_app = typer.Typer(
    name="make",
    help="""[bold cyan]Code Generators[/bold cyan] - Scaffold boilerplate for API bridge methods, UI pages, and database models.

[bold]Common Workflows:[/bold]
  [cyan]$ stone make api get_user_profile[/cyan]               # Scaffold a new bridge API method with frontend mock
  [cyan]$ stone make page Settings[/cyan]                       # Scaffold a new Vue page component and route
  [cyan]$ stone make model Task --fields "title:str"[/cyan]       # Scaffold an SQLAlchemy model class
""",
    rich_markup_mode="rich",
    no_args_is_help=True,
)


def _to_snake_case(name: str) -> str:
    """Convert string to snake_case identifier."""
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s).lower()
    s = re.sub(r"[^a-z0-9_]+", "_", s).strip("_")
    return s or "custom_method"


def _to_pascal_case(name: str) -> str:
    """Convert string to PascalCase identifier."""
    words = re.split(r"[^a-zA-Z0-9]+", name)
    return "".join(w.capitalize() for w in words if w) or "CustomPage"


def _to_kebab_case(name: str) -> str:
    """Convert string to kebab-case slug."""
    s = _to_snake_case(name)
    return s.replace("_", "-")


@make_app.command(
    "api", short_help="Scaffold a new bridge API method with frontend mock."
)
def make_api_command(
    name: Annotated[
        str, typer.Argument(help="Method name (e.g. get_user_settings, export_data)")
    ],
    description: Annotated[
        str,
        typer.Option(
            "--description", "-d", help="Docstring description for the method"
        ),
    ] = "",
) -> None:
    """
    Generate a decorated bridge method in 'app/api.py' and mirror it in 'ui/utils/bridge.mock.js'.

    [bold green]Examples:[/bold green]
      [cyan]$ stone make api get_user_settings[/cyan]
      [cyan]$ stone make api export_csv -d "Export user report as CSV format"[/cyan]
    """
    method_name = _to_snake_case(name)
    desc = (
        description
        or f"{method_name.replace('_', ' ').capitalize()} bridge API method."
    )

    api_path = os.path.join(PROJECT_ROOT, "app", "api.py")
    mock_path = os.path.join(PROJECT_ROOT, "ui", "utils", "bridge.mock.js")

    if not os.path.exists(api_path):
        console.print(f"[bold red]Error:[/bold red] API file not found at {api_path}")
        raise typer.Exit(code=1)

    # 1. Update app/api.py
    with open(api_path, encoding="utf-8") as f:
        api_content = f.read()

    pattern = rf"def\s+{re.escape(method_name)}\s*\("
    if re.search(pattern, api_content):
        console.print(
            f"[bold yellow]Warning:[/bold yellow] Method '{method_name}' already exists in app/api.py"
        )
    else:
        new_method = (
            f"\n    @bridge_method\n"
            f"    def {method_name}(self):\n"
            f'        """{desc}"""\n'
            f'        return {{"status": "success", "data": {{"message": "Hello from {method_name}"}}}}\n'
        )
        api_content = api_content.rstrip() + new_method
        with open(api_path, "w", encoding="utf-8") as f:
            f.write(api_content)
        console.print(
            f"[bold green]✓[/bold green] Added bridge method [bold cyan]{method_name}[/bold cyan] to [magenta]app/api.py[/magenta]"
        )

    # 2. Update ui/utils/bridge.mock.js
    if os.path.exists(mock_path):
        with open(mock_path, encoding="utf-8") as f:
            mock_content = f.read()

        mock_pattern = rf"\b{re.escape(method_name)}\s*:"
        if re.search(mock_pattern, mock_content):
            console.print(
                f"[bold yellow]Warning:[/bold yellow] Mock '{method_name}' already exists in ui/utils/bridge.mock.js"
            )
        else:
            # Find the closing bracket of mockApi object
            mock_method = f"    {method_name}: () => ok({{ message: 'Hello from {method_name} (mock)' }}),\n}}"
            if mock_content.rstrip().endswith("}"):
                idx = mock_content.rstrip().rfind("}")
                mock_content = mock_content[:idx] + mock_method + "\n"
            else:
                mock_content = mock_content.rstrip() + f"\n// Added {method_name}\n"

            with open(mock_path, "w", encoding="utf-8") as f:
                f.write(mock_content)
            console.print(
                "[bold green]✓[/bold green] Added mock implementation to [magenta]ui/utils/bridge.mock.js[/magenta]"
            )

    console.print("\n[bold green]Usage in Vue components:[/bold green]")
    console.print(f"  [cyan]const data = await callApi('{method_name}')[/cyan]")


@make_app.command(
    "page", short_help="Scaffold a new Vue view component and register its route."
)
def make_page_command(
    name: Annotated[
        str,
        typer.Argument(help="Page/view name (e.g. Settings, Analytics, UserProfile)"),
    ],
    path: Annotated[
        str | None,
        typer.Option(
            "--path", "-p", help="Custom route path (default: derived from name)"
        ),
    ] = None,
    title: Annotated[
        str | None,
        typer.Option("--title", "-t", help="Breadcrumb/Page display title"),
    ] = None,
) -> None:
    """
    Generate a new Vue view component in 'ui/pages/' and register it in 'ui/router.js'.

    [bold green]Examples:[/bold green]
      [cyan]$ stone make page Settings[/cyan]
      [cyan]$ stone make page UserProfile --path /profile --title "User Profile"[/cyan]
    """
    raw_name = name.strip()
    raw_name = raw_name.removesuffix(".vue")

    pascal_name = _to_pascal_case(raw_name)
    component_name = pascal_name if pascal_name.startswith("P") else f"P{pascal_name}"
    display_title = (
        title
        or re.sub(
            r"(?<!^)(?=[A-Z])",
            " ",
            pascal_name[1:]
            if pascal_name.startswith("P") and len(pascal_name) > 1
            else pascal_name,
        ).strip()
    )
    route_path = (
        path
        or f"/{_to_kebab_case(pascal_name[1:] if pascal_name.startswith('P') and len(pascal_name) > 1 else pascal_name)}"
    )

    page_file = os.path.join(PROJECT_ROOT, "ui", "pages", f"{component_name}.vue")
    router_file = os.path.join(PROJECT_ROOT, "ui", "router.js")

    if os.path.exists(page_file):
        console.print(
            f"[bold red]Error:[/bold red] Page component already exists at {page_file}"
        )
        raise typer.Exit(code=1)

    # 1. Create the Vue page component
    vue_content = f"""<script setup>
import {{ ref }} from 'vue'
// import {{ callApi }} from '@/utils/bridge.js'

const title = ref('{display_title}')
</script>

<template>
    <v-main>
        <v-container>
            <h1 class="text-h4 font-weight-bold mb-4">{{{{ title }}}}</h1>
            <p class="text-body-1">
                Welcome to the {display_title} view. Customize this component in
                <code>ui/pages/{component_name}.vue</code>.
            </p>
        </v-container>
    </v-main>
</template>
"""
    os.makedirs(os.path.dirname(page_file), exist_ok=True)
    with open(page_file, "w", encoding="utf-8") as f:
        f.write(vue_content)
    console.print(
        f"[bold green]✓[/bold green] Created Vue page component at [magenta]ui/pages/{component_name}.vue[/magenta]"
    )

    # 2. Update ui/router.js
    if os.path.exists(router_file):
        with open(router_file, encoding="utf-8") as f:
            router_content = f.read()

        import_stmt = f"import {component_name} from '@/pages/{component_name}.vue'\n"
        route_entry = (
            f"    {{\n"
            f"        path: '{route_path}',\n"
            f"        component: {component_name},\n"
            f"        meta: {{ breadcrumb: '{display_title}' }},\n"
            f"    }},\n"
        )

        if component_name not in router_content:
            # Add import after other imports
            last_import = 0
            for match in re.finditer(r"(?m)^import\s+.*$", router_content):
                last_import = match.end()

            if last_import > 0:
                router_content = (
                    router_content[:last_import]
                    + "\n"
                    + import_stmt
                    + router_content[last_import:]
                )
            else:
                router_content = import_stmt + router_content

            # Insert route before closing bracket of routes array
            routes_match = re.search(r"const\s+routes\s*=\s*\[", router_content)
            if routes_match:
                routes_close_idx = router_content.find("]", routes_match.end())
                if routes_close_idx != -1:
                    router_content = (
                        router_content[:routes_close_idx]
                        + route_entry
                        + router_content[routes_close_idx:]
                    )

            with open(router_file, "w", encoding="utf-8") as f:
                f.write(router_content)
            console.print(
                f"[bold green]✓[/bold green] Registered route [bold cyan]{route_path}[/bold cyan] in [magenta]ui/router.js[/magenta]"
            )


@make_app.command("model", short_help="Scaffold an SQLAlchemy database model.")
def make_model_command(
    name: Annotated[
        str, typer.Argument(help="Model class name (e.g. Task, Project, Customer)")
    ],
    table_name: Annotated[
        str | None,
        typer.Option(
            "--table-name",
            "-t",
            help="Database table name (default: pluralized snake_case)",
        ),
    ] = None,
    fields: Annotated[
        str | None,
        typer.Option(
            "--fields",
            "-f",
            help="Comma-separated field definitions (e.g. 'title:str,content:text,is_active:bool')",
        ),
    ] = None,
    migrate: Annotated[
        bool,
        typer.Option(
            "--migrate",
            "-m",
            help="Automatically generate an Alembic database migration for the new model",
        ),
    ] = False,
) -> None:
    """
    Generate an SQLAlchemy model class with automatic to_dict() serialization in 'app/models.py'.

    [bold green]Examples:[/bold green]
      [cyan]$ stone make model Task[/cyan]
      [cyan]$ stone make model Project --fields "title:str,description:text,is_active:bool" --migrate[/cyan]
    """
    class_name = _to_pascal_case(name)
    snake_name = _to_snake_case(class_name)
    tbl = table_name or (
        f"{snake_name}s" if not snake_name.endswith("s") else snake_name
    )

    models_path = os.path.join(PROJECT_ROOT, "app", "models.py")

    field_lines = [
        "    id = Column(Integer, primary_key=True, autoincrement=True)",
    ]

    needed_types = {"Column", "Integer"}

    if fields:
        for f in fields.split(","):
            f = f.strip()
            if not f:
                continue
            parts = f.split(":")
            fname = _to_snake_case(parts[0])
            ftype = parts[1].lower() if len(parts) > 1 else "str"

            if ftype in ("str", "string", "varchar"):
                field_lines.append(
                    f"    {fname} = Column(String, nullable=False, default='')"
                )
                needed_types.add("String")
            elif ftype in ("text",):
                field_lines.append(f"    {fname} = Column(Text, nullable=True)")
                needed_types.add("Text")
            elif ftype in ("int", "integer"):
                field_lines.append(
                    f"    {fname} = Column(Integer, nullable=False, default=0)"
                )
            elif ftype in ("bool", "boolean"):
                field_lines.append(
                    f"    {fname} = Column(Boolean, nullable=False, default=False)"
                )
                needed_types.add("Boolean")
            elif ftype in ("float", "double", "real"):
                field_lines.append(
                    f"    {fname} = Column(Float, nullable=False, default=0.0)"
                )
                needed_types.add("Float")
            elif ftype in ("datetime", "date", "timestamp"):
                field_lines.append(
                    f"    {fname} = Column(DateTime, default=datetime.utcnow)"
                )
                needed_types.add("DateTime")
            else:
                field_lines.append(f"    {fname} = Column(String, nullable=True)")
                needed_types.add("String")

    field_lines.append("    created_at = Column(DateTime, default=datetime.utcnow)")
    needed_types.add("DateTime")

    # Read existing app/models.py
    existing_content = ""
    if os.path.exists(models_path):
        with open(models_path, encoding="utf-8") as f:
            existing_content = f.read()

    # Check if model already exists
    if re.search(rf"\bclass\s+{re.escape(class_name)}\b", existing_content):
        console.print(
            f"[bold yellow]Warning:[/bold yellow] Model '{class_name}' already exists in app/models.py"
        )
        return

    # Check imports
    imports_to_add = []
    if (
        "from datetime import datetime" not in existing_content
        and "DateTime" in needed_types
    ):
        imports_to_add.append("from datetime import datetime")
    if "from app.base import Base" not in existing_content:
        imports_to_add.append("from app.base import Base")

    types_str = ", ".join(sorted(needed_types))
    if "from sqlalchemy import" not in existing_content:
        imports_to_add.append(f"from sqlalchemy import {types_str}")
    else:
        # Update existing sqlalchemy import if needed
        pass

    model_code = (
        f"\n\nclass {class_name}(Base):\n"
        f'    """{class_name} database model."""\n'
        f'    __tablename__ = "{tbl}"\n\n' + "\n".join(field_lines) + "\n"
    )

    header = ""
    if imports_to_add:
        header = "\n".join(imports_to_add) + "\n"

    new_content = (header + existing_content).strip() + model_code

    with open(models_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    console.print(
        f"[bold green]✓[/bold green] Added model [bold cyan]{class_name}[/bold cyan] (table: [magenta]{tbl}[/magenta]) to [magenta]app/models.py[/magenta]"
    )

    if migrate:
        from cli.commands.db.migrations import db_migrate_command

        migration_msg = f"create_{tbl}_table"
        console.print(
            f"\n[cyan]Generating migration revision for '{migration_msg}'...[/cyan]"
        )
        try:
            db_migrate_command(message=migration_msg)
        except Exception as e:  # noqa: BLE001
            console.print(
                f"[bold yellow]Migration generation failed:[/bold yellow] {e}"
            )
            console.print(
                "You can generate it manually using: [cyan]stone db migrate -m 'create_"
                + tbl
                + "_table'[/cyan]"
            )
