import json
import math
import copy

# CONSTANTS
G = 9.8

# DATA LOADING

def load_input(path):
    with open(path) as f:
        data = json.load(f)
    return data

# PHYSICS HELPERS
def max_corner_speed(friction, radius, crawl_speed):
    return math.sqrt(friction * G * radius) + crawl_speed

def time_to_change_speed(v_i, v_f, accel):
    return abs(v_f - v_i) / accel

 

 

def distance_to_change_speed(v_i, v_f, accel):

    return (v_f**2 - v_i**2) / (2 * accel)

 
class Simulator:
    def __init__(self, data):
        self.car = data["car"]
        self.track = data["track"]["segments"]
        self.race = data["race"]

    def simulate(self, strategy):
        total_time = 0
        current_speed = 0
        
        for seg, action in zip(self.track, strategy):
            if seg["type"] == "straight":
                t, current_speed = self.simulate_straight(
                    current_speed,
                    action["target_speed"],
                    seg["length_m"],
                    action["brake_point"]
                )
                total_time += t

            else:  # corner
                t, current_speed = self.simulate_corner(
                    current_speed,
                    seg["radius_m"],
                    seg["length_m"]
                )
                total_time += t
        return total_time

 

    def simulate_straight(self, v_i, target_speed, length, brake_point):

        accel = self.car["accel_m/se2"]

        brake = self.car["brake_m/se2"]

 

        # Accelerate phase

        t1 = time_to_change_speed(v_i, target_speed, accel)

        d1 = distance_to_change_speed(v_i, target_speed, accel)

 

        # Cruise phase

        d2 = max(0, brake_point - d1)

        t2 = d2 / target_speed if target_speed > 0 else 0

 

        # Braking phase (simplified: assume stop or next segment)

        t3 = 0

 

        total_time = t1 + t2 + t3

        return total_time, target_speed

 

    def simulate_corner(self, v_i, radius, length):

        crawl = self.car["crawl_constant_m/s"]

 

        # Assume constant friction (simplified for Level 1)

        friction = 1.0

 

        v_max = max_corner_speed(friction, radius, crawl)

 

        if v_i > v_max:

            # crash penalty

            penalty = self.race["corner_crash_penalty_s"]

            return penalty + (length / crawl), crawl

        else:

            return length / v_i, v_i

 

 

# =========================

# OPTIMIZER

# =========================

 

class Optimizer:

 

    def __init__(self, simulator):

        self.sim = simulator

 

    def initial_strategy(self):

        """Start with safe speeds"""

        strategy = []

 

        for seg in self.sim.track:

            if seg["type"] == "straight":

                strategy.append({

                    "target_speed": 30,   # safe default

                    "brake_point": seg["length_m"] * 0.7

                })

            else:

                strategy.append({})

 

        return strategy

 

    def mutate(self, strategy):

        import random

        new = copy.deepcopy(strategy)

 

        for i, seg in enumerate(self.sim.track):

            if seg["type"] == "straight":

                new[i]["target_speed"] += random.uniform(-5, 5)

                new[i]["target_speed"] = max(5, new[i]["target_speed"])

 

        return new

 

    def optimize(self, iterations=200):

        best = self.initial_strategy()

        best_time = self.sim.simulate(best)

 

        for _ in range(iterations):

            candidate = self.mutate(best)
            t = self.sim.simulate(candidate)

            if t < best_time:
                best = candidate
                best_time = t
        return best, best_time

def main():
    data = load_input("input.json")
    sim = Simulator(data)
    opt = Optimizer(sim)
    best_strategy, best_time = opt.optimize()
    print("Best Time:", best_time)
    print("Strategy:", json.dumps(best_strategy, indent=2))

if __name__ == "__main__":
    main()
