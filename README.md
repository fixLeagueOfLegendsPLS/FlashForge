# FlashForge

**A local Quizlet alternative without any limitations.**

FlashForge is a fully offline desktop flashcard application that lets you create, import, and study flashcards with absolutely no restrictions on text length, card count, or deck size.

## Features

### No Limits
- **Unlimited text length** - Cards can contain any amount of text
- **Unlimited cards per deck** - Add as many cards as you need
- **Unlimited decks** - Organize your learning without restrictions
- **100% offline** - All data stored locally, no account required

### Smart Import System
- **Universal importer** with customizable delimiters
- **Auto-detection** of file format and separators
- **Preview before import** - See exactly how cards will look
- Support for: TXT, CSV, TSV, JSON, Anki, Quizlet exports
- **Custom separators** including multi-character (e.g., `::`, `|||`)

### Multiple Study Modes
- **Flashcards** - Classic flip-card study with keyboard shortcuts
- **Learn** - Spaced repetition with SM-2 algorithm
- **Write** - Type answers with typo tolerance
- **Test** - Multiple choice, true/false, and written tests
- **Match** - Connect terms with definitions

### Modern Interface
- **Dark, Light, and AMOLED** themes
- Customizable accent colors
- Smooth animations
- Keyboard shortcuts for power users

### Progress Tracking
- Daily statistics and streaks
- Activity heatmap (GitHub-style)
- Per-deck progress tracking
- Achievement system

## Installation

### From Release (Recommended)

Download the latest release for your platform:
- **Windows**: `FlashForge.exe`
- **macOS**: `FlashForge.app`
- **Linux**: `FlashForge`

### From Source

1. Clone the repository:
```bash
git clone https://github.com/yourusername/flashforge.git
cd flashforge
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python src/main.py
```

## Building from Source

To create a standalone executable:

```bash
# Standard build (single file)
python build.py

# Build as directory
python build.py --onedir

# Debug build (with console)
python build.py --debug

# Create portable version
python build.py --portable
```

The output will be in the `dist` folder.

## Usage

### Creating a Deck

1. Click **"+ Create Deck"** on the home screen
2. Enter a name and optional description
3. Choose an icon and color
4. Start adding cards

### Importing Cards

1. Click **"Import"** in the sidebar
2. Select your file
3. Configure separators if needed (or use auto-detect)
4. Preview the cards
5. Click **"Import"**

**Supported formats:**
- Text files with custom delimiters
- CSV and TSV files
- JSON files
- Quizlet exports (copy-paste)
- Anki exports

### Keyboard Shortcuts

**Global:**
- `Ctrl+N` - New deck
- `Ctrl+I` - Import
- `Ctrl+E` - Export
- `Ctrl+F` - Search
- `Ctrl+,` - Settings
- `Ctrl+Q` - Quit

**Study Mode:**
- `Space` - Flip card
- `←` / `1` - Don't know
- `→` / `4` - Know
- `2` - Hard (Learn mode)
- `3` - Good (Learn mode)
- `S` - Star card
- `H` - Show hint
- `E` - Edit card
- `Esc` - Exit

## Data Storage

Your data is stored locally in:
- **Windows**: `%APPDATA%/FlashForge/`
- **macOS**: `~/Library/Application Support/FlashForge/`
- **Linux**: `~/.local/share/FlashForge/`

For **portable mode**, place a `data` folder next to the executable.

## Technology

- **Python 3.11+**
- **CustomTkinter** - Modern UI framework
- **SQLAlchemy** - Database ORM
- **SQLite** - Local database
- **Pillow** - Image support
- **PyInstaller** - Executable packaging

## Project Structure

```
flashforge/
├── src/
│   ├── main.py              # Entry point
│   ├── app.py               # Main application
│   ├── database/            # SQLAlchemy models & manager
│   ├── ui/
│   │   ├── theme.py         # Theme system
│   │   ├── components/      # Reusable UI components
│   │   └── screens/         # Application screens
│   ├── core/
│   │   ├── importer.py      # Card import logic
│   │   ├── exporter.py      # Card export logic
│   │   ├── study_engine.py  # SM-2 & Leitner algorithms
│   │   └── statistics.py    # Progress tracking
│   └── utils/               # Configuration & helpers
├── assets/                  # Icons, sounds, fonts
├── tests/                   # Test suite
├── build.py                 # Build script
└── requirements.txt
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Running Tests

```bash
pytest tests/ -v
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by Quizlet, Anki, and other flashcard applications
- Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- SM-2 algorithm by Piotr Wozniak

---

Made with love for learners everywhere.
