
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
    app.run()

