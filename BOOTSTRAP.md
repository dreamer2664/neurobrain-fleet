# bootstrap — every agent, every fresh sandbox

Agents wake up in a wiped 2 GB sandbox with nothing installed. This file is the
first thing to run. It takes ~4 minutes and ends with a working training stack.

```bash
# 0) identity
export AGENT_ID=01            # change me: 01..08
export NTFY=https://ntfy.sh
export TOPIC=neuralbrain
export GH_TOKEN=$GITHUB_PAT   # provided by the operator (write access to the fleet repo)

# 1) toolchain
sudo apt-get update -qq && sudo apt-get install -y -qq git curl jq >/dev/null
python3 -m pip install --quiet torch --index-url https://download.pytorch.org/whl/cpu
python3 -m pip install --quiet numpy pillow matplotlib
python3 -c "import torch, numpy, PIL; print('stack ok', torch.__version__)"

# 2) repos
git clone -q https://github.com/dreamer2664/neurobrain.git ~/neurobrain
git clone -q https://x-access-token:$GH_TOKEN@github.com/dreamer2664/neurobrain-fleet.git ~/fleet
cd ~/fleet && git config user.name "agent-$AGENT_ID" && git config user.email "agent$AGENT_ID@fleet.local"
git checkout -q -B agent-$AGENT_ID

# 3) bus smoke test
./scripts/ntfy.sh pub "[$AGENT_ID] status: online. claimed: <one line>"

# 4) corpus (only if you need token streams; cached in the main repo if present)
cd ~/neurobrain
[ -f data/code_train.bin ] || python3 scripts/build_corpus.py \
    --max-code-bytes 160000000 --vocab-size 2048
```

If `data/code_train.bin` is missing and the build takes too long, use
`--max-code-bytes 40000000` for a 4× faster corpus and note it in STATUS.md.

## Rules of the sandbox

- 2 cores, 2 GB RAM, no GPU. `torch.set_num_threads(2)`; keep workers ≤ 2.
- Swap does not exist. Peak RSS above ~1.6 GB gets you OOM-killed. Measure it.
- The workspace snapshot keeps files under `~/` but drops `__pycache__`,
  `node_modules`, `dist`, `build`. Big binaries (>100 MB) may not survive a
  rollback — push anything you need to keep.
- No pretrained models, no API calls to language services, no downloaded
  weights. From scratch or it does not count.
