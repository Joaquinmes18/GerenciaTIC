from datetime import datetime
from pathlib import Path
import sqlite3
from html import escape

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr, Field


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / 'feedback.db'


class FeedbackCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    email: EmailStr
    sugerencia: str = Field(min_length=1, max_length=2000)
    funcion: str = Field(min_length=1, max_length=2000)


app = FastAPI(title='PhishShield Feedback API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


def initialize_database() -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            '''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                email TEXT NOT NULL,
                sugerencia TEXT NOT NULL,
                funcion TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            '''
        )
        connection.commit()


def fetch_feedback_rows() -> list[dict[str, str | int]]:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            '''
            SELECT id, nombre, email, sugerencia, funcion, created_at
            FROM feedback
            ORDER BY id DESC
            '''
        ).fetchall()

    return [dict(row) for row in rows]


@app.on_event('startup')
def on_startup() -> None:
    initialize_database()


@app.get('/health')
def health_check() -> dict[str, str]:
    return {'status': 'ok'}


@app.get('/api/feedback')
def list_feedback() -> list[dict[str, str | int]]:
    return fetch_feedback_rows()


@app.post('/api/feedback')
def create_feedback(payload: FeedbackCreate) -> dict[str, str | int]:
    created_at = datetime.utcnow().isoformat(timespec='seconds') + 'Z'

    try:
        with sqlite3.connect(DATABASE_PATH) as connection:
            cursor = connection.execute(
                '''
                INSERT INTO feedback (nombre, email, sugerencia, funcion, created_at)
                VALUES (?, ?, ?, ?, ?)
                ''',
                (payload.nombre, payload.email, payload.sugerencia, payload.funcion, created_at),
            )
            connection.commit()
    except sqlite3.Error as error:
        raise HTTPException(status_code=500, detail='No se pudo guardar el feedback.') from error

    return {
        'message': 'Feedback guardado correctamente.',
        'id': cursor.lastrowid,
        'created_at': created_at,
    }


@app.get('/admin/feedback', response_class=HTMLResponse)
def feedback_admin_view() -> str:
    rows = fetch_feedback_rows()
    table_rows = '\n'.join(
        f'''
        <tr>
            <td>{row['id']}</td>
            <td>{escape(str(row['nombre']))}</td>
            <td>{escape(str(row['email']))}</td>
            <td>{escape(str(row['sugerencia']))}</td>
            <td>{escape(str(row['funcion']))}</td>
            <td>{escape(str(row['created_at']))}</td>
        </tr>
        '''
        for row in rows
    ) or '''
        <tr>
            <td colspan="6" class="empty-state">Todavía no hay registros guardados.</td>
        </tr>
    '''

    return f'''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PhishShield | Registros de feedback</title>
        <style>
            body {{
                margin: 0;
                font-family: Inter, Arial, sans-serif;
                background: #030712;
                color: #f3f4f6;
                padding: 32px 16px;
            }}
            .wrap {{ max-width: 1200px; margin: 0 auto; }}
            .card {{ background: rgba(17, 24, 39, 0.86); border: 1px solid rgba(255,255,255,0.08); border-radius: 18px; padding: 24px; }}
            h1 {{ margin: 0 0 8px; font-size: 32px; }}
            p {{ color: #9ca3af; line-height: 1.6; }}
            .meta {{ margin: 16px 0 20px; display: flex; gap: 12px; flex-wrap: wrap; }}
            .pill {{ background: rgba(59,130,246,0.12); color: #bfdbfe; border: 1px solid rgba(59,130,246,0.25); border-radius: 999px; padding: 8px 12px; font-size: 14px; }}
            .actions {{ margin: 16px 0 22px; display: flex; gap: 12px; flex-wrap: wrap; }}
            a.button {{ display: inline-block; text-decoration: none; color: #fff; background: #3b82f6; padding: 10px 14px; border-radius: 10px; }}
            a.secondary {{ background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.08); }}
            table {{ width: 100%; border-collapse: collapse; overflow: hidden; border-radius: 12px; }}
            th, td {{ text-align: left; padding: 14px 12px; border-bottom: 1px solid rgba(255,255,255,0.08); vertical-align: top; }}
            th {{ color: #e5e7eb; font-size: 13px; text-transform: uppercase; letter-spacing: 0.08em; background: rgba(255,255,255,0.04); }}
            td {{ color: #d1d5db; font-size: 14px; }}
            .empty-state {{ text-align: center; padding: 24px; color: #9ca3af; }}
            .note {{ margin-top: 16px; font-size: 14px; color: #9ca3af; }}
            code {{ color: #93c5fd; }}
        </style>
    </head>
    <body>
        <div class="wrap">
            <div class="card">
                <h1>Registros del formulario</h1>
                <p>Esta pantalla muestra los envíos guardados en la base SQLite local del proyecto.</p>
                <div class="meta">
                    <span class="pill">Total de registros: {len(rows)}</span>
                    <span class="pill">Base de datos: backend/feedback.db</span>
                </div>
                <div class="actions">
                    <a class="button" href="/api/feedback" target="_blank" rel="noreferrer">Ver JSON</a>
                    <a class="button secondary" href="/health" target="_blank" rel="noreferrer">Ver estado del backend</a>
                    <a class="button secondary" href="javascript:history.back()">Volver atrás</a>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Nombre</th>
                            <th>Email</th>
                            <th>Sugerencia</th>
                            <th>Función</th>
                            <th>Fecha</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
                <p class="note">Si ejecutas el backend en otro puerto, esta pantalla seguirá funcionando desde el mismo servidor FastAPI. El archivo físico de la base está en <code>backend/feedback.db</code>.</p>
            </div>
        </div>
    </body>
    </html>
    '''