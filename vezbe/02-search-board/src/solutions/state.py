from __future__ import print_function

from abc import *
import copy


class State(object):
    """
    Apstraktna klasa koja opisuje stanje pretrage.
    """

    @abstractmethod
    def __init__(self, board, parent=None, position=None, goal_position=None):
        """
        :param board: Board (tabla)
        :param parent: roditeljsko stanje
        :param position: pozicija stanja
        :param goal_position: pozicija krajnjeg stanja
        :return:
        """
        self.board = board
        self.parent = parent  # roditeljsko stanje
        
        if self.parent is None:  # ako nema roditeljsko stanje, onda je ovo inicijalno stanje
            self.position = board.find_position(self.get_agent_code())  # pronadji pocetnu poziciju
            self.goal_position = board.find_position(self.get_agent_goal_code())  # pronadji krajnju poziciju
        else:  # ako ima roditeljsko stanje, samo sacuvaj vrednosti parametara
            self.position = position
            self.goal_position = goal_position
            
        self.depth = parent.depth + 1 if parent is not None else 1  # povecaj dubinu/nivo pretrage
        
        # Spisak pokupljenih kutija
        self.picked_boxes = copy.deepcopy(parent.picked_boxes) if parent is not None else []

    def get_next_states(self):
        new_positions = self.get_legal_positions()  # dobavi moguce (legalne) sledece pozicije iz trenutne pozicije
        next_states = []
        # napravi listu mogucih sledecih stanja na osnovu mogucih sledecih pozicija
        for new_position in new_positions:
            next_state = self.__class__(self.board, self, new_position, self.goal_position)
            next_states.append(next_state)
            
        # Provjeravamo da li je trenutna pozicija portal da bismo dodali i ta stanja...
        portal_positions = self.board.find_elements('p')
        if self.position in portal_positions:
            portal_positions.remove(self.position)
            for position in portal_positions:
                state = self.__class__(self.board, self, position, self.goal_position)
                next_states.append(state)
            
        return next_states

    @abstractmethod
    def get_agent_code(self):
        """
        Apstraktna metoda koja treba da vrati kod agenta na tabli.
        :return: str
        """
        pass

    @abstractmethod
    def get_agent_goal_code(self):
        """
        Apstraktna metoda koja treba da vrati kod agentovog cilja na tabli.
        :return: str
        """
        pass

    @abstractmethod
    def get_legal_positions(self):
        """
        Apstraktna metoda koja treba da vrati moguce (legalne) sledece pozicije na osnovu trenutne pozicije.
        :return: list
        """
        pass

    @abstractmethod
    def is_final_state(self):
        """
        Apstraktna metoda koja treba da vrati da li je treuntno stanje zapravo zavrsno stanje.
        :return: bool
        """
        pass

    @abstractmethod
    def unique_hash(self):
        """
        Apstraktna metoda koja treba da vrati string koji je JEDINSTVEN za ovo stanje
        (u odnosu na ostala stanja).
        :return: str
        """
        pass
    
    @abstractmethod
    def get_cost(self):
        """
        Apstraktna metoda koja treba da vrati procenu cene
        (vrednost heuristicke funkcije) za ovo stanje.
        Koristi se za vodjene pretrage.
        :return: float
        """
        pass
    
    @abstractmethod
    def get_current_cost(self):
        """
        Apstraktna metoda koja treba da vrati stvarnu trenutnu cenu za ovo stanje.
        Koristi se za vodjene pretrage.
        :return: float
        """
        pass


class RobotState(State):
    def __init__(self, board, parent=None, position=None, goal_position=None):
        super(self.__class__, self).__init__(board, parent, position, goal_position)
        # posle pozivanja super konstruktora, mogu se dodavati "custom" stvari vezani za stanje
        # TODO 6 i TODO 8: prosiriti stanje sa informacijom da li je robot pokupio sve kutije
        if parent is not None:
            self.picked_boxes = copy.deepcopy(parent.picked_boxes)
        else:
            self.picked_boxes = []

        # Ako smo trenutno na polju koje je kutija dodamo kutiju
        if self.position in board.boxes and self.position not in self.picked_boxes:
            self.picked_boxes.append(self.position)
        
        # Ako je broj kutija jednak broju svih kutija ili roditelj ima sve kutije
        self.has_boxes = (len(self.picked_boxes) == len(board.boxes)) or (parent is not None and parent.has_boxes)

    def get_agent_code(self):
        return 'r'

    def get_agent_goal_code(self):
        return 'g'
        
    def get_cost(self):
        # Euklidovo rastojanje
        return ((self.position[0] - self.goal_position[0])**2 + (self.position[1] - self.goal_position[1])**2)**0.5  
        
        # Menhetn udaljenost     
        # return abs(self.position[0] - self.goal_position[0]) + abs(self.position[1] - self.goal_position[1])
        
    def get_current_cost(self):
        return self.depth

    def get_legal_positions(self):
        # d_rows (delta rows), d_cols (delta columns)
        # moguci smerovi kretanja robota (desno, levo, dole, gore)
        
        # TODO 5: Rijesen smijer kretanja robota - moze i dijagonalno
        d_rows = [0, 0, 1, -1, -1, -1, 1, 1]
        d_cols = [1, -1, 0, 0, -1, 1, -1, 1]

        row, col = self.position  # trenutno pozicija
        new_positions = []
        for d_row, d_col in zip(d_rows, d_cols):  # za sve moguce smerove
            new_row = row + d_row  # nova pozicija po redu
            new_col = col + d_col  # nova pozicija po koloni
            # ako nova pozicija nije van table i ako nije zid ('w'), ubaci u listu legalnih pozicija
            if 0 <= new_row < self.board.rows and 0 <= new_col < self.board.cols and self.board.data[new_row][new_col] != 'w':
                new_positions.append((new_row, new_col))
        return new_positions

    def is_final_state(self):
        # Dodata informacija da mora posjedovati i sve kutije da bi bio final_state
        return self.position == self.goal_position and self.has_boxes

    def unique_hash(self):
        # Izmijenjen unique_hash zbog stanja
        # Dodat i spisak kutija koje je pokupio.
        # Ne moze samo broj - bitno je koje je kutije pokupio.
        return str(self.position) + str(self.picked_boxes)
