import random
import numpy as np
from deap import base, creator, tools, algorithms
import matplotlib.pyplot as plt
from tabulate import tabulate
import pandas as pd
import os
# -------------------------------
# Set a fixed random seed for reproducibility
random.seed(42)
np.random.seed(42)
# -------------------------------

ENABLE_AREA_LIMITS = False  # Set to False to disable area restrictions

# Define area limits (only used if ENABLE_AREA_LIMITS = True)
CRANE_X_RANGE = (20, 40) if ENABLE_AREA_LIMITS else (0, 100)
CRANE_Y_RANGE = (40, 60) if ENABLE_AREA_LIMITS else (0, 100)
PICKUP_X_RANGE = (20, 90) if ENABLE_AREA_LIMITS else (0, 100)
PICKUP_Y_RANGE = (0, 30) if ENABLE_AREA_LIMITS else (0, 100)

# Define PPVC Components
PPVC_COMPONENTS = [
    {'x': 18.5, 'y': 14.5, 'width': 7, 'length': 3, 'height': 4.5, 'storeys': 1},   #1
    {'x': 18.5, 'y': 17.5, 'width': 7, 'length': 3, 'height': 4.5, 'storeys': 1},   #2
    {'x': 18.5, 'y': 20.5, 'width': 7, 'length': 3, 'height': 4.5, 'storeys': 1},   #3
    {'x': 19,   'y': 24.5, 'width': 6, 'length': 5, 'height': 4.5, 'storeys': 1},   #4
    {'x': 19,   'y': 29.5, 'width': 6, 'length': 5, 'height': 4.5, 'storeys': 1},   #5
    {'x': 18.5, 'y': 33.5, 'width': 7, 'length': 3, 'height': 4.5, 'storeys': 1},   #6
    {'x': 18.5, 'y': 36.5, 'width': 7, 'length': 3, 'height': 4.5, 'storeys': 1},   #7
    {'x': 18.5, 'y': 39.5, 'width': 7, 'length': 3, 'height': 4.5, 'storeys': 1},   #8
    {'x': 24.5, 'y': 21.5, 'width': 5, 'length': 11, 'height': 4.5, 'storeys': 1},  #9
    {'x': 24.5, 'y': 32.5, 'width': 5, 'length': 11, 'height': 4.5, 'storeys': 1},  #10
    {'x': 24.5, 'y': 43.5, 'width': 5, 'length': 11, 'height': 4.5, 'storeys': 1},  #11
    {'x': 32.5, 'y': 46.5, 'width': 11, 'length': 5, 'height': 4.5, 'storeys': 1},  #12
    {'x': 43.5, 'y': 46.5, 'width': 11, 'length': 5, 'height': 4.5, 'storeys': 1},  #13
    {'x': 46.5, 'y': 54.5, 'width': 5, 'length': 11, 'height': 4.5, 'storeys': 1},  #14
    {'x': 41,   'y': 51.5, 'width': 6, 'length': 5, 'height': 4.5, 'storeys': 1},   #15
    {'x': 40.5, 'y': 55.5, 'width': 7, 'length': 3, 'height': 4.5, 'storeys': 1},   #16
    {'x': 40.5, 'y': 58.5, 'width': 7, 'length': 3, 'height': 4.5, 'storeys': 1},   #17
    {'x': 40.5, 'y': 61.5, 'width': 7, 'length': 3, 'height': 4.5, 'storeys': 1},   #18
    {'x': 54.5, 'y': 46.5, 'width': 11, 'length': 5, 'height': 4.5, 'storeys': 1},  #19
    {'x': 51.5, 'y': 54.5, 'width': 5, 'length': 11, 'height': 4.5, 'storeys': 1},  #20
    {'x': 57,   'y': 51.5, 'width': 6, 'length': 5, 'height': 4.5, 'storeys': 1},   #21
    {'x': 57.5, 'y': 55.5, 'width': 7, 'length': 3, 'height': 4.5, 'storeys': 1},   #22
    {'x': 57.5, 'y': 58.5, 'width': 7, 'length': 3, 'height': 4.5, 'storeys': 1},   #23
    {'x': 57.5, 'y': 61.5, 'width': 7, 'length': 3, 'height': 4.5, 'storeys': 1},   #24
    {'x': 65.5, 'y': 46.5, 'width': 11, 'length': 5, 'height': 4.5, 'storeys': 1},  #25
    {'x': 76.5, 'y': 46.5, 'width': 11, 'length': 5, 'height': 4.5, 'storeys': 1},  #26
    {'x': 79.5, 'y': 54.5, 'width': 5, 'length': 11, 'height': 4.5, 'storeys': 1},  #27
    {'x': 74.5, 'y': 54.5, 'width': 5, 'length': 11, 'height': 4.5, 'storeys': 1},  #28
    {'x': 69.5, 'y': 54.5, 'width': 5, 'length': 11, 'height': 4.5, 'storeys': 1},  #29
    {'x': 85,   'y': 51.5, 'width': 6, 'length': 5, 'height': 4.5, 'storeys': 1},   #30
    {'x': 85.5, 'y': 55.5, 'width': 7, 'length': 3, 'height': 4.5, 'storeys': 1},   #31
    {'x': 85.5, 'y': 58.5, 'width': 7, 'length': 3, 'height': 4.5, 'storeys': 1},   #32
    {'x': 85.5, 'y': 61.5, 'width': 7, 'length': 3, 'height': 4.5, 'storeys': 1},   #33
    {'x': 79.5, 'y': 38.5, 'width': 5, 'length': 11, 'height': 4.5, 'storeys': 1},  #34
    {'x': 85,   'y': 41.5, 'width': 6, 'length': 5, 'height': 4.5, 'storeys': 1},   #35
    {'x': 85.5, 'y': 37.5, 'width': 7, 'length': 3, 'height': 4.5, 'storeys': 1},   #36
    {'x': 85.5, 'y': 34.5, 'width': 7, 'length': 3, 'height': 4.5, 'storeys': 1},   #37
    {'x': 85.5, 'y': 31.5, 'width': 7, 'length': 3, 'height': 4.5, 'storeys': 1},   #38
    {'x': 74.5, 'y': 38.5, 'width': 5, 'length': 11, 'height': 4.5, 'storeys': 1},  #39
    {'x': 69,   'y': 41.5, 'width': 6, 'length': 5, 'height': 4.5, 'storeys': 1},   #40
    {'x': 68.5, 'y': 37.5, 'width': 7, 'length': 3, 'height': 4.5, 'storeys': 1},   #41
    {'x': 68.5, 'y': 34.5, 'width': 7, 'length': 3, 'height': 4.5, 'storeys': 1},   #42
    {'x': 68.5, 'y': 31.5, 'width': 7, 'length': 3, 'height': 4.5, 'storeys': 1},   #43
]

# Crane Parameters
CRANE_SIZE = 5            # 5x5 meters
NO_LIFT_RADIUS = 5        # 5 m radius around crane
PICKUP_ZONE_WIDTH = 12    # Pickup zone width (meters)
PICKUP_ZONE_LENGTH = 5   # Pickup zone length (meters)
CRANE_RADIUS = 60         # Crane max reach
ROTATE_SPEED = 0.07        # Rotation speed (radians per second)
LIFT_SPEED = 0.6          # Lift speed (m/s)
MOVE_SPEED = 1.0          # Hook move speed (m/s)
DELAY_TIME = 5            # Seconds between actions

# Define Fitness Function using DEAP
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

def is_valid_location(center_x, center_y, width, length, exclude_areas):
    for area in exclude_areas:
        area_center_x = area['x']
        area_center_y = area['y']
        if not (center_x + width/2 <= area_center_x - area['width']/2 or
                center_x - width/2 >= area_center_x + area['width']/2 or
                center_y + length/2 <= area_center_y - area['length']/2 or
                center_y - length/2 >= area_center_y + area['length']/2):
            return False
    return True

def is_in_no_pickup_zone(crane_x, crane_y, pickup_x, pickup_y):
    distance = np.hypot(crane_x - pickup_x, crane_y - pickup_y)
    return distance < NO_LIFT_RADIUS

def pickup_zone_overlaps_ppvc(pickup_x, pickup_y, width, length, ppvc_components):
    for comp in ppvc_components:
        if not (pickup_x + width/2 <= comp['x'] - comp['width']/2 or
                pickup_x - width/2 >= comp['x'] + comp['width']/2 or
                pickup_y + length/2 <= comp['y'] - comp['length']/2 or
                pickup_y - length/2 >= comp['y'] + comp['length']/2):
            return True
    return False

def evaluate(individual):
    crane_x, crane_y, pickup_x, pickup_y = individual

    # Check against custom area limits first
    if not (CRANE_X_RANGE[0] <= crane_x <= CRANE_X_RANGE[1]):
        return (float('inf'),)
    if not (CRANE_Y_RANGE[0] <= crane_y <= CRANE_Y_RANGE[1]):
        return (float('inf'),)
    if not (PICKUP_X_RANGE[0] <= pickup_x <= PICKUP_X_RANGE[1]):
        return (float('inf'),)
    if not (PICKUP_Y_RANGE[0] <= pickup_y <= PICKUP_Y_RANGE[1]):
        return (float('inf'),)

    if not (0 <= crane_x <= 100 and 0 <= crane_y <= 100):
        return (float('inf'),)
    if np.hypot(crane_x - pickup_x, crane_y - pickup_y) > CRANE_RADIUS:
        return (float('inf'),)
    if is_in_no_pickup_zone(crane_x, crane_y, pickup_x, pickup_y):
        return (float('inf'),)
    valid_orientations = [
        is_valid_location(pickup_x, pickup_y, PICKUP_ZONE_WIDTH, PICKUP_ZONE_LENGTH, PPVC_COMPONENTS),
        is_valid_location(pickup_x, pickup_y, PICKUP_ZONE_LENGTH, PICKUP_ZONE_WIDTH, PPVC_COMPONENTS)
    ]
    if not any(valid_orientations):
        return (float('inf'),)
    for ppvc in PPVC_COMPONENTS:
        if np.hypot(crane_x - ppvc['x'], crane_y - ppvc['y']) > CRANE_RADIUS:
            return (float('inf'),)
    if pickup_zone_overlaps_ppvc(pickup_x, pickup_y, PICKUP_ZONE_WIDTH, PICKUP_ZONE_LENGTH, PPVC_COMPONENTS):
        return (float('inf'),)
    
    total_time = 0
    total_delay = 0  # Track total delay time

    for i, ppvc in enumerate(PPVC_COMPONENTS):
        dest_x = ppvc['x']
        dest_y = ppvc['y']
        height = ppvc['height']
        clearance = height + 3
        r_pickup = np.hypot(pickup_x - crane_x, pickup_y - crane_y)
        r_dest = np.hypot(dest_x - crane_x, dest_y - crane_y)
        angle_pickup = np.arctan2(pickup_y - crane_y, pickup_x - crane_x)
        angle_dest = np.arctan2(dest_y - crane_y, dest_x - crane_x)
        rotation_angle = abs(np.arctan2(np.sin(angle_dest - angle_pickup),
                                        np.cos(angle_dest - angle_pickup)))
        
        lift_to_clearance = max((clearance - PPVC_COMPONENTS[0]['height']) / LIFT_SPEED, 0)
        rotate_to_dest = rotation_angle / ROTATE_SPEED
        radial_move_to_dest = abs(r_dest - r_pickup) / MOVE_SPEED
        lower_at_dest = 3 / LIFT_SPEED
        
        # Delivery sequence (4 actions = 3 delays)
        delivery_delay = 3 * DELAY_TIME
        delivery_time = (lift_to_clearance + rotate_to_dest + 
                        radial_move_to_dest + lower_at_dest) + delivery_delay
        total_time += delivery_time
        total_delay += delivery_delay

        if i < len(PPVC_COMPONENTS) - 1:
            # ADD MISSING RETURN SEQUENCE CALCULATIONS
            next_ppvc = PPVC_COMPONENTS[i+1]
            next_clearance = next_ppvc['height'] + 3
            
            lift_back = 3 / LIFT_SPEED
            radial_move_back = abs(r_dest - r_pickup) / MOVE_SPEED
            rotate_back = rotation_angle / ROTATE_SPEED
            adjust_height = abs(next_clearance - clearance) / LIFT_SPEED
            lower_at_pickup = 3 / LIFT_SPEED

            # Now calculate return_time
            return_delay = 4 * DELAY_TIME
            return_time = (lift_back + radial_move_back + rotate_back + 
                          adjust_height + lower_at_pickup) + return_delay
            total_time += return_time
            total_delay += return_delay

    return (total_time,)

def evaluate_with_timings(individual):
    crane_x, crane_y, pickup_x, pickup_y = individual
    if not (0 <= crane_x <= 100 and 0 <= crane_y <= 100):
        return (float('inf'), [])
    if np.hypot(crane_x - pickup_x, crane_y - pickup_y) > CRANE_RADIUS:
        return (float('inf'), [])
    if is_in_no_pickup_zone(crane_x, crane_y, pickup_x, pickup_y):
        return (float('inf'), [])
    valid_orientations = [
        is_valid_location(pickup_x, pickup_y, PICKUP_ZONE_WIDTH, PICKUP_ZONE_LENGTH, PPVC_COMPONENTS),
        is_valid_location(pickup_x, pickup_y, PICKUP_ZONE_LENGTH, PICKUP_ZONE_WIDTH, PPVC_COMPONENTS)
    ]
    if not any(valid_orientations):
        return (float('inf'), [])
    for ppvc in PPVC_COMPONENTS:
        if np.hypot(crane_x - ppvc['x'], crane_y - ppvc['y']) > CRANE_RADIUS:
            return (float('inf'), [])
    if pickup_zone_overlaps_ppvc(pickup_x, pickup_y, PICKUP_ZONE_WIDTH, PICKUP_ZONE_LENGTH, PPVC_COMPONENTS):
        return (float('inf'), [])
    
    total_time = 0
    total_delay = 0   
    timings = []
    current_hook_height = PPVC_COMPONENTS[0]['height']
    r_pickup = np.hypot(pickup_x - crane_x, pickup_y - crane_y)
    angle_pickup = np.arctan2(pickup_y - crane_y, pickup_x - crane_x)
    
    for i, ppvc in enumerate(PPVC_COMPONENTS):
        dest_x = ppvc['x']
        dest_y = ppvc['y']
        height = ppvc['height']
        clearance = height + 3
        r_dest = np.hypot(dest_x - crane_x, dest_y - crane_y)
        angle_dest = np.arctan2(dest_y - crane_y, dest_x - crane_x)
        rotation_angle = abs(np.arctan2(np.sin(angle_dest - angle_pickup),
                                        np.cos(angle_dest - angle_pickup)))
        
        # Delivery sequence calculations
        lift_to_clearance = (clearance - current_hook_height) / LIFT_SPEED if clearance > current_hook_height else 0
        rotate_to_dest = rotation_angle / ROTATE_SPEED
        radial_move_to_dest = abs(r_dest - r_pickup) / MOVE_SPEED
        lower_at_dest = 3 / LIFT_SPEED
        
        # Delivery delays
        delivery_delay = 3 * DELAY_TIME
        delivery_time = (lift_to_clearance + rotate_to_dest + 
                        radial_move_to_dest + lower_at_dest) + delivery_delay
        total_time += delivery_time
        total_delay += delivery_delay
        step_timings = [lift_to_clearance, rotate_to_dest, 
                       radial_move_to_dest, lower_at_dest]

        if i < len(PPVC_COMPONENTS) - 1:
            # Add transition delay
            total_time += DELAY_TIME
            total_delay += DELAY_TIME
            step_timings.append(DELAY_TIME)

            # Return sequence calculations
            next_ppvc = PPVC_COMPONENTS[i+1]
            next_clearance = next_ppvc['height'] + 3
            
            # Calculate return movement times
            lift_back = 3 / LIFT_SPEED
            radial_move_back = abs(r_dest - r_pickup) / MOVE_SPEED
            rotate_back = rotation_angle / ROTATE_SPEED
            adjust_height = abs(next_clearance - clearance) / LIFT_SPEED
            lower_at_pickup = 3 / LIFT_SPEED

            # Return delays
            return_delay = 4 * DELAY_TIME
            return_time = (lift_back + radial_move_back + rotate_back + 
                          adjust_height + lower_at_pickup) + return_delay
            total_time += return_time
            total_delay += return_delay
            
            # Update tracking variables
            current_hook_height = next_ppvc['height']
            step_timings.extend([lift_back, radial_move_back, rotate_back,
                                adjust_height, lower_at_pickup])

        timings.append(step_timings)
    
    return (total_time, timings, total_delay)

def generate_individual(crane_x_range=CRANE_X_RANGE, crane_y_range=CRANE_Y_RANGE):
    while True:
        # Generate within specified limits for both crane and pickup
        crane_x = random.randint(CRANE_X_RANGE[0], CRANE_X_RANGE[1])
        crane_y = random.randint(CRANE_Y_RANGE[0], CRANE_Y_RANGE[1])
        pickup_x = random.randint(PICKUP_X_RANGE[0], PICKUP_X_RANGE[1])
        pickup_y = random.randint(PICKUP_Y_RANGE[0], PICKUP_Y_RANGE[1])

        if (is_valid_location(crane_x, crane_y, CRANE_SIZE, CRANE_SIZE, PPVC_COMPONENTS) and
            is_valid_location(pickup_x, pickup_y, PICKUP_ZONE_WIDTH, PICKUP_ZONE_LENGTH, PPVC_COMPONENTS) and
            not is_in_no_pickup_zone(crane_x, crane_y, pickup_x, pickup_y)):
            return creator.Individual([crane_x, crane_y, pickup_x, pickup_y])

def mutate(individual, indpb=0.2):
    # Get current area limits from configuration
    crane_x_min, crane_x_max = CRANE_X_RANGE
    crane_y_min, crane_y_max = CRANE_Y_RANGE
    pickup_x_min, pickup_x_max = PICKUP_X_RANGE
    pickup_y_min, pickup_y_max = PICKUP_Y_RANGE

    for i in range(len(individual)):
        if random.random() < indpb:
            # Apply Gaussian mutation with range clamping
            mutated_value = individual[i] + random.gauss(0, 5)
            
            # Clamp values to respective ranges
            if i == 0:  # Crane X
                mutated_value = max(crane_x_min, min(crane_x_max, mutated_value))
            elif i == 1:  # Crane Y
                mutated_value = max(crane_y_min, min(crane_y_max, mutated_value))
            elif i == 2:  # Pickup X
                mutated_value = max(pickup_x_min, min(pickup_x_max, mutated_value))
            elif i == 3:  # Pickup Y
                mutated_value = max(pickup_y_min, min(pickup_y_max, mutated_value))
            
            individual[i] = mutated_value
    return individual,

# -------------------------------
# Setup the DEAP toolbox and genetic algorithm components
toolbox = base.Toolbox()
toolbox.register("individual", generate_individual)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", evaluate)
toolbox.register("mate", tools.cxBlend, alpha=0.5)
toolbox.register("mutate", mutate)
toolbox.register("select", tools.selTournament, tournsize=3)
# -------------------------------

def optimize_crane_and_pickup():
    hof = tools.HallOfFame(1)
    population = toolbox.population(n=200)
    algorithms.eaSimple(population, toolbox, 0.7, 0.3, 500, halloffame=hof, verbose=False)
    
    if not hof:
        return None
        
    best_solution = hof[0]
    total_time, timings, total_delay = evaluate_with_timings(best_solution)
    return {
        'crane_location': (best_solution[0], best_solution[1]),
        'pickup_location': (best_solution[2], best_solution[3]),
        'total_time': total_time,
        'total_delay': total_delay,
        'movement_time': total_time - total_delay,
        'timings': timings
    }

def run_multiple_trials(trials=10):
    all_results = []  # Store all valid trial results
    best_time = float('inf')
    best_overall = None
    for i in range(trials):
        result = optimize_crane_and_pickup()
        if result:
            all_results.append(result)
            if result['total_time'] < best_time:
                best_overall = result
                best_time = result['total_time']
            print(f"Trial {i+1}: Total Time = {result['total_time']:.2f}s")
        else:
            print(f"Trial {i+1}: No solution found")
    return best_overall, all_results  # Return both best and all results

best_setup, all_trials = run_multiple_trials(trials=10)  # Unpack both returns

if best_setup:
    print("\nBest Overall Results:")
    print(f"Crane Position: {best_setup['crane_location']}")
    print(f"Pickup Zone: {best_setup['pickup_location']}")
    print(f"Total Movement Time: {best_setup['movement_time']:.2f}s")
    print(f"Total Delay Time: {best_setup['total_delay']:.2f}s")
    print(f"Combined Total Time: {best_setup['total_time']:.2f}s")

    # Prepare TRIAL RESULTS data for Excel
    trials_data = []
    for idx, trial in enumerate(all_trials):
        trials_data.append({
            "Trial": idx + 1,
            "Crane X": trial['crane_location'][0],
            "Crane Y": trial['crane_location'][1],
            "Pickup X": trial['pickup_location'][0],
            "Pickup Y": trial['pickup_location'][1],
            "Total Time (s)": trial['total_time'],
            "Movement Time (s)": trial['movement_time'],
            "Delay Time (s)": trial['total_delay']
        })
    trials_df = pd.DataFrame(trials_data)

    # Prepare summary data for Excel
    summary_data = {
        'Crane X': [best_setup['crane_location'][0]],
        'Crane Y': [best_setup['crane_location'][1]],
        'Pickup X': [best_setup['pickup_location'][0]],
        'Pickup Y': [best_setup['pickup_location'][1]],
        'Total Movement Time (s)': [best_setup['movement_time']],
        'Total Delay Time (s)': [best_setup['total_delay']],
        'Combined Total Time (s)': [best_setup['total_time']]
    }
    summary_df = pd.DataFrame(summary_data)

    # Prepare timings data for Excel
    headers = ["PPVC", "Lift", "→Rotate", "→Move", "→Lower", 
               "ΔDelay", "LiftB", "→MoveB", "→RotateB", "→Adjust", "→LowerP"]
    timings_list = []
    for i, timing in enumerate(best_setup['timings']):
        row = [i + 1]
        for t in timing:
            if isinstance(t, float):
                row.append(f"{t:.2f}s")
            else:
                row.append(f"Delay({t}s)")
        # Pad row to ensure all rows have the same length as headers
        while len(row) < len(headers):
            row.append('')
        timings_list.append(row)
    timings_df = pd.DataFrame(timings_list, columns=headers)
    
    # Prepare input parameters data for Excel
    input_params = {
        "Parameter": [
            "ENABLE_AREA_LIMITS",
            "CRANE_X_RANGE",
            "CRANE_Y_RANGE", 
            "PICKUP_X_RANGE",
            "PICKUP_Y_RANGE",
            "CRANE_SIZE",
            "NO_LIFT_RADIUS",
            "PICKUP_ZONE_WIDTH",
            "PICKUP_ZONE_LENGTH",
            "CRANE_RADIUS",
            "ROTATE_SPEED",
            "LIFT_SPEED",
            "MOVE_SPEED",
            "DELAY_TIME",
            "PPVC_COMPONENTS (Count)",
            "PPVC Component Structure"
        ],
        "Value": [
            ENABLE_AREA_LIMITS,
            f"{CRANE_X_RANGE[0]}-{CRANE_X_RANGE[1]}",
            f"{CRANE_Y_RANGE[0]}-{CRANE_Y_RANGE[1]}",
            f"{PICKUP_X_RANGE[0]}-{PICKUP_X_RANGE[1]}",
            f"{PICKUP_Y_RANGE[0]}-{PICKUP_Y_RANGE[1]}",
            f"{CRANE_SIZE} m",
            f"{NO_LIFT_RADIUS} m",
            f"{PICKUP_ZONE_WIDTH} m",
            f"{PICKUP_ZONE_LENGTH} m",
            f"{CRANE_RADIUS} m",
            f"{ROTATE_SPEED} rad/s",
            f"{LIFT_SPEED} m/s",
            f"{MOVE_SPEED} m/s",
            f"{DELAY_TIME} s",
            len(PPVC_COMPONENTS),
            "x,y,width,length,height,storeys"
        ],
        "Description": [
            "Whether area limits are enforced",
            "Allowed X range for crane position",
            "Allowed Y range for crane position",
            "Allowed X range for pickup zone",
            "Allowed Y range for pickup zone",
            "Crane physical size",
            "No-lift radius around crane",
            "Pickup zone width dimension",
            "Pickup zone length dimension", 
            "Maximum crane reach radius",
            "Crane rotation speed",
            "Vertical lifting speed",
            "Horizontal movement speed",
            "Delay between operations",
            "Number of PPVC components",
            "Structure of each PPVC component"
        ]
    }
    
    params_df = pd.DataFrame(input_params)
    
    # Define the output directory and file path
    output_directory = r"C:\Users\Besitzer\OneDrive\桌面\study\FYP\Final report\Different components"
    output_file_path = os.path.join(output_directory, "crane_optimization_results.xlsx")

    # Ensure the directory exists
    os.makedirs(output_directory, exist_ok=True)

    # Write to Excel using the full file path
    with pd.ExcelWriter(output_file_path) as writer:
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        trials_df.to_excel(writer, sheet_name='All Trials', index=False)  # New sheet
        timings_df.to_excel(writer, sheet_name='Operation Sequence', index=False)
        params_df.to_excel(writer, sheet_name='Input Parameters', index=False)
    print(f"\nData has been exported to '{output_file_path}'")

# Visualization
plt.figure(figsize=(8, 8))
for i, ppvc in enumerate(PPVC_COMPONENTS):
    rect = plt.Rectangle((ppvc['x'] - ppvc['width']/2, ppvc['y'] - ppvc['length']/2),
                         ppvc['width'], ppvc['length'],
                         color='gray', alpha=0.5, label='PPVC' if i==0 else "")
    plt.gca().add_patch(rect)
    plt.text(ppvc['x'], ppvc['y'], str(i+1), color='black', ha='center', va='center')
plt.scatter(*best_setup['crane_location'], color='red', label='Crane Location', marker='o', s=100)
plt.scatter(*best_setup['pickup_location'], color='blue', label='Pickup Location', marker='x', s=100)
crane_circle = plt.Circle(best_setup['crane_location'], CRANE_RADIUS, color='red', fill=False,
                          linestyle='dashed', label='Crane Reach')
plt.gca().add_patch(crane_circle)
pickup_rect = plt.Rectangle((best_setup['pickup_location'][0] - PICKUP_ZONE_WIDTH/2,
                             best_setup['pickup_location'][1] - PICKUP_ZONE_LENGTH/2),
                            PICKUP_ZONE_WIDTH, PICKUP_ZONE_LENGTH, color='blue', alpha=0.2, label='Pickup Zone')
plt.gca().add_patch(pickup_rect)
no_pickup_circle = plt.Circle(best_setup['crane_location'], NO_LIFT_RADIUS, color='red', fill=False,
                              linestyle='dotted', label='No Pickup Zone')
plt.gca().add_patch(no_pickup_circle)
plt.xlim(0, 100)
plt.ylim(0, 100)
plt.xlabel("X Coordinate")
plt.ylabel("Y Coordinate")
plt.title("Optimized Crane and Pickup Locations")
plt.legend()
plt.grid()
plt.show()
