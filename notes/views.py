'''Import app object'''
from __init__ import *
'''Import flask objects'''
from flask import render_template, request, url_for, redirect


'''takes note object/instance and form object as parameter
then sends all data in the database,
not stage or commit, only prepares
returns true if its an empty note'''
def notes_into_db(single_note, form):
    single_note.set_title(form.title.data)
    single_note.set_preview(form)
    single_note.set_body(form)
    single_note.set_creation_date(form)
    single_note.set_modification_date()
    '''if title is not set when saving
    then takes first 100 char from preview
    from preview, vause tags are already removed'''
    if single_note.get_title() == '':
        title = single_note.get_preview()
        single_note.set_title(title[:100])
    '''if both title and body is empty, means empty note
    returns true so, empty note wont be saved.'''
    if (single_note.get_title() == '') and (single_note.get_body() == ''):
        return True


'''this function creates a new note'''
@app.route('/', methods=['GET', 'POST'])
def new_note():
    '''define a new form object/instance'''
    my_form = NotesForm()
    '''if new button is pressed refresh page'''
    if my_form.new.data:
        return redirect('/')
    '''if save button is pressed, create a Note() model/instance
    use notes_into_db to send all data into the database
    if both title and body is empty, then do nothing
    else, stage all changes in the database and
    finally write this new note in the database
    after writing into database, load this new note from database.'''
    if my_form.save.data:
        single_note = Note()
        empty = notes_into_db(single_note, my_form)
        if empty:
            return redirect('/')
        db.session.add(single_note)
        db.session.commit()
        return redirect(url_for('view_note', note_id=single_note.get_id()))
    '''if delete button is pressed, refresh page'''
    if my_form.delete.data:
        return redirect('/')
    '''when writing a new note, always set the creation date
    and modification date to current time
    btw creation date can be changed, but modification date can't be changed'''
    my_form.creation_date.raw_data = current_time()
    my_form.modification_date.raw_data = current_time()
    '''get all notes from database in a descending order'''
    notes = Note.query.order_by(Note.creation_date.desc()).all()
    '''normally render the new note page
    and pass the form object and all notes from database'''
    return render_template('new_note.html', my_form=my_form, notes=notes)

'''this function displays a note from database
when the address gets a note_id/primary key of a note
it displays that note.'''
@app.route('/<int:note_id>', methods=['GET', 'POST'])
def view_note(note_id):
    '''define a new form object'''
    my_form = NotesForm()
    '''loads/selects a row based on note_id
    if note_id is not available then automatically return 404 error'''
    single_note = Note.query.get_or_404(note_id)
    '''if new button is pressed, discard all changes, go to new note page'''
    if my_form.new.data:
        return redirect('/')
    '''if save button is pressed, save all modifications using notes_into_db function'''
    if my_form.save.data:
        empty = notes_into_db(single_note, my_form)
        if empty:
            return redirect('/')
        db.session.commit()
    '''if delete button is pressed, select this column
    delete the column, and commit this delete in database
    and return to create new note page'''
    if my_form.delete.data:
        db.session.delete(single_note)
        db.session.commit()
        return redirect('/')
    '''load note title, body, creation and modification date from database
    into the form object, so when rendering, this datas will be automatically loaded
    this could be also done from template
    but all logics only in the backend is more efficient'''
    my_form.title.data = single_note.get_title()
    my_form.note_body.data = single_note.get_body()
    my_form.creation_date.raw_data = single_note.get_creation_date()
    my_form.modification_date.raw_data = single_note.get_modification_date()
    '''get all notes from database in a descending order'''
    notes = Note.query.order_by(Note.creation_date.desc()).all()
    '''rendering note from database'''
    return render_template('view_note.html', my_form=my_form, notes=notes, single_note=single_note)
