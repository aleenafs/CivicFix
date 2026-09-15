# department.py
# MODULE 4: Smart Government Department Routing

ROUTING_TABLE = {
    'pothole':      'PWD - Roads and Buildings Dept',
    'road':         'PWD - Roads and Buildings Dept',
    'footpath':     'PWD - Roads and Buildings Dept',
    'fallen tree':  'GCC - Parks and Horticulture Dept',
    'tree':         'GCC - Parks and Horticulture Dept',
    'streetlight':  'TANGEDCO - Electrical Division',
    'light':        'TANGEDCO - Electrical Division',
    'garbage':      'GCC - Solid Waste Management Dept',
    'waste':        'GCC - Solid Waste Management Dept',
    'graffiti':     'GCC - Solid Waste Management Dept',
    'water':        'CMWSSB - Water Supply Division',
    'tap':          'CMWSSB - Water Supply Division',
    'sewage':       'CMWSSB - Sewerage Division',
    'drain':        'CMWSSB - Sewerage Division',
    'pipeline':     'CMWSSB - Water Supply Division',
}

DEPARTMENT_CONTACTS = {
    'PWD - Roads and Buildings Dept':       'pwd.chennai@tn.gov.in',
    'GCC - Parks and Horticulture Dept':    'parks.gcc@chennaicorporation.gov.in',
    'TANGEDCO - Electrical Division':       'tangedco.chennai@tn.gov.in',
    'GCC - Solid Waste Management Dept':    'swm.gcc@chennaicorporation.gov.in',
    'CMWSSB - Water Supply Division':       'water.cmwssb@tn.gov.in',
    'CMWSSB - Sewerage Division':           'sewerage.cmwssb@tn.gov.in',
}

DEPARTMENT_SLA_DAYS = {
    'PWD - Roads and Buildings Dept':       7,
    'GCC - Parks and Horticulture Dept':    5,
    'TANGEDCO - Electrical Division':       3,
    'GCC - Solid Waste Management Dept':    2,
    'CMWSSB - Water Supply Division':       4,
    'CMWSSB - Sewerage Division':           3,
}

def assign_department(issue_type):
    issue_lower = issue_type.lower()
    for keyword, department in ROUTING_TABLE.items():
        if keyword in issue_lower:
            return department
    return 'GCC - General Municipal Services'

def get_department_email(department):
    return DEPARTMENT_CONTACTS.get(department, 'civic@chennaicorporation.gov.in')

def get_sla_days(department):
    return DEPARTMENT_SLA_DAYS.get(department, 7)

def get_routing_info(issue_type):
    dept = assign_department(issue_type)
    return {
        'department':    dept,
        'contact_email': get_department_email(dept),
        'sla_days':      get_sla_days(dept)
    }