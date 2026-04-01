from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager

from typing import Annotated

from sqlmodel import SQLModel, Field, Session, create_engine, select

import os


class Tarefa(SQLModel, table=True):
    id: int = Field(primary_key=True)
    titulo: str = Field(nullable=False, index=True)
    finalizado: bool = Field(default=False)


API = FastAPI()
MYSQL_USERNAME = ""
MYSQL_PASSWORD = ""
MYSQL_HOST = ""
URL = f""
ENGINE = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global URL, ENGINE
    host, uname, passwd, db = check_env()
    URL = f"mysql+pymysql://{uname}:{passwd}@{host}/{db}"
    ENGINE = create_engine(URL)
    SQLModel.metadata.create_all(ENGINE)
    yield


def get_session():
    with Session(ENGINE) as session:
        yield session


SESSAO = Annotated[Session, Depends(get_session)]
API = FastAPI(lifespan=lifespan)


@API.post("/tarefas")
def criar(titulo_tarefa: str, sessao: SESSAO):
    tarefa = Tarefa(titulo=titulo_tarefa)
    sessao.add(tarefa)
    sessao.commit()
    sessao.refresh(tarefa)
    return tarefa


@API.get("/tarefas")
def listar(sessao: SESSAO) -> list[Tarefa]:
    return sessao.exec(select(Tarefa)).all()


def check_env():
    variables = ["MYSQL_HOST", "MYSQL_USERNAME", "MYSQL_PASSWORD", "MYSQL_DATABASE"]

    for var in variables:
        if var not in os.environ.keys():
            print(f"A variável de ambiente '{var}' não foi definida")
            exit(1)

    return (
        os.environ[variables[0]],
        os.environ[variables[1]],
        os.environ[variables[2]],
        os.environ[variables[3]],
    )
