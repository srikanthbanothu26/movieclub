from flask import Flask, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Movie(db.Model):
    __tablename__="movies"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    year = db.Column(db.String(10))
    director = db.Column(db.String(255))
    actors = db.Column(db.String(500))
    rated = db.Column(db.String(50))
    released = db.Column(db.String(50))
    runtime = db.Column(db.String(50))
    genre = db.Column(db.String(255))
    boxoffice = db.Column(db.String(300))
    poster_url = db.Column(db.String(500))

    def __repr__(self):
        return f"<Movie {self.title}>"

@app.route("/", methods=["GET", "POST"])
def movie_():
    if request.method == "POST":
        movie_name = request.form.get("search_term", "")
        api_key = "28f9e296"
        url = f"http://www.omdbapi.com/?t={movie_name}&apikey={api_key}"
        resp = requests.get(url)
        data = resp.json()
        print(data)
        
        if "Title" in data:
            title = data["Title"].lower()
            year = data.get("Year", "N/A")
            director = data.get("Director", "N/A")
            actors = data.get("Actors", "N/A")
            rated = data.get("Rated", "N/A")
            released = data.get("Released", "N/A")
            runtime = data.get("Runtime", "N/A")
            genre = data.get("Genre", "N/A")
            boxoffice = data.get("BoxOffice", "N/A")
            poster_url = data.get("Poster", "N/A")

            existing_movie = Movie.query.filter_by(title=title).first()
            if not existing_movie:
                new_movie = Movie(title=title, year=year, director=director, actors=actors, rated=rated,
                                  released=released, runtime=runtime, genre=genre, boxoffice=boxoffice,
                                  poster_url=poster_url)
                db.session.add(new_movie)
                db.session.commit()

    # Fetch all movie data from the database
    movie_data = Movie.query.all()
    
    return render_template("index.html", movie_data=movie_data)

@app.route("/search", methods=["POST"])
def search_movie():
    search_term_db = request.form.get("search_term_db", "")
    movie_data = Movie.query.filter(Movie.title.like(f'%{search_term_db}%')).all()
    return render_template("index.html", movie_data=movie_data)

@app.route("/delete/<int:movie_id>", methods=["POST"])
def delete_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect("/")


# Wrap the creation of tables within an application context
with app.app_context():
    db.create_all()
    
if __name__ == "__main__":
    app.run(debug=True,port=9000)
