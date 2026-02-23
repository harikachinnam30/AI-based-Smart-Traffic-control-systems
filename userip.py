import random
import csv

# Your existing functions and fuzzy rules stay the same...
# Fuzzy sets
waitingTrafficFuzzySet = ['minimal', 'light', 'average', 'heavy']
oncomingTrafficFuzzySet = ['minimal', 'light', 'average', 'heavy']
pedestrianFuzzySet = ['none', 'few', 'many']
weatherFuzzySet = ['clear', 'rainy', 'foggy']
durationFuzzySet = ['short', 'medium', 'long']
durationMapping = {'short': (20, 50), 'medium': (51, 80), 'long': (81, 130)}

# Fuzzy rules
fuzzyRules = [
   # Minimal waiting traffic
    (['minimal', 'minimal', 'none', 'clear'], 'short'),
    (['minimal', 'minimal', 'none', 'rainy'], 'short'),
    (['minimal', 'minimal', 'none', 'foggy'], 'short'),
    (['minimal', 'minimal', 'few', 'clear'], 'short'),
    (['minimal', 'minimal', 'few', 'rainy'], 'medium'),
    (['minimal', 'minimal', 'few', 'foggy'], 'medium'),
    (['minimal', 'minimal', 'many', 'clear'], 'medium'),
    (['minimal', 'minimal', 'many', 'rainy'], 'medium'),
    (['minimal', 'minimal', 'many', 'foggy'], 'long'),

    (['minimal', 'light', 'none', 'clear'], 'short'),
    (['minimal', 'light', 'none', 'rainy'], 'medium'),
    (['minimal', 'light', 'none', 'foggy'], 'medium'),
    (['minimal', 'light', 'few', 'clear'], 'medium'),
    (['minimal', 'light', 'few', 'rainy'], 'medium'),
    (['minimal', 'light', 'few', 'foggy'], 'long'),
    (['minimal', 'light', 'many', 'clear'], 'medium'),
    (['minimal', 'light', 'many', 'rainy'], 'long'),
    (['minimal', 'light', 'many', 'foggy'], 'long'),

    # Light waiting traffic
    (['light', 'minimal', 'none', 'clear'], 'short'),
    (['light', 'minimal', 'none', 'rainy'], 'medium'),
    (['light', 'minimal', 'none', 'foggy'], 'medium'),
    (['light', 'minimal', 'few', 'clear'], 'medium'),
    (['light', 'minimal', 'few', 'rainy'], 'medium'),
    (['light', 'minimal', 'few', 'foggy'], 'medium'),
    (['light', 'minimal', 'many', 'clear'], 'medium'),
    (['light', 'minimal', 'many', 'rainy'], 'medium'),
    (['light', 'minimal', 'many', 'foggy'], 'long'),

    # Average waiting traffic
    (['average', 'average', 'none', 'clear'], 'medium'),
    (['average', 'average', 'none', 'rainy'], 'medium'),
    (['average', 'average', 'none', 'foggy'], 'long'),
    (['average', 'average', 'few', 'clear'], 'medium'),
    (['average', 'average', 'few', 'rainy'], 'medium'),
    (['average', 'average', 'few', 'foggy'], 'long'),
    (['average', 'average', 'many', 'clear'], 'long'),
    (['average', 'average', 'many', 'rainy'], 'long'),
    (['average', 'average', 'many', 'foggy'], 'long'),
    (['average', 'light', 'none', 'clear'], 'medium'),
    (['light', 'heavy', 'few', 'rainy'], 'long'),

    # Heavy waiting traffic
    (['heavy', 'minimal', 'none', 'clear'], 'medium'),
    (['heavy', 'minimal', 'none', 'rainy'], 'long'),
    (['heavy', 'minimal', 'none', 'foggy'], 'long'),
    (['heavy', 'minimal', 'few', 'clear'], 'medium'),
    (['heavy', 'minimal', 'few', 'rainy'], 'long'),
    (['heavy', 'minimal', 'few', 'foggy'], 'long'),
    (['heavy', 'minimal', 'many', 'clear'], 'long'),
    (['heavy', 'minimal', 'many', 'rainy'], 'long'),
    (['heavy', 'minimal', 'many', 'foggy'], 'long'),

    (['heavy', 'heavy', 'many', 'clear'], 'long'),
    (['heavy', 'heavy', 'many', 'rainy'], 'long'),
    (['heavy', 'heavy', 'many', 'foggy'], 'long'),

    # Catch-all rules for unhandled combinations
    (['minimal', 'minimal', 'none', 'clear'], 'short'),
    (['heavy', 'heavy', 'many', 'rainy'], 'long'),
    (['light', 'average', 'none', 'clear'], 'medium'),
    (['light', 'average', 'none', 'rainy'], 'medium'),
    (['light', 'average', 'none', 'foggy'], 'medium'),
    (['light', 'average', 'few', 'clear'], 'medium'),
    (['light', 'average', 'few', 'rainy'], 'medium'),
    (['light', 'average', 'few', 'foggy'], 'medium'),
    (['light', 'average', 'many', 'clear'], 'medium'),
    (['light', 'average', 'many', 'rainy'], 'medium'),
    (['light', 'average', 'many', 'foggy'], 'medium'),
    (['heavy', 'average', 'none', 'clear'], 'medium'),
    (['heavy', 'average', 'none', 'rainy'], 'long'),
    (['heavy', 'average', 'none', 'foggy'], 'long'),
    (['heavy', 'average', 'few', 'clear'], 'medium'),
    (['heavy', 'average', 'few', 'rainy'], 'long'),
    (['heavy', 'average', 'few', 'foggy'], 'long'),
    (['heavy', 'average', 'many', 'clear'], 'long'),
    (['heavy', 'average', 'many', 'rainy'], 'long'),
    (['heavy', 'average', 'many', 'foggy'], 'long'),
    (['minimal', 'light', 'many', 'clear'], 'medium'),
    (['minimal', 'light', 'many', 'rainy'], 'long'),
    (['minimal', 'light', 'many', 'foggy'], 'long'),
    (['light', 'light', 'many', 'clear'], 'medium'),
    (['light', 'light', 'many', 'rainy'], 'long'),
    (['light', 'light', 'many', 'foggy'], 'long'),
    (['average', 'heavy', 'many', 'clear'], 'long'),
    (['average', 'heavy', 'many', 'rainy'], 'long'),
    (['average', 'heavy', 'many', 'foggy'], 'long'),
    (['heavy', 'heavy', 'many', 'clear'], 'long'),
    (['heavy', 'heavy', 'many', 'rainy'], 'long'),
    (['heavy', 'heavy', 'many', 'foggy'], 'long'),
    (['light', 'light', 'many', 'foggy'], 'long'),
    (['light', 'light', 'few', 'clear'], 'medium'),
    (['light', 'light', 'few', 'rainy'], 'medium'),
    (['light', 'light', 'few', 'foggy'], 'medium'),
    (['heavy', 'heavy', 'few', 'clear'], 'medium'),
    (['heavy', 'heavy', 'few', 'foggy'], 'long'),

]
def carWaitingFunction(carsWaiting):
    membership = []
    membership.append(['minimal', max(0, min(1, (10 - carsWaiting) / 10))])
    membership.append(['light', max(0, min(1, (carsWaiting - 5) / 5 if carsWaiting >= 5 else 0, (15 - carsWaiting) / 5))])
    membership.append(['average', max(0, min(1, (carsWaiting - 10) / 10, (30 - carsWaiting) / 10))])
    membership.append(['heavy', max(0, min(1, (carsWaiting - 20) / 10))])
    return [m for m in membership if m[1] > 0] or [['minimal', 0]]


# Membership functions 
def carIncomingFunction(carsIncoming):
    membership = []
    membership.append(['minimal', max(0, min(1, (10 - carsIncoming) / 10))])
    membership.append(['light', max(0, min(1, (carsIncoming - 5) / 5 if carsIncoming >= 5 else 0, (15 - carsIncoming) / 5))])
    membership.append(['average', max(0, min(1, (carsIncoming - 10) / 10, (30 - carsIncoming) / 10))])
    membership.append(['heavy', max(0, min(1, (carsIncoming - 20) / 10))])
    return [m for m in membership if m[1] > 0] or [['minimal', 0]]

def pedestrianFunction(pedestrians):
    membership = []
    membership.append(['none', max(0, min(1, (5 - pedestrians) / 5))])
    membership.append(['few', max(0, min(1, (pedestrians - 3) / 2 if pedestrians >= 3 else 0, (10 - pedestrians) / 5))])
    membership.append(['many', max(0, min(1, (pedestrians - 8) / 2))])
    return [m for m in membership if m[1] > 0] or [['none', 0]]

def weatherFunction(weather):
    membership = []
    if weather == 'clear':
        membership.append(['clear', 1])
    elif weather == 'rainy':
        membership.append(['rainy', 1])
    elif weather == 'foggy':
        membership.append(['foggy', 1])
    return [m for m in membership if m[1] > 0]

# Inference function 
def infer(waitingTraffic, incomingTraffic, pedestrianTraffic, weatherCondition, fuzzyRules):
    possibleRules = []
    resultMax = {}

    for waiting in waitingTraffic:
        for incoming in incomingTraffic:
            for pedestrian in pedestrianTraffic:
                for weather in weatherCondition:
                    for rule in fuzzyRules:
                        if rule[0] == [waiting[0], incoming[0], pedestrian[0], weather[0]]:
                            membership_value = min(waiting[1], incoming[1], pedestrian[1], weather[1])
                            resultMax[rule[1]] = max(resultMax.get(rule[1], 0), membership_value)

    return resultMax
def duration_category(duration):
    """Determine the category of a duration based on the new mapping ranges."""
    for category, (low, high) in durationMapping.items():
        if low <= duration <= high:
            return category
    return None
def defuzzyfication(inference):
    durationCenters = {'short': 35, 'medium': 65, 'long': 105}
    numerator = 0
    denominator = 0
    for term, value in inference.items():
        numerator += durationCenters[term] * value
        denominator += value
    return numerator / denominator if denominator != 0 else 0

while True:
    try:
        # User input
        print("\nEnter the following details:\n")
        waitingCars = int(input("Number of vehicles waiting: "))
        incomingCars = int(input("Number of vehicles incoming: "))
        pedestrians = int(input("Number of pedestrians: "))
        weather = input("Weather (clear/rainy/foggy): ").lower()
        if weather not in ['clear', 'rainy', 'foggy']:
            print("Invalid weather input. Please try again.")
            continue

        expected_duration = int(input("Enter the expected duration (in seconds): "))
        waitingTraffic = carWaitingFunction(waitingCars)
        incomingTraffic = carIncomingFunction(incomingCars)
        pedestrianTraffic = pedestrianFunction(pedestrians)
        weatherCondition = weatherFunction(weather)
        # Perform inference and defuzzification
        inferenceResult = infer(waitingTraffic, incomingTraffic, pedestrianTraffic, weatherCondition, fuzzyRules)
        predicted_duration = defuzzyfication(inferenceResult)
        predicted_category = duration_category(predicted_duration)
        expected_category = duration_category(expected_duration)
        print("--- Prediction Results ---")
        print(f"Predicted Duration: {predicted_duration:.2f} seconds")
        print(f"Predicted Category: {predicted_category}")
        print(f"Expected Category: {expected_category}")
        if predicted_category == expected_category:
            print("✅ Prediction matches the expected category.")
        else:
            print("❌ Prediction does not match the expected category.")
        again = input("\nDo you want to test another input? (yes/no): ").lower()
        if again != 'yes':
            break
    except ValueError:
        print("Invalid input. Please enter the correct data format.")

