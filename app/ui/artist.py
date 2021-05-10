import urwid
from ..player.player import player
from .parts import UiButton

class UiArtist(urwid.WidgetWrap):
	def __init__(self, ui, artist):
		self.widget = self.build(ui, artist)
		super(UiArtist, self).__init__(self.widget)

	def build(self, ui, artist):
					

		self.ui = ui
		self.artist = artist
		self.page = 0

		self.ui.setMain(urwid.Text("Получаю исполнителя"), False)	
		
		self.tracks = artist.getTracks()
		self.albums = artist.getAlbums()		

		tracksList = [
			urwid.Columns([
				urwid.Text('Название'),						
				urwid.Text('Действия'),
			])
		]

		for track in self.tracks:			
			tracksList.append(self.build_track(track))
		
		
		tracksList.append(urwid.Pile([
			urwid.Divider(),
			UiButton('Получить еще ' + str(self.page), on_press=self.load_more),
			UiButton('Получить всё ' + str(self.page), on_press=self.load_all),
			urwid.Divider()
		]))

		albumWidgets = []		
		for album in self.albums:
			albumWidgets.append(urwid.Pile([
				UiButton(album.title, on_press=self.on_album_click, user_data=album),
				urwid.Divider(),
			]))
		
		self.blockContent = urwid.SimpleListWalker([])
		self.tracksListWidget = urwid.BoxAdapter(urwid.ListBox(self.blockContent),height=self.ui.size() - 10)
		self.blockContent.extend(tracksList)

		return urwid.BoxAdapter(urwid.ListBox([
			urwid.LineBox(
				urwid.GridFlow(albumWidgets, 40, 0, 0, 'left'),
				'Альбомы'
			),
			urwid.LineBox(
				self.tracksListWidget,
				self.artist.name
			)
		]), height=self.ui.size() - 10)

	def build_track(self, track):
		albums = []
		for album in track._albums:
			albums.append(UiButton('Альбом ' + album.title, normalColor='album', on_press=self.on_album_click, user_data=album))


		trackWidgets = [
			urwid.Pile([
				UiButton(track.title, on_press=self.on_track_click, user_data=track),	
				urwid.Pile(albums),
			]),								
			urwid.Columns([
				UiButton(self.getLikeDislikeText(track), align='center', on_press=self.on_like_press, user_data=track),					
				UiButton(self.getLikeDislikeText(track, True), align='center',on_press=self.on_dislike_press, user_data=track),
			])
		]

		return (urwid.Pile([
			urwid.Columns(trackWidgets),	
			urwid.Divider(),			
		]))

	def on_track_click(self, el, data):
		self.ui.loop.draw_screen()
		player.start(data, self.tracks)

	def load_more(self, el):
		el.set_label('Загрузка...')
		self.page = self.page + 1
		data = self.artist.getTracks(page=self.page)

		self.blockContent.pop()
		for item in data:
			self.tracks.append(item)
			self.blockContent.append(self.build_track(item))	

		if (len(data) > 0):
			self.blockContent.append(urwid.Pile([
				urwid.Divider(),
				UiButton('Получить еще ' + str(self.page), on_press=self.load_more),
				UiButton('Получить всё ' + str(self.page), on_press=self.load_all),
				urwid.Divider()
			]))

		self.ui.loop.draw_screen()	

	def load_all(self, el):
		el.set_label('Загрузка...')
		self.blockContent.pop()
		while True:
			self.page = self.page + 1
			data = self.artist.getTracks(page=self.page)
			
			if (len(data) == 0):
				break

			for item in data:
				self.tracks.append(item)
				self.blockContent.append(self.build_track(item))

		self.ui.loop.draw_screen()



	def on_album_click(self, el, data):	
		from .tracklist import UiTracksList	
		self.ui.setMain(urwid.Text("Получаю треки"), False)	
		self.ui.setMain(UiTracksList(self.ui, data.getTracks(), data.title))


	def getLikeDislikeText(self, track, dislike=False):
		text = "♥"
		if dislike:
			text = "♡"

		if (dislike == False and track.is_liked == 1):
			return "✅ " + text

		if (dislike == True and track.is_disliked == 1):
			return "✅ " + text

		return text	
	def on_like_press(self, button, track):
		track.like()
		button.set_text(self.getLikeDislikeText(track))

	def on_dislike_press(self, button, track):
		track.dislike()
		button.set_text(self.getLikeDislikeText(track, True))

