import tempfile
import os
from flask import Flask, request, redirect, send_file, render_template
from skimage import io
import base64
import glob
import numpy as np

app = Flask(__name__, template_folder='template')

@app.route("/")
def main():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        # check if the post request has the file part
        img_data = request.form.get('myImage').replace("data:image/png;base64,","")
        aleatorio = request.form.get('numero')
        print(aleatorio)
        aleatorio = toDirectory(aleatorio)
        with tempfile.NamedTemporaryFile(delete = False, mode = "w+b", suffix='.png', dir=str(aleatorio)) as fh:
            fh.write(base64.b64decode(img_data))
        #file = request.files['myImage']
        print("Image uploaded")
    except Exception as err:
        print("Error occurred")
        print(err)

    return redirect("/", code=302)


@app.route('/prepare', methods=['GET'])
def prepare_dataset():
    images = []
    chars = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "+", "-", "x", "/"]
    digits = []
    for char in chars:
        filelist = glob.glob('{}/*.png'.format(char))
        images_read = io.concatenate_images(io.imread_collection(filelist))
        images_read = images_read[:, :, :, 3]
        digits_read = np.array([char] * images_read.shape[0])
        images.append(images_read)
        digits.append(digits_read)
    images = np.vstack(images)
    digits = np.concatenate(digits)
    np.save('X.npy', images)
    np.save('y.npy', digits)
    return "OK!"

@app.route('/X.npy', methods=['GET'])
def download_X():
    return send_file('./X.npy')
@app.route('/y.npy', methods=['GET'])
def download_y():
    return send_file('./y.npy')

def toDirectory(value):
    match value:
        case 'x':
            return 'TIMES'
        case '/':
            return 'DIVS'
        case '+':
            return 'PLUS'
        case '-':
            return 'MINUS'
        case _:
            return value
            

if __name__ == "__main__":
    chars = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "PLUS", "MINUS", "TIMES", "DIVS"]
    for c in chars:
        if not os.path.exists(str(c)):
            os.mkdir(str(c))
    app.run()
