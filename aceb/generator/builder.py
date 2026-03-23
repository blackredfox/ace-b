from __future__ import annotations

import hashlib
import math
import random
import string

from aceb.config import BenchmarkConfig
from aceb.env.episode import EpisodeSpec


def build_episode_spec(config: BenchmarkConfig, episode_id: str) -> EpisodeSpec:
    alphabet = _build_alphabet(config.alphabet_size)
    episode_seed = _derive_episode_seed(config.seed, episode_id)
    rng = random.Random(episode_seed)

    input_stream = _build_input_stream(alphabet, config.input_length, rng)
    shift_pre, shift_post = _build_shift_pair(len(alphabet), rng)
    switch_step = _build_switch_step(config.input_length, config.switch_ratio_min, config.switch_ratio_max, rng)

    return EpisodeSpec(
        episode_id=episode_id,
        alphabet=alphabet,
        input_stream=input_stream,
        shift_pre=shift_pre,
        shift_post=shift_post,
        switch_step=switch_step,
        history_window=config.history_window,
        seed=episode_seed,
    )


def _build_alphabet(alphabet_size: int) -> list[str]:
    alphabet: list[str] = []

    for index in range(alphabet_size):
        if index < len(string.ascii_uppercase):
            alphabet.append(string.ascii_uppercase[index])
        else:
            alphabet.append(f"S{index}")

    return alphabet


def _derive_episode_seed(base_seed: int, episode_id: str) -> int:
    seed_material = f"{base_seed}:{episode_id}".encode("utf-8")
    seed_digest = hashlib.sha256(seed_material).digest()
    return int.from_bytes(seed_digest[:8], byteorder="big", signed=False)


def _build_input_stream(alphabet: list[str], input_length: int, rng: random.Random) -> list[str]:
    input_stream = [rng.choice(alphabet) for _ in range(input_length)]

    if len(set(input_stream)) == 1:
        repeated_symbol = input_stream[0]
        repeated_index = alphabet.index(repeated_symbol)
        input_stream[-1] = alphabet[(repeated_index + 1) % len(alphabet)]

    return input_stream


def _build_shift_pair(alphabet_size: int, rng: random.Random) -> tuple[int, int]:
    candidates = list(range(1, alphabet_size))
    shift_pre, shift_post = rng.sample(candidates, 2)

    if shift_pre % alphabet_size == shift_post % alphabet_size:
        raise ValueError("shift_pre and shift_post must not be modulo-equivalent")

    return shift_pre, shift_post


def _build_switch_step(
    input_length: int,
    switch_ratio_min: float,
    switch_ratio_max: float,
    rng: random.Random,
) -> int:
    lower_bound = math.ceil(input_length * switch_ratio_min)
    upper_bound = math.floor(input_length * switch_ratio_max)

    candidate_steps = [
        step
        for step in range(lower_bound, upper_bound + 1)
        if 0 < step < input_length - 1
    ]

    if not candidate_steps:
        raise ValueError("config does not allow a valid switch_step within the required bounds")

    return rng.choice(candidate_steps)
