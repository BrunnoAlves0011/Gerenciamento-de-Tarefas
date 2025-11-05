from fastapi import FastAPI, HTTPException, Depends, Request, Form, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse, StreamingResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from banco import SessionLocal, engine
from modelo import Tarefas, Users, Perfil, Base
from fastapi.staticfiles import StaticFiles
import uvicorn
from starlette.middleware.sessions import SessionMiddleware
from datetime import datetime, timedelta, time
import locale

import json
import zipfile
import io
from functools import wraps
import requests

Base.metadata.create_all(bind=engine)
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="supersecretkey")

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
    print(request.session.get("logged_in"))
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

        hoje = datetime.now().date()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        fim_semana = inicio_semana + timedelta(days=6)
        
        # Tarefas de hoje
        tarefas_hoje = db.query(Tarefas).filter(
            Tarefas.user == user,
            Tarefas.data == hoje
        ).order_by(Tarefas.data, Tarefas.prioridade).all()
        
        # Tarefas da semana
        tarefas_semana = db.query(Tarefas).filter(
            Tarefas.user == user,
            Tarefas.data.between(inicio_semana, fim_semana),
            Tarefas.data > hoje
        ).order_by(Tarefas.data).all()
        
        count_hoje = len(tarefas_hoje)
        count_semana = len(tarefas_semana)

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
            "data_atual": data_atual,
            "tarefas_hoje": tarefas_hoje,
            "tarefas_semana": tarefas_semana,
            "count_hoje": count_hoje,
            "count_semana": count_semana
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



# Tela Config
@app.get("/config")
def config(request: Request, db: Session = Depends(get_db)):
    user = request.session.get("username")
    total_tarefas = db.query(Tarefas).filter(Tarefas.user == user).count()

    return templates.TemplateResponse("config.html", {
        "request": request,
        "user": user,
        "total_tarefas": total_tarefas
    })

@app.get("/config/exportar")
def exportar_dados(request: Request, db: Session = Depends(get_db)):
    try:
        user = request.session.get("username")
        
        # Busca todas as tarefas do usuário
        tarefas = db.query(Tarefas).filter(Tarefas.user == user).all()
        
        # Converte para dicionário
        dados_export = {
            'exportado_em': datetime.now().isoformat(),
            'usuario': user,
            'total_tarefas': len(tarefas),
            'tarefas': []
        }
        
        for tarefa in tarefas:
            dados_export['tarefas'].append({
                'id': tarefa.id,
                'titulo': tarefa.titulo,
                'descricao': tarefa.descricao,
                'data': tarefa.data.isoformat() if tarefa.data else None,
                'time': tarefa.time.strftime("%H:%M:%S") if tarefa.time else None,
                'prioridade': tarefa.prioridade,
                'categoria': tarefa.categoria,
                'concluido': tarefa.concluido
            })
        
        # Cria arquivo JSON
        json_data = json.dumps(dados_export, ensure_ascii=False, indent=2)
        
        # Cria arquivo ZIP em memória
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Nome do arquivo com data
            filename = f'tarefas_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            zip_file.writestr(filename, json_data)
        
        zip_buffer.seek(0)
        
        # Retorna o arquivo ZIP
        return StreamingResponse(
            zip_buffer,
            media_type='application/zip',
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Erro ao exportar dados: {str(e)}"}
        )

@app.post("/config/importar-url")
async def importar_dados_url(request: Request, db: Session = Depends(get_db)):
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return JSONResponse(
                status_code=400,
                content={"error": f"URL não fornecida"}
            )
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        dados_importados = response.json()
        
        if 'tarefas' not in dados_importados:
            return JSONResponse(
                status_code=400,
                content={"error": f"Formato de Dados invalidos"}
            )
        
        user = request.session.get("username")
        tarefas_importadas = 0
        
        for tarefa_data in dados_importados['tarefas']:
            tarefa_existente = db.query(Tarefas).filter(
                Tarefas.user   == user,
                Tarefas.titulo == tarefa_data.get('titulo'),
                Tarefas.data   == tarefa_data.get('data'),
                Tarefas.time   == tarefa_data.get('time')
            ).first()
            
            time_value = None
            if tarefa_data.get('time'):
                time_str = tarefa_data.get('time')
            if '.' in time_str:
                time_str = time_str.split('.')[0]
            time_value = datetime.strptime(time_str, "%H:%M:%S").time()

            if not tarefa_existente:
                nova_tarefa = Tarefas(
                    user=user,
                    titulo=tarefa_data.get('titulo'),
                    descricao=tarefa_data.get('descricao'),
                    data=datetime.fromisoformat(tarefa_data.get('data')) if tarefa_data.get('data') else None,
                    time=time_value,
                    prioridade=tarefa_data.get('prioridade', 'Média'),
                    categoria=tarefa_data.get('categoria', 'Outros'),
                    concluido=tarefa_data.get('concluido', False)
                )
                db.add(nova_tarefa)
                tarefas_importadas += 1
        
        db.commit()
        
        return JSONResponse(
            status_code=200,
            content={
                'success': True,
                'mensagem': f'{tarefas_importadas} tarefas importadas com sucesso!',
                'total_importadas': tarefas_importadas
            }
        )
        
    except requests.RequestException as e:
        return JSONResponse(
            status_code=400,
            content={"error": f"Erro ao acessar URL: {str(e)}"}
        )
    except json.JSONDecodeError:
        return JSONResponse(
            status_code=400,
            content={"error": "Formato JSON invalido"}
        )
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"error": f"Erro ao importar dados: {str(e)}"}
        )

@app.post("/config/importar-arquivo")
async def importar_dados(
    request: Request, 
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        if not arquivo or arquivo.filename == '':
            return JSONResponse(
                status_code=400,
                content={"error": "Nenhum arquivo enviado"}
            )
        
        conteudo = await arquivo.read()
        
        if arquivo.filename.endswith('.zip'):
            with zipfile.ZipFile(io.BytesIO(conteudo)) as zip_file:
                json_filename = zip_file.namelist()[0]
                with zip_file.open(json_filename) as json_file:
                    dados_importados = json.load(json_file)
        else:
            dados_importados = json.loads(conteudo.decode('utf-8'))
        
        if 'tarefas' not in dados_importados:
            return JSONResponse(
                status_code=400,
                content={"error": "Formato de dados inválido"}
            )
        
        user = request.session.get("username")
        tarefas_importadas = 0
        
        for tarefa_data in dados_importados['tarefas']:
            tarefa_existente = db.query(Tarefas).filter(
                Tarefas.user   == user,
                Tarefas.titulo == tarefa_data.get('titulo'),
                Tarefas.data   == tarefa_data.get('data'),
                Tarefas.time   == tarefa_data.get('time')
            ).first()
            
            time_value = None
            if tarefa_data.get('time'):
                time_str = tarefa_data.get('time')
            if '.' in time_str:
                time_str = time_str.split('.')[0]
            time_value = datetime.strptime(time_str, "%H:%M:%S").time()

            if not tarefa_existente:
                nova_tarefa = Tarefas(
                    user=user,
                    titulo=tarefa_data.get('titulo'),
                    descricao=tarefa_data.get('descricao'),
                    data=datetime.fromisoformat(tarefa_data.get('data')) if tarefa_data.get('data') else None,
                    time=time_value,
                    prioridade=tarefa_data.get('prioridade', 'Média'),
                    categoria=tarefa_data.get('categoria', 'Outros'),
                    concluido=tarefa_data.get('concluido', False)
                )
                db.add(nova_tarefa)
                tarefas_importadas += 1
        
        db.commit()
        
        return JSONResponse(
            status_code=200,
            content={
                'success': True,
                'mensagem': f'{tarefas_importadas} tarefas importadas com sucesso!',
                'total_importadas': tarefas_importadas
            }
        )
        
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"error": f'Erro ao importar dados: {str(e)}'}
        )



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
def tarefas_criar(request: Request, db: Session = Depends(get_db)):
    user = request.session.get("username")
    tarefas = db.query(Tarefas).filter_by(user=user).all()
    return templates.TemplateResponse("tarefas_criar.html", {
        "request": request, 
        "tarefas": tarefas
        })

@app.get("/home/tarefa_visualizar/{tarefa_id}")
def tarefa_view(request: Request, tarefa_id: int, db: Session = Depends(get_db)):
    user = request.session.get("username")
    tarefa = db.query(Tarefas).filter(
        Tarefas.id == tarefa_id,
        Tarefas.user == user
    ).first()

    if tarefa:
        return templates.TemplateResponse("tarefas_visualizar.html", {
            "request": request,
            "tarefa": tarefa,
            "taskId" : tarefa_id
        })
    else:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")



# Tela Perfil
@app.get("/home/perfil", response_class=HTMLResponse)
def perfil(request: Request, db: Session = Depends(get_db)):
    user = request.session.get("username")
    profile = db.query(Perfil).filter_by(username=user).first()
    tarefas = db.query(Tarefas).filter_by(user=user).all()

    total = len(tarefas)
    concluidas = 0
    andamento = 0
    taxa = 0

    for x in tarefas:
        if x.concluido == True:
            concluidas += 1
        else:
            andamento += 1
    if concluidas == 0:
        concluidas = 0
    else:
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



# Ação Del Conta
@app.delete("/perfil/excluir-conta/{user}")
def deletar_conta(request: Request, user: str, db: Session = Depends(get_db)):
    perfil = db.query(Perfil).filter_by(username=user).delete()

    users = db.query(Users).filter_by(username=user).delete()

    if not perfil:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")
    
    tarefas = db.query(Tarefas).filter_by(user=user).delete()

    db.commit()

    logout()

    return {"message": "Tarefa excluída com sucesso"}



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

    time = datetime.now()
    time_obj = datetime.time(time)
    data_obj = None
    if data:
        data_obj = datetime.strptime(data, "%Y-%m-%d").date()
    
    nova_tarefa = Tarefas(
        user=user,
        titulo=titulo,
        descricao=descricao,
        data=data_obj,
        time = time_obj,
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
