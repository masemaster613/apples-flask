from flask import Flask, redirect, url_for, render_template, request
from flask_login import LoginManager, current_user, UserMixin, login_user, login_required, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from apples import Game
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '1faf50e934b6df68fdc808d2fbad63ba'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'welcome'


apples = Game()

players = []
submission = []

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(user_id)

#set up user class
class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(20), unique=True, nullable=False)
	is_judge = False
	handed_in = False
	score = 0



	def handin(self):
		self.handed_in = True

	def __repr__(self):
		return f"User('{self.name}')"


#forms
class WelcomeForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired()])
	submit = SubmitField('Enter')

class StartForm(FlaskForm):
	submit = SubmitField('start')

class NewTurnForm(FlaskForm):
	submit = SubmitField('next turn')

class HandinForm(FlaskForm):
	cards = RadioField('Red Cards', choices=[])
	submit = SubmitField('Hand in')

class JudgeForm(FlaskForm):
	cards = RadioField('Which do you choose', choices=[])
	submit = SubmitField('Reveal')




#routes
@app.route('/')
def go_to_welcome():
	return redirect(url_for('welcome'))

@app.route("/welcome", methods=['GET', 'POST'])
def welcome():
	form = WelcomeForm()
	try:
		players.remove(current_user)
	except:
		pass
	logout_user()
	if form.validate_on_submit():
		user = User.query.filter_by(name=form.name.data).first()
		if user:
			if user not in players:
				players.append(user)
			login_user(user)
		else:
			user = User(name=form.name.data)
			db.session.add(user)
			db.session.commit()
			if user not in players:
				players.append(user)
			login_user(user)
		if apples.is_started:
			return redirect(url_for('game_started'))
		return redirect(url_for('sessions'))
	return render_template('welcome.html', title='welcome', form=form)

@app.route("/game_started", methods=['GET', 'POST'])
@login_required
def game_started():
	return render_template('game_started.html')

@app.route("/sessions", methods=['GET', 'POST'])
@login_required
def sessions():
	form = StartForm()
	if form.validate_on_submit():
		return redirect(url_for('waiting'))
	return render_template('session.html', form=form, players=players, user=current_user)

@app.route('/waiting', methods=['GET', 'POST'])
@login_required
def waiting():
	form = NewTurnForm()
	if not apples.is_started:
		apples.start(players)
	if form.validate_on_submit():
		apples.new_turn()
		try:
			print(players[apples.judge])
		except IndexError:
			apples.judge = 0
	if current_user == players[apples.judge]:
		return redirect(url_for('judging'))
	elif current_user.name in apples.submission:
		current_user.handed_in = True
		return render_template('waiting.html', apples=apples, current_user=current_user, form=form, players=players)
	else:
		return redirect(url_for('handin'))

@app.route("/judging", methods=['GET', 'POST'])
@login_required
def judging():
	form = JudgeForm()
	if request.method == 'POST':
		apples.winner = form.cards.data
		for player in players:
			if not player == players[apples.judge]:
				if apples.submission[player.name][0] == apples.winner:
					player.score += 1
	form.cards.choices = list(apples.submission.values())
	current_user.is_judge = True
	if current_user == players[apples.judge]:
		return render_template('judge.html', form=form, apples=apples, current_user=current_user, players=players)
	else:
		return redirect(url_for('waiting'))

@app.route('/handin', methods=['GET', 'POST'])
@login_required
def handin():
	current_user.is_judge = False
	form = HandinForm()
	if request.method == 'POST':
		apples.submission[current_user.name]=(form.cards.data, form.cards.data)
		apples.hands[current_user.name].remove(form.cards.data)
		apples.new_card(current_user.name)
		return redirect(url_for('waiting'))
	for card in apples.hands[current_user.name]:
		form.cards.choices.append((card,card))
	return render_template('handin.html', form=form, apples=apples, current_user=current_user, players=players)


if __name__ == '__main__':
	app.run(host='0.0.0.0',debug=True)
