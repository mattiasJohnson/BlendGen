import bpy
import mathutils
from mathutils import Vector
import random
from typing import Dict

positions_start = { "wK": "e1", "wQ": "d1", "wR1": "a1", "wR2": "h1", "wB1": "c1", "wB2": "f1", "wN1": "b1", "wN2": "g1", "wP1": "a2", "wP2": "b2", "wP3": "c2", "wP4": "d2", "wP5": "e2", "wP6": "f2", "wP7": "g2", "wP8": "h2", "bK": "e8", "bQ": "d8", "bR1": "a8", "bR2": "h8", "bB1": "c8", "bB2": "f8", "bN1": "b8", "bN2": "g8", "bP1": "a7", "bP2": "b7", "bP3": "c7", "bP4": "d7", "bP5": "e7", "bP6": "f7", "bP7": "g7", "bP8": "h7", }

def getPiece(name):
    piece = bpy.data.objects[name]
    return piece

def movePiece(name, pos):
    piece = bpy.data.objects[name]
    pos_vec = mathutils.Vector(pos)
    piece.location = pos_vec

def getRandomBoard() -> Dict[str,str]:
    """
    Generates a random piece position dictionary.
    """
    pos_list = []
    positions = positions_start.copy()

    for i in range(1, 9):
        for j in range(0, 8):
            position = chr(97 + j) + str(i)
            pos_list.append(position)
    random_positions = random.sample(pos_list, 32)

    for idx, piece in enumerate(positions):
        positions[piece] = random_positions[idx]

    return positions

class Board:

    def __init__(self, bottom_left: Vector, top_left: Vector):
        self.unit_vector_up = (top_left - bottom_left) / 8
        # Rotate 90 degrees clockwise
        self.unit_vector_right = mathutils.Vector(
            (self.unit_vector_up.y, -self.unit_vector_up.x, self.unit_vector_up.z)
        )

        # Bottom left corner of board
        self.bottom_left = bottom_left

        # Bottom left corner piece center
        self.bottom_left_centered = self.bottom_left + 0.5 * self.unit_vector_right + 0.5 * self.unit_vector_up
        
        self.positions = positions_start.copy()


    def setPositions(self, new_positions: Dict[str, str]) -> None:
        """
        Takes a dictionary on the form {"wQ":"b4"} and moves all the pieces.
        """
        for piece, position in new_positions.items():
            coord = self.translateCoordinate(position)
            movePiece(piece, coord)

    def translateCoordinate(self, chess_coordinate: str) -> Vector:
        """
        Translates a chess coordinate like b5 to the corresponding position vector.
        Instance function since needs board corners.
        """
        x_offset = (ord(chess_coordinate[0]) - 97) * self.unit_vector_right
        y_offset = (int(chess_coordinate[1]) - 1) * self.unit_vector_up
        coordinate = self.bottom_left_centered + x_offset + y_offset

        return coordinate
            
    def randomise(self):
        random_positions = getRandomBoard()
        self.setPositions(random_positions)
        
    def reset(self):
        positions = positions_start.copy()
        self.setPositions(positions)