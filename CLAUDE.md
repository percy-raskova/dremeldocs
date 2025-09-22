# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Twitter/X data archive repository containing a personal data export from @BmoreOrganized. It's not a traditional development project but rather a data archive that may be used for analysis, documentation, or presentation purposes.

## Archive Structure

```
twitter-archives/
├── Your archive.html       # Main viewer - open in browser to explore data
├── data/                   # Twitter data files (70+ categories)
│   ├── manifest.js        # Defines data structure and file mappings
│   ├── account.js         # Account information
│   ├── tweets.js          # 21,723 tweets
│   ├── likes.js           # 88,679 liked tweets
│   └── [various].js       # Other data categories
└── assets/                # Static viewer assets
```

## Working with the Archive

### Viewing the Archive
```bash
# Open the archive viewer in default browser
open twitter-archives/Your\ archive.html
# Or on Linux:
xdg-open twitter-archives/Your\ archive.html
```

### Data Access Pattern
All data files follow this structure:
```javascript
window.YTD.category_name.part0 = [ /* array of data objects */ ]
```

### Key Data Files
- `tweets.js` - All tweets with full metadata
- `direct-messages.js` / `direct-messages-group.js` - Message history
- `follower.js` / `following.js` - Social graph data
- `tweet_media/` / `direct_messages_media/` - Associated media files

## Privacy and Security Considerations

- This archive contains personal data including private messages, login history, and device information
- Never commit sensitive modifications that could expose personal information
- Be cautious when analyzing or sharing insights from this data

## Common Analysis Tasks

### Extract Tweet Data
```bash
# Quick count of tweets
grep -o '"id_str"' twitter-archives/data/tweets.js | wc -l

# Extract tweet text (requires jq after converting to proper JSON)
node -e "const fs=require('fs'); const data=require('./twitter-archives/data/tweets.js'); console.log(JSON.stringify(window.YTD.tweets.part0))" > tweets.json
```

### Media File Locations
- Tweet media: `twitter-archives/data/tweets_media/`
- DM media: `twitter-archives/data/direct_messages_media/`
- Profile media: `twitter-archives/data/profile_media/`

## Data Statistics
- Total tweets: 21,723
- Liked tweets: 88,679
- Followers: 4,900
- Following: 2,005
- Blocked accounts: 412
- Date range: Archive generated September 21, 2025

## Important Notes

- This is a static archive with no build/test/deployment processes
- The HTML viewer works entirely client-side using the JavaScript data files
- Any development work would likely focus on data analysis or creating new visualization tools
- The archive follows Twitter/X's standard export format