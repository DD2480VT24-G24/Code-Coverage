# Code-Coverage

## Cyclomatic Complexity
- subtensor.py - `get_canonical_form_slice`: 23 edges, 10 nodes, 1 connected components =  15 CC
- ``belongs_to_set`` - #decisions = 17, #exit points = 7 => M = 12
- ``index_vars_to_types`` - #decisions = 22, #exit = 10 => M = 14
- math.py - `mean` : 28 nodes, 40 edges, 1 component = 14
- math.py `check_and_normalize_axes`:
    - Excluding raise as exit point #decisions = 19, #exit points = 1 => M = 20 (Same as Lizard tool)
    - Including raise as exit point #decisions = 19, #exit points = 3 => M = 18

## Statements of contribution
- Adam
    - Collaborated with Andreas & Casper to write the coverage tool
    - Analyzed CC for the function `index_vars_to_types`
    - Implemented CC improvement/reduction for the function `index_vars_to_types`
    - Implemented tests to increase branch coverage for the function `index_vars_to_types`
- Andreas
- Casper
- Martin:
    - Collaborated with Victor to create the project report
    - Analyzed CC for the function `check_and_normalize_axes`
    - Implemented CC improvement/reduction for the function `check_and_normalize_axes`
    - Implemented tests to increase branch coverage for the function `check_and_normalize_axes`
     
- Victor