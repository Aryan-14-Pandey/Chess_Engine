"""
Stores all info about the current game state.
Also, responsible for determining the valid moves at the current state.
Maintains a move log.
"""
class GameState:
    def __init__(self):
        #board is a 8x8 2-D List
        #each element has two characters, first character represents the color of the piece.
        #second character represents type of the piece.
        # string "--" represents an empty square with no piece.
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]



        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.checkMate = False
        self.staleMate = False
        self.enPassantPossible = () #coordinatees for the square where the en passant is possible
        self.enPassantPossibleLog = [self.enPassantPossible]
        self.currentCastlingRights = CastleRights(wks=True, bks=True, wqs=True, bqs=True)
        self.castleRightsLog = [CastleRights(wks=self.currentCastlingRights.wks,
                                             bks=self.currentCastlingRights.bks,
                                             wqs=self.currentCastlingRights.wqs,
                                             bqs=self.currentCastlingRights.bqs)]



        self.moveFunctions = {"p" : self.getPawnMoves, "N" : self.getKnightMoves, "B" : self.getBishopMoves,
                              "Q" : self.getQueenMoves, "K" : self.getKingMoves, "R" : self.getRookMoves,}

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #log the move to undo it later or display history of the game.
        self.whiteToMove = not self.whiteToMove  # swap turns
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] +'Q'

        #castling move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: #king side castle
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = "--"  # Clear the old rook
            else: #queen side castle
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2] = "--"


        # enpassant move
        if move.isEnPassantMove:
            self.board[move.startRow][move.endCol]= '--'  # capturing the pawn

        #update is enpassantPossible variable
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2: #only when pawn moves 2 squares
            self.enPassantPossible = ((move.startRow + move.endRow)//2, move.startCol) #take the average, pawn moves, 6 to 4, capture square is 5
        else:
            self.enPassantPossible = ()

        #update the castling rights: when a king or rook is moved
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                             self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))

        self.enPassantPossibleLog.append(self.enPassantPossible)

    #undo the last made move
    def undoMove(self):
        if len(self.moveLog) > 0: #make sure move log is not empty, there should be a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved #put the piece moved onto the prev square
            self.board[move.endRow][move.endCol] = move.pieceCaptured

            self.whiteToMove = not self.whiteToMove  # change turns back


            #update king's position if needed
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)


            #undo enpassant
            if move.isEnPassantMove:
                self.board[move.endRow][move .endCol] = '--' #leave the capture square black
                self.board[move.startRow][move.endCol]= move.pieceCaptured


            self.enPassantPossibleLog.pop()
            self.enPassantPossible = self.enPassantPossibleLog[-1]


            #undo castling rights
            self.castleRightsLog.pop()  # get rid of new castle rights from the move that we're doing
            # Fixed castling rights restoration
            if len(self.castleRightsLog) > 0:
                prevRights = self.castleRightsLog[-1]
                # Create a NEW object instead of referencing the same one
                self.currentCastlingRights = CastleRights(
                    prevRights.wks, prevRights.bks,
                    prevRights.wqs, prevRights.bqs
                )
            else:
                self.currentCastlingRights = CastleRights(True, True, True, True)


            #undo the castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # kingside
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = "--"

                else:  # queenside
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = "--"

            self.checkMate = False
            self.staleMate = False


    #function to update the castle rights
    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False

        elif move.pieceMoved == 'bK':
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False

        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.wks = False

        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.bks = False

        #if a rook is captured
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.bks = False


    def getValidMoves(self):
        tempEnPassantPossible = self.enPassantPossible
        tempCastleRights  = CastleRights(self.currentCastlingRights.wks,self.currentCastlingRights.bks,
                                         self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)
        #1 generate all moves
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        #2 make the move
        for i in range(len(moves) - 1, -1, -1):  # when removing from a list go backwards through that list
            self.makeMove(moves[i])

        #3 generate all opponents moves,

        #4 see if they attack your king
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()

        #checkmate or stalemate
        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True

        #5 if they do attack the king, not a valid move
        self.enPassantPossible = tempEnPassantPossible
        self.currentCastlingRights = tempCastleRights
        return moves


    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    def getAllPossibleMoves(self):
        moves = []
        for c in range(len(self.board[0])):  # cols
            for r in range(len(self.board)):  # rows
                turn = self.board[r][c][0]
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)
        return moves




    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:  # white pawn
            if self.board[r-1][c]== "--": #one square forward move for the pawn
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--" : # 2 square pawn advance
                    moves.append(Move((r, c), (r - 2, c), self.board))

            if c-1 >= 0: #captures to the left
                if self.board[r-1][c-1][0] == "b":
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1,c-1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r-1, c-1), self.board, isEnPassantMove=True))

            if c+1 < len(self.board[0]): #captures to the right
                if self.board[r-1][c+1][0] == "b":
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r - 1, c + 1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r - 1, c+1), self.board, isEnPassantMove=True))



        else:  # black pawn
            if r+1<8:
                if self.board[r+1][c]== "--": #one square forward move for the pawn
                    moves.append(Move((r, c), (r+1, c), self.board))
                    if r == 1 and self.board[r +2][c] == "--" : # 2 square pawn advance
                        moves.append(Move((r, c), (r +2, c), self.board))

                if c - 1 >= 0:  # captures to the left
                    if self.board[r+1][c - 1][0] == "w":
                        moves.append(Move((r, c), (r + 1, c - 1), self.board))
                    elif (r + 1, c - 1) == self.enPassantPossible:
                        moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnPassantMove=True))

                if c + 1 < len(self.board[0]): #captures to the right
                    if self.board[r+1][c + 1][0] == "w":
                        moves.append(Move((r, c), (r + 1, c + 1), self.board))
                    elif (r + 1, c + 1) == self.enPassantPossible:
                        moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnPassantMove=True))




    def getKnightMoves(self, r, c, moves):
        possibleKnightMoves = [(1,2), (2,1), (-2,1), (-1,2), (2, -1), (1,-2), (-2,-1), (-1,-2)]

        if self.whiteToMove: opp = "b"
        else: opp = "w"

        for d in possibleKnightMoves:
            endRow = r + d[0]
            endCol = c + d[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if (self.board[endRow][endCol]  == "--") or (self.board[endRow][endCol][0] == opp):
                    moves.append(Move((r, c), (r+d[0], c+d[1]), self.board))

    def getRookMoves(self, r, c, moves):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
        if self.whiteToMove:
            enemy_color = 'b'
        else:
            enemy_color = 'w'

        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i

                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":  # empty square
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemy_color:  # capture enemy piece
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break  # cannot jump over pieces
                    else:
                        break  # friendly piece blocks path
                else:
                    break  # off board

    def getBishopMoves(self, r, c, moves):
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # four diagonals
        enemy_color = 'b' if self.whiteToMove else 'w'

        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i

                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":  # empty square
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemy_color:  # capture enemy piece
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break  # cannot jump over pieces
                    else:
                        break  # friendly piece blocks path
                else:
                    break  # off board

    def getQueenMoves(self, r, c, moves):
        # Queen moves are rook moves + bishop moves combined
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        possibleKingMoves = [(1, 1), (-1, -1), (-1, 0), (-1, 1), (1, 0), (0, -1), (1, -1), (0, 1)]
        allyColor = "w" if self.whiteToMove else "b"
        if not self.whiteToMove:
            opp = "w"
        else:
            opp = "b"
        for d in possibleKingMoves:
            endRow = r + d[0]
            endCol = c + d[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if(self.board[endRow][endCol] == "--") or (self.board[endRow][endCol][0] == opp):
                    moves.append(Move((r, c), (r+d[0], c+d[1]), self.board))

        #castling



    #generating all valid castle moves for the king at (r,c) and add them to the list of moves
    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r,c):
            return #can't castle if in check
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingSideCastleMoves(r, c,moves)

        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueenSideCastleMoves(r, c, moves)




    def getKingSideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove = True))



    def getQueenSideCastleMoves(self, r, c, moves):
        if self.board[r][c - 1] == "--" and self.board[r][c - 2] == "--" and self.board[r][c - 3] == "--":
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))





class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs




class Move: #stores all info about the current move, piece captured, en passant, castling etc.

    #ranked notation to denote each square ex: a7 blah blah
    # maps keys to values
    # key : value

    ranksToRows = {"1" : 7, "2" : 6, "3" : 5, "4" : 4, "5" : 3, "6" : 2, "7" : 1, "8" : 0}
    rowsToRanks ={v: k for k, v in ranksToRows.items()} #reverses the dict mapping
    filesToCols ={"a" : 0 , "b" : 1, "c" : 2, "d" : 3, "e" : 4, "f" : 5, "g" : 6, "h" : 7 }
    colsToFiles = {v: k for k, v in filesToCols.items()}


    def __init__(self, startSq, endSq, board, isEnPassantMove = False, isCastleMove = False): #enpassant, castling possibility

        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]


        #en passant
        self.isEnPassantMove = isEnPassantMove
        if self.isEnPassantMove and board[self.endRow][self.endCol] == "--":
            # Only override if the capture square is empty (true en passant)
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'

        self.isCapture = self.pieceCaptured != '--'
        #castle move
        self.isCastleMove = isCastleMove


        #pawn promotion
        self.isPawnPromotion = False
        if (self.pieceMoved == "wp" and self.endRow == 0) or (self.pieceMoved == "bp" and self.endRow == 7):
            self.isPawnPromotion = True

        #id of each move ex: g1f3
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol


    #Overriding the equals method
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)


    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    def __str__(self):
        #castle move:
        if self.isCastleMove:
            return "O-O" if self.endCol == 6 else "O-O-O"

        endSquare = self.getRankFile(self.endRow, self.endCol)

        #pawn moves
        if self.pieceMoved[1] == "p":
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "x" +endSquare
            else:
                return endSquare


        #piece moves
        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString += "x"
        return moveString + endSquare



