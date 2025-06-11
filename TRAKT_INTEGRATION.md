# Trakt.tv Integration Guide

This guide explains how to set up and use the Trakt.tv integration with TMDbCollector to create collections based on your Trakt lists, watchlists, and collections.

## Overview

The Trakt integration allows you to:
- Create collections from your Trakt watchlist
- Create collections from your Trakt collection
- Create collections from any public Trakt list
- Use trending and popular Trakt lists
- Mix Trakt sources with manual TMDb IDs in custom lists

## Setup

### 1. Create a Trakt Application

1. Go to [https://trakt.tv/oauth/applications](https://trakt.tv/oauth/applications)
2. Click "New Application"
3. Fill in the required fields:
   - **Name**: Your application name (e.g., "TMDbCollector")
   - **Description**: Brief description
   - **Redirect URI**: For local use, you can use `urn:ietf:wg:oauth:2.0:oob`
4. Save and note your **Client ID** and **Client Secret**

### 2. Configure TMDbCollector

Add the Trakt configuration to your `config/config.yaml`:

```yaml
# Trakt configuration
trakt:
  client_id: "YOUR_TRAKT_CLIENT_ID"
  client_secret: "YOUR_TRAKT_CLIENT_SECRET"
  access_token: "YOUR_TRAKT_ACCESS_TOKEN"  # Optional, see OAuth section
  username: "YOUR_TRAKT_USERNAME"  # Optional, for accessing specific user lists
```

### 3. OAuth Authentication (Optional)

For accessing private lists, watchlists, and collections, you need an access token:

#### Method 1: Manual OAuth Flow
1. Generate an authorization URL using the Trakt client
2. Visit the URL and authorize your application
3. Exchange the authorization code for an access token
4. Add the access token to your config file

#### Method 2: Public Lists Only
If you only want to use public Trakt lists, you can omit the `access_token` and `client_secret` fields.

## Usage

### Recipe-Based Collections

The Trakt integration extends the existing recipe system with new source types:

#### Available Source Types

1. **`trakt_watchlist`** - Your Trakt watchlist
2. **`trakt_collection`** - Your Trakt collection  
3. **`trakt_list`** - Specific user's list
4. **`trakt_trending_list`** - Currently trending lists
5. **`trakt_popular_list`** - Popular lists

#### Example Recipes

Add these to your `collection_recipes.py` or use them as templates:

```python
# Your personal watchlist
{
    "name": "My Trakt Watchlist",
    "source_type": "trakt_watchlist",
    "target_servers": ['emby'],
    "category_id": 12,
    "description": "Movies from your Trakt watchlist"
}

# Specific user's list
{
    "name": "Top 250 Movies",
    "source_type": "trakt_list",
    "trakt_list_params": {
        "username": "lish408",
        "list_slug": "top-250-movies"
    },
    "target_servers": ['emby'],
    "category_id": 12,
    "item_limit": 100
}

# Trending movies from popular lists
{
    "name": "Trakt Trending Movies",
    "source_type": "trakt_trending_list",
    "item_limit": 50,
    "target_servers": ['emby'],
    "category_id": 12
}
```

### Custom Lists with Trakt Integration

The custom lists feature now supports Trakt references alongside TMDb IDs:

#### Example Custom List

```yaml
---
# Custom list mixing TMDb IDs and Trakt sources
- name: "My Ultimate Collection"
  description: "Personal picks plus community favorites"
  items:
    # Direct TMDb IDs
    - 550    # Fight Club
    - 13     # Forrest Gump
    
    # From a specific Trakt list
    - trakt_list:
        username: "movielover"
        list_slug: "hidden-gems"
    
    # From your personal watchlist
    - trakt_watchlist:
        username: "me"
    
    # More TMDb IDs
    - 680    # Pulp Fiction
    - 11     # Star Wars
```

#### Supported Custom List Item Types

1. **Direct TMDb ID**: `- 12345`
2. **TMDb ID with metadata**: `- id: 12345`
3. **Trakt list reference**: 
   ```yaml
   - trakt_list:
       username: "username"
       list_slug: "list-slug"
   ```
4. **Trakt watchlist reference**:
   ```yaml
   - trakt_watchlist:
       username: "username"  # Use "me" for authenticated user
   ```

## Configuration Options

### Recipe Parameters

- **`item_limit`**: Maximum number of items to fetch (default: 50)
- **`trakt_list_params`**: Parameters for specific list access
  - `username`: Trakt username
  - `list_slug`: List slug/identifier

### Authentication Levels

1. **Public Only**: Only `client_id` required
   - Can access public lists
   - Cannot access personal watchlists/collections

2. **Full Access**: `client_id`, `client_secret`, and `access_token` required
   - Can access personal watchlists and collections
   - Can access private lists (if permitted)

## Finding Trakt Lists

### Popular Lists
- Browse [Trakt's list section](https://trakt.tv/lists)
- Look for highly-rated community lists
- Note the username and list slug from the URL

### List URL Format
Trakt list URLs follow this pattern:
```
https://trakt.tv/users/{username}/lists/{list-slug}
```

For example:
- URL: `https://trakt.tv/users/lish408/lists/top-250-movies`
- Username: `lish408`
- List slug: `top-250-movies`

## Troubleshooting

### Common Issues

1. **"Trakt client not configured"**
   - Ensure `client_id` is set in config
   - Check for typos in configuration

2. **"Authentication failed"**
   - Verify your `access_token` is valid
   - Check if token has expired (tokens are long-lived but can expire)

3. **"No TMDb ID found for movie"**
   - Some Trakt entries may not have TMDb mappings
   - This is normal and those items will be skipped

4. **Rate limiting**
   - Trakt allows 1000 requests per 5 minutes
   - Large lists may take time to process
   - The client includes automatic rate limiting

### Debugging

Enable debug logging to see detailed Trakt API interactions:

```python
import logging
logging.getLogger("TraktClient").setLevel(logging.DEBUG)
```

## Best Practices

1. **Start Small**: Test with small lists before using large collections
2. **Use Item Limits**: Prevent overwhelming your media server with huge collections
3. **Cache Results**: The application handles API rate limiting automatically
4. **Monitor Logs**: Check logs for any skipped items or API issues
5. **Regular Updates**: Re-run periodically to keep collections current

## Example Configurations

### Minimal Configuration (Public Lists Only)
```yaml
trakt:
  client_id: "your_client_id_here"
```

### Full Configuration (Personal Access)
```yaml
trakt:
  client_id: "your_client_id_here"
  client_secret: "your_client_secret_here"
  access_token: "your_access_token_here"
  username: "your_username"
```

## Security Notes

- Keep your `client_secret` and `access_token` private
- Use environment variables for sensitive credentials in production
- Regularly rotate access tokens if needed
- The `client_id` can be safely shared as it's public

## Support

For issues specific to Trakt integration:
1. Check the logs for detailed error messages
2. Verify your Trakt credentials and permissions
3. Test with smaller lists first
4. Ensure your TMDb integration is working properly

The Trakt integration builds on top of the existing TMDb functionality, so a working TMDb setup is required.