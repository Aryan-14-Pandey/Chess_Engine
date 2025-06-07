"""
This will be our driver file, handle user input and displaying current game state.
"""
import pygame
import pygame as p
from Chess import ChessEngine, ChessAI
from Chess.ChessAI import DEPTH


WIDTH = HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 256
MOVE_LOG_PANEL_HEIGHT = HEIGHT
DIMENSION= 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 #animation
IMAGES = {}

'''
Load Images will initialize a global dictionary of images
'''

def loadImages():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "wR", "wN", "wB", "wQ", "wK", "wp", "bp"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


#driver
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH + MOVE_LOG_PANEL_WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    screen.fill(p.Color("white"))
    gs= ChessEngine.GameState()
    moveLogFont = p.font.SysFont("Times New Roman", 14, False, False)
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False    #Flag variable to check if moveMade = True not because of undo
    gameOver = False
    playerOne = False   #if a human is playing white, this will be true, if AI then false
    playerTwo = False  #same as above for black


    loadImages()
    running = True
    sqSelected = () #no square selected initially, keeps track of last click of the user (row,col)
    playerClicks = [] #upto 2 tuples, player's clicks (two tuples), [(6,4), (4,4)]


    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            #mouse handler
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = pygame.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col) or col>=8 : #user clicks same square twice, or, user clicked the moveLog
                        sqSelected = () #unselect, #first click is select, next is deselected
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected) #append for both first and second click

                    if len(playerClicks) == 2: #after 2nd click
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade: #fixes issues with wasting a click
                            playerClicks = [sqSelected]

            #key handlers
            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_z: #undo when z is pressed
                    print("Z")
                    gs.undoMove()
                    moveMade = True
                    animate = False

                    #resetting the board
                if event.key == pygame.K_r: #reset the board when 'r' is pressed
                    gs = ChessEngine.GameState() #reinstate the game state completely
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False


        '''#AI MOVE FINDER LOGIC
        if not gameOver and not humanTurn:
            AIMove = ChessAI.findBestMove(gs, validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True
        '''

        # AI MOVE FINDER LOGIC
        if not gameOver and not humanTurn:
            print(f"About to call AI. Valid moves: {len(validMoves)}")
            AIMove = ChessAI.findBestMove(gs, validMoves)
            print(f"AI returned: {AIMove}")

            if AIMove is not None:
                gs.makeMove(AIMove)
                moveMade = True
                animate = True
            else:
                print("CRITICAL ERROR: AI returned None!")
                gameOver = True

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False


        drawGameState(screen, gs, validMoves, sqSelected, moveLogFont)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, "Black Wins!")
            else:
                drawText(screen, "White Wins!")
        elif gs.staleMate:
            gameOver = True
            drawText(screen, "Stale Mate!")


        clock.tick(MAX_FPS)
        pygame.display.flip()

def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen,gs.board)
    drawMoveLog(screen, gs, moveLogFont)



def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, pygame.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


#highlight square selected and move for piece selected
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): #square selected is a piece that can be moved
            #highlight the selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(90) #transparency values: 0 - transparent, 255 - opaque
            s.fill(p.Color("blue"))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))

            #highlight the moves from that square
            s.fill(p.Color("yellow"))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))

def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog),2):
        moveString = str(i//2 + 1)  + '. ' + str(moveLog[i]) + " "
        if i+1 < len(moveLog):
            moveString += str(moveLog[i+1]) + "  "
        moveTexts.append(moveString)

    movesPerRow = 3
    padding = 5
    textY = padding
    lineSpacing = 2
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i+j < len(moveTexts):
                text+= moveTexts[i+j]
        textObject = font.render(text, 0, p.Color("white"))
        textLocation = moveLogRect.move(padding,textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing



def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


#animating a move
def animateMove(move, screen, board, clock):
    global colors
    coords = [] #list of rows and cols that the animation will go through
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 4 #frames moved one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount+1):
        r,c = (move.startRow + (frame / frameCount * dR), move.startCol + (frame / frameCount * dC))
        drawBoard(screen)
        drawPieces(screen, board)
        #erase the piece moved from it's ending square
        color=colors[(move.endRow + move.endCol)%2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        #draw captured piece onto rectangle
        if move.pieceCaptured != "--":
            if move.isEnPassantMove:
                enPassantRow = (move.endRow + 1) if move.pieceCaptured[0] == 'b' else (move.endRow - 1)
                endSquare = p.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        #draw moving pieces
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

#Game Over text prompt
def drawText(screen, text):
    font = pygame.font.SysFont("Times New Roman", 45, True)
    textObject = font.render(text, 0, p.Color("white"))
    textLocation = p.Rect(0,0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("red"))
    screen.blit(textObject, textLocation.move(2, 2))


if __name__ == '__main__':
    main()

















