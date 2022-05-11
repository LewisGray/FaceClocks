from datetime import datetime
from clockInSystem import db


class Attendee(db.Model):
    attendeeID = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(20),nullable = False)
    lastName = db.Column(db.String(20),nullable = False)
    status = db.Column(db.String(20),nullable = False,default = "Absent")
    image =  db.Column(db.String(20),nullable = False)
    isAdmin =  db.Column(db.Boolean,nullable = False)
    isSuper =  db.Column(db.Boolean,nullable = False, default = False)
    clocks = db.relationship('Register',backref='attendeeLookup', lazy = True)

    def __repr__(self):
        return f"Attendee('{self.firstName}','{self.lastName}')"

class Register(db.Model):
    clockID = db.Column(db.Integer, primary_key=True)
    attendeeID = db.Column(db.Integer,db.ForeignKey('attendee.attendeeID'), nullable = True)
    date = db.Column(db.String(20),nullable = False)
    time = db.Column(db.String(20),nullable = False)
    action = db.Column(db.String(20),nullable = False)

class Cases(db.Model):
    caseID = db.Column(db.Integer, primary_key=True)
    image =  db.Column(db.String(20),nullable = False)
    date = db.Column(db.String(20),nullable = False)
    time = db.Column(db.String(20),nullable = False)
    action = db.Column(db.String(20),nullable = False)