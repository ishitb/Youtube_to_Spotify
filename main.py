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
        self.songs = songs

    def find_songs(self) :
        found_songs = []

        url = 'https://api.spotify.com/v1/search?type=track'

        for song in self.songs :
            query = url + f"&q={re.sub(' ', '%20', song.lower())}"

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
                print("Song:", re.sub(' ', '%20', song.lower()))
    
            found_songs.append(
                response.json()['tracks']['items'][0]['uri']
            )
    
        print(found_songs)

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.

    youtube = Youtube()
    spotify = Spotify(youtube.get_playlist_items())
    spotify.find_songs()
    
    # youtube.get_song_details()

if __name__ == "__main__":
    main()