from flask import Flask, request, jsonify
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

app = Flask(__name__)

@app.route('/recommend_wp', methods=['POST'])
def recommend_songs():
    # Spotify API anahtarlarınızı buraya ekleyin
    client_id = 'bc6f5a71013f4155a0874aebe0100635'
    client_secret = '98a1134230354a64ac77120d3572a6bb'

    # API kimlik doğrulaması
    client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Veri setini oluşturma
    playlist_id_dataset = '6fFu08cB9yTyGVJ95o5nua'
    dataset_playlist = sp.playlist(playlist_id_dataset)
    dataset_tracks = dataset_playlist["tracks"]["items"]
    dataset_ids = []
    dataset_names = []
    dataset_artists = []
    for track in dataset_tracks:
        if track["track"]:
            dataset_ids.append(track["track"]["id"])
            dataset_names.append(track["track"]["name"])
            artist = track["track"]["artists"][0]["name"]
            dataset_artists.append(artist)
    dataset_features = sp.audio_features(dataset_ids)
    dataset_df = pd.DataFrame(dataset_features)
    dataset_df["name"] = dataset_names
    dataset_df["artist"] = dataset_artists
    dataset_df = dataset_df.drop(['analysis_url', 'track_href', 'type', 'uri', 'id'], axis=1)
    dataset_df = dataset_df[
        ['name', 'artist', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness',
         'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms']]
    dataset_df.to_csv('spotify_dataset.csv', index=False)

    # Özellikleri ölçeklendirme
    scaler = StandardScaler()
    X = dataset_df.drop(['name', 'artist'], axis=1)
    X = scaler.fit_transform(X)

    # Modeli oluşturma
    model = NearestNeighbors(n_neighbors=10, algorithm='ball_tree')
    model.fit(X)

    # Kullanıcının çalma listesini alın
    playlist_id = request.json['playlist_id']
    playlist = sp.playlist(playlist_id)
    playlist_tracks = playlist["tracks"]["items"]

    user_ids = []
    user_names = []
    user_artists = []
    for track in playlist_tracks:
        if track["track"]:
            user_ids.append(track["track"]["id"])
            user_names.append(track["track"]["name"])
            artist = track["track"]["artists"][0]["name"]
            user_artists.append(artist)

    user_features = sp.audio_features(user_ids)
    user_df = pd.DataFrame(user_features)
    user_df["name"] = user_names
    user_df["artist"] = user_artists
    user_df = user_df.drop(['analysis_url', 'track_href', 'type', 'uri', 'id'], axis=1)
    user_df = user_df[
        ['name', 'artist', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness',
         'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms']]

    # Özellikleri ölçeklendirme
    user_X = scaler.transform(user_df.drop(['name', 'artist'], axis=1))

    # Kullanıcının dinlediği tüm şarkıların özelliklerini kullanarak öneri yapma
    query = user_X

    # En yakın şarkıları bulma
    distances, indices = model.kneighbors(query)

    # Öneri listesi oluşturma
    recommendations = []
    for i in indices[0]:
        song = dataset_df.iloc[i]
        recommendations.append((song['name'], song['artist']))

    # Öneri listesini JSON formatına dönüştürme
    recommendations_json = {'recommendations': recommendations}

    # Öneri listesini döndürme
    return jsonify(recommendations_json)

# *********************************************

@app.route('/recommend_ws', methods=['POST'])
def recommend_songs_ws():
    # Spotify API anahtarlarınızı buraya ekleyin
    client_id = 'bc6f5a71013f4155a0874aebe0100635'
    client_secret = '98a1134230354a64ac77120d3572a6bb'

    # API kimlik doğrulaması
    client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Veri setini oluşturma
    playlist_id_dataset = '6fFu08cB9yTyGVJ95o5nua'
    dataset_playlist = sp.playlist(playlist_id_dataset)
    dataset_tracks = dataset_playlist["tracks"]["items"]
    dataset_ids = []
    dataset_names = []
    dataset_artists = []
    for track in dataset_tracks:
        if track["track"]:
            dataset_ids.append(track["track"]["id"])
            dataset_names.append(track["track"]["name"])
            artist = track["track"]["artists"][0]["name"]
            dataset_artists.append(artist)
    dataset_features = sp.audio_features(dataset_ids)
    dataset_df = pd.DataFrame(dataset_features)
    dataset_df["name"] = dataset_names
    dataset_df["artist"] = dataset_artists
    dataset_df = dataset_df.drop(['analysis_url', 'track_href', 'type', 'uri', 'id'], axis=1)
    dataset_df = dataset_df[
        ['name', 'artist', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness',
         'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms']]
    dataset_df.to_csv('spotify_dataset.csv', index=False)

    # Özellikleri ölçeklendirme
    scaler = StandardScaler()
    X = dataset_df.drop(['name', 'artist'], axis=1)
    X = scaler.fit_transform(X)

    # Modeli oluşturma
    model = NearestNeighbors(n_neighbors=10, algorithm='ball_tree')
    model.fit(X)

    # Kullanıcının çalma listesini alın
    song_link = request.json['song_link']
    song_id = sp.track(song_link)['id']

    user_ids = [song_id]
    user_names = [sp.track(song_link)['name']]
    user_artists = [sp.track(song_link)['artists'][0]['name']]

    user_features = sp.audio_features(user_ids)
    user_df = pd.DataFrame(user_features)
    user_df["name"] = user_names
    user_df["artist"] = user_artists
    user_df = user_df.drop(['analysis_url', 'track_href', 'type', 'uri', 'id'], axis=1)
    user_df = user_df[
        ['name', 'artist', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness',
         'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms']]

    # Özellikleri ölçeklendirme
    user_X = scaler.transform(user_df.drop(['name', 'artist'], axis=1))

    # Kullanıcının dinlediği tüm şarkının özelliklerini kullanarak öneri yapma
    query = user_X

    # En yakın şarkıları bulma
    distances, indices = model.kneighbors(query)

    # Öneri listesi oluşturma
    recommendations = []
    for i in indices[0]:
        song = dataset_df.iloc[i]
        recommendations.append((song['name'], song['artist']))

    # Öneri listesini JSON formatına dönüştürme
    recommendations_json = {'recommendations': recommendations}

    # Öneri listesini döndürme
    return jsonify(recommendations_json)

if __name__ == '__main__':
    app.run(debug=True)
