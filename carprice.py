# Import required libraries
from flask import Flask, render_template, request 
import joblib
import datetime as dt


app = Flask(__name__)

# Load all the joblib files
regressor = joblib.load('carpricepredict.joblib')
label_coder = joblib.load('enconder_dict.joblib')
mmt = joblib.load('make_model_trim.joblib')

# Modifying mmt to include no values till no previous selection made
mmt[1]['Empty_Placeholder'] = []
mmt[2]['Empty_Placeholder'] = []

@app.route('/', methods=['GET'])
def home():
    #mmt = joblib.load('make_model_trim.joblib')
    return render_template('index.html', mmt=mmt) 

@app.route('/popularcars', methods=['GET'])
def pop_cars():
    return render_template('popularcars.html')

@app.route('/about', methods=['GET'] )
def about():
    return render_template('about.html')

@app.route('/results', methods=['POST'])
def results():
    # Get values from html form
    if request.method == "POST":
        mmts_dict = {}
        mmts_dict['make'] = request.form.get('make')
        mmts_dict['model'] = request.form.get('model')
        mmts_dict['trim'] = request.form.get('trim')
        mmts_dict['state'] = request.form.get('state')
        year = int(request.form.get('year'))
        btype = request.form.get('carbody')
        transmission = request.form.get('transmission')
        condition = request.form.get('condition')
        odometer = float(request.form.get('odometer'))

    # Empty list to contain all the values to be used for price prediction
    predictor_list = []

    # Add make, model, trim and state after transformation using label encoder
    for o in ['make', 'model', 'trim', 'state']:
        try:
            predictor_list.append(label_coder[o].transform([mmts_dict[o]])[0])
        except:
            predictor_list.append(-1)
            
    # Add Condition
    if condition == 'Excellent':
        predictor_list.append(5)
    elif condition == 'Good':
        predictor_list.append(4)
    elif condition == 'Average':
        predictor_list.append(3)
    elif condition == 'Poor':
        predictor_list.append(2)
    else:
        predictor_list.append(1)

    # Add odometer value to the list
    predictor_list.append(odometer)

    # Add information about body type
    if btype == 'CONVERTIBLE':
        predictor_list = predictor_list + [1, 0, 0, 0, 0, 0, 0]
    elif btype == 'COUPE':
        predictor_list = predictor_list + [0, 1, 0, 0, 0, 0, 0]
    elif btype == 'HATCHBACK':
        predictor_list = predictor_list + [0, 0, 1, 0, 0, 0, 0]
    elif btype == 'OTHER':
        predictor_list = predictor_list + [0, 0, 0, 1, 0, 0, 0]
    elif btype == 'SEDAN':
        predictor_list = predictor_list + [0, 0, 0, 0, 1, 0, 0]
    elif btype == 'SUV':
        predictor_list = predictor_list + [0, 0, 0, 0, 0, 1, 0]
    elif btype == 'VAN':
        predictor_list = predictor_list + [0, 0, 0, 0, 0, 0, 1]
    else:
        predictor_list = predictor_list + [0, 0, 0, 0, 0, 0, 0]
        
    # Add information about transmission
    if transmission == 'Automatic':
        predictor_list.append(0)
    else:
        predictor_list.append(1)

    # Add car age
    predictor_list.append(dt.datetime.now().year - year)

    # Make price prediction
    predict_price = regressor.predict([predictor_list])[0]

    return render_template('results.html', predict_price=int(predict_price), year=year, make=mmts_dict['make'], model=mmts_dict['model'], state=mmts_dict['state'])

if __name__ == "__main__":
    app.run(debug=True)