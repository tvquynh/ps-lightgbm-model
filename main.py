#ML
from ember.features import PEFeatureExtractor
import numpy as np
import os
import pandas as pd
import time
import lightgbm as lgb
from datetime import datetime
#Flask
from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super@1235(*)(&^%FYFFTTTƯ^&yhưtie^5654secretkey'
app.config['UPLOAD_FOLDER'] = 'static/files'

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

@app.route('/', methods=['GET',"POST"])
@app.route('/home', methods=['GET',"POST"])
def home():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data # First grab the file
        file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename))
        file.save(file_path) # Then save the file
        #-----ML
        #Create column header
        columns = []
        for i in range(0,2381):
            feature = "f" + str(i)
            columns.append(feature)
        #Load selected features
        df_features = pd.read_csv('select_features.csv')
        select_features = df_features["0"]
        #Load model
        save_model = "PS-20M_lgb_1511-features_classifier.txt"
        #save_model = "lightgbm.model"

        gbm = lgb.Booster(model_file=save_model) 
        print ("Model", save_model, "is loaded")
        extractor = PEFeatureExtractor()
        # file_path = file_path.replace("/","\\")
        data = open(file_path,"rb").read()
        features = np.array(extractor.feature_vector(data), dtype=np.float32).reshape(1,-1)
        data = pd.DataFrame(features, columns=columns)
        selected_data = data[select_features]
        preds = gbm.predict(selected_data)
        file_stats = os.stat(file_path)
        detected = " a goodware (^_^)" if preds < 0.5 else " a malware"
        result = file_path.rsplit('\\', 1)[-1] + " is " + detected + " - File size is " + str(file_stats.st_size / (1024)) + " kilobytes"
        data = []
        # #-----
        return result
    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)