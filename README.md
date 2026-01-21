# Mangago Reading List Exporter

A functional reading list exporter for Mangago.me with an interactive CLI feature. Supports exporting features to JSON and CSV format.

## Features

- 🔍 Access: Access reading list by code, displaying results with title, creator, description, tags, and total entries.
- ⬇️ Export: Save reading list into JSON and CSV format.
- ⌨️ Interface: Built with a **CLI (Command Line Interface)**, offering a fully interactive experience.

## Installation

1. Clone the repository:
   ```bash
   https://github.com/jmbacasno/Mangago-Reading-List-Exporter.git
   cd Mangago-Reading-List-Exporter
   ```

2. Install the required dependencies:
   ```bash
   pip install selenium beautifulsoup4 typer rich 
   ```

3. Install ChromeDriver:
   - Download ChromeDriver from https://chromedriver.chromium.org/
   - Add ChromeDriver to your system PATH
   - Or place ChromeDriver in the project directory

## Usage

### CLI Interface

Run the interactive CLI:
```bash
python -m cli.main
```

Or using the launcher:
```bash
python launcher.py
```

The CLI will guide you through:
1. Acessing reading list by code
2. Export by selecting format (JSON or CSV)

### Important Note

You can access your Mangago reading list code by visiting your list in your browser and copying the code from its URL.
```bash
https://www.mangago.me/home/mangalist/<reading_list_code>/
```

## Dependencies

- Python 3.11+
- Selenium (for web scraping)
- BeautifulSoup4 (for HTML parsing)
- Typer (for CLI)
- Rich (for CLI interface)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
