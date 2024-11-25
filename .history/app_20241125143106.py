from flask import Flask, request, jsonify
import requests

# Your existing code for get_definition and define_word functions...

# Import for Google Sheet interaction
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

app = Flask(__name__)


# Replace with the path to your JSON key file
CREDENTIALS_FILE = 'your_credentials.json'

def get_spreadsheet_client():
    """
    Creates and returns a Google Sheets client object.
    """
    creds = Credentials.from_service_account_file('your_credentials.json')
    service = build('sheets', 'v4', credentials=creds)
    return service.spreadsheets()

# sheet = get_spreadsheet_client().sheet1  # Assuming data goes to sheet1

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
    sheet_id = 'YOUR_SHEET_ID'
    range_name = 'Sheet1!A:A'  # Assuming the word is in the first column

    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id, range=range_name).execute()
    values = result.get('values', [])

    if word not in [row[0] for row in values]:
        try:
            sheet.values().append(
                spreadsheetId=sheet_id,
                range="Sheet1",
                valueInputOption="RAW",
                body={"values": [[word, definition]]}
            ).execute()
        except Exception as e:
            print(f"Error adding data to Google Sheet: {e}")
            return jsonify({'error': 'Error saving data'}), 500

    return jsonify({'definition': definition})

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)