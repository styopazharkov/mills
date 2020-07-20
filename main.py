from copy import deepcopy
import random

PLAYER = 0
AI = 1 #clean up
FIRSTMOVE=AI

class MillGame():
    def __init__(self,gameState=None,moves=[],turn=0):
        if gameState==None:
            self.gameState={}
            for sq in range(3):
                for th in range(8):
                    self.gameState[(sq,th)]="."
        else:
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

        #update properties, MAYBE could be optimized so you dont have to recalculate
        self.pastMoves.append(move)
        self.mills=self.getMills(self.gameState)
        self.pieces=[self.getPieces(PLAYER),self.getPieces(AI)]
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
        if not removables:
            return enemyPieces
        else:
            return removables 

    def enemy(self,turn): #returns enemy
        if turn==AI:
            return PLAYER
        else:
            return AI

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

    def isWinPlayer(self,possMoves):
        if len(self.pastMoves)>=18 and self.turn==AI:
            if len(self.pieces[AI])<=2 or not possMoves:
                return True
        
        return False

    def isWinAI(self, possMoves):
        if len(self.pastMoves)>=18 and self.turn==PLAYER:
            if len(self.pieces[PLAYER])<=2 or not possMoves:
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
            # INSERT option for variation where you can move anywhere after 3 pieces left
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


class GameUI():
    def __init__(self, AIDEPTH1,SCOREDOUBLE1,SCOREMILL1,SCOREPIECE1, AIDEPTH2,SCOREDOUBLE2,SCOREMILL2,SCOREPIECE2, mode="manual"):
        
        self.mode=mode
        gameState={}
        for sq in range(3):
            for th in range(8):
                gameState[(sq,th)]="."
        # gameState[(0,1)]=PLAYER
        # gameState[(0,2)]=PLAYER
        # gameState[(0,4)]=PLAYER
        # gameState[(1,2)]=PLAYER
        # gameState[(2,2)]=AI
        # gameState[(2,5)]=AI
        # gameState[(2,6)]=AI
        self.game=MillGame(gameState,[], FIRSTMOVE)
        self.ai=GameAI(AIDEPTH1,SCOREDOUBLE1,SCOREMILL1,SCOREPIECE1) #1s, AI
        self.ai2=GameAI(AIDEPTH2,SCOREDOUBLE2,SCOREMILL2,SCOREPIECE2) #0s, PLAYER
        
        if self.mode=="auto":
            #print("playing automatically: ", end="")
            self.play()
        else:
            print("Wellcome to Mills, enter 'new' for a new game, 'end' to quit, 'help' for instructions")
            inp=input()
            while inp not in ["new", "end"]:
                if inp=="help":
                    print("INSERT help and rules here")
                else:
                    print("please enter valid command")
                inp=input()
            if inp=="new":
                self.play()
            elif inp=="end":
                print("bye")

    def play(self):
        #print("New Game of Mills")
        
        playing=True
        self.showboard()
        while playing:
            if self.mode!="auto":
                print("Player "+str(self.game.turn)+" to move")
            possMoves={}
            possMovesList=self.game.getPossMoves()
            for move in possMovesList:
                possMoves[str(move)]=move

            if self.game.isWinAI(possMoves):
                if self.mode!="auto":
                    print("AI1 has won the Game (1s)")
                else:
                    pass##
                    #print("1")##
                self.result=1
                playing=False
                break
            elif self.game.isWinPlayer(possMoves):
                self.result=0
                if self.mode!="auto":
                    print("AI2 have won the Game (0s)") 
                else:
                    pass#
                    #print("0")##
                playing=False
                break
            elif len(self.game.pastMoves)>200:
                self.result=0.5
                if self.mode!="auto":
                    print("its a draw")
                else:
                    pass##
                    #print("0.5")##
                playing=False
            #start ai2
            if self.game.turn==AI: #AI 1s turn (1s)
                self.game.makeMove(self.ai.getMove(self.game, possMovesList, self.game.turn))
                self.showboard()
                if self.mode!="auto":
                    print(self.ai.getScore(self.game, self.game.turn), end=" ")##
                    print(self.ai2.getScore(self.game, self.game.turn))##
            #end ai2
            elif self.game.turn==PLAYER: #AI 2s turn (0s)
                self.game.makeMove(self.ai2.getMove(self.game, possMovesList, self.game.turn))
                self.showboard()
                if self.mode!="auto":
                    print(self.ai.getScore(self.game, self.game.turn), end=" ") ##
                    print(self.ai2.getScore(self.game, self.game.turn)) ##
            else: #Players turn
                inp=input()
                if inp=="poss":
                    for key in possMoves.keys():
                        print(key, end=" ")
                    print()
                elif inp=="moves":
                    print(self.game.pastMoves)
                elif inp=="mills":
                    print(self.game.mills)
                elif inp=="pieces":
                    print(self.game.pieces)
                elif inp=="end":
                    print("bye")
                    playing=False
                elif inp=="help":
                    print("INSERT help and rules here")
                elif inp=="new":
                    #INSERT a new game function here
                    print("not a feature yet")
                elif inp in possMoves:
                    self.game.makeMove(possMoves[inp])
                    self.showboard()
                    print(self.ai.getScore(self.game))##
                else:
                    print("please enter valid command")

    def showboard(self): #prints gameboard
        if self.mode=="auto":
            return
        for th in [7,0,1]:
            print(self.game.gameState[0,th], end="     ")
        print()
        print(end="  ")
        for th in [7,0,1]:
            print(self.game.gameState[1,th], end="   ")
        print()
        print(end="    ")
        for th in [7,0,1]:
            print(self.game.gameState[2,th], end=" ")
        print()

        for sq in [0,1,2]:
            print(self.game.gameState[sq,6], end=" ")
        print(end="  ")
        for sq in [2,1,0]:
            print(self.game.gameState[sq,2], end=" ")
        print()

        print(end="    ")
        for th in [5,4,3]:
            print(self.game.gameState[2,th], end=" ")
        print()
        print(end="  ")
        for th in [5,4,3]:
            print(self.game.gameState[1,th], end="   ")
        print()
        for th in [5,4,3]:
            print(self.game.gameState[0,th], end="     ")
        print()


class GameAI():
    def __init__(self, depth, score_double, score_mill, score_piece):
        self.depth=depth
        self.score_double=score_double
        self.score_mill=score_mill
        self.score_piece=score_piece
    def getMove(self, game, possMoves, turn):
        move=random.choice(possMoves)
        temp_game=deepcopy(game)
        temp_game.makeMove(move)
        minScore=self.minimax(temp_game, self.depth, temp_game.turn, temp_game.getPossMoves(), -100000, 100000)
        bestMove=move
         #+infinity
        for move in possMoves:
            temp_game=deepcopy(game)
            temp_game.makeMove(move)
            temp_score=self.minimax(temp_game, self.depth, temp_game.turn, temp_game.getPossMoves(), -100000, 100000)
            if turn==AI:
                if temp_score<minScore:
                    bestMove=move
                    minScore=temp_score
            elif turn==PLAYER:
                if temp_score>minScore:
                    bestMove=move
                    minScore=temp_score
        return bestMove
    
    def minimax(self, game, depth, turn, possMoves, alpha, beta): #returns minimax score
        #INSERT TERMINAL NODE
        if game.isWinAI(possMoves):
            return -1000000
        if game.isWinPlayer(possMoves):
            return 1000000
        if depth == 0:
            score=self.getScore(game, turn)
            return score
        if turn==PLAYER:
            score = -100000
            for move in possMoves:
                temp_game=deepcopy(game)
                temp_game.makeMove(move)
                score = max(score, self.minimax(temp_game, depth - 1, AI, temp_game.getPossMoves(), alpha, beta))
                alpha=max(alpha,score)
                if alpha>=beta:
                    break
            return score
        else: #AI
            score = 100000
            for move in possMoves:
                temp_game=deepcopy(game)
                temp_game.makeMove(move)
                score = min(score, self.minimax(temp_game, depth-1, PLAYER, temp_game.getPossMoves(),alpha,beta))
                beta=min(beta,score)
                if beta <= alpha:
                    break
            return score
    
    def getScore(self, game, turn): #returns heuristic score
        
        score=0
        aiNum=len(game.pieces[AI])
        playerNum=len(game.pieces[PLAYER])
        score -= (aiNum-playerNum)*self.score_piece #number of pieces INSERT to increase value of piece lead if there are less peices.
        for mill in game.mills: #adds to score for mills
            if mill[0]==AI:
                score -= self.score_mill
            elif mill[0]==PLAYER:
                score += self.score_mill
        for triple in game.triples:
            countPlayer=0
            countAI=0
            for spot in triple:
                if game.gameState[spot]==AI:
                    countAI+=1
                elif game.gameState[spot]==PLAYER:
                    countPlayer+=1
            if (countPlayer, countAI)==(0,2):
                score-=self.score_double
            elif (countPlayer, countAI)==(2,0):
                score+=self.score_double
        return score


# TODO: reduce clutter, check runtime, balance score, make gui

def runtest(depth1,double1,mill1,piece1,depth2,double2,mill2,piece2): #wins out of 100
    print("starting runtest . . .")
    # AIDEPTH1 = depth1 #AI1 1s, AI, negatives, first, highr game sum
    # SCOREDOUBLE1 = double1
    # SCOREMILL1 = mill1
    # SCOREPIECE1 = piece1

    # AIDEPTH2 = depth2 #AI2 0s, PLAYER, positives, second, lower game sum
    # SCOREDOUBLE2 = double2
    # SCOREMILL2 = mill2
    # SCOREPIECE2 = piece2
    result=0
    for i in range(50):
        result+=GameUI(depth1, double1, mill1, piece1, depth2, double2, mill2, piece2, "auto").result
        if (i+1)%10==0:
            print(str(result)+ " out of " + str(i+1))
    result2=0
    print("switch")
    for i in range(50):
        result2+=GameUI(depth2, double2, mill2, piece2, depth1, double1, mill1, piece1, "auto").result
        if (i+1)%10==0:
            print(str(i+1-result2)+ " out of " + str(i+1))
    print(result+50-result2)
    return result+result2
    print("End of runtest")

GameUI(2,1,1,1,1,1,1,1)
#runtest(2,1,1,1,2,2,3,15)
#assuming that pice is more valuable than mill and mill is more valuable than piece; no value change throughout the game (MAYBE change this)
# depth=1
# double=1
# factor1=1
# factor2=1
# for _ in range(10):
#     _factor1=1.26**random.randint(0,10)
#     _factor2=1.26**random.randint(0,10)
#     mill=double*factor1
#     piece=mill*factor2
#     _mill=double*_factor1
#     _piece=_mill*_factor2
#     print((double,mill,piece,_mill,_piece))
#     if runtest(depth,double,mill,piece,depth,double,_mill,_piece)<40:
#         factor1, factor2 = _factor1, _factor2
#         print("success")
 