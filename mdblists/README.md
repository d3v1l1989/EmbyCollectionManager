# MDBList Collections

This directory contains text files that define custom movie collections using MDBList.com lists, TMDb IDs, and movie titles.

## How It Works

Each `.txt` file in this directory becomes a collection in your media server. The filename (without extension) becomes the collection name.

## Supported Formats

### 1. MDBList URLs
```
https://mdblist.com/lists/username/list-name
```

### 2. Direct TMDb IDs
```
550
680
13
```

### 3. Movie Titles
```
Fight Club
Pulp Fiction
The Matrix
```

### 4. Comments
Lines starting with `#` are ignored:
```
# This is a comment
550  # Fight Club (TMDb ID)
The Matrix  # Will be searched on TMDb
```

## Example File Structure

**File: `mdblists/My Favorite Action Movies.txt`**
```
# My favorite action movies collection
550  # Fight Club
https://mdblist.com/lists/actionfan/best-action-movies
The Matrix
John Wick
```

This would create a collection named "My Favorite Action Movies" with movies from:
- Fight Club (TMDb ID 550)
- All movies from the MDBList "best-action-movies" list
- The Matrix (searched by title)
- John Wick (searched by title)

## Configuration

MDBList processing can be configured in `config/config.yaml`:

```yaml
# MDBList API configuration (optional)
mdblist:
  api_key: "YOUR_MDBLIST_API_KEY"  # Get from https://mdblist.com/preferences

# MDBList local files configuration
mdblists:
  enabled: true                     # Enable/disable processing
  directory: "mdblists"            # Directory to scan for files
  max_items_per_collection: 0      # Max items per collection (0 = unlimited)
```

## Notes

- Files are processed in alphabetical order
- Duplicate movies are automatically removed
- If MDBList API key is not configured, MDBList URLs will be skipped
- Movie title searches use TMDb search and take the first (most relevant) result
- Custom poster templates are automatically generated for MDBList collections
- **Pagination Support**: Large MDBList collections are automatically fetched in batches of 1000 items
- **Unlimited by Default**: Collections have no size limit by default (fetches all items from MDBList)