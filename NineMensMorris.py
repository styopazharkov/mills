#VERSION 0.1.10


from copy import deepcopy
import random
import pygame, sys
from collections import defaultdict



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
        self.mills=self.getMills(self.gameState) #mills of the form [turn, [(sq,th),(sq,th),(sq,th)]]
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
        self.pieces=[self.getPieces(0),self.getPieces(1)] #SHOULD be optimized so you dont have to recalculate
        self.turn=self.enemy(self.turn)
    
    def undo(self):
        if self.pastMoves:
            previousMove=self.pastMoves.pop()
            self.turn=self.enemy(self.turn)
            if previousMove[0]=="place":
                self.gameState[previousMove[1]]="."
            elif previousMove[0]=="placer":#["placer", piece, removable]
                self.gameState[previousMove[2]]=self.enemy(self.turn)
                self.gameState[previousMove[1]]="."
            elif previousMove[0]=="move":#["move", piece, neighbor]
                self.gameState[previousMove[2]]="."
                self.gameState[previousMove[1]]=self.turn
            elif previousMove[0]=="mover":#["mover", piece, neighbor, removable]
                self.gameState[previousMove[1]]=self.turn
                self.gameState[previousMove[2]]="."
                self.gameState[previousMove[3]]=self.enemy(self.turn)
            self.mills=self.getMills(self.gameState) #MAYBE could be optimized so you dont have to recalculate
            self.pieces=[self.getPieces(0),self.getPieces(1)] #SHOULD be optimized so you dont have to recalculate

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

class GameAI():
    def __init__(self, depthMode="optimized", score_double=10, score_mill=10, score_piece=10, score_conn=1): #mode: 0, 1, 2... , time_optimized
        self.mode=depthMode
        self.score_double=score_double
        self.score_mill=score_mill
        self.score_piece=score_piece
        self.score_conn=score_conn

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
                return 3
            elif gameLength<18:
                return 4
            else:
                numMoves=len(possMoves)
                if numMoves<10:
                    return 5
                else:
                    return 4

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
        for triple in game.triples: #add to score for doubles
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

        for spot0 in game.pieces[0]: #add to score for open neighbor spots 0
            for neighbor in game.connections[spot0]:
                if game.gameState[neighbor]==".":
                    score+=self.score_conn

        for spot1 in game.pieces[1]: #add to score for open neighbor spots 1
            for neighbor in game.connections[spot1]:
                if game.gameState[neighbor]==".":
                    score-=self.score_conn

        return score

class GUI():
    def __init__(self):
        pygame.init()
        self.aidStatus=""
        self.clock = pygame.time.Clock()
        self.unit=60
        self.WIN_WIDTH = 800
        self.WIN_HEIGHT = 600
        self.winCenter=(self.WIN_WIDTH//2,self.WIN_HEIGHT//2)
        self.boardCenter=(self.WIN_WIDTH//3,self.WIN_HEIGHT*4//7)
        self.spotDict=self.makeSpotDict()
        self.win = pygame.display.set_mode((self.WIN_WIDTH, self.WIN_HEIGHT))
        self.pressedButtons=defaultdict(lambda: False)
        self.highlighted=defaultdict(list) #highlighted spots based on number of moves
        pygame.display.set_caption("Nine Mens Morris")
        self.introLoop()
        
        pygame.quit()
        sys.exit()
    #LOOPS:
    def introLoop(self): #loop for intro
        self.mode="PvP"
        self.startBlankGame()
        gameOn = True 
        while gameOn:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.win.fill((255,255,255))
            self.createText("Welcome to Nine Mens Morris",self.WIN_WIDTH//2,self.WIN_HEIGHT*1//3,45,(0,0,0))
            self.createButton("new", "New Game",180,350,150,70, (170,170,170), (140,140,140), 20, self.loopReturn, "mode_select")
            self.createButton("rules", "Rules",470,350,150,70, (170,170,170), (140,140,140), 20, self.loopReturn, "rules_from_intro")
            #Add a ability to make custom game board
            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()
    
    def rulesLoop(self, loop):
        gameOn = True 
        while gameOn:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.win.fill((255,255,255))
            self.createText("Red always moves first.",self.WIN_WIDTH//2,self.WIN_HEIGHT//7,35,(0,0,0))
            self.createButton( "back", "back", 320,290,200,100, (170,170,170), (140,140,140), 23, self.loopReturn, loop)
            pygame.display.update()
            self.clock.tick(60)
        return

    def winLoop(self, winner):
        self.aidStatus=""
        gameOn = True 
        while gameOn:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.win.fill((255,255,255))
            if winner==0:
                text, color= "Red has won the game!", (200,0,0)
            elif winner==1:
                text, color= "Blue has won the game!", (0,0,200)
            else:
                text, color= "200 moves made: it's a Draw!", (0,0,0)

            self.drawBoard()
            self.drawPieces(self.game)
            self.createText(text,self.WIN_WIDTH//2,self.WIN_HEIGHT//7,35,color)
            self.createButton( "again", "Play Again", 520,450,200,50, (170,170,170), (140,140,140), 23, self.loopReturn, "intro")
            pygame.display.update()
            self.clock.tick(60)
        return

    def playLoop(self):
        looping=True
        while looping:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.aidStatus="thinking"
            self.win.fill((255,255,255))
            self.drawBoard()
            self.drawPieces(self.game)

            #create threads for buttons while ai is thinking

            pygame.display.update()
            self.clock.tick(60)

            possMoves= self.game.getPossMoves()
            if self.game.isWin0(possMoves): #checks p0 wins
                self.winLoop(0)
            elif self.game.isWin1(possMoves): #checks p1 wins 
                self.winLoop(1)
            elif len(self.game.pastMoves)>200: #draw 
                self.winLoop(0.5)
            if self.game.turn==0:
                if self.mode in {"AIvAI", "AIvP"}:
                    move=self.ai.getMove(self.game, possMoves, self.game.turn)
                    self.updateHighlighted(move)
                    self.game.makeMove(move)
                else:
                    move=self.waitForMoveLoop(possMoves)
                    self.updateHighlighted(move)
                    self.game.makeMove(move)
            else: #turn =1
                if self.mode in {"AIvAI", "PvAI"}:
                    move=self.ai.getMove(self.game, possMoves, self.game.turn)
                    self.updateHighlighted(move)
                    self.game.makeMove(move)
                else:
                    move=self.waitForMoveLoop(possMoves)
                    self.updateHighlighted(move)
                    self.game.makeMove(move)
    def modeSelectLoop(self):
        looping = True 
        while looping:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.win.fill((255,255,255))
            self.createText("Please select game mode",self.WIN_WIDTH//2,self.WIN_HEIGHT//4,45,(0,0,0))
            self.createButton("back", "Exit", self.WIN_WIDTH-105,5,100,30, (170,170,170), (140,140,140), 20, self.loopReturn, "intro")
            self.createButton( "pvp", "Human vs. Human", 200,200,400,60, (170,170,170), (140,140,140), 20, self.loopReturn, "play")
            self.createButton("pvai","Human vs. Computer", 200,270,400,60, (170,170,170), (140,140,140), 20, self.loopReturn, "ai_select_in_pvai")
            self.createButton("aivp","Computer vs. Human", 200,340,400,60, (170,170,170), (140,140,140), 20, self.loopReturn, "ai_select_in_aivp")
            self.createButton("aivai", "Computer vs. Computer",  200,410,400,60, (170,170,170), (140,140,140), 20, self.loopReturn, "ai_select_in_aivai")
            pygame.display.update()
            self.clock.tick(60)
        return

    def waitForMoveLoop(self, possMoves): #SHOULD return the move that the human wants to make

        def incrementA(a,colorTrend): #changes the possmovecolor
            if colorTrend=="+":
                if a>200:
                    return a, "-"
                else:
                    return a+1.5, "+"
            else:
                if a<102:
                    return a, "+"
                else:
                    return a-1.5, "-"
        
        def getSpot(mouse, possMoves, index):
            for possMove in possMoves:
                location=self.spotDict[possMove[index]]
                if -self.unit//2<location[0]-mouse[0]<self.unit//2 and -self.unit//2<location[1]-mouse[1]<self.unit//2:
                    return possMove
            return False

        def drawPossSpots(a, spots): #also draws buttons
            self.win.fill((255,255,255))
            self.drawBoard()
            self.drawPieces(temp_game)
            self.createButton("exit","Exit Game", self.WIN_WIDTH-125,5,120,30, (170,170,170), (140,140,140), 20, self.loopReturn, "intro")
            self.createButton("rules","Rules", self.WIN_WIDTH//2-50,5,100,20, (170,170,170), (140,140,140), 15, self.loopReturn, "rules_from_move")
            self.createButton("chmod","Change Mode", 5,5,145,30, (170,170,170), (140,140,140), 20, self.loopReturn, "mode_select")
            if self.mode!="PvP":
                self.createButton("chdiff","Change Difficulty", 155,5,185,30, (170,170,170), (140,140,140), 20, self.loopReturn, "ai_select")
            if self.mode!="AIvAI":
                self.createButton("undo","Undo", self.WIN_WIDTH-205,5,75,30, (170,170,170), (140,140,140), 20, self.loopReturn, "undo")
            #add change ai diff button
            #add change mode button
            for spot in spots:
                occupant=temp_game.gameState[spot]
                if occupant==0: #red, 0
                    pygame.draw.circle(self.win, (255,a,a), self.spotDict[spot], 10)
                elif occupant==1: # blue, 1
                    pygame.draw.circle(self.win, (a,a,255), self.spotDict[spot], 10) 
                elif temp_game.turn==0: # occupant= ".", turn=0, red
                    pygame.draw.circle(self.win, (a,100,100), self.spotDict[spot], 10)
                else:  # occupant= ".", turn=1, blue
                    pygame.draw.circle(self.win, (100,100,a), self.spotDict[spot], 10)

        def waitForPlacerMove(placed, possMoves): #returns 'placer' move if selected first placed spot forms a mill
            a, colorTrend=100, "+"
            possMoves=[move for move in possMoves if move[1]==placed]
            possSpots=[move[2] for move in possMoves]
            temp_game.gameState[placed]=temp_game.turn
            temp_game.pieces=[temp_game.getPieces(0),temp_game.getPieces(1)] #SHOULD be optimized so you dont have to recalculate
            temp_game.mills=temp_game.getMills(temp_game.gameState)
            if temp_game.turn==0:
                self.aidStatus="rplacer"
            else: #turn=1, blue
                self.aidStatus="bplacer"
            while True: #wait loop
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse = pygame.mouse.get_pos()
                        spot=getSpot(mouse, possMoves, 2)
                        if spot:
                            return spot
                
                drawPossSpots(a, possSpots)
                pygame.display.update()
                self.clock.tick(60)
                a, colorTrend = incrementA(a, colorTrend)

        def waitForPlaceMove(possMoves): #waits until a move is made that places a peice. returns the move is it is 'place' type. calls waitForPl
            a, colorTrend=100, "+"
            possSpots=[move[1] for move in possMoves]
            if temp_game.turn==0:
                self.aidStatus="rplace"
            else: #turn=1, blue
                self.aidStatus="bplace"
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse = pygame.mouse.get_pos()
                        spot=getSpot(mouse, possMoves, 1)
                        if spot:
                            if spot[0]=="placer":
                                return waitForPlacerMove(spot[1], possMoves)
                            else:
                                return spot

                drawPossSpots(a, possSpots)
                pygame.display.update()
                self.clock.tick(60)
                a, colorTrend = incrementA(a, colorTrend)

        def waitForMoveMoveStart(possMoves): #waits until a start spot is selected during the moving phase
            a, colorTrend=100, "+"
            possSpots=[move[1] for move in possMoves]
            if temp_game.turn==0:
                self.aidStatus="rstartmove"
            else: #turn=1, blue
                self.aidStatus="bstartmove"
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse = pygame.mouse.get_pos()
                        spot=getSpot(mouse, possMoves, 1)
                        if spot:
                            return waitForMoveMoveEnd(spot[1], possMoves)

                drawPossSpots(a, possSpots)
                pygame.display.update()
                self.clock.tick(60)
                a, colorTrend = incrementA(a, colorTrend)

        def waitForMoveMoveEnd(start, possMoves): #waits until an end spot is selected during movng phase
            a, colorTrend=100, "+"
            possMoves=[move for move in possMoves if move[1]==start]
            possSpots=[move[2] for move in possMoves]

            if temp_game.turn==0:
                self.aidStatus="rendmove"
            else: #turn=1, blue
                self.aidStatus="bendmove"
            temp_game.gameState[start]="." #NEED to add so that start spot is 'selected' somehow
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse = pygame.mouse.get_pos()
                        spot=getSpot(mouse, possMoves, 2)
                        if spot:
                            if spot[0]=="mover":
                                return waitForMoverMove(spot[2], possMoves)
                            else:
                                return spot

                drawPossSpots(a, possSpots)
                pygame.display.update()
                self.clock.tick(60)
                a, colorTrend = incrementA(a, colorTrend)

        def waitForMoverMove(end, possMoves):  #waits until removable is selected if a mill is formed by a move move
            a, colorTrend=100, "+"
            possMoves=[move for move in possMoves if move[2]==end]
            possSpots=[move[3] for move in possMoves]

            temp_game.gameState[end]=temp_game.turn #makes sure 
            temp_game.mills=temp_game.getMills(temp_game.gameState)
            temp_game.pieces=[temp_game.getPieces(0),temp_game.getPieces(1)]

            if temp_game.turn==0:
                self.aidStatus="rmover"
            else: #turn=1, blue
                self.aidStatus="bmover"

            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse = pygame.mouse.get_pos()
                        spot=getSpot(mouse, possMoves, 3)
                        if spot:
                            return spot

                drawPossSpots(a, possSpots)
                pygame.display.update()
                self.clock.tick(60)
                a, colorTrend = incrementA(a, colorTrend)

        temp_game=deepcopy(self.game)
        if len(self.game.pastMoves)<18:
            return waitForPlaceMove(possMoves)
        else:
            return waitForMoveMoveStart(possMoves)
    
    def aiDiffSelectLoop(self):
        looping = True 
        while looping:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.win.fill((255,255,255))
            self.createText("Please select computer difficulty",self.WIN_WIDTH//2,self.WIN_HEIGHT//4,45,(0,0,0))
            self.createButton("back", "Mode Select", self.WIN_WIDTH-145,5,140,30, (170,170,170), (140,140,140), 20, self.loopReturn, "mode_select")
            self.createButton( "easy", "Easy", 200,200,400,60, (170,170,170), (140,140,140), 20, self.loopReturn, "play_in_diff0")
            self.createButton("ok", "Okay", 200,270,400,60, (170,170,170), (140,140,140), 20, self.loopReturn, "play_in_diff1")
            self.createButton("decent","Decent", 200,340,400,60, (170,170,170), (140,140,140), 20, self.loopReturn, "play_in_diff2")
            self.createButton("good", "Strong",  200,410,400,60, (170,170,170), (140,140,140), 20, self.loopReturn, "play_in_diffOptimized")
            pygame.display.update()
            self.clock.tick(60)
        return

    def loopReturn(self, loop): #cotrols which loop to run
        if loop=="intro":
            self.introLoop()
        elif loop=="rules_from_intro":
            self.rulesLoop("intro")
        elif loop=="rules_from_move":
            self.rulesLoop("play")
        elif loop=="mode_select":
            self.modeSelectLoop()
        elif loop=="ai_select":
            self.aiDiffSelectLoop()
        elif loop=="ai_select_in_pvai":
            self.mode="PvAI"
            self.aiDiffSelectLoop()
        elif loop=="ai_select_in_aivp":
            self.mode="AIvP"
            self.aiDiffSelectLoop()
        elif loop=="ai_select_in_aivai":
            self.mode="AIvAI"
            self.aiDiffSelectLoop()
        elif loop=="play_in_diff0":
            self.ai=GameAI(0)
            self.playLoop()
        elif loop=="play_in_diff1":
            self.ai=GameAI(1)
            self.playLoop()
        elif loop=="play_in_diff2":
            self.ai=GameAI(2)
            self.playLoop()
        elif loop=="play_in_diffOptimized":
            self.ai=GameAI()
            self.playLoop()
        elif loop=="play":
            self.playLoop()
        elif loop=="undo":
            self.undo()
            self.playLoop()
        else:
            print("ERROR: not a loop")

    #endLOOPS
    #HELPERS

    def updateHighlighted(self, move):
        if move[0]=="place":
            self.highlighted[len(self.game.pastMoves)]=[move[1]]
        elif move[0]=="placer":
            self.highlighted[len(self.game.pastMoves)]=[move[1], move[2]]
        elif move[0]=="move":
            self.highlighted[len(self.game.pastMoves)]=[move[1], move[2]]
        elif move[0]=="mover":
            self.highlighted[len(self.game.pastMoves)]=[move[1], move[2], move[3]]


    def makeSpotDict(self): #creates dict with all the spots
        dic={}
        for sq in range(3):
            for th in range(8):
                if th==0:
                    dic[(sq,th)]=(self.boardCenter[0],self.boardCenter[1]-self.unit*(3-sq))
                elif th==1:
                    dic[(sq,th)]=(self.boardCenter[0]+self.unit*(3-sq),self.boardCenter[1]-self.unit*(3-sq))
                elif th==2:
                    dic[(sq,th)]=(self.boardCenter[0]+self.unit*(3-sq),self.boardCenter[1])
                elif th==3:
                    dic[(sq,th)]=(self.boardCenter[0]+self.unit*(3-sq),self.boardCenter[1]+self.unit*(3-sq))
                elif th==4:
                    dic[(sq,th)]=(self.boardCenter[0],self.boardCenter[1]+self.unit*(3-sq))
                elif th==5:
                    dic[(sq,th)]=(self.boardCenter[0]-self.unit*(3-sq),self.boardCenter[1]+self.unit*(3-sq))
                elif th==6:
                    dic[(sq,th)]=(self.boardCenter[0]-self.unit*(3-sq),self.boardCenter[1])
                elif th==7:
                    dic[(sq,th)]=(self.boardCenter[0]-self.unit*(3-sq),self.boardCenter[1]-self.unit*(3-sq))
        return dic

    def startBlankGame(self): #starts a blank game
        gameState={}
        for sq in range(3):
            for th in range(8):
                gameState[(sq,th)]="."
        self.game=MillGame(gameState,[])

    def undo(self): #undos last move, does nothing if no previous move
        if self.mode=="PvP":
            self.game.undo()
        elif self.mode in {"PvAI", "AIvP"}:
            self.game.undo()
            self.game.undo()

    #endHELPERS
    #CREATORS/DRAWERS

    def createText(self, text, x, y, size, color): #creates a line of text
        font = pygame.font.Font('freesansbold.ttf',size)
        TextSurf, TextRect = self.text_objects(text, font, color)
        TextRect.center = (x,y)
        self.win.blit(TextSurf,TextRect)

    def createButton(self, name, text, left, top, width, height, inactiveColor, activeColor, fontSize, action=None, arg=None): #creates a clickable button, calls action on release
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if left<mouse[0]<left+width and top<mouse[1]<top+height:
            self.drawRoundedRect(self.win, activeColor, (left,top,width,height), 7) #if mouse is over button
            if click[0]==1 and action!=None:
                self.pressedButtons[name]=True
            if click[0]==0 and action!=None and self.pressedButtons[name]==True:
                self.pressedButtons[name]=False
                if arg!=None:
                    action(arg)
                else:
                    action()
        else:
            self.drawRoundedRect(self.win, inactiveColor, (left,top,width,height),7)  #if mouse not over button
            self.pressedButtons[name]=False
        self.createText(text, left+width//2, top+height//2, fontSize, (0,0,0))#draw button
    
    def text_objects(self, text, font, color): #creates a pair for text objects
        textSurface = font.render(text, True, color)
        return textSurface, textSurface.get_rect()
    
    def drawBoard(self): #draws the game board, key, and AI
        for sq in range(3): #draws spots
            for th in range(8):
                 pygame.draw.circle(self.win, (100,100,100), self.spotDict[(sq,th)], 20)

        for triple in self.game.triples: #draws edges
            end1=self.spotDict[triple[0]]
            end2=self.spotDict[triple[2]]
            pygame.draw.line(self.win, (100,100,100), end1, end2, 14)

        self.drawKey() #clean up (?) with drawEverything fun
        self.drawAid() #^^^

    def drawPieces(self, game): #draws the pieces of a given game, also connects mills and highlights past moves
        for piece in game.pieces[0]: #red player 0
            pygame.draw.circle(self.win, (255,0,0), self.spotDict[piece], 14)

        for piece in game.pieces[1]: #blue. player 1
            pygame.draw.circle(self.win, (0,0,255), self.spotDict[piece], 14)

        for mill in game.mills:
            if mill[0]==0: #red mill
                pygame.draw.line(self.win, (255,0,0), self.spotDict[mill[1][0]], self.spotDict[mill[1][2]], 6)
            else: #blue mill
                pygame.draw.line(self.win, (0,0,255), self.spotDict[mill[1][0]], self.spotDict[mill[1][2]], 6)
            
        self.drawSpotHighlights(self.highlighted[len(self.game.pastMoves)-1])

    def drawKey(self): #draws the key to the side of the game board
        pygame.draw.circle(self.win, (100,100,100), (self.WIN_WIDTH*6//9,self.WIN_HEIGHT*4//7-40), 14)
        pygame.draw.circle(self.win, (255,10,10), (self.WIN_WIDTH*6//9,self.WIN_HEIGHT*4//7-40), 10)
        pygame.draw.circle(self.win, (100,100,100), (self.WIN_WIDTH*6//9,self.WIN_HEIGHT*4//7+20), 14)
        pygame.draw.circle(self.win, (10,10,255), (self.WIN_WIDTH*6//9,self.WIN_HEIGHT*4//7+20), 10)
        if self.mode in {"PvP", "PvAI"}:
            text1="- Human  "
        else:
            text1="  - Computer"
        if self.mode in {"PvP", "AIvP"}:
            text2="- Human  "
        else:
            text2="  - Computer"
            #show the ai difficulty
        self.createText(text1,self.WIN_WIDTH*6//9+70,self.WIN_HEIGHT*4//7-40,20,(0,0,0))
        self.createText(text2,self.WIN_WIDTH*6//9+70,self.WIN_HEIGHT*4//7+20,20,(0,0,0))

    def drawAid(self): #draws text above the board that helps 
        
        text=""
        if self.aidStatus=="thinking":
            text = "Computer thinking..."
        elif self.aidStatus=="rplace":
            text = "Red's turn: select a spot"
        elif self.aidStatus=="bplace":
            text = "Blue's turn: select a spot"
        elif self.aidStatus=="rplacer":
            text = "Reds's turn: select a blue piece to remove"
        elif self.aidStatus=="bplacer":
            text = "Blue's turn: select a red piece to remove"
        elif self.aidStatus=="rstartmove":
            text = "Red's turn: select a piece to move"
        elif self.aidStatus=="bstartmove":
            text = "Blue's turn: select a piece to move"
        elif self.aidStatus=="rendmove":
            text = "Reds's turn: select a spot to move to"
        elif self.aidStatus=="bendmove":
            text = "Blue's turn: select a spot to move to"
        elif self.aidStatus=="rmover":
            text = "Reds's turn: select a blue piece to remove"
        elif self.aidStatus=="bmover":
            text = "Blue's turn: select a red piece to remove"
        if text:
            self.createText(text,self.WIN_WIDTH//2,self.WIN_HEIGHT//7,22, (0,0,0))

    def drawRoundedRect(self, win, color, dims, radius): #draws a rounded rectangle; dims: (left,top,width,height)
        pygame.draw.rect(win, color, (dims[0]+radius, dims[1]+radius, dims[2]-2*radius, dims[3]-2*radius))
        for spot in [(dims[0]+radius,dims[1]+radius),(dims[0]+radius,dims[1]+dims[3]-radius),(dims[0]+dims[2]-radius,dims[1]+radius),(dims[0]+dims[2]-radius,dims[1]+dims[3]-radius)]:
            pygame.draw.circle(win, color, spot, radius)
        for pair in [[(dims[0]+radius-1,dims[1]+radius-1),(dims[0]+radius-1,dims[1]+dims[3]-radius)],[(dims[0]+radius-1,dims[1]+radius-1),(dims[0]+dims[2]-radius,dims[1]+radius-1)],[(dims[0]+dims[2]-radius,dims[1]+radius-1),(dims[0]+dims[2]-radius,dims[1]+dims[3]-radius)],[(dims[0]+dims[2]-radius,dims[1]+dims[3]-radius),(dims[0]+radius-1,dims[1]+dims[3]-radius)]]:
            pygame.draw.line(win, color, pair[0], pair[1], radius*2)

    def drawSpotHighlights(self, spots):
        for spot in spots:
            pygame.draw.circle(self.win, (255,255,0), self.spotDict[spot], 16, 2)
    #endCREATORS/DRAWERS

if __name__ == "__main__":
    GUI()

# TODO ai: reduce clutter; optimize heuristic (?); optimize depth function, make so that ai tries to win in less moves if it can
# TODO GUI: add ability to make custom game start, multithread the GUI and comp, write help page, create drawEverything function, hint button, settings, animate moves



 