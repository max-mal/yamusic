from ..main import db
from ..query import Query
from ..model import Model

class PlaylistModel(Model):
	
	def boot(self):
		self._tracks = []

	def getTable(self):
		return 'playlists'

	def getTracks(self):
		from ...api.repository import repository
		self._tracks = repository.getPlaylistTracks(self)		
		return self._tracks

	def saveTracks(self, commit = True):
		for track in self._tracks:
			Query.insert(db, 'playlist_tracks', {
				'track_id': track.id,
				'playlist_id': self.id
			})
		if commit:
			db.commit()