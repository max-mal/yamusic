from ..model import Model

class ArtistModel(Model):

	def boot(self):
		self._tracks = []
		self._albums = []

	def getTable(self):
		return 'artists'

	def getTracks(self, append=False, page=0, pageSize=20):
		from ...api.repository import repository
		data = repository.getArtistTracks(self, page=page, pageSize=pageSize)
		if (append == True):
			self._tracks.extend(data)
		else:
			self._tracks = data
		return self._tracks

	def getAlbums(self):
		from ...api.repository import repository
		self._albums = repository.getArtistAlbums(self)
		return self._albums

	def saveAlbums(self, commit = False):
		for album in self._albums:
			Query.insert(db, 'artist_albums', {
				'album_id': album.id,
				'artist_id': self.id
			})
		if commit:
			db.commit()