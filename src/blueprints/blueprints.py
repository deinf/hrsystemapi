from src.blueprints.auth.auth import auth
from src.blueprints.user.user import user
from src.blueprints.department.department import department
from src.blueprints.payroll.payroll import payroll
from src.blueprints.attendance.attendance import attendance
from src.blueprints.leave.leave import leave
from src.blueprints.performance.performance import performance

__all__ = ['auth', 'user', 'department', 'payroll', 'attendance', 'leave', 'performance']