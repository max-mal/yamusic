import threading
import copy

class Downloader:
	def __init__(self):
		self.queue = []		
		self.lock = threading.Lock()

	def start(self):
		thread = threading.Thread(target=worker, args=(self,), daemon=True)
		thread.start()

	def add(self, tracks):
		self.lock.acquire()
		self.queue.extend(tracks)
		self.lock.release()

def worker(manager):
	from ..api.music import music
	while True:			
		if len(manager.queue) == 0:
			continue

		manager.lock.acquire()
		track = manager.queue.pop(0)
		manager.lock.release()

		track.checkDownloaded()
		if track.is_downloaded == 1:
			track.store()
			continue

		attempt = 0
		maxAttempts = 5

		while attempt < maxAttempts:		
			try:
				attempt = attempt + 1
				music.downloadTrack(track)
				break
			except Exception as error:
				print(error)		


downloader = Downloader()
downloader.start()