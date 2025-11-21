import json

with open('aima4e.json', 'r') as f:
    data = json.load(f)

# Get all unique citation types
citation_types = set()
for section_name, entries in data['sections'].items():
    for entry in entries:
        if entry['type'] != 'string':
            citation_types.add(entry['type'])

print('Citation types:')
for t in sorted(citation_types):
    print(f'  {t}')

# Count entries by type
type_counts = {}
for section_name, entries in data['sections'].items():
    for entry in entries:
        entry_type = entry['type']
        type_counts[entry_type] = type_counts.get(entry_type, 0) + 1

print('\nEntry counts by type:')
for t, count in sorted(type_counts.items()):
    print(f'  {t}: {count}')

# Sample some fields from different citation types
print('\nSample fields by citation type:')
samples = {}
for section_name, entries in data['sections'].items():
    for entry in entries:
        if entry['type'] != 'string' and entry['type'] not in samples:
            samples[entry['type']] = entry.get('fields', {})
        if len(samples) >= 5:  # Just get a few examples
            break

for cite_type, fields in samples.items():
    print(f'\n{cite_type} fields: {list(fields.keys())[:10]}...')  # Show first 10 fields