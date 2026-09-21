students = [
    {"id": 1, "name": "Rahul", "age": 21},
    {"id": 2, "name": "Anu", "age": 22}
]


# CREATE
def add_student(student):
    students.append(student)


# READ
def display_students():
    for student in students:
        print(student)


# UPDATE
def update_student(student_id, new_age):
    for student in students:
        if student["id"] == student_id:
            student["age"] = new_age


# DELETE
def delete_student(student_id):
    global students
    students = [
        student for student in students
        if student["id"] != student_id
    ]


# Test CRUD operations

print("Initial students:")
display_students()

print("\nAfter CREATE:")
add_student({"id": 3, "name": "Bharadwaj", "age": 22})
display_students()

print("\nAfter UPDATE:")
update_student(1, 25)
display_students()

print("\nAfter DELETE:")
delete_student(2)
display_students()