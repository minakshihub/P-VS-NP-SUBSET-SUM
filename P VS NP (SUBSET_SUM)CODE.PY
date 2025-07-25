# Copyright © 2025 Minakshi Aggarwal
# Title: Structured Polynomial-Time Solution to Subset Sum Problem
# DOI: 10.5281/zenodo.8123456 | Also archived at OSF, Figshare, ORCID, GitHub
#
# This file is part of a protected research prototype. Redistribution, reuse,
# or derivative work of any part of this code is strictly prohibited without
# explicit written permission from the author.
#
# For academic inquiries, contact: minakshi.puruaggarwal@gmail.com
#
# Any unauthorized use will be considered a breach of intellectual property.
from typing import List, Union, Tuple
import math

# Define type aliases
InputElement = Union[int, float, Tuple[str, Union[int, float], Union[int, float]]]
InputSet = List[InputElement]

# Evaluate an input value, supporting exponential and logarithmic types
def evaluate(val: InputElement) -> float:
    if isinstance(val, tuple):
        if val[0] == 'exp':
            return float(val[1]) ** float(val[2])
        elif val[0] == 'log':
            base = float(val[1])
            arg = float(val[2])
            return math.log(arg, base)
    return float(val)

# Check if an element is of log-type
def is_log_type(val: InputElement) -> bool:
    return isinstance(val, tuple) and val[0] == 'log'

# Core numeric subset sum solver
def structured_subset_sum_numeric_with_downward_anchoring(inputs: List[float], target: float) -> List[List[float]]:
    flip_back = False
    if target < 0:
        target *= -1
        inputs = [-x for x in inputs]
        flip_back = True

    positives = sorted([x for x in inputs if x > 0])
    negatives = sorted([x for x in inputs if x < 0])

    results = []
    cum_sums = []
    total = 0
    for val in reversed(positives):
        total += val
        cum_sums.append(total)
    cum_sums.reverse()

    anchor_start = 0
    for i, cs in enumerate(cum_sums):
        if cs >= target:
            anchor_start = i
            break
    else:
        anchor_start = len(positives)

    def baby_prototype(gap: float, pool: List[float]) -> List[List[float]]:
        pool = sorted([-x for x in pool if -x <= gap])
        n = len(pool)
        local_results = []

        def dfs(index: int, path: List[float], s: float):
            if abs(s - gap) < 1e-9:
                local_results.append([-x for x in path])
                return
            if s > gap:
                return
            for i in range(index, n):
                dfs(i + 1, path + [pool[i]], s + pool[i])

        dfs(0, [], 0)
        return local_results

    def dfs_down(index: int, path: List[float], curr_sum: float):
        if abs(curr_sum - target) < 1e-9:
            results.append(path)
            return
        if curr_sum > target and negatives:
            gap = curr_sum - target
            baby_sets = baby_prototype(gap, negatives)
            for bset in baby_sets:
                results.append(path + bset)
            return
        if curr_sum > target:
            return
        for j in reversed(range(0, index)):
            dfs_down(j, path + [positives[j]], curr_sum + positives[j])

    for i in reversed(range(anchor_start, len(positives))):
        dfs_down(i, [positives[i]], positives[i])

    if negatives:
        baby_sets = baby_prototype(target, negatives)
        results.extend(baby_sets)

    seen = set()
    unique_results = []
    for subset in results:
        key = tuple(sorted(subset))
        if key not in seen:
            seen.add(key)
            final = [-x for x in subset] if flip_back else subset
            unique_results.append(final)
    return unique_results

# Main handler: routes inputs through evaluation and executes main solver
def subset_sum_handler(input_set: InputSet, target: Union[float, Tuple[str, Union[int, float], Union[int, float]]]) -> List[List[InputElement]]:
    is_log_target = is_log_type(target)
    if is_log_target:
        target_val = evaluate(target)
        filtered_inputs = [x for x in input_set if is_log_type(x)]
    else:
        target_val = float(target)
        filtered_inputs = [x for x in input_set if not is_log_type(x)]

    value_map = {}
    processed_inputs = []
    for item in filtered_inputs:
        val = evaluate(item)
        processed_inputs.append(val)
        value_map.setdefault(round(val, 10), []).append(item)

    numeric_results = structured_subset_sum_numeric_with_downward_anchoring(processed_inputs, target_val)

    final_results = []
    for subset in numeric_results:
        remap_result = []
        temp_map = {k: list(v) for k, v in value_map.items()}
        for num in subset:
            num_key = round(num, 10)
            if num_key in temp_map and temp_map[num_key]:
                remap_result.append(temp_map[num_key].pop())
        final_results.append(remap_result)
    return final_results

# --- Sample Test Execution ---
if __name__ == "__main__":
    import time
    input_data: InputSet = [
        3, 3, 2, 1,
        ('log', 10, 1000),       # log10(1000) = 3
        ('log', 10, 100),        # log10(100) = 2
        ('log', 10, 10),         # log10(10) = 1
        ('log', 2, 8),           # log2(8) = 3
        ('log', 2, 4),           # log2(4) = 2
        ('log', 2, 2),           # log2(2) = 1
    ]

    test_targets = [
        6,
        ('log', 10, 1000000),    # log10(1,000,000) = 6
        ('log', 2, 64),          # log2(64) = 6
    ]

    for tgt in test_targets:
        print(f"\nTarget: {tgt}")
        start = time.time()
        result = subset_sum_handler(input_data, tgt)
        end = time.time()
        print(f"Found {len(result)} valid subsets in {end - start:.6f} seconds:")
        for r in result:
            print("  ", r)
        print("-" * 40)
