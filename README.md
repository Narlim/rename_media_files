Rename files according to jellyfin's media file format

## USAGE

get the api key from TMDB and fill in the `config.ini`

### for tv show or anine
example:
```
python format.py --tv 火影忍者 --season 1 --target '/mnt/anime/火影忍者'
```
will create dir like: `Season 01`, and remove episodes to the dir.

### for movies
example:
```
python format.py --movie 星际穿越 --year 2014 --target '/mnt/movies/星际穿越/星际穿越.mkv'
```
Note the difference between the 'target' of tv show and movies.