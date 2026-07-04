from Bio.PDB import PDBParser

pdb_file = "scripts/examples/pdl1_outputs_fv_hotspot/set1_top2/rf2_predictions_fixed/pdl1_fv_hotspot_set1_1_dldesign_3_best.pdb"

aa3to1 = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C",
    "GLN": "Q", "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I",
    "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P",
    "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V",
}

parser = PDBParser(QUIET=True)
structure = parser.get_structure("candidate", pdb_file)
model = structure[0]

for chain_id in ["T", "H", "L"]:
    seq = ""
    for residue in model[chain_id]:
        if residue.id[0] == " " and "CA" in residue:
            seq += aa3to1.get(residue.resname, "X")
    print(f">{chain_id}")
    print(seq)
    print()
