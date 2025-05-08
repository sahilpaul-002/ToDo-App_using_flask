from flask import Flask
# Import the render_template and redirect functions from Flask to render HTML templates and handle redirects
from flask import render_template, redirect, url_for
# Import the SQLAlchemy class from Flask-SQLAlchemy to handle database operations
from flask_sqlalchemy import SQLAlchemy
# Import mapped_column and Mapped from SQLAlchemy to define the database model
from sqlalchemy.orm import Mapped, mapped_column
# Import datetime to handle date and time operations
from datetime import datetime
# Import select, delete, update from SQLAlchemy to perform SQL queries
from sqlalchemy import select, delete, update
# Import requests module
from flask import request
# Import flash to display messages to the user
from flask import flash

# Create the db object using the SQLAlchemy constructor.
db = SQLAlchemy()

app = Flask(__name__)

#Secret key for flash messages
app.secret_key = "sahilpaul"  # Required for flash() to work

# Create database connection
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Defime the database model(databse table) for the todo list
class todoList(db.Model):
    sno:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    todoTitle:Mapped[str] = mapped_column(nullable=False)
    todoDescription:Mapped[str] = mapped_column(nullable=False)
    # Automatically set the date when a new record is created
    createdDate:Mapped[datetime] = mapped_column(default=db.func.current_timestamp())  

    def __repr__(self) -> str:
        return f"{self.sno} - {self.todoTitle} - {self.todoDescription} - {self.createdDate}"

# Create the database and the table if it doesn't exist
with app.app_context():
    db.create_all()

@app.route("/", methods=["GET", "POST"])
def insertAndDisplayData():
    # Check if HTTP method is POST
    if request.method == "POST":
        # Get the data from the form using the request object
        title = request.form.get("todoTitle")
        description = request.form.get("todoDescription")
        # Add a new todo item to the database
        todo = todoList(todoTitle=title, todoDescription=description)
        db.session.add(todo)
        db.session.commit()
        # Display flash message only in the redirected page once
        flash("Todo Added Successfully", "success")

    # Query to fetch data from table
    query = select(todoList)
    # Execute the query and fetch all results
    rows = db.session.execute(query).scalars().all()

    # Render a html file with the fetched data
    return render_template("index.html", rows=rows)

@app.route("/dataTest")
def dataTest():
    # Query to fetch data from table
    query = select(todoList)
    # Execute the query and fetch all results
    rows = db.session.execute(query).scalars().all()
    # print(rows)
    for row in rows:
        print(row.sno, row.todoTitle, row.todoDescription, row.createdDate)

    # Render a html page
    return "<p>Test Page</p?"

@app.route("/update", methods=["GET", "POST"])
def updateData():
    if request.method == "GET":
        # Extract the sno from the query parameter in the URL
        sno = request.args.get("id", type=int)
        # Fetch the data from the database using the sno
        query = select(todoList).where(todoList.sno == sno)
        todoItem = db.session.execute(query).scalars().first()
        # Render a html page with the fetched data
        return render_template("update.html", todoItem=todoItem)
    elif request.method == "POST":
        # Get the sno from the query parameter in the URL
        sno = request.args.get("id", type=int)
        # Get the updatw success status from the query parameter in the URL
        updateSuccess = request.args.get("updateSuccess", type=bool)
        # Get the updated data from the form using the request object
        title = request.form.get("todoTitle")
        description = request.form.get("todoDescription")
        # Update the todo item in the database using the sno
        query = update(todoList).where(todoList.sno == sno).values(
            todoTitle=title, todoDescription=description
        )
        print(query)
        db.session.execute(query)
        db.session.commit()
        # Display flash message only in the redirected page once
        if updateSuccess:
            flash("Update Successful", "success")
        else:
            flash("Update Unsuccessful", "danger")
        # Redirect to the main page after updating
        return redirect(url_for("insertAndDisplayData"))
    else:
        # Display flash message only in the redirected page once
        flash("Invalid Request", "danger")
        # If the request method is neither GET nor POST, return an alert
        return redirect(url_for("insertAndDisplayData"))


@app.route("/delete", methods=["GET", "POST"])
def deleteData():
    if request.method == "GET":
        # Extract the sno from the query parameter
        sno = request.args.get("id", type=int)
        # Fetch the data from the database using the sno
        query = delete(todoList).where(todoList.sno == sno)
        # Execute the delete query
        db.session.execute(query)
        # todoItem = db.get_or_404(todoList, sno)
        # db.session.delete(todoItem)
        db.session.commit()
        # Dispolay flash message only in the redirected page once
        flash("Delete Successful", "success")
        # Redirect to the main page after deletion
        return redirect(url_for("insertAndDisplayData"))
    else:
        # Dispolay flash message only in the redirected page once
        flash("Delete Unsuccessful", "danger")
        return redirect(url_for("insertAndDisplayData"))


# Run the application
if __name__ == "__main__":
    app.run(debug=True)