# AI-Guided De Novo Antibody Design Against PD-L1

An end-to-end computational antibody design workflow using **RFantibody**, **ProteinMPNN**, **RoseTTAFold2 (RF2)**, and **Boltz**.

This project demonstrates how open-source AI models can be integrated into a reproducible antibody discovery pipeline, starting from a known antigen structure and ending with independent structural validation.

---

# Project Overview

Unlike conventional tutorials that simply reproduce published examples, this project applies RFantibody to a new target:

- **Target:** Human PD-L1
- **Reference complex:** Atezolizumab–PD-L1 (PDB: 5X8L)
- **Objective:** Generate novel antibody candidates against the PD-L1 epitope using an AI-driven workflow.

---

# Workflow

```

PD-L1 crystal structure (5X8L)
│
├── Extract epitope residues
│
├── Crop target structure
│
├── RFantibody
│ Backbone generation
│
├── ProteinMPNN
│ Sequence design
│
├── RoseTTAFold2
│ Structure prediction
│
└── Boltz
Independent structural validation

```

---

# Methods

## 1. Epitope Extraction

Starting from the experimentally determined Atezolizumab–PD-L1 complex (PDB: 5X8L), interface residues were identified using Biopython.

Contact residues within 5 Å were extracted and used to define the target epitope.

Example:

```

PD-L1 contact residues

45, 49, 51...
111–125

Suggested crop:
A35–135

```

---

## 2. Target Cropping

The PD-L1 target was reduced to residues A35–135.

Cropping reduces computational cost while preserving the complete antibody epitope.

---

## 3. RFantibody

RFantibody generated de novo antibody backbones against the cropped PD-L1 target.

Output:

- 10 backbone candidates

---

## 4. ProteinMPNN

ProteinMPNN designed amino acid sequences compatible with each generated backbone.

Output:

- 5 sequence designs per backbone

---

## 5. RoseTTAFold2

RF2 predicted folded antibody-antigen complex structures.

Output:

- Predicted complexes for each designed sequence

---

## 6. Boltz

Boltz independently evaluated the predicted antibody-antigen complex.

Unlike RF2, Boltz was not involved in generating the candidate structures, providing an independent assessment of structural confidence.

---

# Results

## Pipeline Summary

| Step | Output |
|------|--------|
| RFantibody | 10 antibody backbones |
| ProteinMPNN | 5 sequences per backbone |
| RF2 | Predicted folded complexes |
| Boltz | Independent structural validation |

---

## Representative Candidate

Candidate:

```

pdl1_ab_des_0_dldesign_0

```

Boltz metrics:

| Metric | Value |
|--------|------:|
| Confidence Score | **0.937** |
| ipTM | **0.913** |
| pTM | **0.939** |
| Complex pLDDT | **0.943** |

These values indicate a highly confident predicted antibody–PD-L1 complex.

---

# Repository Structure

```

data/
input/
output/

scripts/
extract_pdl1_epitope.py
crop_pdl1_target.py
extract_candidate_sequences.py

results/
rfantibody/
proteinmpnn/
rf2/
boltz/

```

---

# Limitations

This project demonstrates computational antibody design only.

The generated antibody has **not** been experimentally validated.

Future work includes:

- Binding affinity prediction
- Interface analysis
- Molecular dynamics
- Experimental validation

---

# References

- RFantibody
- ProteinMPNN
- RoseTTAFold2
- Boltz
