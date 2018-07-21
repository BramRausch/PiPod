import os
import RPi.GPIO as GPIO
import pygame
import eyed3
import csv
import random
import alsaaudio
import Adafruit_ADS1x15

currentSong = []
menu = {
    "Main": ["Music", "Applications", "Settings"],
    "Music": ["Artists", "Albums", "Tracks"],
    "Applications": [],
    "Artists": [],
    "Albums": [],
    "Tracks": [],
    "list": [],
    "Queue": [],
    "Settings": ["Sleep", "Shutdown", "Reboot", "Update library"],
    "current": "musicController",
    "history": [],
}

# Define colors
backgroundColor = (0, 0, 0)  # global
primaryColor = (255, 255, 255)  # global
secondaryColor = (100, 100, 255)  # global


class interface:
    selectedItem = 0
    sleep = 0
    metadata = []
    tracks = {}
    artists = []
    albums = []
    playing = 0
    queueIndex = 0
    volume = 15

    def __init__(self):
        os.putenv('SDL_FBDEV', '/dev/fb1')  # Route the output to framebuffer 1 (TFT display)
        pygame.init()
        pygame.font.init()
        self.lcd = pygame.display.set_mode((320, 240))
        pygame.mouse.set_visible(False)
        pygame.key.set_repeat(500, 100)
        self.dispWidth, self.dispHeight = pygame.display.get_surface().get_size()

        self.font = pygame.font.Font("TerminusTTF-4.46.0.ttf", 18)
        pygame.mixer.init()
        pygame.mixer.music.set_volume(1.0)
        self.alsa = alsaaudio.Mixer(alsaaudio.mixers()[0])
        self.alsa.setvolume(self.volume)

        # Load music
        self.load()

        # Initialize ADC
        self.adc = Adafruit_ADS1x15.ADS1115()

        # Set backlight pin as output and turn it on
        GPIO.setwarnings(False)  # disable warning because it is known that the pin is already set as output
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(23, GPIO.OUT)
        GPIO.output(23, GPIO.HIGH)

    def clear(self):
        self.lcd.fill(backgroundColor)

    def toggleSleep(self):
        if self.sleep == 0:
            GPIO.output(23, GPIO.LOW)
            self.sleep = 1
        else:
            GPIO.output(23, GPIO.HIGH)
            self.sleep = 0

    def shutdown(self):
        self.lcd.fill(backgroundColor)
        text = self.font.render("Shutting down", True, primaryColor)
        self.lcd.blit(text, ((self.dispWidth - text.get_width()) / 2, (self.dispHeight - text.get_height()) / 2))
        pygame.display.flip()
        os.system("sudo halt")

    def reboot(self):
        self.lcd.fill(backgroundColor)
        text = self.font.render("Rebooting", True, primaryColor)
        self.lcd.blit(text, ((self.dispWidth - text.get_width()) / 2, (self.dispHeight - text.get_height()) / 2))
        pygame.display.flip()
        os.system("sudo reboot")

    def listView(self, menu):
        self.clear()
        index = 0
        marginTop = (self.dispHeight-9) / 2 - (21 * self.selectedItem)  # text height 18/2=9
        marginLeft = 10
        marginTop += 21 * (self.selectedItem - 12 if self.selectedItem > 12 else 0)
        index += (self.selectedItem - 12 if self.selectedItem > 12 else 0)
        for item in menu[
                    self.selectedItem - 12 if self.selectedItem > 12 else 0:self.selectedItem + 12]:  # I'm sorry, if selected item is more then 4 start slicing the list
            if index == self.selectedItem:
                text = self.font.render(item, True, secondaryColor)
            else:
                text = self.font.render(item, True, primaryColor)
            self.lcd.blit(text, (marginLeft, marginTop))
            marginTop += 21
            index += 1

    def musicController(self):
        self.clear()

        adc0 = self.adc.read_adc(0, gain=1) * (4.096/32767) / 1.2 * 2.2
        adc1 = self.adc.read_adc(1, gain=1) * (4.096/32767) / 1.2 * 2.2
        charginText = self.font.render("Charging" if adc0 > 4.5 else "", True, primaryColor)
        batteryVoltageText = self.font.render("%.2f" % round(adc1, 2), True, primaryColor)
        self.lcd.blit(charginText, (10, 1))
        self.lcd.blit(batteryVoltageText, (self.dispWidth - batteryVoltageText.get_width() - 10, 1))
        pygame.draw.line(self.lcd, primaryColor, (0,20), (self.dispWidth, 20))

        if currentSong:
            artist = self.font.render(currentSong[1], True, primaryColor)
            album = self.font.render(currentSong[2], True, primaryColor)
            title = self.font.render(currentSong[3], True, primaryColor)
            self.lcd.blit(artist, (10, 30))
            self.lcd.blit(album, (10, 51))
            self.lcd.blit(title, (10, 72))

        volumeText = self.font.render(str(self.alsa.getvolume()[0]), True, primaryColor)

        volumeUpText = self.font.render("+", True, secondaryColor if self.selectedItem == 0 else primaryColor)
        volumeDownText = self.font.render("-", True, secondaryColor if self.selectedItem == 1 else primaryColor)
        prevText = self.font.render("Prev", True, secondaryColor if self.selectedItem == 2 else primaryColor)
        playPauseText = self.font.render("Play/Pause", True, secondaryColor if self.selectedItem == 3 else primaryColor)
        nextText = self.font.render("Next", True, secondaryColor if self.selectedItem == 4 else primaryColor)
        shuffleText = self.font.render("Shuffle", True, secondaryColor if self.selectedItem == 5 else primaryColor)
        clearText = self.font.render("Clear", True, secondaryColor if self.selectedItem == 6 else primaryColor)

        self.lcd.blit(volumeText, (self.dispWidth - 10 - volumeText.get_width(), self.dispHeight - 63))
        self.lcd.blit(volumeUpText, (10, self.dispHeight - 63))
        self.lcd.blit(volumeDownText, (15 + volumeDownText.get_width(), self.dispHeight - 63))
        self.lcd.blit(playPauseText, ((self.dispWidth - playPauseText.get_width()) / 2, self.dispHeight - 42))
        self.lcd.blit(prevText, (10, self.dispHeight - 42))
        self.lcd.blit(playPauseText, ((self.dispWidth - playPauseText.get_width()) / 2, self.dispHeight - 42))
        self.lcd.blit(nextText, (self.dispWidth - nextText.get_width() - 10, self.dispHeight - 42))
        self.lcd.blit(shuffleText, (10, self.dispHeight - 21))
        self.lcd.blit(clearText, (self.dispWidth - clearText.get_width() - 10, self.dispHeight - 21))

    def menuAction(self, action):
        if action == "up":
            if self.selectedItem > 0:
                self.selectedItem -= 1
            elif menu["current"] == "Queue":
                menu["history"].pop()
                self.selectedItem = 6
                menu["current"] = "musicController"

        elif action == "down":
            if menu["current"] == "musicController":
                if self.selectedItem < 6:
                    self.selectedItem += 1
                else:
                    menu["history"].append(menu["current"])  # update history
                    menu["current"] = "Queue"  # go to next menu
                    self.selectedItem = 0

            else:
                if self.selectedItem < len(menu[menu["current"]]) - 1:
                    self.selectedItem += 1

        elif action == "select":
            if menu["current"] == "Artists":
                tempList = []
                for item in menu["Tracks"]:
                    if item[1] == menu["Artists"][self.selectedItem]:
                        tempList.append(item)
                menu["list"] = tempList
                menu["current"] = "list"
                self.selectedItem = 0
            elif menu["current"] == "Albums":
                tempList = []
                for item in menu["Tracks"]:
                    if item[2] == menu["Albums"][self.selectedItem]:
                        tempList.append(item)
                menu["list"] = tempList
                menu["current"] = "list"
                self.selectedItem = 0
            elif menu["current"] == "Settings":
                if menu["Settings"][self.selectedItem] == "Update library":
                    self.update()
                elif menu["Settings"][self.selectedItem] == "Sleep":
                    self.toggleSleep()
                elif menu["Settings"][self.selectedItem] == "Shutdown":
                    self.shutdown()
                elif menu["Settings"][self.selectedItem] == "Reboot":
                    self.reboot()
            else:
                if menu[menu["current"]]:  # check if empty
                    menu["history"].append(menu["current"])  # update history
                    menu["current"] = menu[menu["current"]][self.selectedItem]  # go to next menu
                self.selectedItem = 0

        elif action == "left":
            # print(menu["history"])
            self.selectedItem = 0
            if menu["history"]:  # check if history is empty
                menu["current"] = menu["history"][-1::][0]
                menu["history"].pop()
            else:
                menu["current"] = "musicController"

        elif action == "right":
            if menu["current"] == "musicController":
                self.selectedItem = 0
                menu["current"] = "Main"

    def loop(self):
        if self.playing == 1:
            if not pygame.mixer.music.get_busy():
                self.next()

    def update(self):
        self.playPause()
        fileList = []
        # print("Updating metadata")
        musicPath = "/home/pi/musicPlayer/Music/"

        self.lcd.fill(backgroundColor)
        text = self.font.render("Updating Library", True, primaryColor)
        self.lcd.blit(text, ((self.dispWidth - text.get_width()) / 2, (self.dispHeight - text.get_height()) / 2))
        pygame.display.flip()

        for path, dirs, files in os.walk(musicPath):
            for file in files:
                if file.endswith('.mp3'):
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
                audiofile = eyed3.load(i)
                tag = audiofile.tag
            except:
                pass
            try:
                writer.writerow((i, tag.artist, tag.album, tag.title))
            except AttributeError:
                print(i)
        print("Done")
        file.close()
        self.load()
        menu["history"] = []
        menu["current"] = "musicController"


    def load(self):
        file = open("info.csv", "rt")
        menu["Artists"] = []
        menu["Albums"] = []
        menu["Tracks"] = []
        try:
            reader = csv.reader(file)
            for row in reader:
                artistClear = row[1].lstrip().lower().title()
                albumClear = row[2].lstrip().lower().title()
                if artistClear is not "":
                    if artistClear not in menu["Artists"]:
                        menu["Artists"].append(artistClear)
                if albumClear is not "":
                    if albumClear not in menu["Albums"]:
                        menu["Albums"].append(albumClear)
                if row[3].lstrip() is not "":
                    self.metadata.append(
                        [row[0], artistClear, albumClear, row[3].lstrip()])  # [filename, artist, album, title]
        finally:
            file.close()

        menu["Artists"].sort()
        menu["Albums"].sort()
        menu["Tracks"] = sorted(self.metadata, key=lambda meta: meta[3])

    def play(self, info):
        global currentSong
        currentSong = list(info)
        # print(currentSong)
        pygame.mixer.music.load(info[0])
        pygame.mixer.music.play()
        self.playing = 1

    def insertNext(self, song):
        menu["Queue"].insert(self.queueIndex + 1, song)  # Put selected at first position

    def playPause(self):
        if self.playing:
            self.playing = 0
            pygame.mixer.music.pause()
        elif not self.playing:
            self.playing = 1
            pygame.mixer.music.unpause()

    def shuffle(self):
        # Before shuffling remove the already played songs to make sure these don't get played again
        currentIndex = menu["Queue"].index(currentSong) + 1
        history = menu["Queue"][0:currentIndex]
        menu["Queue"] = menu["Queue"][currentIndex::]
        random.shuffle(menu["Queue"])
        # Add the already played songs to the front again
        menu["Queue"] = history + menu["Queue"]

    def clearQueue(self):
        del currentSong[:]
        self.playing = 0
        pygame.mixer.music.pause()
        menu["Queue"] = []

    def next(self):
        if self.queueIndex < len(menu["Queue"]) - 1:
            self.queueIndex += 1
            self.play(menu["Queue"][self.queueIndex])

    def prev(self):
        if self.queueIndex > 0:
            self.queueIndex -= 1
            self.play(menu["Queue"][self.queueIndex])

    def volumeUp(self):
        if self.volume <= 95:
            self.volume += 5
            self.alsa.setvolume(self.volume)
            # pygame.mixer.music.set_volume(self.volume/100)
            print(self.volume)

    def volumeDown(self):
        if self.volume > 5:
            self.volume -= 5
            self.alsa.setvolume(self.volume)
            # pygame.mixer.music.set_volume(self.volume/100)
