# Code-Coverage

## Cyclomatic Complexity
- subtensor.py - `get_canonical_form_slice`: 23 edges, 10 nodes, 1 connected components =  15 CC
- ``belongs_to_set`` - #decisions = 17, #exit points = 7 => M = 12
- ``index_vars_to_types`` - #decisions = 22, #exit = 10 => M = 14
- math.py - `mean` : 28 nodes, 40 edges, 1 component = 14
- math.py `check_and_normalize_axes`:
    - Excluding raise as exit point #decisions = 19, #exit points = 1 => M = 20 (Same as Lizard tool)
    - Including raise as exit point #decisions = 19, #exit points = 3 => M = 18

## Test Covarage
- math.py - `mean`: 40.00% -> 55.00%
- math.py - `check_and_normalize_axes`: 0% (None) -> 50.00%
- subtensor.py - `get_canonical_form_slice`: 73.08% -> 92.31%
- subtensor.py - `index_vars_to_type`: 35.29% -> 70.59%
- rewriting.py - `belongs_to_set`: 0% -> 62.50%
