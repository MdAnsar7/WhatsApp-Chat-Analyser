import re
import pandas as pd


def preprocess(data):

    cnt_temp_am_pm = 0;
    for i in data:
        if i == '-':
            break
        else:
            cnt_temp_am_pm += 1

    cnt_temp_am_pm -= 3
    am_pm = data[cnt_temp_am_pm] + data[cnt_temp_am_pm + 1]

    if am_pm == 'am' or am_pm == 'pm':
        pattern = "\d{1,2}\/\d{2,4}\/\d{2,4},\s\d{1,2}:\d{1,2}\s\w{1,2}\s-\s"  # for 12 hr format
    else:
        pattern = '\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s'

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    time_format = dates[0]
    cnt = 2
    newTimeFormat = ""
    for i in time_format:
        if i == '/':
            cnt -= 1
        if i == ',':
            break;
        if cnt == 0:
            newTimeFormat += i;

    newTimeFormat = newTimeFormat[1:]



    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # convert message_date type
    if len(newTimeFormat) == 2:
        if am_pm == 'am' or am_pm == 'pm':
            df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %I:%M %p - ')
        else:
            df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %H:%M - ')
    else:
        if am_pm == 'am' or am_pm == 'pm':
            df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%Y, %I:%M %p - ')
        else:
            df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%Y, %H:%M - ')

    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split('([\w\w]+?):\s', message)
        if (entry[1:]):  # user name
            users.append(entry[0] + entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['minute'] = df['date'].dt.minute
    df['hour'] = df['date'].dt.hour
    df['month_num'] = df['date'].dt.month
    df['only_date'] = df['date'].dt.date
    df['day_name'] = df['date'].dt.day_name()

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df