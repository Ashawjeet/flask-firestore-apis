from flask import Flask, request, jsonify,render_template  
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
 