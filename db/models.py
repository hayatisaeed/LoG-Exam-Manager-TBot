from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Float, Table
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()

# Association tables for many-to-many relationships
teacher_groups = Table(
    'teacher_groups',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('group_id', Integer, ForeignKey('groups.id'))
)

student_groups = Table(
    'student_groups',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('group_id', Integer, ForeignKey('groups.id'))
)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    chat_id = Column(String, unique=True, nullable=True)
    fullname = Column(String, nullable=False)
    role = Column(String, nullable=False)
    profile_data = Column(String, nullable=True)
    teaching_groups = relationship('Group', secondary=teacher_groups, back_populates='teachers')
    student_groups = relationship('Group', secondary=student_groups, back_populates='students')


class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    teachers = relationship('User', secondary=teacher_groups, back_populates='teaching_groups')
    students = relationship('User', secondary=student_groups, back_populates='student_groups')


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
