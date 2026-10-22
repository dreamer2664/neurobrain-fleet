# spec: the 4 GB budget (owner: agent 1)

Target machine: 8 GB RAM, slow dual/quad-core CPU, no GPU, Windows-first,
Linux supported. brainbox may use **at most 4096 MB RSS** including Python,
weights, KV cache, screenshots and the HTTP server. Design headroom: aim for
3000 MB so the OS and the user's apps breathe.

Allocation plan (agent 7 owns the numbers):

| component | budget | notes |
|---|---|---|
| python + torch runtime | 400 MB | measure real RSS, not estimates |
| language model weights | 600 MB | int8 if needed |
| KV cache + activations | 500 MB | ctx 256, batch 1 |
| vision model | 200 MB | GripNet is small already |
| screenshot buffers | 100 MB | downscale to 1280x720 for grounding |
| room to spike | 1200 MB | OS, temp, fragmentation |

Non-negotiables:

- `/health` reports RSS; a watchdog kills and restarts the server above 3.8 GB.
- Benchmarks must run on 2 threads to match the target class of machine.
- A model that cannot hit 4 GB is not shippable, no matter its loss.
