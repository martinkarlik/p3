import pygame
import cv2
import random
from src import game_algorithms
from src import game_interface

random_cup = False

FONT_SANS_BOLD = ['freesansbold.ttf', 40]
TAPE_IMAGE = "../images/tableImages/tape.png"
ICON = "../images/cheers.png"
TABLE_IMAGES = ["../images/tableImages/choose_game_mode.png", "../images/tableImages/PlaceCups.png"]

SONGS = ["../sound/mass_effect_elevator_music_2.mp3", "../sound/epic_musix.mp3"]  # you_can_add_more
SOUNDS = ["../sound/cuteguisoundsset/Wav/Select.wav", "../sound/cuteguisoundsset/Wav/Achievement.wav",
          "../sound/cuteguisoundsset/Wav/Cursor.wav", "../sound/hit_the_golden_cup_jingle.wav"]

if __name__ == '__main__':
    # CAPTURE SETUP
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_EXPOSURE, -5)

    # PYGAME SETUP
    pygame.init()
    pygame.display.set_caption("BeerPong")
    icon = pygame.image.load(ICON)
    pygame.display.set_icon(icon)

    # Select, Achievement, cursor

    jingle = pygame.mixer.Channel(3)
    sound_fx = []
    for sound in SOUNDS:
        sound_fx.append(pygame.mixer.Sound(sound))

    screen = pygame.display.set_mode((game_interface.DISPLAY_WIDTH, game_interface.DISPLAY_HEIGHT))
    font = pygame.font.Font(FONT_SANS_BOLD[0], FONT_SANS_BOLD[1])
    table_img = game_interface.set_table_img(TABLE_IMAGES[1])
    tape_img = pygame.image.load(TAPE_IMAGE)
    tpl = cv2.imread("../images/testImages/beer.jpg",
                     cv2.IMREAD_GRAYSCALE)  # this template will be replaced by a numpy array with 1's where the circle is and 0's where not

    # GAME LOGIC SETUP
    game_phase = "game_play"
    modes = [game_interface.Button("CASUAL", [0.3, 0.5, 0.1, 0.4], True),
             game_interface.Button("COMPETITIVE", [0.3, 0.5, 0.6, 0.9], True),
             game_interface.Button("CUSTOM", [0.7, 0.9, 0.1, 0.4], False),
             game_interface.Button("EASTERN EUROPEAN", [0.7, 0.9, 0.6, 0.9], False)]

    gameoverbutton = [game_interface.Button("PLAY AGAIN", [0.3, 0.5, 0.5, 0.75], False)]

    team_a = [game_interface.Player(game_interface.Player.team_names[i], game_interface.Player.team_colors[i]) for i in range(0, game_interface.Player.players_num)]
    team_a[random.randint(0, len(team_a) - 1)].drinks = True

    team_b = [game_interface.Player(game_interface.Player.team_names[i], game_interface.Player.team_colors[i]) for i in
              range(0, game_interface.Player.players_num)]
    team_b[random.randint(0, len(team_b) - 1)].drinks = True

    beers_left = []
    beers_right = []

    selection_music_playing = False
    gameplay_music_playing = False

    _, frame = cap.read()
    table_transform = game_algorithms.find_table_transform(frame, game_algorithms.TABLE_SHAPE)
    print(table_transform)

    app_running = True
    while app_running and cap.isOpened():

        _, frame = cap.read()
        table = game_algorithms.apply_transform(frame, table_transform, game_algorithms.TABLE_SHAPE)

        ###cv2.imshow("table", table)
        cv2.waitKey(1)

        if game_phase == "mode_selection":
            game_algorithms.choose_option(table, modes)

            if not selection_music_playing:
                selection_music_playing = True
                pygame.mixer.music.stop()
                pygame.mixer.music.load(SONGS[0])
                pygame.mixer.music.play(-1)

            for mode in modes:
                if mode.chosen:
                    mode.meter = min(mode.meter + 2, 100)
                else:
                    pygame.mixer.stop()
                    mode.meter = max(mode.meter - 6, 0)

                if mode.meter >= 100:
                    sound_fx[0].play()
                    game_phase = "game_play"
                    table_img = game_interface.set_table_img(TABLE_IMAGES[1])

            # game_interface.display_table_img(screen, table_img)
            game_interface.display_mode_selection(screen, font, tape_img, modes)

        elif game_phase == "game_play":

            if not gameplay_music_playing:
                gameplay_music_playing = True
                pygame.mixer.music.stop()
                pygame.mixer.music.load(SONGS[1])
                pygame.mixer.music.play(-1)

            current_beers_left = []
            current_beers_right = []

            game_algorithms.extract_beers(table, tpl, current_beers_left, current_beers_right)
            game_algorithms.inform_beers(beers_left, beers_right, current_beers_left, current_beers_right)
            game_algorithms.check_for_objects(table, beers_left, beers_right)

            # -------------------------

            # region Wand Detection/ Golden cup
            for beer in beers_left:
                if beer.wand_here:
                    beer.meter += 10
                else:
                    beer.meter = max(beer.meter - 10, 0)
                if beer.meter == 100 and not jingle.get_busy():
                    jingle.play(sound_fx[3])
                if beer.meter >= 100:
                    beer.yellow = True
                if beer.yellow:
                    # Display text Gold cup text: for when the left side has highlighted a cup in the right side. So
                    # a cup on the right is highlighted
                    golden_cup_txt = font.render('Golden Cup active', True, (255, 255, 0))
                    rotated_text = pygame.transform.rotate(golden_cup_txt, 90)
                    screen.blit(rotated_text, rotated_text.get_rect(center=((game_interface.DISPLAY_WIDTH / 2) + 50,
                                                                            game_interface.DISPLAY_HEIGHT / 2)))

                    print(beer.counter)
                    beer.counter -= 1
                    if beer.counter <= 0:
                        beer.yellow = False
                        beer.counter = 100

            for beer in beers_right:
                if beer.wand_here:
                    beer.meter += 10
                else:
                    beer.meter = max(beer.meter - 10, 0)
                if beer.meter == 100 and not jingle.get_busy():
                    jingle.play(sound_fx[3])
                if beer.meter >= 100:
                    beer.yellow = True
                if beer.yellow:
                    # Display text Gold cup text: for when the left side has highlighted a cup in the right side. So
                    # a cup on the right is highlighted
                    golden_cup_txt = font.render('Golden Cup active', True, (255, 255, 0))
                    rotated_text = pygame.transform.rotate(golden_cup_txt, -90)
                    screen.blit(rotated_text, rotated_text.get_rect(center=((game_interface.DISPLAY_WIDTH / 2) - 50,
                                                                            game_interface.DISPLAY_HEIGHT / 2)))

                    beer.counter -= 1
                    if beer.counter <= 0:
                        beer.yellow = False
                        beer.counter = 100

            for i in range(0, len(beers_left)):
                if beers_left[i].yellow:
                    min_dist = 1000
                    red_index = -1
                    for j in range(0, len(beers_left)):
                        if j == i:
                            continue
                        else:
                            distance = abs(beers_left[i].center[0] - beers_left[j].center[0]) + abs(
                                beers_left[i].center[1] - beers_left[j].center[1])
                            if distance < min_dist:
                                min_dist = distance
                                red_index = j
                    if red_index > -1:
                        beers_left[red_index].red = True
                        # This is extremely dumb, help me
                        # if not beers_left[i].yellow:
                        #     beers_left[red_index].red = False
                        #     beers_left[i].red = False
                else:
                    beers_left[i].red = False

            for i in range(0, len(beers_right)):
                if beers_right[i].yellow:
                    min_dist = 1000
                    red_index = -1
                    for j in range(0, len(beers_right)):
                        if j == i:
                            continue
                        else:
                            distance = abs(beers_right[i].center[0] - beers_right[j].center[0]) + abs(
                                beers_right[i].center[1] - beers_right[j].center[1])
                            if distance < min_dist:
                                min_dist = distance
                                red_index = j
                    if red_index > -1:
                        beers_right[red_index].red = True
                        # This is extremely dumb, help me
                        # if not beers_right[i].yellow:
                        #     beers_right[red_index].red = False
                        #     beers_right[i].red = False
                else:
                    beers_right[i].red = False
            # endregion

            # region Score detection
            for beer in beers_left:
                for i in range(0, len(beer.balls)):
                    if beer.balls[i] and not team_b[i].hit:
                        team_b[i].score += 1
                        team_b[i].hit = True
                        for player in team_a:
                            if player.drinks:
                                beer.color = player.color

                    elif team_b[i].hit and not beer.balls[i]:
                        for j in range(1, len(team_a)):
                            if team_a[j].drinks:
                                team_a[j].drinks = False
                                team_a[j + 1 if j + 1 < len(team_a) else 0].drinks = True

            for beer in beers_right:
                for i in range(0, len(beer.balls)):
                    if beer.balls[i] and not team_a[i].hit:
                        team_a[i].score += 1
                        team_a[i].hit = True

                    elif team_a[i].hit and not beer.balls[i]:
                        for j in range(1, len(team_b)):
                            if team_b[j].drinks:
                                team_b[j].drinks = False
                                team_b[j + 1 if j + 1 < len(team_b) else 0].drinks = True
            # endregion
            # -------------------------

            print(len(beers_left), len(beers_right))
            game_interface.display_table_img(screen, table_img)
            game_interface.display_score(screen, font, team_a, team_b)
            game_interface.display_beers(screen, beers_left, beers_right)

        elif game_phase == "game_over":
            game_interface.display_table_img(screen, table_img)
            game_algorithms.choose_option(table, gameoverbutton)

            for gameobutton in gameoverbutton:
                if gameobutton.chosen:
                    gameobutton.meter = min(gameobutton.meter + 2, 100)
                else:
                    pygame.mixer.stop()
                    gameobutton.meter = max(gameobutton.meter - 6, 0)

                if gameobutton.meter >= 100:
                    #sound_fx[0].play()
                    game_phase = "game_mode"
                    table_img = game_interface.set_table_img(TABLE_IMAGES[1])

            game_interface.game_over(screen, team_a, team_b, font, font)
            game_interface.gamebutton(screen, font, gameoverbutton)

        # KEYBOARD INPUT
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                app_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    app_running = False
                if event.key == pygame.K_SPACE:
                    random_cup = True
                    print('You have pressed spacebar')

        pygame.display.update()

    cap.release()
    cv2.destroyAllWindows()
