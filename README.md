# Step-by-step Instructions for Docking and/or Design with Rosetta

This guide walks through the full pipeline for docking a small molecule ligand into a protein active site using Rosetta. Steps proceed from ligand preparation → parameter generation → enzyme preparation → active site placement → constraint setup → docking → scoring.

---

## Overview

| Step | Tool | What You're Doing |
|------|------|-------------------|
| 1 | Spartan | Build ligand & generate conformer library |
| 2 | HIVE (Rosetta) | Convert mol2 → Rosetta-ready params + conformers |
| 3 | HIVE (Rosetta) | Prepare & relax enzyme PDB |
| 4 | PyMOL | Place ligand in active site → `docked.pdb` |
| 5 | PyMOL + text editor | Write constraint file → `cst_X.cst` |
| 6 | Text editor | Configure `dock.xml` for your system |
| 7 | HIVE | Run docking and/or design |
| 8 | HIVE | Score & filter results |

---

## 1) Prepare Ligand Library with Spartan

### Build the ligand
- Use the Spartan build guides carefully — **α and β positions matter!**

### Generate conformers
1. Click **Setup → Calculate**

   ![Spartan Calculate Menu](https://github.com/user-attachments/assets/b4ab5113-7379-4a95-946e-468fe9d1e449)

2. Configure the calculation:
   - Use **Molecular Mechanics** with **MMFF** force field
   - Check **Maximum Conformers Examined** (set your own number; example: 3600)
   - Check **Percent Conformers Kept: 100%**
   - Click **Submit**

3. Monitor job progress by clicking the **Monitor** icon (World icon with screen):

   ![Spartan Monitor](https://github.com/user-attachments/assets/7a8c88b4-0b3d-4803-ab38-ce25cd0789fb)

   > ⚠️ Large ligands can take **hours** to run. You can also terminate jobs from this screen.

4. After the job completes, a new window will open — use the left arrow at the bottom to browse conformers.

### Save files
- Save the conformer library as **`.mol2`**
- Also save the original ligand as both a **Spartan file** and **`.mol2`** — just in case

📹 [Reference video](https://www.youtube.com/watch?v=ocuT3tYeK7I)

---

## 2) Prepare Ligands for Rosetta (on HIVE)

### Connect to HIVE
```bash
ssh username@hive.hpc.ucdavis.edu
```

### Load required modules
```bash
module load conda/latest
module load cuda/12.6.2  # Good to have even when not using a GPU
```

### Transfer files between local and HIVE
```bash
# Local → HIVE
scp -r /path/to/local/folder username@hive.hpc.ucdavis.edu:/quobyte/jbsiegelgrp/username

# HIVE → Local
scp -r username@hive.hpc.ucdavis.edu:/quobyte/jbsiegelgrp/username/folder /path/to/local/folder
```
### Alternatively use [Cyberduck](https://cyberduck.io/) for file transfers - its great!


### Naming your ligand
> 💡 Use a creative 3-letter/number code (e.g., `CL3`). **Avoid `001`** — pick something unique and meaningful to your project.

### Upload and run parameter generation

Upload your `CL3.mol2` conformer library to HIVE, then run one of the following:

**Option A — generic potential (preferred for most ligands):**
```bash
python3 /quobyte/jbsiegelgrp/software/Rosetta_314/rosetta/main/source/scripts/python/public/generic_potential/mol2genparams.py -s CL3.mol2
```

**Option B — molfile to params:**
```bash
python3 /quobyte/jbsiegelgrp/software/Rosetta_314/rosetta/main/source/scripts/python/public/molfile_to_params.py -n CL3 -p CL3 --conformers-in-one-file CL3.mol2
```

### Output files generated
- `CL3.pdb` — ligand structure
- `CL3_conformers.pdb` — all conformers
- `CL3.params` — Rosetta parameters file

### Download all three files, then edit `CL3.params`

Add the following line at the **end** of your `.params` file:
```
PDB_ROTAMERS CL3_conformers.pdb
```

Example:

![Params file example](https://github.com/user-attachments/assets/9f18591a-f5af-4ba0-89c3-dd282cef242e)

---

## 3) Prepare the Enzyme PDB (on HIVE)

1. Obtain the enzyme PDB from [UniProt](https://www.uniprot.org/) or [RCSB PDB](https://www.rcsb.org/)
   - Alternatively, generate a structure with AlphaFold3 — see [AlphaFold3 Submission for HIVE](https://github.com/MissMaryR/AlphaFold3-Submission-for-HIVE)

2. Relax the PDB for Rosetta compatibility — see [Relax PDBs for Rosetta](https://github.com/MissMaryR/Relax-pdbs-for-Rosetta)

---

## 4) Place Ligand in the Active Site with PyMOL → `docked.pdb`

### Guides for initial placement
Before manually docking, use one of these tools to get a rough starting pose:
- [Chai](https://www.chaidiscovery.com/)
- AlphaFold3
- [Boltz](https://github.com/jwohlwend/boltz)

> These generate PDB files with approximate ligand placement — often not close enough to catalytic residues for final analysis, but useful as a starting guide.

### Pair Fit method (recommended when you have a reference ligand)
1. Open your **relaxed PDB** and **`CL3.pdb`** in PyMOL
2. Add the roughly docked PDB from Chai/AF3/Boltz and **align it to your relaxed PDB**
3. Use `SHOW` to display atom names on catalytic residues and ligands
4. Run `pair_fit` in the PyMOL command line to move your ligand (`LIG1`) on top of the reference ligand (`LIG2`):
   ```
   pair_fit LIG1/ATOM1+ATOM2, LIG2/ATOM1+ATOM2
   ```
   Example with `CL3`:
   ```
   pair_fit CL3/O1+C4+O3+C7, LIG2/O2_1+C3_1+O3_1+C4_1
   ```
   - Keep pressing Enter to cycle through available positions
   - Adjust which atoms you align as needed

### Manual placement method (alternative)
- Pair fit the ligand to a catalytic residue, then use **PyMOL editing mode** to fine-tune the position
- A mouse is strongly recommended for editing mode
- It doesn't need to be exact — within a couple of angstroms is fine; the constraint file will guide Rosetta to the precise placement

### Export the docked PDB
1. **Delete everything** except the relaxed PDB and the placed ligand (`CL3.pdb`)
   - Keep the relaxed PDB **first**, ligand **second** — order matters in the PDB file
2. **File → Export Structure → Export Molecule → Save as PDB**
3. Open the saved file and verify:
   - The ligand is at the **bottom** of the file
   - The ligand is labeled as **chain X** (if 2 ligands: chains X and Y)
   - The main enzyme chain should be **chain A***.
   - If different than chains A & X, adjust dock.xml file to your chains.
4. This is your **`docked.pdb`** file

---

## 5) Make the Constraint File → `cst_X.cst`

### Background: what constraints do
Constraints tell Rosetta where to place the ligand relative to catalytic residues by enforcing distances, angles, and torsions. Less is more — start with distance and angle constraints and only add more if needed.

### Atom labeling diagram

![Atom labeling diagram](https://github.com/user-attachments/assets/ffa6f6db-52a4-4bd6-a5b6-8b3c8dc3dee9)

Reference: [RosettaCommons constraint file format](https://docs.rosettacommons.org/docs/latest/rosetta_basics/file_types/match-cstfile-format)

### Example constraint file
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
- Use `residue3` for your ligand (3-letter code)
- Use `residue1` for the catalytic residue (1-letter amino acid code)

### Understanding the constraint columns

Each constraint line has 4 columns: `x0`, `xtol`, `k`, and `covalent/periodicity`

| Column | Meaning | Example |
|--------|---------|---------|
| `x0` | Target distance (Å) or angle | `2.00` |
| `xtol` | Allowed tolerance around `x0` | `0.30` → range is 1.70–2.30 Å |
| `k` | Force constant (constraint strength) | `100` = strict, `50`/`25` = looser |
| `covalent` | For `distanceAB` only: `1` = covalent, `0` = non-covalent | `0` |

> 💡 Use PyMOL's **Wizard → Measure** tool to measure distances and angles between your ligand and catalytic residues as a starting reference.

> ⚠️ The 5th column (number of samples) is **not used** — omit it.

### Add REMARK lines to `docked.pdb`
Open `docked.pdb` in a text editor and add the following at the very top:
```
REMARK 666 MATCH TEMPLATE X  CL3   1   MATCH MOTIF A GLU    409  1              
REMARK 666 MATCH TEMPLATE X  CL3   1   MATCH MOTIF A ASP    220  2
```

Example:

![REMARK 666 example](https://github.com/user-attachments/assets/8aaff5ea-2cd1-4b9a-8a5c-006377c1219a)

This correlates to two constraints in the constraint file, if you just have one constraint then it would be one line, etc. 

**Adjust to match your system:**
- Replace `CL3` with your ligand code
- Replace `GLU`/`ASP` with your catalytic residues (3-letter codes)
- Replace residue numbers (`409`, `220`) with the correct numbers from your PDB
- `CL3` is on chain **X**; catalytic residues are on chain **A** in this example
- The order must match your constraint file

> ⚠️ **This is a common source of Rosetta crashes.** Double-check that the chain IDs, residue names, and residue numbers all match exactly.

---

## 6) Decide on Dock or Design xml

### Multi-chain enzymes
- Set `min_jumps` equal to the **number of chains** (e.g., `2` for a dimer, `3` for a trimer)

### Docking vs. Design mode

# Docking only
Use `dock.xml` if you only want to dock your ligand into the active site to find a binding position. 
This won't do any mutations, only ligand placing. 

# Dock & Design
Use `design.xml` if you want Rosetta to mutate residues around the ligand and dock it into the mutated active site. 
This will do mutations and ligand placing. 

Depending on what you choose, adjust the `flags` file to correspond to the correct script path. 

---

## 7) Upload Files to HIVE and Run Docking

### Required files

| File | Description |
|------|-------------|
| `docked.pdb` | Enzyme with placed ligand |
| `cst_X.cst` | Constraint file |
| `flags` | Rosetta flags file, adjust dock or design xml |
| `CL3_conformers.pdb` | Conformer library |
| `CL3.params` | Ligand parameters |
| `dock.xml` | Rosetta XML protocol | or | `design.xml` | Rosetta XML protocol |
| `submit.sh` | SLURM submission script to start run |
| `Scoring.sh` | SLURM submission script to score PDBs in results folder |
| `results/` folder | for generated docked PDBs |
| `scripts/` folder | Contains `rosetta_scores6.py` |

### Submit the docking job
```bash
sbatch submit.sh
```
This will generate PDB and score files in the `results/` folder.

---

## 8) Score and Filter Results

After the run is finished, run:
```bash
sbatch Scoring.sh
```

This script will:
1. Quickly process all score files
2. Generate a `Top_PDBs/` folder with copies of the **top 10 PDBs**
3. Output a `top_glycan_features.txt` file

### View results
```bash
emacs top_glycan_features.txt
```

### How results are filtered
1. Reports the total number of PDBs generated
2. Filters for entries that **passed all constraints** (score < 1.0)
3. Keeps the **top 20%** by total score
4. Selects the **top 10** by interface energy score
