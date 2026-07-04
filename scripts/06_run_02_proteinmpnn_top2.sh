#!/usr/bin/env bash
set -euo pipefail

cd /workspace/RFantibody
export PYTHONPATH=/workspace/RFantibody/src:${PYTHONPATH:-}

mkdir -p scripts/examples/pdl1_outputs_fv_hotspot/set1_top2

cp scripts/examples/pdl1_outputs_fv_hotspot/set1/pdl1_fv_hotspot_set1_1.pdb \
   scripts/examples/pdl1_outputs_fv_hotspot/set1_top2/

cp scripts/examples/pdl1_outputs_fv_hotspot/set1/pdl1_fv_hotspot_set1_4.pdb \
   scripts/examples/pdl1_outputs_fv_hotspot/set1_top2/

mkdir -p scripts/examples/pdl1_outputs_fv_hotspot/set1_top2/proteinmpnn_sequences

python scripts/proteinmpnn_interface_design.py \
  -pdbdir scripts/examples/pdl1_outputs_fv_hotspot/set1_top2 \
  -outpdbdir scripts/examples/pdl1_outputs_fv_hotspot/set1_top2/proteinmpnn_sequences \
  -checkpoint_path weights/ProteinMPNN_v48_noise_0.2.pt \
  -loop_string H1,H2,H3,L1,L2,L3 \
  -seqs_per_struct 5 \
  -temperature 0.1
