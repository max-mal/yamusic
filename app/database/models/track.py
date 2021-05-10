from ..main import db
from ..query import Query
from ..model import Model
import threading
import os.path
import string
import os

class TrackModel(Model):

	def boot(self):
		self._artists = []
		self._albums = []
		self._directLink = None		

	def defaultAttributes(self):
		if not hasattr(self, 'is_liked'):
			self.is_liked = 0

		if not hasattr(self, 'is_disliked'):
			self.is_disliked = 0

	def getTable(self):
		return 'tracks'

	def like(self):
		from ...api.music import music
		music.likeTrack(self)

	def dislike(self):
		from ...api.music import music
		music.dislikeTrack(self)		

	def checkDownloaded(self):
		if os.path.isfile(self.getDownloadsDirectory() + '/' + self.generateFilename()):			
			self.is_downloaded = 1
			return 1
		else:
			self.is_downloaded = 0
			return 0

	def saveArtists(self, commit=True):
		for artist in self._artists:
			Query.insert(db, 'track_artists', {
				'track_id': self.id,
				'artist_id': artist.id
			})
		if commit:
			db.commit()

	def getArtists(self):
		from ...api.repository import repository
		self._artists = repository.getTrackArtists(self)
		return self._artists

	def saveAlbums(self, commit=True):
		for album in self._albums:
			Query.insert(db, 'track_albums', {
				'track_id': self.id,
				'album_id': album.id
			})
		if commit:
			db.commit()

	def getAlbums(self):
		from ...api.repository import repository
		self._albums = repository.getTrackAlbums(self)
		return self._albums

	def afterFetch(self):
		self.getArtists()
		self.getAlbums()

	def getUri(self, download=True):
		self.checkDownloaded()
		if self.is_downloaded == 1:
			return self.getDownloadsDirectory() + '/' + self.generateFilename()

		from ...api.music import music
		ret = music.getUri(self)
		if download == True:
			self.downloadTrack()
		return ret
	
	def getFullTitle(self):
		return '{name} ({artists})'.format(
			name=self.title,
			artists=','.join(map(lambda a: a.name, self._artists))
		)

	def generateFilename(self):
		return '{title}.mp3'.format(title=prepareFilename(self.getFullTitle()))

	def getDownloadsDirectory(self):
		return os.getcwd() + '/amusic'

	def downloadTrack(self):
		from ...api.music import music
		thread = threading.Thread(target=downloadTrackWorker, args=(self, music,))
		thread.start()

def downloadTrackWorker(track, music): 

	attempt = 0
	maxAttempts = 5

	while attempt < maxAttempts:		
		try:
			attempt = attempt + 1
			music.downloadTrack(track)
			break
		except Exception as error:
			print(error)


def prepareFilename(data):	
	table = str.maketrans("\0", " ")
	data = data.translate(table)
	table = str.maketrans("/", "-")
	data = data.translate(table)
	return data