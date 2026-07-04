#!/usr/bin/env bash
set -euo pipefail

cd /workspace/RFantibody
export PYTHONPATH=/workspace/RFantibody/src:${PYTHONPATH:-}

mkdir -p scripts/examples/pdl1_outputs_fv_hotspot/set1

HYDRA_FULL_ERROR=1 python scripts/rfdiffusion_inference.py \
  --config-name antibody \
  antibody.target_pdb=/workspace/RFantibody/scripts/examples/pdl1_inputs/pdl1_A35_135.pdb \
  antibody.framework_pdb=/workspace/RFantibody/scripts/examples/example_inputs/hu-4D5-8_Fv.pdb \
  antibody.T_scheme=single_T_correct_selfcond \
  antibody.no_bugfix_t1d_mask=False \
  inference.ckpt_override_path=/workspace/RFantibody/weights/RFdiffusion_Ab.pt \
  inference.output_prefix=/workspace/RFantibody/scripts/examples/pdl1_outputs_fv_hotspot/set1/pdl1_fv_hotspot_set1 \
  inference.num_designs=5 \
  "ppi.hotspot_res=[A56,A59,A62,A66,A68,A69,A112,A117]"
