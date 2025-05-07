from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignUpForm, AddRecordForm, NoteForm, TaskForm
from .models import Record, Task, Note
from django.db.models import Q


def home(request):
    records = None

    if request.user.is_authenticated:
        query = request.GET.get('q')  # Get the search term
        if query:
            records = Record.objects.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query) |
                Q(phone__icontains=query) |
                Q(city__icontains=query) |
                Q(state__icontains=query) |
                Q(address__icontains=query),
                created_by=request.user
            )
        else:
            records = Record.objects.filter(created_by=request.user)

    # Check to see if user is logging in
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Authenticate
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You Have Been Logged In!')
            return redirect('home')
        else:
            messages.success(request, 'There Was An Error Logging In, Please Try Again..')
            return redirect('home')
    else:
        return render(request, 'home.html', {'records': records})


def logout_user(request):
    logout(request)
    messages.success(request, 'You Have Been Logged Out...')
    return redirect('home')


def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            # Authenticate and login
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "You Have Successfully Registered! Welcome!")
            return redirect('home')
    else:
        form = SignUpForm()
        return render(request, 'register.html', {'form': form})

    return render(request, 'register.html', {'form': form})


def customer_record(request, pk):
    if not request.user.is_authenticated:
        messages.success(request, "You Must Be Logged In To View That Page...")
        return redirect('home')

    record = Record.objects.get(id=pk)
    all_notes = record.notes.filter(is_pinned=False).order_by('-created_at')  # Latest first
    pinned_notes = record.notes.filter(is_pinned=True).order_by('-created_at')
    latest_notes = all_notes[:2]
    older_notes = all_notes[2:]
    tasks = record.tasks.order_by('due_date')

    note_form = NoteForm()
    task_form = TaskForm()

    # Handle note submission
    if request.method == 'POST':
        if 'content' in request.POST:
            note_form = NoteForm(request.POST)
            if note_form.is_valid():
                note = note_form.save(commit=False)
                note.record = record
                note.author = request.user
                note.save()
                messages.success(request, "Note added.")
                return redirect('record', pk=pk)

        elif 'title' in request.POST:
            task_form = TaskForm(request.POST)
            if task_form.is_valid():
                task = task_form.save(commit=False)
                task.record = record
                task.user = request.user
                task.save()
                messages.success(request, "Task created.")
                return redirect('record', pk=pk)

    return render(request, 'record.html', {
        'record': record,
        'pinned_notes': pinned_notes,
        'latest_notes': latest_notes,
        'older_notes': older_notes,
        'tasks': tasks,
        'note_form': note_form,
        'task_form': task_form,
        'now': now(),
    })


def delete_record(request, pk):
    if request.user.is_authenticated:
        record = Record.objects.get(id=pk)
        record.delete()
        messages.success(request, "Record Deleted Successfully..")
        return redirect('home')
    else:
        messages.success(request, "You Must Be Logged In To Delete A Record")
        return redirect('home')


def add_record(request):
    form = AddRecordForm(request.POST or None)
    if request.user.is_authenticated:
        if request.method == 'POST':
            if form.is_valid():
                record = form.save(commit=False)
                record.created_by = request.user
                record.save()
                messages.success(request, "Record Added..")
                return redirect('home')
        return render(request, 'add_record.html', {'form': form})
    else:
        messages.success(request, "You Must Be Logged In To Add A Record")
        return redirect('home')


def update_record(request, pk):
    if request.user.is_authenticated:
        current_record = Record.objects.get(id=pk)
        form = AddRecordForm(request.POST or None, instance=current_record)
        if form.is_valid():
            form.save()
            messages.success(request, "Record Has Been Updated!")
            return redirect('home')
        return render(request, 'update_record.html', {'form': form})
    else:
        messages.success(request, "You Must Be Logged In To Update A Record")
        return redirect('home')


@login_required
def profile_view(request):
    user = request.user
    records = Record.objects.filter(created_by=user)
    tasks = Task.objects.filter(user=user)
    task_count = tasks.count()
    completed_task_count = tasks.filter(is_completed=True).count()

    return render(request, 'profile.html', {
        'user': user,
        'records': records,
        'task_count': task_count,
        'completed_task_count': completed_task_count,
    })


@login_required
def toggle_task_completion(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.is_completed = not task.is_completed
    task.save()
    return redirect('record', pk=task.record.id)


@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task Updated.")
            return redirect('record', pk=task.record.id)
    else:
        form = TaskForm(instance=task)

    return render(request, 'edit_task.html', {'form': form, 'task': task})


@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    messages.success(request, "Task Deleted.")
    return redirect('record', pk=task.record.id)


@login_required
def edit_note(request, pk):
    note = get_object_or_404(Note, id=pk)

    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, "Note Updated.")
            return redirect('record', pk=note.record.id)
    else:
        form = NoteForm(instance=note)

    return render(request, 'edit_note.html', {'form': form, 'note': note})


@login_required
def delete_note(request, pk):
    note = get_object_or_404(Note, id=pk)
    note.delete()
    messages.success(request, "Note Deleted.")
    return redirect('record', pk=note.record.id)


def toggle_pin_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    note.is_pinned = not note.is_pinned
    note.save()
    return redirect('record', pk=note.record.id)
