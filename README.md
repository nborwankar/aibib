# AIBib - AI Bibliography Database

A structured bibliography database from "Artificial Intelligence: A Modern Approach" (AIMA) 4th edition, converted from BibTeX format to JSON and SQLite for easy querying and integration.

## Overview

This repository contains a comprehensive bibliography of academic references related to Artificial Intelligence and Machine Learning, originally from the AIMA 4th edition textbook. The data has been processed and made available in multiple formats:

- **BibTeX** - Original source format (`aima4e.bib`)
- **JSON** - Structured data with section categorization (`aima4e.json`)
- **SQLite** - Queryable database with indexed tables (`aima4e.db`)

## Contents

### Database Statistics

- **2,457 bibliographic citations** including:
  - 881 journal articles
  - 601 conference papers
  - 578 books
  - 157 miscellaneous entries
  - 139 book chapters
  - 65 technical reports
  - 32 PhD theses
  - And more

- **1,261 BibTeX string definitions** for:
  - 861 conference abbreviations
  - 246 publisher names
  - 87 anthology references
  - 43 journal names
  - 24 organizations and institutions

## Files

- `aima4e.bib` - Original BibTeX bibliography file (628KB+)
- `aima4e.json` - Structured JSON format with section categorization
- `aima4e.db` - SQLite database with indexed tables
- `bibtex_to_json.py` - Conversion script from BibTeX to JSON
- `create_database.py` - Database creation and population script
- `analyze_json.py` - JSON analysis utility

## Usage

### Querying the Database

```python
import sqlite3

# Connect to database
conn = sqlite3.connect('aima4e.db')
cursor = conn.cursor()

# Find all articles by a specific author
cursor.execute("""
    SELECT title, year, journal
    FROM citations
    WHERE author LIKE '%Russell%' AND type = 'article'
    ORDER BY year DESC
""")

for row in cursor.fetchall():
    print(row)
```

### Working with JSON

```python
import json

with open('aima4e.json', 'r') as f:
    data = json.load(f)

# Access conference citations
conferences = data['sections']['conferences']
print(f"Total conference entries: {len(conferences)}")
```

### Converting Custom BibTeX Files

```bash
# Convert your own BibTeX file
python bibtex_to_json.py your_file.bib output.json

# Create SQLite database from JSON
python create_database.py output.json your_database.db
```

## Database Schema

### Citations Table
Stores all bibliographic entries with fields including:
- `id` - Auto-incrementing primary key
- `type` - Entry type (article, book, inproceedings, etc.)
- `cite_key` - BibTeX citation key
- `section` - Source section categorization
- `author`, `title`, `year`, `journal`, `booktitle`, etc.
- Indexed on: `type`, `year`, `author`, `cite_key`

### String Definitions Table
Stores BibTeX @string definitions:
- `id` - Auto-incrementing primary key
- `key` - String definition key
- `value` - Replacement value
- `section` - Source section
- Indexed on: `key`, `section`

## Features

- **Complete Data Preservation** - All original BibTeX fields maintained
- **Section Categorization** - Records tagged with their source section
- **Performance Optimization** - Database indexes for common search patterns
- **Flexible Schema** - Accommodates variations in BibTeX formats
- **Error Handling** - Robust parsing for various BibTeX conventions

## Requirements

- Python 3.6+
- No external dependencies (uses only standard library)

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

Bibliography data sourced from "Artificial Intelligence: A Modern Approach" (AIMA) 4th edition by Stuart Russell and Peter Norvig.
