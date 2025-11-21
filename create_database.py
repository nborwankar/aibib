#!/usr/bin/env python3
"""
Create SQLite database from the JSON bibliography data.
"""

import json
import sqlite3
from typing import Dict, Any


def create_schema(cursor):
    """Create the database schema."""
    
    # Citations table for bibliographic entries
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS citations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            citation_key TEXT NOT NULL,
            entry_type TEXT NOT NULL,
            section TEXT NOT NULL,
            
            -- Core bibliographic fields
            title TEXT,
            author TEXT,
            year TEXT,
            
            -- Publication venue fields
            journal TEXT,
            booktitle TEXT,
            publisher TEXT,
            
            -- Volume/pagination fields  
            volume TEXT,
            number TEXT,
            issue TEXT,
            pages TEXT,
            chapter TEXT,
            
            -- Editorial fields
            editor TEXT,
            editors TEXT,
            edition TEXT,
            series TEXT,
            
            -- Institutional fields
            school TEXT,
            institution TEXT,
            organization TEXT,
            
            -- Location fields
            address TEXT,
            location TEXT,
            city TEXT,
            
            -- Publication details
            month TEXT,
            day TEXT,
            date TEXT,
            howpublished TEXT,
            note TEXT,
            
            -- Identifiers and URLs
            doi TEXT,
            isbn TEXT,
            issn TEXT,
            url TEXT,
            bibsource TEXT,
            biburl TEXT,
            timestamp TEXT,
            
            -- Misc fields
            numpages TEXT,
            acmid TEXT,
            issue_date TEXT,
            source TEXT,
            original TEXT,
            comment TEXT,
            priority TEXT
        )
    """)
    
    # String definitions table for @string entries
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS string_definitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            definition_key TEXT NOT NULL,
            value TEXT NOT NULL,
            section TEXT NOT NULL
        )
    """)


def create_indexes(cursor):
    """Create indexes for performance."""
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_citations_type ON citations(entry_type)",
        "CREATE INDEX IF NOT EXISTS idx_citations_section ON citations(section)",
        "CREATE INDEX IF NOT EXISTS idx_citations_author ON citations(author)",
        "CREATE INDEX IF NOT EXISTS idx_citations_year ON citations(year)",
        "CREATE INDEX IF NOT EXISTS idx_citations_journal ON citations(journal)",
        "CREATE INDEX IF NOT EXISTS idx_string_section ON string_definitions(section)",
        "CREATE INDEX IF NOT EXISTS idx_string_key ON string_definitions(definition_key)"
    ]
    
    for index_sql in indexes:
        cursor.execute(index_sql)


def insert_citation(cursor, entry: Dict[str, Any]):
    """Insert a citation entry into the database."""
    
    # Extract basic info
    citation_key = entry.get('key', '')
    entry_type = entry.get('type', '')
    section = entry.get('section', '')
    
    # Extract all possible fields from the 'fields' dict
    fields = entry.get('fields', {})
    
    # Prepare the INSERT statement with all possible columns
    columns = [
        'citation_key', 'entry_type', 'section',
        'title', 'author', 'year', 'journal', 'booktitle', 'publisher',
        'volume', 'number', 'issue', 'pages', 'chapter',
        'editor', 'editors', 'edition', 'series',
        'school', 'institution', 'organization',
        'address', 'location', 'city',
        'month', 'day', 'date', 'howpublished', 'note',
        'doi', 'isbn', 'issn', 'url', 'bibsource', 'biburl', 'timestamp',
        'numpages', 'acmid', 'issue_date', 'source', 'original', 'comment', 'priority'
    ]
    
    values = [citation_key, entry_type, section]
    
    # Add field values in the same order as columns (skipping first 3 which are already added)
    for col in columns[3:]:
        values.append(fields.get(col, None))
    
    placeholders = ', '.join(['?' for _ in columns])
    sql = f"INSERT INTO citations ({', '.join(columns)}) VALUES ({placeholders})"
    
    cursor.execute(sql, values)


def insert_string_definition(cursor, entry: Dict[str, Any]):
    """Insert a string definition into the database."""
    
    definition_key = entry.get('key', '')
    value = entry.get('value', '')
    section = entry.get('section', '')
    
    cursor.execute("""
        INSERT INTO string_definitions (definition_key, value, section)
        VALUES (?, ?, ?)
    """, (definition_key, value, section))


def populate_database(json_file: str, db_file: str):
    """Create and populate the SQLite database."""
    
    # Load JSON data
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    try:
        # Create schema
        print("Creating database schema...")
        create_schema(cursor)
        
        # Process all entries
        citation_count = 0
        string_count = 0
        
        print("Populating database...")
        for section_name, entries in data['sections'].items():
            for entry in entries:
                if entry['type'] == 'string':
                    insert_string_definition(cursor, entry)
                    string_count += 1
                else:
                    insert_citation(cursor, entry)
                    citation_count += 1
        
        # Create indexes
        print("Creating indexes...")
        create_indexes(cursor)
        
        # Commit changes
        conn.commit()
        
        print(f"Database created successfully!")
        print(f"  Citations: {citation_count}")
        print(f"  String definitions: {string_count}")
        print(f"  Database file: {db_file}")
        
        # Show some sample data
        print("\nSample citations:")
        cursor.execute("SELECT citation_key, entry_type, title, author, year FROM citations LIMIT 3")
        for row in cursor.fetchall():
            print(f"  {row[0]} ({row[1]}): {row[2]} by {row[3]} ({row[4]})")
        
        print("\nSample string definitions:")
        cursor.execute("SELECT definition_key, value, section FROM string_definitions LIMIT 3")
        for row in cursor.fetchall():
            print(f"  {row[0]} = '{row[1]}' (from {row[2]})")
            
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    populate_database('aima4e.json', 'aima4e.db')