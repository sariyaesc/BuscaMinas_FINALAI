import itertools
import random


class Minesweeper():
    """
    Representación del juego Buscaminas
    """

    def __init__(self, height=3, width=3, mines=1):

        # Establece el ancho, alto y número de minas iniciales
        self.height = height
        self.width = width
        self.mines = set()

        # Inicializa un campo vacío sin minas
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Añade minas aleatoriamente
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # Al principio, el jugador no ha encontrado ninguna mina
        self.mines_found = set()

    def print(self):
        """
        Imprime una representación en texto
        de dónde están ubicadas las minas.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Devuelve el número de minas que están
        dentro de una fila y columna de una celda dada,
        sin incluir la celda en sí.
        """

        # Mantiene el conteo de minas cercanas
        count = 0

        # Itera sobre todas las celdas dentro de una fila y columna
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignora la celda en sí
                if (i, j) == cell:
                    continue

                # Actualiza el conteo si la celda está dentro del tablero y es una mina
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Verifica si todas las minas han sido marcadas.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Declaración lógica sobre un juego de Buscaminas.
    Una sentencia consiste en un conjunto de celdas del tablero
    y un conteo del número de esas celdas que son minas.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Devuelve el conjunto de todas las celdas en self.cells que se sabe que son minas.
        """
        if self.count==len(self.cells):
            return self.cells
        else:
            return None
        

    def known_safes(self):
        """
        Devuelve el conjunto de todas las celdas en self.cells que se sabe que son seguras.
        """
        if self.count==0:
            return self.cells
        else: 
            return None
        

    def mark_mine(self, cell):
        """
        Actualiza la representación interna del conocimiento dado el hecho
        de que se sabe que una celda es una mina.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count=self.count-1
    
    def mark_safe(self, cell):
        """
        Actualiza la representación interna del conocimiento dado el hecho
        de que se sabe que una celda es segura.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Jugador del juego Buscaminas
    """

    def __init__(self, height=8, width=8):

        # Establece el alto y ancho inicial
        self.height = height
        self.width = width

        # Lleva el registro de qué celdas han sido seleccionadas
        self.moves_made = set()

        # Lleva el registro de celdas que se sabe que son seguras o minas
        self.mines = set()
        self.safes = set()

        # Lista de sentencias sobre el juego que se sabe que son verdaderas
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marca una celda como mina y actualiza todo el conocimiento
        para marcar esa celda también como mina.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marca una celda como segura y actualiza todo el conocimiento
        para marcar esa celda también como segura.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Llamada cuando el tablero de Buscaminas nos dice, para una celda
        segura dada, cuántas celdas vecinas tienen minas.

        Esta función debe:
            1) marcar la celda como una jugada ya realizada
            2) marcar la celda como segura
            3) añadir una nueva sentencia a la base de conocimiento de la IA
               basada en el valor de `cell` y `count`
            4) marcar cualquier celda adicional como segura o como mina
               si se puede concluir con base en la base de conocimiento
            5) añadir cualquier nueva sentencia a la base de conocimiento
               si se pueden inferir a partir del conocimiento existente
        """
        #1 
        self.moves_made.add(cell)

        #2
        self.mark_safe(cell)

        #3
        cells=set()

        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                if (i, j) == cell:
                    continue

                if 0 <= i < self.height and 0 <= j < self.width:
                    if (i, j) not in self.moves_made and (i, j) not in self.mines:
                        cells.add((i, j))
                    elif (i, j) in self.mines:
                        count -= 1
        self.knowledge.append(Sentence(cells, count))
        
        #4
        for sentence in self.knowledge:
            safes = sentence.known_safes()
            if safes:
                for cell in safes.copy():
                    self.mark_safe(cell)
            mines = sentence.known_mines()
            if mines:
                for cell in mines.copy():
                    self.mark_mine(cell)
        
        #5
        for sentence1 in self.knowledge:
            for sentence2 in self.knowledge:
                if sentence1 is sentence2:
                    continue
                if sentence1 == sentence2:
                    self.knowledge.remove(sentence2)
                elif sentence1.cells.issubset(sentence2.cells):
                    new_knowledge = Sentence(
                        sentence2.cells - sentence1.cells,
                        sentence2.count - sentence1.count)
                    if new_knowledge not in self.knowledge:
                        self.knowledge.append(new_knowledge)


    def make_safe_move(self):
        """
        Devuelve una celda segura para seleccionar en el tablero de Buscaminas.
        La jugada debe saberse que es segura, y no debe haber sido
        realizada anteriormente.

        Esta función puede usar el conocimiento en self.mines, self.safes
        y self.moves_made, pero no debe modificar ninguno de esos valores.
        """
        available_steps = self.safes - self.moves_made
        if available_steps:
            return random.choice(tuple(available_steps))
        return None

    def make_random_move(self):
        """
        Devuelve una jugada para hacer en el tablero de Buscaminas.
        Debe elegir aleatoriamente entre las celdas que:
            1) no hayan sido seleccionadas, y
            2) no se sepa que son minas
        """
        if len(self.mines) + len(self.moves_made) == self.height * self.width:
            return None

        # loop until an appropriate move is found
        while True:
            i = random.randrange(self.height)
            j = random.randrange(self.width)
            if (i, j) not in self.moves_made and (i, j) not in self.mines:
                return (i, j)
