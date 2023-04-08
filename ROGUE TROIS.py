class Coord(object):
    def __init__(self,x,y):
        self.x=x
        self.y=y
        
    def __eq__(self,other):
        if self.x==other.x and self.y==other.y:
            return True
        return False
        
    def __repr__(self):
        return f"<{self.x},{self.y}>"
        
    def __add__(self,other):
        return Coord(self.x+other.x,self.y+other.y)


class Element(object):
    def __init__(self,name=None,abbrv=""):
        if abbrv=="":
            self._abbrv=name[0]
        else:
            self._abbrv=abbrv
        self._name=name
        
    def __repr__(self):
        return str(self._abbrv)
        
    def description(self):
        return "<"+self._name+">"
        
    def meet(self,hero):
        hero.take(self)
        return True

class Creature(Element):
    def __init__(self,name,hp=10,abbrv="",strength=1):
        Element.__init__(self,name,abbrv)
        self._hp=hp 
        self._strength=strength
    
    def description(self):
        return Element.description(self) +"("+str(self._hp)+")"
    
    def meet(self,other):
        self._hp=self._hp-other._strength
        if self._hp<=0:
            return True
        return False



class Hero(Creature):
    def __init__(self,name="Hero",hp=10,abbrv="@",strength=2,inventory=None):
        if inventory is None:
            inventory = []
        Creature.__init__(self,name,hp,abbrv,strength)
        self._inventory=inventory
    
    def description(self):
        return Creature.description(self)+str(self._inventory)
    
    def take(self,elem):
        self._inventory.append(elem)


class Map(object):
    ground="."
    empty=' '
    dir={'z': Coord(0,-1), 's': Coord(0,1), 'd': Coord(1,0), 'q': Coord(-1,0)}

    
    def __init__(self,size=20,pos=Coord(1,1),hero=None,roomsToReach=None,rooms=None):
        self.size=size
        self.posi=pos
        if hero==None:
            self._hero=Hero()
        else:
            self._hero=hero
        self._mat=[]
        if roomsToReach is None:
            self._roomsToReach=[]
        else:
            self._roomsToReach=roomsToReach
        if rooms is None:
            self._rooms=[]
        else:
            self._rooms=rooms
        for i in range(self.size):
            l=[]
            for j in range(self.size):
                l.append(Map.empty)
            self._mat.append(l)
        #self._mat[pos.y][pos.x]=self._hero
        #self._elem={self._hero : self.posi}
        self._elem={}

        
    def __repr__(self):
        c=""
        for i in range(self.size):
            for x in range(self.size):
                c=c+str(self._mat[i][x])
            c=c+'\n'
        return c
        
    def __len__(self):
        return self.size

    def __contains__(self, item):
        if isinstance(item,Coord):
            if 0<=item.x<len(self) and 0<=item.y<len(self):
                return True
        elif self._elem.get(item) or item==Map.ground:
            return True
        return False 
    
    def get(self,c):
        if c in self:
            return self._mat[c.y][c.x]
    
    def pos(self,e):
        if e in self:
            return self._elem[e]
            
    def put(self,c,e):
        self._mat[c.y][c.x]=e
        self._elem[e]=c
            
    def rm(self,c):
        del self._elem[self.get(c)]
        self._mat[c.y][c.x]=Map.ground
        
        
    def move(self,e, way):
        b=self.pos(e)
        if type(b)!=None:
            newpos=Coord(b.x+way.x,b.y+way.y)
            if newpos in self:
                np=self.get(newpos)
                if np==Map.ground:
                    self.rm(b)
                    self.put(newpos,e)
                elif np.meet(e):
                    self.rm(newpos)    
    
    def addRoom(self,room):
        self._roomsToReach.append(room)
        for i in range(room.c1.x,room.c2.x+1):
            for o in range(room.c1.y,room.c2.y+1):
                self._mat[o][i]=Map.ground
    
    def findRoom(self,coord):           #retourne la salle, parmi _roomsToReach, qui contient la coordonnée coord. Retourne False si aucune salle ne correspond.
        for room in self._roomsToReach:
            if coord in room:
                return room
        return False

    def intersectNone(self,room):       #retourne True si aucune salle, parmi _roomsToReach, n'a une intersection avec room, False sinon.
        for i in range(len(self._roomsToReach)):
            if self._roomsToReach[i].intersect(room):
                return False
        return True
        
    def dig(self,coord):                #Change une coord en un point et si c'est une room l'enlève de RTC et la met dans rooms
        self._mat[coord.y][coord.x]=Map.ground
        b=self.findRoom(coord)
        if b!=False:
            self._rooms.append(b)
            self._roomsToReach.remove(b)

    def corridor(self,start,end):
        a=start
        while(start.y<end.y and a.y<=end.y+1)or(start.y>end.y and a.y>=end.y+1):
            self.dig(a)
            a.y+=1 if start.y<end.y else -1
        while(start.x<end.x+1 and a.x<=end.x+1)or(start.x>end.x+1 and a.x>=end.x+1):
            self.dig(a)
            a.x+=1 if start.x<end.x+1 else -1

    

class Room(object):
    def __init__(self,c1=Coord(1,1),c2=Coord(2,2)):
        self.c1=c1
        self.c2=c2
    
    def __repr__(self):
        return f"[<{self.c1.x},{self.c1.y}>, <{self.c2.x},{self.c2.y}>]"
        
    def __contains__(self,item):
        if isinstance(item,Coord):
            if self.c1.x<=item.x<=self.c2.x and self.c1.y<=item.y<=self.c2.y:
                return True
        return False
        
    def center(self):
        ord=((self.c2.x)+(self.c1.x))//2
        abs=(self.c2.y + self.c1.y)//2
        return Coord(ord,abs)
        
    def intersect(self,salle):
        if self.c1 in salle or self.c2 in salle or Coord(self.c1.x,self.c2.y) in salle or Coord(self.c2.x,self.c1.y) in salle:
            return True
        if salle.c1 in self or salle.c2 in self or Coord(salle.c1.x,salle.c2.y) in self or Coord(salle.c2.x,salle.c1.y) in self:
            return True
        return False
        
