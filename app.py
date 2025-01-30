from flask import Flask, redirect, request, url_for, render_template,session
import spotipy
from spotipy.oauth2 import SpotifyOAuth

SPOTIFY_CLIENT_ID = "992dc94fe5c04e0ea321e5632023b728"
SPOTIFY_CLIENT_SECRET = "20428fa42c194eed93de0dd091447bba"
SPOTIFY_REDIRECT_URI = "https://5000-deangeligiul-prgspotify-s14caz58e17.ws-eu117.gitpod.io/callback" #dopo il login andiamo qui

app = Flask(__name__)
app.secret_key = 'chiave_per_session' #ci serve per identificare la sessione

#config SpotifyOAuth per l'autenticazione e redirect uri
sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="user-read-private" #permessi x informazioni dell'utente
)

@app.route('/')
def login():
    auth_url = sp_oauth.get_authorize_url() #login di spotify
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code') #recupero codice di autorizzazione
    token_info = sp_oauth.get_access_token(code) #uso il code per un codice di accesso
    session['token_info'] = token_info #salvo il token nella mia sessione x riutilizzarlo
    return redirect(url_for('home'))

@app.route('/home')
def home():
    token_info = session.get('token_info', None) #recupero token sissione (salvato prima)
    if not token_info:
        return redirect(url_for('login'))
    sp = spotipy.Spotify(auth=token_info['access_token']) #usiamo il token per ottenere i dati del profilo
    user_info = sp.current_user()
    print(user_info) #capiamo la struttura di user_info per usarle nel frontend
    playlists = sp.current_user_playlists() #sempre tramite il token sp preso prima
    playlists_info = playlists['items'] #prendiamo solo la lista delle playlist
    return render_template('home.html', user_info=user_info, playlists=playlists_info) #passo le info utente all'home.html

@app.route('/brani/<playlist_id>')
def playlist_items(playlist_id):
    token_info = session.get('token_info', None) #recupero token sissione (salvato prima)
    if not token_info:
        return redirect(url_for('login'))
    sp = spotipy.Spotify(auth=token_info['access_token'])
    tracks_data = sp.playlist_tracks(playlist_id)['items']  # Ottiene i brani della playlist
    return render_template('brani.html', tracks=tracks_data)

@app.route('/logout')
def logout():
    session.clear() #cancelliamo l'access token salvato in session
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)