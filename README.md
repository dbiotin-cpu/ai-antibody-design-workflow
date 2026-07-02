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



<p align="center">
  <img src="figures/workflow.png" alt="AI Antibody Design Workflow" width="900">
</p>



---

# Methods

## 1. Epitope Extraction

To focus the design on the antibody binding site, interface residues between PD-L1 and Atezolizumab were identified from the experimentally determined complex (PDB: 5X8L). Residues within **5 Å** of the antibody were extracted, and the target was cropped to residues **A35–A135** for subsequent antibody design.

<p align="center">
  <img src="figures/epitope_extraction.png" alt="PD-L1 epitope extraction" width="850">
</p>

<p align="center">
<b>Figure 2.</b> Epitope identification from the PD-L1–Atezolizumab complex. Interface residues (red) were extracted and used to define the cropped PD-L1 target (A35–A135).
</p>

---

## 2. Target Cropping

The PD-L1 target was reduced to residues A35–135.

Cropping reduces computational cost while preserving the complete antibody epitope.

---

## 3. RFantibody Backbone Generation

The cropped PD-L1 structure was used as the design target for RFantibody. The model generated multiple de novo antibody backbone candidates positioned to recognize the selected epitope.

<p align="center">
  <img src="figures/RFantibody_Design.png" alt="RFantibody backbone generation" width="850">
</p>

<p align="center">
<b>Figure 3.</b> Representative RFantibody-generated antibody backbone docked against the cropped PD-L1 target. PD-L1 is shown in cyan, while the designed antibody heavy and light chains are shown in orange and yellow, respectively.
</p>
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
