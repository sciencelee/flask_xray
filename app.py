
import os, sys, time
from flask import Flask, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename

#from scipy.misc import imsave, imread, imresize
#import numpy as np
import keras.models
#import re


from keras.models import load_model
import numpy as np
from keras.preprocessing import image
from werkzeug.datastructures import FileStorage




model = load_model('model/chest_xray_cnn_100_801010.h5')


UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/static/uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

app = Flask(__name__, static_url_path="/static")

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# limit upload size upto 8mb
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024


def allowed_file(filename):
    # make sure it is only an allowed extension as we defined in ALLOWED_EXTENSIONS set
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    print(os.getcwd(), flush=True)
    if request.method == 'POST':
        #print("POST", flush=True)
        if 'file' not in request.files:
            print('No file attached in request', flush=True)
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            print('No file selected', flush=True)
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # next line prevents hacking tricks with uploaded files accessing bash (The more you know***)
            filename = secure_filename(file.filename)
            print(file, flush=True)
            #myfile = FileStorage(request.stream).save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) # save copy of file!!!!
            #process_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), filename)
            # after processing, we just redirect back to the
            filepath = app.root_path + '/static/uploads/' + filename

            time.sleep(2)
            #redirect(url_for('uploaded_file', filename=filename))

            test_image = image.load_img(filepath, target_size=(150, 150))
            test_image = image.img_to_array(test_image)
            test_image = np.expand_dims(test_image, axis=0)
            result = model.predict(test_image)
            if result[0][0] >= 0.5:
                pred = 'Pneumonia'
            else:
                pred = 'Normal'

            result = "{:.2f}".format(result[0][0])

            return render_template('index.html', filename=filename, pred=pred, result=result)  # pass whatever we need to populate index

    #print(os.listdir(UPLOAD_FOLDER), flush=True) # returns list
    return render_template('index.html')  # pass whatever we need to populate index


def process_file(path, filename):
    pass
    # good time to open the file ... open(path, 'rb') or whatever
    # could make an output file to downloads and treat it as below
    # output = open(filename, 'w')
    # output_stream = open(app.config['DOWNLOAD_FOLDER'] + filename, 'wb')
    # output.write(output_stream)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)












#  THIS IS MY OLD SORT OF WORKING CODE
# import imghdr
# import os
# from flask import Flask, render_template, request, redirect, url_for, abort, send_from_directory, Request
# from werkzeug.utils import secure_filename
# from flask import Flask, render_template, request
# from werkzeug.utils import secure_filename
# import os
# import time
#
#
#
#
#
# # boilerplate stuff from https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/
#
# app = Flask(__name__)
# app.config['MAX_CONTENT_LENGTH'] = 2000 * 2000  # MIGHT NEED BIGGER XRAYS
# app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
# app.config['UPLOAD_FOLDER'] = 'static'
# #UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/uploads/'
#
#
#
#
#
# def validate_image(stream):
#     header = stream.read(512)
#     stream.seek(0)
#     format = imghdr.what(None, header)
#     if not format:
#         return None
#     return '.' + (format if format != 'jpeg' else 'jpg')
#
#
#
# @app.route('/', methods=['GET'])
# def index():
#     # if request.method == 'GET':
#     #     return (render_template('main2.html'))
#     # if request.method == 'POST':
#     #     my_file = request.files[0]
#     #     # mess with my image
#     #     #prediction = model.predict(???
#     #     return render_template('main2.html',
#     #                             original_input={'Filename': my_file}, # dict of inputs
#     #                             result='HELLO'
#     #                                  )
#
#     return render_template('main2.html')
#
#
#
#
#
# @app.route('/', methods=['POST'])
# def upload_files():
#     # OUR IMAGE IS UPLOADED VIA POST when we submit the form.
#     # The other '/' route is to process the GET (when we visit the page but do not submit data)
#     uploaded_file = request.files['file']
#
#     filename = secure_filename(uploaded_file.filename)  # do this to prevent hacking!!!
#     filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # grab the full path
#     # below is from flask website on getting images
#     if filename != '':
#         file_ext = os.path.splitext(filename)[1]
#         if file_ext not in app.config['UPLOAD_EXTENSIONS'] or \
#                 file_ext != validate_image(uploaded_file.stream):
#             abort(400)
#         uploaded_file.save(filepath)  # upload to my saved path
#
#
#     prediction = 1
#
#     # wait until the file is uploaded
#     time_to_wait = 10 # seconds
#
#     for i in range(time_to_wait * 5):
#         if os.path.isfile(filepath):
#             break
#         prediction += 1
#         time.sleep(0.2)  # 5 waits is 1s
#
#     full_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#
#     # Trying this to fix display image problems
#     # first we will send the user to the upload page
#     return redirect(url_for('uploaded_file', filename=filename))
#
#     #Results must be strings!
#     return render_template('main2.html',
#                             filename=str(filename),
#                             result=str(prediction)
#                             )
#
#
# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#     filename = img_folder + filename
#     return render_template('main2.html', filename = filename, result='Go')
#
# @app.route('/static/<filename>')
# def send_file(filename):
#     return send_from_directory(img_folder, filename)
#
# if __name__ == '__main__':
#     app.run(debug=True)
#
# #UPLOAD_FOLDER1 = os.path.join(os.environ['HOME'], 'upload')
#
# #/Users/aaronlee/PycharmProjects/heroku_chest_xray/static/2020-2021_2nd_grade_Newsletters_2.jpg
#
#
#
#
#
#
#
#
