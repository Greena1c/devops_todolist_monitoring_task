from django.contrib.auth.decorators import login_required
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from lists.forms import TodoForm, TodoListForm
from lists.models import Todo, TodoList

REQUEST_COUNT = Counter("http_requests_total", "Total HTTP Requests", ["method"])

def metrics(request):
    REQUEST_COUNT.labels(method=request.method).inc()
    return HttpResponse(generate_latest(), content_type=CONTENT_TYPE_LATEST)

def index(request):
    return render(request, "lists/index.html", {"form": TodoForm()})


def todolist(request, todolist_id):
    todolist = get_object_or_404(TodoList, pk=todolist_id)
    if request.method == "POST":
        redirect("lists:add_todo", todolist_id=todolist_id)

    return render(
        request, "lists/todolist.html", {"todolist": todolist, "form": TodoForm()}
    )


def add_todo(request, todolist_id):
    if request.method == "POST":
        form = TodoForm(request.POST)
        if form.is_valid():
            user = request.user if request.user.is_authenticated else None
            todo = Todo(
                description=request.POST["description"],
                todolist_id=todolist_id,
                creator=user,
            )
            todo.save()
            return redirect("lists:todolist", todolist_id=todolist_id)
        else:
            return render(request, "lists/todolist.html", {"form": form})

    return redirect("lists:index")


@login_required
def overview(request):
    if request.method == "POST":
        return redirect("lists:add_todolist")
    return render(request, "lists/overview.html", {"form": TodoListForm()})


def new_todolist(request):
    if request.method == "POST":
        form = TodoForm(request.POST)
        if form.is_valid():
            # create default todolist
            user = request.user if request.user.is_authenticated else None
            todolist = TodoList(creator=user)
            todolist.save()
            todo = Todo(
                description=request.POST["description"],
                todolist_id=todolist.id,
                creator=user,
            )
            todo.save()
            return redirect("lists:todolist", todolist_id=todolist.id)
        else:
            return render(request, "lists/index.html", {"form": form})

    return redirect("lists:index")


def add_todolist(request):
    if request.method == "POST":
        form = TodoListForm(request.POST)
        if form.is_valid():
            user = request.user if request.user.is_authenticated else None
            todolist = TodoList(title=request.POST["title"], creator=user)
            todolist.save()
            return redirect("lists:todolist", todolist_id=todolist.id)
        else:
            return render(request, "lists/overview.html", {"form": form})

    return redirect("lists:index")
