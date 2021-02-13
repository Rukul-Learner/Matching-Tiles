import random,pygame,sys
from pygame.locals import *

FPS = 30

TileSize = 50 #in pixels
GapSize = 10 #in pixels
RevealSpeed = 10
BoardSize = 10 # in rows and columns
# x-y coordinates of top left corner of game board
boardTopLeftX = int((1280-(BoardSize * (TileSize + GapSize)))/2)
boardTopLeftY = int((720-(BoardSize * (TileSize + GapSize)))/2)

#Colors      R   G   B
Gray     = (100,100,100)
NavyBlue = (60 , 60,100)
White    = (255,255,255)
Red      = (255, 0 , 0 )
Green    = ( 0 ,255, 0 )
Blue     = ( 0 , 0 ,255)
Yellow   = (255,255, 0 )
Orange   = (255,128, 0 )
Purple   = (255, 0 ,255)
Cyan     = ( 0 ,255,255)
Pink     = (255, 0 ,127)
Olive    = ( 51,102, 0 )
Lavender = (128, 0 ,128)

#Shapes
DONUT="donut"
SQUARE="square"
DIAMOND="diamond"
OVAL="oval"
LINES="lines"

BackgroundColor = NavyBlue
CoverColor = White
LightBgColor= Gray
HighlightColor = Blue

allColors=(Red, Green, Blue, Yellow, Orange, Purple, Cyan, Pink, Olive, Lavender)
allShapes=(DONUT, SQUARE, DIAMOND, OVAL, LINES)

#main function
def main():
    global FPSCLOCK, DISPLAYSURF
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((1280,720))

    mousex = 0 # used to store x coordinate of mouse event
    mousey = 0 # used to store y coordinate of mouse event
    pygame.display.set_caption('Memory Tiles')

    gameBoard = getRandomizedBoard()
    RevealedTiles = generateRevealedTiles(False)

    firstSelection = None # stores the (x, y) of the first box clicked.

    DISPLAYSURF.fill(BackgroundColor)
    startGameAnimation(gameBoard)

    while True: # main game loop
        mouseClicked = False

        DISPLAYSURF.fill(BackgroundColor) # drawing the window
        drawBoard(gameBoard, RevealedTiles)

        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouseClicked = True

        tilex, tiley = getTileAtPixel(mousex, mousey)
        if tilex != None and tiley != None:
            # The mouse is currently over a tile.
            if not RevealedTiles[tilex][tiley]:
                drawHighlightBox(tilex, tiley)
            if not RevealedTiles[tilex][tiley] and mouseClicked:
                revealTilesAnimation(gameBoard, [(tilex, tiley)])
                RevealedTiles[tilex][tiley] = True # set the box as "revealed"
                if firstSelection == None: # the current box was the first box clicked
                    firstSelection = (tilex, tiley)
                else: # the current box was the second box clicked
                    # Check if there is a match between the two icons.
                    icon1shape, icon1color = getShapeAndColor(gameBoard, firstSelection[0], firstSelection[1])
                    icon2shape, icon2color = getShapeAndColor(gameBoard, tilex, tiley)

                    if icon1shape != icon2shape or icon1color != icon2color:
                        # Icons don't match. Re-cover up both selections.
                        pygame.time.wait(1000) # 1000 milliseconds = 1 sec
                        coverTilesAnimation(gameBoard, [(firstSelection[0], firstSelection[1]), (tilex, tiley)])
                        RevealedTiles[firstSelection[0]][firstSelection[1]] = False
                        RevealedTiles[tilex][tiley] = False
                    elif hasWon(RevealedTiles): # check if all pairs found
                        gameWonAnimation(gameBoard)
                        pygame.time.wait(2000)

                        # Reset the board
                        gameBoard = getRandomizedBoard()
                        RevealedTiles = generateRevealedTiles(False)

                        # Show the fully unrevealed board for a second.
                        drawBoard(gameBoard, RevealedTiles)
                        pygame.display.update()
                        pygame.time.wait(1000)

                        # Replay the start game animation.
                        startGameAnimation(gameBoard)
                    firstSelection = None # reset firstSelection variable

        # Redraw the screen and wait a clock tick.
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def generateRevealedTiles(val):#takes boolean parameter
    revealedTiles = []
    for i in range(BoardSize):#columns
        revealedTiles.append([val] * BoardSize)#rows
    return revealedTiles

def getRandomizedBoard():
    #get list of all possible tile patterns
    tiles=[]
    for color in allColors:
        for shapes in allShapes:
            tiles.append((shapes, color))
    tiles=tiles*2
    random.shuffle(tiles)
    board = []
    for x in range(BoardSize):
        column=[]
        for y in range(BoardSize):
            column.append(tiles[0])
            del tiles[0]
        board.append(column)
    return board

def splitIntoGroupsOf(groupSize, theList):
    # splits a list into a list of lists, where the inner lists have at
    # most groupSize number of items.
    result = []
    for i in range(0, len(theList), groupSize):
        result.append(theList[i:(i + groupSize)])
    return result


def leftTopCoordinatessOfTile(tilecoverx, tilecovery):
    # Convert board coordinates to pixel coordinates
    left = tilecoverx * (TileSize + GapSize) + boardTopLeftX
    top = tilecovery * (TileSize + GapSize) + boardTopLeftY
    return (left, top)


def getTileAtPixel(x, y):
    for tilex in range(BoardSize):
        for tiley in range(BoardSize):
            left, top = leftTopCoordinatessOfTile(tilex, tiley)
            tileRect = pygame.Rect(left, top, TileSize, TileSize)
            if tileRect.collidepoint(x, y):
                return (tilex, tiley)
    return (None, None)


def drawTile(shape, color, tilecoverx, tilecovery):
    quarter = int(TileSize * 0.25) # syntactic sugar
    half =    int(TileSize * 0.5)  # syntactic sugar

    left, top = leftTopCoordinatessOfTile(tilecoverx, tilecovery) # get pixel coords from board coords(tilecoverx = x row of grid)
    # Draw the shapes
    if shape == DONUT:
        pygame.draw.circle(DISPLAYSURF, color, (left + half, top + half), half - 5)
        pygame.draw.circle(DISPLAYSURF, BackgroundColor, (left + half, top + half), quarter - 5)
    elif shape == SQUARE:
        pygame.draw.rect(DISPLAYSURF, color, (left + quarter, top + quarter, TileSize - half, TileSize - half))
    elif shape == DIAMOND:
        pygame.draw.polygon(DISPLAYSURF, color, ((left + half, top), (left + TileSize - 1, top + half), (left + half, top + TileSize - 1), (left, top + half)))
    elif shape == LINES:
        for i in range(0, TileSize, 4):
            pygame.draw.line(DISPLAYSURF, color, (left, top + i), (left + i, top))
            pygame.draw.line(DISPLAYSURF, color, (left + i, top + TileSize - 1), (left + TileSize - 1, top + i))
    elif shape == OVAL:
        pygame.draw.ellipse(DISPLAYSURF, color, (left, top + quarter, TileSize, half))


def getShapeAndColor(board, tilex, tiley):
    # shape value for x, y spot is stored in board[x][y][0]
    # color value for x, y spot is stored in board[x][y][1]
    return board[tilex][tiley][0], board[tilex][tiley][1]


def drawTileCovers(board, tiles, coverage):
    # Draws tiles being covered/revealed. "tiles" is a list
    # of two-item lists, which have the x & y spot of the tile.
    for tile in tiles:
        left, top = leftTopCoordinatessOfTile(tile[0], tile[1])
        pygame.draw.rect(DISPLAYSURF, BackgroundColor, (left, top, TileSize, TileSize))
        shape, color = getShapeAndColor(board, tile[0], tile[1])
        drawTile(shape, color, tile[0], tile[1])
        if coverage > 0: # only draw the cover if there is an coverage
            pygame.draw.rect(DISPLAYSURF, CoverColor, (left, top, coverage, TileSize))
    pygame.display.update()
    FPSCLOCK.tick(FPS)


def revealTilesAnimation(board, tilesToReveal):
    # Do the "tile reveal" animation.
    for coverage in range(TileSize, (-RevealSpeed) - 1, -RevealSpeed):
        drawTileCovers(board, tilesToReveal, coverage)


def coverTilesAnimation(board, tilesToCover):
    # Do the "tile cover" animation.
    for coverage in range(0, TileSize + RevealSpeed, RevealSpeed):
        drawTileCovers(board, tilesToCover, coverage)


def drawBoard(board, revealed):
    # Draws all of the tiles in their covered or revealed state.
    for x in range(BoardSize):
        for y in range(BoardSize):
            left, top = leftTopCoordinatessOfTile(x, y)
            if not revealed[x][y]:
                # Draw a covered tile.
                pygame.draw.rect(DISPLAYSURF, CoverColor, (left, top, TileSize, TileSize))
            else:
                # Draw the (revealed) icon.
                shape, color = getShapeAndColor(board, x, y)
                drawTile(shape, color, x, y)


def drawHighlightBox(boxx, boxy):
    left, top = leftTopCoordinatessOfTile(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, HighlightColor, (left - 5, top - 5, TileSize + 10, TileSize + 10), 4)


def startGameAnimation(board):
    # Randomly reveal the tiles 10 at a time.
    coveredTiles = generateRevealedTiles(False)
    tilecovers = []
    for x in range(BoardSize):
        for y in range(BoardSize):
            tilecovers.append( (x, y) )
    random.shuffle(tilecovers)
    tileGroups = splitIntoGroupsOf(10, tilecovers)

    drawBoard(board, coveredTiles)
    for tileGroup in tileGroups:
        revealTilesAnimation(board, tileGroup)
        coverTilesAnimation(board, tileGroup)


def gameWonAnimation(board):
    # flash the background color when the player has won
    coveredTiles = generateRevealedTiles(True)
    color1 = LightBgColor
    color2 = BackgroundColor

    for i in range(13):
        color1, color2 = color2, color1 # swap colors
        DISPLAYSURF.fill(color1)
        drawBoard(board, coveredTiles)
        pygame.display.update()
        pygame.time.wait(300)


def hasWon(revealedTiles):
    # Returns True if all the tiles have been revealed, otherwise False
    for i in revealedTiles:
        if False in i:
            return False # return False if any boxes are covered.
    return True


if __name__ == '__main__':
    main()
