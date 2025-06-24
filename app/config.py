# app/config.py
"""
Central RBAC policy.
Maps each role to the list of departments it can access.
"""

ROLE_ACCESS = {
    "employee":     ["general"],
    "finance":      ["finance", "general"],
    "marketing":    ["marketing", "general"],
    "hr":           ["hr", "general"],
    "engineering":  ["engineering", "general"],
    "c_level":      ["finance", "marketing", "hr", "engineering", "general"],
}
