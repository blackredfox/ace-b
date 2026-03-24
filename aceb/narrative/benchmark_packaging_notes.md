# Benchmark Packaging Notes

What still needs to be mapped into Kaggle Benchmarks SDK format:

- **Task input:** current observation for a step (`step_id`, `input_symbol`, bounded history, last feedback)
- **Expected output:** one predicted symbol from the episode alphabet
- **Verification logic:** compare predicted symbol against the active rule output defined by the episode specification and current step
- **Benchmark grouping:** a benchmark bundle of procedurally generated RCS-1 episodes sharing the same generation config, with baseline-comparison and evaluator logic applied over completed trajectories

This note is for packaging readiness only; it is not the SDK migration itself.