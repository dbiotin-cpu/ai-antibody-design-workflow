from Bio.PDB import PDBParser, PDBIO, Select

PDB_FILE = "/workspace/boltz_pd_l1/5X8L.pdb"
OUTPUT_FILE = "scripts/examples/pdl1_inputs/pdl1_A35_135.pdb"

CHAIN_ID = "A"
START = 35
END = 135

class CropSelect(Select):
    def accept_chain(self, chain):
        return chain.id == CHAIN_ID

    def accept_residue(self, residue):
        return residue.id[0] == " " and START <= residue.id[1] <= END

parser = PDBParser(QUIET=True)
structure = parser.get_structure("pdl1", PDB_FILE)

io = PDBIO()
io.set_structure(structure)
io.save(OUTPUT_FILE, CropSelect())

print(f"Saved {OUTPUT_FILE}")
