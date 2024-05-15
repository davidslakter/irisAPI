import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from iris import Contact

service_account_name = 'iris-service-account-key.json'

cred = credentials.Certificate(service_account_name)
default_app = firebase_admin.initialize_app(cred)

db = firestore.client()

def addCamera(uid, camera):
    db.collection(u'users').document(uid).collection(u'cameras').add({
        'id': camera["ID"],
        'feed_link': camera["url"],
        'name': camera["name"],
        'location': camera["location"],
        'person_density': camera["person_density"]
     })


def removeCamera(uid, camera_id):
    camera_ref = db.collection(u'users').document(uid).collection(u'cameras') 
    camera_docs = camera_ref.where(u'id', u'==', camera_id).stream()

    for doc in camera_docs:
        print('deleting cam from database')
        camera_ref.document(str(doc.id)).delete()

def updateThreshold(uid, camera_id, person_density):
    camera_ref = db.collection(u'users').document(uid).collection(u'cameras') 
    camera_docs = camera_ref.where(u'id', u'==', camera_id).stream()
    
    for doc in camera_docs:
        print('updating person_density value')
        camera_ref.document(str(doc.id)).update({
            'person_density': person_density
        })

def addEvent(event, verified):
    db.collection(u'users').document(event['uid']).collection(u'abnormal_events').add({
        'Addressed': False,
        'Camera_Name': event['camera_name'],
        'Confidence': event['confidence'],
        'Is_Verfied': verified,
        'Location': event['location'],
        'Name': event['crime_name'],
        'Time_Start': event['time_started'],
        'streamURL': event['stream-url'],
        'eventURL': event['event-url']
    })

def verifyContactKey(uid, contact_id):
    contacts = db.collection(u'users').document(uid).collection(u'contacts').stream()
    
    for contact in contacts:
        if contact.get('id') == contact_id:
            return False

    return True

def getContacts(uid):
    contact_stream = db.collection(u'users').document(uid).collection(u'contacts').stream()
    contacts = []
    for contact in contact_stream:
         contacts.append(Contact.Contact(contact.to_dict()))
    return contacts

def addContact(uid, contact):
    db.collection(u'users').document(uid).collection(u'contacts').add({
            'id': contact.id,
            'contact_name': contact.contact_name,
            'contact_position': contact.contact_position,
            'email': contact.email,
            'phone': contact.phone
        })

def removeContact(uid, contact_id):
    contact_ref = db.collection(u'users').document(uid).collection(u'contacts')
    contact_docs = contact_ref.where(u'id', u'==', contact_id).stream()

    for doc in contact_docs:
        print('deleting contact from database')
        contact_ref.document(str(doc.id)).delete()

def updateContacts(iris_instance):
    uid = iris_instance.uid
    doc_ref = db.collection(u'users').document(uid)
    
    doc = doc_ref.get()
    # check if the uid exists in db
    if doc.exists:
        # update iris instance with all contacts in db
        contacts = db.collection(u'users').document(uid).collection(u'contacts').stream()
        for existing_contact in contacts:
            contact_dict = existing_contact.to_dict()
            new_contact = Contact.Contact(contact_dict)
            new_contact.id = contact_dict['id']
            iris_instance.contacts[new_contact.id] = new_contact



def isAuthenticated(uid, auth_key):
    user_doc = db.collection(u'users').document(uid).get()
    if user_doc.exists:
        user_data = user_doc.to_dict()
        return user_data['auth_key'] == auth_key
    return False
