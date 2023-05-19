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
app.config['SECRET_KEY'] = 'Nthjhbcn159753'  # Собственный секретный ключ
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

    # Разделение изображения на четыре части
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

    # Созранение графика
    plot_path = 'static/color_distribution.png'
    plt.savefig(plot_path)
    plt.close()

    return plot_path


@app.route('/', methods=['GET', 'POST'])
def index():
    form = UploadForm()

    if form.validate_on_submit():
        # проверка на существованеи файла в запросе POST
        if 'file' not in request.files:
            return render_template('index.html', error='No file selected')

        file = form.file.data

        # Проверка если файл пустой
        if file.filename == '':
            return render_template('index.html', error='No file selected')

        # Проверка, является ли файл допустимым изображением
        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            return render_template('index.html', error='Invalid file format')

        # Сохранение выгруженного файла
        image_path = os.path.join('static', file.filename)
        file.save(image_path)

        # открытие изображения
        image = Image.open(image_path)

        # разбиение изображения на 4 части
        top_left, top_right, bottom_left, bottom_right = split_image(image)

        # сохранение новых изображений
        top_left.save('static/top_left.png')
        top_right.save('static/top_right.png')
        bottom_left.save('static/bottom_left.png')
        bottom_right.save('static/bottom_right.png')

        # Генерируется график распределения цветов для исходного изображения
        original_plot_path = plot_color_distribution(image)

        # Генерируется график распределения цветов для новых изображений
        top_left_plot_path = plot_color_distribution(top_left)
        top_right_plot_path = plot_color_distribution(top_right)
        bottom_left_plot_path = plot_color_distribution(bottom_left)
        bottom_right_plot_path = plot_color_distribution(bottom_right)

        return render_template('index.html', form=form, image_path=image_path, original_plot_path=original_plot_path,
                               top_left_path='static/top_left.png', top_right_path='static/top_right.png',
                               bottom_left_path='static/bottom_left.png', bottom_right_path='static/bottom_right.png',
                               top_left_plot_path=top_left_plot_path, top_right_plot_path=top_right_plot_path,
                               bottom_left_plot_path=bottom_left_plot_path,
                               bottom_right_plot_path=bottom_right_plot_path)

    return render_template('index.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
