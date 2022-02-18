# ChessR

![Generated images of chess games](https://github.com/TheFamousRat/ChessR/blob/master/illustration.jpeg)

## Summary

ChessR is a project to generate large synthetic datasets of images representing pictures of board games. Example of such a dataset, applied to chess boards, can be found here : https://www.kaggle.com/thefamousrat/synthetic-chess-board-images

The application its been tested on for now was the generation of images of chess games, but the framework has been built to be game-agnostic, and could as such be used for any board game. The only strong constraint for now is that the board be rectangular with evenly-sized cells.

Such synthetic datasets provide great training resources for neural network, essentially removing the hassling of collecting and annotating data. Classic CNN architectures trained on the linked chess datasets attained quickly accuracies of over 99% on test data. See example notebooks on the Kaggle page.

## Implementation

The generator was designed using the Python API of the Blender engine. The whole code is written in Python, with 3D handling done by Blender and rendering by the Cycles engine of Blender.

The images are generated to look like plausible pictures taken from a phone camera, at an overlooking angle so that the pieces are well visible. The following augmentations are implemented :
 - Random rotation of the pieces
 - Random placement of the pieces within the cells
 - Camera rotation
 - Motion blur
 - Light and shadows variation
 - Flash camera simulation
 - Variations in focal length within plausible range for a phone camera

The pieces and boards used in the example dataset were taken from free and commercial models on the site CGTrader. The meshes are not provided with this repo.

## How to use

Ensure that your version of Blender is 2.8 and above. Install the requirements using Blender's pip 

`
/path/to/Blender's/bin/python3.9 -m pip install -r requirements.txt
`

This is all that must be done for setting up the Python environment. However if you want to use your own pieces and boards more must be done. 

### Scene organization

Three collections need to be built and regroup different data types :

 - A collection regrouping the boards. The children of this collection must be objects corresponding to boards.
 - A collection regrouping the types of pieces. The children of this collection must be other collections whose names correspond to a unique type of game piece.
 - A collection regrouping the pieces. The children of this collection must be other collections regrouping the objects forming a pieces set.

In the chess set generation, the scene tree looked like this : 

```
┖╴(Scene Collection)
  ┠╴(piecesTypes)
  ┃  ┠╴(pieceType1)
  ┃  ┃  ┠╴piece1_1
  ┃  ┃  ┖╴piece2_1
  ┃  ┖╴(pieceType2)
  ┃     ┠╴piece1_2
  ┃     ┖╴piece2_2
  ┠╴(plateaux)
  ┃  ┠╴plateau1
  ┃  ┖╴plateau2
  ┖╴Pieces sets
    ┠╴(set1)
    ┃  ┠╴piece1_1
    ┃  ┖╴piece1_2
    ┠╴(set2)
    ┃  ┠╴piece2_1
    ┃  ┖╴piece2_2
```

The names of the collections can be changed at will, but must then be updated accordingly in the constants of globals.py.

### Adding a new piece

The new piece must be made of a single mesh. It must have a children named "Base", represented by an empty object. This empty must be positioned at the base of the piece, with proper scaling and positioning so that it matches the position and radius of the piece's base.

The piece must be added to a pieces set collection. If the piece is part of a new set, a new corresponding collection must be created under "Pieces set", and the piece be added to it.

Finally, the piece must be added to a collection corresponding to its type under "piecesTypes".

NOTE : Each piece type must be represented at least once per set

### Adding a new board

The new board must be made of a single mesh. It must be added as a direct child of the collection "plateau". Four types of empties must then be added and positioned as its children :

 - As many Empties as cells on the board, representing the center of the board's cells, and positioned accordingly. In chess you'd have empties named "A1", "A2"... "H8". The names must exactly contain the name of the cell, all in uppercase.
 - Four Empties representing the four corners of the board, and named "BL", "BR", "TL", "TR" ("T" or "B" for Top and Bottom, "L" and "R" for Left and Right)
 - One Empty representing the base of the board, named "Board"
 - One Empty representing the center of the board, named "Center"

NOTE : The names only need to contain the information, they do not need to exactly match. For example, "LR.001" or "LR2" for "LR" would work fine

### Changing paths names, empties names, cells setup

All elements such as Collections names, cells names, empties' names are constant registered in the globals.py file. If the user wishes to change those, he must update globals.py imperatively.


