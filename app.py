import csv
import os

from flask import Flask, jsonify, request, render_template, redirect, flash
import json

# declared an empty variable for reassignment
from pyasn1.compat.octets import null
from werkzeug.utils import secure_filename

from scoring import get_id_result

response = ''

# creating the instance of our flask application
app = Flask(__name__)
UPLOAD_FOLDER_ENROLL = 'data/wav/enroll'
UPLOAD_FOLDER_TEST = 'data/wav/test'
app.config["DEBUG"] = True
app.config['UPLOAD_FOLDER_TEST'] = UPLOAD_FOLDER_TEST
app.config['UPLOAD_FOLDER_ENROLL'] = UPLOAD_FOLDER_ENROLL
parsedPathTest = 'data/wav/test/'
parsedPathEnroll = 'data/wav/enroll/'


@app.route('/getList', methods=['GET'])
def get_list_users():
    with open('cfg/enroll_list.csv') as file:
        data = csv.reader(file, delimiter=',')
        first_line = True
        speakers = []
        for row in data:
            if not first_line:
                speakers.append(row[1])
            else:
                first_line = False
    return jsonify(speakers)


# route to entertain our post and get request from flutter app
@app.route('/identify', methods=['GET', 'POST'])
def identify_speaker():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER_TEST'], filename))
            path = parsedPathTest + filename
            name = filename.split(".", 1)[0]
            with open('cfg/test_list.csv', mode='w') as file:
                writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                # way to write to csv file
                writer.writerow(['filename', 'speaker'])
                writer.writerow([path, name])
            res = get_id_result()
            return jsonify({'PersonName': res})
    return '''
            <!doctype html>
            <title>Upload new File</title>
            <h1>Upload new File</h1>
            <form method=post enctype=multipart/form-data>
              <input type=file name=file>
              <input type=submit value=Upload>
            </form>
            '''


@app.route('/addSpeaker', methods=['GET', 'POST'])
def add_speaker():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER_ENROLL'], filename))
            path = parsedPathEnroll + filename
            with open('cfg/enroll_list.csv', 'r+', newline='') as file:
                csv_reader = csv.reader(file, delimiter=",", lineterminator='\n')
                for row in csv_reader:
                    if row == null:
                        continue
                    if request.values['person_name'] == row[1]:
                        return "User already added!!"

                csv_writer = csv.writer(file, delimiter=',')
                csv_writer.writerow([path, request.values['person_name']])
                file.close()
            return ""

    return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
          <input type=text name=person_name>
          <input type=file name=file>
          <input type=submit value=Upload>
        </form>
        '''


if __name__ == "__main__":
    app.run(debug=True)
