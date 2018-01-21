


from flask import Flask, request, session, redirect, url_for, render_template, flash
from wtforms import Form, validators, BooleanField, FloatField, StringField, SelectField, PasswordField, SubmitField, TextAreaField
from wtforms_components import DateTimeField, DateRange, TimeField
from datetime import datetime, timedelta

from athome import app, sign, actives, uprofile, basics

app.secret_key = 'OLOLO'


class RegForm(Form):
    fullname = StringField('Fullname', [validators.Length(min=4, max=25)])
    code = SelectField('Code', choices=[('7', '+7'), ('38', '+38'), ('375', '+375')])
    phone = StringField('Phone', [validators.Length(min=10, max=20)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('confirm')
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])


class ProfileForm(Form):
    nickname = StringField('nickname', [validators.DataRequired()]) #[validators.Length(min=4, max=25)]
    #photo =
    fullname = StringField('fullname', [validators.DataRequired()]) #, [validators.Length(min=4, max=30)]
    code = SelectField(u'Code', choices=[('7', '+7'), ('38', '+38'), ('375', '+375')])
    phone = StringField('phone', [validators.DataRequired()]) #, [validators.Length(min=10, max=20)]
    latitude = FloatField('latitude', [validators.NumberRange(min=-90, max=90, message='Invalid latitude'), validators.DataRequired()])
    longitude = FloatField('longitude', [validators.NumberRange(min=-180, max=180, message='Invalid longitude'), validators.DataRequired()])
    submit = SubmitField('UPDATE')


class AddForm(Form):
    type = SelectField('type', choices=[('Sport', 'Sport'), ('Games', 'Games'),
                                         ('Practises', 'Practises'), ('Language', 'Language'),
                                         ('Dance', 'Dance'), ('Kids', 'Kids'), ('Eco', 'Eco'),
                                         ('Lost/Found', 'Lost/Found'), ('Event', 'Event'),
                                         ('Charity', 'Charity'), ('Music', 'Music'), ('Art', 'Art')])
    #photo =
    title = StringField('Title', [validators.DataRequired()])
    description = TextAreaField('Description', [validators.DataRequired()])
    starts = DateTimeField('Start date', format='%Y-%m-%d')
    start_time = TimeField('Start time', format='%H:%M')
    ends = DateTimeField('End date', format='%Y-%m-%d')
    end_time = TimeField('End time', format='%H:%M')
    latitude = FloatField('Latitude', [validators.NumberRange(min=-90, max=90, message='Invalid latitude'),
                                       validators.DataRequired()])
    longitude = FloatField('Longitude', [validators.NumberRange(min=-180, max=180, message='Invalid longitude'),
                                         validators.DataRequired()])
    access = BooleanField('Accessable')
    submit = SubmitField('POST')


class CommentForm(Form):
    comment = TextAreaField('comment', [validators.DataRequired()])
    post = SubmitField('POST')

##############################  ACTIVITIES  ##################################


@app.route('/', methods=['GET'])
def actives_list():
    if not session.get('logged_in') or not session.get('user'):
        return render_template('signin.html', error=None)
    [list, message] = actives.show_actives(int(session.get('user')))
    return render_template('actives.html', entries=list, error=message)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if not session.get('logged_in') or not session.get('user'):
        return render_template('signin.html', error=None)

    form = AddForm(request.form)
    id = session.get('user')
    if request.method == 'GET':
        return render_template('add.html', form=form, error=None)
    if request.method == 'POST' and form.validate():

        #photo =
        [starts] = form.starts.raw_data
        [stime] = form.start_time.raw_data
        [ends] = form.ends.raw_data
        [etime] = form.end_time.raw_data

        starts = starts + ' ' + stime
        ends = ends + ' '+ etime

        #validating if trying to add event in the next 6 months
        sd = datetime.strptime(starts, "%Y-%m-%d %H:%M")
        ed = datetime.strptime(ends, "%Y-%m-%d %H:%M")
        print(sd, ed)
        if sd > ed:
            print(sd,ed)
            return render_template('add.html', form=form, error='Activity should end later than it starts')
        if sd < datetime.now() or ed > datetime.now() + timedelta(6*365/12):
            return render_template('add.html', form=form, error='Activity should start and end within next 6 months')

        new_activity = actives.Activity(None, form.type.data, id, form.title.data,
                                        starts, ends, form.latitude.data, form.longitude.data,
                                        form.description.data, 0, 0, None, form.access.data)

        [new_id, error] = actives.add_act(new_activity)
        if not new_id:
            return render_template('add.html', form=form, error=error)

        return render_template('an_act.html', act_id=new_id, activity=new_activity, joined=True,
                               word='comments', comments=[], form=CommentForm())
    if not form.validate():
        print(form.starts.data)
        flash_errors(form)
        return render_template('add.html', form=form, error=None)

@app.route('/<int:act_id>', methods=['GET', 'POST'])
def single_activ(act_id):

    if not session.get('logged_in') or not session.get('user'):
        return render_template('signin.html', error=None)

    [act, error1] = actives.single_act(act_id)
    if act == None:
        abort(404)
    id = session.get('user')
    [im_in, whatever] = actives.joined(act_id, id)
    [comms, error2] = actives.get_comments(act_id)
    if act.c % 10 == 1 or act.c == 1:
        word = ' comment'
    else:
        word = ' comments'
    form = CommentForm(request.form)
    #form2= Form(prefix='form2')

    if request.method == 'GET':
        return render_template('an_act.html', activity=act, joined = im_in, word=word,
                               comments=comms, error1=error1, error2=error2, form=form)

    if request.method == 'POST' and form.validate():
        [done, error4] = actives.comm_act(act_id, id, form.comment.data)
        if done:
            [comms, error2] = actives.get_comments(act_id)
            act.c = act.c + 1
            return render_template('an_act.html', act_id=act_id, activity=act, joined=im_in, word=word,
                               comments=comms, form=form, error1=error2, error2=None)
        else:
            return render_template('an_act.html', act_id=act_id, activity=act, joined=im_in, word=word,
                                   comments=comms, form=form, error1=error4, error2=None)

    if request.method == 'POST' and request.form['btn'] == 'JOIN':
        [joined, error3] = actives.join_act(act.id, id)
        if joined:
            act.j = act.j+1
            im_in = True
            return render_template('an_act.html', activity=act, joined = im_in, word=word,
                                   comments=comms, error1=error1, error2=error2, form=form)
        else:
            return render_template('an_act.html', activity=act, joined = im_in, word=word,
                                   comments=comms, error1=error3, error2=None, form=form)



############################  SIGN IN / UP  ##################################


@app.route('/signin', methods=['GET', 'POST'])
def signin():

    if request.method == 'GET':
        return render_template('signin.html', error=None)

    if request.method == 'POST':
        code = int(request.form['code'])
        phone = request.form['phone']
        password = request.form['password']
        phone = basics.phone_validation(phone)

        if not phone:
            return render_template('signin.html', error='Invalid phone number')

        [uid, message] = sign.login_check(code, phone, password)  # check if there's 10 digits (we support CIS only now)
        if not message:  # check are the login data correct
            session['logged_in'] = True
            session['user'] = uid
            print("logged in:", session.get('logged_in'), ', as id:', session.get('user'))
            return redirect(url_for('actives_list'))
        else:
            return render_template('signin.html', error=message)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegForm(request.form)

    if request.method == 'GET':
        return render_template('register.html', form=form, error=None)

    if request.method == 'POST' and form.validate():
        print(1)
        phone = form.phone.data
        phone = basics.phone_validation(phone)
        if not phone:
            print(2)
            return render_template('register.html', form=form, error='Invalid phone number')

        code = form.code.data
        code = int(code)

        [uid, message] = sign.add_user([form.fullname.data, phone, code, form.password.data])
        if not message:
            print(3)
            session['user'] = uid
            session['logged_in'] = True
            flash("Welcome home! You can edit the data you've added anytime in Profile")
            return redirect(url_for('actives_list'))
        else:
            print(4)
            return render_template('register.html', form=form, error=message)
    if request.method == 'POST' and not form.validate():
        flash_errors(form)
        print(5)
        return render_template('register.html', form=form, error=None)


################################  PROFILE  ###################################


@app.route('/profile', methods=['GET'])
def profile():
    if not session.get('logged_in') or not session.get('user'):
        return render_template('signin.html', error=None)
    else:
        id = int(session.get('user'))
        print(id)
        [userdata, error] = uprofile.show_profile(id)

        return render_template('profile.html', error=error, profile=userdata)

@app.route('/settings', methods=['GET','POST'])
def settings():

    if not session.get('logged_in') or not session.get('user'):
        return render_template('signin.html', error=None)

    form1 = ProfileForm(request.form)
    id = session.get('user')
    [userdata, error] = uprofile.show_profile(id)

    if request.method == 'GET':
        return render_template('settings.html', form1=form1, fn=userdata.f, nn=userdata.n,
                               cr=userdata.c, pn=userdata.p, la=userdata.la, lo=userdata.lo, error=error)

    if request.method == 'POST' and form1.validate():

        #did phone or display name changed?
        phone = form1.phone.data
        clean_phone = basics.phone_validation(phone)

        if not clean_phone:
            return render_template('settings.html', form1=form1, fn=form1.fullname.data,
                               nn=form1.nickname.data, cr=form1.code.data, pn=userdata.p,
                               la=form1.latitude.data, lo=form1.longitude.data,
                               ph=None, error='Invalid phone number')

        code = form1.code.data
        code = int(code)

        pc = userdata.p != clean_phone or userdata.c != code #did phone number change?
        dnc = userdata.n != form1.nickname.data #did display name change?

        #saving changes
        newdata = uprofile.UserData(form1.fullname.data, form1.nickname.data, code, clean_phone,
                                   form1.latitude.data, form1.longitude.data, None)

        #trying to update
        [done, upd_data, error] = uprofile.edit_profile(userdata, newdata, id, pc, dnc)
        if done and not error:
            return render_template('profile.html', profile=upd_data, error=None)
        else:
            return render_template('settings.html', form1=form1, fn=upd_data.f, nn=upd_data.f,
                                   cr=upd_data.c, pn=upd_data.p, la=upd_data.la, lo=upd_data.lo,
                                   ph=upd_data.ph, error=error)

    if not form1.validate() and request.form['btn'] != 'LOGOUT':
        flash_errors(form1)
        return render_template('settings.html', form1=form1, fn=form1.fullname.data,
                               nn=form1.nickname.data, cr=form1.code.data, pn=form1.phone.data,
                               la=form1.latitude.data, lo=form1.longitude.data,
                               ph=None, error=None)

    if request.method == 'POST' and request.form['btn'] == 'LOGOUT':

        session.clear()
        return render_template('signin.html', error=None)

@app.route('/notifs', methods=['GET'])
def notifs():
    if not session.get('logged_in') or not session.get('user'):
        return render_template('signin.html', error=None)
    [notif_list, error] = actives.show_notifs(session.get('user'))
    return render_template('notifs.html', error=error, notifs=notif_list)


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))

if __name__ == '__main__':
    app.run()
    #app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    #app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
