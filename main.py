from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from flask import jsonify

import time

app = Flask(__name__)


Firestore = credentials.Certificate("FireBaseKey.json")

firebase_admin.initialize_app(Firestore)

Database = firestore.client()

tenants_ref = Database.collection('tenants')



def CreateanID():

    return f"req_{datetime.now().strftime('%Y%m%d%H%M%S')}"


# This function allows a generated ID as well as a specific date/time to be implemented onto flask web app
def SubmitMaintenance(apartment_number, area_of_problem, problem_description, photo_url):

    # This code makes the ID and specifies the Data/Time that is auto generated after making a request

    request_id = CreateanID()

    date_time = datetime.now()

    # This code displays the maintenance request of the tenant onto Firestore
    requests_ref = Database.collection('maintenance_requests')

    new_request = requests_ref.add({


        'request_id': request_id,


        'apartment_number': apartment_number,

        'area_of_problem': area_of_problem,

        'problem_description': problem_description,

        'photo_url': photo_url,

        'status': 'pending',

        'date_time': date_time
    })



# This code works with the Html so that it can work with the flask web app and display it
@app.route('/')

def index():


    return render_template('index.html')

@app.route('/submit_request', methods=['POST'])

# This function allows for the staff member to change a pending request to completed
def SubmitwithTenant():


    if request.method == 'POST':


        numberapt = request.form['apartment_number']

        Issuearea = request.form['area_of_problem']

        IssueDescription = request.form['problem_description']

        ImgLink = request.form['photo_url']


        SubmitMaintenance(numberapt, Issuearea, IssueDescription, ImgLink)

        return redirect(url_for('index'))

# This is the path that allows for a specific filer search that only staff members can perform
@app.route('/browse_requests', methods=['GET', 'POST'])

def SpecificFilter():


    if request.method == 'POST':

        numapt = request.form.get('apartment_number')

        problemdescription = request.form.get('area_of_problem')

        Beginday = request.form.get('start_date')

        EndDay = request.form.get('end_date')

        checkerstatus = request.form.get('status')

 
        saveinfo = Database.collection('maintenance_requests')

        if numapt:
            saveinfo = saveinfo.where('apartment_number', '==', numapt)

        if problemdescription:
            saveinfo = saveinfo.where('area_of_problem', '==', problemdescription)

        if Beginday:
            saveinfo = saveinfo.where('date_time', '>=', datetime.strptime(Beginday, '%Y-%m-%d'))

        if EndDay:
            saveinfo = saveinfo.where('date_time', '<=', datetime.strptime(EndDay, '%Y-%m-%d'))

        if checkerstatus:
            saveinfo = saveinfo.where('status', '==', checkerstatus)

        # Execute the query and get the results
        results = saveinfo.stream()

        return render_template('browse_requests.html', results=results)

    return render_template('browse_requests.html')

# This function allows for the staff member to change a pending request to completed
@app.route('/update_status', methods=['POST'])

def update_status():


    if request.method == 'POST':

        request_id = request.form.get('request_id')

        print(f"Request ID: {request_id}")

        status_id = request.form.get('status')

        print(f"Status: {status_id}")




        request_ref = Database.collection('maintenance_requests').document(request_id)



        document_snapshot = request_ref.get()


        if document_snapshot.exists:

            current_status = document_snapshot.get('status')

            if current_status is not None and current_status.lower() == 'pending':

                print("Updating status to 'completed'")

                request_ref.update({'status': 'completed'})

                response_message = "Status updated successfully"




                return redirect(url_for('SpecificFilter'))

            else:

                response_message = "Request is already marked as completed or status is not 'pending'"

                print(response_message)

    # Redirect to browse_requests in case of an error or no update
    return redirect(url_for('SpecificFilter'))



# This function allows to add a tenant to the collections firebase with specific paramaters as a manager
def add_tenant(tenant_id, name, phone_number, email, check_in_date, check_out_date, apartment_number):
    tenants_ref.document(tenant_id).set({

        'tenant_id': tenant_id,

        'name': name,

        'phone_number': phone_number,

        'email': email,

        'check_in_date': check_in_date,

        'check_out_date': check_out_date,

        'apartment_number': apartment_number
    })

# This function allows to move a tenant to the collections firebase with specific paramaters as a manager
def move_tenant(tenant_id, new_apartment_number):
    tenants_ref.document(tenant_id).update({'apartment_number': new_apartment_number})

# This function allows to delete a tenant to the collections firebase with specific paramaters as a manager
def delete_tenant(tenant_id):

    tenants_ref.document(tenant_id).delete()

# This is the path to add a new tenant
@app.route('/add_tenant', methods=['POST'])

def add_tenant_route():

    if request.method == 'POST':

        tenant_id = request.form['tenant_id']

        name = request.form['name']

        phone_number = request.form['phone_number']

        email = request.form['email']

        check_in_date = request.form['check_in_date']

        check_out_date = request.form['check_out_date']

        apartment_number = request.form['apartment_number']

        add_tenant(tenant_id, name, phone_number, email, check_in_date, check_out_date, apartment_number)

        return redirect(url_for('index'))

# This is the path to move a tenant to a new apartment
@app.route('/move_tenant', methods=['POST'])

def move_tenant_route():

    if request.method == 'POST':

        tenant_id = request.form['tenant_id']

        new_apartment_number = request.form['new_apartment_number']


        move_tenant(tenant_id, new_apartment_number)

        return redirect(url_for('index'))



# This is the path to delete a tenant
@app.route('/delete_tenant', methods=['POST'])

def delete_tenant_route():

    if request.method == 'POST':

        tenant_id = request.form['tenant_id']

        delete_tenant(tenant_id)

        return redirect(url_for('index'))




if __name__ == '__main__':
    app.run(debug=True)
