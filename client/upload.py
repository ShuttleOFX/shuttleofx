from flask import (
    Flask,
    abort,
    request,
    render_template,
    send_from_directory,
    redirect,
    url_for,
    jsonify
)
from werkzeug import secure_filename
import os, zipfile, tarfile

basedir = os.path.abspath(os.path.dirname(__file__))


# app = Flask(__name__)


from client import app



UPLOAD_FOLDER = 'upload/'

app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'zip', 'tar', 'tar.gz', 'gz'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']



@app.route('/upload')
def upld():
    return render_template('upload.html', uploaded=None)


# @app.route('/uploaded')
# def uplded():
#     return render_template('configureUpload.html')


@app.route('/upload', methods=['POST'])
def upldfile():
    if request.method == 'POST':

        # print basedir

        saved_files_urls = []

        for f in request.files.getlist('file[]'):
            print f
            if f and allowed_file(f.filename):

                # filename = uniqueId BD
                filename = secure_filename(f.filename)

                print filename

                updir = os.path.join(basedir, UPLOAD_FOLDER)
                f.save(os.path.join(updir, filename))
                file_size = os.path.getsize(os.path.join(updir, filename))
                saved_files_urls.append(url_for('uploaded_file', filename=filename))

                # zipf = zipfile.ZipFile(updir + filename, "r")
                # for name in zipf.namelist():
                #     print name

                extension = os.path.splitext(filename)[1]
                print extension

                if extension == ".zip":
                    with zipfile.ZipFile(updir + filename, "r") as zipf:
                        zipf.extractall(updir)
                if extension == ".gz":
                    tarf = tarfile.open(updir + filename, 'r')
                    tarf.extractall(updir)


                os.remove(os.path.join(updir, filename))

            # return saved_files_urls[0]

        return render_template('upload.html', uploaded="true")




@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)






