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

import requests
import json



from client import app



UPLOAD_FOLDER = 'http://0.0.0.0:5002/upload/'

app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'zip', 'tar', 'tar.gz', 'gz'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']



@app.route('/upload')
def upld():
    print("salut salut 0")
    return render_template('upload.html', uploaded=None)



@app.route('/bundle/<bundleId>/upload', methods=['POST'])
# @login_required
def upldfile(bundleId):
    if request.method == 'POST':
        print request.headers
        print len(request.data)
        header = {'content-type' : request.headers['content-type']}
        req = requests.post('http://0.0.0.0:5002/bundle/'+bundleId+'/archive', data=request.data, headers = request.headers)
        print("salut salut 1")
        return render_template('upload.html', uploaded="true")




@app.route('/uploads/<filename>')
def uploaded_file(filename):
    print("salut salut 2")
    return send_from_directory(UPLOAD_FOLDER, filename)


# def uploaded_file(filename):
#     print("salut salut 2")
#     return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/bundle', methods=['POST'])
def newMetaBundle() :
    header = {'content-type' : 'application/json'}
    req = requests.post('http://0.0.0.0:5002/bundle', data=json.dumps(request.form), headers = header)
    return req.text , req.status_code


