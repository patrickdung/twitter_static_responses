Twitter static responses plugin for Pelican
-------------------------------------------
Uses Twitter V2 API

Options
-------

- TWITTER_DISPLAY_STATIC_RESPONSES = True
- TWITTER_BEARER_TOKEN = 'your-developer-api-token'
- TWITTER_USERNAME = 'your twitter username'
- TWITTER_STATS_CACHE_FILENAME = './twitter_stats/cache.json'
- # Not ready for the overwrite initial cache
- #TWITTER_STATS_OVERWRITE_INITIAL_CACHE = True
- #TWITTER_STATS_OVERWRITE_INITIAL_CACHE = False
- TWITTER_STATS_UPDATE_INITIAL_CACHE = True

Initial setup
-------------
Create a file 'twitter_stats/cache.json' with content:
{"data": []}

Notes
-----
This plugin references these plugins:

- `Pelican webmention <https://github.com/drivet/pelican-webmention>`__
- `Webmention static by Kappa <https://github.com/kappa-wingman/webmention_static_kappa>`__
- `Pelican plugins <https://github.com/getpelican/pelican-plugins>`__
