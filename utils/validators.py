def validate_role(role):
    valid_roles = ["admin", "teacher", "student"]
    return role in valid_roles
