import os
import urllib.request
from flask.helpers import send_file
from app import app
from flask import render_template, flash, redirect, url_for, send_from_directory, current_app
from flask_login import current_user, login_user
from app.models import Album, User, Photo
from flask_login import logout_user
from flask_login import login_required
from flask import Response,request
from werkzeug.urls import url_parse
from app import db
from app.main import bp
from app.main.forms import CreateAlbumForm, RegistrationForm, EditAlbumForm
from app.main.forms import LoginForm
from datetime import datetime
from werkzeug.utils import secure_filename
from google.cloud import storage
from urllib.parse import urlparse

from flask_wtf import form

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)    

@bp.route('/logout')
def logout():
    logout_user()
    return render_template('home.html')


@bp.route('/')
def home():
    return render_template('home.html')

@bp.route('/index')
@login_required
def index(): 
    # user = {'username': 'Priya'}
    album ={'username':User.username}
    
    return render_template("index.html", title='Home', album=album) 

@bp.route('/albumvalues', methods = ['GET', 'POST'])
@bp.route('/album', methods = ['GET', 'POST'])
@login_required
def album(): 
    albumvalues = Album.query.filter_by(user_id=current_user.id).all()
    if albumvalues==True:
        return redirect(url_for('main.browse'))
    return render_template("album.html", title='ALBUM',albumvalues=albumvalues)  

@bp.route('/editAlbum/<id>' , methods = ['GET', 'POST'])
@login_required
def editAlbum(id):
    albumForm = Album.query.filter_by(id=id).first()
    form = EditAlbumForm()
    album = Album.query.get(id)
    album.name=form.name.data
    album.description=form.description.data
    album.category=form.category.data
    album.is_favourite=form.is_favourite.data
    db.session.add(album)
    db.session.commit()
    if form.is_submitted():
        flash('Album details updated sucessfully!')
        next_page = url_for('main.album')
        return redirect(next_page) 
    # id = Album.id
    return render_template("editAlbum.html", title='EDIT ALBUMS', album=album, form=form)
    
@bp.route('/deleteAlbum/<id>' , methods = ['GET', 'POST'])
@login_required
def deleteAlbum(id):
    album=Album.query.filter_by(id=id).first()
    db.session.delete(album)
    db.session.commit()
    flash('Album deleted sucessfully!')
    albumvalues = Album.query.filter_by(user_id=current_user.id).all()

    return render_template("album.html", title='Album', albumvalues=albumvalues)

@bp.route('/createAlbum', methods=['GET', 'POST'])
@login_required
def createAlbum(): 
    form = CreateAlbumForm()
    createalbum = Album(name=form.name.data, description=form.description.data, category=form.category.data, is_favourite=form.is_favourite.data, user_id=current_user.id)
    next_page = request.args.get('next')
    if form.validate_on_submit():
        db.session.add(createalbum)
        db.session.commit()
        flash('Congratulations, you created an album!')
        next_page = url_for('main.album')
        return redirect(next_page)
    # return redirect(url_for('main.login'))
    return render_template("createAlbum.html", title='CREATE ALBUM', form=form)

@bp.route('/SignUp', methods=['GET', 'POST'])
def SignUp():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.login'))
    return render_template('Sign Up.html', title='Sign Up', form=form)

ALLOWED_EXTENSIONS =(['jpg'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/browse')	
@bp.route('/browse/<id>')
def browse(id):
    albumvalues = Album.query.filter_by(user_id=current_user.id).all()
    return render_template('browse.html', id=id, albumvalues=albumvalues)

@bp.route('/upload/<albumId>', methods=['GET','POST'])
@login_required
def upload(albumId):
    album = Album.query.filter_by(user_id=current_user.id).all()
    user = User.query.filter_by(id=current_user.id).all()
    gbucket_url='http://storage.googleapis.com/photos--bucket/'
    # credential_path = r"C:\Users\Manju\Downloads\flask-photo-album-a04256f4cc69.json"
    # os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('main.index'))
    file = request.files['file']
    gcs = storage.Client()
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(url_for('main.index'))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file = request.files['file']
        bucket_name='photos--bucket'
        # destination_blob_name=filename
        storage_client = storage.Client()
        bucket = storage_client.bucket(r'photos--bucket/user_username/album_id')
        blob = bucket.blob(filename)
        # blob.upload_from_filename(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        blob.upload_from_file(file)
        photo= Photo(photo_url=(gbucket_url+filename) , album_id=albumId)
        db.session.add(photo)
        db.session.commit()
        flash('Image successfully uploaded and displayed below')
        # return blob.public_url
        return redirect(url_for('main.viewalbum', albumId=albumId))
        # return render_template('browse.html', filename=filename)
    else:
        flash('Only .jpg images are allowed')
    return render_template('browse.html')
       
@bp.route('/display/<filename>')
@login_required
def display_image(filename):
	# print('display 
    # filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

@bp.route('/viewalbum/<albumId>')
def viewalbum(albumId):
    photos = Photo.query.filter_by(album_id=albumId).all()
    album = Album.query.filter_by(id=albumId).first()
    return render_template('viewalbum.html', photos=photos, album=album)

@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    photos = [
        {'author': user, 'photo_url': 'No image'}]
    return render_template('user.html', user=user, photos=photos)