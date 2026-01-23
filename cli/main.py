import sys
import os
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

CURRENT_DIR = Path.cwd()
SAVE_PATH = CURRENT_DIR / "saves"
SAVE_PATH_JSON = SAVE_PATH / "json"
SAVE_PATH_CSV = SAVE_PATH / "csv"

from src.models import MangaList
from src.parser import MANGA_LIST_URL_WITH_PAGE, parse_manga_list_info, get_manga_list_entries, parse_manga
from src.exporter import export_manga_list_to_json, export_manga_list_to_csv

from selenium import webdriver
from bs4 import BeautifulSoup, Tag

app = typer.Typer()
console = Console()

def app_get_initial_manga_list(console: Console, code: int):
    try:
        # Set web driver options
        options = webdriver.ChromeOptions()
        options.page_load_strategy = "eager"
        
        # Set web driver
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(10)

        # Load first page of manga list and get manga list with info
        with console.status("[bold green]Fetching manga details...", spinner="dots"):
            manga_list_url = MANGA_LIST_URL_WITH_PAGE.format(manga_list_code=code, page_no=1)
            driver.get(manga_list_url)
            manga_list_first_page_soup = BeautifulSoup(driver.page_source, "html.parser")
            manga_list = parse_manga_list_info(manga_list_first_page_soup)
            manga_list.url = manga_list_url

        # Get manga list entries for each page
        with Progress(SpinnerColumn(), TextColumn("Preparing manga list entries..."), BarColumn(), console=console) as progress:
            task = progress.add_task("Fetching entries...", total=manga_list.pages)
            manga_list_entries = []
            for page in range(1, manga_list.pages + 1):
                try: 
                    manga_list_entries.extend(get_manga_list_entries(driver, code, page))
                    progress.update(task, advance=1)
                except Exception as e:
                    console.print(f"\n[red]Error fetching manga list entries for page {page}: {e}[/red]")
                    break
        
        # Set manga list entries
        manga_list.entries = manga_list_entries

        return manga_list
    
    except Exception as e:
        console.print(f"\n[red]Error fetching manga list: {e}[/red]")
    
    finally:
        # Close web driver
        driver.quit()

def app_assign_manga_to_manga_list_entries(console: Console, manga_list: MangaList):
    try:
        # Set web driver options
        options = webdriver.ChromeOptions()
        options.page_load_strategy = "eager"
        
        # Set web driver
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(10)

        with Progress(SpinnerColumn(), TextColumn("Preparing manga details..."), BarColumn(), console=console) as progress:
            task = progress.add_task("Fetching details...", total=len(manga_list.entries))
            for manga_list_entry in manga_list.entries:
                driver.get(manga_list_entry.manga_url)
                manga_soup = BeautifulSoup(driver.page_source, "html.parser")
                manga = parse_manga(manga_soup)
                manga.url = manga_list_entry.manga_url
                manga_list_entry.manga = manga

                progress.update(task, advance=1)

        return manga_list
    
    except Exception as e:
        console.print(f"\n[red]Error fetching manga details: {e}[/red]")
    
    finally:
        # Close web driver
        driver.quit()

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
            console.print("1. Export reading list by code")
            console.print("2. Quit program")
            
            choice = Prompt.ask("\n[bold green]Choose an option[/bold green]", choices=["1", "2"])
            
            if choice == "1":
                reading_list_code = Prompt.ask("\n[bold green]Enter manga list code to export[/bold green]")
                if not reading_list_code:
                    console.print("\n[red]Please enter a valid manga list code.[/red]")
                    continue
                
                with console.status(f"[bold green]Searching for manga list with code '{reading_list_code}'...[/bold green]"):
                    manga_list = app_get_initial_manga_list(console, reading_list_code)

                if not manga_list:
                    console.print("\n[yellow]No manga list found.[/yellow]")
                    continue
                
                table = Table(title=f"\n{manga_list.title}")
                table.add_column("Creator", style="magenta")
                table.add_column("Date Created", style="blue")
                table.add_column("Entries", style="white")
                table.add_column("Description", style="green")
                table.add_column("Tags", style="yellow")
                
                table.add_row(
                    manga_list.creator,
                    manga_list.creation_date,
                    str(len(manga_list.entries)),
                    manga_list.description if manga_list.description else "N/A",
                    ", ".join(manga_list.tags) if manga_list.tags else "N/A",
                )
                console.print(table)

                if not manga_list.entries:
                    console.print("\n[yellow]Manga list is empty. Nothing to export.[/yellow]")
                    continue
                
                console.print("\n[bold]Export Options:[/bold]")
                console.print("1. Export to JSON")
                console.print("2. Export to CSV")

                user_input = Prompt.ask("\n[bold green]Choose an option[/bold green]", choices=["1", "2"])

                if user_input == "1":
                    with console.status("[bold green]Searching for manga details", spinner="dots"):
                        full_manga_list = app_assign_manga_to_manga_list_entries(console, manga_list)

                    with console.status("[bold green]Exporting to JSON...", spinner="dots"):
                        export_manga_list_to_json(full_manga_list, SAVE_PATH_JSON)
                    
                    console.print("\n[green]Success! Export file saved to 'saves/json' folder[/green].")
                    continue
                
                elif user_input == "2":
                    with console.status("[bold green]Searching for manga details", spinner="dots"):
                        full_manga_list = app_assign_manga_to_manga_list_entries(console, manga_list)
                    
                    with console.status("[bold green]Exporting to CSV...", spinner="dots"):
                        export_manga_list_to_csv(full_manga_list, SAVE_PATH_CSV)
                    
                    console.print("\n[green]Success! Export file saved to 'saves/csv' folder[/green].")
                    continue
            
            elif choice == "2":
                break
        
        except Exception as e:
            console.print(f"\n[bold red]An unexpected error occurred: {e}[/bold red]")
        finally:
            pass
        
        if not Confirm.ask("\n[bold green]Would you like to export another manga list?[/bold green]"):
            break
    
    console.print("\n[bold blue]Thank you for using Mangago Reading List Exporter! 📚[/bold blue]")

if __name__ == "__main__":
    app()
