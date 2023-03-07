import requests
import argparse
import os
import configparser
import sys



def parse_arguments():
    parser = argparse.ArgumentParser(description="Get TV show episode information from TMDB")
    parser.add_argument("--tv", type=str, help="Name of the TV show")
    parser.add_argument("--movie", type=str, help="Name of the movie")
    parser.add_argument("--season", type=str, help="Season of the TV syhow")
    parser.add_argument("--target", type=str, help="Target dir of the TV show")
    parser.add_argument("--year", type=str, help="The movie released year")
    return parser.parse_args()



def get_id(search_query, api_key):
    """
    get the first matched tv show id.
    """
    url = f"https://api.themoviedb.org/3/search/tv?api_key={api_key}&language=zh-CN&query={search_query}"
    try:
        response = requests.get(url)
        response_data = response.json()
        results = response_data.get("results")
    except:
        print('network requests error')
    if results is not None:
        for result in results:
            if result['id'] is not None:
                print(f"{result['name']} ({result['id']})")
                return result['id']
    else:
        print('can not get the id, check the name.')
        
    
def get_movie_info(movie_name, api_key, year=''):
    """
    according name and year to search movies info.
    """
    params = {
        'api_key': api_key,
        'query': movie_name,
        'year': year,
        'language': 'zh-CN'
    }
    url = "https://api.themoviedb.org/3/search/movie"
    response = requests.get(url, params=params).json()
    if 'results' in response and response['results']:
        result = response['results'][0]
        movie_id = result['id']
        movie_title = result['title']
        year = result['release_date'][:4]
        print(f'Movie found: {movie_title} (ID: {movie_id}) (year: {year})')
        return movie_title, year
    else:
        print('Movie not found.')

    

def get_episodes(id, season_number, api_key):
    """
    get list of the episodes
    """
    url = f"https://api.themoviedb.org/3/tv/{id}/season/{season_number}?api_key={api_key}&language=zh-CN"
    try:
        response = requests.get(url)
        response_data = response.json()
        episodes = response_data.get("episodes")
    except:
        print('get episodes error')
    return episodes


def get_local_episodes(target_dir):
    """
    get the local episode name exclude suffix name.
    """
    names = [name for name in os.listdir(target_dir)
            if os.path.isfile(os.path.join(target_dir, name))
            and name.endswith(('mp4', 'mkv'))]
    return names


def rename(target, destination_name, source_name=None, season_dir=None, movie_dir=None):
    """
    rename the media files depends on tv show or movies.
    """
    if season_dir:
        try:
            os.rename(f"{target}/{source_name}", f"{target}/{season_dir}/{destination_name}")
        except OSError as e:
            print("error occurred while renaming tv show")
    elif movie_dir:
        try:
            file_path = os.path.abspath(target)
            parent_path = os.path.dirname(os.path.dirname(file_path))
            os.rename(f"{target}", f"{parent_path}/{movie_dir}/{destination_name}")
        except OSError as e:
            print("error occurred while renaming movie")
    else:
        print("Not found the dir to change.")



def formatted_name(season_number, episode_number):
     return f"Episode S{int(season_number):02}E{episode_number:02}"


def create_dir(target, season_number=None, movie_name='', year=''):
    """
    create dir at the target dir when has season_number else
    create dir at the parent target dir.
    """
    if season_number:
        if os.path.isdir(target):
            created_dir = f"Season {int(season_number):02}"
            try:
                os.mkdir(f"{target}/{created_dir}")
            except FileExistsError:
                print("target dir already exists.")
        else:
            print("target is not dir")
            return None
    else:
        if os.path.isfile(target):
            created_dir = f"{movie_name} ({year})"
            try:
                file_path = os.path.abspath(target)
                parent_path = os.path.dirname(os.path.dirname(file_path))
                os.mkdir(f"{parent_path}/{created_dir}")
            except FileExistsError:
                print("target dir already exists.")
        else:
            print('target is not file.')
            return None
    return created_dir


def main(api_key):

    search_query = parse_arguments().tv
    season_number = parse_arguments().season
    target = parse_arguments().target
    movie_name = parse_arguments().movie
    year = parse_arguments().year


    if movie_name:
        movie_title, year = get_movie_info(movie_name=movie_name, api_key=api_key, year=year)
        try:
            created_dir = create_dir(target=target , movie_name=movie_title, year=year)
        except:
            sys.exit(1)
        suffix_name = target.split('.')[-1]
        destination_name = movie_title + "." + suffix_name
        rename(target=target, destination_name=destination_name, movie_dir=created_dir)
    else:
        id = get_id(search_query, api_key)
        episodes = get_episodes(id, season_number, api_key)
        local_episodes = sorted(get_local_episodes(target))
        suffix_name = local_episodes[0].split('.')[-1]
        try:
            created_dir = create_dir(target=target, season_number=season_number)
        except:
            sys.exit(1)
        if len(episodes) == len(local_episodes):
            for old_episode_name, episode in zip(local_episodes, episodes):
                new_name = formatted_name(season_number, episode['episode_number']) \
                + '-' + episode['name'] + '.' + suffix_name
                rename(target, season_dir=created_dir, source_name=old_episode_name, destination_name=new_name)
        else:
            print('error: local episodes number is defferent from the TMDB, check the information.')



if __name__ == '__main__':

    config = configparser.ConfigParser()
    config.read('config.ini')

    api_key = config.get('api', 'api_key')
    if len(api_key) != 32:
        print("please check the api key")
        sys.exit(1)
    main(api_key) 


