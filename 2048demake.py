from graphics import *
import time
import random
import numpy as np

colors = {0: '', 2: '#eee4da', 4: '#eee1c9', 8: '#f3b27a', 16: '#f69664', 32: '#f67f5f',
          64: '#f75f3b', 128: "#edd073", 256: "#edcc62", 512: "#edc850", "1": "#dacaba", "2": "#e2d3c3"}


def help():
    try:
        win_help = ButWin(title="Help", width=350, height=400)
        win_help.setBackground("#fcf5eb")
        win_help.createtxt(Point(145, 160), """
        2048 is a game of strategy
        Simply click the four directions
        Try to not block your tiles while
        gathering as much points as possible
        This game comes with a twist of items
        They will spawn once every 3 turns~
        Utilize them wisely!
        
        Powerups:
        SpawnBlockers - blocks new tilespawns
        for 3 turns
        
        TileDoubler - double the value of 2 
        random tiles in the grid 
        
        
        Click window to go back:
        """, color='#261803', size=10)

        win_help.getMouse()
        win_help.close()

    except GraphicsError:
        pass

def quit():
    print('exiting')
    sys.exit()


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
        rect2 = Rectangle(Point(p1.x+3, p1.y+3), Point(p2.x+3, p2.y+3))
        rect2.setOutline('grey' if heavyshade else '#bfbfbf')
        rect2.setFill("grey" if heavyshade else '#bfbfbf')
        rect2.draw(self)

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

    def updateGrid(self, grid, v) -> None:
        for r in grid:
            for c in r:
                c.changev(v)

# item logic, as there are only so few im not making subclasses
class item:
    def __init__(self, win, name: str, position: Point):
        self.logo = []
        self.name = name
        self.win = win
        self.blinker = Circle(position, 5)
        
    def draw(self) -> None:
        for e in self.logo:
            e.draw(self.win)

    def blink(self, expand: bool=True):
        self.blinker.draw(self.win)
        self.blinker.radius = 3
        pass


# handles logic, computation and game
class GameManager:
    def __init__(self, win):
        self.win = win
        self.score = 0
        self.items = []
        self.board = Board()
        self.board.createBGGrid(win)
        self.grid = self.board.createGrid(win)
        self.lost = False

        # animation, cart is a collector that executed all at once
        self.animcart = []

    # input: grid -> list of values, change grid, (and play action)
    def move(self, grid, transpose, rightToLeft):
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

        """animation, append it to animcart, honestly couldn't figure out up and down animation 
        and i had to basically hard code it in the end. Not proud of this at all but it works"""
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
        if self.lost:
            return

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

    def lost(self):
        print('game lost')

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

        self.animAll(dir)

        for r in range(4):
            for c in range(4):
                self.grid[r][c].changev(fgrid[r][c])

        self.genRandom()

    # func execute all in shopping cart
    def animAll(self, dir):
        if len(self.animcart) == 0:
            return

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

    # items, pickup, generate and how they function
    def giveItem(self, item: int):
        pass
    
    def useitem(self, item: int):
        if item > len(self.items):
            infotxt.setText(f'no item')
            time.sleep(0.5)
            infotxt.setText(f'item slots')
            return
        infotxt.setText(f'get item{item} used')
        time.sleep(0.5)
        infotxt.setText(f'item slots')


def main():
    # main window layout
    win = ButWin(title="2048 Demake", width=400, height=570)
    win.createtxt(Point(108, 64), '2048\n  Demake', color='#767c85', size=32)
    win.createtxt(Point(104, 60), '2048\n  Demake', color='#e69b19', size=32)

    global gm
    gm = GameManager(win)

    # create buttons
    win.createbut(Point(250, 75), Point(350, 100), action="help()", text="Help", color="#fff6e8")

    global infotxt
    infotxt = win.createtxt(Point(275, 465), text="item slots:", color='grey', size=13)
    win.createbut(Point(315, 485), Point(370, 540), action='gm.useitem(3)')
    win.createbut(Point(250, 485), Point(305, 540), action='gm.useitem(2)')
    win.createbut(Point(185, 485), Point(240, 540), action='gm.useitem(1)')

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
    win.createtxt(Point(280, 40), text="score:", color='grey', size=12)
    global scoretxt
    scoretxt = win.createtxt(Point(330, 40), text="0", color='#86553b', size=16)

    while True:
        try:
            win.checkButtonClick(win.getMouse())
        except GraphicsError:
            quit()

if __name__ == '__main__':
    main()
