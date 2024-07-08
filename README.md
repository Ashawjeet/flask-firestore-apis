+http://127.0.0.1:5000/retrieve_data/organizations/ims system/data/alldata/bincards detail
http://127.0.0.1:5000/retrieve_data/organizations/ims system/data/location
http://127.0.0.1:5000/retrieve_data/organizations/ims system/data/category
http://127.0.0.1:5000/retrieve_data/Organizations/IMS System/Data/All Data/Items



from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase app with service account credentials
cred = credentials.Certificate("serviceAccount.json")
firebase_admin.initialize_app(cred)

# Create a Firestore client
db = firestore.client()

app = Flask(__name__)

# Route to write data to a collection and document
@app.route('/write_data/<collection_name>/<document_id>/', methods=['POST'])
@app.route('/write_data/<collection_name>/<document_id>/<subcollection1>/<subdocument1_id>/', methods=['POST'])
@app.route('/write_data/<collection_name>/<document_id>/<subcollection1>/<subdocument1_id>/<subcollection2>/<subdocument2_id>/', methods=['POST'])
def write_data(collection_name, document_id, subcollection1=None, subdocument1_id=None, subcollection2=None, subdocument2_id=None):
    try:
        # Get JSON data from the request
        data = request.get_json()

        # Reference to the document
        doc_ref = db.collection(collection_name).document(document_id)

        if subcollection1 and subdocument1_id:
            # Reference to the first subcollection
            subcollection1_ref = doc_ref.collection(subcollection1).document(subdocument1_id)

            if subcollection2 and subdocument2_id:
                # Reference to the second subcollection
                subcollection2_ref = subcollection1_ref.collection(subcollection2).document(subdocument2_id)

                # Attempt to set the data
                subcollection2_ref.set(data)

                return jsonify({"message": f"Data submitted successfully to {collection_name}/{document_id}/{subcollection1}/{subdocument1_id}/{subcollection2}/{subdocument2_id}"}), 200
            else:
                # Attempt to set the data to the first subcollection document
                subcollection1_ref.set(data)

                return jsonify({"message": f"Data submitted successfully to {collection_name}/{document_id}/{subcollection1}/{subdocument1_id}"}), 200
        else:
            # Attempt to set the data to the main document
            doc_ref.set(data)

            return jsonify({"message": f"Data submitted successfully to {collection_name}/{document_id}"}), 200

    except Exception as e:
        return jsonify({"error": f"Error writing data: {e}"}), 500

# Route to retrieve data from a collection/document or nested subcollections/documents
@app.route('/retrieve_data/<collection_name>/<document_id>/', methods=['GET'])
@app.route('/retrieve_data/<collection_name>/<document_id>/<subcollection1>/<subdocument1_id>/', methods=['GET'])
@app.route('/retrieve_data/<collection_name>/<document_id>/<subcollection1>/<subdocument1_id>/<subcollection2>/<subdocument2_id>/', methods=['GET'])
def retrieve_data(collection_name, document_id, subcollection1=None, subdocument1_id=None, subcollection2=None, subdocument2_id=None):
    try:
        # Reference to the document
        doc_ref = db.collection(collection_name).document(document_id)

        if subcollection1 and subdocument1_id:
            # Reference to the first subcollection
            subcollection1_ref = doc_ref.collection(subcollection1).document(subdocument1_id)

            if subcollection2 and subdocument2_id:
                # Reference to the second subcollection
                subcollection2_ref = subcollection1_ref.collection(subcollection2).document(subdocument2_id)

                # Retrieve data from Firestore
                data_from_firestore = subcollection2_ref.get().to_dict()

                if data_from_firestore:
                    return jsonify(data_from_firestore), 200
                else:
                    return jsonify({"message": "Document not found"}), 404
            else:
                # Retrieve data from the first subcollection document
                data_from_firestore = subcollection1_ref.get().to_dict()

                if data_from_firestore:
                    return jsonify(data_from_firestore), 200
                else:
                    return jsonify({"message": "Document not found"}), 404
        else:
            # Retrieve data from the main document
            data_from_firestore = doc_ref.get().to_dict()

            if data_from_firestore:
                return jsonify(data_from_firestore), 200
            else:
                return jsonify({"message": "Document not found"}), 404

    except Exception as e:
        return jsonify({"error": f"Error retrieving data: {e}"}), 500

# Route to retrieve all documents from specified subcollections
@app.route('/retrieve_data/<collection_name>/<document_id>/<subcollection1>/', methods=['GET'])
@app.route('/retrieve_data/<collection_name>/<document_id>/<subcollection1>/<subcollection2>/', methods=['GET'])
def retrieve_subcollection_data(collection_name, document_id, subcollection1, subcollection2=None):
    try:
        # Reference to the document
        doc_ref = db.collection(collection_name).document(document_id)

        if subcollection2:
            # Reference to the second subcollection
            subcollection_ref = doc_ref.collection(subcollection1).document(document_id).collection(subcollection2)
        else:
            # Reference to the first subcollection
            subcollection_ref = doc_ref.collection(subcollection1)

        # Retrieve all documents from the subcollection
        all_data = {}
        docs = subcollection_ref.stream()

        for doc in docs:
            all_data[doc.id] = doc.to_dict()

        if all_data:
            return jsonify(all_data), 200
        else:
            return jsonify({"message": "No data found in the subcollection"}), 404

    except Exception as e:
        return jsonify({"error": f"Error retrieving subcollection data: {e}"}), 500

# Route to retrieve all documents from specified subcollections in nested subcollections
@app.route('/retrieve_data/<collection_name>/<document_id>/<subcollection1>/<subdocument1_id>/<subcollection2>/', methods=['GET'])
def retrieve_nested_subcollection_data(collection_name, document_id, subcollection1, subdocument1_id, subcollection2):
    try:
        # Reference to the document
        doc_ref = db.collection(collection_name).document(document_id)

        # Reference to the first subcollection
        subcollection1_ref = doc_ref.collection(subcollection1).document(subdocument1_id)

        # Reference to the second subcollection
        subcollection2_ref = subcollection1_ref.collection(subcollection2)

        # Retrieve all documents from the nested subcollection
        all_data = {}
        docs = subcollection2_ref.stream()

        for doc in docs:
            all_data[doc.id] = doc.to_dict()

        if all_data:
            return jsonify(all_data), 200
        else:
            return jsonify({"message": "No data found in the nested subcollection"}), 404

    except Exception as e:
        return jsonify({"error": f"Error retrieving nested subcollection data: {e}"}), 500

# Route to retrieve all documents from specified subcollections in nested subcollections after subdocument1
@app.route('/retrieve_data/<collection_name>/<document_id>/<subcollection1>/<subdocument1_id>/<subcollection2>/', methods=['GET'])
def retrieve_nested_subcollection2_data(collection_name, document_id, subcollection1, subdocument1_id, subcollection2):
    try:
        # Reference to the document
        doc_ref = db.collection(collection_name).document(document_id)

        # Reference to the first subcollection
        subcollection1_ref = doc_ref.collection(subcollection1).document(subdocument1_id)

        # Reference to the second subcollection
        subcollection2_ref = subcollection1_ref.collection(subcollection2)

        # Retrieve all documents from the nested subcollection
        all_data = {}
        docs = subcollection2_ref.stream()

        for doc in docs:
            all_data[doc.id] = doc.to_dict()

        if all_data:
            return jsonify(all_data), 200
        else:
            return jsonify({"message": "No data found in the nested subcollection2"}), 404

    except Exception as e:
        return jsonify({"error": f"Error retrieving nested subcollection2 data: {e}"}), 500

# Route to retrieve all documents from specified subcollections in nested subcollections after subdocument1
@app.route('/retrieve_data/<collection_name>/<document_id>/<subcollection1>/<subdocument1_id>/<subcollection2>/<subcollection3>/', methods=['GET'])
def retrieve_nested_subcollection3_data(collection_name, document_id, subcollection1, subdocument1_id, subcollection2, subcollection3):
    try:
        # Reference to the document
        doc_ref = db.collection(collection_name).document(document_id)

        # Reference to the first subcollection
        subcollection1_ref = doc_ref.collection(subcollection1).document(subdocument1_id)

        # Reference to the second subcollection
        subcollection2_ref = subcollection1_ref.collection(subcollection2).document(subdocument1_id)

        # Reference to the third subcollection
        subcollection3_ref = subcollection2_ref.collection(subcollection3)

        # Retrieve all documents from the nested subcollection
        all_data = {}
        docs = subcollection3_ref.stream()

        for doc in docs:
            all_data[doc.id] = doc.to_dict()

        if all_data:
            return jsonify(all_data), 200
        else:
            return jsonify({"message": "No data found in the nested subcollection3"}), 404

    except Exception as e:
        return jsonify({"error": f"Error retrieving nested subcollection3 data: {e}"}), 500

# Route to retrieve documents from specified subcollections after subdocument1 in nested subcollections
@app.route('/retrieve_data/<collection_name>/<document_id>/<subcollection1>/<subdocument1_id>/<subcollection2>/<subdocument2_id>/', methods=['GET'])
def retrieve_nested_subcollection_after_subdocument1_data(collection_name, document_id, subcollection1, subdocument1_id, subcollection2, subdocument2_id):
    try:
        # Reference to the document
        doc_ref = db.collection(collection_name).document(document_id)

        # Reference to the first subcollection
        subcollection1_ref = doc_ref.collection(subcollection1).document(subdocument1_id)

        # Reference to the second subcollection
        subcollection2_ref = subcollection1_ref.collection(subcollection2).document(subdocument2_id)

        # Retrieve all documents from the nested subcollection
        all_data = {}
        docs = subcollection2_ref.stream()

        for doc in docs:
            all_data[doc.id] = doc.to_dict()

        if all_data:
            return jsonify(all_data), 200
        else:
            return jsonify({"message": "No data found in the nested subcollection after subdocument1"}), 404

    except Exception as e:
        return jsonify({"error": f"Error retrieving nested subcollection after subdocument1 data: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
 

{
  "type": "service_account",
  "project_id": "firestoredemo-a8bf0",
  "private_key_id": "4197d93581b6beece0cb493952cd89ed3abdf1eb",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCrdtc6uZNsaRQA\n/XQwQISFQ3BQrQjsanBNy2+4cSh0V1sGXXnehOfjYHdo6L0Bc8QBoDFt8k0+HM3J\n3gSupfi2+g8AJCUwgqYRhEDl33muc5cYfFTCsn3Mi4q/62u6uq0IEWgVzu+dP0d9\nbeLizK/qwPuHAyxgE/S1GqNTUc4M/0MJMM8oc+rgUvqpNPqKZ4LigWy65evGbYeS\n1fTgd+WT4nfoJfOU2OIqFZ5hcn4yEsFsKSmdwVxD3L89/Yj/yWWuRQTUo0FKpPyZ\nrwzWFYovn5xxLpfpvY1HpToKLrrYZBjqMS3zUNYLkf5RCQwE1lxgiWFPIXYchwYl\nDBX3NzA3AgMBAAECggEAI9GDG6Lpr5Nx2NUZgPzxUg9o9ol3HEAN7sppL7v/yfH3\ns2gyja/w6xhbSYCY/yUqVHac7M1ZoniM6rck/kDwqHSrTom+dRhNzcn1bq/U8QL3\nlOdgI3369pBN71KkIhFeFRnhxvCAMLan3gVnCJ7evukKgkVA718r1utWJBEqPJ98\nRwLp+mayeevFp/X93d8EJrwNHb65LWyZLxqOV8BAnTr2JrWW0Q0+A6A4unt1PVBv\n2tqm0k7DjxJbCCyX3VrKFzQihSeI9KcBxD6yBbsZ1sTIm34QXw/Hpql/SOvxjx60\n1xi7ZUc+cX3Xn9z/VQZY2qOjxYhO4aAIPWgcxvDL0QKBgQDrUGyB9RwECYBKHWAL\nwxuJjak5THGAO1YjXo8K5cTwB61CE6cKwtdRW6DIOSTPrsJFdf5BN45bmULfckSd\nY8UQJUXI3FqBWbIix7iMN76mAdbwidbZs4GqyjKgiecBn61G3rdE5gkUy7yrYToU\nEP+uqzI+oMaP1ekd5vbMm/+PMQKBgQC6iYUbsFWOqU4EobdfZ9485VtSX3huuCt0\nGqBv2YjQXWcQdOuPYUJBArJ/4qVUXm1X1r5f/XRi8U3QTZNtjOoed2gCrgUJzJRg\nDAPUcqy6bRsn0UPn48lqCnbRN3FirlExDwJNPc+qReodfaq53v6+XphqarzWcF+f\nfqwvURvr5wKBgQDpcnMDhqCRnL9qR7Q2VwylrSVaE+1yMuuk0TWFsSdsnaEUMZ0B\nfwTP0OA0YwSTCSPwdzuThcM0OlruhFVv8z/YYbHWsE0VkF+6Q3thmBgKZz7OiWDd\nv0j/n/MT81t67+eerGsS7kfKGsmFGELfD3Io3exN14DFx4iqwqzLlmO1sQKBgD5Q\nVFQEmwA2VKa9cyl+5EHJiLFCzVOHWJTHlFLpA4g/u39G364dGmnnQcPw7bP6e2J9\njUk5vRiUbZ8pWxecnFUjJG7IvUwhuGtBeEIPMN5yNkEd6iZb9NvktP59G/aQLvVJ\ng0ZUYLwL8QJ7CX5gHQ9xQE9EauLj1T3Nri18Vex/AoGAWVov9TekGeCgTUoGwzF1\nf+k5slVRdGBrDWMJiE7sP3yMYFPvHgtEcPibT2tQ1WGzMFK+3vcsk95iBb5wMBmd\npyD4+KUoOBkM3yo2yQnwIwp0vMXfZWFGGaLOIC2usTyQ0EbZTg+ee/qQr9BS9yBr\nUdWkHC2ohdwZ6ip6utmC0v4=\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-an3vd@firestoredemo-a8bf0.iam.gserviceaccount.com",
  "client_id": "115485470618498263273",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-an3vd%40firestoredemo-a8bf0.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
