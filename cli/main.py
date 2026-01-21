import typer
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
import sys
import os
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

CURRENT_DIR = Path.cwd()
SAVE_PATH = CURRENT_DIR / "saves"
SAVE_PATH_JSON = SAVE_PATH / "json"
SAVE_PATH_CSV = SAVE_PATH / "csv"

from urllib.parse import urlparse
from src.models import Manga, MangaList, MangaListEntry
from src.parser import get_manga_details, get_manga_list, get_manga_from_manga_list
from src.exporter import import_data_to_json, import_data_to_csv

app = typer.Typer()
console = Console()

@app.command()
def main():
    """
    Interactive CLI for exporting reading list from Mangago.me
    """
    console.print("[bold blue]Mangago Reading List Exporter[/bold blue]")
    console.print("[italic]Export your reading list quickly![/italic]")
    
    while True:
        try:
            console.print("\n[bold]Options:[/bold]")
            console.print("1. Export")
            console.print("2. Exit")
            
            choice = Prompt.ask("[bold green]Choose an option[/bold green]", choices=["1", "2"])
            
            if choice == "1":
                reading_list_code = Prompt.ask("[bold green]Enter reading list code to export[/bold green]")
                if not reading_list_code:
                    console.print("[red]Please enter a valid reading list code.[/red]")
                    continue

                with console.status(f"[bold green]Searching for reading list with code '{reading_list_code}'...[/bold green]"):
                    manga_list = get_manga_list(reading_list_code)

                if not manga_list:
                    console.print("[yellow]No reading lisyt found.[/yellow]")
                    continue
                
                table = Table(title=f"Reading List")
                table.add_column("Title", style="cyan", no_wrap=True)
                table.add_column("Creator", style="magenta")
                table.add_column("Date Created", style="blue")
                table.add_column("Entries", style="white")
                table.add_column("Description", style="green")
                table.add_column("Tags", style="yellow")
                
                table.add_row(
                    manga_list.title,
                    manga_list.creator,
                    manga_list.creation_date,
                    str(len(manga_list.entries)),
                    manga_list.description,
                    ", ".join(manga_list.tags)
                )
                console.print(table)

                # Check if list is not empty
                if not manga_list.entries:
                    console.print("Manga list is empty. Nothing to export.")
                    continue

                console.print("\n[bold]Export Options:[/bold]")
                console.print("1. Export to JSON")
                console.print("2. Export to CSV")
            
                user_input = Prompt.ask("[bold green]Choose an option[/bold green]", choices=["1", "2"])

                if user_input == "1":
                    with console.status("[bold green]Searching for manga details", spinner="dots"):
                        full_manga_list = get_manga_from_manga_list(manga_list)

                    with console.status("[bold green]Exporting to JSON...", spinner="dots"):
                        import_data_to_json(full_manga_list, SAVE_PATH_JSON)
                    
                    console.print("[green]Success! Export file saved to 'saves/json' folder[/green].")
                    continue
                elif user_input == "2":
                    with console.status("[bold green]Searching for manga details", spinner="dots"):
                        full_manga_list = get_manga_from_manga_list(manga_list)
                    
                    with console.status("[bold green]Exporting to CSV...", spinner="dots"):
                        import_data_to_csv(manga_list, SAVE_PATH_CSV)
                    
                    console.print("[green]Success! Export file saved to 'saves/csv' folder[/green].")
                    continue

            elif choice == "2":
                break
        
        except Exception as e:
            console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")
        finally:
            pass

        if not Confirm.ask("\n[bold green]Would you like to export another manga list?[/bold green]"):
            break
    
    console.print("\n[bold blue]Thank you for using Mangago Reading List Exporter! 📚[/bold blue]")

if __name__ == "__main__":
    app()