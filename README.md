# Step-by-step Instructions for Docking with Rosetta

## 1) Prepare Ligand library with Spartan

1. Build ligand
2. Click setup -> calculations -> conformer distribution
* with molecular mechanics and MMFF
* increase max number of conformers to 100%
* if its a large ligand, it can take hours to run
3. After running, a new window will open
4. Bottom will show number of conformers, left arrow to go through them
5. Save library as mol2
6. Also save the original ligand as a spartan file and mol2 file - just in case

[refer to video](https://www.youtube.com/watch?v=ocuT3tYeK7I) 

## 2) Use HIVE to prepare ligands for Rosetta

1. upload CL3.mol2 library conformer to HIVE
* CL3 can instead be any 3 letter/number code for a ligand, dont use 001, be creative
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



## 3) Use HIVE to prepare enzyme for Rosetta

1. Acquire enzyme PDB from [Uniprot](https://www.uniprot.org/) or [RCSB PDB](https://www.rcsb.org/)
   or refer to my [Alphafold3 Submission for HIVE](https://github.com/MissMaryR/AlphaFold3-Submission-for-HIVE) to generate a PDB from AF3
2. Refer to my [Relax pdbs for Rosetta](https://github.com/MissMaryR/Relax-pdbs-for-Rosetta) to prepare your PDB



## 4) Use PyMOL to place ligand into active site - makes docked.pdb file

### To help guide ligand placement in the active site, try using: [Chai](https://www.chaidiscovery.com/), AF3, or [Boltz](https://github.com/jwohlwend/boltz)
* they will generate PDBs with a general ligand placement - often not close enough to catalytic residues for docking analysis but acts as a guide

1. Open relaxed PDB & ligand (CL3.pdb) in PyMOL
2. If you made a roughly docked PDB from sources above try using the [Pair fit](https://pymolwiki.org/index.php/Pair_fit) commands in PyMOL
   * also add the roughly docked PDB to the PyMOL session and align it with the relaxed PDB
   * run commands in the command line in PyMOL
   * use SHOW to show atom names on catalytic residues & ligands
   * it works by moving LIG1 (your ligand) on top of LIG2 (ligand already in active site)
   * ```
     pair_fit LIG1/ATOM1+ATOM2, LIG2/ATOM1+ATOM2
     ```
   * example code with moving CL3 (your ligand) on top of LIG2
   * ```
     pair_fit CL3/O1+C4+O3+C7, LIG2/O2_1+C3_1+O3_1+C4_1
     ```
   * keep pressing enter to move it to different positions, if several are available
   * alternatively you can adjust the number of atoms to align
   * save the session
3. Alternatively, you can use the Pair Fit method to align the ligand to a catalytic residue
   * then use editing mode in PyMOL to move the ligand into a spot that is catalytically relevant
   * it does not need to be super specific, just within a couple angstroms, the constraint file will tell rosetta where to place the ligand
   * recommend using a mouse for editing mode
5. Make sure to delete everything except the relaxed PDB and the placed ligand (CL3.pdb)
   * keep the order with relaxed PDB first and then the ligand, this matters for the pdb file
6. File -> export structure -> export molecule -> save as PDB
7. Open the saved file and make sure your ligand is at the bottom and labeled as chain X
   * if 2 ligands - X & Y
8. This will be your docked.pdb file

## 5) Use PyMOL to make constraint file - cst_X.cst

1. Open the cst_X.cst with emacs or textedit
2. We refer to the [RosettaCommons page](https://docs.rosettacommons.org/docs/latest/rosetta_basics/file_types/match-cstfile-format) for how to make constraints
3. Here is a diagram for ATOM labels:
   * <img width="518" height="282" alt="Screenshot 2026-02-23 at 3 49 32 PM" src="https://github.com/user-attachments/assets/ffa6f6db-52a4-4bd6-a5b6-8b3c8dc3dee9" />
* example constraint file to accompany diagram
```
CST::BEGIN
  TEMPLATE::   ATOM_MAP: 1 atom_name: C1 C2 C3
  TEMPLATE::   ATOM_MAP: 1 residue3: CL3

  TEMPLATE::   ATOM_MAP: 2 atom_type: O1 O2 O3
  TEMPLATE::   ATOM_MAP: 2 residue1: E

  CONSTRAINT:: distanceAB:    2.00   0.30 100.00  1        
  CONSTRAINT::    angle_A:  105.10   6.00 100.00  360.00   
  CONSTRAINT::    angle_B:  116.90   5.00  50.00  360.00   
  CONSTRAINT::  torsion_A:  105.00  10.00  50.00  360.00   
  CONSTRAINT::  torsion_B:  180.00  10.00  25.00  180.00   
  CONSTRAINT:: torsion_AB:    0.00  45.00   0.00  180.00   
CST::END
```
   * use residue3 for your ligand and residue1 for the residue using its' one letter code
   * my example cst_X.cst file only uses a distance and angle constraint, less constraints are better but more may need to be used if necessary
   * Each of these strings is followed by 4 (optionally 5 ) columns of numbers: x0, xtol, k, covalent/periodicity, and number of samples.
   * The 1st column, x0, specifies the optimum distance x0 for the respective value.
   * The 2nd, xtol, column specifies the allowed tolerance xtol of the value.
   * The 3rd column specifies the force constant k, or the strength of this particular parameter. If x is the value of the constrained parameter, the score penalty applied will be: 0 if |x - x0| < xtol and k * ( |x - x0| - xtol ) otherwise This 3rd column is only relevant for enzdes, and the number in it is not used by the matcher.
   * The 4th column has a special meaning in case of the distanceAB parameter. It specifies whether the constrained interaction is covalent or not. 1 means covalent, 0 means non-covalent
   * we dont use the 5th column - deleted

 ### Constraints in simpler terms:
   * 1st column - distance in Angstroms or angle to constrain
      * use PyMOL Wizard function to measure distances and angles for reference
   * 2nd column - how much you allow it to move outside of the constraint from 1st column
      * we constrain at 3A with a tolerance of 0.2A, so the ligand will be constrained 2.8-3.2A to the residue
   * 3rd column - use 100 to strictly use the constraint, reduce to 50 or 25 to more loosely follow the constraint
   * 4th column - 1=covalent 0=non-covalent

4. Save cst_X.cst file
5. Open your docked.pdb file with TextEdit and add this to the top
```
REMARK 666 MATCH TEMPLATE X  CL3   1   MATCH MOTIF A GLU    409  1              
REMARK 666 MATCH TEMPLATE X  CL3   1   MATCH MOTIF A ASP    220  2
```
   *should look like this:
   <img width="576" height="95" alt="Screenshot 2026-02-23 at 4 10 11 PM" src="https://github.com/user-attachments/assets/8aaff5ea-2cd1-4b9a-8a5c-006377c1219a" />

6. Adjust the ligand (CL3) & residues (GLU & ASP) to yours
   * tt should be in the same order as your constraint file
   * here, CL3 is on chain X and GLU/ASP are both on chain A; with GLU as residue 409 and ASP as residue 220
   * be careful - this is a common spot for rosetta crashes, everything must correlate correctly
7. Save the docked.pdb

## 6) Notes for dock2.xml file

Do you have a dimer? trimer?
   * “min_jumps” should be equal to the number of chains

To adjust the script for design:
   * All “repack_only” should be 1 for docking, 0 for design
   * All “design” should be 0 for docking, 1 for design

## 7) Upload files to HIVE and run docking

1.	Enzyme with substrate – docked.pdb
2.	Constraint file – cst_X.cst
3.	Flags file – flags
4.	Conformer library – CL3_conformers.pdb (not shown on github)
5.	Params file – CL3.params
6.	dock xml file – dock2.xml
7.	Submission script – submit.sh

### run docking with 
```
sbatch submit.sh
```
this will make PDB and score files in the results folder

## 8) Score results

go to results folder and run
```
sbatch zzzScoring.sh
```
this will quickly run through all score files and generate a zzztop_pdbs folder with a copy of the top 10 PDBs
with a top_glycan_features.txt file, open it with 
```
emacs top_glycan_features.txt
```

this script shows the total number of PDBs made
then filters for entries that passed all constraints < 1.0
then filters for the top 20% with the best toal score
then selects the top 10 with the best interface energy score










     

