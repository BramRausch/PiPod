#!/usr/bin/python3
import playback
import display
import navigation
import device
import pygame

done = False
music = playback.music()
view = display.view()
menu = navigation.menu()
PiPod = device.PiPod()

menu.loadMetadata()
status = PiPod.getStatus()
songMetadata = music.getStatus()

displayUpdate = pygame.USEREVENT + 1
pygame.time.set_timer(displayUpdate, 500)

view.update(status, menu.menuDict, songMetadata)

while not done:
    music.loop()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                PiPod.toggleSleep()

            elif event.key == pygame.K_u:
                music.volumeUp()

            elif event.key == pygame.K_d:
                music.volumeDown()

            elif event.key == pygame.K_UP:
                if status[2]:
                    music.volumeUp()
                elif menu.menuDict["current"] == "musicController":
                    menu.gotomenu()
                else:
                    action = menu.up()

            elif event.key == pygame.K_DOWN:
                if status[2]:
                    music.volumeDown()
                elif menu.menuDict["current"] == "musicController":
                    music.shuffle()
                    menu.menuDict["Queue"] = music.playlist
                else:
                    action = menu.down()

            elif event.key == pygame.K_LEFT:
                if status[2] or menu.menuDict["current"] == "musicController":
                    music.prev()
                else:
                    action = menu.left()

            elif event.key == pygame.K_RIGHT:
                if status[2] or menu.menuDict["current"] == "musicController":
                    music.next()
                else:
                    action = menu.right()
                    if action == "updateList":
                        music.updateList(menu.menuDict["Queue"])

            elif event.key == pygame.K_RETURN:
                if status[2] or menu.menuDict["current"] == "musicController":
                    music.playPause()
                else:
                    action = menu.select()
                    if action == "play":
                        music.loadList(menu.menuDict["Queue"])
                        music.play()
                    elif action == "clearQueue":
                        menu.menuDict["Queue"] = []
                        music.clearQueue()
                    elif action == "updateLibrary":
                        if music.updateLibrary():
                            done = True
                    elif action == "toggleSleep":
                        PiPod.toggleSleep()
                    elif action == "shutdown":
                        while not PiPod.shutdown():
                            view.popUp("Shutdown")
                    elif action == "reboot":
                        while not PiPod.reboot():
                            view.popUp("Reboot")
                    elif action == "playAtIndex":
                        if menu.menuDict["selectedItem"] == 0:
                            music.clearQueue()
                            menu.menuDict["Queue"] = []
                        else:
                            music.playAtIndex(menu.menuDict["selectedItem"]-1)

        status = PiPod.getStatus()
        songMetadata = music.getStatus()
        view.update(status, menu.menuDict, songMetadata)


      # display.update() without arguments updates the entire display just like display.flip()
    pygame.time.Clock().tick(
        30)  # Limit the framerate to 20 FPS, this is to ensure it doesn't use all of the CPU resources

