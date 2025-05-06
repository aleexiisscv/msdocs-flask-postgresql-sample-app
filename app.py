import os
from datetime import datetime

from flask import Flask, redirect, render_template, request, send_from_directory, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

app = Flask(__name__, static_folder='static')
csrf = CSRFProtect(app)
load_dotenv()
# Set the secret key for CSRF protection
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')  # Usa una clave secreta segura
# WEBSITE_HOSTNAME exists only in production environmentttt
if 'WEBSITE_HOSTNAME' not in os.environ:
    # local development, where we'll use environment variables
    print("Loading config.development and environment variables from .env file.")
    app.config.from_object('azureproject.development')
else:
    # production
    print("Loading config.production.")
    app.config.from_object('azureproject.production')

# Configuración
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.update(
    SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

# Initialize the database connection
db = SQLAlchemy(app)

# Enable Flask-Migrate commands "flask db init/migrate/upgrade" to work
migrate = Migrate(app, db)

# The import must be done after db initialization due to circular import issue
from models import Restaurant, Review , ImageConversionResult

@app.route('/', methods=['GET'])
def index():
    print("SOLICTANDO NUEVA INFORMACION")
    images = ImageConversionResult.query.all()
    return render_template('index.html', images=images)


@app.route('/create_image_conversion', methods=['GET'])
def create_image_conversion():
    return render_template('create_image_conversion.html')

@app.route('/add_image_conversion', methods=['POST'])
@csrf.exempt
def add_image_conversion():
    try:
        user_name = request.form['user_name']
        file_name = request.form['file_name']
        red_pixels = int(request.form['red_pixels'])
        green_pixels = int(request.form['green_pixels'])
        blue_pixels = int(request.form['blue_pixels'])

        image_conversion_result = ImageConversionResult(
            user_name=user_name,
            file_name=file_name,
            red_pixels=red_pixels,
            green_pixels=green_pixels,
            blue_pixels=blue_pixels,
            timestamp=datetime.now()
        )
        db.session.add(image_conversion_result)
        db.session.commit()

        return redirect(url_for('index'))
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

@app.route('/upload', methods=['GET', 'POST'])
@csrf.exempt
def upload_image():

    if request.method == 'POST':
        if 'image_file' not in request.files:
            return "No file part", 400
        file = request.files['image_file']

        if file.filename == '':
            return "No selected file", 400

        user_name = request.form.get('user_name')
        red_pixels = request.form.get('red_pixels')
        green_pixels = request.form.get('green_pixels')
        blue_pixels = request.form.get('blue_pixels')

        if not user_name or not red_pixels or not green_pixels or not blue_pixels:
            return "All fields are required", 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)

            image_conversion_result = ImageConversionResult(
                user_name=user_name,
                file_name=filename,
                red_pixels=int(red_pixels),
                green_pixels=int(green_pixels),
                blue_pixels=int(blue_pixels),
                timestamp=datetime.now(),
                image_path=filename
            )
            db.session.add(image_conversion_result)
            db.session.commit()

            return redirect(url_for('index'))

    return render_template('upload_image.html')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    print(f"Serving file######: {filename}")
    return send_from_directory(os.path.join(app.root_path, 'uploads'), filename)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run()
