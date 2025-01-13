import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint, MetaData, func

# Create an instance of SQLAlchemy

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)

def generate_uuid():
    return str(uuid.uuid4())

# Employee Table
class Employee(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20))
    hire_date = db.Column(db.DateTime(timezone=True), default=func.now())
    position = db.Column(db.String(100))
    department_id = db.Column(db.String(36), db.ForeignKey('department.id', ondelete='SET NULL'))
    salary = db.Column(db.Float)
    status = db.Column(db.String(50), default="active")

    department = db.relationship('Department', back_populates='employee')
    leaves = db.relationship('Leave', back_populates='employee')
    attendance = db.relationship('Attendance', back_populates='employee')
    payroll = db.relationship('Payroll', back_populates='employee')
    performance = db.relationship('Performance', back_populates='employee')
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    
    
    @property
    def serialize(self):
        return {
            'first_name' : self.first_name,
            'last_name' : self.last_name,
            'position' :self. position,
            'salary' : self.salary,
            'status' : self.status,
            'hire_date' : self.hire_date,
            'created_at' : self.created_at,
            'updated_at' : self.updated_at
        }
        

# Department Table
class Department(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))

    employee = db.relationship('Employee', back_populates='department')
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    def __init__(self, name, location):
        self.name = name
        self.location = location

# Leave Table
class Leave(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    employee_id = db.Column(db.String(36), db.ForeignKey('employee.id'))
    leave_type = db.Column(db.String(50))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(50), default="pending")
    reason = db.Column(db.Text)

    employee = db.relationship('Employee', back_populates='leaves')
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def __init__(self, employee_id, leave_type, start_date, end_date, status, reason):
        self.employee_id = employee_id
        self.leave_type = leave_type
        self.start_date = start_date
        self.end_date = end_date
        self.status = status
        self.reason = reason

# Attendance Table
class Attendance(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    employee_id = db.Column(db.String(36), db.ForeignKey('employee.id'))
    date = db.Column(db.Date, default=datetime.utcnow)
    check_in_time = db.Column(db.Time)
    check_out_time = db.Column(db.Time)
    status = db.Column(db.String(50), default="present")

    employee = db.relationship('Employee', back_populates='attendance')
    
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    
    
    def __init__(self, employee_id, check_in_time, check_out_time, status):
        self.employee_id = employee_id
        self.check_in_time = check_in_time
        self.check_out_time = check_out_time
        self.status = status

# Payroll Table
class Payroll(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    employee_id = db.Column(db.String(36), db.ForeignKey('employee.id'))
    base_salary = db.Column(db.Float)
    bonus = db.Column(db.Float, default=0.0)
    deductions = db.Column(db.Float, default=0.0)
    net_salary = db.Column(db.Float)
    pay_date = db.Column(db.Date, default=datetime.utcnow)

    employee = db.relationship('Employee', back_populates='payroll')
    
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    

    def __init__(self, employee_id, base_salary, bonus, deductions, net_salary, pay_date):
        self.employee_id = employee_id
        self.base_salary = base_salary
        self.bonus = bonus
        self.deductions = deductions
        self.net_salary = net_salary
        self.pay_date = pay_date

# Performance Table
class Performance(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    employee_id = db.Column(db.String(36), db.ForeignKey('employee.id'))
    review_date = db.Column(db.Date, default=datetime.utcnow)
    rating = db.Column(db.Integer)
    feedback = db.Column(db.Text)

    employee = db.relationship('Employee', back_populates='performance')
    
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    

    def __init__(self, employee_id, rating, feedback):
        self.employee_id = employee_id
        self.rating = rating
        self.feedback = feedback

# User Table
class User(db.Model, UserMixin):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="employee")  # Admin, Employee, etc.
    employee_id = db.Column(db.String(36), db.ForeignKey('employee.id'))

    employee = db.relationship('Employee', cascade="all, delete", backref='user')

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    
    
