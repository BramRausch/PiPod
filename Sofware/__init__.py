import controls
import pygame

done = False
inter = controls.interface()
inter.musicController()
menu = controls.menu
displayUpdate = pygame.USEREVENT + 1
pygame.time.set_timer(displayUpdate, 20000)

def updateDisplay():
    if not inter.sleep:
        # [filename, artist, album, title]
        if menu["current"] == "musicController":
            inter.musicController()
        elif menu["current"] == "Tracks" or menu["current"] == "Queue":
            inter.listView(list(map(lambda x: x[3], menu[menu["current"]])))
        elif menu["current"] == "list":
            inter.listView(list(map(lambda x: x[3], menu["list"])))
        else:
            inter.listView(menu[menu["current"]])

        pygame.display.update()

updateDisplay()

while not done:
    inter.loop()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                inter.toggleSleep()
            elif event.key == pygame.K_u:
                inter.volumeUp()
            elif event.key == pygame.K_d:
                inter.volumeDown()
            elif event.key == pygame.K_UP:
                if inter.sleep:
                    inter.volumeUp()
                else:
                    inter.menuAction("up")
            elif event.key == pygame.K_DOWN:
                if inter.sleep:
                    inter.volumeDown()
                else:
                    inter.menuAction("down")
            elif event.key == pygame.K_LEFT:
                if inter.sleep:
                    inter.prev()
                else:
                    inter.menuAction("left")
            elif event.key == pygame.K_RIGHT:
                if inter.sleep:
                    inter.next()
                elif menu["current"] == "list" or menu["current"] == "Tracks":
                    inter.insertNext(menu[menu["current"]][inter.selectedItem])
                # menu["Queue"].insert(1, menu[menu["current"]][inter.selectedItem])  # Put selected at first position
                else:
                    inter.menuAction("right")
            elif event.key == pygame.K_RETURN:
                if inter.sleep:
                    inter.playPause()
                elif menu["current"] == "list" or menu["current"] == "Tracks":
                    inter.play(menu[menu["current"]][inter.selectedItem])  # Play the selected song
                    if menu["Queue"]:
                        for item in list(menu[menu["current"]]):
                            if item not in menu["Queue"]:
                                menu["Queue"].append(item)
                    else:
                        menu["Queue"] = list(
                            menu[menu["current"]])  # copy the list where the song is selected to the queue
                    menu["Queue"].remove(menu[menu["current"]][inter.selectedItem])  # Remove selected
                    menu["Queue"].insert(0, menu[menu["current"]][inter.selectedItem])  # Put selected at first position
                elif menu["current"] == "musicController":
                    if inter.selectedItem == 0:
                        inter.volumeUp()
                    elif inter.selectedItem == 1:
                        inter.volumeDown()
                    elif inter.selectedItem == 2:
                        inter.prev()
                    elif inter.selectedItem == 3:
                        inter.playPause()
                    elif inter.selectedItem == 4:
                        inter.next()
                    elif inter.selectedItem == 5:
                        inter.shuffle()
                    elif inter.selectedItem == 6:
                        inter.clearQueue()
                else:
                    inter.menuAction("select")

        updateDisplay()


      # display.update() without arguments updates the entire display just like display.flip()
    pygame.time.Clock().tick(
        40)  # Limit the framerate to 20 FPS, this is to ensure it doesn't use all of the CPU resources
