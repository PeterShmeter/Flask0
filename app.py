from flask import Flask, render_template, request, send_file, send_from_directory, redirect, url_for, session
from markupsafe import Markup
from sql_storage import chat_storage
from tprint import *
from io import BytesIO
from flask_socketio import SocketIO, join_room, leave_room, send

sessions = []
DB_FILE_NAME = 'chat.db'
ds = chat_storage(DB_FILE_NAME)
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # подствавьте свой секретный ключ
socketio = SocketIO(app)

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'name' not in session.keys():
        if request.method == 'POST':
            print('New session:', request.form['name'])
            session['name'] = request.form['name']
        else:
            print('New session:')
            return render_template('author.html')
    if request.method == 'POST':
        if 'message_id' in request.form.keys():
            attachment = ds.get_message_attachment(request.form['message_id'])
            return send_file(BytesIO(attachment['attachment']), download_name=attachment['attachment_name'],
                             as_attachment=True
                             )
            # return send_from_directory(directory='C:\\Users\\Customer\\Desktop\\', path='Eng_vid.txt', as_attachment=True)
        if 'form-name' in request.form.keys() and request.form['form-name'] == 'main':
            if request.form['message'] != '':
                message = {
                    'message': request.form['message'],
                    'dt_message': now(),
                    'username': session['name'],
                }
                file = request.files['attachment']
                if file is not None and file.filename != '':
                    message['attachment_name'] = file.filename
                    message['attachment'] = file.read()
                ds.insert('messages', message)
                ds.commit()
                for sess in sessions:
                    print(sess.keys())
                # dictToSend = {'question': 'what is the answer?'}
                # res = requests.post('/endpoint', json=dictToSend)
                # session
                return redirect('/')
    messages = ds.select('select id, dt_message, username, message, attachment_name from messages order by dt_message')
    str_messages = ''
    for item in messages:
        dt_mes = date2str(datetime.datetime.strptime(item["dt_message"], "%Y-%m-%d %H:%M:%S.%f"))
        # templ = '<form><b style="color: blue">{{username}}</b> {{ dt_mes }}<br>{{ message }}<br>{{ file_button }}</form>'
        # print(templ)
        if item['attachment_name'] is not None:
            templ2 = render_template('record.html', username=item["username"], dt_mes=dt_mes, message=item['message'],
                file_button=Markup('<input type="text" name="message_id" value="{{ message_id }}" hidden><input type="submit" value="{{ attachment_name }}" action="/"><br>')
            )
            templ2 = templ2.replace('{{ message_id }}', str(item['id']))
            templ2 = templ2.replace('{{ attachment_name }}', item['attachment_name'])
        else:
            templ2 = render_template('record.html', username=item["username"], dt_mes=dt_mes, message=item['message'], file_button='')
        # print(templ2)
        str_messages += templ2


    final_html = render_template('simple_form.html', special=Markup(str_messages))
    return final_html


if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
    # print(ds.get_message_attachment(2))
