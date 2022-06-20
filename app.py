from email.policy import default
from wsgiref.validate import validator
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime,date
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField, DateField, SelectField,EmailField, PasswordField
from wtforms.validators import DataRequired, ValidationError
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_mail import Message
from threading import Thread

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'warzone.pi2.2022@gmail.com' #os.environ.get('MAIL_USERNAME') 
app.config['MAIL_PASSWORD'] = 'betxrsxwtnhbzhnx' #os.environ.get('MAIL_PASSWORD')
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Warzone]'
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <warzone.pi2.2022@gmail.com>'
app.config['FLASKY_ADMIN'] = 'warzone.pi2.2022@gmail.com' #os.environ.get('FLASKY_ADMIN')

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
migrate = Migrate(app,db)
mail = Mail(app)

horarios = ['14h às 15h','15h às 16h','16h às 17h','17h às 18h','18h às 19h','19h às 20h','20h às 21h','21h às 22h','23h às 00h']

def send_async_email(app,msg):
    with app.app_context():
        mail.send(msg)

def send_email(to,subject,template,**kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
        sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app,msg])
    thr.start()
    return thr

def validate_date(form, field):
    if field.data < date.today():
        raise ValidationError('A data selecionada deve ser a partir de hoje')

class NameForm(FlaskForm):
    name = StringField('What is your name?',validators=[DataRequired()])
    submit = SubmitField('Submit')

class BookingForm(FlaskForm):
    banda = StringField('Digite o nome da banda/artista',validators=[DataRequired()])
    responsavel = StringField('Digite o nome do responsável:',validators=[DataRequired()])
    celular = StringField('Digite o número do seu celular:',validators=[DataRequired()])
    email = EmailField('Digite seu e-mail:',validators=[DataRequired()])
    dia = DateField('Selecione a data:', default=date.today(),validators=[DataRequired(),validate_date])
    horario = SelectField('Selecione o horário:', validators=[DataRequired()],choices=horarios)
    agendar = SubmitField('Agendar')

class ConsultaForm(FlaskForm):
    dia = DateField('Selecione uma data',default=date.today(),validators=[DataRequired()])
    consultar = SubmitField('Consultar')

class LoginForm(FlaskForm):
    username = StringField('Digite o nome do usuário',validators=[DataRequired()])
    password = PasswordField('Digite a senha',validators=[DataRequired()])
    entrar = SubmitField('Entrar')

"""class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), unique = True)
    users = db.relationship('User', backref = 'role')

    def __repr__(self):
        return '<Role %r>' % self.name"""

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), unique = True)
    password = db.Column(db.String(64))

    def __repr__(self):
        return '<User %r>' % self.username

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key = True)
    banda = db.Column(db.String(64))
    responsavel = db.Column(db.String(64))
    celular = db.Column(db.String(64))
    email = db.Column(db.String(64))
    dia = db.Column(db.Date)
    horario = db.Column(db.String(64))

    def __repr__(self):
        return '<Booking %r>' % self.banda



@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Booking=Booking)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),505




@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')

@app.route('/agendamento', methods=['GET','POST'])
def agendamento():
    form = BookingForm()
    if form.validate_on_submit():
        dia = Booking.query.filter_by(dia=form.dia.data).first()
        horario = Booking.query.filter_by(horario=form.horario.data,dia=form.dia.data).first()
        print(form.dia.data<date.today())
        if dia is None or ((dia is not None) and (horario is None)):
            booking = Booking(banda = form.banda.data,
                              dia=form.dia.data, 
                              responsavel=form.responsavel.data,
                              horario=form.horario.data,
                              email=form.email.data,
                              celular=form.celular.data)
            db.session.add(booking)
            db.session.commit()
            session['known'] = False
            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'],'Novo Agendamento',
                    'mail/new_booking',booking=booking)
            flash('Agendamento realizado com sucesso!')
        else:
            session['known'] = True
            flash('O horário selecionado já está ocupado!')
        session['horario'] = form.horario.data
        form.horario.data = ''
        return redirect(url_for('agendamento'))
    return render_template('agendamento.html', form=form, 
        horario=session.get('horario'), known = session.get('known',False))
    
    """ form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username = form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'],'New User',
                    'mail/new_user',user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html', form=form,dt=dt, 
        name=session.get('name'), known = session.get('known',False)) """

@app.route('/consulta', methods=['GET','POST'])
def consulta():
    form = ConsultaForm()
    ocupados = []
    livres = []
    if form.validate_on_submit():
        agendamentos = Booking.query.filter_by(dia=form.dia.data).all()
        for i in range(len(agendamentos)):
            ocupados.append(agendamentos[i].horario)
        for horario in horarios:
            if horario not in ocupados:
                livres.append(horario)
    return render_template('consulta.html', form=form, livres=livres)

@app.route('/agendados', methods=['GET','POST'])
def agendados():
    agendados = Booking.query.filter(Booking.dia >= date.today()).order_by(Booking.dia,Booking.horario).all()
    return render_template('agendados.html', agendados=agendados)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        usuario = User.query.filter_by(username=form.username.data).first()
        senha = User.query.filter_by(password=form.password.data,username=form.username.data).first()

        if (senha):
            return redirect(url_for('agendados'))
        else:
            flash('Usuário ou senha inválidos!')
    return render_template('login.html', form=form)

