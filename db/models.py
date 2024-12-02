from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Float, Table
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()

# Association tables for many-to-many relationships
group_students = Table(
    'group_students', Base.metadata,
    Column('group_id', Integer, ForeignKey('groups.id')),
    Column('student_id', Integer, ForeignKey('users.id'))
)

group_teachers = Table(
    'group_teachers', Base.metadata,
    Column('group_id', Integer, ForeignKey('groups.id')),
    Column('teacher_id', Integer, ForeignKey('users.id'))
)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)  # Auto-incremented primary key
    user_id = Column(String, unique=True, nullable=True)  # Unique user identifier
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'student', 'teacher', 'admin'
    profile_data = Column(String)



class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    students = relationship('User', secondary=group_students, backref='groups_as_student')
    teachers = relationship('User', secondary=group_teachers, backref='groups_as_teacher')


class Exam(Base):
    __tablename__ = 'exams'
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id'))
    file_path = Column(String, nullable=False)
    deadline = Column(DateTime)


class Submission(Base):
    __tablename__ = 'submissions'
    id = Column(Integer, primary_key=True)
    exam_id = Column(Integer, ForeignKey('exams.id'))
    student_id = Column(Integer, ForeignKey('users.id'))
    file_path = Column(String, nullable=False)
    upload_time = Column(DateTime)
    duration = Column(Float)  # Time taken to upload after download
    score = Column(Float)
