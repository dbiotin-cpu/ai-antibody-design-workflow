from Bio.PDB import PDBParser, NeighborSearch

PDB_FILE = "/workspace/boltz_pd_l1/5X8L.pdb"

TARGET_CHAIN = "A"          # PD-L1
ANTIBODY_CHAINS = ["F", "K"]   # Heavy + Light
CUTOFF = 5.0

parser = PDBParser(QUIET=True)
structure = parser.get_structure("complex", PDB_FILE)
model = structure[0]

target = model[TARGET_CHAIN]

# Build NeighborSearch on antibody atoms
antibody_atoms = []
for chain_id in ANTIBODY_CHAINS:
    antibody_atoms.extend(list(model[chain_id].get_atoms()))

ns = NeighborSearch(antibody_atoms)

contacts = []

for residue in target:

    # Skip waters / hetero atoms
    if residue.id[0] != " ":
        continue

    for atom in residue:

        if ns.search(atom.coord, CUTOFF):

            contacts.append(residue)

            break

print("=" * 60)
print(f"PD-L1 contact residues within {CUTOFF} Å")
print("=" * 60)

numbers = []

for residue in contacts:

    resnum = residue.id[1]

    numbers.append(resnum)

    print(f"{TARGET_CHAIN} {resnum:3d} {residue.resname}")

print()

print("Residue numbers:")
print(numbers)

print()

crop_start = max(1, min(numbers) - 10)
crop_end = max(numbers) + 10

print(f"Suggested crop: {crop_start}-{crop_end}")
