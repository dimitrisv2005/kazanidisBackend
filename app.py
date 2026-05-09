from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
import base64
import io
from PIL import Image

app = Flask(__name__)
CORS(app) # Επιτρέπει τις κλήσεις από το κινητό

# Χρησιμοποίησε το API Key σου
client = genai.Client()

@app.route('/scan', methods=['POST'])
def scan_object():
    try:
        data = request.json
        image_base64 = data.get('image')
        target_lang = data.get('target_lang')

        if not image_base64:
            return jsonify({"error": "No image provided"}), 400

        # Προετοιμασία της εικόνας για το Gemini
        # Το νέο SDK δέχεται απευθείας το base64 string αν το δομήσουμε σωστά
        prompt = (f"Αναγνώρισε το αντικείμενο στη φωτογραφία. "
                  f"Επίστρεψε ΑΠΟΚΛΕΙΣΤΙΚΑ ένα JSON με τα εξής πεδία: "
                  f"'objectGr': το όνομα στα ελληνικά, "
                  f"'objectTr': το όνομα στα {target_lang}. "
                  f"Μην γράψεις τίποτα άλλο εκτός από το JSON.")

        response = client.models.generate_content(
            model="gemini-flash-latest",
            config={"response_mime_type": "application/json"},
            contents=[
                prompt,
                {"inline_data": {"data": image_base64, "mime_type": "image/png"}}
            ]
        )

        # Επιστροφή της απάντησης στο κινητό
        return response.text, 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # ΠΡΟΣΟΧΗ: Το host='0.0.0.0' είναι απαραίτητο για να είναι ορατός ο server στο δίκτυο
    app.run(host='0.0.0.0', port=5000, debug=True)