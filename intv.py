print("Welcome......")
students = {
    "james": 10,
    "dane": 2
}
get_user_type = input("Are you an existing user? (Y/N/quit): ")

def add_edit_student(name, score):
    students[name] = score
    return True

def remove_student(name):
    students.pop(name)
    return True


def logged_user(username, password):

    if username != password:
        return False
    print("Students    |   Score")
    for key, value in students.items():
        print(f"{key}   |   {value}")

    new_action = input("enter your next action (Add/Remove/Edit): ")

    if new_action.lower() == "add":
        new_stud = input("Enter student name: ")
        new_score = 0
        while True:
            score = input(f"Enter {new_stud} score: ")
            try:
                new_score += float(score)
                break
            except:
                print("Score must be float")

        add_edit_student(new_stud, new_score)
        print("Students    |   Score")
        for key, value in students.items():
            print(f"{key}   |   {value}")
        print(f"student:{new_stud} with score:{new_score} has been added")

    elif new_action.lower() == "remove":
        rem_stud = input("Enter student name: ")
        remove_student(rem_stud)

    elif new_action.lower() == "edit":
        et_stu = ''
        new_score = 0
        while True:
            edt_stud = input("Enter student name: ")

            if edt_stud not in students.keys():
                print("student doesn't exist")
                continue
            et_stu += edt_stud
            score = input(f"Enter {edt_stud} new score: ")
            try:
                new_score += float(score)
                break
            except:
                print("Score must be float")

        print(f"student:{edt_stud} with score:{new_score} has been change")
        add_edit_student(et_stu, new_score)
        print("Students    |   Score")
        for key, value in students.items():
            print(f"{key}   |   {value}")

if get_user_type.lower() == "y":
    username = input("Enter your username: ")
    password = input(f"Enter password of {username}")

    amp = logged_user(username, password)

    if amp == False:
        print("invalid username and password")

elif get_user_type.lower() == "n":
    username = input("Enter a username: ")
    password = input("Enter new password: ")

    amp = logged_user(username, password)
    if amp == False:
        print("cannot let password be same as username")
else:
    print("goodbye")