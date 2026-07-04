#!/usr/bin/env bash
set -euo pipefail

cd /workspace/RFantibody

export PYTHONPATH=/workspace/RFantibody/include/SE3Transformer:/workspace/RFantibody/src:${PYTHONPATH:-}

mkdir -p scripts/examples/pdl1_outputs_fv_hotspot/set1_top2/rf2_predictions_fixed

python scripts/rf2_predict.py \
  input.pdb_dir=/workspace/RFantibody/scripts/examples/pdl1_outputs_fv_hotspot/set1_top2/proteinmpnn_sequences \
  output.pdb_dir=/workspace/RFantibody/scripts/examples/pdl1_outputs_fv_hotspot/set1_top2/rf2_predictions_fixed \
  inference.num_recycles=5 \
  inference.cautious=True \
  inference.hotspot_show_proportion=0.1 \
  model.model_weights=/workspace/RFantibody/weights/RF2_ab.pt
