import pygame
import os

backgroundColor = (0, 0, 0)  # global
primaryColor = (255, 255, 255)  # global
secondaryColor = (100, 100, 255)  # global


class view():
    def __init__(self):
        os.putenv('SDL_FBDEV', '/dev/fb1')  # Route the output to framebuffer 1 (TFT display)
        pygame.init()
        pygame.font.init()
        self.lcd = pygame.display.set_mode((320, 240))
        pygame.mouse.set_visible(False)
        pygame.key.set_repeat(500, 100)
        self.dispWidth, self.dispHeight = pygame.display.get_surface().get_size()
        self.font = pygame.font.Font("TerminusTTF-4.46.0.ttf", 18)

    def update(self, status, menuDict, songMetadata):
        if menuDict["current"] == "musicController":
            self.musicController(
                menuDict["selectedItem"],
                status[1],
                status[0],
                songMetadata["currentSong"],
                songMetadata["currentTime"],
                songMetadata["songLength"],
                songMetadata["volume"]
            )
        elif menuDict["current"] == "Tracks":
            self.listView(list(map(lambda x: x[3], menuDict[menuDict["current"]])), menuDict["selectedItem"])
        elif menuDict["current"] == "Queue":
            self.listView(["Clear queue"] + list(map(lambda x: x[3], menuDict[menuDict["current"]])), menuDict["selectedItem"])
        elif menuDict["current"] == "list":
            self.listView(list(map(lambda x: x[3], menuDict["list"])), menuDict["selectedItem"])
        else:
            self.listView(menuDict[menuDict["current"]], menuDict["selectedItem"])

        pygame.display.update()

    def clear(self):
        self.lcd.fill(backgroundColor)

    def popUp(self, text):
        self.lcd.fill(backgroundColor)
        text = self.font.render(text, True, primaryColor)
        self.lcd.blit(text, ((self.dispWidth - text.get_width()) / 2, (self.dispHeight - text.get_height()) / 2))
        pygame.display.flip()

    def listView(self, menu, selectedItem):
        self.clear()
        index = 0
        marginTop = (self.dispHeight - 9) / 2 - (21 * selectedItem)  # text height 18/2=9
        marginLeft = 10
        marginTop += 21 * (selectedItem - 12 if selectedItem > 12 else 0)
        index += (selectedItem - 12 if selectedItem > 12 else 0)
        for item in menu[
                    selectedItem - 12 if selectedItem > 12 else 0:selectedItem + 12]:  # I'm sorry, if selected item is more then 4 start slicing the list
            if index == selectedItem:
                text = self.font.render(item, True, secondaryColor)
            else:
                text = self.font.render(item, True, primaryColor)
            self.lcd.blit(text, (marginLeft, marginTop))
            marginTop += 21
            index += 1

    def musicController(self, selectedItem, batLevel, chargeStatus, currentSong, currentTime, songLength, volume):
        self.clear()

        # Status bar
        volumeText = self.font.render(str(volume) + "%", True, primaryColor)
        self.lcd.blit(volumeText, (10, 1))

        if chargeStatus:
            chargeText = self.font.render("Charging", True, primaryColor)
            self.lcd.blit(chargeText, (self.dispWidth - chargeText.get_width() - 10, 1))
        else:
            chargeText = self.font.render(batLevel, True, primaryColor)
            self.lcd.blit(chargeText, (self.dispWidth - chargeText.get_width() - 10, 1))

        pygame.draw.line(self.lcd, primaryColor, (0, 20), (self.dispWidth, 20))

        # Current song information
        if currentSong:
            artist = self.font.render(currentSong[1], True, primaryColor)
            album = self.font.render(currentSong[2], True, primaryColor)
            title = self.font.render(currentSong[3], True, primaryColor)
            self.lcd.blit(artist, (10, 30))
            self.lcd.blit(album, (10, 51))
            self.lcd.blit(title, (10, 72))

        # Time bar
        pygame.draw.rect(self.lcd, primaryColor, (10, self.dispHeight - 18, self.dispWidth - 20, 15), 1)

        if songLength > 0:
            progress = round((self.dispWidth - 20) * currentTime / songLength)
            pygame.draw.rect(self.lcd, primaryColor, (10, self.dispHeight - 18, progress, 15))
            currentTimeText = self.font.render(
                "{0:02d}:{1:02d} / ".format(int(currentTime / 1000 / 60), round(currentTime / 1000 % 60)), True,
                primaryColor)
            songLengthText = self.font.render(
                "{0:02d}:{1:02d}".format(int(songLength / 1000 / 60), round(songLength / 1000 % 60)), True,
                primaryColor)
        else:
            currentTimeText = self.font.render("00:00 / ", True, primaryColor)
            songLengthText = self.font.render("00:00", True, primaryColor)

        self.lcd.blit(currentTimeText, (10, self.dispHeight - 39))
        self.lcd.blit(songLengthText, (10 + currentTimeText.get_width(), self.dispHeight - 39))

