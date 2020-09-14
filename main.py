# -*- coding: utf-8 -*-

# Sample Python code for youtube.playlists.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python

import os, json, re, pickle, requests
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import errors, discovery
from google.auth.transport.requests import Request
import secrets as spotify_secrets

class Youtube :
    def __init__(self):
        self.scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "secret.json"

        # Get credentials and create an API client
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, self.scopes)
        # credentials = flow.run_console()
        credentials = self.get_credentials(flow)
        
        self.youtube_client = discovery.build(
            api_service_name, api_version, credentials=credentials)

    def get_credentials(self, flow) :
        creds = None
        
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        return creds


    def get_playlist_items(self) :

        request = self.youtube_client.playlistItems().list(
            part="contentDetails,snippet",
            maxResults=13,
            playlistId="PLEp1lyvf6DrKr5FBKQESMIdXTzsEvZT2Z"
        )
        response = request.execute()

        self.song_titles = []

        for res in response['items'] :
            title = res['snippet']['title']
            title = title.split('|')[0].strip()
            title = title.split('-')[0].strip() + ' ' + title.split('-')[1].strip() if len(title.split('-')) > 1 else title.split('-')[0].strip()

            # Removing brackets
            bracket_start = title.find('(')
            bracket_end = title.find(')')
            title = title.replace('(', ' ')
            title = title.replace(')', '')

            title = re.sub(title[bracket_start - 1:bracket_end + 1], '', title)

            # Corner Cases 
            if title.startswith('Dil Beparvah') : title = 'Dil Beparvah'
            elif title.startswith('Lucifer') : title = 'Creep Lucifer'
            elif title.startswith('Kadam') : title = 'Kadam'
            elif title.startswith('Kho gaye hum kahan') : title = 'Kho gaye hum kahan'
            elif title.startswith('Grant Gustin Running Home to You') : title = 'Grant Gustin Runnin Home to You'

            self.song_titles.append(title)

        return self.song_titles

class Spotify :
    def __init__(self, songs):
        self.token = spotify_secrets.SPOTIFY_TOKEN
        self.user_id = spotify_secrets.SPOTIFY_USER_ID
        self.songs = songs

    def find_songs(self) :
        found_songs = []

        url = 'https://api.spotify.com/v1/search?type=track'

        for song in self.songs :
            query = url + f"&q={re.sub(' ', '%20', song)}"

            response = requests.get(
                query,
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.token}'
                }
            )
            try :
                uri = response.json()['tracks']['items'][0]['uri']
            except Exception as e :
                print(e)
                print("Song:", re.sub(' ', '%20', song))
    
            found_songs.append(
                response.json()['tracks']['items'][0]['uri']
            )
    
        self.songs_searched = found_songs
        # print(found_songs)

    def create_or_find_playlist(self) :
        url = f'https://api.spotify.com/v1/users/{self.user_id}/playlists'

        response = requests.get(
            url,
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
        )

        for playlist in json.loads(response.content)['items'] :
            if playlist['name'] == 'From Youtube' :
                self.playlist_id = playlist['id']

        if not self.playlist_id :
            response = requests.post(
                url,
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.token}'
                },
                data = json.dumps({
                    'name': 'From Youtube',
                    'public': True,
                    'description': "Tracks automatically being added from Youtube from a python program."
                })
            )

            self.playlist_id = json.loads(response.content)['id']

    def add_songs_to_playlist(self) :
        url = f'https://api.spotify.com/v1/playlists/{self.playlist_id}/tracks'

        response = requests.post(
            url,
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            },
            data = json.dumps([
                    track for track in self.songs_searched
                ])
        )

        if response.status_code == 201 :
            print(f"{len(self.songs_searched)} Songs Added to Playlist Successfully")

        else :
            print(response.status_code, json.loads(response.content))

def main():

    youtube = Youtube()
    spotify = Spotify(youtube.get_playlist_items())
    spotify.find_songs()
    spotify.create_or_find_playlist()
    spotify.add_songs_to_playlist()
    
    # youtube.get_song_details()

if __name__ == "__main__":
    main()