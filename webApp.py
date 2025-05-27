from flask import Flask, render_template, request, redirect, url_for, session, flash
import webbrowser
import os
from flask_cors import CORS
import json
import user_db

import lambdaTTS
import lambdaSpeechToScore
import lambdaGetSample

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = '*'
app.secret_key = 'your_secret_key_here'  # Set a strong secret key for session management

rootPath = ''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = user_db.authenticate_user(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('main'))
        else:
            flash('Invalid username or password', 'error')
            return render_template('auth.html', login_error='Invalid username or password')
    return render_template('auth.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    if password != confirm_password:
        return render_template('auth.html', register_error='Passwords do not match')
    success = user_db.create_user(username, email, password)
    if success:
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    else:
        return render_template('auth.html', register_error='Registration failed. Username or email may already exist.')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route(rootPath+'/')
def main():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('main.html', username=session.get('username'))


@app.route(rootPath+'/getAudioFromText', methods=['POST'])
def getAudioFromText():
    event = {'body': json.dumps(request.get_json(force=True))}
    return lambdaTTS.lambda_handler(event, [])


@app.route(rootPath+'/getSample', methods=['POST'])
def getNext():
    event = {'body':  json.dumps(request.get_json(force=True))}
    return lambdaGetSample.lambda_handler(event, [])


@app.route(rootPath+'/GetAccuracyFromRecordedAudio', methods=['POST'])
def GetAccuracyFromRecordedAudio():

    try:
        event = {'body': json.dumps(request.get_json(force=True))}
        lambda_correct_output = lambdaSpeechToScore.lambda_handler(event, [])
    except Exception as e:
        print('Error: ', str(e))
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Credentials': "true",
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': ''
        }

    return lambda_correct_output


if __name__ == "__main__":
    language = 'de'
    # print(os.system('pwd'))
    print(os.getcwd())
    webbrowser.open_new('http://127.0.0.1:3000/')
    app.run(host="0.0.0.0", port=3000)
