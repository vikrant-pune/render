from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

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

    return jsonify({'definition': definition})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=YOUR_PORT)

