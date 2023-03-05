import json
import sqlite3
import secrets
from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Union
from typing import List
from pydantic import BaseModel
from datetime import datetime


origins = [
    "*"
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

con = sqlite3.connect("hackaton-lnm.db")

class LinksUser(BaseModel):
    github: Union[str, None] = None
    linkedin: Union[str, None] = None
    website: Union[str, None] = None

class RegUser(BaseModel):
    email: str
    password_hash: str
    fio: str
    links: LinksUser

class AuthUser(BaseModel):
    email: str
    password_hash: str

class User(BaseModel):
    id: int
    password_hash: str
    token: Union[str, None] = None
    tome_token: Union[str, None] = None
    fio: str
    links: Union[str, None] = None
    email: str
    resume: Union[str, None] = None
    date_create: Union[str, None] = None
    date_update: Union[str, None] = None

class Resume(BaseModel):
    position: Union[str, None] = None
    experience: Union[str, None] = None
    language: Union[str, None] = None
    technologies: Union[str, None] = None
    cv: Union[str, None] = None

class EditResume(BaseModel):
    token: Union[str, None] = None
    id_user: int
    resume: Resume

class CreateProject(BaseModel):
    user_id: int
    title: str
    body: str
    vacancies: List[str] = []

@app.get('/')
async def index():
    return {'message': 'hello world'}



@app.post('/prod/{id}')
async def proj(id):

    cursor = con.cursor()
    cursor.execute(f"SELECT * FROM projects WHERE id = {id};")
    result = cursor.fetchone()
    cursor.close()

    return {
            "id": result[0],
            "title": result[2],
            "body": result[3],
            "vacancies": result[4],
            "image": result[5]
    }

@app.post('/projects/create')
async def createproj(mod: CreateProject):

        cursor = con.cursor()
        data = json.dumps(mod.vacancies)
        data2 = json.dumps(data)
        cursor.execute(f"""INSERT INTO projects (
                user_admin,
                title,
                body,
                vacancies,
                image)
            VALUES (
                {mod.user_id},
                '{mod.title}',
                '{mod.body}',
                '{data2}',
                '["{mod.user_id}"]'
            )""")
        con.commit()
        cursor.close()
        return {"message": "create proj"}



@app.post('/projects/{id}')
async def projects(id):
    try:
        cursor = con.cursor()
        cursor.execute(f"SELECT * FROM users WHERE id = {id};")
        result = cursor.fetchone()
        cursor.close()

        data = json.loads( result[7])
        data_t = data['technologies']

        # list key word users
        data_l = data_t.split("\n")

        cursor = con.cursor()
        cursor.execute(f"SELECT * FROM projects;")
        result = cursor.fetchall()
        cursor.close()

        access = []

        for element in data_l:
            for word in result:
                key_word = word[4]
                id_word = word[0]
                print(element)
                status = key_word.find(element)

                if status != -1:
                    access.append(element + ":" + str(id_word))

        return access
    except:
        return {"error": "Error db"}

    #except:
    #    return {"error": "error save to database"}



@app.post('/profile/{id}')
async def profile(id):
    try:
        cursor = con.cursor()
        cursor.execute(f"SELECT * FROM users WHERE id = {id};")
        result = cursor.fetchone()
        cursor.close()
        try:
            links = result[5]
        except:
            links = ''
        try:
            resume = json.loads(result[7])
        except:
            resume = ''

        return {
            'id' : result[0],
            'fio': result[4],
            'links': links,
            'resume': resume,
        }
    except:
        return {"error": "error save to database"}

@app.post('/user-resume/{id}')
async def userresume(id):
    try:
        cursor = con.cursor()
        cursor.execute(f"SELECT resume FROM users WHERE id = '{id}';")
        result = cursor.fetchone()
        cursor.close()
        return json.loads(result[0])
    except:
        return {"error": "error db"}

@app.post('/edit-resume')
async def editresume(edit: EditResume):
    cursor = con.cursor()
    cursor.execute(f"SELECT * FROM users WHERE token = '{edit.token}';")
    result = cursor.fetchone()
    cursor.close()

    if result is None:
        return {'error': 'error login or password '}

    id_user = result[0]

    if id_user != edit.id_user:
        return {'error': 'error login or password 1'}

    try:
        cursor = con.cursor()
        data = json.dumps(edit.resume.__dict__)
        cursor.execute(f"UPDATE users SET resume = '{data}' WHERE id = {edit.id_user};")
        con.commit()
        cursor.close()
        return {"message": "ok"}
    except:
        return {"error": "error save to database"}

@app.post('/login')
async def login(user: AuthUser, request: Request):
    # return ip request
    # request.client.host

    cursor = con.cursor()
    cursor.execute(f"SELECT * FROM users WHERE email = '{user.email}';")
    result = cursor.fetchone()
    cursor.close()

    if result is None:
        return {'error': 'error login or password'}

    password_hash = result[1]

    if user.password_hash != password_hash:
        return {'error': 'error login or password'}

    return {
        'id': result[0],
        'token' : result[2],
        'fio': result[4]
    }

# registry
# email, password, fio, github, website, linkedin, confirm, captcha ???
@app.post('/registry')
async def registry(user: RegUser):

    #request verify user email
    cursor = con.cursor()
    cursor.execute(f"SELECT * FROM users WHERE email = '{user.email}';")
    result = cursor.fetchone()
    cursor.close()

    token = secrets.token_hex(8)
    token_time = datetime.now()

    if result is not None:
        return {"error": "email is registry"}

    cursor = con.cursor()
    data = '{"position": null, "experience": null, "language": null, "technologies": "React", "cv": null}'
    data2 = json.dumps(data)
    links = json.dumps(user.links.__dict__)
    cursor.execute(f"""INSERT INTO users (
            email,
            password_hash,
            token,
            time_token,
            fio,
            links,
            resume,
            date_create,
            date_update) 
        VALUES (
            '{user.email}',
            '{user.password_hash}',
            '{token}',
            '{token_time}',
            '{user.fio}',
            '{links}',
            '{data}',
            '{token_time}',
            '{token_time}'
        )""")

    con.commit()
    cursor.close()

    return {"token": token}

@app.post('/project-user/{id}')
async def projectuser(id):
    try:
        cursor = con.cursor()
        cursor.execute(f"SELECT * FROM projects WHERE user_admin = {id};")
        result = cursor.fetchall()
        cursor.close()
        return result
    except:
        return {"error": "error db"}

@app.post('/addusertoproject/{id_user}/{id_proj}')
async def addusertoproject(id_user, id_proj):
    cursor = con.cursor()
    cursor.execute(f"SELECT image FROM projects WHERE id = {id_proj}")
    result = cursor.fetchone()

    data = json.loads(result[0])
    data.append(id_user)
    data2 = json.dumps(data)

    cursor.execute(f"UPDATE projects SET image ='{data2}' WHERE id = {id_proj}")
    # вариант с подстановками
    # cursor.execute("UPDATE people SET name =? WHERE name=?", ("Tomas", "Tom"))
    con.commit()
    cursor.close()

    return data

@app.post('/listusersadditionalproject/{id}')
async def listusersadditionalproject(id):
    cursor = con.cursor()
    cursor.execute(f"SELECT image FROM projects WHERE id = {id}")
    result =  cursor.fetchone()
    data = json.loads(result[0])
    cursor.close()
    return data