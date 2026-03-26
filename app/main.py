from typing import Annotated

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.db import get_session, init_db
from app.models import Document, Project, ProjectStatus, Requirement, Task
from app.schemas import CompareRequest, CompareResult, ProjectCreate, ProjectRead, RequirementCreate, TaskCreate
from app.services import compare_texts, requirements_to_csv, simple_ocr

app = FastAPI(title="Nano Lab MVP API", version="0.2.0")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
SessionDep = Annotated[Session, Depends(get_session)]


@app.on_event("startup")
def on_startup() -> None:
    init_db()


# ===== Web pages =====
@app.get("/", response_class=HTMLResponse)
def web_home(request: Request, session: SessionDep):
    projects = list(session.exec(select(Project).order_by(Project.created_at.desc())).all())
    return templates.TemplateResponse("index.html", {"request": request, "projects": projects})


@app.post("/web/projects")
def web_create_project(session: SessionDep, name: str = Form(...), description: str = Form("")):
    project = Project(name=name, description=description)
    session.add(project)
    session.commit()
    session.refresh(project)
    return RedirectResponse(url=f"/projects/{project.id}/view", status_code=303)


@app.get("/projects/{project_id}/view", response_class=HTMLResponse)
def web_project_view(project_id: int, request: Request, session: SessionDep):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    reqs = list(session.exec(select(Requirement).where(Requirement.project_id == project_id).order_by(Requirement.created_at.desc())).all())
    tasks = list(session.exec(select(Task).where(Task.project_id == project_id).order_by(Task.created_at.desc())).all())
    docs = list(session.exec(select(Document).where(Document.project_id == project_id).order_by(Document.created_at.desc())).all())
    share_url = str(request.url)

    return templates.TemplateResponse(
        "project.html",
        {
            "request": request,
            "project": project,
            "requirements": reqs,
            "tasks": tasks,
            "documents": docs,
            "share_url": share_url,
        },
    )


@app.post("/projects/{project_id}/web/requirements")
def web_add_requirement(
    project_id: int,
    session: SessionDep,
    title: str = Form(...),
    detail: str = Form(""),
    priority: str = Form("medium"),
):
    if not session.get(Project, project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    req = Requirement(project_id=project_id, title=title, detail=detail, priority=priority)
    session.add(req)
    session.commit()
    return RedirectResponse(url=f"/projects/{project_id}/view", status_code=303)


@app.post("/projects/{project_id}/web/tasks")
def web_add_task(project_id: int, session: SessionDep, title: str = Form(...)):
    if not session.get(Project, project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    task = Task(project_id=project_id, title=title)
    session.add(task)
    session.commit()
    return RedirectResponse(url=f"/projects/{project_id}/view", status_code=303)


@app.post("/projects/{project_id}/web/documents")
async def web_upload_document(project_id: int, session: SessionDep, file: UploadFile = File(...)):
    if not session.get(Project, project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    content = await file.read()
    text = simple_ocr(file.filename, content)
    doc = Document(project_id=project_id, filename=file.filename, extracted_text=text)
    session.add(doc)
    session.commit()
    return RedirectResponse(url=f"/projects/{project_id}/view", status_code=303)


# ===== API endpoints =====
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/projects", response_model=ProjectRead)
def create_project(payload: ProjectCreate, session: SessionDep) -> Project:
    project = Project(name=payload.name, description=payload.description)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


@app.get("/projects", response_model=list[ProjectRead])
def list_projects(session: SessionDep) -> list[Project]:
    return list(session.exec(select(Project).order_by(Project.created_at.desc())).all())


@app.patch("/projects/{project_id}/activate", response_model=ProjectRead)
def activate_project(project_id: int, session: SessionDep) -> Project:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    project.status = ProjectStatus.active
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


@app.post("/projects/{project_id}/requirements")
def add_requirement(project_id: int, payload: RequirementCreate, session: SessionDep) -> Requirement:
    if not session.get(Project, project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    req = Requirement(project_id=project_id, title=payload.title, detail=payload.detail, priority=payload.priority)
    session.add(req)
    session.commit()
    session.refresh(req)
    return req


@app.get("/projects/{project_id}/requirements")
def list_requirements(project_id: int, session: SessionDep) -> list[Requirement]:
    return list(session.exec(select(Requirement).where(Requirement.project_id == project_id)).all())


@app.get("/projects/{project_id}/requirements/export.csv", response_class=PlainTextResponse)
def export_requirements_csv(project_id: int, session: SessionDep) -> str:
    rows = session.exec(
        select(Requirement.id, Requirement.title, Requirement.detail, Requirement.priority).where(
            Requirement.project_id == project_id
        )
    ).all()
    return requirements_to_csv(rows)


@app.get("/projects/{project_id}/requirements/export.pdf")
def export_requirements_pdf(project_id: int, session: SessionDep) -> Response:
    reqs = session.exec(select(Requirement).where(Requirement.project_id == project_id)).all()
    body = "\n".join([f"- [{r.priority}] {r.title}: {r.detail}" for r in reqs]) or "No requirements"
    return Response(content=f"PDF_PLACEHOLDER\nProject: {project_id}\n{body}", media_type="application/pdf")


@app.post("/projects/{project_id}/tasks")
def add_task(project_id: int, payload: TaskCreate, session: SessionDep) -> Task:
    if not session.get(Project, project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    task = Task(project_id=project_id, title=payload.title)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@app.get("/projects/{project_id}/dashboard")
def project_dashboard(project_id: int, session: SessionDep) -> dict:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    req_count = len(session.exec(select(Requirement.id).where(Requirement.project_id == project_id)).all())
    task_items = session.exec(select(Task).where(Task.project_id == project_id)).all()
    completed = len([t for t in task_items if t.done])
    docs = len(session.exec(select(Document.id).where(Document.project_id == project_id)).all())

    return {
        "project": {"id": project.id, "name": project.name, "status": project.status},
        "summary": {
            "requirements": req_count,
            "tasks_total": len(task_items),
            "tasks_completed": completed,
            "documents": docs,
        },
    }


@app.post("/projects/{project_id}/documents")
async def upload_document(project_id: int, session: SessionDep, file: UploadFile = File(...)) -> Document:
    if not session.get(Project, project_id):
        raise HTTPException(status_code=404, detail="Project not found")

    content = await file.read()
    text = simple_ocr(file.filename, content)

    doc = Document(project_id=project_id, filename=file.filename, extracted_text=text)
    session.add(doc)
    session.commit()
    session.refresh(doc)
    return doc


@app.post("/analysis/compare", response_model=CompareResult)
def compare(payload: CompareRequest) -> CompareResult:
    return compare_texts(payload.left_text, payload.right_text)
