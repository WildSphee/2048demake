from graphics import *

# customizable features
colors = {0: '', 2: '#eee4da', 4: '#eee1c9', 8: '#f3b27a', 16: '#f69664', 32: '#f67f5f',
          64: '#f75f3b', 128: "#edd073", 256: "#edcc62", 512: "#edc850", 1024: '#f5e6bc',
          2048:"#dff7d0", "1": "#dacaba", "2": "#e2d3c3"}

itemlist = [("GenBlocker", [(Circle(Point(0, 0), 20), '#8d6bdb'), (Circle(Point(11, 0), 3), 'white'),
                            (Circle(Point(-11, 0), 3), 'white'), (Circle(Point(0, 0), 3), 'white')]),
            ("TileDoubler", [(Circle(Point(0, 0), 20), 'pink'), (Text(Point(0, 0), text='II'), 'white')]),
            ("4Haters", [(Circle(Point(0, 0), 20), 'green'), (Polygon(Point(10, 15), Point(15, 10), Point(5, 0),
            Point(15, -10), Point(10, -15), Point(0, -5), Point(-10, -15), Point(-15, -10), Point(-5, 0),
            Point(-15, 10), Point(-10, 15), Point(0, 5)), 'white'), (Text(Point(0, 0), text='4'), 'orange')]),
            ]