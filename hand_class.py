import hand_grabber
import sys


class Hand:

    def __init__(self):
        self.id = ""
        self.stake = ""
        self.table_id = ""
        self.date = ""
        self.time = ""
        self.action = []
        self.action_static = []
        self.preflop_action = []
        self.flop_action = []
        self.turn_action = []
        self.river_action = []
        self.showdown_action = []
        self.player_hand_results = []
        self.player_hand_results_static = []
        self.summary = []
        self.first_line = ""
        self.second_line = ""
        self.current_bet = 0
        self.small_blind = ""
        self.big_blind = ""
        self.small_blind_id = ""
        self.big_blind_id = ""
        self.pot = 0
        self.uncalled_bet = 0
        self.uncalled_bet_list = []
        self.fold_list = []
        self.suit_list = []
        self.user_hand = ""
        self.board = ""
        self.flop = ""
        self.turn = ""
        self.river = ""
        self.player_id_list = []
        self.pot_list = []
        self.waiting_list = []
        self.rake = ""
        self.winner_str = ""
        self.winner = ""
        self.button_id = ""
        self.allin_list = []

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def action_separator(self, action):
        street_count = 0
        for g in action:
            if g.find("More time") != -1:
                continue
            if g.find("Was dealt") != -1:
                continue
            if g.find("Small Blind") != -1:
                continue
            if g.find("Big Blind") != -1:
                continue
            if g.find("Waiting") != -1:
                continue
            if g.find("Decline Entry Bet") != -1:
                continue

            if g.find("Showing") != -1:
                self.showdown_action.append(g)
                continue
            if g.find("Has") != -1:
                self.showdown_action.append(g)
                continue

            if street_count == 0:
                if g.find("Flop") != -1:
                    street_count = 1
                    continue
                else:
                    self.preflop_action.append(g)
            if street_count == 1:
                if g.find("Turn") != -1:
                    street_count = 2
                    continue
                else:
                    self.flop_action.append(g)
            if street_count == 2:
                if g.find("River") != -1:
                    street_count = 3
                    continue
                else:
                    self.turn_action.append(g)
            if street_count == 3:
                self.river_action.append(g)

    def print_action(self):
        sys.stdout = open("C:\\Users\\Bjorn Jacobson\\PycharmProjects\\GP_Scraper\\GP_Scraper\\Output\\test.txt", "a")
        print(self.first_line)
        print(self.second_line)
        for g in self.player_hand_results:
            print(g)
        print("*** HOLE CARDS ***")
        for g in self.preflop_action:
            print(g)
        if self.flop_action:
            print("*** FLOP *** " + self.flop)
        for g in self.flop_action:
            print(g)
        if self.turn_action:
            print("*** TURN *** " + self.flop + " " + self.turn)
        for g in self.turn_action:
            print(g)
        if self.river_action:
            print("*** RIVER *** " + self.flop + " " + self.turn + " " + self.river)
        for g in self.river_action:
            print(g)
        print(self.winner_str)
        if self.showdown_action:
            print("*** SHOWDOWN ***")
        for g in self.showdown_action:
            print(g)
        print("*** SUMMARY ***")
        for g in self.summary:
            print(g)
        print()
        sys.stdout.close()
        return

    def format_results(self):
        for g in self.player_hand_results:
            for w in self.waiting_list:
                if g.find(w) != -1:
                    self.player_hand_results.remove(g)

        for g in range(0, len(self.player_hand_results)):
            self.player_hand_results[g] = self.player_hand_results[g].split()
            self.player_hand_results[g].pop(-1)
            self.player_hand_results[g].pop(-1)
            self.player_hand_results[g] = "Seat " + str(g+1) + ": " + self.player_hand_results[g][0] + \
                                          " ($%.2f" % float(self.player_hand_results[g][1]) + " in chips)"

    def raise_format_mini(self, a):
        for g in a:
            if g.find("bets") != -1 or g.find("raises") != -1:
                count = 0
                while g[-(count + 1)] != "$":
                    count += 1
                bet = float(g[-count:])
                if g.find("raises") != -1:
                    i = a.index(g)
                    a[i] = g[:-(count + 2)]
                    a[i] += " $" + "%.2f" % self.current_bet + " to $" + "%.2f" % bet
                self.current_bet = bet
        return a

    def raise_format(self):
        self.current_bet = float(self.big_blind)
        if self.preflop_action:
            self.preflop_action = self.raise_format_mini(self.preflop_action)
        if self.flop_action:
            self.flop_action = self.raise_format_mini(self.flop_action)
        if self.turn_action:
            self.turn_action = self.raise_format_mini(self.turn_action)
        if self.river_action:
            self.river_action = self.raise_format_mini(self.river_action)
        return

    def get_blinds(self):
        for g in self.action:
            if g.find("Small Blind") != -1:
                self.small_blind_id = g.split()[0]
                self.small_blind = "%.2f" % float(g.split()[-1])
            if g.find("Big Blind") != -1:
                self.big_blind_id = g.split()[0]
                self.big_blind = "%.2f" % float(g.split()[-1])
            if self.big_blind_id and self.big_blind:
                break
        return

    def blinds_output(self):
        if self.small_blind_id:
            self.player_hand_results.append(self.small_blind_id + ": posts small blind $" + self.small_blind)
        if self.big_blind_id:
            self.player_hand_results.append(self.big_blind_id + ": posts big blind $" + self.big_blind)

    def get_folds(self):
        fold_street = "folded before the flop"
        for t in self.action:
            if t.find("Flop") != -1:
                fold_street = "folded on the flop"
            if t.find("Turn") != -1:
                fold_street = "folded on the turn"
            if t.find("River") != -1:
                fold_street = "folded on the river"
            if t.find("folds") != -1:
                if t[0] == "w":
                    self.fold_list.append(t[:8] + " " + fold_street)
                else:
                    self.fold_list.append(t[:11] + " " + fold_street)
        return

    def get_user_hand(self):
        user_hand = "["
        s = self.suit_index("warioman Was dealt")
        user_suits = self.suit_list[s: s+2]
        for g in self.action_static:
            if g.find("warioman Was dealt") != -1:
                user_cards = g[-2:]
        for b in range(0, 2):
            user_hand += user_cards[b] + user_suits[b] + " "
        user_hand = user_hand[:-1]
        user_hand += "]"
        self.user_hand = user_hand
        self.preflop_action.insert(0, "Dealt to warioman " + self.user_hand)
        return

    def get_flop(self):
        flop = "["
        s = self.suit_index("Flop")
        flop_suits = self.suit_list[s: s+3]
        for g in self.action_static:
            if g.find("Flop") != -1:
                flop_cards = g[-3:]
        if flop_cards:
            for b in range(0, 3):
                flop += flop_cards[b] + flop_suits[b] + " "
            flop = flop[:-1]
            flop += "]"
            self.flop = flop
        return

    def get_turn(self):
        turn = "["
        s = self.suit_index("Turn")
        turn_suits = self.suit_list[s + 3: s + 4]
        for g in self.action_static:
            if g.find("Turn") != -1:
                turn_cards = g[-1:]
        if turn_cards:
            for b in range(0, 1):
                turn += turn_cards[b] + turn_suits[b] + " "
            turn = turn[:-1]
            turn += "]"
            self.turn = turn
        return

    def get_river(self):
        river = "["
        s = self.suit_index("River")
        river_suits = self.suit_list[s + 4: s + 5]
        for g in self.action_static:
            if g.find("River") != -1:
                river_cards = g[-1:]
        if river_cards:
            for b in range(0, 1):
                river += river_cards[b] + river_suits[b] + " "
            river = river[:-1]
            river += "]"
            self.river = river
        return

    def suit_index(self, a):
        count = 0
        for w in self.player_hand_results_static:
            if w.find(a) == -1:
                if w[-3:] != "N/A":
                    count += 5
            else:
                break
        for b in self.action_static:
            if b.find(a) == -1:
                if b.find("warioman Was dealt") != -1:
                    count += 2
                if b.find("Showing") != -1:
                    count += 2
                if b.find("Flop") != -1:
                    count += 3
                if b.find("Turn") != -1:
                    count += 4
                if b.find("River") != -1:
                    count += 5
                if b.find("Has") != -1:
                    count += 5
            else:
                break
        return count

    def get_pot(self):
        self.pot_list = self.player_id_list.copy()
        if self.small_blind_id:
            pot = 2*float(self.small_blind)
        else:
            pot = 0
        if self.small_blind and self.big_blind:
            uncalled_bet = float(self.big_blind) - float(self.small_blind)
        else:
            uncalled_bet = 0

        for g in range(0, len(self.pot_list)):
            self.pot_list[g] = [self.pot_list[g]]
            self.pot_list[g].append(0)
            self.pot_list[g].append(0)

        for g in range(0, len(self.pot_list)):
            for m in range(0, len(self.player_hand_results_static)):
                if self.pot_list[g][0] == self.player_hand_results_static[m].split()[0]:
                    self.pot_list[g].append(round(float(self.player_hand_results_static[m].split()[1]), 2))

        for g in range(0, len(self.pot_list)):
            if self.pot_list[g][0] == self.small_blind_id:
                self.pot_list[g][1] = float(self.small_blind)
            if self.pot_list[g][0] == self.big_blind_id:
                self.pot_list[g][1] = float(self.big_blind)

        count2 = 0
        uncalled = True
        for p in [self.preflop_action, self.flop_action, self.turn_action, self.river_action]:
            f = ""
            for g in p:
                if g.find("raises") != -1:
                    count = 0
                    while g[-(count + 1)] != "$":
                        count += 1
                    bet = float(g[-count:])
                    f = g.split(":")[0]
                    uncalled = True
                    for x in range(0, len(self.pot_list)):
                        if self.pot_list[x][0] == f:
                            self.pot_list[x][1] = bet

                if g.find("bets") != -1:
                    count = 0
                    while g[-(count + 1)] != "$":
                        count += 1
                    bet = float(g[-count:])
                    f = g.split(":")[0]
                    uncalled = True
                    for x in range(0, len(self.pot_list)):
                        if self.pot_list[x][0] == f:
                            self.pot_list[x][1] = bet

                if g.find("calls") != -1:
                    count = 0
                    while g[-(count + 1)] != "$":
                        count += 1
                    bet = float(g[-count:])
                    f = g.split(":")[0]
                    uncalled = False
                    for x in range(0, len(self.pot_list)):
                        if self.pot_list[x][0] == f:
                            self.pot_list[x][1] += bet

            call_list = []
            if self.big_blind and p == self.preflop_action:
                biggest_bet = self.big_blind
            else:
                biggest_bet = 0
            for z in range(0, len(self.pot_list)):
                call_list.append(self.pot_list[z][1])
            call_list.sort(reverse=True)
            biggest_bet = call_list[0]
            call_list = call_list[1:]
            if call_list[0] == biggest_bet:
                uncalled_bet = 0
            else:
                uncalled_bet = biggest_bet - call_list[0]

            street = ""
            if count2 == 0:
                street = "preflop"
            if count2 == 1:
                street = "flop"
            if count2 == 2:
                street = "turn"
            if count2 == 3:
                street = "river"

            for z in range(0, len(self.pot_list)):
                self.pot += self.pot_list[z][1]
                self.pot_list[z][2] += self.pot_list[z][1]

            for z in range(0, len(self.pot_list)):
                if round(self.pot_list[z][2], 2) == round(self.pot_list[z][3], 2):
                    already_allin = False
                    if self.allin_list:
                        for h in self.allin_list:
                            if self.pot_list[z][0] == h[0]:
                                already_allin = True
                    if already_allin:
                        break
                    else:
                        self.allin_list.append([self.pot_list[z][0], street])

            for z in range(0, len(self.pot_list)):
                self.pot_list[z][1] = 0

            self.uncalled_bet = uncalled_bet
            self.pot -= self.uncalled_bet

            if self.uncalled_bet < .01:
                self.uncalled_bet = 0

            if self.uncalled_bet != 0 and uncalled:
                self.uncalled_bet_list.append(street)
                if f == "":
                    f = self.big_blind_id
                self.uncalled_bet_list.append(f)
                self.uncalled_bet_list.append(self.uncalled_bet)

            count2 += 1
        return

    def get_player_ids(self):
        for g in range(0, len(self.player_hand_results_static)):
            f = self.player_hand_results_static[g].split()[0]
            self.player_id_list.append(f)
        return

    def get_waiters(self):
        for g in self.action_static:
            if g.find("Waiting") != -1:
                self.waiting_list.append(g.split()[0])
        return

    def create_summary(self):
        self.summary.append("Pot $" + "%.2f" % self.pot + " | Rake $" + "%.2f" % self.rake)

        count = 1
        for t in self.player_id_list:
            k = False
            if t == self.small_blind_id:
                sum_id = " (small blind)"
            elif t == self.big_blind_id:
                sum_id = " (big blind)"
            elif t == self.button_id:
                sum_id = " (button blind)"
            else:
                sum_id = ""

            if t == self.winner:
                self.summary.append("Seat " + str(count) + ": " + self.winner + sum_id + " shows " + "and won $" +
                                    "%.2f" % (float(self.pot)-float(self.rake)) + " with")
                count += 1
                continue
            for p in self.fold_list:
                if p.split()[0] == t:
                    self.summary.append("Seat " + str(count) + ": " + p.split()[0] + sum_id + " " +
                                        p[len(p.split()[0])+1:])
                    k = True
                    count += 1
                    break
            if k:
                continue
            else:
                self.summary.append("Seat " + str(count) + ": " + t + sum_id + " mucked")
            count += 1
        return

    def add_uncalled_bets(self):
        g = self.uncalled_bet_list.copy()
        while g:
            if g[0] == "preflop":
                self.preflop_action.append("Uncalled bet ($" + str("%.2f" % float(g[2])) + ") returned to " + g[1])
            elif g[0] == "flop":
                self.flop_action.append("Uncalled bet ($" + str("%.2f" % float(g[2])) + ") returned to " + g[1])
            elif g[0] == "turn":
                self.turn_action.append("Uncalled bet ($" + str("%.2f" % float(g[2])) + ") returned to " + g[1])
            elif g[0] == "river":
                self.river_action.append("Uncalled bet ($" + str("%.2f" % float(g[2])) + ") returned to " + g[1])
            else:
                break
            if len(g) > 3:
                g = g[3:]
            else:
                break
        return

    def collected_pot(self):
        winner = ""
        didnt_fold = self.player_id_list.copy()
        for g in self.player_id_list:
            for z in range(0, len(self.fold_list)):
                if g == self.fold_list[z].split()[0]:
                    didnt_fold.remove(g)
        if self.waiting_list:
            for g in self.player_id_list:
                for z in self.waiting_list:
                    if g == z:
                        didnt_fold.remove(g)
        for g in self.player_hand_results_static:
            if round(float(g.split()[2]), 2) > 0:
                winner = g.split()[0]
        if winner:
            self.winner = winner
            self.winner_str = winner + " collected $" + "%.2f" % (
                        float(self.pot) - float(self.rake)) + " from the the pot"
        if winner == "":
            for g in range(0, len(didnt_fold)):
                self.winner_str += didnt_fold[g] + " collected $" + "%.2f" % (
                            float(self.pot)/len(didnt_fold) - float(self.rake)/len(didnt_fold)) + " from the the pot"
                if g != len(didnt_fold)-1:
                    self.winner_str += "\n"
        if len(didnt_fold) == 1 and didnt_fold[0] == self.big_blind_id:
            self.winner = self.big_blind_id
        print("didnt fold")
        print(didnt_fold)
        return

    def get_rake(self):
        rake = self.pot * .05
        if rake > 1.50:
            rake = 1.50
        preflop_only = True
        for g in self.action:
            if g.find("Flop") != -1:
                preflop_only = False
        if preflop_only:
            rake = 0
        self.rake = rake
        return

    def print_action2(self):
        print(self.first_line)
        print(self.second_line)
        for g in self.player_hand_results:
            print(g)
        print("*** HOLE CARDS ***")
        for g in self.preflop_action:
            print(g)
        if self.flop_action:
            print("*** FLOP *** " + self.flop)
        for g in self.flop_action:
            print(g)
        if self.turn_action:
            print("*** TURN *** " + self.flop + " " + self.turn)
        for g in self.turn_action:
            print(g)
        if self.river_action:
            print("*** RIVER *** " + self.flop + " " + self.turn + " " + self.river)
        for g in self.river_action:
            print(g)
        print(self.winner_str)
        if self.showdown_action:
            print("*** SHOWDOWN ***")
        for g in self.showdown_action:
            print(g)
        print("*** SUMMARY ***")
        for g in self.summary:
            print(g)
        return

    def is_allin(self):
        print(self.allin_list)
        all_in_index = 0
        p = len(self.allin_list)
        preflop_reverse = self.preflop_action.copy()
        preflop_reverse.reverse()
        flop_reverse = self.flop_action.copy()
        flop_reverse.reverse()
        turn_reverse = self.turn_action.copy()
        turn_reverse.reverse()
        river_reverse = self.river_action.copy()
        river_reverse.reverse()
        for g in range(0, p):
            if self.allin_list[g][1] == "preflop":
                for x in range(len(self.preflop_action)):
                    if preflop_reverse[x].split(":")[0] == self.allin_list[g][0]:
                        all_in_index = (-1*x)-1
                        break
            if all_in_index:
                self.preflop_action[all_in_index] += " and is all-in"
                all_in_index = 0
        for g in range(0, p):
            if self.allin_list[g][1] == "flop":
                for x in range(len(self.flop_action)):
                    if flop_reverse[x].split(":")[0] == self.allin_list[g][0]:
                        all_in_index = (-1*x)-1
                        break
            if all_in_index:
                self.flop_action[all_in_index] += " and is all-in"
                all_in_index = 0
        for g in range(0, p):
            if self.allin_list[g][1] == "turn":
                for x in range(len(self.turn_action)):
                    if turn_reverse[x].split(":")[0] == self.allin_list[g][0]:
                        all_in_index = (-1*x)-1
                        break
            if all_in_index:
                self.turn_action[all_in_index] += " and is all-in"
                all_in_index = 0
        for g in range(0, p):
            if self.allin_list[g][1] == "river":
                for x in range(len(self.river_action)):
                    if river_reverse[x].split(":")[0] == self.allin_list[g][0]:
                        all_in_index = (-1*x)-1
                        break
            if all_in_index:
                self.river_action[all_in_index] += " and is all-in"
                all_in_index = 0

# git hub upload test