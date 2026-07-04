#!/usr/bin/env python

"""
score_epitope_contacts.py

Purpose:
Rank RFantibody-designed PD-L1 binder candidates by how well they contact
the original atezolizumab epitope on PD-L1.

Default assumptions:
- Reference complex: 5X8L PDB
- PD-L1 chain in reference: chain A
- Atezolizumab chains in reference: chains F and K
- Designed PD-L1 target chain: chain T
- Designed antibody/binder chains: all chains except chain T
- Contact cutoff: 5 Å

Example:
python score_epitope_contacts.py \
  --reference 5x8l.pdb \
  --design_glob "pdl1_ab_des_*.pdb" \
  --ref_target_chain A \
  --ref_binder_chains F K \
  --design_target_chain T \
  --cutoff 5.0 \
  --out epitope_scores.csv
"""

import argparse
import csv
import glob
from pathlib import Path

from Bio.PDB import PDBParser, NeighborSearch, Superimposer, is_aa
from Bio.Align import PairwiseAligner


AA3_TO_1 = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C",
    "GLN": "Q", "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I",
    "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P",
    "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V",
}


def load_model(pdb_path):
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure(Path(pdb_path).stem, pdb_path)
    return structure[0]


def residue_key(residue):
    """
    Use residue number + insertion code as the residue identity.
    Example: residue 56 with no insertion code -> "56"
    """
    hetflag, resseq, icode = residue.id
    icode = icode.strip()
    return f"{resseq}{icode}" if icode else str(resseq)


def get_aa_residues(chain):
    return [res for res in chain if is_aa(res, standard=True)]


def get_sequence_and_residues(chain):
    residues = get_aa_residues(chain)
    seq = []

    for res in residues:
        resname = res.get_resname().upper()
        seq.append(AA3_TO_1.get(resname, "X"))

    return "".join(seq), residues


def heavy_atoms_from_residues(residues):
    atoms = []
    for res in residues:
        for atom in res:
            element = atom.element.strip().upper()
            if element != "H":
                atoms.append(atom)
    return atoms


def heavy_atoms_from_chains(chains):
    atoms = []
    for chain in chains:
        for res in get_aa_residues(chain):
            for atom in res:
                element = atom.element.strip().upper()
                if element != "H":
                    atoms.append(atom)
    return atoms


def contact_residue_keys(target_chain, binder_chains, cutoff):
    """
    Return target-chain residue keys that have any heavy atom within cutoff
    of any heavy atom in the binder chains.
    """
    target_residues = get_aa_residues(target_chain)
    target_atoms = heavy_atoms_from_residues(target_residues)
    binder_atoms = heavy_atoms_from_chains(binder_chains)

    if not target_atoms:
        raise ValueError(f"No target atoms found for chain {target_chain.id}")

    if not binder_atoms:
        raise ValueError("No binder atoms found")

    ns = NeighborSearch(binder_atoms)
    contacted = set()

    for atom in target_atoms:
        nearby = ns.search(atom.coord, cutoff, level="A")
        if nearby:
            contacted.add(residue_key(atom.get_parent()))

    return contacted


def build_ref_to_design_residue_map(ref_chain, design_chain):
    """
    Build residue correspondence between reference PD-L1 and designed PD-L1
    using sequence alignment.

    Returns:
    - ref_to_design: dict mapping reference residue key -> design residue key
    - design_to_ref: dict mapping design residue key -> reference residue key
    """
    ref_seq, ref_residues = get_sequence_and_residues(ref_chain)
    design_seq, design_residues = get_sequence_and_residues(design_chain)

    aligner = PairwiseAligner()
    aligner.mode = "local"
    aligner.match_score = 2
    aligner.mismatch_score = -1
    aligner.open_gap_score = -5
    aligner.extend_gap_score = -0.5

    alignments = aligner.align(ref_seq, design_seq)

    if len(alignments) == 0:
        raise ValueError("Could not align reference target chain to design target chain")

    alignment = alignments[0]

    ref_to_design = {}
    design_to_ref = {}

    # alignment.aligned contains aligned blocks:
    # alignment.aligned[0] = blocks in ref sequence
    # alignment.aligned[1] = blocks in design sequence
    for ref_block, design_block in zip(alignment.aligned[0], alignment.aligned[1]):
        ref_start, ref_end = ref_block
        design_start, design_end = design_block

        block_len = min(ref_end - ref_start, design_end - design_start)

        for i in range(block_len):
            ref_res = ref_residues[ref_start + i]
            design_res = design_residues[design_start + i]

            ref_key = residue_key(ref_res)
            design_key = residue_key(design_res)

            ref_to_design[ref_key] = design_key
            design_to_ref[design_key] = ref_key

    return ref_to_design, design_to_ref


def superpose_design_to_reference(ref_chain, design_chain, design_model, ref_to_design):
    """
    Superpose designed PD-L1 chain onto reference PD-L1 chain using CA atoms
    from mapped residues. This is useful for RMSD reporting and visualization.

    The contact score itself does not require superposition, because contacts are
    measured within each complex, but RMSD helps diagnose badly aligned designs.
    """
    ref_res_by_key = {residue_key(res): res for res in get_aa_residues(ref_chain)}
    design_res_by_key = {residue_key(res): res for res in get_aa_residues(design_chain)}

    fixed_atoms = []
    moving_atoms = []

    for ref_key, design_key in ref_to_design.items():
        ref_res = ref_res_by_key.get(ref_key)
        design_res = design_res_by_key.get(design_key)

        if ref_res is None or design_res is None:
            continue

        if "CA" in ref_res and "CA" in design_res:
            fixed_atoms.append(ref_res["CA"])
            moving_atoms.append(design_res["CA"])

    if len(fixed_atoms) < 3:
        return None

    sup = Superimposer()
    sup.set_atoms(fixed_atoms, moving_atoms)

    all_design_atoms = list(design_model.get_atoms())
    sup.apply(all_design_atoms)

    return sup.rms


def score_design(
    reference_model,
    design_path,
    ref_target_chain_id,
    ref_binder_chain_ids,
    design_target_chain_id,
    cutoff,
):
    design_model = load_model(design_path)

    ref_target_chain = reference_model[ref_target_chain_id]
    ref_binder_chains = [reference_model[c] for c in ref_binder_chain_ids]

    design_target_chain = design_model[design_target_chain_id]

    design_binder_chains = [
        chain
        for chain in design_model
        if chain.id != design_target_chain_id
    ]

    if not design_binder_chains:
        raise ValueError(
            f"{design_path}: no binder chains found. "
            f"Design target chain is set to {design_target_chain_id}; "
            "all other chains are treated as binder chains."
        )

    # Original atezolizumab epitope on reference PD-L1
    ref_epitope_keys = contact_residue_keys(
        target_chain=ref_target_chain,
        binder_chains=ref_binder_chains,
        cutoff=cutoff,
    )

    # Map reference PD-L1 residues to design PD-L1 residues
    ref_to_design, design_to_ref = build_ref_to_design_residue_map(
        ref_target_chain,
        design_target_chain,
    )

    # Superpose design PD-L1 to reference PD-L1 for RMSD reporting
    target_ca_rmsd = superpose_design_to_reference(
        ref_chain=ref_target_chain,
        design_chain=design_target_chain,
        design_model=design_model,
        ref_to_design=ref_to_design,
    )

    # Candidate contacts on designed PD-L1
    design_contact_keys = contact_residue_keys(
        target_chain=design_target_chain,
        binder_chains=design_binder_chains,
        cutoff=cutoff,
    )

    # Convert candidate contacts back to reference residue numbering
    design_contacts_as_ref = set()

    for design_key in design_contact_keys:
        ref_key = design_to_ref.get(design_key)
        if ref_key is not None:
            design_contacts_as_ref.add(ref_key)

    covered_epitope = ref_epitope_keys & design_contacts_as_ref
    off_epitope_contacts = design_contacts_as_ref - ref_epitope_keys

    epitope_size = len(ref_epitope_keys)
    design_contact_count = len(design_contacts_as_ref)
    covered_count = len(covered_epitope)
    off_epitope_count = len(off_epitope_contacts)

    epitope_coverage = covered_count / epitope_size if epitope_size else 0.0

    if design_contact_count > 0:
        epitope_precision = covered_count / design_contact_count
    else:
        epitope_precision = 0.0

    # Simple combined score:
    # high coverage is most important, then precision.
    combined_score = (0.7 * epitope_coverage) + (0.3 * epitope_precision)

    return {
        "design": Path(design_path).name,
        "combined_score": combined_score,
        "epitope_coverage": epitope_coverage,
        "epitope_precision": epitope_precision,
        "ref_epitope_residue_count": epitope_size,
        "covered_epitope_count": covered_count,
        "design_contact_count_mapped_to_ref": design_contact_count,
        "off_epitope_contact_count": off_epitope_count,
        "target_CA_RMSD_after_superpose": target_ca_rmsd,
        "covered_epitope_residues": ",".join(sorted(covered_epitope, key=residue_sort_key)),
        "missed_epitope_residues": ",".join(
            sorted(ref_epitope_keys - covered_epitope, key=residue_sort_key)
        ),
        "off_epitope_contact_residues": ",".join(
            sorted(off_epitope_contacts, key=residue_sort_key)
        ),
    }


def residue_sort_key(x):
    """
    Sort residue labels like 35, 36, 100A.
    """
    number = ""
    suffix = ""

    for char in x:
        if char.isdigit() or char == "-":
            number += char
        else:
            suffix += char

    try:
        number = int(number)
    except ValueError:
        number = 999999

    return number, suffix


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--reference",
        required=True,
        help="Reference PDB file, e.g. 5x8l.pdb",
    )

    parser.add_argument(
        "--design_glob",
        default="pdl1_ab_des_*.pdb",
        help='Glob pattern for designed complexes, e.g. "pdl1_ab_des_*.pdb"',
    )

    parser.add_argument(
        "--ref_target_chain",
        default="A",
        help="PD-L1 chain ID in the reference structure",
    )

    parser.add_argument(
        "--ref_binder_chains",
        nargs="+",
        default=["F", "K"],
        help="Atezolizumab antibody chain IDs in the reference structure",
    )

    parser.add_argument(
        "--design_target_chain",
        default="T",
        help="PD-L1 chain ID in designed complexes",
    )

    parser.add_argument(
        "--cutoff",
        type=float,
        default=5.0,
        help="Heavy-atom contact cutoff in Å",
    )

    parser.add_argument(
        "--out",
        default="epitope_scores.csv",
        help="Output CSV file",
    )

    args = parser.parse_args()

    reference_model = load_model(args.reference)

    design_paths = sorted(glob.glob(args.design_glob))

    if not design_paths:
        raise FileNotFoundError(
            f"No design PDB files found with pattern: {args.design_glob}"
        )

    rows = []

    for design_path in design_paths:
        print(f"Scoring {design_path}...")

        try:
            row = score_design(
                reference_model=reference_model,
                design_path=design_path,
                ref_target_chain_id=args.ref_target_chain,
                ref_binder_chain_ids=args.ref_binder_chains,
                design_target_chain_id=args.design_target_chain,
                cutoff=args.cutoff,
            )
            rows.append(row)

        except Exception as e:
            print(f"  WARNING: failed to score {design_path}: {e}")

    rows = sorted(
        rows,
        key=lambda r: (
            r["combined_score"],
            r["epitope_coverage"],
            r["epitope_precision"],
        ),
        reverse=True,
    )

    fieldnames = [
        "design",
        "combined_score",
        "epitope_coverage",
        "epitope_precision",
        "ref_epitope_residue_count",
        "covered_epitope_count",
        "design_contact_count_mapped_to_ref",
        "off_epitope_contact_count",
        "target_CA_RMSD_after_superpose",
        "covered_epitope_residues",
        "missed_epitope_residues",
        "off_epitope_contact_residues",
    ]

    with open(args.out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print()
    print(f"Done. Wrote results to: {args.out}")
    print()
    print("Top candidates:")
    print("-" * 80)

    for i, row in enumerate(rows[:10], start=1):
        rmsd = row["target_CA_RMSD_after_superpose"]
        rmsd_text = f"{rmsd:.2f}" if rmsd is not None else "NA"

        print(
            f"{i:2d}. {row['design']} | "
            f"score={row['combined_score']:.3f} | "
            f"coverage={row['epitope_coverage']:.3f} | "
            f"precision={row['epitope_precision']:.3f} | "
            f"target_CA_RMSD={rmsd_text}"
        )


if __name__ == "__main__":
    main()