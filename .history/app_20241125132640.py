from flask import Flask, request, jsonify
import requests
from oauth2client.service_account import ServiceAccountCredentials 1   # for gspread

# Your existing code for get_definition and define_word functions...

# Import for Google Sheet interaction
import gspread
from oauth2client.service_account import ServiceAccountCredentials


app = Flask(__name__)


# Replace with the path to your JSON key file
CREDENTIALS_FILE = 'your_credentials.json'

def get_spreadsheet_client():
  """
  Creates and returns a Google Sheets client object.
  """
  credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE)
  gc = gspread.authorize(credentials)
  return gc.open_by_key('YOUR_SHEET_ID')  # Replace with your sheet ID

sheet = get_spreadsheet_client().sheet1  # Assuming data goes to sheet1

def get_definition(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    headers = {'Authorization': 'Token YOUR_API_KEY'}  # Replace with your API key

    response = requests.get(url, headers=headers)
    data = response.json()

    if 'title' in data and data['title'] == 'No Definitions found for that word.':
        return None

    definition = data[0]['meanings'][0]['definitions'][0]['definition']
    return definition

@app.route('/define', methods=['GET'])
def define_word():
    word = request.args.get('word')
    if not word:
        return jsonify({'error': 'Word not provided'}), 400

    definition = get_definition(word)
    if not definition:
        return jsonify({'error': 'Word not found'}), 404

    # Check if the word already exists in the sheet
    existing_words = sheet.col_values(1)  # Assuming the word is in the first column
    if word not in existing_words:
        try:
            sheet.append_row([word, definition])
        except Exception as e:
            print(f"Error adding data to Google Sheet: {e}")
            return jsonify({'error': 'Error saving data'}), 500

    return jsonify({'definition': definition})

@app.route('/')
def hello_world():
    return 'Hello, World!'

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=YOUR_PORT)

