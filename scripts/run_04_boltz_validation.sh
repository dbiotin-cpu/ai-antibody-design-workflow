#!/usr/bin/env bash
set -euo pipefail

source /workspace/miniconda3/etc/profile.d/conda.sh
conda activate Boltz

cd /workspace/RFantibody_PDL1

boltz predict boltz_final_candidate/final_candidate_boltz.yaml \
  --out_dir boltz_final_candidate/boltz_output \
  --use_msa_server
