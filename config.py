# Weight related probabilities
PROBABILITY_WEIGHT_MUTATION = 0.8
PROBABILITY_INDIVIDUAL_WEIGHT_PERTURBATION = 0.9
PROBABILITY_INDIVIDUAL_WEIGHT_REASSIGNMENT = 0.1

WEIGHT_SHIFT_STRENGTH = 0.3
WEIGHT_RANDOM_STRENGTH = 1

# Node related probabilities
PROBABILITY_NODE_MUTATION = 0.2

# Connection related probabilities
PROBABILITY_CONNECTION_MUTATION = 0.2
PROBABILITY_CROSSOVER_CONNECTION_DISABLED = 0.75 # chance that an inherited gene was disabled if it was disabled in either parent

# DISTANCE FUNCTION PARAMETERS
DISTANCE_EXCESS_GENES_IMPORTANCE = 1 # Importance of excess genes in determining distance
DISTANCE_DISJOINT_GENES_IMPORTANCE = 1 # Importance of disjoint genes in determining distance
DISTANCE_AVG_WEIGHT_DIFF_IMPORTANCE = 1 # Importance of average weight difference in determining distance