from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
import csv
from sklearn import datasets, linear_model
import warnings
import pandas as pd
import numpy as np
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from matplotlib import pyplot as plt
import pmdarima as pm
from PIL import Image, ImageDraw, ImageFont
warnings.filterwarnings("ignore")

SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
    dataset = pd.read_csv("Graph/newData1.csv")
    X = dataset.iloc[1:, 1].values
    y = dataset.iloc[1:, 2].values
    X1 = dataset['1.Time']
    X2 = dataset['2.Signal Value']
    Xf = np.array(list(zip(X1, X2)))
    yf = dataset['5.Health Status']
    X_train, X_test, y_train, y_test = train_test_split(Xf, yf, test_size=0.30)
    current_status = dataset.iloc[-1]["5.Health Status"]
    current_value = dataset.iloc[-1]["2.Signal Value"]
    current_time = dataset.iloc[-1]["1.Time"]
    current_date = dataset.iloc[-1]["6.Date"]
    data = pd.date_range(current_date, periods=50, freq='D')
    predicted_date = data[-1]
    print(predicted_date)
    pred_time = current_time + 50
    new_time = [[pred_time]]

    df = pd.read_csv('Graph/newData1.csv', usecols=['2.Signal Value'], header=0)

    model = pm.auto_arima(df.values, start_p=1, start_q=1,
                          test='adf',  # use adftest to find optimal 'd'
                          max_p=3, max_q=3,  # maximum p and q
                          m=1,  # frequency of series
                          d=None,  # let model determine 'd'
                          seasonal=False,  # No Seasonality
                          start_P=0,
                          D=0,
                          trace=True,
                          error_action='ignore',
                          suppress_warnings=True,
                          stepwise=True)
    # Forecast
    n_periods = 50
    fc = None
    confint = None
    index_of_fc = None
    fc_series = None
    lower_series = None
    upper_series = None
    fc, confint = model.predict(n_periods=n_periods, return_conf_int=True)
    index_of_fc = np.arange(len(df.values), len(df.values) + n_periods)

    # make series for plotting purpose
    fc_series = pd.Series(fc, index=index_of_fc)
    last_element = fc_series[-1:]
    print(last_element)
    pred_value = last_element[pred_time]
    lower_series = pd.Series(confint[:, 0], index=index_of_fc)
    upper_series = pd.Series(confint[:, 1], index=index_of_fc)

    # Plot
    plt.plot(df.values)
    plt.plot(fc_series, color='darkgreen')
    plt.fill_between(lower_series.index,lower_series,upper_series,color='k', alpha=.15)
    plt.title("Final Forecast")
    plt.savefig('Graph/graph2.png')
    #plt.show()

    predict_val = [[pred_time, pred_value]]

    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    predicted = model.predict(predict_val)
    y_pred = model.predict(X_test)
    print('Health Status : ', predicted)
    print('accuracy random forest: ', accuracy_score(y_test, y_pred))

    image = Image.open('background.png')
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('Roboto-Black.ttf', size=15)
    message = str(predicted_date)
    color = 'rgb(0, 0, 0)'  # black color
    draw.text((10, 10), 'Prediction Date : ', fill=color, font=font)
    draw.text((130, 10), message, fill=color, font=font)
    draw.text((10, 40), 'Prediction Value : ', fill=color, font=font)
    pred_value = last_element[pred_time].astype(str)
    draw.text((130, 40), pred_value, fill=color, font=font)
    message = predicted[0]
    draw.text((10, 70), 'Machine Status : ', fill=color, font=font)
    draw.text((130, 70), message, fill=color, font=font)

    image.save('prognosis2.png')

    image = Image.open('background.png')
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('Roboto-Black.ttf', size=15)
    current_time = current_date
    current_value = current_value.astype(str)
    color = 'rgb(0, 0, 0)'  # black color
    draw.text((10, 10), 'Current Date : ', fill=color, font=font)
    draw.text((130, 10), current_time, fill=color, font=font)
    draw.text((10, 40), 'Current Value : ', fill=color, font=font)
    draw.text((130, 40), current_value, fill=color, font=font)
    message = predicted[0]
    draw.text((10, 70), 'Machine Status : ', fill=color, font=font)
    draw.text((130, 70), current_status, fill=color, font=font)

    image.save('diagnosis2.png')

    data = [pred_time, pred_value, predicted[0]]
    with open('Graph/predicted.csv', 'a') as csvFile:
        writer = csv.writer(csvFile, delimiter=',')
        writer.writerow(data)

    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials_backup.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    #parameter1
    #1BCVoi2yXL_seuaDBumEUpIw1vpc5yJGj
    #1MMNdZNchkmDYBy3fpWpRP_wOxfil3y_p
    #10IKDxJYrGvF2DX90Tbze_HQ_0tjh9z1f
    #parameter2
    #File ID: 1Hd1tTVsJj0jo8hUMfwlMTHb0GHVGGEXt
    #File ID: 1iOpHrN2kdLSpdN1Xds4r8QHgEkwM2iqc
    #File ID: 1dLBqrB1gwGlvE_KbUvvfMYS3sf_KRvBQ

    file_id = '1Hd1tTVsJj0jo8hUMfwlMTHb0GHVGGEXt'
    file_metadata = {'name':'graph2.png'}
    media = MediaFileUpload('Graph/graph2.png',
                            mimetype='image/jpeg')
    file = service.files().update(fileId=file_id,body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
    print('File ID: %s' % file.get('id'))

    file_id = '1iOpHrN2kdLSpdN1Xds4r8QHgEkwM2iqc'
    file_metadata = {'name':'prognosis2.png'}
    media = MediaFileUpload('prognosis2.png',
                            mimetype='image/jpeg')
    file = service.files().update(fileId=file_id,body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
    print('File ID: %s' % file.get('id'))

    file_id = '1dLBqrB1gwGlvE_KbUvvfMYS3sf_KRvBQ'
    file_metadata = {'name':'diagnosis2.png'}
    media = MediaFileUpload('diagnosis2.png',
                            mimetype='image/jpeg')
    file = service.files().update(fileId=file_id,body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
    print('File ID: %s' % file.get('id'))


if __name__ == '__main__':
    while True:
            main()
