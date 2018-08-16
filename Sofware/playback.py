import vlc
import random
import alsaaudio
import os
import csv
import taglib

class music():
    volume = 15
    playlist = [["", "", "", ""]]
    currentSongIndex = 0
    
    def __init__(self):
        self.vlcInstance = vlc.Instance()
        self.player = self.vlcInstance.media_player_new()
        self.alsa = alsaaudio.Mixer(alsaaudio.mixers()[0])
        self.alsa.setvolume(self.volume)

    def getStatus(self):
        status = {
            "songLength": self.player.get_length(),
            "currentTime": self.player.get_time(),
            "currentSong": self.playlist[self.currentSongIndex],
            "volume": self.alsa.getvolume()[0],
            "playlist": self.playlist
        }
        return status

    def loop(self):
        if self.player.get_state() == vlc.State.Ended and self.currentSongIndex < len(self.playlist)-1:
            self.currentSongIndex += 1
            self.play()
        
    def loadList(self, songList):
        self.playlist = songList
        self.currentSongIndex = 0
        self.play()

    def updateList(self, newList):
        if self.playlist[0] == ["", "", "", ""]:
            self.playlist.pop(0)
            self.playlist = newList
            self.currentSongIndex = 0
            self.play()
        else:
            self.currentSongIndex = newList.index(self.playlist[self.currentSongIndex])
            self.playlist = newList
        
    def play(self):
        # print(currentSong)
        self.player.set_media(self.vlcInstance.media_new_path(self.playlist[self.currentSongIndex][0]))
        self.player.play()

    def playAtIndex(self, index):
        self.currentSongIndex = index
        self.player.set_media(self.vlcInstance.media_new_path(self.playlist[self.currentSongIndex][0]))
        self.player.play()

    def playPause(self):
        if self.player.get_state() == vlc.State.Playing:
            self.player.pause()
        elif not self.player.get_state() == vlc.State.Playing:
            self.player.play()

    def shuffle(self):
        # Before shuffling remove the already played songs to make sure these don't get played again
        tempPlaylist = self.playlist[self.currentSongIndex + 1::]
        random.shuffle(tempPlaylist)
        # Add the already played songs to the front again
        self.playlist = self.playlist[:self.currentSongIndex + 1] + tempPlaylist

    def clearQueue(self):
        self.playlist = [["", "", "", ""]]
        self.currentSongIndex = 0
        self.player.stop()

    def next(self):
        if self.currentSongIndex < len(self.playlist)-1:
            self.currentSongIndex += 1
            self.play()

    def prev(self):
        if self.currentSongIndex > 0:
            self.currentSongIndex -= 1
            self.play()

    def volumeUp(self):
        if self.volume <= 95:
            self.volume += 5
            self.alsa.setvolume(self.volume)
            print(self.volume)

    def volumeDown(self):
        if self.volume > 5:
            self.volume -= 5
            self.alsa.setvolume(self.volume)

    def updateLibrary(self):
        self.playPause()
        fileList = []
        # print("Updating metadata")
        musicPath = "/home/pi/musicPlayer/Music/"

        for path, dirs, files in os.walk(musicPath):
            for file in files:
                if file.endswith('.mp3') or file.endswith('.m4a') or file.endswith('.wav') or file.endswith('.wma'):
                    fileList.append(os.path.join(path, file))
                    print(os.path.join(path, file))
        '''
            for f in files:
                filename = os.path.join(root, f)
                if filename.endswith('.mp3'):
                    fileList.append(filename)
        '''
        file = open("info.csv", "w", newline="")
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # print("Saving metadate")
        for i in fileList:
            try:
                audiofile = taglib.File(i)
                tag = audiofile.tags
            except:
                pass
            try:
                writer.writerow((i, tag["ARTIST"][0], tag["ALBUM"][0], tag["TITLE"][0]))
            except AttributeError:
                print(i)
        print("Done")
        file.close()

        return 1