# Step-by-step Instructions for Docking with Rosetta

## Prepare Ligand library with Spartan

1. Build ligand
2. Click setup -> calculations -> conformer distribution
⋅⋅⋅⋅* with molecular mechanis and MMFF
⋅⋅⋅⋅* increase max number of conformers to 100%
⋅⋅⋅⋅* if its a large ligand, it can take hours to run
3. After running, a new window will open
4. Bottom will show number of conformers, left arrow to go through them
5. Save library as mol2
6. Also save the original ligand as a spartan file and mol2 file - just in case

[refer to video](https://www.youtube.com/watch?v=ocuT3tYeK7I) 

## Use HIVE to prepare ligands for Rosetta

1. upload CL3.mol2 library conformer to HIVE
⋅⋅⋅⋅* CL3 can instead be any 3 letter/number code for a ligand, dont use 001, be creative
3. run with
```
python3 /quobyte/jbsiegelgrp/software/Rosetta_314/rosetta/main/source/scripts/python/public/generic_potential/mol2genparams.py -s CL3.mol2
```
or try
```
python3 /quobyte/jbsiegelgrp/software/Rosetta_314/rosetta/main/source/scripts/python/public/molfile_to_params.py -n CL3 -p CL3 --conformers-in-one-file CL3.mol2
```
3. will generate CL3.pdb, CL3_conformers.pdb, CL3.params files
4. download all
5. write PDB_ROTAMERS CL3_conformers.pdb at the end of your params file
   example:
   <img width="552" height="117" alt="Screenshot 2026-02-23 at 2 32 08 PM" src="https://github.com/user-attachments/assets/9f18591a-f5af-4ba0-89c3-dd282cef242e" />



## Use HIVE to prepare enzyme for Rosetta

1. 
