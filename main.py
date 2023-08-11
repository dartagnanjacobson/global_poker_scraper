# chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\selenium\AutomationProfile"
from hand_grabber import *
from hand_class import *
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from datetime import *
import time
import re
import sys

start_time = time.time()

# This block allows Selenium to access an open browser window
service = Service("C:\\Users\\Bjorn Jacobson\\PycharmProjects\\GP_Scraper\\GP_Scraper\\chromedriver.exe")
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("debuggerAddress", '127.0.0.1:9222')
driver = webdriver.Chrome(service=service, options=chrome_options)
ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)

# This block creates a new hand history file each time the program is run with the filename being the time
# the program started
x = datetime.now()
x = str(x)
x = convert(x)
for y in x:
    if y == ":" or y == ".":
        x[x.index(y)] = "-"
x = list_to_string(x)
f = open("GP_Hand_History" + str(x) + ".txt", "x")
# This loop grabs one hand and writes it to the file with each iteration

count = 0
previous_hand_id = ""
while count < 10000:
    current_hand = Hand()
    print(count+1)
    # driver.implicitly_wait(5)
    suit_list = []
    bb_player_id = "undefined"
    sb_player_id = "undefined"
    button_seat_number = 10
    warioman_hand = ""
    count += 1
    player_hand_results = []
    action = []
    player_id_list = []
    # This block grabs the table data (table name, stakes, etc.)
    table = WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions).until(
        expected_conditions.presence_of_element_located(
            (By.XPATH, "//*[@id='profilePageView']/div/div/div[3]/div[2]/div/div[2]/div/div[1]/div[2]")))

    hand_start_time = WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions).until(
        expected_conditions.presence_of_element_located(
            (By.XPATH, "//*[@id='profilePageView']/div/div/div[3]/div[2]/div/div[2]/div/div[1]/div[3]"))).text
    hand_id = hand_start_time[hand_start_time.index("Hand: ")+6:]

    while previous_hand_id == hand_id:
        table = WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, "//*[@id='profilePageView']/div/div/div[3]/div[2]/div/div[2]/div/div[1]/div[2]")))

        hand_start_time = WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, "//*[@id='profilePageView']/div/div/div[3]/div[2]/div/div[2]/div/div[1]/div[3]"))).text
        hand_id = hand_start_time[hand_start_time.index("Hand: ") + 6:]

    html = driver.page_source
    p = re.findall("suit-icon-[cdhs]", html)
    for q in range(0, len(p)):
        suit_list.append(p[q][-1:])
    # print(html)
    # Stakes is a list that stores 3 variables (table name, stakes, and game type)
    stakes = table.get_attribute('innerHTML').split(',')
    stakes[1] = stakes[1][1:]
    stakes[2] = stakes[2][1:]
    if stakes[2] == "NL Hold\'em":
        stakes[2] = "Hold\'em No Limit"

    hand_date = hand_start_time[hand_start_time.index("Hand Started: ")+14:hand_start_time.index(" - H")]
    hand_date = datetime.strptime(hand_date, '%B %d, %Y %I:%M %p').strftime('%Y/%m/%d %H:%M:%S')
    hand_date = hand_date + " ET"

    f.write("PokerStars Hand #" + hand_id + ":  " + stakes[2] + " ($" + stakes[1][:stakes[1].index("/")] + "/$" + str("%.2f" % float(stakes[1][stakes[1].index("/")+1:])) + " USD) - " + hand_date + "\n")

    # This block prints hand results for each player
    for i in range(1, len(driver.find_elements(By.XPATH, "//*[@id='profilePageView']/div/div/div[3]/div[2]/div/div["
                                                         "2]/div/div[2]/div/table/tbody/tr")) + 1):
        try:
            player_hand_results.append(WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions).until(
                expected_conditions.presence_of_element_located(
                    (By.XPATH, "//*[@id='profilePageView']/div/div/div[3]/div[2]/div/div["
                               "2]/div/div[2]/div/table/tbody/tr[" + str(i) + "]"))).text)
            player_id = (player_hand_results[i-1][0:11])
            if player_id[0] == "w":
                player_id = "warioman"
            player_id_list.append(player_id)
        except:
            pass

    # This block iterates through the table and prints the action
    for j in range(1, 5):
        try:
            for i in range(1, len(driver.find_elements(By.XPATH, "/html/body/div[2]/div/div[2]/div[2]/div/div/div["
                                                                 "3]/div[2]/div/div[2]/div/div[4]/div[" + str(j)
                                                                 + "]/table/tbody/tr")) + 1):
                action.append(WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions).until(
                    expected_conditions.presence_of_element_located(
                        (By.XPATH, "/html/body/div[2]/div/div[2]/div[2]/div/div/div[3]/div["
                                   "2]/div/div[2]/div/div[4]/div[" + str(j) +
                                   "]/table/tbody/tr[" + str(i) + "]"))).text)
        except:
            pass


    # t is small blind index in action list
    try:
        t = 0
        while action[t][0:6] == "System" or action[t][:-8] == "Waiting" or action[t][-17:] == "Decline Entry Bet":
            t += 1
        sb_player_id = action[t][0:11]
        if sb_player_id[0] == "w":
            sb_player_id = "warioman"
        bb_player_id = action[t+1][0:11]
        if bb_player_id[0][0] == "w":
            bb_player_id = "warioman"
        button_seat_number = player_id_list.index(sb_player_id)
        if button_seat_number == 0:
            button_seat_number = 6
    except:
        pass
    f.write("Table '" + stakes[0] + "' 6-max Seat #" + str(button_seat_number) + " is the button\n")
    chip_stack_list = []
    list2 = []

    # print(table.get_attribute('innerHTML') + " " + hand_id)

    current_hand.player_hand_results = player_hand_results.copy()
    current_hand.player_hand_results_static = player_hand_results.copy()
    current_hand.action = action.copy()
    current_hand.action_static = action.copy()
    current_hand.first_line = "PokerStars Hand #" + hand_id + ":  " + stakes[2] + " ($" + "%.2f" % float(stakes[1][:stakes[1].index(
        "/")]) + "/$" + str("%.2f" % float(stakes[1][stakes[1].index("/") + 1:])) + " USD) - " + hand_date
    current_hand.second_line = "Table '" + stakes[0] + "' 6-max Seat #" + str(button_seat_number) + " is the button"
    current_hand.suit_list = suit_list

    for g in range(0, len(current_hand.action)):
        current_hand.action[g] = format_action(current_hand.action[g])

    current_hand.action_separator(current_hand.action)

    current_hand.get_waiters()
    current_hand.format_results()

    current_hand.get_blinds()
    current_hand.raise_format()
    current_hand.blinds_output()
    current_hand.get_folds()

    try:
        for i in current_hand.action_static:
            if i.find("warioman Was dealt") != -1:
                current_hand.get_user_hand()

        for i in current_hand.action_static:
            if i.find("Flop") != -1:
                current_hand.get_flop()

        for i in current_hand.action_static:
            if i.find("Turn") != -1:
                current_hand.get_turn()

        for i in current_hand.action_static:
            if i.find("River") != -1:
                current_hand.get_river()
    except IndexError:
        pass
    current_hand.get_player_ids()
    current_hand.get_pot()
    current_hand.get_rake()
    current_hand.collected_pot()
    current_hand.create_summary()
    current_hand.add_uncalled_bets()
    current_hand.is_allin()

    current_hand.print_action()
    sys.stdout = sys.__stdout__
    current_hand.print_action2()
    print(current_hand)

    if current_hand.allin_list:
        print("all-in list")
        print(current_hand.allin_list)

    for z in range(1, len(player_id_list) + 1):
        list2 = player_hand_results[z-1].split()
        chip_stack = "%.2f" % float(list2[1])
        chip_stack_list.append(chip_stack)

    for z in range(1, len(player_hand_results) + 1):
        f.write("Seat " + str(z) + ": " + player_id_list[z - 1] + " ($" + chip_stack_list[z - 1] + " in chips)\n")
    count3 = 0
    for w in player_hand_results:
        if w[-3:] != "N/A":
            count3 += 5
    warioman_suits = suit_list[count3:count3+2]
    for z in action:
        if z[0] == "w" and z.find("Was dealt") != -1:
            warioman_hand = z
            break
        else:
            warioman_hand = ""
    if warioman_hand != "":
        warioman_hand = warioman_hand[-2:]
        warioman_hand = warioman_hand[0] + warioman_suits[0] + " " + warioman_hand[1] + warioman_suits[1]
    # print(warioman_hand)
    preflop_action = []
    for s in action:
        if s.find("Blind") != -1 or s.find("Was dealt") != -1:
            continue
        else:
            preflop_action.append(s)
    preflop_action2 = preflop_action.copy()
    # print("stakes")
    # print(stakes[1])
    f.write(sb_player_id + ": posts small blind $" + str("%.2f" % float(stakes[1][:stakes[1].index("/")])) + "\n")
    f.write(bb_player_id + ": posts big blind $" + str("%.2f" % float(stakes[1][stakes[1].index("/") + 1:])) + "\n")
    big_blind = str("%.2f" % float(stakes[1][stakes[1].index("/") + 1:]))
    small_blind = str("%.2f" % float(stakes[1][:stakes[1].index("/")]))
    # print(big_blind)
    f.write("*** HOLE CARDS ***\n")
    count2 = 0
    for w in player_hand_results:
        if w[-3:] != "N/A":
            count2 += 5
    f.write("Dealt to warioman [" + warioman_hand + "]\n")
    count4 = 0
    for g in preflop_action:
        if g.find("Fold") != -1:
            preflop_action[count4] = preflop_action[count4][:-5]
            preflop_action[count4] += ": folds"
        count4 += 1
    count5 = 0
    for g in preflop_action:
        if g.find("Call") != -1:
            if g[0] == "w":
                index1 = 8
            else:
                index1 = 11
            player_temp_id = g[:index1]
            preflop_action[count5] = preflop_action[count5][index1:]
            preflop_action[count5] = preflop_action[count5][5:]
            preflop_action[count5] = player_temp_id + ": calls " + preflop_action[count5]
            bet = preflop_action[count5][-5:]
            while bet[0] == " " or re.match("[a-z]", bet[0]) is not None:
                bet = bet[1:]
            bet = ("%.2f" % float(bet))
            while preflop_action[count5][-1] == " " or re.match("[0-9]", preflop_action[count5][-1]) is not None or re.match("\.", preflop_action[count5][-1]) is not None:
                preflop_action[count5] = preflop_action[count5][:-1]
            preflop_action[count5] += " $" + bet
        count5 += 1
    count6 = 0
    for g in preflop_action:
        if g.find("Bet") != -1 and g.find("Entry Bet") == -1:
            if g[0] == "w":
                index1 = 8
            else:
                index1 = 11
            player_temp_id = g[:index1]
            preflop_action[count6] = preflop_action[count6][index1:]
            preflop_action[count6] = preflop_action[count6][4:]
            preflop_action[count6] = player_temp_id + ": bets " + preflop_action[count6]
            bet = preflop_action[count6][-7:]
            while bet[0] == " " or re.match("[a-z]", bet[0]) is not None:
                bet = bet[1:]
            bet = ("%.2f" % float(bet))
            while preflop_action[count6][-1] != "s":
                preflop_action[count6] = preflop_action[count6][:-1]
            while preflop_action[count6][-1] == " ":
                preflop_action[count6] = preflop_action[count6][:-1]
            preflop_action[count6] += " $" + bet
        count6 += 1
    count7 = 0
    for g in preflop_action:
        if g.find("Check") != -1:
            if g[0] == "w":
                index1 = 8
            else:
                index1 = 11
            player_temp_id = g[:index1]
            preflop_action[count7] = preflop_action[count7][index1:]
            preflop_action[count7] = preflop_action[count7][6:]
            preflop_action[count7] = player_temp_id + ": checks" + preflop_action[count7]
        count7 += 1
    count8 = 0
    for g in preflop_action:
        if g.find("Muck") != -1:
            if g[0] == "w":
                index1 = 8
            else:
                index1 = 11
            player_temp_id = g[:index1]
            preflop_action[count8] = preflop_action[count8][index1:]
            preflop_action[count8] = preflop_action[count8][5:]
            preflop_action[count8] = player_temp_id + ": doesn't show hand" + preflop_action[count8]
        count8 += 1
    flop_cards = []
    for g in preflop_action:
        if g[0:7] == "Showing":
            count3 += 2
        if g[0:4] == "Flop":
            flop_cards.append(g[-3:])
    if warioman_hand:
        flop_suits = suit_list[count3 + 2:count3 + 5]
    else:
        flop_suits = suit_list[count3:count3 + 3]
    flop = "["
    if flop_cards:
        for g in range(0, 3):
            try:
                flop += flop_cards[0][g] + flop_suits[g]
            except:
                pass
            if g < 2:
                flop += " "
    flop += "]"
    current_bet = big_blind
    count9 = 0
    for g in preflop_action:
        if g.find("Raise") != -1:
            if g[0] == "w":
                index1 = 8
            else:
                index1 = 11
            player_temp_id = g[:index1]
            preflop_action[count9] = preflop_action[count9][index1:]
            preflop_action[count9] = preflop_action[count9][6:]
            raise_temp = preflop_action[count9]
            preflop_action[count9] = player_temp_id + ": raises $" + raise_temp
            bet = preflop_action[count9][-5:]
            while bet[0] == " " or re.match("[a-z$]", bet[0]) is not None:
                bet = bet[1:]
            preflop_action[count9] = preflop_action[count9][:-4]
            while preflop_action[count9][-1] == " ":
                preflop_action[count9] = preflop_action[count9][:-1]
            preflop_action[count9] += current_bet + " to $" + bet
        if g.find("Raise") != -1 or g.find("bets") != -1:
            bet = g[-5:]
            while bet[0] == " " or re.match("[a-z$]", bet[0]) is not None:
                bet = bet[1:]
            bet = ("%.2f" % float(bet))
            current_bet = bet
        count9 += 1
    turn_cards = []
    for g in preflop_action:
        if g[0:7] == "Showing":
            count3 += 2
        if g[0:4] == "Turn":
            turn_cards.append(g[-1:])
    if warioman_hand:
        turn_suits = suit_list[count3 + 8:count3 + 9]
    else:
        turn_suits = suit_list[count3 + 6:count3 + 7]
    turn = "["
    if turn_cards:
        for g in range(0, 1):
            try:
                turn += turn_cards[0][g] + turn_suits[g]
            except:
                pass
    turn += "]"
    river_cards = []
    for g in preflop_action:
        if g[0:7] == "Showing":
            count3 += 2
        if g[0:5] == "River":
            river_cards.append(g[-1:])
    if warioman_hand:
        river_suits = suit_list[count3 + 12:count3 + 13]
    else:
        river_suits = suit_list[count3 + 10:count3 + 11]
    river = "["
    if river_cards:
        for g in range(0, 1):
            try:
                river += river_cards[0][g] + river_suits[g]
            except:
                pass
    river += "]"
    river1 = 0
    show_down = 0
    net_results = []
    pot1 = 0
    player_id_list3 = player_id_list.copy()
    street_pot = 0
    player_temp_id2 = " "
    player_temp_id3 = " "
    for g in range(len(player_id_list3)):
        player_id_list3[g] = [player_id_list3[g]]
        player_id_list3[g].append(0)
    preflop_only = 1
    uncalled_bet = " "
    bet2 = 0
    for t in action:
        if t.find("Bet") != -1 or t.find("Raise") != -1:
            if t.find("Entry Bet") != -1:
                continue
            if t[0] == "w":
                player_temp_id3 = "warioman"
            if t[:6] == "Player":
                player_temp_id3 = t[:11]
            uncalled_bet = t
            call = 0
        if t.find("Call") != -1:
            uncalled_bet = " "
            call = 1
    if uncalled_bet != " ":
        if uncalled_bet.find("Bet") != -1:
            bet2 = uncalled_bet[-6:]
            while bet2[0] == " " or re.match("[a-zA-Z$]", bet2[0]) is not None:
                bet2 = bet2[1:]
            uncalled_bet = "Uncalled bet ($" + "%.2f" % float(bet2) + ") returned to " + player_temp_id3 + "\n"
    if uncalled_bet != " ":
        if uncalled_bet.find("Raise") != -1:
            bet2 = uncalled_bet[-6:]
            while bet2[0] == " " or re.match("[a-zA-Z$]", bet2[0]) is not None:
                bet2 = bet2[1:]
            uncalled_bet = "Uncalled bet ($" + "%.2f" % float(bet2) + ") returned to " + player_temp_id3 + "\n"
    for t in action:
        if t.find("Flop") != -1 or t.find("Turn") != -1 or t.find("River") != -1:
            for g in player_id_list3:
                pot1 += float(g[1])
                # print("pot in loop = " + str(pot1))
            for h in range(len(player_id_list3)):
                # print(str(player_id_list3[h][1]) + " added to pot")
                player_id_list3[h][1] = 0
            preflop_only = 0
        if t.find("Call") != -1 or t.find("Bet") != -1 or t.find("Raise") != -1 or t.find("Blind") != -1:
            if t.find("Entry Bet") != -1:
                continue
            # print("true1")
            if t[0] == "w":
                player_temp_id2 = "warioman"
                # print("true2")
            if t[:6] == "Player":
                # print("true3")
                player_temp_id2 = t[:11]
            for x in range(len(player_id_list3)):
                if player_id_list3[x][0] == player_temp_id2:
                    # print("true4")
                    bet1 = t[-6:]
                    while bet1[0] == " " or re.match("[a-zA-Z$]", bet1[0]) is not None:
                        bet1 = bet1[1:]
                        # print("bet1 = ")
                        # print(bet1)
                    if t.find("Call") != -1:
                        player_id_list3[x][1] += float(bet1)
                    if t.find("Raise") != -1:
                        player_id_list3[x][1] = float(bet1)
                    if t.find("Bet") != -1:
                        player_id_list3[x][1] = float(bet1)
                    if t.find("Blind") != -1:
                        player_id_list3[x][1] = float(bet1)
    for g in player_id_list3:
        pot1 += float(g[1])
    for h in range(len(player_id_list3)):
        player_id_list3[h][1] = 0
    if preflop_only == 1 and bet2 == 0:
        bet2 = float(big_blind) - float(small_blind)

    pot1 -= float(bet2)


    for t in player_hand_results:
        net_results.append(t.split())
    results_str = " "
    net = 0
    results_printed = 0
    winnings = 0
    rake = pot1 * 0.05
    if rake > 1.50:
        rake = 1.50
    if preflop_only == 1:
        rake = 0
    winnings = pot1 - rake
    for t in net_results:
        if float(t[2]) > 0:
            temp = 0
            temp = "%.2f" % float(t[2])
            net = "%.2f" % float(t[2])
            results_str = t[0] + " collected $" + "%.2f" % winnings + " from pot\n"
    if results_str[0] == "w":
        winner = "warioman"
    else:
        winner = results_str[:11]
    board = flop + turn + river
    board = board.replace("][", " ")
    while board.find(" ]") != -1:
        board = board.replace(" ]", "]")
    for t in preflop_action:
        if t[:4] == "Turn":
            f.write("*** TURN *** " + flop + " " + turn + "\n")
        elif t[:5] == "River":
            f.write("*** RIVER *** " + flop + " " + turn + " " + river + "\n")
            river1 = 1
        elif t[:4] == "Flop":
            f.write("*** FLOP *** " + flop + "\n")
        elif river1 == 1 and t.find("Showing") != -1 and show_down != 1:
            f.write("*** SHOW DOWN *** \n")
            show_down = 1
        elif t.find("Showing") != -1 and show_down == 1:
            continue
        elif t.find("Has") != -1:
            continue
        elif t.find("More time") != -1:
            continue
        else:
            f.write(t + "\n")
    if uncalled_bet != " ":
        f.write(uncalled_bet)
    f.write(results_str)
    f.write("*** SUMMARY ***\n")
    f.write("Total Pot $" + "%.2f" % pot1 + " | Rake $" + "%.2f" % rake + "\n")
    if board != "[]":
        f.write("Board " + board + "\n")
    fold_street = "folded before the flop"
    fold_list = []
    for t in preflop_action:
        if t.find("Flop") != -1:
            fold_street = "folded on the flop"
        if t.find("Turn") != -1:
            fold_street = "folded on the turn"
        if t.find("River") != -1:
            fold_street = "folded on the river"
        if t.find("folds") != -1:
            if t[0] == "w":
                fold_list.append(t[:8] + " " + fold_street)
            else:
                fold_list.append(t[:11] + " " + fold_street)
    player_id_list2 = player_id_list
    folder_list = []
    for i in fold_list:
        if i[0] == "w":
            folder_list.append("warioman")
        else:
            folder_list.append(i[:11])
    winner_cards = ""
    count9 = 0
    for g in player_hand_results:
        if g[-3:] != "N/A":
            count9 += 5
    if warioman_hand:
        count9 += 2
    for t in preflop_action2:
        if t.find("Flop") != -1:
            count9 += 3
        if t.find("Turn") != -1:
            count9 += 4
        if t.find("River") != -1:
            count9 += 5
        if t.find("Showing") != -1 and (t[:8] != winner and t[:11] != winner):
            count9 += 2
        if t.find("Showing") != -1 and (t[:8] == winner or t[:11] == winner):
            winner_cards = t[-2:]
            break
    winner_suits = suit_list[count9: count9+2]
    winner_hand = ""
    try:
        if winner_cards != "":
            winner_hand = winner_cards[0] + winner_suits[0] + " " + winner_cards[1] + winner_suits[1]
    except:
        pass
    for t in range(0, len(player_id_list)):
        if player_id_list[t] == bb_player_id:
            summary_id = " (big blind)"
        elif player_id_list[t] == sb_player_id:
            summary_id = " (small blind)"
        elif t+1 == button_seat_number:
            summary_id = " (button)"
        else:
            summary_id = ""
        temp2 = ""
        if player_id_list[t][0] == "w":
            for g in fold_list:
                if g[0] == "w":
                    temp2 = " " + g[9:]
        elif player_id_list[t] == winner:
            f.write("Seat " + str(t+1) + ": " + winner + " shows [" + winner_hand + "] and won ($" + "%.2f" % winnings + ") with \n")
            continue
        elif player_id_list[t] != winner and player_id_list[t] not in folder_list:
            f.write("Seat " + str(t + 1) + ": " + player_id_list[t] + summary_id + " mucked\n")
            continue
        else:
            for g in fold_list:
                if g[:11] == player_id_list[t]:
                    temp2 = " " + g[12:]
        f.write("Seat " + str(t+1) + ": " + player_id_list[t] + summary_id + temp2 + "\n")
    f.write("\n")
    driver.find_element(By.XPATH, "//*[@id='profilePageView']/div/div/div[3]/div[2]/div/div[1]/div/button[3]").click()
    # shows processing speed in hands/sec
    print(("%.2f" % (count/float("%s" % (time.time() - start_time)))) + " Hands per Second")
    previous_hand_id = hand_id
    print()
f.close()
driver.quit()
