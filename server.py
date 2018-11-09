from flask import Flask, jsonify, request, Response, session, render_template, redirect, url_for, make_response
from flask_cors import CORS
import os
import time
import base64
from pymongo import MongoClient
from cryptography.fernet import Fernet
import datetime
import random
import collections
import pickle

key = b'5HFFdBeSChtl1oWaEWwDhTi5Cr7s4LohO5W2zIngmHU='
cipher_suite = Fernet(key)


app = Flask(__name__)
app.secret_key = os.urandom(24) # for session
# app.config["REDIS_URL"] = "redis://localhost"
# app.register_blueprint(sse, url_prefix='/stream')
CORS(app)

client = MongoClient('localhost', 27017)
db = client['hms']

# specializations = ["heart specialist", "neurosurgean", "general physician"]

def getAllSpecializations():

	query = {"flag": 1}
	specialities = []
	#db = client['rough']
	collection = db["users"]

	docs = collection.find(query, {"specialization": 1})

	for doc in docs:
		if(doc["specialization"] in specialities):
			pass
		else:
			specialities.append(doc["specialization"])
	
	return specialities

	
def get_free_icu_or_ward_number(what):

	query = {"_id": what}
	collection = db["hospital_details"]

	doc = collection.find_one(query)

	print("doc: ", doc)

	availability = doc["availability"]

	number = ""

	for i in range(len(availability)):
		if(int(availability[i]) == 1):
			availability[i] = 0
			number += str(i + 1)
			break
	
	if(number):
		collection.update_one(
			{"_id": what}, 
			{"$set": {'availability': availability}}, 
			upsert=False)

	return number	
	
def gimme_a_nurse():

	query = {"flag": 5}
	collection = db["users"]
	docs = collection.find(query)

	nurse = []

	for doc in docs:
		nurse.append(doc)
	
	nurse.sort(key = lambda x: len(x["incharge_patients"]))

	now = datetime.datetime.now()
	time = now.time()

	i = 0
	while i < len(nurse):
		start = datetime.datetime.strptime(nurse[i]["check_in_time"], "%H:%M").time()
		end = datetime.datetime.strptime(nurse[i]["check_out_time"], "%H:%M").time()
		if(start <= time < end):
			break
		i += 1
	
	selected_nurse = nurse[i]
	print("selected_nurse:", selected_nurse)
	
	return selected_nurse["_id"]

def gimme_a_doctor(specialization):

	query = {"flag": 1, "specialization": specialization}
	collection = db["users"]
	now = datetime.datetime.now()
	now =  now.strftime("%m/%d/%Y %H:%M")
	date = now.split(" ")[0]
	time = now.split(" ")[1]
	time2 = datetime.datetime.strptime(time, "%H:%M").time()

	docs = collection.find(query, {"_id": 1, "name": 1, "check_in_time": 1, "check_out_time": 1, "avg_time_per_patient": 1, "specialization": 1, "appointments": 1, })
	
	doctors = []
	for doc in docs:
		start = datetime.datetime.strptime(doc["check_in_time"], "%H:%M").time()
		end = datetime.datetime.strptime(doc["check_out_time"], "%H:%M").time() 
		if(start <= time2 < end):
			doctors.append(doc)
	
	random_doctor = False
	print("doctors: ", doctors)
	for doctor in doctors:
		try:
			appointments_today = doctor["appointments"][date]
			if appointments_today:
				for time in appointments_today:
					start = time
					hrs = int(start.split(":")[0])
					mins = int(start.split(":")[1])
					mins += int(doctor["avg_time_per_patient"])
					if(mins >= 60):
						hrs += 1
						mins = mins % 60
					end = str(hrs) + ":" + str(mins)
					start = datetime.datetime.strptime(start, "%H:%M").time()
					end = datetime.datetime.strptime(end, "%H:%M").time()
					if(start <= time2 < end):
						break
				else:
					selected_doctor = doctor
					break
			else:
				selected_doctor = doctor
				break
		except:
			print("No appointments on this day")
			print(date)
			selected_doctor = doctor
			break
	else:
		print("No doctor is free hence selecting a random doctor")
		selected_doctor = doctors[random.randint(0, len(doctors) - 1)]
		random_doctor = True
	
	print("selected_doctor: ", selected_doctor)

	return selected_doctor["_id"]

def sorted_appointments_name(_id):

	collection = db["users"]
	doc = collection.find_one({"_id": _id})
	date = datetime.datetime.now().date().strftime("%m/%d/%Y")
	try:
		appointments = collections.OrderedDict(sorted(doc["appointments"][date].items()))
		return appointments, doc["name"]
	except:
		return {}, doc["name"]
def save_pickle(filename, obj):
	with open(filename + '.pickle', 'wb') as handle:
		pickle.dump(obj, handle, protocol=pickle.HIGHEST_PROTOCOL)

def get_pickle(filename):
	with open(filename + ".pickle", 'rb') as handle:
		obj = pickle.load(handle)
	return obj


@app.route('/')
def homepage():

	return render_template("index.html")

@app.route('/about')
def about():

	return render_template("about_page.html")

@app.route('/register', methods = ["GET", "POST"])
def register():
	
	if request.method == "GET":
		return render_template("register.html")
	
	else:
		#print("here")
		
		doc = {
				"_id" 				: request.form["username"],
				"flag" 				: 2,
				"firstname" 		: request.form["firstname"],
				"lastname"			: request.form["lastname"],
				"password" 			: cipher_suite.encrypt(request.form["password"].encode()),
				"dob"				: request.form["dob"],
				"gender" 			: request.form["gender"],
				"phone_number" 		: request.form["contact_no"],
				"email_id" 			: request.form["email"],
				"image"				: request.form["image"],
				"notify"			: False, 
				"appointments"		: {}
			  }
		
		collection = db['users']
		collection.insert_one(doc)
		
		# return "Registered successfully"
		resp = make_response(render_template(str(2) + "_home.html", name = doc['firstname'] + " " + doc['lastname'], appointments=doc["appointments"], image = doc['image']))
		resp.set_cookie("id", doc['_id'])
				
		return resp
		
@app.route('/check_user_name_exists', methods = ["GET"])
def check_user_name_exists():

	username = request.args['username']

	# query the database to check if the username exists
	# 	if exists:
	# 		send yes
	# 	else:
	#		send no

	collection = db['users']
	if collection.find_one({'_id': username }):
		return "username exists!!!"

	return ""

@app.route('/login', methods = ["GET", "POST"])
def login():
	
	if request.method == "GET":
		return render_template("login_page.html")

	else:
		username = request.form['username']
		password = request.form['password']

		collection = db['users']

		docs = collection.find_one({ '_id': username })

		if docs:
			print(docs['password'])
			if cipher_suite.decrypt(docs['password']).decode() == password:
				
				# html pages:
				# 	1_home.html => doctor
				# 	2_home.html => patient
				# 	3_home.html => admin
				# 	4_home.html => emergency

				if(int(docs["flag"]) == 3):
					resp = make_response(render_template(str(int(docs['flag'])) + "_home.html"))
					print(resp)
					resp.set_cookie("id", docs['_id'])	
				else:
					if(int(docs["flag"]) == 1):
						appointments, name = sorted_appointments_name(docs["_id"])
						resp = make_response(render_template(str(int(docs['flag'])) + "_home.html", name=name, appointments=appointments, date=datetime.datetime.now().date().strftime("%d-%m-%Y"), inpatients = docs["inpatients"]))
						resp.set_cookie("id", docs['_id'])
						new_appointments = get_pickle("new_appointments")
						new_appointments[docs["_id"]] = []
						save_pickle("new_appointments", new_appointments)
						logged_in = get_pickle("logged_in")
						logged_in[docs["_id"]] = True
						save_pickle("logged_in", logged_in)
						print("logged in: ", logged_in)
					elif(int(docs["flag"]) == 2):
						# appointments = sorted_appointments_name(docs["_id"])
						resp = make_response(render_template(str(int(docs['flag'])) + "_home.html", name=docs["firstname"] + " " + docs["lastname"], appointments=docs["appointments"], image=docs["image"]))
						resp.set_cookie("id", docs['_id'])
					else:
						specialities = getAllSpecializations()
						#return render_template("4_home.html", specialities=specialities)
						resp = make_response(render_template(str(int(docs['flag'])) + "_home.html", specialities=specialities, success=False))
						resp.set_cookie("id", docs['_id'])
				return resp

				# return "Render page : " + str(int(docs['flag'])) + "_home.html"

			else:
				return render_template("login_page.html", error_message = "Invalid password")	
		
		else:
			return render_template("login_page.html", error_message = "Invalid username")


@app.route('/logout', methods = ["GET"])
def logout():

	_id = request.cookies.get("id")
	collection = db["users"]
	doc = collection.find_one({"_id": _id}, {"flag": 1})
	if(int(doc["flag"]) == 1):
		logged_in = get_pickle("logged_in")
		logged_in[doc["_id"]] = True
		save_pickle("logged_in", logged_in)	
		print("logged in: ", logged_in)
	resp = redirect(url_for("homepage"))
	resp.set_cookie("id", "")
				
	return resp

@app.route('/search', methods = ["GET", "POST"])
def search():
	
	if request.method == "GET":
		return render_template("search.html")
	
	else:
		specialities = getAllSpecializations()
		doctor_name = request.form['doctor_name']

		if(doctor_name in specialities):
			query = {
					  'flag': 1,
					  'specialization': doctor_name
					}	
		else:
			# print("here")
			query = { 
					  'flag': 1,  
					  'name': doctor_name 
					}

		# db = client['rough']
		collection = db['users']
		
		doc = collection.find(query, { '_id': 0, 'password': 0, 'flag': 0, 'avg_time_per_patient': 0 })
		#doc = collection.find(query)
		
		l = []

		for i in doc:
			l.append(i)
		# if(doc):
		# 	doc['error_message'] = ""

		# else:
		# 	doc['error_message'] = "Error!! Requested Doctor details not found!"
		print(l)
		return jsonify(l)

@app.route("/doctor_name_suggestions", methods = ["GET"])
def doctor_name_suggestions():

	prefix = request.args['name']
	suggestions = []

	# db = client['rough']
	collection = db['users']

	docs = collection.find({ 'flag': 1 }) 

	specializations = getAllSpecializations()

	for doc in docs:
		if doc['name'].lower().startswith(prefix.lower()):
			suggestions.append(doc['name'])

	for i in specializations:
		if i.lower().startswith(prefix.lower()):
			suggestions.append(i)

	print(suggestions)

	return jsonify(suggestions)

@app.route("/doctors_speciality_suggestions", methods = ["GET"])
def doctors_speciality_suggestions():

	speciality = request.args['speciality']
	print(speciality)
	#db = client['rough']
	collection = db['users']
	
	doctor_list = []
	query = {'flag': 1, 'specialization': speciality}

	docs = collection.find(query, {"_id": 1, 'name': 1})

	for doc in docs:
		doctor_list.append(doc)

	print(doctor_list)
	return jsonify(doctor_list)

@app.route('/date_time_suggestions', methods = ["GET"])
def date_time_suggestions():

	date = request.args['date']
	doctor_id = request.args['doctor_id']
	specialization = request.args['speciality']

	#db = client['rough']
	collection = db['users']

	time_list = []

	query = {"_id": doctor_id}
	
	doc = collection.find_one(query, {"check_in_time": 1, "check_out_time": 1, "avg_time_per_patient": 1, "appointments": 1})

	avg_time_per_patient = int(doc["avg_time_per_patient"])

	print(doc['appointments'])
	try:
		appointments_date = doc['appointments'][date]
	except:
		appointments_date = []
	
	# appointments_date: dictionary
	# 	key : time
	# 	value : patient_id
	
	start_hours = int(doc["check_in_time"].split(":")[0])
	start_mins = int(doc["check_in_time"].split(":")[1])

	end_hours = int(doc["check_out_time"].split(":")[0])
	end_mins = int(doc["check_out_time"].split(":")[1])

	if(end_mins == 0):
		end_mins = 60
	print(start_hours)
	print(start_mins)

	print(end_hours)
	print(end_mins)

	print(avg_time_per_patient)

	print(appointments_date)
	
	while((start_hours < end_hours) or (not((start_hours == end_hours) and (start_mins <= end_mins)))):
		appointment_time = str(start_hours) + ":" + str(start_mins)
		print(appointment_time)
		if(start_mins == 0):
			appointment_time += '0'
		if(appointment_time in appointments_date):
			pass
		else:
			time_list.append(appointment_time)

		start_mins += avg_time_per_patient

		if(start_mins >= 60):
			start_hours += 1
			start_mins = start_mins % 60
	
	return jsonify(time_list)

@app.route("/book_appointment", methods = ["GET", "POST"])
def book_appointment():
	
	if request.method == "GET":
		specialities = getAllSpecializations()

		return render_template("book_appointment.html", specialities = specialities)

	else:

		doctor_id = request.form['doctor_id']
		patient_id = request.cookies.get("id")
		specialization = request.form['specialization']
		date = request.form['date']
		time = request.form['time']
		details = request.form['details']

		# print(doctor_id)
		# print(specialization)
		# print(date)
		# print(time)
		# print(details)
		# print(patient_id)

		# save these details into the db for doctor and for patient also
		collection = db['users']

		# update doctors data
		doctor_doc = collection.find_one({"_id": doctor_id, "flag": 1})
		patient_doc = collection.find_one({"_id": patient_id})

		appointments = doctor_doc['appointments']
		# print("doctor")
		# print(appointments)

		try:
			appointments[date][time] = { "patient_id": patient_id, "patient_name": patient_doc["firstname"] + " " + patient_doc["lastname"], "details": details }
		except:
			appointments[date] = { time: { "patient_id": patient_id, "patient_name": patient_doc["firstname"] + " " + patient_doc["lastname"], "details": details } }

		# print(appointments)
		

		collection.update_one( {"_id": doctor_id}, {"$set": {'appointments': appointments}}, upsert=False )
		
		# if the appointment is of today and the doctor has already logged in then add that appointment to new_appointments so that it can update with the view asynchronously
		today = datetime.datetime.now().date().strftime("%m/%d/%Y")
		if(today == date):
			logged_in = get_pickle("logged_in")
			print(logged_in)
			if(logged_in[doctor_id]):
				new_appointments = get_pickle("new_appointments")
				new_appointments[doctor_id].append({ time: { "patient_id": patient_id, "patient_name": patient_doc["firstname"] + " " + patient_doc["lastname"], "details": details } })
				print("new_appointments: ", new_appointments)
				save_pickle("new_appointments", new_appointments)
			save_pickle("logged_in", logged_in)
		# update patients data

		appointments = patient_doc["appointments"]

		# print("patient")
		# print(appointments)

		try:
			appointments[date][time] = { "doctor_id": doctor_id, "doctor_name": doctor_doc["name"], "details": details }
		except:
			appointments[date] = { time: { "doctor_id": doctor_id, "doctor_name": doctor_doc["name"], "details": details } }
		
		# print(appointments)

		collection.update_one(
			{"_id": patient_id}, 
			{"$set": {'appointments': appointments}}, 
			upsert=False)

		return render_template("2_home.html", name = patient_doc["firstname"] + " " + patient_doc["lastname"], appointments = appointments, image = patient_doc["image"] )
 
@app.route("/add_doctor", methods = ["GET", "POST"])
def add_doctor():

	if request.method == "GET":
		return redirect(url_for("homepage"))

	else:
		name = request.form['name']
		username = request.form['username']
		password = cipher_suite.encrypt(request.form["password"].encode())
		email = request.form['email']
		dob = request.form['dob']
		phone_number = request.form['phone']
		check_in_time = request.form['check_in_time']
		check_out_time = request.form['check_out_time']
		avg_time_per_patient = request.form['avg_time_per_patient']
		qualification = request.form['qualification']
		specialization = request.form['specialization']
		achievements = request.form['achievements']
		experience = request.form['experience']
		about = request.form['about']
		flag = 1

		collection = db["users"]

		toInsert = {
			"_id": username,
			"flag": flag, 
			"name": name,
			"password": password,
			"email": email,
			"phone": phone_number,
			"dob": dob,
			"check_in_time": check_in_time,
			"check_out_time": check_out_time,
			"avg_time_per_patient": avg_time_per_patient,
			"qualification": qualification,
			"specialization": specialization,
			"achievements": achievements,
			"experience": experience,
			"about": about,
			"appointments": {},
			"inpatients": [], 
			"nurses": []
		}

		collection.insert_one(toInsert)
		
		return render_template("3_home.html")

@app.route("/add_nurse", methods = ["GET", "POST"])
def add_nurse():

	if request.method == "GET":
		return redirect(url_for("homepage"))

	else:
		name = request.form['name']
		username = request.form['username']	
		email = request.form['email']
		phone_number = request.form['phone']
		check_in_time = request.form['check_in_time']
		check_out_time = request.form['check_out_time']
		qualification = request.form['qualification']
		experience = request.form['experience']
		about = request.form['about']
		flag = 5
		

		collection = db["users"]

		toInsert = {
			"_id": username,
			"flag": flag, 
			"name": name,
			"email": email,
			"phone": phone_number,
			"check_in_time": check_in_time,
			"check_out_time": check_out_time,
			"qualification": qualification,
			"experience": experience,
			"about": about,
			"incharge_patients": {} # key => patient # value => doctor_id/emergency_dept_id
		}

		collection.insert_one(toInsert)
		
		return render_template("3_home.html")

@app.route("/add_emergency_department", methods = ["GET", "POST"])
def add_emergency_department():

	if request.method == "GET":
		return redirect(url_for("homepage"))

	else:
		username = request.form['username']	
		password = cipher_suite.encrypt(request.form["password"].encode())
		flag = 4
		

		collection = db["users"]

		toInsert = {
			"_id": username,
			"flag": flag, 
			"password": password
		}

		collection.insert_one(toInsert)
		
		return render_template("3_home.html")

@app.route("/ward_info", methods = ["GET", "POST"])
def ward_info():

	if request.method == "GET":
		return redirect(url_for("homepage"))

	else:
		num_wards = request.form['wards']	

		collection = db["hospital_details"]

		wards = [1] * int(num_wards) 

		toInsert = {
			"_id": "wards",
			"availability": wards
		}

		collection.insert_one(toInsert)
		
		return render_template("3_home.html")

@app.route("/icu_info", methods = ["GET", "POST"])
def icu_info():

	if request.method == "GET":
		return redirect(url_for("homepage"))

	else:
		num_icu = request.form['icu']	

		collection = db["hospital_details"]

		icu = [1] * int(num_icu)

		toInsert = {
			"_id": "icu",
			"availability": icu
		}

		collection.insert_one(toInsert)
		
		return render_template("3_home.html")

@app.route("/provide_feedback", methods = ["GET", "POST"])
def provide_feedback():

	if request.method == "GET":
		speciality = getAllSpecializations()
		return render_template("feedback.html", specialities = speciality)
	else:
		now = datetime.datetime.now()
		now =  now.strftime("%d-%m-%Y %H:%M")
		date = now.split(" ")[0]
		time = now.split(" ")[1]

		
		doctor_id = request.form["doctor"]
		specialization = request.form["specialization"]
		feedback = request.form["feedback"]
		patient_id = request.cookies.get("id")

		collection = db["users"]
		doc = collection.find_one({"_id": doctor_id})

		doctor_name = doc['name']

		collection = db["feedback"]

		# print(date)
		# print(time)
		# print(patient_id)
		# print(doctor_id)
		# print(doctor_name)
		# print(specialization)
		# print(feedback)

		toInsert = {
			"patient_id": patient_id, 
			"doctor_id": doctor_id,
			"doctor_name": doctor_name,
			"date": date,
			"time": time,
			"specialization": specialization,
			"feedback": feedback
		}
		
		collection.insert_one(toInsert)

		speciality = getAllSpecializations()
		return render_template("feedback.html", specialities = speciality)
	
@app.route("/cancel_appointment")
def cancel_appointment():

	collection = db["users"]
	doc = collection.find_one({"_id": request.cookies.get("id")}, {"appointments": 1})

	return render_template("cancel_appointment.html", appointments = doc["appointments"])

@app.route("/update_appointment", methods = ["GET"])
def update_appointment():
	
	doctor_id = request.args["doctor_id"]
	doctor_id = doctor_id[1: len(doctor_id) - 1]
	patient_id = request.cookies.get("id")
	date = request.args["date"]
	time = request.args["time"]

	#print(doctor_id, "***", sep = "")

	print(patient_id)
	print(date)
	print(time)

	collection = db["users"]

	doctor_doc = collection.find_one({"_id": doctor_id, "flag": 1})
	patient_doc = collection.find_one({"_id": patient_id})

	appointments = doctor_doc['appointments']

	del appointments[date][time]
	print(appointments)

	collection.update_one( {"_id": doctor_id}, {"$set": {'appointments': appointments}}, upsert=False )

	appointments = patient_doc['appointments']

	del appointments[date][time]
	print(appointments)
	collection.update_one(
			{"_id": patient_id}, 
			{"$set": {'appointments': appointments}}, 
			upsert=False)	

	return "done"

@app.route("/home")
def home():
	username = request.cookies.get("id")
	if(username):
		collection = db["users"]
		doc = collection.find_one({"_id": username}, {"password": 0})
		flag = int(doc["flag"])
		if(flag == 1):
			appointments, name = sorted_appointments_name(doc["_id"])
			new_appointments = get_pickle("new_appointments")
			new_appointments[doc["_id"]] = []
			save_pickle("new_appointments", new_appointments)
			return render_template("1_home.html", name = name, appointments = appointments, date=datetime.datetime.now().date().strftime("%d-%m-%Y"), inpatients = doc["inpatients"])
		elif(flag == 2):
			return render_template("2_home.html", name = doc["firstname"] + " " + doc["lastname"], image = doc["image"], appointments = doc["appointments"])
		elif(flag == 4):
			specialities = getAllSpecializations()
			return render_template("4_home.html", specialities=specialities, success=False)
		else:
			return render_template(str(flag) + "_home.html")
	else:
		return render_template("404.html")

@app.route("/all_feedbacks", methods=["GET"])
def all_feedbacks():
	feedbacks = []
	collection = db["feedback"]
	docs = collection.find({})
	for doc in docs:
		feedbacks.append(doc)
	return render_template("all_feedbacks.html", feedbacks = feedbacks)


@app.route("/gimme_a_ward_number", methods = ["GET"]) 
def gimme_a_ward_number():

	_id = request.cookies.get("id")
	if _id == "":
		return render_template("404.html")
	else:
		collection = db["users"]
		doc = collection.find_one({"_id": _id}, {"flag": 1})
		if int(doc["flag"]) != 4:
			return render_template("404.html")
		else:
			ward_num = get_free_icu_or_ward_number("wards")
			if(ward_num):
				return "ward-" + ward_num
			return ward_num

@app.route("/gimme_a_icu_number", methods = ["GET"]) 
def gimme_a_icu_number():

	_id = request.cookies.get("id")
	if _id == "":
		return render_template("404.html")
	else:
		collection = db["users"]
		doc = collection.find_one({"_id": _id}, {"flag": 1})
		if int(doc["flag"]) != 4:
			return render_template("404.html")
		else:
			icu_num = get_free_icu_or_ward_number("icu")
			if(icu_num):
				return "icu-" + icu_num
			return icu_num

@app.route("/assign_nurse", methods = ["GET"])
def assign_nurse():

	_id = request.cookies.get("id")
	if _id == "":
		return render_template("404.html")
	else:
		collection = db["users"]
		doc = collection.find_one({"_id": _id}, {"flag": 1})
		if int(doc["flag"]) != 4:
			return render_template("404.html")
		else:
			nurse_id = gimme_a_nurse()

			return nurse_id

@app.route("/assign_doctor", methods = ["GET"])
def assign_doctor():

	_id = request.cookies.get("id")
	if _id == "":
		return render_template("404.html")
	else:
		collection = db["users"]
		doc = collection.find_one({"_id": _id}, {"flag": 1})
		if int(doc["flag"]) != 4:
			return render_template("404.html")
		else:
			specialization = request.args["specialization"]

			doctor_id = gimme_a_doctor(specialization)

			return doctor_id

@app.route("/add_emergency", methods = ["POST"])
def add_emergency():

	_id = request.cookies.get("id")
	if _id == "":
		return render_template("404.html")
	else:
		collection = db["users"]
		doc = collection.find_one({"_id": _id}, {"flag": 1})
		if int(doc["flag"]) != 4:
			return render_template("404.html")
		else:
			firstname = request.form["firstname"]
			lastname = request.form["lastname"]
			age = request.form["age"]
			gender = request.form["gender"]
			icu_ward = request.form["icu_ward"]
			ward_number = request.form["ward_number"]
			icu_number = request.form["icu_number"]
			nurse_needed = request.form["nurse_needed"]
			nurse_id = request.form["nurse_id"]
			specialization = request.form["specialization"]
			doctor_id = request.form["doctor_id"]
			message = request.form["message"]
			
			now = datetime.datetime.now()

			patient_id = "emergency-" + now.strftime("%m/%d/%Y-%H:%M")


			# print(firstname)
			# print(lastname)
			# print(age)
			# print(gender)
			# print(icu_ward)
			# print(ward_number)
			# print(icu_number)
			# print(nurse_needed)
			# print(nurse_id)
			# print(specialization)
			# print(doctor_id)
			# print(message)

			# make an entry in nurse's data
			
			collection = db["users"]
			doc = collection.find_one({"_id": nurse_id, "flag": 5})
			incharge_patients = doc["incharge_patients"]
			incharge_patients[patient_id] = doctor_id

			collection.update_one(
				{"_id": nurse_id}, 
				{"$set": {'incharge_patients': incharge_patients}}, 
				upsert=False
			)

			# block that slot in doctor's appointments

			doc = collection.find_one({"_id": doctor_id, "flag": 1})

			appointments = doc["appointments"]

			try:
				appointments_today = appointments[now.date().strftime("%m/%d/%Y")]
			except:
				# no appointments today
				appointments_today = {  }

			start_hours = int(doc["check_in_time"].split(":")[0])
			start_mins = int(doc["check_in_time"].split(":")[1])

			end_hours = int(doc["check_out_time"].split(":")[0])
			end_mins = int(doc["check_out_time"].split(":")[1])

			if(end_mins == 0):
				end_mins = 60

			avg_time_per_patient = int(doc["avg_time_per_patient"])	
			busy = False
			while((start_hours < end_hours) or (not((start_hours == end_hours) and (start_mins <= end_mins)))):
				start = str(start_hours) + ":" + str(start_mins)
				print(start)
				if(start_mins == 0):
					start += '0'
				
				# hrs = int(start.split(":")[0])
				# mins = int(start.split(":")[1])
				# mins += avg_time_per_patient
				# if(mins >= 60):
				# 	hrs += 1
				# 	mins = mins % 60
				# end = str(hrs) + ":" + str(mins)	

				# appointment_time = datetime.datetime.strptime(appointment_time, "%H:%M").time()

				if(datetime.datetime.strptime(start, "%H:%M").time() < now.time()):
					pass
				else:
					if start in appointments_today:
						# doctor is busy in that timeslot
						busy = True
						break
					else:
						appointments_today[start] = { "patient_id": patient_id, "patient_name": firstname + " " + lastname, "details": message }
						break

				start_mins += avg_time_per_patient

				if(start_mins >= 60):
					start_hours += 1
					start_mins = start_mins % 60

			if(busy):
				# send sms to delayed patients
				print("Doctor has an ongoing appointment now")
				pass
			else:
				appointments[now.date().strftime("%m/%d/%Y")] = appointments_today
				collection.update_one(
					{"_id": doctor_id}, 
					{"$set": {'appointments': appointments}}, 
					upsert=False
				)	

			# update emergency details

			to_insert = {
				"_id": patient_id,
				"firstname": firstname,
				"lastname": lastname,
				"age": age,
				"gender": gender,
				"ward_number": ward_number,
				"icu_number": icu_number,
				"nurse_id": nurse_id,
				"doctor_id": doctor_id,
				"specialization": specialization,
				"message": message,
				"discharged": False
			}

			collection = db["emergency"]
			collection.insert_one(to_insert)

			specialities = getAllSpecializations()
			return render_template("4_home.html", specialities=specialities, success = True)

@app.route('/update_appointments')
def update_appointments():
	
	doctor_id = request.cookies.get("id")
	while(True):
		try:
			new_appointments = get_pickle("new_appointments")
			if(new_appointments[doctor_id]):
				print("****************************************************")
				ret = new_appointments[doctor_id]
				print(ret)
				print("****************************************************")
				new_appointments[doctor_id] = []
				save_pickle("new_appointments", new_appointments)
				return jsonify(ret)
		except:
			continue

@app.route("/doctor_patient", methods = ["GET", "POST"])
def doctor_patient():
	_id = request.cookies.get("id")
	if _id == "":
		return render_template("404.html")
	else:
		collection = db["users"]
		doc = collection.find_one({"_id": _id})
		if int(doc["flag"]) != 1:
			return render_template("404.html")
		else:
			if request.method == "GET":
				time = request.args["time"]
				patient_id = request.args["patient_id"]
				patient_name = request.args["patient_name"]
				details = request.args["details"]
				doctor_name = doc["name"]
				return render_template("doctor-patient.html", doctor_name = doctor_name, time = time, patient_id = patient_id, patient_name = patient_name, details = details)
			else:
				time = request.form["time"]
				patient_id = request.form["patient_id"]
				comment = request.form["comment"]
				submit_type = request.form["submit_type"]
				date = datetime.datetime.now().date().strftime("%m/%d/%Y")
				insert_doc = {
					"patient_id": patient_id,
					"doctor_id": _id,
					"date": date,
					"time": time,
					"comments": comment
				}
				collection = db["consultation_history"]
				collection.insert_one(insert_doc)

				# remove that appointment from doctor's appointment list

				collection = db["users"]
				doc = collection.find_one({"_id": _id, "flag": 1})
				appointments = doc["appointments"]
				del appointments[date][time]
				collection.update_one(
					{"_id": _id}, 
					{"$set": {'appointments': appointments}}, 
					upsert=False
				)

				if(submit_type == "done"):
					return redirect(url_for('home'))
				else:
					# patient is admitted

					# get a free ward 
					ward_num = get_free_icu_or_ward_number("wards")
					if(ward_num):
						ward_num = "ward-" + ward_num
					
					if(ward_num == ""):
						print("no wards empty")
						return render_template("admit_status.html", status = "Oops! No wards free at the moment", ward_num = "", nurse_name = "", doctor_name = doc["name"])

					# get a nurse
					nurse_id = gimme_a_nurse()

					patient_doc = db["users"].find_one({"_id": patient_id, "flag": 2}, {"firstname": 1, "lastname": 1})
					nurse_doc = db["users"].find_one({"_id": nurse_id, "flag": 5})
					
					# update that doctors record in DB
					new_inpatient = {
						"patient_id": patient_id,
						"patient_name": patient_doc["firstname"] + " " + patient_doc["lastname"], 
						"ward_number": ward_num,
						"nurse_id": nurse_id,
						"nurse_name": nurse_doc["name"],
						"date": date,
						"time": time 
					}

					inpatients = doc["inpatients"]
					inpatients.append(new_inpatient)
					db["users"].update_one(
						{"_id": _id}, 
						{"$set": {'inpatients': inpatients}}, 
						upsert=False
					)

					# update the nurse's record in DB
					incharge_patients = nurse_doc["incharge_patients"]
					incharge_patients[_id] = patient_id
					db["users"].update_one(
						{"_id": _id}, 
						{"$set": {'incharge_patients': incharge_patients}}, 
						upsert=False
					)

					return render_template("admit_status.html", status = "Success", patient_name = patient_doc["firstname"] + " " + patient_doc["lastname"], ward_num = ward_num, nurse_name = nurse_doc["name"], doctor_name = doc["name"])

@app.route("/test")
def test():
	# _id = request.cookies.get("id")
	# appointments, name = sorted_appointments_name(_id)
	# return render_template("1_home.html", name = name, appointments=appointments)

	return render_template("admit_status.html", status = "Oops", ward_num = "ward-1", nurse_name = "Anne Marie", doctor_name = "Dr. Peter")

if __name__ == '__main__':
	logged_in = {}
	with open('logged_in.pickle', 'wb') as handle:
		pickle.dump(logged_in, handle, protocol=pickle.HIGHEST_PROTOCOL)
	
	new_appointments = {}
	with open('new_appointments.pickle', 'wb') as handle:
		pickle.dump(new_appointments, handle, protocol=pickle.HIGHEST_PROTOCOL)

	app.run(host="0.0.0.0", port = 5001, debug = True, threaded = True)