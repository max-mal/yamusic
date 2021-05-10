from ..model import Model
from ..query import Query
from ..main import db
from ..query import Query

class AlbumModel(Model):
	def boot(self):
		self._artists = []
		self._tracks = []

	def getTable(self):
		return 'albums'

	def saveArtists(self, commit = True):
		for artist in self._artists:
			Query.insert(db, 'artist_albums', {
				'album_id': self.id,
				'artist_id': artist.id
			})
		if commit:
			db.commit()

	def getArtists(self):
		pass

	def getTracks(self):
		from ...api.repository import repository
		self._tracks = repository.getAlbumTracks(self)
		return self._tracks

	def saveTracks(self, commit = True):
		for track in self._tracks:
			Query.insert(db, 'track_albums', {
				'album_id': self.id,
				'track_id': track.id
			})
		if commit:
			db.commit()