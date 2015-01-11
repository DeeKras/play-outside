from models import SchoolData
from config import db


def find_all_schools():
    schools = db.session.query(SchoolData).all()
    for school in schools:
        print school.last_name, school.CECE_code, school.school_name, school.latitude, school.longitude

find_all_schools()       