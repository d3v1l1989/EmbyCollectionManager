#!/usr/bin/env python3
"""
Script to remove duplicate collection entries from collection_recipes.py
"""
import re

def main():
    # Read the collection_recipes.py file
    with open('src/collection_recipes.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Additional duplicates found and their line numbers to remove (second occurrence)
    duplicates_to_remove = {
        # Franchise Collections
        209: 'Alien Collection',
        210: 'Die Hard Collection',
        211: 'Ghostbusters Collection',
        220: 'Iron Man Collection',
        231: 'Final Destination Collection',
        234: 'Captain America Collection',
        
        # Director Collections
        411: 'Alejandro González Iñárritu Collection',
        412: 'Greta Gerwig Collection',
        413: 'Ingmar Bergman Collection',
        414: 'Federico Fellini Collection',
        415: 'Billy Wilder Collection',
        416: 'John Carpenter Collection',
        417: 'Danny Boyle Collection',
        
        # Genre Collections
        350: 'Adventure & Fantasy Movies',
    }
    
    # Filter out the duplicate lines
    filtered_lines = []
    for i, line in enumerate(lines):
        # Lines are 0-indexed in the list, but 1-indexed in the file
        if (i + 1) not in duplicates_to_remove:
            filtered_lines.append(line)
    
    # Write the filtered content back to the file
    with open('src/collection_recipes.py', 'w', encoding='utf-8') as f:
        f.writelines(filtered_lines)
    
    # Note about Captain America & Iron Man Collection IDs
    note = """
Note: There was a discrepancy in the collection IDs for:
- Captain America Collection (131292 vs 131295)
- Iron Man Collection (131294 vs 131292)
Removed the duplicates and kept the original entries.
"""
    print(f"Successfully removed {len(duplicates_to_remove)} duplicate collections.")
    print(note)

if __name__ == "__main__":
    main()
