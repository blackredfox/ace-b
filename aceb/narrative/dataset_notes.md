# Dataset Notes

RCS-1 uses a procedurally generated synthetic dataset rather than a fixed corpus.

Each episode is represented by `EpisodeSpec` with the following fields:

- `episode_id`: deterministic episode identifier
- `alphabet`: the symbol set used in the episode
- `input_stream`: ordered sequence of input symbols shown to the agent
- `shift_pre`: cyclic shift rule before the hidden change
- `shift_post`: cyclic shift rule after the hidden change
- `switch_step`: hidden boundary where the active rule changes
- `history_window`: maximum amount of recent interaction history exposed to the agent
- `seed`: deterministic seed for episode reproduction

Why this dataset design is useful:

- It is **procedural**: episodes are generated from configuration + seed, reducing memorization of fixed examples.
- It is **verifiable**: the correct answer for every step is determined exactly by the active rule and current input symbol.
- It is **low-ambiguity**: there is no subjective labeling; correctness is rule-based.
- It supports **controlled variation**: benchmark difficulty and episode structure can be changed without breaking determinism.

All labels are generated from deterministic rule application, so ground truth is verifiable and ambiguity is minimized by construction.

In short, the benchmark uses synthetic episodes to isolate adaptation under hidden rule change while keeping correctness fully auditable.
