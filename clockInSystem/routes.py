from time import time
from clockInSystem.models import Attendee,Register,Cases
from clockInSystem.forms import RegistrationForm,AttendeeForm,InfoForm
from flask import render_template, request, url_for,Response, flash, redirect,session
from clockInSystem import app, db
import cv2
import face_recognition
import numpy as np
import secrets
import os
import datetime


def gen_frames(camera,known_face_names,known_face_encodings):
        # Initialize some variables
        loops = 0
        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True
        while True:
            success, frame = camera.read()  # read the camera frame
            if not success:
                break
            else:
                # Resize frame of video to 1/4 size for faster face recognition processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
                rgb_small_frame = small_frame[:, :, ::-1]

                # Only process every other frame of video to save time
                if process_this_frame:
                    # Find all the faces and face encodings in the current frame of video
                    face_locations = face_recognition.face_locations(rgb_small_frame)
                    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                    face_names = []
                    for face_encoding in face_encodings:
                        # See if the face is a match for the known face(s)
                        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                        name = "Unknown"
                        # Or instead, use the known face with the smallest distance to the new face
                        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            name = known_face_names[best_match_index]
                        print(name)
                        print("^")
                        f = open("myfile.txt", "w")
                        f.write(name)
                        if name == "Unknown":
                            random_hex = secrets.token_hex(8)
                            picture_fn = random_hex + ".jpg"
                            picture_path = os.path.join(app.root_path, 'static/cases', picture_fn)
                            f.write("\n" + picture_fn)
                            cv2.imwrite(picture_path,frame)
                        face_names.append(name)
                        f.close
                        
                
                
    #################################################################################################################
                
                        # Display the results
                    for (top, right, bottom, left), name in zip(face_locations, face_names):
                        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                        top *= 4
                        right *= 4
                        bottom *= 4
                        left *= 4

                        # Draw a box around the face
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                        # Draw a label with a name below the face
                        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                        font = cv2.FONT_HERSHEY_DUPLEX
                        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
                        camera.release()
            process_this_frame = not process_this_frame
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
####################################################################################################################
@app.route('/video_feed')
def video_feed():
    camera = cv2.VideoCapture(0,cv2.CAP_DSHOW)
    known_face_encodings = []
    known_face_names = []
    profiles = Attendee.query.all()
    for eachAtendee in profiles:
        picture_path = os.path.join(app.root_path, 'static/face_images', eachAtendee.image)
        _image = face_recognition.load_image_file(picture_path)
        face_encoding = face_recognition.face_encodings(_image)[0]
        face_name = eachAtendee.firstName +" "+ eachAtendee.lastName
        known_face_encodings.append(face_encoding)
        known_face_names.append(face_name)
    display =gen_frames(camera,known_face_names,known_face_encodings)
    
    return Response(display, mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__=='__main__':
    app.run(debug=True)

@app.route('/about')
def about():
    return render_template("about.html")
 
@app.route("/startScreen")
@app.route('/')
def startScreen():
    session.pop("clockAction",None)
    session.pop("super",None)
    session.pop("fileName",None)
    return render_template("startScreen.html")

@app.route('/mainMenu',methods=['GET','POST']) 
def mainMenu():
    f = open("myfile.txt", "w")
    f.close()
    if request.method == 'POST':
        if "Sign In" in request.form:
            session["clockAction"] = "Sign In"
        elif "Sign Out" in request.form:
            session["clockAction"] = "Sign Out"
        elif "Start Break" in request.form:
            session["clockAction"] = "Start Break"
        elif "End Break" in request.form:
            session["clockAction"] = "End Break"
        elif "Admin Tools" in request.form:
            session["clockAction"] = "Admin Tools"
          
    else:
        return render_template("mainMenu.html"), {"Refresh": "60; url=startScreen"}
    
    return redirect(url_for('cameraScreen'))
    #

@app.route('/cameraScreen', methods=['GET','POST'])
def cameraScreen():
    if request.method == 'POST':
        size = os.path.getsize('myfile.txt')
        if size <= 0:
            flash(f'Wait for recognition before continuing','warning')
            return redirect(url_for('mainMenu'))
        else:
            return redirect(url_for('success'))
    else:
        return render_template('cameraScreen.html'), {"Refresh": "60; url=startScreen"}

@app.route('/adminTools',methods=['GET','POST']) 
def adminTools():
    if request.method == 'POST':
        if "Manage Attendees" in request.form:
            return redirect(url_for('attendeeManagement'))
            
        elif "View Reports" in request.form:
            return redirect(url_for('viewReports'))
            
        elif "Review Pictures" in request.form:
            return redirect(url_for('reviewPictures'))
    
    return render_template("adminTools.html"), {"Refresh": "60; url=startScreen"}

@app.route('/editAttendee/<int:attendeeID>',methods=['GET','POST'])
def editAttendee(attendeeID):
    if session["super"] == "True":
        super = "True"
    else:
        super = "False"
    form = RegistrationForm()
    attendeeToEdit = Attendee.query.filter_by(attendeeID=attendeeID).all()[0]
    if form.validate_on_submit():
        attendeeToEdit.firstName = form.firstName.data
        attendeeToEdit.lastName = form.lastName.data
        attendeeToEdit.isAdmin = form.isAdmin.data
        if form.image.data is None:
            pass
        else:
            picture_file = save_picture(form.image.data)
            attendeeToEdit.image = picture_file
        db.session.commit()
        flash(f'Account Updated for {form.firstName.data}!','success')
        return redirect(url_for('attendeeManagement'))
    else:
        form.firstName.data = attendeeToEdit.firstName
        form.lastName.data = attendeeToEdit.lastName
        form.isAdmin.data = attendeeToEdit.isAdmin
        if form.image.data is None:
            pass
        else:
            form.image.data = attendeeToEdit.image
        return render_template('register.html', title='Update',form=form,attendee = attendeeToEdit,legend = "Manage an Attendee",submitButton = "Update Attendee",edit = "True",supers = super), {"Refresh": "60; url=startScreen"}

@app.route('/deleteAttendee/<int:attendeeID>',methods=['GET','POST'])
def deleteAttendee(attendeeID):
    attendeeToDelete = Attendee.query.filter_by(attendeeID=attendeeID).all()[0]
    db.session.delete(attendeeToDelete)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('attendeeManagement'))
    

@app.route('/attendeeManagement')
def attendeeManagement():
    attendeeList = Attendee.query.all()
    return render_template("management.html",attendeeList = attendeeList), {"Refresh": "60; url=startScreen"}


@app.route('/success')
def success():
    f = open("myfile.txt", "r")
    name = f.readline()
    nameArray = name.split()
    if nameArray[0] == "Unknown":
        fileName = f.readline()
        session["fileName"] = fileName
        f.close()
        return redirect(url_for('failure'))
    f.close()
    attendeeID = Attendee.query.filter_by(firstName=nameArray[0],lastName = nameArray[1]).all()    
    if attendeeID[0].isSuper == True:
        session["super"] = "True"
    else:
        session["super"] = "False"
    if session["clockAction"] == "Admin Tools":
        if attendeeID[0].isAdmin == True or attendeeID[0].isSuper == True:
            return redirect(url_for('adminTools'))
        else:
            return redirect(url_for('mainMenu'))
    else:
        
        x = datetime.datetime.now() 
        date= x.strftime("%x")
        time= x.strftime("%X")
        action= session["clockAction"]
        if action != "Sign Out":
            attendeeID[0].status = "Present"
        else:
            attendeeID[0].status = "Absent"
        newClock =  Register(attendeeID=attendeeID[0].attendeeID,date= date, time = time, action = action)
        db.session.add(newClock)
        db.session.commit()
        return render_template("success.html",name = name,action =action), {"Refresh": "60; url=startScreen"}






@app.route('/failure') 
def failure():
    x = datetime.datetime.now() 
    date= x.strftime("%x")
    time= x.strftime("%X")
    action= session["clockAction"]
    image_file = url_for('static', filename='cases/' + session["fileName"])
    newCase = Cases(image=image_file,date=date,time=time,action=action)
    db.session.add(newCase)
    db.session.commit()

    return render_template("failure.html",caseID = newCase.caseID,action = action), {"Refresh": "60; url=startScreen"}

@app.route('/reviewPictures', methods=['GET','POST'])
def reviewPictures():
    caseList = Cases.query.all()
    return render_template("reviewCases.html",caseList = caseList), {"Refresh": "60; url=startScreen"}


@app.route('/resolveCase/<int:caseID>',methods=['GET','POST'])
def resolveCase(caseID):
    case = Cases.query.filter_by(caseID = caseID).all()
    form = AttendeeForm()
    form.attendee.choices = [(g.attendeeID, g.firstName +" "+ g.lastName) for g in Attendee.query.order_by('attendeeID')]
    form.attendee.choices.append(("Imposter","Imposter"))
    if form.validate_on_submit():
        if form.attendee.data != "Imposter":
            attendee = Attendee.query.filter_by(attendeeID = form.attendee.data).all()
            if case[0].action != "Sign Out":
                attendee[0].status = "Present"
            else:
                attendee[0].status = "Absent"
            resolvedCase =  Register(attendeeID=attendee[0].attendeeID,date= case[0].date, time = case[0].time, action = case[0].action)
        else:
            resolvedCase =  Register(date= case[0].date, time = case[0].time, action = case[0].action)
        db.session.add(resolvedCase)
        db.session.delete(case[0])
        db.session.commit()
        flash(f'Case Resolved!','success')
        return redirect(url_for('reviewPictures'))
    return render_template("resolveCase.html",case = case[0],form = form), {"Refresh": "60; url=startScreen"}



def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/face_images', picture_fn)
    form_picture.save(picture_path)
    return picture_fn


@app.route('/registerAttendee', methods=['GET','POST']) 
def registerAttendee():
    if session["super"] == "True":
        super = "True"
    else:
        super = "False"
    form = RegistrationForm()
    if form.validate_on_submit():  
        newAttendee = Attendee(firstName=form.firstName.data,lastName=form.lastName.data,isAdmin = form.isAdmin.data,image=save_picture(form.image.data) )
        db.session.add(newAttendee)
        db.session.commit()
        flash(f'Account Created for {form.firstName.data}!','success')
        return redirect(url_for('attendeeManagement'))
    return render_template('register.html', title='Register',form=form,legend = "Register an Attendee",submitButton = "Register Attendee",edit = "False",supers = super ), {"Refresh": "60; url=startScreen"}



@app.route('/viewReports',methods=['GET','POST'])
def viewReports():
    attendeeList = Attendee.query.all()
    form = InfoForm()
    if form.validate_on_submit():
        date = str(form.date.data)
        return redirect(url_for('viewDate', date = date))
    return render_template("viewReports.html",attendeeList = attendeeList,form=form), {"Refresh": "60; url=startScreen"}


@app.route('/viewAttendee/<int:attendeeID>',methods=['GET','POST'])
def viewAttendee(attendeeID):
    employeeClocks = Register.query.filter_by(attendeeID=attendeeID).all()
    if bool(employeeClocks):
        display = "Clocks"
    else:
        display = "None"
    return render_template("reports.html",clocks = employeeClocks, display =display), {"Refresh": "60; url=startScreen"}

@app.route('/viewDate/<string:date>',methods=['GET','POST'])
def viewDate(date):
    dateArray = date.split("-")
    year = list(dateArray[0])
    searchDate = str(dateArray[1]+"/"+dateArray[2]+"/"+year[2]+year[3])
    employeeClocks = Register.query.filter_by(attendeeID=1).all()
    print(employeeClocks[0].date)
    print(searchDate)
    dateClocks = Register.query.filter_by(date=searchDate).all()
    if bool(dateClocks):
        display = "Clocks"
    else:
        display = "None"
    return render_template("reports.html",clocks = dateClocks,display =display), {"Refresh": "60; url=startScreen"}

@app.route('/viewPresent',methods=['GET','POST'])
def viewPresent():
    presentAttendees = Attendee.query.filter_by(status = "Present").all()
    if bool(presentAttendees):
        display = "Attendees"
    else:
        display = "None"
    return render_template("reports.html",presentAttendees = presentAttendees,display = display), {"Refresh": "60; url=startScreen"}