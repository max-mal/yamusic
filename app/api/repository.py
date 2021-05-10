from .music import music
from ..database.models.album import AlbumModel
from ..database.models.track import TrackModel
from ..database.models.artist import ArtistModel
from ..database.models.playlist import PlaylistModel

class Repository:
	def __init__(self, music):
		self.music = music
		self.online = True

	def isOnline(self):
		return self.online

	def getFeedPlaylists(self):
		if not self.isOnline():
			return PlaylistModel.query('WHERE is_feed = 1')

		return self.music.getFeedPlaylists()

	def getPlaylistTracks(self, playlist):
		if not self.isOnline():
			print(playlist.id)
			data =  TrackModel.query('INNER JOIN playlist_tracks on playlist_tracks.track_id = tracks.id WHERE playlist_tracks.playlist_id = ?', [playlist.id])			
			return data

		return self.music.getPlaylistTracks(playlist)

	def getTrackArtists(self, track):
		return ArtistModel.query('INNER JOIN track_artists on track_artists.artist_id = artists.id where track_artists.track_id = ? group by artists.id', [track.id]);

	def getTrackAlbums(self, track):
		return AlbumModel.query('INNER JOIN track_albums on track_albums.album_id = albums.id where track_id = ? group by albums.id', [track.id])

	def getArtistAlbums(self, artist):
		if self.isOnline():
			return self.music.getArtistAlbums(artist)

		return AlbumModel.query('INNER JOIN artist_albums on artist_albums.album_id = albums.id where artist_id = ? group by albums.id', [artist.id])
	def getArtistTracks(self, artist, page=0, pageSize=20):
		if self.isOnline():
			return music.getArtistTracks(artist, page=page, pageSize=pageSize)

		return TrackModel.query('INNER JOIN track_artists on track_artists.track_id = tracks.id WHERE track_artists.artist_id = ? LIMIT {size} OFFSET {offset}'.format(size=pageSize, offset=(page * pageSize)), [artist.id])

	def getAlbumTracks(self, album):
		if self.isOnline():
			return self.music.getAlbumTracks(album)

		return TrackModel.query('INNER JOIN track_albums on track_albums.track_id = tracks.id WHERE track_albums.album_id = ?', [album.id])

	def search(self, query):
		if self.isOnline():
			return self.music.search(query)
		
		return {
			"best": None,
			"best_type": None,
			"tracks": TrackModel.query('WHERE title LIKE ?', ['%{query}%'.format(query=query)]),
			"albums": AlbumModel.query('WHERE title LIKE ?', ['%{query}%'.format(query=query)]),
			"artists": ArtistModel.query('WHERE name LIKE ?', ['%{query}%'.format(query=query)]),
			"playlists": PlaylistModel.query('WHERE title LIKE ?', ['%{query}%'.format(query=query)]),
		}

	def getLikedTracks(self):
		if self.isOnline():
			return self.music.getLikedTracks()
		return TrackModel.query('WHERE is_liked = 1')
	

repository = Repository(music)