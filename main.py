# -*- coding: utf-8 -*-

# Sample Python code for youtube.playlists.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python

import os, json, re
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from youtube_dl import YoutubeDL as ydl

class Youtube :
    def __init__(self):
        self.scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "secret.json"

        # Get credentials and create an API client
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, self.scopes)
        credentials = flow.run_console()
        
        self.youtube_client = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

    def get_playlist_items(self) :

        request = self.youtube_client.playlistItems().list(
            part="contentDetails,snippet",
            maxResults=13,
            playlistId="PLEp1lyvf6DrKr5FBKQESMIdXTzsEvZT2Z"
        )
        response = request.execute()

        self.song_details = []

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

            self.song_details.append(title)


def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.

    youtube = Youtube()
    youtube.get_playlist_items()
    # youtube.get_song_details()

if __name__ == "__main__":
    main()