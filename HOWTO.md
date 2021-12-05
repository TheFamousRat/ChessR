#Adding a new pieces set :
     - (optional) Add the pieces in a child collection to the collection "Chess sets" and named after the set
     - Add a circular empty named "Base" for every piece. This empty must be : 
          - Named "Base" (or containing that name)
          - A child to the piece
          - Scaled to roughly contain the piece's base bounds               - Position properly around the piece's base center
      - Add the pieces to the collection corresponding to their type : white bishops must be added to "bishop_w", black rooks to "rook_b" etc. 

#Adding a new plateau :
    - (optional) Add the plateau in a child collection to the collection "Chess sets" and named after the set
    - For each cell of the plateau, add an empty containing the unique name of this cell and placed roughly at its center. 

NOTE : during the initial checks, the algorithm will check if all cells are present for each plateau, and will otherwise delete its previously found cells and place in a square pattern correctly named cells around the center of the plateau. The user will then have the place those placeholder cells correctly himself.

#Using custom pieces types :      
If the pieces are custom and do not exist in base chess, then new collections corresponding to the new types must be added under the collection "piecesTypes". The pieces are then added to this new collection as usual

#Using a custom plateau size
For now, the algorithm only supports rectangular plateaux. Add the appropriate cell names in the cells list "cellsNames", that contains the id for every cells in the plateau.