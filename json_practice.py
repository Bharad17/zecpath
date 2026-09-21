import json

students = [
    {"id": 1, "name": "Rahul", "age": 21},
    {"id": 2, "name": "Anu", "age": 22}
]

# Write data to JSON
with open("students.json", "w") as file:
    json.dump(students, file, indent=4)

print("Data written to students.json")

# Read data from JSON
with open("students.json", "r") as file:
    data = json.load(file)

print("\nData read from JSON:")
for student in data:
    print(student)