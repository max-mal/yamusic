import urwid
from .artist import UiArtist
from .parts import UiButton

class UiTracksList(urwid.WidgetWrap):
	def __init__(self, ui, tracks, name='Треки', showDownload=True):
		self.widget = self.build(ui, tracks, name, showDownload)
		super(UiTracksList, self).__init__(self.widget)

	def build(self, ui, tracks, name='Треки', showDownload=True):
		
		self.ui = ui

		self.tracks = tracks

		tracksList = [
			urwid.Columns([
				urwid.Text('Название'),
				urwid.Text('Исполнитель'),				
				urwid.Text('Действия'),
			]),			
		]

		if showDownload and self.ui.repository.online:
			tracksList.append(urwid.Divider())
			tracksList.append(UiButton('Скачать все треки', on_press=self.download_all))
			tracksList.append(urwid.Divider())

		for track in tracks:
			albums = []
			for album in track._albums:
				albums.append(UiButton('Альбом ' + album.title, normalColor='album', on_press=self.on_album_click, user_data=album))

			artists = []
			for artist in track._artists:
				artists.append(UiButton(artist.name, on_press=self.on_artist_click, user_data=artist))


			trackWidgets = [
				urwid.Pile([
					UiButton(track.title, on_press=self.on_track_click, user_data=track),	
					urwid.Pile(albums),
				]),				
				urwid.Pile(artists),
				urwid.Columns([
					UiButton(self.getLikeDislikeText(track), align='center', on_press=self.on_like_press, user_data=track),					
					UiButton(self.getLikeDislikeText(track, True), align='center',on_press=self.on_dislike_press, user_data=track),
				])
			]

			tracksList.append(urwid.Pile([
				urwid.Columns(trackWidgets),
				urwid.Divider()
			]))		

		return urwid.LineBox(
			urwid.BoxAdapter(urwid.ListBox(tracksList), height=self.ui.size() - 10), 
			name
		)

	def getLikeDislikeText(self, track, dislike=False):
		text = "♥"
		if dislike:
			text = "♡"

		if (dislike == False and track.is_liked == 1):
			return "✅ " + text

		if (dislike == True and track.is_disliked == 1):
			return "✅ " + text

		return text			

	def on_track_click(self, el, data):
		self.ui.loop.draw_screen()
		self.ui.player.start(data, self.tracks)

	def on_artist_click(self, el, data):
		self.ui.setMain(UiArtist(self.ui, data))

	def on_album_click(self, el, data):	
		self.ui.setMain(urwid.Text("Получаю альбом"), False)	
		self.ui.setMain(UiTracksList(self.ui, data.getTracks(), data.title))

	def on_like_press(self, button, track):
		track.like()
		button.set_text(self.getLikeDislikeText(track))

	def on_dislike_press(self, button, track):
		track.dislike()
		button.set_text(self.getLikeDislikeText(track, True))

	def download_all(self, el):
		from ..api.downloader import downloader
		downloader.add(self.tracks)
		el.set_text('Скачивание запущено')
	



