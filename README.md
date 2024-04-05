# Nostalgix

A mish-mash set of tools for extracting insights and creating playlists from a spotify extended streaming history export.

This project contains utility functions and scripts to:

- Authenticate with spotify.
- Extract and process data from a spotify extended streaming history export to see insights like top artistes, top tracks played
- Create new playlists directly on spotify from the extracted data

This project is already suspended, feel free to fork if you want to do something useful with this, I wrote it to create personal playlists and have derived maximum utility from it, hence will not be able to actively maintain it.

Honestly, you're more likely to find it useful as a reference for how to create your own stuff with the spotify API and exported data.

### Getting your streaming history

Get an extended streaming history from Spotify. You can do this by sending an email to `	privacy@spotify.com` with the subject `Request for Extended Streaming History`. You will provide your spotify account details and to speed verification up, probably your last streaming device and song played. You will receive a download link in your email to download the data. The data contains multiple json files for all of your streaming history, likely partitioned by year. This may take a few weeks to arrive.

Once you have the data, to make things easier, you should concatenate all of the json data into one file. You can do this with python or by manually copying over.

### How to Use
To use the project, you will need to create a `.env` file in the root directory of the project with the following keys:

```env
SPOTIFY_CLIENT_ID=...
SPOTIFY_CLIENT_SECRET=...
SPOTIFY_STREAMING_HISTORY_COMBINED_FILE=...
```

- `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` are your spotify developer app credentials. You can create an app [here](https://developer.spotify.com/dashboard/applications).
- SPOTIFY_STREAMING_HISTORY_COMBINED_FILE is the path to the combined streaming history file you created earlier.


Next, run `python server.py` to start the server. This will open a browser window to authenticate with spotify. Once authenticated, an auth_response.json file will be created with your auth details. You can now terminate the server.
> Note: You may see a server error screen in your browser, this is expected (as long as the `auth_response.json` file is created, everything is fine), just close the tab.

You can now modify the app.py file to create any playlists you want by calling any of the pre-defined functions. You can also create your own functions to extract any insights you want from the streaming history data.

### I don't want to create playlists, I just want to see insights

There are `get` functions in app.py that you can use to get insights from your streaming history data. You can modify these functions to get any insights you want.
