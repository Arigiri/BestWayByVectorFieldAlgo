import pygame
from math import *

class Block:
    def __init__(self, position : tuple, size : int) -> None:
        self.position = position
        self.size = size
        self.type = "None"
        self.dist = 0
        self.visited = False
        self.Vector = (0, 0)
        self.center = (size // 2 + self.position[0] * self.size, size // 2 + self.position[1] * self.size)
        pass

    def show(self, surface : pygame.Surface, O : tuple) -> None:
        position = (self.position[0] * self.size + O[0], self.position[1] * self.size + O[1])
        pygame.draw.rect(surface, (0,0,0), pygame.Rect(position[0], position[1], self.size, self.size), 1)
        if self.type == "Wall":
            pygame.draw.rect(surface, (100, 100, 100), pygame.Rect(position[0] + 1, position[1] + 1, self.size - 2, self.size - 2))
        elif self.type == "Main":
            pygame.draw.circle(surface, (0, 0, 255), (position[0] + self.size//2, position[1] + self.size//2), self.size//2 - 2)
        elif self.type == "Sub":
            pygame.draw.circle(surface, (0, 255, 0), (position[0] + self.size//2, position[1] + self.size//2), self.size//2 - 2)
        if self.visited == False or self.type == "Wall" or (self.type != "Main" and self.dist == 0  ):#or self.type != "None":
            return
        
        font = pygame.font.Font('freesansbold.ttf', 10)
        text = font.render(str(self.dist), True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (position[0] + self.size // 2, position[1] + self.size//2)
        
        
        # distRect = pygame.draw.rect(surface, (255, 0, 0), pygame.Rect(position[0] + 1, position[1] + 1, self.size - 2, self.size - 2))
        distRect = pygame.Rect(position[0] + 1, position[1] + 1, self.size - 2, self.size - 2)
        SurfaceRect = pygame.Surface(distRect.size, pygame.SRCALPHA)
        
        alpha = max((-200 // 16) * self.dist + 200, 0)
        pygame.draw.rect(SurfaceRect, ((255, 0, 0, alpha)), SurfaceRect.get_rect())
        surface.blit(SurfaceRect, distRect)
        pygame.draw.line(surface, (0, 0, 0), (position[0] + self.size/2, position[1] + self.size / 2) ,  (position[0] + self.size * self.Vector[0] // 2 + self.size/2, position[1] + self.size * self.Vector[1] //2 + self.size/2))
        surface.blit(text, textRect) 
        
        if self.type == "Wall":
            pygame.draw.rect(surface, (100, 100, 100), pygame.Rect(position[0] + 1, position[1] + 1, self.size - 2, self.size - 2))
        elif self.type == "Main":
            pygame.draw.circle(surface, (0, 0, 255), (position[0] + self.size//2, position[1] + self.size//2), self.size//2 - 2)
        elif self.type == "Sub":
            pygame.draw.circle(surface, (0, 255, 0), (position[0] + self.size//2, position[1] + self.size//2), self.size//2 - 2)

class Particle:
    def __init__(self, position : tuple) -> None:
        self.position = position
        self.dir = (0, 0)
        self.r = 5
        self.speed = 3
        self.IsMovedToCenter = False
        self.CurBlock = ""
        self.NextBlock = ""
        pass
    
    def show(self, surface : pygame.Surface) -> None:
        pygame.draw.circle(surface, (0, 255, 255), self.position, self.r)
        pass
    
    def GetCurrBlockPos(self, game) -> tuple:
        x = self.position[0] // game.BlockSize
        y = self.position[1] // game.BlockSize
        return (x, y)
    
    def GetBlock(self, game, position) -> Block:
        return game.BlockTrace[position]
    
    def dist(self, v1, v2) -> float:
        x = v2[0] - v1[0]
        y = v2[0] - v1[0]
        return (x * x + y * y) ** (1/2)
    
    def normalize(self, vector) -> tuple:
        x = vector[0]
        y = vector[1]
        dt = (x * x + y * y) ** (1/2)
        if dt == 0:
            return (1, 1)
        x /= dt
        y /= dt
        return (x, y)
    
    def Update(self, game) -> None:
        curBlockPosition = self.GetCurrBlockPos(game)
        block = self.GetBlock(game, curBlockPosition)
        NextBlock = self.GetBlock(game, (block.position[0] + block.Vector[0], block.position[1] + block.Vector[1]))
        if block.type == "Wall":
            self.Move()
            return
        if self.NextBlock == "":
            self.NextBlock = NextBlock
        if self.IsMovedToCenter == False:
            self.dir = (NextBlock.center[0] - self.position[0], NextBlock.center[1] - self.position[1])
            self.dir = self.normalize(self.dir)
            if self.dist(self.NextBlock.center, self.position) < 1:
                self.IsMovedToCenter = True
        else:
            self.NextBlock = NextBlock
            self.IsMovedToCenter = False
        self.Move()
        pass
    
    def Move(self) -> None:
        self.position = (self.position[0] + self.dir[0] * self.speed, self.position[1] + self.dir[1] * self.speed)

class Game:
    def __init__(self, O = (0, 0)) -> None:
        pygame.init()
        #create screen
        self.width = 600
        self.heigth = 600
        self.canvas = pygame.display.set_mode((self.width, self.heigth))
        self.running = True
        self.mousePos = (-1, -1)
        self.OnMouseClick = False
        self.ClickType = 0
        self.O = O
        #Config map
        self.BlockSize = 30
        self.MapSize = (self.width//self.BlockSize, self.heigth//self.BlockSize)
        #Create Map
        self.BlockList = []
        self.BlockTrace = {}
        self.WallList = []
        self.Main = (-1, -1)
        self.Graph = {}
        self.NeedUpdateHeatmap = False
        for y in range(0, self.heigth, self.BlockSize):
            for x in range(0, self.width, self.BlockSize):
                newBlock = Block((x//self.BlockSize, y//self.BlockSize), self.BlockSize)
                self.BlockList.append(newBlock)
                self.BlockTrace[newBlock.position] = newBlock
        self.OldMain = self.BlockList[0]
        #Create particles
        self.ParticlesList = []
    
    def eventUpdate(self) -> None:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONUP:
                self.mousePos = pygame.mouse.get_pos()
                self.OnMouseClick = True
                self.ClickType = event.button
                if event.button == 3:
                    self.NeedUpdateHeatmap = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.CreateGraph()
    
    def draw(self) -> None:
        pygame.draw.rect(self.canvas, (255, 255, 255), pygame.Rect(0, 0, self.width, self.heigth))
        for block in self.BlockList:
            block.show(self.canvas, (0, 0))
        for particle in self.ParticlesList:
            particle.show(self.canvas)
        pygame.display.flip()
    
    def update(self) -> None:
        self.eventUpdate()
        self.draw()
        self.CreateWall()
        if self.NeedUpdateHeatmap == True:
            if self.Graph == {}:
                self.CreateGraph()
            else:
                self.CreateHeatmap()
            self.NeedUpdateHeatmap = False
        #update Particles
        for particle in self.ParticlesList:
            particle.Update(self) 
        
    def convertMousePosToBlockPos(self) -> tuple:
        return (self.mousePos[0]//self.BlockSize, self.mousePos[1]//self.BlockSize)
    
    def CreateWall(self):
        if self.OnMouseClick:
            newPos = self.convertMousePosToBlockPos()
            #find block
            block = self.BlockTrace[newPos]
            if block.type != "None":
                if(block.type == "Wall"):
                    self.WallList.remove(newPos)
                elif block.type == "Sub":
                    self.ParticlesList.remove(newPos)
                elif block.type == "Main":
                    self.Main = (-1, -1)
                block.type = "None"
            elif self.ClickType == 1:
                print(newPos)
                block.type = "Wall"
                self.WallList.append(newPos)
            elif self.ClickType == 3:
                self.OldMain.type = "None"
                block.type = "Main"
                self.Main = newPos
                self.OldMain = block
            elif self.ClickType == 2:
                particle = Particle(self.mousePos)
                self.ParticlesList.append(particle)
            self.OnMouseClick = False
    
    def CreateGraph(self) -> None:
        self.Graph = {} 
        for block in self.BlockList:
            if block.type == "Wall":
                continue
            if self.Graph.get(block) == None:
                self.Graph[block] = []
            position = block.position
            if self.BlockTrace.get((position[0] + 1, position[1])) != None:
                newblock = self.BlockTrace[(position[0] + 1, position[1])]
                if newblock.type != "Wall":
                    self.Graph[block].append(newblock)
            
            if self.BlockTrace.get((position[0] - 1, position[1])) != None:
                newblock = self.BlockTrace[(position[0] - 1, position[1])]
                if newblock.type != "Wall":
                    self.Graph[block].append(newblock)
                
            if self.BlockTrace.get((position[0], position[1] + 1)) != None:
                newblock = self.BlockTrace[(position[0], position[1] + 1)]
                if newblock.type != "Wall":
                    self.Graph[block].append(newblock)
            
            if self.BlockTrace.get((position[0], position[1] - 1)) != None:
                newblock = self.BlockTrace[(position[0], position[1] - 1)]
                if newblock.type != "Wall":
                    self.Graph[block].append(newblock)
            pass
        self.CreateHeatmap()
        pass 
    
    def CreateHeatmap(self):
        startpoint = self.BlockTrace[self.Main]
        for block in self.BlockList:
            block.visited = False
            block.dist = 0
        openlist = [startpoint]
        startpoint.visited = True
        while len(openlist) > 0:
            point = openlist[0]
            if point.type == "Wall":
                print(point.position, "??")
            for nextpoint in self.Graph[point]:
                if nextpoint.visited == False:
                    nextpoint.dist = point.dist + 1
                    openlist.append(nextpoint)
                    nextpoint.visited = True
                elif nextpoint.dist > point.dist + 1:
                    nextpoint.dist = point.dist + 1
            openlist.pop(0)
            pass
        self.CalculateVector()
        pass
    
    def CalculateVector(self):
        print("calculate")
        blockSearch = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (-1, -1), (1, -1)]
        startPoint = (0, 0)
        openList = [startPoint]
        for block in self.BlockList:
            block.visited = False
        while len(openList) > 0:
            MaxDist = 1000
            Dir = (0, 0)
            thisPos = openList[0]
            if self.BlockTrace.get(thisPos) == None or self.BlockTrace[thisPos].type == "Wall":
                continue
            else: thisBlock = self.BlockTrace[thisPos]
            thisBlock.visited = True
            for nextBlock in blockSearch:
                newpos = (thisPos[0] + nextBlock[0], thisPos[1] + nextBlock[1])
                if self.BlockTrace.get(newpos) != None:
                    newBlock = self.BlockTrace[newpos]
                    if newBlock.type == "Wall":
                        newBlock.visited = True
                        continue
                    if newBlock.visited == False:
                        openList.append(newpos)
                    newBlock.visited = True
                    if MaxDist > newBlock.dist:
                        MaxDist = newBlock.dist
                        Dir = nextBlock
            thisBlock.Vector = Dir
            # if thisBlock.dist == 2:
            #     print(MaxDist, Dir)
            #     self.draw()
            #     input()
            openList.pop(0)
        pass

game = Game()

while game.running:
    game.update()