# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Int()
    genre_id = fields.Str()
    genre = fields.Str()
    director_id = fields.Str()
    director = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)


@movie_ns.route('/')
class MovieView(Resource):
    def get(self):
        director_id = request.args.get("director_id")
        genre_id = request.args.get("genre_id")
        if director_id and genre_id:
            movies = Movie.query.filter_by(director_id=director_id, genre_id=genre_id).all()
        elif director_id:
            movies = Movie.query.filter_by(director_id=director_id).all()
        elif genre_id:
            movies = Movie.query.filter_by(genre_id=genre_id).all()
        else:
            movies = Movie.query.all()
        if movies:
            return movies_schema.dump(movies), 200
        else:
            return "", 404


@movie_ns.route('/<int:uid>')
class MovieView(Resource):
    def get(self, uid: int):
        try:
            movie = Movie.query.get(uid)
            return movie_schema.dump(movie), 200
        except Exception:
            return "", 404


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)


@director_ns.route('/<int:uid>')
class DirectorView(Resource):
    def post(self):
        req_json = request.json
        new_director = Director(**req_json)

        with db.session.begin():
            db.session.add(new_director)
        return "", 201

    def put(self, uid):
        director = Director.query.get(uid)
        req_json = request.json
        director.name = req_json.get("name")
        db.session.add(director)
        db.session.commit()
        return "", 204

    def delete(self, uid):
        director = Director.query.get(uid)
        db.session.delete(director)
        db.session.commit()
        return "", 204


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


@genre_ns.route('/<int:uid>')
class GenreView(Resource):
    def post(self):
        req_json = request.json
        new_genre = Genre(**req_json)

        with db.session.begin():
            db.session.add(new_genre)
        return "", 201

    def put(self, uid):
        genre = Genre.query.get(uid)
        req_json = request.json
        genre.name = req_json.get("name")
        db.session.add(genre)
        db.session.commit()
        return "", 204

    def delete(self, uid):
        genre = Genre.query.get(uid)
        db.session.delete(genre)
        db.session.commit()
        return "", 204


if __name__ == '__main__':
    app.run(debug=True)
