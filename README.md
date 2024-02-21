# Code-Coverage

## Cyclomatic Complexity
- subtensor.py - `get_canonical_form_slice`: 23 edges, 10 nodes, 1 connected components =  15 CC
- math.py - `mean` : 28 nodes, 40 edges, 1 component = 14
- ``belongs_to_set`` - #decisions = 17, #exit points = 7 => M = 12
- math.py `check_and_normalize_axes`:
    - Excluding raise as exit point #decisions = 19, #exit points = 1 => M = 20 (Same as Lizard tool)
    - Including raise as exit point #decisions = 19, #exit points = 3 => M = 18

