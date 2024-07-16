from config import colors, itemlist
from graphics import *
import time
import random
import numpy as np


# a Graphwin subclass to create buttons
class ButWin(GraphWin):
    def __init__(self, *args, **kwargs):
        self.buttons = {}
        super().__init__(*args, **kwargs)

    def createtxt(self, pt, text, color="white", size=15, draw=True) -> Text:
        t = Text(pt, text)
        t.setFill(color)
        t.setSize(size)
        t.setFace("courier")
        t.setStyle("bold")
        if draw:
            t.draw(self)
        return t

    def createpoly(self, *args):
        p = Polygon(*args)
        p.setFill('#666666')
        p.setOutline('white')
        p.draw(self)

    def createbut(self, p1: Point, p2: Point, action: str, text='', color='#ede0c5', heavyshade=True) -> Rectangle:
        shade = Rectangle(Point(p1.x+3, p1.y+3), Point(p2.x+3, p2.y+3))
        shade.setOutline('grey' if heavyshade else '#bfbfbf')
        shade.setFill("grey" if heavyshade else '#bfbfbf')
        shade.draw(self)

        rect = Rectangle(p1, p2)
        rect.setOutline("#6e4910")
        rect.setFill(color)
        rect.draw(self)
        self.buttons[(p1, p2)] = action

        if text:
            self.createtxt(Point((p1.x + p2.x) / 2, (p1.y + p2.y) / 2), text, color='#b57719', size=11)

        return rect

    def checkButtonClick(self, click):
        for k, v in self.buttons.items():
            if k[0].x < click.x < k[1].x and k[0].y < click.y < k[1].y:
                eval(v)


class Tile(Rectangle):
    def __init__(self, *args, v=0, win, textloc, nocolor=False, **kwargs):
        self.nocolor = nocolor
        self.value = v
        self.win = win
        tx, ty = textloc
        self.numdisplay = win.createtxt(Point(tx, ty), color='#403837', text=v if int(v) > 0 else '', draw=False)
        super().__init__(*args, **kwargs)

    def display(self):
        self.setFill(colors.get(self.value) if not self.nocolor else "#cdc1b4")
        self.draw(self.win)
        self.numdisplay.draw(self.win)

    def changev(self, v):
        self.value = v
        self.numdisplay.setText(v if v != 0 and type(v) == int else '')
        self.setFill(colors.get(v))

    def bmove(self, dx, dy):
        self.move(dx, dy)
        self.numdisplay.move(dx, dy)


class Board:
    def __init__(self):
        self.bdis = 5       # box distance
        self.offsetx = 55
        self.offsety = 130
        self.bsize = 70     # box size

    def createBGGrid(self, win=None) -> None:
        for r in range(4):
            for c in range(4):
                disx, disy = self.offsetx + c * (self.bsize + self.bdis), self.offsety + r * (self.bsize + self.bdis)
                tile = Tile(Point(disx, disy), Point(disx + self.bsize, disy + self.bsize), win=win,
                            textloc=(disx+self.bsize/2, disy+self.bsize/2), nocolor=True)
                tile.display()

    def createGrid(self, win=None) -> list:
        grid = []
        for r in range(4):
            row = []
            for c in range(4):
                disx, disy = self.offsetx + c * (self.bsize + self.bdis), self.offsety + r * (self.bsize + self.bdis)
                tile = Tile(Point(disx, disy), Point(disx + self.bsize, disy + self.bsize), win=win,
                            textloc=(disx+self.bsize/2, disy+self.bsize/2))
                tile.display()
                row.append(tile)
            grid.append(row)

        for i in [4, 2]:
            grid[random.randint(0, 3)][random.randint(0, 3)].changev(i)

        return grid


# item logic, as there are only so few im not making subclasses
class Item:
    def __init__(self, win, itemID: int, position: Point):
        self.icon = [(e[0].clone(), e[1]) for e in itemlist[itemID][1]]
        self.position = position
        self.name = itemlist[itemID][0]
        self.win = win

    def draw(self) -> None:
        for e in self.icon:
            poly, color = e
            poly.setFill(color)
            if type(poly) == Text:
                poly.setFace('courier')
                poly.setStyle('bold')
                poly.setSize(22)

            poly.move(self.position.x, self.position.y)
            poly.draw(self.win)

    def undraw(self) -> None:
        for e in self.icon:
            e[0].undraw()

    def blink(self, expand=True):
        cir = Circle(self.position, 30)
        r = cir.radius if expand else cir.radius * 2.1

        for i in range(5):
            cir = Circle(self.position, r * (1 + (i * 0.1 if expand else -i * 0.1)))
            cir.setOutline("#d4be81" if expand else "#94865f")
            cir.setWidth(5)
            cir.draw(self.win)
            time.sleep(0.01)
            cir.undraw()


# handles logic, computation and game
class GameManager:
    def __init__(self, win):
        self.win = win
        self.score = 0
        self.items = [None, None, None]
        self.board = Board()
        self.board.createBGGrid(win)
        self.grid = self.board.createGrid(win)
        self.logging = Logging()

        # animation, cart is a collector that executed all at once
        self.animcart = []
        #items
        self.itemslot_defaulttxt = 'item slots:'
        self.genblocker = 0

    # input: grid -> list of values, change grid, (and play action)
    def move(self, grid, transpose, rightToLeft) -> list:
        fgrid = []
        faction = []
        grid = np.transpose(grid).tolist() if transpose else grid
        for fi, f in enumerate(grid):
            if rightToLeft:
                f.reverse()

            actions = []
            lastempty = len(f) - 1
            v = len(f) - 1

            for ri, e in enumerate(reversed(f)):
                i = len(f) - ri - 1

                if e == 0 or i > v:
                    continue

                else:  # if the next one is the same as current
                    if i != lastempty:
                        actions.append((i, lastempty))

                    recur = 1
                    v = i - recur

                    while i - recur >= 0:  # start a recursion
                        checking = f[i - recur]

                        if checking == 0:
                            recur += 1
                        elif checking == e:  # if we find same number, append to action
                            actions.append((i - recur, lastempty))
                            lastempty -= 1
                            v = i - recur - 1  # gas station problem, start from where recursion ends
                            break
                        else:
                            lastempty -= 1
                            break

            final = f.copy()
            for a in actions:
                final[a[1]] += f[a[0]]
                final[a[0]] -= f[a[0]]
                # score increase
                faction.append(((fi, a[0]), abs(a[0]-a[1])))

            final.reverse() if rightToLeft else ''

            fgrid.append(final)

        fgrid = np.transpose(fgrid).tolist() if transpose else list(fgrid)

        for a in faction:

            # down animation
            if transpose and not rightToLeft:
                c, r = a[0]
            else:
                r, c = a[0]
            distance = a[1]

            # up animation
            if transpose and rightToLeft:
                c, r = a[0]
                c = 3-c
                r = 3-r

            self.animcart.append((self.grid[r][3-c if rightToLeft else c], distance))

        return fgrid

    def genRandom(self):
        pool = []
        for r in self.grid:
            for c in r:
                if c.value == 0:
                    pool.append(c)
        if len(pool) == 0:
            return

        tile = random.choice(pool)
        v = random.choice([2, 2, 4])

        # animation
        tile.changev("1")
        time.sleep(0.1)
        tile.changev("2")
        time.sleep(0.1)
        tile.changev(v)

        self.score += v
        scoretxt.setText(str(self.score))

    def getdir(self, dir):
        valuegrid = [[c.value for c in r] for r in self.grid]
        fgrid = []

        if dir == "w":
            fgrid = self.move(valuegrid, True, True)
        elif dir == "s":
            fgrid = self.move(valuegrid, True, False)
        elif dir == "a":
            fgrid = self.move(valuegrid, False, True)
        elif dir == "d":
            fgrid = self.move(valuegrid, False, False)

        changed = self.animAll(dir)

        for r in range(4):
            for c in range(4):
                self.grid[r][c].changev(fgrid[r][c])

        if changed:
            if self.genblocker > 0:
                self.genblocker -= 1
            else:
                self.genRandom()

            self.spawnItem()
            # logging
            self.logging.writefile(valuegrid)


    # func execute all in shopping cart, returns whether any animation executed
    def animAll(self, dir) -> bool:
        if len(self.animcart) == 0:
            return False

        dirx = 7.5 if dir == 'd' else 0
        dirx = -7.5 if dir == 'a' else dirx
        diry = -7.5 if dir == 'w' else 0
        diry = 7.5 if dir == 's' else diry

        for i in range(10):
            for anim in self.animcart:
                tile, distance = anim
                tile.bmove(dirx*distance, diry*distance)
            time.sleep(0.0001)

        time.sleep(0.2)

        # reset location
        for anim in self.animcart:
            tile, distance = anim
            tile.bmove(-dirx*distance*10, -diry*distance*10)

        self.animcart = []
        return True

    # items, pickup, generate and how they function
    # item has a 20% chance to generate every turn
    def spawnItem(self) -> bool:
        # item spawn chance
        if random.randint(0, 4) != 0:
            return False

        for i, e in enumerate(self.items):
            if e is None:
                newitem = Item(self.win, itemID=random.randint(0, len(itemlist)-1),
                               position=Point(212.5+(i*65), 512.5))
                newitem.draw()
                newitem.blink()
                self.items[i] = newitem

                break
        else:
            self.itemslot_defaulttxt = 'item bar full'
            infotxt.setText(self.itemslot_defaulttxt)

            return False

        return True

    def item_genblocker(self):
        self.genblocker += 2
        return True

    def item_tiledoubler(self):
        pool = []
        for r, re in enumerate(self.grid):
            for ce in re:
                if ce.value != 0:
                    pool.append(ce)
        if len(pool) < 2:
            return False
        target = random.sample(pool, 2)
        for e in target:
            e.changev(e.value*2)
            self.score += e.value
            scoretxt.setText(str(self.score))
        return True

    def item_4hater(self):
        for r, re in enumerate(self.grid):
            for ce in re:
                if ce.value == 4:
                    ce.changev(0)
        return True

    def useitem(self, id: int):
        item = self.items[id]

        if item == None:
            infotxt.setText(f'no item')
            time.sleep(0.5)
            infotxt.setText(self.itemslot_defaulttxt)
            return

        # allocate item to their functions
        if item.name == "GenBlocker":
            used = self.item_genblocker()
        elif item.name == "TileDoubler":
            used = self.item_tiledoubler()
        elif item.name == "4Haters":
            used = self.item_4hater()

        if used:
            infotxt.setText(f'{item.name} used')
            item.blink(expand=False)
            item.undraw()
            self.items[id] = None

            #logging
            self.logging.writefile(f'{item.name} used\n')
        else:
            infotxt.setText(f'failed to use item')

        time.sleep(0.8)
        self.itemslot_defaulttxt = 'item slots:'
        infotxt.setText(self.itemslot_defaulttxt)

# logging and exporting game results
class Logging:
    def __init__(self):
        recordname = time.localtime()
        print(recordname)
        self.file = open(f"log{recordname.tm_hour}{recordname.tm_min!s}.txt", 'w')

    def writefile(self, var):
        if type(var) == list:
            for e in var:
                self.file.write(f'{str(e)}\n')
            self.file.write('\n')
        else:
            self.file.write(str(var))

    def closefile(self):
        self.file.close()


def helpwin():
    try:
        win_help = ButWin(title="Help", width=350, height=420)
        win_help.setBackground("#fcf5eb")
        win_help.createtxt(Point(145, 200), """
        2048 is a game of strategy
        Simply click the four directions
        And combine tiles of the same values
        gathering as much points as possible
        This game comes with a twist of items
        with a 20% chance to spawn per turn~
        Utilize them wisely!

        Items:
        GenBlockers - stops new tile spawning
        for 2 turns

        TileDoubler - double the value of 2 
        random tiles in the grid 

        4Haters - remove ALL 4s from the grid
        \n\n\n\n\n
        Click window to go back:
        """, color='#261803', size=10)

        for i, item in enumerate(itemlist):
            for e in item[1]:
                poly, color = e
                poly = poly.clone()
                poly.setFill(color)
                if type(poly) == Text:
                    poly.setFace('courier')
                    poly.setStyle('bold')
                    poly.setSize(22)
                poly.move(120 + i * 55, 320)
                poly.draw(win_help)

        win_help.getMouse()
        win_help.close()

    except GraphicsError:
        pass


def main():
    # main window layout
    win = ButWin(title="2048 Demake", width=400, height=570)
    win.createtxt(Point(108, 64), '2048\n  Demake', color='#767c85', size=32)
    win.createtxt(Point(104, 60), '2048\n  Demake', color='#e69b19', size=32)

    global gm
    gm = GameManager(win)

    # create buttons
    win.createbut(Point(250, 75), Point(350, 100), action="helpwin()", text="Help", color="#fff6e8")

    global infotxt
    infotxt = win.createtxt(Point(275, 465), text="item slots:", color='grey', size=13)
    win.createbut(Point(315, 485), Point(370, 540), action='gm.useitem(2)')
    win.createbut(Point(250, 485), Point(305, 540), action='gm.useitem(1)')
    win.createbut(Point(185, 485), Point(240, 540), action='gm.useitem(0)')

    win.createbut(Point(65, 450), Point(125, 492.5), heavyshade=False, action='gm.getdir("w")')
    win.createbut(Point(65, 497.5), Point(125, 540), heavyshade=False, action='gm.getdir("s")')
    win.createbut(Point(25, 450), Point(60, 540), heavyshade=False, action='gm.getdir("a")')
    win.createbut(Point(130, 450), Point(165, 540), heavyshade=False, action='gm.getdir("d")')

    # direction symbols
    win.createpoly(Point(82, 478), Point(108, 478), Point(95, 465))
    win.createpoly(Point(82, 512.5), Point(108, 512.5), Point(95, 525))
    win.createpoly(Point(50, 505), Point(50, 485), Point(35, 495))
    win.createpoly(Point(140, 505), Point(140, 485), Point(155, 495))
    # score display
    win.createtxt(Point(275, 40), text="score:", color='grey', size=12)
    global scoretxt
    scoretxt = win.createtxt(Point(340, 40), text="0", color='#86553b', size=18)

    print("The entire game is run on the window, terminal is NOT needed!\n"
          "Press the 'help' button on top right for more information")

    while True:
        try:
            win.checkButtonClick(win.getMouse())
        except GraphicsError:
            gm.logging.writefile(f'final score:{gm.score}')
            gm.logging.closefile()
            sys.exit()

if __name__ == '__main__':
    main()
