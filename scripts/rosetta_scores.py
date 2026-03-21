#!/usr/bin/env python3

import os
import math
import csv
import shutil


def safe_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return float('nan')


def load_scores():
    data = []
    header = []

    for filename in os.listdir('.'):
        if filename.endswith('.sc') and filename.startswith('score'):
            with open(filename, 'r') as f:
                for line in f:
                    if line.startswith('#') or not line.strip():
                        continue
                    tokens = line.strip().split()
                    if not header:
                        header = tokens
                        continue
                    if tokens[0] == header[0]:
                        continue
                    if len(tokens) < len(header):
                        continue

                    row = {}
                    for i, col in enumerate(header):
                        if col == 'description':
                            row[col] = tokens[-1].strip()
                        else:
                            row[col] = safe_float(tokens[i])
                    data.append(row)
    return data, header


def main():
    base_dir = os.getcwd()
    
    subdirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    
    if not subdirs:
        print("No subdirectories found.")
        return

    for subdir in subdirs:
        subdir_path = os.path.join(base_dir, subdir)
        top_pdbs_path = os.path.join(subdir_path, "Top_PDBs")
        results_path = os.path.join(subdir_path, "results")

        if os.path.exists(top_pdbs_path):
            print(f"⏭️  Skipping '{subdir}' — Top_PDBs already exists.")
            continue

        if not os.path.exists(results_path):
            print(f"⚠️  Skipping '{subdir}' — no 'results' folder found.")
            continue

        print(f"\n📂 Processing: {subdir}")
        os.chdir(results_path)

        data, header = load_scores()
        if not data:
            print("  No valid score data found.")
            os.chdir(base_dir)
            continue

        all_pdbs = set(row.get('description') for row in data)
        print(f"  🔢 Total unique PDB entries found: {len(all_pdbs)}")

        interf_E_key = next((k for k in header if k.startswith("SR_3_interf_E_1_2")), None)
        if interf_E_key is None:
            print("  ❌ Missing SR_3_interf_E_1_2 field.")
            os.chdir(base_dir)
            continue

        glycan_features = [
            'description',
            'total_score',
            'all_cst',
            interf_E_key,
            'SR_3_dsasa_1_2',
            'interface_delta_X',
        ]
        available_features = [f for f in glycan_features if f in header or f == interf_E_key]

        filtered = [row for row in data if row.get('all_cst', float('inf')) < 1.0]
        print(f"  ✅ Passed constraint filter (all_cst < 1.0): {len(filtered)} entries")
        if not filtered:
            print("  ❌ No entries passed constraint filter.")
            os.chdir(base_dir)
            continue

        filtered.sort(key=lambda r: r.get('total_score', float('inf')))
        top_20_total = filtered[:math.ceil(0.2 * len(filtered))]
        print(f"  ✅ Top 20% by total_score: {len(top_20_total)} entries")

        top_20_total.sort(key=lambda r: r.get(interf_E_key, float('inf')))
        top_final = top_20_total[:10]
        print(f"  ✅ Selected top 10 by best {interf_E_key}")

        output_dir = top_pdbs_path
        os.makedirs(output_dir, exist_ok=True)

        csv_out = os.path.join(output_dir, "glycan_top_filtered.csv")
        full_csv_out = os.path.join(output_dir, "glycan_top_fullscores.csv")
        glycan_txt = os.path.join(output_dir, "top_glycan_features.txt")

        with open(csv_out, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=available_features)
            writer.writeheader()
            for row in top_final:
                writer.writerow({k: row.get(k, 'NA') for k in available_features})

        with open(full_csv_out, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()
            for row in top_final:
                writer.writerow({k: row.get(k, 'NA') for k in header})

        with open(glycan_txt, 'w') as f:
            header_line = '  '.join(f"{k:<20}" for k in available_features)
            f.write(header_line + "\n")
            for row in top_final:
                row_line = '  '.join(
                    f"{row.get(k, 'NA'):<20.2f}" if isinstance(row.get(k), float)
                    else f"{row.get(k, 'NA'):<20}"
                    for k in available_features
                )
                f.write(row_line + "\n")

            f.write("\n" + "="*80 + "\n")
            f.write("Summary Statistics:\n")
            f.write(f"Total PDBs parsed:                {len(all_pdbs)}\n")
            f.write(f"Entries passing all_cst < 1.0:   {len(filtered)}\n")
            f.write(f"Top 20% by total_score:          {len(top_20_total)}\n")
            f.write(f"Top 10 by best {interf_E_key}:         {len(top_final)}\n")

        print(f"\n  📝 Output written to:")
        print(f"   - Glycan features CSV:   {csv_out}")
        print(f"   - Full scores CSV:       {full_csv_out}")
        print(f"   - TXT summary:           {glycan_txt}")

        copied = []
        for row in top_final:
            pdb_name = row['description']
            if not pdb_name.endswith('.pdb'):
                pdb_name += '.pdb'
            if os.path.exists(pdb_name):
                dest = os.path.join(output_dir, os.path.basename(pdb_name))
                shutil.copy2(pdb_name, dest)
                copied.append(dest)
            else:
                print(f"  ⚠️  PDB not found: {pdb_name}")

        if copied:
            print(f"  📁 Copied {len(copied)} PDB files to {output_dir}/")
        else:
            print(f"  ⚠️  No PDBs were copied to {output_dir}/.")

        os.chdir(base_dir)


if __name__ == "__main__":
    main()
