from copy import deepcopy
import random

PLAYER = 0
AI = 1 #clean up
FIRSTMOVE=AI

class MillGame():
    #MAYBE swith 0 and 1 to magic numbers PLAYER1, PLAYER2
    def __init__(self,gameState,moves=[],turn=0):
        self.gameState=gameState
        self.pastMoves=moves
        self.turn=turn
        self.connections={}  #STATIC creates a dictionary with what points are connected to what
        for sq in range(3):#^^^
            for th in range(8):
                if th%2==1:
                    # corners of each square
                    self.connections[(sq,th)]=[(sq,(th+1)%8),(sq,th-1)]
                elif sq==0:
                    #outer square edges
                    self.connections[(sq,th)]=[(sq,th+1),(sq,(th-1)%8),(sq+1,th)]
                elif sq==1:
                    #middle square edges
                    self.connections[(sq,th)]=[(sq,th+1),(sq,(th-1)%8),(sq+1,th),(sq-1,th)]
                elif sq==2:
                    #inner square edges
                    self.connections[(sq,th)]=[(sq,th+1),(sq,(th-1)%8),(sq-1,th)]
        self.triples=[] #STATIC creates a list of all rows of 3 on the board , maybe should be a dic for each point
        for sq in range(3): #^^^
            self.triples.append([(sq,th) for th in [7,0,1]])
            self.triples.append([(sq,th) for th in [1,2,3]])
            self.triples.append([(sq,th) for th in [3,4,5]])
            self.triples.append([(sq,th) for th in [5,6,7]])
        for th in [0,2,4,6]:#^^^ #triples of the form [(sq,th),(sq,th),(sq,th)]
            self.triples.append([(sq,th) for sq in [0,1,2]])
        self.mills=self.getMills(self.gameState)
        self.pieces=[self.getPieces(0),self.getPieces(1)]

    def makeMove(self, move): #actually makes a move
        if move[0]=="place": #["place", piece]
            self.gameState[move[1]]=self.turn
        elif move[0]=="placer":#["placer", piece, removable]
            self.gameState[move[1]]=self.turn
            self.gameState[move[2]]="."
        elif move[0]=="move":#["move", piece, neighbor]
            self.gameState[move[1]]="."
            self.gameState[move[2]]=self.turn
        elif move[0]=="mover":#["mover", piece, neighbor, removable]
            self.gameState[move[1]]="."
            self.gameState[move[2]]=self.turn
            self.gameState[move[3]]="."

        self.pastMoves.append(move)
        self.mills=self.getMills(self.gameState) #MAYBE could be optimized so you dont have to recalculate
        self.pieces=[self.getPieces(PLAYER),self.getPieces(AI)] #SHOULD be optimized so you dont have to recalculate
        self.turn=self.enemy(self.turn)
        
    def getRemovables(self, turn): #given a player, returns all enemy pieces that can be removed
        removables=[]
        enemyPieces=self.pieces[self.enemy(turn)]
        for enemyPiece in enemyPieces:
            addIt=True
            for mill in self.mills:
                if enemyPiece in mill[1]:
                    addIt=False
            if addIt:
                removables.append(enemyPiece)
        if removables:
            return removables
        return enemyPieces

    def enemy(self,turn): #returns enemy
        if turn==0:
            return 1
        else:
            return 0

    def getPieces(self,turn): #returns a list of spots where each player has pieces
        pieces=[]
        for sq in range(3):
            for th in range(8):
                if self.gameState[(sq,th)]==turn:
                    pieces.append((sq,th))
        return pieces

    def getMills(self,gameState): #mills of the form [turn, [(sq,th),(sq,th),(sq,th)]]
        mills=[]
        for triple in self.triples:
            val=gameState[triple[0]]
            if val==gameState[triple[1]]==gameState[triple[2]] and val!=".":
                mills.append([val, triple])
        return mills

    def isWin0(self,possMoves): #checks if player 0 has won
        if (len(self.pastMoves)>=18 and len(self.pieces[1])<=2 or not possMoves):
            return True
        return False

    def isWin1(self, possMoves): #checks if player 1 has won
        if (len(self.pastMoves)>=18 and len(self.pieces[0])<=2) or not possMoves:
            return True
        return False
            
    def getPossMoves(self): #moves of the form [type, start (sq,th), end(if)(sq,th),remove(sq,th)]
        possMoves=[]
        if len(self.pastMoves)<18: #placing phase
            for sq in range(3):
                for th in range(8):
                    if self.gameState[(sq,th)]==".":
                        temp_gameState=self.gameState.copy()
                        temp_gameState[(sq,th)]=self.turn
                        if len(self.getMills(temp_gameState))>len(self.mills):
                            for removable in self.getRemovables(self.turn):
                                possMoves.append(["placer",(sq,th),removable])
                        else:
                            possMoves.append(["place",(sq,th)])
        else: #moving phase 
            # MAYBE insert option for variation where you can move anywhere after 3 pieces left
            for sq in range(3):
                for th in range(8):
                    if self.gameState[(sq,th)]==self.turn:
                        for neighbor in self.connections[(sq,th)]:
                            if self.gameState[neighbor]==".":
                                temp_gameState=self.gameState.copy()
                                temp_gameState[(sq,th)]="."
                                temp_gameState[neighbor]=self.turn
                                formsMill=False
                                for mill in self.getMills(temp_gameState):
                                    if neighbor in mill[1]:
                                        formsMill=True
                                        for removable in self.getRemovables(self.turn):
                                            possMoves.append(["mover",(sq,th),neighbor,removable])
                                if not formsMill:
                                    possMoves.append(["move",(sq,th),neighbor])
        return possMoves

class UIhandler():
    def askForMove(self,game: MillGame, possMoves):
        print("Player "+str(game.turn)+" to move, please enter command:")
        possMovesList=possMoves
        possMovesDict={}
        for move in possMovesList:
            possMovesDict[str(move)]=move
        inp=input()
        if inp in possMovesDict:
            return possMovesDict[inp]
        elif inp=="move":
            print("not a feature yet")
            return self.askForMove(game, possMoves)
        elif inp=="poss":
            print(possMovesList)
            return self.askForMove(game, possMoves)
        elif inp=="moves":
            print(game.pastMoves)
            return self.askForMove(game, possMoves)
        elif inp=="mills":
            print(game.mills)
            return self.askForMove(game, possMoves)
        elif inp=="pieces":
            print(game.pieces)
            return self.askForMove(game, possMoves)
        elif inp=="end":
            print("bye")
            return "end"
        elif inp=="help":
            print("INSERT help and rules here")
            return self.askForMove(game, possMoves)
        elif inp=="new":
            #INSERT a new game function here
            print("not a feature yet")
            return self.askForMove(game, possMoves)
        else:
            print("please enter a valid command")
            return self.askForMove(game, possMoves)

    def showIntro(self):

        print("Wellcome to Mills, enter 'new' for a new game, 'end' to quit, 'help' for instructions")
        inp=input()
        while inp not in ["new", "end"]:
            if inp=="help":
                print("INSERT help and rules here")
            else:
                print("please enter valid command")
            inp=input()
        if inp=="new":
            return "play"
        elif inp=="end":
            print("bye")
            return "end"

    def showboard(self, game: MillGame): #prints gameboard

        for th in [7,0,1]:
            print(game.gameState[0,th], end="     ")
        print()
        print(end="  ")
        for th in [7,0,1]:
            print(game.gameState[1,th], end="   ")
        print()
        print(end="    ")
        for th in [7,0,1]:
            print(game.gameState[2,th], end=" ")
        print()

        for sq in [0,1,2]:
            print(game.gameState[sq,6], end=" ")
        print(end="  ")
        for sq in [2,1,0]:
            print(game.gameState[sq,2], end=" ")
        print()

        print(end="    ")
        for th in [5,4,3]:
            print(game.gameState[2,th], end=" ")
        print()
        print(end="  ")
        for th in [5,4,3]:
            print(game.gameState[1,th], end="   ")
        print()
        for th in [5,4,3]:
            print(game.gameState[0,th], end="     ")
        print()

class PvPGame():
    def __init__(self,firstmove=0):
        self.handler=UIhandler()
        gameState={}
        for sq in range(3):
            for th in range(8):
                gameState[(sq,th)]="."
        self.game=MillGame(gameState,[], firstmove)
        if self.handler.showIntro()=="play":
            self.play()

    def play(self):
        playing=True
        self.handler.showboard(self.game)
        while playing:
            possMoves=self.game.getPossMoves()
            if self.game.isWin0(possMoves): #checks p0 wins
                print("Player 0 has won the Game in "+ str(len(self.game.pastMoves)) + " moves")
                self.result, playing=0, False
                break
            if self.game.isWin1(possMoves): #checks p1 wins
                print("Player 1 has won the Game in "+ str(len(self.game.pastMoves)) + " moves")
                self.result, playing=1, False
                break
            elif len(self.game.pastMoves)>200: #draw
                print("its a draw, 200 move limit exceeded")
                self.result, playing=0.5, False
                break

            command=self.handler.askForMove(self.game, possMoves)
            if command=="end":
                playing=False
            else:
                self.game.makeMove(command)
                self.handler.showboard(self.game)

class PvAIGame():
    #PLAYER = 0
    #AI = 1
    def __init__(self,firstmove=0):
        self.handler=UIhandler()
        self.ai=GameAI() #REMOVE hardcode part
        gameState={}
        for sq in range(3):
            for th in range(8):
                gameState[(sq,th)]="."
        self.game=MillGame(gameState,[], firstmove)
        if self.handler.showIntro()=="play":
            self.play()

    def play(self):
        playing=True
        self.handler.showboard(self.game)
        while playing:
            possMoves=self.game.getPossMoves()
            if self.game.isWin0(possMoves): #checks p0 wins
                print("You have won the Game in "+ str(len(self.game.pastMoves)) + " moves")
                self.result, playing=0, False
                break
            if self.game.isWin1(possMoves): #checks p1 wins
                print("AI has won the Game in "+ str(len(self.game.pastMoves)) + " moves")
                self.result, playing=1, False
                break
            elif len(self.game.pastMoves)>200: #draw
                print("its a draw, 200 move limit exceeded")
                self.result, playing=0.5, False
                break
            if self.game.turn==1: #If AI turn, AI =1 always
                self.game.makeMove(self.ai.getMove(self.game, possMoves, 1))
                self.handler.showboard(self.game)
                continue
            command=self.handler.askForMove(self.game, possMoves) # If player turn
            if command=="end":
                playing=False
            else:
                self.game.makeMove(command)
                self.handler.showboard(self.game)

class AIvAIGame():
    def __init__(self,firstmove=0):
        self.handler=UIhandler()
        self.ai0=GameAI() #REMOVE hardcode part
        self.ai1=GameAI() #REMOVE hardcode part
        gameState={}
        for sq in range(3):
            for th in range(8):
                gameState[(sq,th)]="."
        self.game=MillGame(gameState,[], firstmove)
        self.play()

    def play(self):
        playing=True
        self.handler.showboard(self.game)
        print()
        while playing:
            possMoves=self.game.getPossMoves()
            if self.game.isWin0(possMoves): #checks p0 wins
                print("AI0 won the Game in "+ str(len(self.game.pastMoves)) + " moves")
                self.result, playing=0, False
                break
            if self.game.isWin1(possMoves): #checks p1 wins
                print("AI1 has won the Game in "+ str(len(self.game.pastMoves)) + " moves")
                self.result, playing=1, False
                break
            elif len(self.game.pastMoves)>200: #draw
                print("its a draw, 200 move limit exceeded")
                self.result, playing=0.5, False
                break
            if self.game.turn==0: #If AI0 turn 
                self.game.makeMove(self.ai0.getMove(self.game, possMoves, 0))
                self.handler.showboard(self.game)
                print()
            else: #if AI1 turn
                self.game.makeMove(self.ai1.getMove(self.game, possMoves, 1))
                self.handler.showboard(self.game)
                print()

class GameAI():
    def __init__(self, mode="optimized"): #mode: 0, 1, 2... , optimized, INSERT manual
        self.mode=mode
        self.depth=1
        self.score_double=1
        self.score_mill=1
        self.score_piece=1

    def getMove(self, game, possMoves, turn):
        depth=self.getDepth(game, possMoves)
        move=possMoves.pop(random.randint(0,len(possMoves)-1))
        temp_game=deepcopy(game)
        temp_game.makeMove(move)
        bestScore=self.minimax(temp_game, depth, temp_game.turn, temp_game.getPossMoves(), -10000, 10000)
        bestMove=move
        for move in possMoves:
            temp_game=deepcopy(game)
            temp_game.makeMove(move)
            temp_score=self.minimax(temp_game, depth, temp_game.turn, temp_game.getPossMoves(), -10000, 10000)
            if turn==0:
                if temp_score>bestScore:
                    bestMove=move
                    bestScore=temp_score
            elif turn==1:
                if temp_score<bestScore:
                    bestMove=move
                    bestScore=temp_score
        return bestMove

    def getDepth(self, game, possMoves): #TODO: optimize this depth function
        if self.mode in {0,1,2,3,4}:
            return self.mode
        elif self.mode=="optimized":
            gameLength=len(game.pastMoves)
            if gameLength==0:
                return 0
            elif gameLength<10:
                return 2
            elif gameLength<18:
                return 3
            else:
                numMoves=len(possMoves)
                if numMoves<10:
                    return 3
                else:
                    return 2



    def minimax(self, game, depth, turn, possMoves, alpha, beta): #returns minimax score with alpha-beta pruning
        if game.isWin1(possMoves):
            return -10000
        if game.isWin0(possMoves):
            return 10000
        if depth == 0:
            score=self.getScore(game, turn)
            return score
        if turn==0:
            score = -100000
            for move in possMoves:
                temp_game=deepcopy(game)
                temp_game.makeMove(move)
                score = max(score, self.minimax(temp_game, depth - 1, 1, temp_game.getPossMoves(), alpha, beta))
                alpha=max(alpha,score)
                if alpha>=beta:
                    break
            return score
        else: #turn=1
            score = 100000
            for move in possMoves:
                temp_game=deepcopy(game)
                temp_game.makeMove(move)
                score = min(score, self.minimax(temp_game, depth-1, 0, temp_game.getPossMoves(),alpha,beta))
                beta=min(beta,score)
                if beta <= alpha:
                    break
            return score
    
    def getScore(self, game, turn): #TODO: OPTIMIZE heuristic #returns heuristic score, 0s want positive, 1s want negative; turn not used, but could be in a different heuristic
        score=0
        num0=len(game.pieces[0])
        num1=len(game.pieces[1])

        score += (num0-num1)*self.score_piece #number of pieces INSERT to increase value of piece lead if there are less peices.
        for mill in game.mills: #adds to score for mills
            if mill[0]==0:
                score += self.score_mill
            elif mill[0]==1:
                score -= self.score_mill
        for triple in game.triples:
            count0=0
            count1=0
            for spot in triple:
                if game.gameState[spot]==0:
                    count0+=1
                elif game.gameState[spot]==1:
                    count1+=1
            if (count0, count1)==(2,0):
                score+=self.score_double
            elif (count0, count1)==(0,2):
                score-=self.score_double
        return score

AIvAIGame()
# TODO: reduce clutter, optimize heuristic, optimize depth function, make gui, improve AI based on paper



 