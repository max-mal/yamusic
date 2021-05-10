import urwid
from ..ui.tracklist import UiTracksList
from ..ui.login import UiLogin
from .parts import UiButton
        

class UiHeader(urwid.WidgetWrap):
	def __init__(self, ui):
		self.widget = self.build(ui)
		super(UiHeader, self).__init__(self.widget)
	
	def build(self, ui):		
		self.ui = ui

		track = self.ui.player.getTrack()

		trackName = ''
		if (track != None):
			trackName = '{name} ({artists})'.format(
				name=track.title,
				artists=','.join(map(lambda a: a.name, track._artists))
			)

		statusText = 'Онлайн'		
		if (not self.ui.repository.online):
			statusText = 'Оффлайн'
		

		loopText = ''
		if (self.ui.player.loop):
			loopText = '🔁  On (F7)'
		else:
			loopText = '🔁  (F7)'


		return urwid.LineBox(urwid.Pile([
			urwid.Columns([
				urwid.Padding(urwid.AttrMap(urwid.Text(trackName), 'greenColor'), right=3),
				urwid.ProgressBar('progressbar.b', 'progressbar.a', self.ui.player.currentPosition * 100)
				
			]),
			urwid.Columns([
				urwid.Pile([
					UiButton('Сейчас играет', self.on_playlist),
					UiButton(statusText, on_press=self.toggle_offline),
					urwid.Text('DL: ' + str(len(self.ui.downloader.queue))),
				]),
				urwid.Text(' '),
				urwid.Pile([
					urwid.AttrMap(UiButton('▶  (F1)', on_press=self.play), 'greenColor'),	
					urwid.AttrMap(UiButton('⏸  (F2)', on_press=self.pause), 'yellowColor'),
					urwid.AttrMap(UiButton('⏹  (F3)', on_press=self.stop), 'redColor'),
				]),
				urwid.Text(' '),
				urwid.Pile([
					UiButton('⏮  (F4)', on_press=self.prevTrack),					
					UiButton('⏭  (F5)', on_press=self.nextTrack),
					UiButton('🔀 (F6)', on_press=self.shuffle)
				]),
				urwid.Text(' '),
				urwid.Pile([
					UiButton(loopText, on_press=self.loop),
					UiButton(self.getLikeDislikeText(track), on_press=self.on_like_press, user_data=track),					
					UiButton(self.getLikeDislikeText(track, True), on_press=self.on_dislike_press, user_data=track),
				])

				
				#UiButton('Like'),
				#UiButton('Dislike'),
			])
			
		]), title='Player')

	def play(self, el):
		self.ui.player.play()

	def pause(self, el):
		self.ui.player.pause()

	def stop(self, el):
		self.ui.player.stop()

	def nextTrack(self, el):
		self.ui.player.nextTrack()

	def prevTrack(self, el):
		self.ui.player.prevTrack()

	def setStatusText(self, button):
		statusText = 'Онлайн'		
		if (not self.ui.repository.online):
			statusText = 'Оффлайн'
		button.set_label(statusText)

	def toggle_offline(self, el):
		if self.ui.repository.online:
			self.ui.repository.online = False
			self.ui.music.online = False
			self.setStatusText(el)
			return

		if not self.ui.music.loggedIn:
			self.ui.music.init()
		else:
			self.ui.repository.online = True
			self.ui.music.online = True
			self.setStatusText(el)
			return

		if not self.ui.music.loggedIn:
			self.ui.repository.online = True
			self.ui.music.online = False
			self.setStatusText(el)
			self.ui.setMain(UiLogin(self.ui))
			return
		

	def on_playlist(self, el):
		playlist = self.ui.player.playlist
		if (playlist == None):
			playlist = []
		
		self.ui.setMain(UiTracksList(self.ui, playlist, 'Сейчас играет'))

	def shuffle(self,el):
		self.ui.player.shuffle()

	def loop(self, el):		
		self.ui.player.setLoop(not self.ui.player.loop)
		if (self.ui.player.loop):
			el.set_label('🔁  On (F7)')
		else:
			el.set_label('🔁  (F7)')

	def getLikeDislikeText(self, track, dislike=False):

		if (not track):
			return ""

		text = " ♥  (F8)"
		if dislike:
			text = " ♡  (F9)"

		if (dislike == False and track.is_liked == 1):
			return "✅ " + text

		if (dislike == True and track.is_disliked == 1):
			return "✅ " + text

		return text

	def on_like_press(self, button, track):
		if not track:
			return False

		track.like()
		button.set_text(self.getLikeDislikeText(track))

	def on_dislike_press(self, button, track):
		if not track:
			return False

		track.dislike()
		button.set_text(self.getLikeDislikeText(track, True))


