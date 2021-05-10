#!/usr/bin/python3

from yandex_music.client import Client, Artist, Track, Playlist, Album
import os.path
import threading
from queue import Queue
import pprint
import vlc
import sys

import logging
logging.basicConfig(level=logging.CRITICAL,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class Player:
    def __init__(self):
        self.token = None
        self.client = None
        self.loggedIn = False
        self.vlc = None
        self.vlcPlayer = None
        self.daemons = []
        self.download_daemons = []
        
        self.download_queue = Queue()
            
    
    def play_tracks(self, tracks):
        
        if self.vlc == None:
            self.vlc = vlc.Instance()
            self.vlcPlayer = self.vlc.media_list_player_new()
            
        media = []
        media_list = self.vlc.media_list_new()
        has_track = False
        
        try:
            for daemon in self.daemons:
                daemon._stop()
                            
        except:
            pass
        
        finally:
            self.daemons = []
        
        queue = Queue()                    
        t = TrackInfo(queue)
        t.setDaemon(True)
        t.start()
        self.daemons.append(t)
                    
        for track in tracks:            
            path = "music/" + self.track_name(track) + '.mp3'
            if os.path.isfile(path):
                #media.append(path)
                media_list.lock()
                media_list.add_media(path)
                media_list.unlock()
                has_track = True
            else:
                if has_track == False:
                    trackInfo = track.get_download_info()
                    for info in trackInfo:
                        if info.codec == "mp3" and info.bitrate_in_kbps == 192:
                            info.get_direct_link()
                            print(info)
                            #media.append(info.direct_link)
                            media_list.lock()
                            media_list.add_media(info.direct_link)
                            media_list.unlock()
                            has_track = True
                            break
                else:                    
                    queue.put({'track': track, 'list': media_list})
        print("Here!")      
        self.vlcPlayer.set_media_list(media_list)
        print("Here!1")
        self.vlcPlayer.play()
        print("Here!2")
        
        should_exit = False
        while not should_exit:
            try:
                selection = self.get_input("[P]lay / P[a]use / [S]top / [N]ext / P[r]ev / Ba[c]k \n>> ", ["P", "a", "S", "N", "r", "c"])
                if selection == "P":
                    self.vlcPlayer.play()
                elif selection == "a":
                    self.vlcPlayer.pause()
                elif selection == "S":
                    self.vlcPlayer.stop()
                    should_exit = True
                elif selection == "N":
                    self.vlcPlayer.next()
                elif selection == "r":
                    self.vlcPlayer.previous()
                elif selection == "c":
                    should_exit = True
            except Exception as e:
                print(e)
        
    def player_controls(self):
        if (self.vlcPlayer == None):
            print("Player not initialized")
            return;
        
        should_exit = False
        while not should_exit:
            try:
                selection = self.get_input("[P]lay / P[a]use / [S]top / [N]ext / P[r]ev / Ba[c]k \n>> ", ["P", "a", "S", "N", "r", "c"])
                if selection == "P":
                    self.vlcPlayer.play()
                elif selection == "a":
                    self.vlcPlayer.pause()
                elif selection == "S":
                    self.vlcPlayer.stop()
                    should_exit = True
                elif selection == "N":
                    self.vlcPlayer.next()
                elif selection == "r":
                    self.vlcPlayer.previous()
                elif selection == "c":
                    should_exit = True
            except Exception as e:
                print(e)
    
    def init(self):
        
        if os.path.isfile('token.txt'):
            try:
                tokenFile = open('token.txt', 'r')
                self.token = tokenFile.read()
                tokenFile.close();
                self.client = Client(self.token)
                self.loggedIn = True
            except:
                print("Failed to create client using saved token. Enter your login/password.")
                self.login()
                
        else:
            self.login()
            
        
        
    def login(self):
        self.loggedIn = False
        while not self.loggedIn:
            try:            
                login = input("Login: ")
                password = input("Password: ")
        
                self.client = Client.from_credentials(login, password, captcha_callback=self.proc_captcha)
                loggedIn = True
                tokenFile = open('token.txt', 'w')
                tokenFile.write(self.client.token)
                tokenFile.close();
                self.loggedIn = True
            except Exception as e:
                print("Login failed!")
                print(e)
            
    def proc_captcha(self, captcha):
        captcha.download('captcha.png')
        if os.system("./captcha.png") != 0:
            os.system("xdg-open ./captcha.png")
        return input('Число с картинки: ')
    
    def get_status(self):
        data = self.client.account_status()
        print("Login: " +  data.account.login)
        print("Name: " + data.account.first_name)
        print("Surname: " + data.account.second_name)
        
    def playlists(self):
        playlists = player.client.feed().generated_playlists
                
        should_exit = False
        while not should_exit:
            try:
                index = 1        
                for playlist in playlists:
                    print(str(index) + ") " + playlist.data.title)
                    index = index + 1
                    
                selection = self.get_input('Playlist number / [B]ack \n>> ', ["B"])
                if (selection == "B"):
                    should_exit = True
                else:
                    self.playlist(playlists[int(selection) - 1])
            except Exception as e:
                print(e)
                
    def track_name(self, track):
        artists = ""
        for artist in track.artists:
            artists = artists + artist.name + " "
        return track.title + " ( " + artists + " )"
    
    def playlist(self, playlist):
        tracksShort = []
        
        if (hasattr(playlist, "data")):
            tracksShort = playlist.data.tracks
        else:            
            p = self.client.playlists_list( playlist.playlist_id )            
            tracksShort = p[0].tracks            
            
        track_ids = []
        for trackShort in tracksShort:
            track_ids.append(trackShort.track_id)
        
        if (len(track_ids) == 0):
            print("Tracks list is empty")
            return
        
        tracks = self.client.tracks(track_ids)                    
        should_exit = False
        while not should_exit:
            try:
                index = 1
                for track in tracks:            
                    print(str(index) + ") " + self.track_name(track))
                    index = index + 1
                    
                selection = self.get_input("Track number / [D]ownload / [P]lay / [L]ike / D[i]slike / [B]ack\n>> ", ["D", "P", "L", "i", "B"])
                if selection == "D":
                    self.download_tracks(tracks)
                elif (selection == "L"):
                    playlist.like()
                elif (selection == "i"):
                    playlist.dislike()
                elif selection == "B":
                    should_exit = True
                elif selection == "P":
                    self.play_tracks(tracks)
                else:
                    self.track(tracks[selection - 1])
            except Exception as e:
                print(e)
            
    def get_input(self, prompt, allowed = [], numbers = True):
        valid = False 
        while not valid:
            selection = input(prompt)
            if selection in allowed:
                return selection
            if (numbers == True):
                try:
                    number = int(selection)
                    if (number > 0):
                        return number                
                except:
                    pass
    def download_tracks(self, tracks):
        if (len(self.download_daemons) == 0):
            for i in range(2):
                t = TrackDownloader(self.download_queue)
                t.setDaemon(True)
                t.start()
                self.download_daemons.append(t)
                
        print("Downloading " + str(len(tracks)) + " tracks")
                
        for track in tracks:
            self.download_queue.put(track.track_id)
        
    def track(self, track):
        print(self.track_name(track))
        should_exit = False
        while not should_exit:
            try:
                selection = self.get_input("[D]ownload / [P]lay / [L]ike / D[i]slike / [B]ack\n>> ", ["D", "P", "L", "i", "B"], False)
                if selection == "D":
                    self.download_tracks([track])
                elif (selection == "L"):
                    track.like()
                elif (selection == "i"):
                    track.dislike()
                elif selection == "P":
                    self.play_tracks([track])
                else:
                    should_exit = True
            except Exception as e:
                print(e)
                
    def search(self):
        query = input("Search: ")
        data = self.client.search(text=query)
        print(data)
        results = []
        for track in data.tracks.results:
            results.append(track)
        for album in data.albums.results:
            results.append(album)
        for artist in data.artists.results:
            results.append(artist)
        for playlist in data.playlists.results:
            results.append(playlist)        
        
        best = data.best.result
        if (best != None):
            print("B) " + self.entity_name(best))      
        
        index = 1
        for result in results:
            print(str(index) + ") " + self.entity_name(result))
            index = index + 1
        
        should_exit = False
        while not should_exit:
            try:
                selection = self.get_input("Number / [B]est choice / [E]xit \n>> ", ["B", "E"])
                if selection == "B":
                    self.open_entity(best)
                elif selection == "E":
                    should_exit = True
                else:
                    self.open_entity(results[selection - 1])
            except Exception as e:
                print(e)
        
    def open_entity(self, entity):
        if (type(entity) is Track):
            self.track(entity)
        elif (type(entity) is Playlist):
            self.playlist(entity)
        elif (type(entity) is Artist):
            self.artist(entity)
        elif (type(entity) is Album):
            self.album(entity)
        
    def entity_name(self, result):
        if (type(result) is Artist):
            return ("(Artist) " + result.name)
        elif type(result) is Track:
            return ("(Track) " + self.track_name(result))
        elif type(result) is Album:
            artists = ""
            for artist in result.artists:
                artists = artists + " " + artist.name
            return ("(Album) " + result.title + " (" + artists + " )")
        elif type(result) is Playlist:
            return "(Playlist) " + result.title + " by " + result.owner.name
        else:            
            return (str(type(result)))
            
    def artist(self, artist):                    
        print(artist.name)
        print(artist.description)
        page = 0
        tracks = artist.get_tracks(page=page).tracks
        albums = artist.get_albums(page=page).albums
        
        entities = []        
        for track in tracks:
            entities.append(track)
            
        for album in albums:
            entities.append(album)
            
        should_exit = False
        while not should_exit:
            try:
                index = 1
                for e in entities:                    
                    print(str(index) + ") " + self.entity_name(e))
                    index = index + 1
                    
                selection = self.get_input("Number / [D]ownload / [P]lay / [L]ike / D[i]slike / [B]ack / [M]ore / [A]ll\n>> ", ["D", "P", "L", "i", "B", "M", "A"])
                if selection == "D":
                    t = []
                    for e in entities:
                        if (type(e) is Track):
                            t.append(e)
                    self.download_tracks(t)
                elif (selection == "L"):
                    artist.like()
                elif (selection == "i"):
                    artist.dislike()
                elif selection == "P":
                    t = []
                    for e in entities:
                        if (type(e) is Track):
                            t.append(e)
                    self.play_tracks(t)
                elif selection == "B":
                    should_exit = True
                elif selection == "M":
                    page = page + 1
                    tracks = artist.get_tracks(page=page).tracks
                    albums = artist.get_albums(page=page).albums
                    for track in tracks:
                        entities.append(track)
                        
                    for album in albums:
                        entities.append(album)
                elif selection == "A":
                    tPage = page
                    aPage = page
                    while True:
                        tPage = tPage + 1
                        tracks = artist.get_tracks(page=tPage).tracks
                        for track in tracks:
                            entities.append(track)
                        sys.stdout.write('.')
                        if (len(tracks) == 0):
                            break
                    print('')
                    while True:
                        aPage = aPage + 1
                        albums = artist.get_albums(page=aPage).albums
                        for a in albums:
                            entities.append(a)
                        sys.stdout.write('.')
                        if (len(albums) == 0):
                            break
                    
                else:
                    self.open_entity(entities[selection - 1])
            except Exception as e:
                print(e)
            
        
        
    def get_all(self, func, prop):
        page = 0
        last_page = 1
        data = []
        while page < last_page:
            portion = func(page=page)
            for e in portion[prop]:
                data.append(e)
            last_page = portion.pager.total / portion.pager.per_page + 1
            page = page + 1
            print(page)
        return data
            
    
    def album(self, album):
        print(self.entity_name(album))
        album_tracks = album.with_tracks()
                        
        should_exit = False
        
        while not should_exit:
            try:
                index = 1
                for track in album_tracks.volumes[0]:
                    print(str(index) + ") " + self.track_name(track))
                    index = index + 1
                    
                selection = self.get_input("[A]rtist / [D]ownload / [P]lay / [L]ike / D[i]slike / [B]ack \n>> ", ["A", "D", "P", "L", "i", "B"])
                if selection == "D":
                    self.download_tracks(album_tracks.volumes[0])
                elif selection == "A":
                    self.artist(album_tracks.artists[0])
                elif selection == "L":
                    album_tracks.like()
                elif selection == "i":
                    album_tracks.dislike()
                elif selection == "B":
                    should_exit = True
                elif selection == "P":
                    self.play_tracks(album_tracks.volumes[0])
                else:
                    self.track(album_tracks.volumes[0][selection - 1])
            except Exception as e:
                print(e)
        
    def menu(self):
        should_exit = False
        while not should_exit:
#            try:
                selection = self.get_input("[P]laylists / [M]e / [S]earch / P[l]ayer / [E]xit \n>> ", ["P", "M", "S", "E", "l"], False)
                if (selection == "P"):
                    self.playlists()
                elif selection == "M":
                    self.get_status()
                elif selection == "S":
                    self.search()
                elif selection == "E":
                    should_exit = True
                elif selection == "l":
                    self.player_controls()
                
#            except Exception as e:
#                print(e)                

class TrackDownloader(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.player = Player()
        self.player.init()
        
    def run(self):
        while True:
            track_id = self.queue.get()
            for i in range(5):
                try:                    
                    track = self.player.client.tracks(track_id)[0]
                    if not os.path.isfile("music/" + self.player.track_name(track) + '.mp3'):
                        track.download("music/" + self.player.track_name(track).replace("/", "") + '.mp3')
                        print("Downloaded " + self.player.track_name(track))                    
                    break
                except Exception as e:
                    print("Cannot download track. Attempt " + str(i) + str(e))
            self.queue.task_done()
            

class TrackInfo(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.player = Player()
        self.player.init()
        
    def run(self):
        while True:
            data = self.queue.get()
            for i in range(5):
                try:                    
                    trackInfo = data['track'].get_download_info()                    
                    for info in trackInfo:
                        if info.codec == "mp3" and info.bitrate_in_kbps == 192:
                            info.get_direct_link()
                            sys.stdout.write('.')                     
                            data['list'].lock()
                            data['list'].add_media(info.direct_link)
                            data['list'].unlock()
                            break
                    break
                except Exception as e:
                    print("Cannot get track info. Attempt " + str(i) + str(e))
            self.queue.task_done()
        

if (__name__ == "__main__"):
    player = Player()
    player.init()
    #player.get_status()
    player.menu()
