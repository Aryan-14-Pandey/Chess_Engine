import random

pieceScores = {"K": 0, "Q": 9, "R": 5, "B": 3.01, "N":3, "p" : 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3

pawnScores =[
[0,  0,  0,  0,  0,  0,  0,  0],
[50, 50, 50, 50, 50, 50, 50, 50],
[10, 10, 20, 30, 30, 20, 10, 10],
[ 5,  5, 10, 25, 25, 10,  5,  5],
 [0,  0,  0, 20, 20,  0,  0,  0],
 [5, -5,-10,  0,  0,-10, -5,  5],
 [5, 10, 10,-20,-20, 10, 10,  5],
 [0,  0,  0,  0,  0,  0,  0,  0]
]

kingScores=[
[-30,-40,-40,-50,-50,-40,-40,-30],
[-30,-40,-40,-50,-50,-40,-40,-30],
[-30,-40,-40,-50,-50,-40,-40,-30],
[-30,-40,-40,-50,-50,-40,-40,-30],
[-20,-30,-30,-40,-40,-30,-30,-20],
[-10,-20,-20,-20,-20,-20,-20,-10],
[20, 20,  0,  0,  0,  0, 20, 20],
[20, 40, 10,  0,  0, 10, 30, 20]
]

piecePositionScores = {
    'p': pawnScores,
    'K' : kingScores
                        }


'''
Picks and returns a random move
'''
def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]


'''
Find the best move based on material alone
'''
'''
def findBestMaterialMove(gs, validMoves): #greedy

    turnMultiplier = 1 if gs.whiteToMove else -1
    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = None
    random.shuffle(validMoves)
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        opponentMoves = gs.getValidMoves()
        if gs.staleMate:
            score = STALEMATE
        if gs.checkMate:
            opponentMaxScore = -CHECKMATE
        else:
            opponentMaxScore = -CHECKMATE
            for opponentMove in opponentMoves:
                gs.makeMove(opponentMove)
                if gs.checkMate:
                    score = CHECKMATE
                elif gs.staleMate:
                    score = STALEMATE
                else:
                    score = -turnMultiplier * scoreMaterial(gs.board)
                if score > opponentMaxScore:
                    opponentMaxScore = score
                gs.undoMove()
        if opponentMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove
        gs.undoMove()

    return bestPlayerMove
'''



'''Helper method to make first recursive call'''
def findBestMove(gs, validMoves):
    global nextMove, counter
    counter = 0
    nextMove = None
    random.shuffle(validMoves)
    #findMoveMinMax(gs, validMoves,  DEPTH, not gs.whiteToMove)
    #findNegaMaxMove(gs, validMoves, DEPTH, 1 if gs.whiteToMove else -1 )
    findNegaMaxAlphaBetaMove(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    if nextMove is None:
        print("WARNING: AI couldn't find move, using fallback")
        nextMove = validMoves[0]
    print(counter)

    return nextMove

def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return scoreMaterial(gs.board)

    random.shuffle(validMoves)
    if whiteToMove:
        maxScore = -CHECKMATE

        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, not whiteToMove)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return maxScore

    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, not whiteToMove)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return minScore

def findNegaMaxMove(gs, validMoves, depth, turnMultiplier):
    global nextMove, counter
    counter += 1
    #always looking for maximum, negating it gives us black's best move, i.e. the minimum
    if depth == 0: #base case
        return turnMultiplier * scoreBoard(gs)

    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findNegaMaxMove(gs, nextMoves, depth - 1, -turnMultiplier)     #recursive call

        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move

        gs.undoMove()
    return maxScore

def findNegaMaxAlphaBetaMove(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    global counter
    counter += 1
    #always looking for maximum, negating it gives us black's best move, i.e. the minimum
    if depth == 0: #base case
        return turnMultiplier * scoreBoard(gs)

    #move ordering - evaluate the best moves first
    orderedMoves = orderMoves(gs, validMoves)

    maxScore = -CHECKMATE
    for move in orderedMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findNegaMaxAlphaBetaMove(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)     #recursive call

        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
                print(nextMove,score)
        gs.undoMove()

        #pruning
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore


'''A positive score is good for white, a negative score is good for black '''
def scoreBoard(gs):
    if gs.checkMate:
        if gs.whiteToMove:
            return -CHECKMATE #black wins
        else:
            return CHECKMATE #white wins

    elif gs.staleMate:
        return STALEMATE #neither side wins
    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--":
                #score it positionally
                piecePositionScore = 0

                if square[1] == 'K':
                    piecePositionScore = piecePositionScores["K"][row][col] if square[0] == 'w' else piecePositionScores["K"][7 - row][col]
                elif square[1] == 'p':
                    piecePositionScore = piecePositionScores["p"][row][col] if square[0] == 'w' else piecePositionScores["p"][7 - row][col]

                if square[0] == 'w':
                    score += pieceScores[square[1]]*10 + (piecePositionScore * 0.0003)
                elif square[0] == 'b':
                    score -= pieceScores[square[1]]*10 + (piecePositionScore * 0.0003)

    # Penalize repetition
    if len(gs.moveLog) >= 8 and gs.moveLog[-1].getChessNotation() == gs.moveLog[-3].getChessNotation():
        score -= 5.0  # or larger depending on severity
    # Bonus for captured pieces in previous move
    if gs.moveLog:
        lastMove = gs.moveLog[-1]
        if lastMove.pieceCaptured != "--":
            score += 0.2 if lastMove.pieceMoved[0] == 'w' else -0.2

    return score


'''Score the board based on material alone, not checkmate'''
def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square != "--":
                if square[0] == 'w':
                    score += pieceScores[square[1]]
                elif square[0] == 'b':
                    score -= pieceScores[square[1]]

    return score




def orderMoves(gs, moves):
    """
    Order moves to improve alpha-beta pruning efficiency.
    Priority: captures > checks > other moves
    """
    captures = []
    checks = []
    others = []

    for move in moves:
        gs.makeMove(move)

        # Check if this move resulted in check
        if gs.inCheck():
            checks.append(move)
        # Check if this was a capture (piece was taken)
        elif move.pieceCaptured != "--":
            captures.append(move)
        else:
            others.append(move)

        gs.undoMove()

    # Return captures first, then checks, then other moves
    return captures + checks + others













