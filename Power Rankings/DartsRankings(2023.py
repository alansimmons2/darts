import csv
import os
import keyboard
import time

class Match:
    def __init__(self, x, y, z, a, b):
        self.p1 = x
        self.p2 = y
        self.r = z
        self.l1 = a
        self.l2 = b

    def getResult(self):
        if self.l1 != -1:
            return str(self.l1) + "-" + str(self.l2)
        else:
            return self.r

class Tournament:
    def __init__(self, num, title):
        self.id = num
        self.name = title
        self.matches = []

current = 0
tournaments = []

def getTournament(t):
    for tournament in tournaments:
        if tournament.id == t:
            return tournament

def save():
    with open('history.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for t in tournaments:
            writer.writerow(["t", t.id, t.name])

        for t in tournaments:
            for m in t.matches:
                writer.writerow(["m", t.id, m.p1, m.p2, m.r, m.l1, m.l2])

def tadd():
    num = int(input("ID >"))
    title = str(input("Name >"))

    tournament = Tournament(num, title)
    tournaments.append(tournament)
    save()

def tlist():
    for tournament in tournaments:
        print(tournament.id, tournament.name)
    wait_escape()

def tchange():
    global current
    t = int(input("ID >"))
    confirm = str(input(getTournament(t).name + "? >"))
    if confirm == "yes":
        current = t 
    
def madd():
    loop = True
    while loop:
        print("Type 'exit' to return to menu")
        x = str(input("Player 1 >"))
        if "exit" in x:
            loop = False
            break
        y = str(input("Player 2 >"))
        if "exit" in y:
            loop = False
            break
        else:
            z = str(input(x + " outcome > "))
            match = 0
            if z in ["w", "d", "l"]:
                match = Match(x, y, z, -1, -1)
            else:
                b = int(input(y + " legs > "))
                z = int(z)
                r = ""
                if z > b:
                    r = "w"
                elif z == b:
                    r = "d"
                else:
                    r = "l"
                
                match = Match(x, y, r, z, b)
            getTournament(current).matches.append(match)
    save()

def mlist():
    print(getTournament(current).name)
    for match in getTournament(current).matches:
            print(match.p1,"vs",match.p2,"(",match.getResult(),")")
    wait_escape()

players = []
rankings = []
historic = []

def updateRanking(name, change):
    for i in range(len(rankings)):
        entry = rankings[i]
        if entry[0] == name:
            rankings[i] = (entry[0], round(entry[1] + change))
            break

def getRanking(name):
    for entry in rankings:
        if entry[0] == name:
            return entry[1]

green = '\033[92m'
end = '\033[0m'

comparison = 0

latest = []

def printRankings():
    global latest
    latest = []
    data = sorted(rankings, key=lambda tup: tup[1], reverse=True)
    recent = []
    for i in range(10):
        t = getTournament(len(tournaments) - 1 - i)
        if len(tournaments) - 1 - i >= 0:
            for m in t.matches:
                if m.p1 not in recent:
                    recent.append(m.p1)
                if m.p2 not in recent:
                    recent.append(m.p2)
    data = [item for item in data if item[0] in recent]
    old_data = sorted(historic[comparison][1], key=lambda tup: tup[1], reverse=True)
    #print(old_data)
    for i in range(len(data)):
        item = data[i]
        change = -i
        rc = 0
        found = False
        for j in range(len(old_data)):
            if old_data[j][0] == item[0]:
                change += j
                found = True
                rc = item[1] - old_data[j][1]
                break
        if found:
            change = "[+" + str(change) + "] " if change > 0 else "[" + str(change) + "] " if change < 0 else "     "
        else:
            change = "[NEW]"
        rc = "(+" + str(rc) + ")" if rc > 0 else "(" + str(rc) + ")" if rc < 0 else "    "

        print(change, i+1, item[0], item[1], rc)
        latest.append((change, i+1, item[0], item[1], rc))
    wait_escape()

def getScore(result):
    if result == "w":
        return 1
    elif result == "d":
        return 0.5
    else:
        return 0

K = 32
ENTRY = 1500

def getMedian():
    data = sorted(rankings, key=lambda tup: tup[1], reverse=True)
    return data[int(len(data) / 2)][1]

def run():
    global comparison
    players.clear()
    rankings.clear()

    ids = []
    for tournament in tournaments:
        ids.append(tournament.id)

    sorted_ids = sorted(ids)
    
    for i in range(len(tournaments)):
        tournament = getTournament(sorted_ids[i])
        tplayers = []
        for m in tournament.matches:
            if m.p1 not in tplayers:
                tplayers.append(m.p1)
                
            if m.p2 not in tplayers:
                tplayers.append(m.p2)
                
            if m.p1 not in players:
                players.append(m.p1)
                rankings.append((m.p1, ENTRY if tournament.id == 0 else getMedian()))

            if m.p2 not in players:
                players.append(m.p2)
                rankings.append((m.p2, ENTRY if tournament.id == 0 else getMedian()))
        updates = []
        for player in players:
            if player not in tplayers and "Week" not in tournament.name and "Warwick A v B" not in tournament.name and "Ladder" not in tournament.name:
                updates.append((player, -15))
            else:
                exp = 0
                actual = 0
                played = 0
                for match in tournament.matches:
                    if match.p1 == player:
                        qa = 10**(getRanking(match.p1)/400)
                        qb = 10**(getRanking(match.p2)/400)
                        exp += qa/(qa + qb)
                        actual += getScore(match.r)
                        played += 1
                    elif match.p2 == player:
                        qa = 10**(getRanking(match.p2)/400)
                        qb = 10**(getRanking(match.p1)/400)
                        exp += qa/(qa + qb)
                        actual += (1 - getScore(match.r))
                        played += 1
                updates.append((player, K*(actual - exp)))

        for update in updates:
            updateRanking(update[0], update[1])
        historic.append((tournament.id, rankings.copy()))
    comparison = len(tournaments) - 2

def comp():
    global comparison
    t = int(input("ID >"))
    confirm = str(input(getTournament(t).name + "? >"))
    if confirm == "yes":
        comparison = t

def h2h():
    p1 = input("Player 1 > ")
    p2 = input("Player 2 > ")

    w = 0
    d = 0
    l = 0

    for t in tournaments:
        for m in t.matches:
            if m.p1 == p1 and m.p2 == p2:
                if m.r == "w":
                    w += 1
                elif m.r == "d":
                    d += 1
                else:
                    l += 1
            elif m.p1 == p2 and m.p2 == p1:
                if m.r == "w":
                    l += 1
                elif m.r == "d":
                    d += 1
                else:
                    w += 1
    print(p1,"vs",p2,"W:",w,"D:",d,"L:",l)
    wait_escape()

def record():
    p1 = input("Player 1 > ")
    params = input("Params > ")

    w = 0
    d = 0
    l = 0

    for t in tournaments:
        for m in t.matches:
            if m.p1 == p1:
                if m.r == "w":
                    w += 1
                    if "w" in params:
                        print(m.p1,"vs",m.p2,"(",m.getResult(),")")
                elif m.r == "d":
                    d += 1
                    if "d" in params:
                        print(m.p1,"vs",m.p2,"(",m.getResult(),")")
                else:
                    l += 1
                    if "l" in params:
                        print(m.p1,"vs",m.p2,"(",m.getResult(),")")
            elif m.p2 == p1:
                if m.r == "w":
                    l += 1
                    if "l" in params:
                        print(m.p1,"vs",m.p2,"(",m.getResult(),")")
                elif m.r == "d":
                    d += 1
                    if "d" in params:
                        print(m.p1,"vs",m.p2,"(",m.getResult(),")")
                else:
                    w += 1
                    if "w" in params:
                        print(m.p1,"vs",m.p2,"(",m.getResult(),")")
    print(p1,"W:",w,"D:",d,"L:",l)
    wait_escape()

def rec(player, stat):
    p = 0
    count = 0
    for t in tournaments:
        for m in t.matches:
            if m.p1 == player:
                p += 1
                if m.r == stat:
                    count += 1
            elif m.p2 == player:
                p += 1
                if stat == "w" and m.r == "l":
                    count += 1
                elif stat == "d" and m.r == "d":
                    count += 1
                elif stat == "l" and m.r == "w":
                    count += 1

    return p if stat == "p" else count

def stats():
    print("# Tournaments:", len(tournaments))

    mc, lc, mx, _ = fix_counts()

    print("# Matches:", mc)
    print("# Legs:", lc)
    print("# Most Played Fixture:", mx[0], "vs", mx[1], "-", mx[2])
    print("# Players:", len(players))
    wait_escape()

def fix_counts():
    mc, lc = 0, 0
    counts = []
    for t in tournaments:
        mc += len(t.matches)
        for m in t.matches:
            found = False
            for i, fix in enumerate(counts):
                if (fix[0] == m.p1 and fix[1] == m.p2) or (fix[0] == m.p2 and fix[1] == m.p1):
                    counts[i] = (fix[0], fix[1], fix[2] + 1)
                    found = True
                    break

            if found == False:
                counts.append((m.p1, m.p2, 1))
            
            if m.l1 != -1:
                lc += (m.l1 + m.l2)
    
    mx = ("", "", 0)

    for fix in counts:
        if fix[2] > mx[2]:
            mx = fix
    counts = sorted(counts, key=lambda tup: tup[2], reverse=False) 
    return mc, lc, mx, counts

def show_fix_counts():
    _, _, _, counts = fix_counts()
    for fix in counts:
        print(fix[0], "vs", fix[1], "-", fix[2])
    wait_escape()

def list_players():
    for index, player in enumerate(players):
        print(str(index + 1) + ": " + player)
    wait_escape()

def export():
    path = str(input("File Name >"))
    confirm = str(input("Write to " + path + ".csv? > "))
    if confirm == "yes":
        printRankings()
        with open(path + ".csv", 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(["Ranking", "Name", "Score", "Played", "Won", "Drawn", "Lost"])
            for entry in latest:
                out = [entry[1], entry[2], entry[3], rec(entry[2], "p"), rec(entry[2], "w"), rec(entry[2], "d"), rec(entry[2], "l")]
                writer.writerow(out)

try:
    with open('history.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            if row[0] == "t":
                tournaments.append(Tournament(int(row[1]), row[2]))
            elif row[0] == "m":
                getTournament(int(row[1])).matches.append(Match(row[2], row[3], row[4], int(row[5]), int(row[6])))
except:
    print("No history found")

new_menu = True

def draw_items(index, items):
    for i in range(len(items)):
        print(("-> " if i == index else "   ") + items[i][0])

def draw_update(index, items, draw):
    os.system('cls' if os.name == 'nt' else 'clear')
    draw()
    draw_items(index, items)
    if draw != draw_menu:
        print("\nPress ESC to return")
        

def menu_loop(index, items, draw):
    draw_update(index, items, draw)
    while True:
        if keyboard.is_pressed('up'):
            if index > 0:
                index -= 1
                draw_update(index, items, draw)
        elif keyboard.is_pressed('down'):
            if index < len(items) - 1:
                index += 1
                draw_update(index, items, draw)
        elif keyboard.is_pressed('right'):
            time.sleep(0.5)
            os.system('cls' if os.name == 'nt' else 'clear')
            items[index][1]()
            draw_update(index, items, draw)
        elif draw != draw_menu and keyboard.is_pressed('ESC'):
            time.sleep(1)
            break

def wait_escape():
    print("\nPress ESC to return")
    while True:
        if keyboard.is_pressed('ESC'):
            break

def draw_wip():
    print("WIP")

def wip():
    menu_loop(0, [], draw_wip)

players_index = 0

players_items = [
    ["List Players", list_players],
    ["View Player's Record", record],
    ["Head To Head", h2h]
]

def draw_players():
    print("PLAYERS MENU")
    print()

def players_loop():
    global players_index, players_items
    menu_loop(players_index, players_items, draw_players)

tournament_edit_index = 0
tournament_edit_items = [
    ["List Matches", mlist],
    ["Add Match", madd]
]

def draw_tournament_edit():
    print("TOURNAMENT EDIT MENU")
    print()

tournaments_list_index = 0

def tournament_edit_loop():
    global tournaments_list_index, tournaments, current, tournament_edit_index, tournament_edit_items
    current = tournaments[tournaments_list_index].id
    menu_loop(tournament_edit_index, tournament_edit_items, draw_tournament_edit)

tournaments_list_items = []

def draw_tournaments_list():
    print("TOURNAMENTS LIST MENU")
    print()

def tournaments_list_loop():
    global tournaments_list_index, tournaments_list_items
    tournaments_list_index = len(tournaments) - 1
    tournaments_list_items = []
    for tournament in tournaments:
        tournaments_list_items.append([str(tournament.id) + ": " + tournament.name, tournament_edit_loop])
    menu_loop(tournaments_list_index, tournaments_list_items, draw_tournaments_list)

tournaments_index = 0

tournaments_items = [
    ["List Tournaments", tlist],
    ["Add Tournament", tadd],
    ["Edit Tournament", tournaments_list_loop]
]

def draw_tournaments():
    print("TOURNAMENTS MENU")
    print()

def tournaments_loop():
    global tournaments_index, tournaments_items
    menu_loop(tournaments_index, tournaments_items, draw_tournaments)    

rankings_index = 0

rankings_items = [
    ["Show Rankings", printRankings],
    ["Change Comparison Point", comp],
    ["Export Rankings", export]
]

def draw_rankings():
    print("RANKINGS MENU")
    print()

def rankings_loop():
    global rankings_index, rankings_items
    run()
    menu_loop(rankings_index, rankings_items, draw_rankings)

stats_index = 0

stats_items = [
    ["View Overall Statistics", stats],
    ["View Fixture Counts", show_fix_counts]
]

def draw_stats():
    print("STATISTICS MENU")
    print()

def stats_loop():
    global stats_index, stats_items
    menu_loop(stats_index, stats_items, draw_stats)

def draw_menu():
    print("/=======================\\")
    print("| Darts Rankings System |")
    print("|-----------------------|")
    print("| By Kyle Mandell, 2022 |")
    print("\\=======================/")
    print("This software should not be considered stable. You should regularly back-up history.csv to avoid data loss.")
    print('''Copyright 2022 Kyle Mandell

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.''')
    print("By using this software, you confirm agreement with the above terms.")
    print()
    print("Use UP and DOWN arrows to navigate menu items. Use RIGHT arrow to select.")
    print()
      

main_menu_index = 0
main_menu_items = [
    ["Players", players_loop],
    ["Tournaments", tournaments_loop],
    ["Rankings", rankings_loop],
    ["Statistics", stats_loop]
]

def main_menu_loop():
    global main_menu_index, main_menu_items
    menu_loop(main_menu_index, main_menu_items, draw_menu)

held = False
if new_menu:
    run()
    main_menu_loop()
else:
    while True:
        menu = input("\n> ")
        if menu == "tadd":
            tadd()
        elif menu == "tlist":
            tlist()
        elif menu == "tchange":
            tchange()
        elif menu == "madd":
            madd()
        elif menu == "mlist":
            mlist()
        elif menu == "comp":
            comp()
            printRankings()
        elif menu == "h2h":
            h2h()
        elif menu == "record":
            record()
        elif menu == "save":
            try:
                save()
            except:
                print("History file open already")
        elif menu == "export":
            try:
                export()
            except:
                print("Results file open already")
        elif menu == "run":
            run()
            printRankings()
        elif menu == "stats":
            stats()
