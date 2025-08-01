from flask import Flask, jsonify, request, make_response, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://gen_user:ovLX1T)Hpg-5%3E_@94.198.216.178:5432/transhata'
app.config['SECRET_KEY'] = 'GU_GEPOLIS_GUAPPSUPPORT_ADMIN_SECRET_KEY_2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Модели данных
class HeroContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    subtitle = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text, nullable=False)


class AboutContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    text1 = db.Column(db.Text, nullable=False)
    text2 = db.Column(db.Text, nullable=False)
    text3 = db.Column(db.Text, nullable=False)
    quote = db.Column(db.Text, nullable=False)


class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    quote = db.Column(db.Text, nullable=False)
    photo = db.Column(db.String(255))


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    tech = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(255))


class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


# Новые модели для навыков
class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50))  # Frontend, Backend и т.д.
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f'<Skill {self.name}>'


class SkillCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)  # "Frontend Разработка"
    technologies = db.Column(db.String(255), nullable=False)  # "Vue.js,HTML5/CSS3"
    description = db.Column(db.Text, nullable=False)  # "Создание современных пользовательских интерфейсов..."
    icon = db.Column(db.String(50))  # Название иконки FontAwesome
    order = db.Column(db.Integer, default=0)  # Порядок отображения
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f'<SkillCard {self.title}>'


# Декоратор для проверки JWT токена
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = AdminUser.query.filter_by(username=data['username']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


# API для аутентификации
@app.route('/admin/login', methods=['POST'])
def login():
    auth = request.json

    if not auth or not auth.get('username') or not auth.get('password'):
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm="Login required!"'}
        )

    user = AdminUser.query.filter_by(username=auth.get('username')).first()

    if not user:
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm="User does not exist!"'}
        )

    if check_password_hash(user.password, auth.get('password')):
        token = jwt.encode({
            'username': user.username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'])

        return jsonify({'token': token})

    return make_response(
        'Could not verify',
        401,
        {'WWW-Authenticate': 'Basic realm="Wrong Password!"'}
    )


# API для главной страницы
@app.route('/admin/hero', methods=['GET', 'PUT'])
@token_required
def hero_content(current_user):
    if request.method == 'GET':
        hero = HeroContent.query.first()
        return jsonify({
            'title': hero.title,
            'subtitle': hero.subtitle,
            'text': hero.text
        })

    if request.method == 'PUT':
        data = request.json
        hero = HeroContent.query.first()

        hero.title = data.get('title', hero.title)
        hero.subtitle = data.get('subtitle', hero.subtitle)
        hero.text = data.get('text', hero.text)

        db.session.commit()

        return jsonify({'message': 'Hero content updated!'})


# API для раздела "Обо мне"
@app.route('/admin/about', methods=['GET', 'PUT'])
@token_required
def about_content(current_user):
    if request.method == 'GET':
        about = AboutContent.query.first()
        return jsonify({
            'title': about.title,
            'text1': about.text1,
            'text2': about.text2,
            'text3': about.text3,
            'quote': about.quote
        })

    if request.method == 'PUT':
        data = request.json
        about = AboutContent.query.first()

        about.title = data.get('title', about.title)
        about.text1 = data.get('text1', about.text1)
        about.text2 = data.get('text2', about.text2)
        about.text3 = data.get('text3', about.text3)
        about.quote = data.get('quote', about.quote)

        db.session.commit()

        return jsonify({'message': 'About content updated!'})


# API для артистов
@app.route('/admin/artists', methods=['GET', 'POST'])
@token_required
def artists(current_user):
    if request.method == 'GET':
        artists = Artist.query.all()
        return jsonify({
            'artists': [{
                'id': artist.id,
                'name': artist.name,
                'genre': artist.genre,
                'quote': artist.quote,
                'photo': artist.photo
            } for artist in artists]
        })

    if request.method == 'POST':
        data = request.json
        new_artist = Artist(
            name=data['name'],
            genre=data['genre'],
            quote=data['quote'],
            photo=data.get('photo', '')
        )
        db.session.add(new_artist)
        db.session.commit()
        return jsonify({'message': 'Artist created!', 'id': new_artist.id}), 201


@app.route('/admin/artists/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def artist(current_user, id):
    artist = Artist.query.get_or_404(id)

    if request.method == 'GET':
        return jsonify({
            'id': artist.id,
            'name': artist.name,
            'genre': artist.genre,
            'quote': artist.quote,
            'photo': artist.photo
        })

    if request.method == 'PUT':
        data = request.json
        artist.name = data.get('name', artist.name)
        artist.genre = data.get('genre', artist.genre)
        artist.quote = data.get('quote', artist.quote)
        artist.photo = data.get('photo', artist.photo)
        db.session.commit()
        return jsonify({'message': 'Artist updated!'})

    if request.method == 'DELETE':
        db.session.delete(artist)
        db.session.commit()
        return jsonify({'message': 'Artist deleted!'})


# API для проектов
@app.route('/admin/projects', methods=['GET', 'POST'])
@token_required
def projects(current_user):
    if request.method == 'GET':
        projects = Project.query.all()
        return jsonify({
            'projects': [{
                'id': project.id,
                'title': project.title,
                'tech': project.tech,
                'description': project.description,
                'link': project.link
            } for project in projects]
        })

    if request.method == 'POST':
        data = request.json
        new_project = Project(
            title=data['title'],
            tech=data['tech'],
            description=data['description'],
            link=data.get('link', '#')
        )
        db.session.add(new_project)
        db.session.commit()
        return jsonify({'message': 'Project created!', 'id': new_project.id}), 201


@app.route('/admin/projects/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def project(current_user, id):
    project = Project.query.get_or_404(id)

    if request.method == 'GET':
        return jsonify({
            'id': project.id,
            'title': project.title,
            'tech': project.tech,
            'description': project.description,
            'link': project.link
        })

    if request.method == 'PUT':
        data = request.json
        project.title = data.get('title', project.title)
        project.tech = data.get('tech', project.tech)
        project.description = data.get('description', project.description)
        project.link = data.get('link', project.link)
        db.session.commit()
        return jsonify({'message': 'Project updated!'})

    if request.method == 'DELETE':
        db.session.delete(project)
        db.session.commit()
        return jsonify({'message': 'Project deleted!'})


# API для навыков (теги)
@app.route('/admin/skills', methods=['GET', 'POST'])
@token_required
def skills(current_user):
    if request.method == 'GET':
        skills = Skill.query.order_by(Skill.order.asc()).all()
        return jsonify({
            'skills': [{
                'id': skill.id,
                'name': skill.name,
                'category': skill.category,
                'order': skill.order
            } for skill in skills]
        })

    if request.method == 'POST':
        data = request.json
        new_skill = Skill(
            name=data['name'],
            category=data.get('category', ''),
            order=data.get('order', 0)
        )
        db.session.add(new_skill)
        db.session.commit()
        return jsonify({'message': 'Skill created!', 'id': new_skill.id}), 201


@app.route('/admin/skills/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def skill(current_user, id):
    skill = Skill.query.get_or_404(id)

    if request.method == 'GET':
        return jsonify({
            'id': skill.id,
            'name': skill.name,
            'category': skill.category,
            'order': skill.order
        })

    if request.method == 'PUT':
        data = request.json
        skill.name = data.get('name', skill.name)
        skill.category = data.get('category', skill.category)
        skill.order = data.get('order', skill.order)
        db.session.commit()
        return jsonify({'message': 'Skill updated!'})

    if request.method == 'DELETE':
        db.session.delete(skill)
        db.session.commit()
        return jsonify({'message': 'Skill deleted!'})


# API для карточек навыков
@app.route('/admin/skillcards', methods=['GET', 'POST'])
@token_required
def skillcards(current_user):
    if request.method == 'GET':
        cards = SkillCard.query.order_by(SkillCard.order.asc()).all()
        return jsonify({
            'skillcards': [{
                'id': card.id,
                'title': card.title,
                'technologies': card.technologies,
                'description': card.description,
                'icon': card.icon,
                'order': card.order
            } for card in cards]
        })

    if request.method == 'POST':
        data = request.json
        new_card = SkillCard(
            title=data['title'],
            technologies=data['technologies'],
            description=data['description'],
            icon=data.get('icon', 'fas fa-code'),
            order=data.get('order', 0)
        )
        db.session.add(new_card)
        db.session.commit()
        return jsonify({'message': 'Skill card created!', 'id': new_card.id}), 201


@app.route('/admin/skillcards/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def skillcard(current_user, id):
    card = SkillCard.query.get_or_404(id)

    if request.method == 'GET':
        return jsonify({
            'id': card.id,
            'title': card.title,
            'technologies': card.technologies,
            'description': card.description,
            'icon': card.icon,
            'order': card.order
        })

    if request.method == 'PUT':
        data = request.json
        card.title = data.get('title', card.title)
        card.technologies = data.get('technologies', card.technologies)
        card.description = data.get('description', card.description)
        card.icon = data.get('icon', card.icon)
        card.order = data.get('order', card.order)
        db.session.commit()
        return jsonify({'message': 'Skill card updated!'})

    if request.method == 'DELETE':
        db.session.delete(card)
        db.session.commit()
        return jsonify({'message': 'Skill card deleted!'})


# Публичные API
@app.route('/api/hero')
def public_hero():
    hero = HeroContent.query.first()
    return jsonify({
        'title': hero.title,
        'subtitle': hero.subtitle,
        'text': hero.text
    })


@app.route('/api/about')
def public_about():
    about = AboutContent.query.first()
    return jsonify({
        'title': about.title,
        'text1': about.text1,
        'text2': about.text2,
        'text3': about.text3,
        'quote': about.quote
    })


@app.route('/api/artists')
def public_artists():
    artists = Artist.query.all()
    return jsonify([{
        'id': artist.id,
        'name': artist.name,
        'genre': artist.genre,
        'quote': artist.quote,
        'photo': artist.photo
    } for artist in artists])


@app.route('/api/projects')
def public_projects():
    projects = Project.query.all()
    return jsonify([{
        'id': project.id,
        'title': project.title,
        'tech': project.tech,
        'description': project.description,
        'link': project.link
    } for project in projects])


# Публичные API для фронтенда
@app.route('/api/hero/p')
def get_hero():
    content = HeroContent.query.first()
    if not content:
        return jsonify({"error": "Content not found"}), 404
    return jsonify({
        "title": content.title,
        "subtitle": content.subtitle,
        "text": content.text
    })


@app.route('/api/about/p')
def get_about():
    content = AboutContent.query.first()
    if not content:
        return jsonify({"error": "Content not found"}), 404
    return jsonify({
        "title": content.title,
        "text1": content.text1,
        "text2": content.text2,
        "text3": content.text3,
        "quote": content.quote
    })


@app.route('/api/artists/p')
def get_artists():
    artists = Artist.query.all()
    return jsonify([{
        "name": artist.name,
        "genre": artist.genre,
        "quote": artist.quote,
        "photo": artist.photo
    } for artist in artists])


@app.route('/api/projects/p')
def get_projects():
    projects = Project.query.all()
    return jsonify([{
        "title": project.title,
        "tech": project.tech,
        "description": project.description,
        "link": project.link
    } for project in projects])


# Новые публичные API для навыков
@app.route('/api/skills/p')
def get_skills():
    skills = Skill.query.order_by(Skill.order.asc()).all()
    return jsonify([skill.name for skill in skills])


@app.route('/api/skillcards/p')
def get_skillcards():
    cards = SkillCard.query.order_by(SkillCard.order.asc()).all()
    return jsonify([{
        "title": card.title,
        "technologies": card.technologies,
        "description": card.description,
        "icon": card.icon
    } for card in cards])


# Роуты для фронтенда
@app.route('/admin-panel')
def admin_panel():
    return render_template("admin.html")


@app.route('/new')
def new():
    return render_template("new.html")


@app.route('/')
def purple():
    return render_template("new.html")



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)