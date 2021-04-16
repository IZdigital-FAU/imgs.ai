from flask import Blueprint


auth = Blueprint('auth', __name__)


@auth.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("User name already exists; please choose another one.", 'warning')
        else:
            user = create_user(form)
            if user.access:
                login_user(user)  # Log in as newly created user
                return redirect(f"{url_for('interface')}")
            flash("Thank you for requesting beta access, you will hear from us in the next 24 hours.", 'info')
    return render_template("signup.html", title="imgs.ai - Sign up for alpha", form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("interface"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(password=form.password.data):
            if user.access:
                log.info(f"{user.username} logged in")
                login_user(user)
                return redirect(url_for("interface"))
            flash("Access not granted yet!")
        else:
            flash("Invalid username/password combination", 'danger')
        return redirect(url_for("login"))
    return render_template("login.html", title="Log in", form=form)


@auth.route("/logout")
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("index"))