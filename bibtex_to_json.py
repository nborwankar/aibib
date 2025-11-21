#!/usr/bin/env python3
"""
Convert BibTeX file to JSON format with section categorization.
Parses the aima4e.bib file and converts it to a structured JSON format
that includes the record type based on section headers.
"""

import json
import re
from typing import Dict, List, Any, Optional


class BibtexToJsonConverter:
    def __init__(self):
        self.current_section = "unknown"
        self.sections = {
            "journals": [],
            "publishers": [],
            "organizations": [],
            "schools_and_institutions": [],
            "conferences": [],
            "anthologies": [],
            "unknown": []
        }
        
    def normalize_section_name(self, section_name: str) -> str:
        """Convert section header to normalized key name."""
        section_map = {
            "JOURNALS": "journals",
            "PUBLISHERS": "publishers", 
            "ORGANIZATIONS": "organizations",
            "SCHOOLS AND INSTITUTIONS": "schools_and_institutions",
            "CONFERENCES": "conferences",
            "ANTHOLOGIES": "anthologies"
        }
        return section_map.get(section_name, "unknown")
    
    def parse_bibtex_entry(self, entry_text: str) -> Optional[Dict[str, Any]]:
        """Parse a single BibTeX entry and return structured data."""
        entry_text = entry_text.strip()
        if not entry_text:
            return None
            
        # Match @string{key = "value"} entries
        string_match = re.match(r'@string\{([^=]+)\s*=\s*"([^"]+)"\}', entry_text, re.IGNORECASE)
        if string_match:
            key, value = string_match.groups()
            return {
                "type": "string",
                "key": key.strip(),
                "value": value.strip(),
                "section": self.current_section
            }
        
        # Match other BibTeX entries like @article, @book, @inproceedings, etc.
        entry_match = re.match(r'@(\w+)\{([^,\s}]+)[,\s]*(.*)', entry_text, re.DOTALL | re.IGNORECASE)
        if entry_match:
            entry_type, entry_key, entry_body = entry_match.groups()
            
            # Clean up entry body - remove trailing }
            entry_body = entry_body.rstrip().rstrip('}')
            
            # Parse fields from entry body
            fields = {}
            
            # Enhanced field parsing to handle various formats
            # Handle quoted fields: field = "value"
            field_pattern = r'(\w+)\s*=\s*"([^"]*)"'
            for field_match in re.finditer(field_pattern, entry_body):
                field_name, field_value = field_match.groups()
                fields[field_name.strip().lower()] = field_value.strip()
            
            # Handle braced fields: field = {value} (with nested braces)
            field_start = 0
            while field_start < len(entry_body):
                brace_match = re.search(r'(\w+)\s*=\s*\{', entry_body[field_start:])
                if not brace_match:
                    break
                    
                field_name = brace_match.group(1).lower()
                brace_start = field_start + brace_match.end() - 1  # Position of opening brace
                
                # Find matching closing brace
                brace_count = 1
                pos = brace_start + 1
                while pos < len(entry_body) and brace_count > 0:
                    if entry_body[pos] == '{':
                        brace_count += 1
                    elif entry_body[pos] == '}':
                        brace_count -= 1
                    pos += 1
                
                if brace_count == 0:
                    field_value = entry_body[brace_start + 1:pos - 1]
                    fields[field_name] = field_value.strip()
                    field_start = pos
                else:
                    field_start += brace_match.end()
            
            # Handle unquoted fields: field = value (for numbers, variables)
            unquoted_pattern = r'(\w+)\s*=\s*([^,}\s][^,}]*?)(?=\s*[,}])'
            for field_match in re.finditer(unquoted_pattern, entry_body):
                field_name, field_value = field_match.groups()
                field_name = field_name.strip().lower()
                field_value = field_value.strip()
                # Only add if not already captured by quoted/braced patterns
                if field_name not in fields and not field_value.startswith(('"', '{')):
                    fields[field_name] = field_value
            
            return {
                "type": entry_type.lower(),
                "key": entry_key.strip(),
                "fields": fields,
                "section": self.current_section
            }
        
        return None
    
    def convert_file(self, input_file: str, output_file: str):
        """Convert BibTeX file to JSON format."""
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Split into lines for processing
        lines = content.split('\n')
        
        current_entry = []
        brace_count = 0
        in_entry = False
        
        for line in lines:
            stripped_line = line.strip()
            
            # Check for section headers
            section_match = re.match(r'%\[([^\]]+)\]', stripped_line)
            if section_match:
                section_name = section_match.group(1)
                self.current_section = self.normalize_section_name(section_name)
                continue
            
            # Skip empty lines and comments (except section headers)
            if not stripped_line or (stripped_line.startswith('%') and not stripped_line.startswith('%[')):
                continue
            
            # Check if starting a new entry
            if stripped_line.startswith('@'):
                # If we were in an entry, process it first
                if current_entry and in_entry:
                    entry_text = ' '.join(current_entry)
                    parsed_entry = self.parse_bibtex_entry(entry_text)
                    
                    if parsed_entry:
                        section_key = parsed_entry["section"]
                        if section_key in self.sections:
                            self.sections[section_key].append(parsed_entry)
                        else:
                            self.sections["unknown"].append(parsed_entry)
                
                # Start new entry
                current_entry = [stripped_line]
                brace_count = stripped_line.count('{') - stripped_line.count('}')
                in_entry = True
            elif in_entry:
                # Continue current entry
                current_entry.append(stripped_line)
                brace_count += stripped_line.count('{') - stripped_line.count('}')
            
            # When braces are balanced and we're in an entry, process it
            if brace_count == 0 and current_entry and in_entry:
                entry_text = ' '.join(current_entry)
                parsed_entry = self.parse_bibtex_entry(entry_text)
                
                if parsed_entry:
                    section_key = parsed_entry["section"]
                    if section_key in self.sections:
                        self.sections[section_key].append(parsed_entry)
                    else:
                        self.sections["unknown"].append(parsed_entry)
                
                current_entry = []
                in_entry = False
        
        # Handle any remaining entry
        if current_entry and in_entry:
            entry_text = ' '.join(current_entry)
            parsed_entry = self.parse_bibtex_entry(entry_text)
            
            if parsed_entry:
                section_key = parsed_entry["section"]
                if section_key in self.sections:
                    self.sections[section_key].append(parsed_entry)
                else:
                    self.sections["unknown"].append(parsed_entry)
        
        # Write to JSON file
        output_data = {
            "metadata": {
                "source_file": input_file,
                "total_entries": sum(len(entries) for entries in self.sections.values()),
                "sections": {k: len(v) for k, v in self.sections.items()}
            },
            "sections": self.sections
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"Converted {output_data['metadata']['total_entries']} entries to {output_file}")
        print("Section breakdown:")
        for section, count in output_data['metadata']['sections'].items():
            print(f"  {section}: {count} entries")


def main():
    """Main function to run the conversion."""
    converter = BibtexToJsonConverter()
    converter.convert_file('aima4e.bib', 'aima4e.json')


if __name__ == "__main__":
    main()