from db_setup import get_db_session
from models import User, Group


def add_test_data():
    try:
        with get_db_session() as session:
            # Add users with unique user IDs
            admin = User(user_id="admin_001", name="Admin User", role="admin")
            teacher = User(user_id="teacher_001", name="Teacher User", role="teacher")
            student = User(user_id="student_001", name="Student User", role="student")
            session.add_all([admin, teacher, student])

            # Add a group
            group = Group(name="Group A")
            group.teachers.append(teacher)
            group.students.append(student)
            session.add(group)

            session.commit()
            print("Test data added!")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    add_test_data()
