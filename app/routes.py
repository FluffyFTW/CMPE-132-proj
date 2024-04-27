import requests
from app.features.roles import roles
from app.features.models import user, books, book_requests, checkout_list
from app.features.forms import login_form, sign_up_form, edit_profile_form, order_form, checkout_form, promotion_form
from flask import session, request, flash, redirect, render_template, url_for
from flask_login import login_user, logout_user, fresh_login_required, current_user, login_required
from datetime import datetime
from sqlalchemy.sql import func
from app import myapp_obj, db

@myapp_obj.before_request
def create_db():
    db.create_all()
    existing_user = user.query.filter_by(username="super_admin").first()
    if existing_user == None:
        admin = user(username = "super_admin", perms = roles.admin)
        admin.set_password("super_password")
        db.session.add(admin)

        librarian = user(username = "test_librarian", perms = roles.librarian)
        librarian.set_password("pass123")
        db.session.add(librarian)

        student_lib = user(username = "test_student_lib", perms = roles.student_libraian)
        student_lib.set_password("pass123")
        db.session.add(student_lib)

        student = user(username = "test_student", perms = roles.student)
        student.set_password("pass123")
        db.session.add(student)

        db.session.commit()
    
@myapp_obj.route("/")
def landing():
    return render_template('landing.html')

@myapp_obj.route("/login/", methods=['GET', 'POST'])
def login():
    logout_user()
    form = login_form()
    if form.validate_on_submit():
        site_user = user.query.filter_by(username=form.username.data).first()
        if site_user and site_user.check_password(form.password.data) == True:
            login_user(site_user)

            return redirect('/home/')
        else:
            flash("Please register for an account.")
            return render_template('login.html', form=form)
    return render_template('login.html', form=form)

@myapp_obj.route("/logout/")
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect('/login/')


@myapp_obj.route("/edit_profile/", methods=['GET', 'POST'])
@login_required
def edit_user_profile():
    form = edit_profile_form()
    if form.validate_on_submit():
        user_id = current_user.id 
        user_var = user.query.get_or_404(current_user.id)
        exists = user.query.filter(user.username == form.new_username.data).first() is not None
        if exists and current_user.username != form.new_username.data:
            flash("Username is already taken")
        else:
            user_var.username = form.new_username.data
            user_var.set_password(form.new_password.data)
            db.session.add(user_var)
            db.session.commit()
            return redirect('/home/')
    return render_template('edit_profile.html', form=form)

@myapp_obj.route("/sign_up/",methods = ['POST', 'GET'])
def sign_up():
    logout_user()
    form = sign_up_form()
    if form.validate_on_submit():
        existing_user = user.query.filter_by(username=form.username.data).first()
        if existing_user == None:
            if(form.email.data.find(".edu") != -1):
                role = roles.student
            else:
                role = roles.public
            new_user = user(username = form.username.data, perms = role)
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect("/home/")
        else:
            flash("User name is already registered.")
    return render_template('signup.html', form=form)
    
@myapp_obj.route("/home/", methods=['GET', 'POST'])
@login_required
def home():
    match current_user.perms:
        case roles.admin:
            return redirect("/home/admin/")
        case roles.librarian:
            return redirect("/home/librarian/")
        case roles.student_libraian:
            return redirect("/home/student_lib/")
        case roles.student:
            return redirect("/home/student/")
        case roles.public:
            return render_template('public.html', user = current_user)

@myapp_obj.route("/home/admin/", methods=['GET', 'POST'])
@login_required
def home_admin():
    if(current_user.perms != roles.admin):
        return redirect("/home/")
    return render_template('admin.html', user = current_user)

@myapp_obj.route("/home/librarian/", methods=['GET', 'POST'])
@login_required
def home_librarian():
    if(current_user.perms != roles.librarian and current_user.perms != roles.admin):
        return redirect("/home/")
    return render_template('librarian.html', user = current_user)

@myapp_obj.route("/home/student_lib/", methods=['GET', 'POST'])
@login_required
def home_student_lib():
    if(current_user.perms != roles.student_libraian and current_user.perms != roles.admin):
        return redirect("/home/")
    return render_template('student_lib.html', user = current_user)

@myapp_obj.route("/home/student/", methods=['GET', 'POST'])
@login_required
def home_student():
    if(current_user.perms != roles.student and current_user.perms != roles.admin):
        return redirect("/home/")
    return render_template('student.html', user = current_user)

@myapp_obj.route("/home/public/", methods=['GET', 'POST'])
@login_required
def home_public():
    if(current_user.perms != roles.admin):
        return redirect("/home/")
    return render_template('public.html', user = current_user)


@myapp_obj.route("/deactivate/", methods = ['POST', 'GET'])
@login_required
def delete_account():
    account = user.query.filter(user.id == current_user.id).first()
    db.session.delete(account)
    db.session.commit()
    flash("Your account has been deactivated.")
    return redirect(url_for('login'))

@myapp_obj.route("/checkout/", methods = ['POST', 'GET'])
@login_required
def checkout():
    form = checkout_form()
    if form.validate_on_submit():
        book = books.query.filter_by(title = form.book.data.lower().strip()).first() 
        if book is not None and book.amount > 0:
            if(book.student_only and current_user.perms == roles.public):
                flash("This book is Student Only")
            else:
                flash(f"{book.title} has now been added to your account")
                book.amount = book.amount - 1
                checkout_log = checkout_list(book_id = book.id, user_id = current_user.id)
                db.session.add(checkout_log)
                db.session.commit()
        else:
            flash("Sorry this book is not with us.")
    return render_template("checkout.html", form = form)

@myapp_obj.route("/checkin/", methods = ['POST', 'GET'])
@login_required
def checkin():
    form = checkout_form()
    if form.validate_on_submit():
        book = books.query.filter_by(title = form.book.data.lower().strip()).first() 
        if book is not None:
                checkout_entry = checkout_list.query.filter_by(book_id = book.id, user_id = current_user.id).first()
                if(checkout_entry is not None):
                    flash(f"Thank you for returning {book.title}")
                    checkout_entry.checkout_in = func.now()
                    db.session.commit()
                else:
                    flash("Sorry this book is not in your account")
        else:
            flash("Sorry this book is not in your account")
    return render_template("checkin.html", form = form)

@myapp_obj.route("/order_books/", methods = ['POST', 'GET'])
@login_required
def order_books():
    if(current_user.perms != roles.librarian and current_user.perms != roles.admin):
        return redirect("/home/")
    form = order_form()
    if form.validate_on_submit():
        book = books.query.filter_by(title = form.book.data.lower().strip()).first() 
        if book is not None:
            book.amount = book.amount + form.quantity.data
            db.session.commit()
            flash("Book ammount updated")
        else:
            new_book = books(title = form.book.data.lower().strip(), amount = form.quantity.data, student_only = form.student_only.data)
            db.session.add(new_book)
            db.session.commit()
            flash("New books purchased")
    return render_template("order_form.html", form = form)

@myapp_obj.route("/request_books/", methods = ['POST', 'GET'])
@login_required
def request_books():
    if(current_user.perms == roles.librarian or current_user.perms == roles.admin):
        return redirect("/order_books/")
    elif(current_user.perms != roles.student_libraian ):
        return redirect("/home/")
    form = order_form()
    if form.validate_on_submit():
        flash(f"{form.book.data} are requested")
        book_req = book_requests(requester_id = current_user.id, 
                                 titles = form.book.data, 
                                 amount = form.quantity.data, 
                                 student_only = form.student_only.data, 
                                 status = "Pending")
        db.session.add(book_req)
        db.session.commit()
    return render_template("request_form.html", form = form)

@myapp_obj.route("/approve_request/", methods = ['POST', 'GET'])
@login_required
def approve_requests():
    if(current_user.perms == roles.student_libraian):
        return redirect("/request_books/")
    elif(current_user.perms == roles.student or current_user.perms == roles.public):
        return redirect("/home/")
    
    curr_request = book_requests.query.filter_by(status = "Pending").first()
    if(curr_request != None):
        requester = user.query.filter_by(id = curr_request.requester_id).first()
        if request.form.get("action", "Approve"):
            curr_request.status = "Approve"
            book = books.query.filter_by(title = curr_request.titles.lower().strip()).first() 
            if book is not None:
                book.amount = book.amount + curr_request.amount
                db.session.commit()
                flash("Book ammount updated")
            else:
                new_book = books(title = curr_request.titles.lower().strip(), amount = curr_request.amount, student_only = curr_request.student_only)
                db.session.add(new_book)
                db.session.commit()
                flash("New books purchased")
        elif request.form.get("action", "Deny"):
            flash("Request Denied")
            current_user.staus == "Deny"
            db.session.commit()
        return render_template("approve_request.html", request = curr_request, requester = requester)
    else:
        return render_template("no_request.html")
    
@myapp_obj.route("/change_roles/", methods = ['POST', 'GET'])
@login_required
def change_roles():
    if(current_user.perms != roles.admin):
        return redirect("/home/")
    form = promotion_form()
    if form.validate_on_submit():
        # target = user.query.filter_by(username = form.username.data)
        print(form.role_select.data)
    return render_template("change_roles.html")