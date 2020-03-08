from flask import jsonify, request, render_template, url_for, flash, redirect
from project.forms import RegistrationForm, LoginForm
from project.db_models import User, Freewrite, Feedback, Prompt
from project import application, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import desc

	
@application.route("/")
def index():
    return render_template("index.html")

@application.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", incomplete_freewrite=has_incomplete_freewrite(), incomplete_feedback=has_incomplete_feedback())
    
@application.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(fname=form.fname.data, lname=form.lname.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template("register.html", form=form)
    
    
@application.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template("login.html", form=form)  


@application.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@application.route("/view")
@login_required
def view():
    prompt_id = request.args.get('n', default = 1, type = int)
    freewrite = Freewrite.query.filter(Freewrite.user==current_user, Freewrite.prompt_id==prompt_id).first()
    if freewrite is None:
        return redirect(url_for('dashboard'))
    else:
       prompt = Prompt.query.filter(Prompt.id==prompt_id).first().prompt
       response = freewrite.content
       feedback_general = False
       feedback_specific = None
       feedback_query = Feedback.query.filter(Feedback.freewrite == freewrite).first()
       if feedback_query is not None:
           feedback_general = feedback_query.general
           feedback_specific = feedback_query.specific
       return render_template("view.html", prompt=prompt, response=response, feedback_general = feedback_general, feedback_specific = feedback_specific, question = freewrite.question)  

@application.route("/get_completed", methods=['GET', 'POST'])
@login_required
def get_completed():
    if request.method == 'POST':
        try:
            message = request.form.get("message");
            if message == "getCompleted":
                freewrites = get_all_freewrites()
                return jsonify({'freewrites': freewrites})
        except:
            return jsonify({'error':'error'})

@application.route("/send_freewrite", methods=['GET', 'POST'])
@login_required
def send_freewrite():
    if request.method == 'POST':
        try:
            # retrieve AJAX call contents
            content = request.form.get("content");
            question = request.form.get("question");
            submitting = int(request.form.get("submitting")) == 1
            prompt_id = int(request.form.get("prompt_id"))
            
            # check if we already have an entry
            entry = Freewrite.query.filter(Freewrite.user==current_user, Freewrite.prompt_id==prompt_id).first()
            
            # if we need to make a new entry
            if entry is None:
                entry = Freewrite(content=content, question=question, complete=submitting, prompt_id=prompt_id, user=current_user)
                db.session.add(entry)
            # there exists an entry for this user / prompt combination
            else:
                entry.content = content
                entry.question = question
                entry.complete = submitting
        
            db.session.commit()
            if submitting:
                findMatch(current_user, prompt_id, entry)
            return jsonify({'result': 'saved' if not submitting else 'submitted'})
        except:
            return jsonify({'error':'error'})
        
@application.route("/send_feedback", methods=['GET', 'POST'])
@login_required
def send_feedback():
    if request.method == 'POST':
        try:
            # retrieve AJAX call contents
            content = request.form.get("content");
            specific = request.form.get("specific");
            submitting = int(request.form.get("submitting")) == 1
            
            entry = Feedback.query.filter(Feedback.user==current_user, Feedback.complete == 0).first()
            
            entry.general = content
            entry.complete = submitting
            entry.specific = specific
            
            if submitting:
                freewrite = Freewrite.query.filter(Freewrite.id == entry.freewrite_id).first()
                freewrite.received_feedback = True
        
            db.session.commit()
            return jsonify({'result': 'saved' if not submitting else 'submitted'})
        except:
            return jsonify({'error':'error'})
        
   
@application.route("/write", methods=['GET', 'POST'])
@login_required
def write():    
    new = request.args.get('new', default = 0, type = int)
    if new == 1:
        freewrites = Freewrite.query.filter(Freewrite.user==current_user, Freewrite.complete == False).all()
        if len(freewrites) == 0:
            prompt = get_prompt()
            return render_template("write.html", prompt=prompt.prompt, prompt_id=prompt.id, content="")  
        else:
            return redirect(url_for('dashboard'))
    else:
        if has_incomplete_freewrite():
            freewrite = Freewrite.query.filter(Freewrite.user==current_user, Freewrite.complete==False).first()
            prompt = Prompt.query.filter(Prompt.id == freewrite.prompt_id).first()
            return render_template("write.html", prompt=prompt.prompt, prompt_id=prompt.id, content=freewrite.content, question=freewrite.question)  
        else:
            return redirect(url_for('dashboard'))
        
@application.route("/feedback", methods=['GET', 'POST'])
@login_required
def feedback():    
    if has_incomplete_feedback():
        feedback = Feedback.query.filter(Feedback.user==current_user, Feedback.complete==False).first()
        freewrite = Freewrite.query.filter(Freewrite.id == feedback.freewrite_id).first()
        prompt = Prompt.query.filter(Prompt.id == freewrite.prompt_id).first()
        return render_template("feedback.html", prompt=prompt.prompt, content=freewrite.content, written_specific=feedback.specific, written_general=feedback.general, question=freewrite.question)  
    else:
        return redirect(url_for('dashboard'))
        

        
### HELPER FUNCTIONS ###
            
# retrieves the next prompt for the user
def get_prompt():
    last_freewrite = Freewrite.query.filter(Freewrite.user==current_user).order_by(desc(Freewrite.prompt_id)).first()
    last_prompt_id = 0 if last_freewrite is None else last_freewrite.prompt_id
    return Prompt.query.filter(Prompt.id == last_prompt_id + 1).first()

# returns true if a user has an incomplete freewrite
def has_incomplete_freewrite():
    return not Freewrite.query.filter(Freewrite.user==current_user, Freewrite.complete==False).first() is None

# returns true if a user has an incomplete feedback
def has_incomplete_feedback():
    return not Feedback.query.filter(Feedback.user==current_user, Feedback.complete==False).first() is None

# returns all completed freewrites by the user in a displayable format
def get_all_freewrites():
    freewrites = Freewrite.query.filter(Freewrite.user==current_user, Freewrite.complete==True).all()
    freewrite_package = []
    for i in range(len(freewrites)):
        f = freewrites[i]
        dic = {}
        dic["name"] = "Prompt " + str(f.prompt_id)
        dic["preview"] = Prompt.query.filter(Prompt.id==f.prompt_id).first().prompt[0:100]
        dic["feedback"] = f.received_feedback
        freewrite_package.append(dic)
    return freewrite_package
        
# if possible, matches users to provide each other with feedback
def findMatch(user, prompt, freewrite):
    match = Freewrite.query.filter(Freewrite.user != user, Freewrite.prompt_id == prompt, Freewrite.complete == True, Freewrite.searching_feedback == True).first()
    if match is not None:
        print("Match")
        freewrite.searching_feedback = False
        match.searching_feedback = False
        db.session.commit()
        feedback1 = Feedback(general="", specific="", user=current_user, freewrite=match)
        feedback2 = Feedback(general="", specific="", user=match.user, freewrite=freewrite)
        db.session.add(feedback1)
        db.session.add(feedback2)
        db.session.commit()