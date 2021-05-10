from .main import db
from .models.album import AlbumModel
from .models.track import TrackModel
from .models.artist import ArtistModel
from .models.playlist import PlaylistModel

class Storage:
	def __init__(self, db):			
		self.db = db

	def savePlaylists(self, playlists, is_feed=0):
		feedPlaylists = []
		for playlist in playlists:		
			playlistItem = playlist
			
			if (hasattr(playlist, 'data')):
				playlistItem = playlist.data

			model = PlaylistModel({
				"id": playlistItem.playlist_id,
				"title": playlistItem.title,
				"uuid": playlistItem.playlist_uuid,
				"description": playlistItem.description,
				"is_feed": is_feed,
			})
			model.store(False)
			feedPlaylists.append(model)			

		self.db.commit()
		return feedPlaylists

	def saveTracks(self, tracks, playlist=None, isLiked=False):
		tracksData = []
		for trackData in tracks:			
			track = trackData
			if hasattr(track, 'track'):
				track = track.track

			trackModel = TrackModel({
				"id": track.id,
				"title": track.title,
				"duration": track.duration_ms,
				"filename": "",
				"is_downloaded": 0,
				"_directLink": None
			})		

			if (isLiked):
				trackModel.is_liked = 1

			# Query.insert(self.db, 'tracks', trackObj)			
			for artist in track.artists:				
				artistModel = ArtistModel({
					"id": artist.id,
					"name": artist.name,					
				})
				artistModel.store(False)
				trackModel._artists.append(artistModel)


			for album in track.albums:
				albumModel = AlbumModel({
					"id": album.id,
					"title": album.title,					
				})
				albumModel.store(False)
				trackModel._albums.append(albumModel)
				
			trackModel.saveArtists(False)
			trackModel.saveAlbums(False)

			trackModel.checkDownloaded()					
			trackModel.store(False)
			
			tracksData.append(trackModel)		
		
		if playlist != None:
			playlist._tracks = tracksData
			playlist.saveTracks(False)

		self.db.commit()
		return tracksData

	def saveArtists(self, artists):
		res = []
		for artist in artists:
			artistModel = ArtistModel({
				"id": artist.id,
				"name": artist.name,					
			})
			artistModel.store(False)
			res.append(artistModel)
		
		self.db.commit()
		return res

	def saveAlbums(self, albums):
		albumsList = []
		for album in albums:
			albumModel = AlbumModel({				
				"id": album.id,
				"title": album.title,
			})

			albumModel.store(False)

			for artist in album.artists:
				artistModel = ArtistModel({
					"id": artist.id,
					"name": artist.name,					
				})
				artistModel.store(False)
				albumModel._artists.append(artistModel)

			albumModel.saveArtists(False)
			albumsList.append(albumModel)

		self.db.commit()

		return albumsList

storage = Storage(db)