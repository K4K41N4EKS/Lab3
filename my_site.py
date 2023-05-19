import os
from flask import Flask, render_template, request
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import InputRequired
from flask_wtf.recaptcha import RecaptchaField

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Nthjhbcn159753'  # Custom secret key
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LeqXx0mAAAAAFCegI4khFxIxOzwY1c82Bfjc2Bj'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LeqXx0mAAAAAGmwN6Rpb0kEkpYrjDwbGFqyqQfl'


class UploadForm(FlaskForm):
    file = FileField('Image File', validators=[InputRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField('Upload')


def split_image(image):
    width, height = image.size
    new_width = width // 2
    new_height = height // 2

    # Split the image into four parts
    top_left = image.crop((0, 0, new_width, new_height))
    top_right = image.crop((new_width, 0, width, new_height))
    bottom_left = image.crop((0, new_height, new_width, height))
    bottom_right = image.crop((new_width, new_height, width, height))

    return top_left, top_right, bottom_left, bottom_right


def plot_color_distribution(image):
    pixels = np.array(image)
    red = pixels[:, :, 0].ravel()
    green = pixels[:, :, 1].ravel()
    blue = pixels[:, :, 2].ravel()

    plt.hist(red, bins=256, color='red', alpha=0.5)
    plt.hist(green, bins=256, color='green', alpha=0.5)
    plt.hist(blue, bins=256, color='blue', alpha=0.5)
    plt.xlabel('Intensity')
    plt.ylabel('Frequency')
    plt.legend(['Red', 'Green', 'Blue'])
    plt.title('Color Distribution')
    plt.grid(True)

    # Save the plot
    plot_path = 'static/color_distribution.png'
    plt.savefig(plot_path)
    plt.close()

    return plot_path


def get_image_size(image):
    width, height = image.size
    return f'{width}x{height}'


@app.route('/', methods=['GET', 'POST'])
def index():
    form = UploadForm()

    if form.validate_on_submit():
        # Check if a file exists in the POST request
        if 'file' not in request.files:
            return render_template('index.html', error='No file selected')

        file = form.file.data

        # Check if the file is empty
        if file.filename == '':
            return render_template('index.html', error='No file selected')

        # Check if the file is a valid image
        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            return render_template('index.html', error='Invalid file format')

        # Save the uploaded file
        image_path = os.path.join('static', file.filename)
        file.save(image_path)

        # Open the image
        image = Image.open(image_path)

        # Split the image into four parts
        top_left, top_right, bottom_left, bottom_right = split_image(image)

        # Save the new images
        top_left.save('static/top_left.png')
        top_right.save('static/top_right.png')
        bottom_left.save('static/bottom_left.png')
        bottom_right.save('static/bottom_right.png')

        # Generate color distribution plot for the original image
        original_plot_path = plot_color_distribution(image)

        # Generate color distribution plots for the new images
        top_left_plot_path = plot_color_distribution(top_left)
        top_right_plot_path = plot_color_distribution(top_right)
        bottom_left_plot_path = plot_color_distribution(bottom_left)
        bottom_right_plot_path = plot_color_distribution(bottom_right)

        # Get the size of the original image
        original_size = get_image_size(image)

        # Get the sizes of the new images
        top_left_size = get_image_size(top_left)
        top_right_size = get_image_size(top_right)
        bottom_left_size = get_image_size(bottom_left)
        bottom_right_size = get_image_size(bottom_right)

        return render_template('index.html', form=form, image_path=image_path, original_plot_path=original_plot_path,
                               top_left_path='static/top_left.png', top_right_path='static/top_right.png',
                               bottom_left_path='static/bottom_left.png', bottom_right_path='static/bottom_right.png',
                               top_left_plot_path=top_left_plot_path, top_right_plot_path=top_right_plot_path,
                               bottom_left_plot_path=bottom_left_plot_path,
                               bottom_right_plot_path=bottom_right_plot_path,
                               original_size=original_size,
                               top_left_size=top_left_size,
                               top_right_size=top_right_size,
                               bottom_left_size=bottom_left_size,
                               bottom_right_size=bottom_right_size)

    return render_template('index.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
