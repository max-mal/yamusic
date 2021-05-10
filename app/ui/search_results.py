import urwid
from .parts import UiButton
from .artist import UiArtist
from .tracklist import UiTracksList

class UiSearchResults(urwid.WidgetWrap):
	def __init__(self, ui, results):
		self.widget = self.build(ui, results)
		super(UiSearchResults, self).__init__(self.widget)

	def build(self, ui, results):
		self.ui = ui

		widgets = urwid.SimpleListWalker([])

		if (results == None):
			return urwid.Text('Ничего не найдено')

		if (results['best_type'] == 'track'):
			widgets.append(urwid.LineBox(self.build_track(results['best']), 'Лучший результат'))


		if (results['best_type'] == 'artist'):
			widgets.append(urwid.LineBox(UiButton(results['best'].name, on_press=self.on_artist_click, user_data=results['best']), 'Лучший результат'))

		if (results['best_type'] == 'playlist'):
			widgets.append(urwid.LineBox(urwid.Pile([
				UiButton(results['best'].title, on_press=self.open_playlist, user_data=results['best']),
				urwid.Divider(),
			]), 'Лучший результат'))

		if (results['best_type'] == 'album'):
			widgets.append(urwid.LineBox(urwid.Pile([
				UiButton('{title} {artists}'.format(title=results['best'].title, artists=', '.join(map(lambda e: e.name ,results['best']._artists))), on_press=self.on_album_click, user_data=results['best'], normalColor='album'),
				urwid.Divider(),
			])))

		if (len(results['tracks']) > 0):
			self.tracks = results['tracks']
			widgets.append(urwid.Divider('═'))
			widgets.append(urwid.Text('Треки', align='center'))
			for track in results['tracks']:
				widgets.append(self.build_track(track))
			widgets.append(urwid.Divider('_'))
			widgets.append(urwid.Divider())			

		if (len(results['artists']) > 0):
			widgets.append(urwid.Divider('═'))
			widgets.append(urwid.Text('Исполнители', align='center'))
			for artist in results['artists']:
				widgets.append(urwid.Pile([
					UiButton(artist.name, on_press=self.on_artist_click, user_data=artist),
					urwid.Divider(),
				]))
			widgets.append(urwid.Divider('_'))
			widgets.append(urwid.Divider())

		if (len(results['albums']) > 0):
			widgets.append(urwid.Divider('═'))
			widgets.append(urwid.Text('Альбомы', align='center'))
			for album in results['albums']:
				widgets.append(urwid.Pile([
					UiButton('{title} {artists}'.format(title=album.title, artists=', '.join(map(lambda e: e.name ,album._artists))), on_press=self.on_album_click, user_data=album, normalColor='album'),
					urwid.Divider(),
				]))
			widgets.append(urwid.Divider('_'))
			widgets.append(urwid.Divider())

		if (len(results['playlists']) > 0):
			widgets.append(urwid.Divider('═'))
			widgets.append(urwid.Text('Плейлисты', align='center'))
			for playlist in results['playlists']:
				widgets.append(urwid.Pile([
					UiButton(playlist.title, on_press=self.open_playlist, user_data=playlist,),
					urwid.Divider(),
				]))
			widgets.append(urwid.Divider('_'))
			widgets.append(urwid.Divider())

		return urwid.LineBox(urwid.BoxAdapter(urwid.ListBox(widgets), height=self.ui.size() - 10))
		
	def build_track(self, track):
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

		return urwid.Columns(trackWidgets)

	def on_track_click(self, el, data):
		self.ui.loop.draw_screen()
		player.start(data, self.tracks)

	def on_artist_click(self, el, data):
		self.ui.setMain(UiArtist(self.ui, data))

	def on_album_click(self, el, data):		
		self.ui.setMain(urwid.Text("Получаю альбом"), False)	
		self.ui.setMain(UiTracksList(self.ui, data.getTracks(), data.title))

	def open_playlist(self, el, data):		
		self.ui.setMain(urwid.Text("Получаю треки"), False)
		tracks = data.getTracks()	
		self.ui.setMain(UiTracksList(self.ui, tracks))	

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

		