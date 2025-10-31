from fastapi import FastAPI, HTTPException, Depends, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from banco import SessionLocal, engine
from modelo import Tarefas, Users, Perfil, Base
from fastapi.staticfiles import StaticFiles
import uvicorn
from starlette.middleware.sessions import SessionMiddleware
from datetime import datetime
import locale

Base.metadata.create_all(bind=engine)
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="supersecretkey")  # use a secure random key!

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

try:
    locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
except:
    locale.setlocale(locale.LC_TIME, "Portuguese_Brazil.1252")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Tela Inicial
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    if request.session.get("logged_in"):
        return templates.TemplateResponse("login.html", {"request": request}, Form=Form)
    else:
        return templates.TemplateResponse("home.html", {"request": request})



# Tela Principal (HomePage)
@app.get("/home", response_class=HTMLResponse)
def homePage(request: Request, db: Session = Depends(get_db), error: str = None, success: str = None):
    if request.session.get("logged_in"):
        user = request.session.get("username")
        tarefas = db.query(Tarefas).filter_by(user=user).all()
        data_atual = datetime.now().strftime("%A, %d de %B de %Y")

        error_msg = None
        success_msg = None
    
        if error == "not_found":
            error_msg = "Tarefa não encontrada!"
        elif error == "tarefa_not_concluded":
            error_msg = "Ocorreu um erro ao concluir a tarefa!"
    
        if success == "deleted":
            success_msg = "Tarefa deletada com sucesso!"

        user = request.session.get("user")

        return templates.TemplateResponse("home.html",  {
            "request": request, 
            "tarefas": tarefas, 
            "user": user,
            "error": error_msg,
            "success": success_msg,
            "data_atual": data_atual
            })
    else:
        return templates.TemplateResponse("login.html", {"request": request})



# Tela Login
@app.get("/login", response_class=HTMLResponse)
def login(request: Request, error: str = None, success: str = None):
    error_msg = None
    success_msg = None
    
    if error == "error_login":
        error_msg = "Erro ao entrar na conta!"

    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": error_msg,
        "success": success_msg
        })

@app.post("/login", response_class=HTMLResponse)
def validar(request: Request, usuario: str = Form(...), senha: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(Users).filter_by(username=usuario, senha=senha).first()
    if user:
        print('Logado com sucesso')
        perfil = db.query(Perfil).filter_by(username = user.username).first()
        request.session["logged_in"] = True
        request.session["username"] = user.username
        request.session["user"] = perfil.nome
        return RedirectResponse(url='/home', status_code=303)
    else:
        print('Erro ao entrar')
        return RedirectResponse(url="/login?error=error_login", status_code=303)



# Tela Cadastro
@app.get("/cadastro", response_class=HTMLResponse)
def cadastro(request: Request, error: str = None, success: str = None):

    error_msg = None
    success_msg = None
    
    if error == "user_existed":
        error_msg = "Usuario já existe!"
    
    if success == "created":
        success_msg = "Conta criada com sucesso!"

    return templates.TemplateResponse("signup.html", {
        "request": request,
        "error": error_msg,
        "success": success_msg
        })

@app.post("/cadastro", response_class=HTMLResponse)
def validar(request: Request, name: str = Form(...), usuario: str = Form(...), email: str = Form(...), senha: str = Form(...), db: Session = Depends(get_db)):
    user_existed = db.query(Users).filter(Users.username == usuario).first()
    profile_existed = db.query(Perfil).filter(Perfil.username == usuario).first()

    data = datetime.now().strftime("%Y-%m-%d")
    data_obj = datetime.strptime(data, "%Y-%m-%d").date()

    if not user_existed and not profile_existed:
        novo_usuario = Users(username=usuario, senha=senha)
        novo_perfil = Perfil(nome=name, username=usuario, email=email, created_at=data_obj)
        db.add(novo_usuario)
        db.add(novo_perfil)
        db.commit()
        return RedirectResponse(url="/login", status_code=303)
    else:
        return RedirectResponse(url="/cadastro?error=user_existed", status_code=303)
    


# Ação Logout
@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=200)



# Tela Sobre
@app.get("/sobre")
def sobre(request: Request):
    return templates.TemplateResponse("sobre.html", {"request": request})



# Tela Ajuda
@app.get("/home/ajuda")
def ajuda(request: Request):
    return templates.TemplateResponse("ajuda.html", {"request": request})



# Tela Lista Tarefas
@app.get("/home/tarefas_lista")
def tarefas_lista(request: Request, db: Session = Depends(get_db)):
    user = request.session.get("username")
    tarefas = db.query(Tarefas).filter_by(user=user).all()
    return templates.TemplateResponse("tarefas_lista.html", {
        "request": request, 
        "tarefas": tarefas
        })

@app.get("/home/adicionar_tarefa")
def tarefas_lista(request: Request, db: Session = Depends(get_db)):
    user = request.session.get("username")
    tarefas = db.query(Tarefas).filter_by(user=user).all()
    return templates.TemplateResponse("tarefas_criar.html", {
        "request": request, 
        "tarefas": tarefas
        })



# Tela Perfil
@app.get("/home/perfil", response_class=HTMLResponse)
def perfil(request: Request, db: Session = Depends(get_db)):
    user = request.session.get("username")
    profile = db.query(Users).filter_by(username=user).first()
    tarefas = db.query(Tarefas).filter_by(user=user).all()

    total = len(tarefas)
    concluidas = 0
    andamento = 0
    taxa = 1

    for x in tarefas:
        if x.concluido == True:
            concluidas += 1
        else:
            andamento += 1

    taxa = (concluidas/total) * 100
    taxa = round(taxa, 2)

    stats = {   
        "total":  total,
        "concluida": concluidas,
        "andamento": andamento,
        "taxa": taxa
    }

    return templates.TemplateResponse("perfil.html", {
        "request"  : request,
        "profile"  : profile,
        "stats"    : stats
    })



# Açoes Tarefas
@app.post("/home/add", response_class=HTMLResponse)
def adicionar_tarefa(
    request: Request,
    titulo: str = Form(...),
    descricao: str = Form(...),
    data: str = Form(None),
    prioridade: str = Form(...),
    categoria: str = Form(...),
    db: Session = Depends(get_db)
):
    user = request.session.get("username")

    data_obj = None
    if data:
        data_obj = datetime.strptime(data, "%Y-%m-%d").date()
    
    nova_tarefa = Tarefas(
        user=user,
        titulo=titulo,
        descricao=descricao,
        data=data_obj,
        concluido=False,
        prioridade=prioridade,
        categoria=categoria
    )
    db.add(nova_tarefa)
    db.commit()
    return RedirectResponse(url="/home", status_code=303)


@app.delete("/home/tarefa/del/{task_id}")
def deletar_tarefa(
    task_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = request.session.get("username")
    
    tarefa = db.query(Tarefas).filter(
        Tarefas.id == task_id,
        Tarefas.user == user  # Segurança: só deleta se for do usuário
    ).first()
    
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    
    db.delete(tarefa)
    db.commit()
    
    return {"message": "Tarefa excluída com sucesso"}


@app.patch("/home/tarefa/finish/{tarefa_id}")
def concluir_tarefa(request: Request, tarefa_id: int, db: Session = Depends(get_db)):
    user = request.session.get("username")
    
    tarefa = db.query(Tarefas).filter(
        Tarefas.id == tarefa_id,
        Tarefas.user == user
    ).first()
    
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    
    # Alterna o status
    tarefa.concluido = not tarefa.concluido
    db.commit()
    db.refresh(tarefa)


@app.get("/home/edit/{tarefa_id}")
def edit_tarefap(request: Request, tarefa_id: int, db: Session = Depends(get_db)):
    user = request.session.get("username")
    tarefa = db.query(Tarefas).filter(
        Tarefas.id == tarefa_id,
        Tarefas.user == user
    ).first()

    return templates.TemplateResponse("tarefas_editar.html", {
        "request": request,
        "tarefa": tarefa,
        "taskId" : tarefa_id
    })


@app.patch("/home/tarefa/edit/{tarefa_id}")
async def edit_tarefaf(request: Request, tarefa_id: int, db: Session = Depends(get_db)):
    raw = await request.body()
    user = request.session.get("username")

    db.query(Tarefas).filter(
        Tarefas.id == tarefa_id,
        Tarefas.user == user
    ).update(raw)

    db.commit()

    return HTTPException(status_code=303)



if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
