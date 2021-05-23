from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog as fd
import tkcalendar
import vcard
from value_objects import AddressVO, PersonVO, CellNumberFieldVO, \
    CustomFieldVO, ContactGroupVO
from faker import Faker
from faker.providers import phone_number
import time
import contact_management
import threading
from datetime import datetime, timezone


class AddressWindow:
    """Fenster um Adresse zu erstellen oder zu bearbeiten."""

    def __init__(self, parent, address: AddressVO = None):
        """Definierung des Hauptfensters"""
        self.parent = parent  # Definiert das Elternfenster
        self.editing_mode = bool(address)  # Variable für den Editing Mode
        self.address = (address or AddressVO(label='Label', street='Straße', house_number='Nr.',
                                             zip_code='PLZ', town='Stadt', person=parent.person))  # definiert die Texte
        # der Felder im Adressfenster
        # populated die Felder
        self.label = StringVar(value=self.address.label)
        self.street = StringVar(value=self.address.street)
        self.house_number = StringVar(value=self.address.house_number)
        self.town = StringVar(value=self.address.town)
        self.zip_code = StringVar(value=self.address.zip_code)
        self.root = Toplevel(parent.root)
        self.root.resizable(width=False, height=False)
        self.header_frame = Frame(self.root, bg='lightgrey')
        # je nach bool editing mode wird die Option eine Adresse hinzuzufügen oder sie zu bearbeiten bereitgestellt
        if self.editing_mode:
            self.build_header(self.header_frame, title='Neue Adresse')
            self.root.title('Adresse hinzufügen')
        else:
            self.build_header(self.header_frame, title='Adresse Bearbeiten')
            self.root.title('Adresse bearbeiten')
        self.header_frame.pack(anchor=W, fill=X)
        self.form_frame = Frame(self.root)
        self.build_form(self.form_frame)
        self.form_frame.pack(anchor=W, padx=10, fill=X)
        self.center_window()
        self.root.mainloop()

    def build_header(self, frame, title):
        """Header des Adressfensters erstellen"""
        bg_color = frame['bg']
        title = Label(frame, text=title, bg=bg_color)
        title.grid(row=1, column=1, sticky=W)
        frame.columnconfigure(2, weight=1)
        if self.editing_mode:
            delete_button = Button(frame, text='Löschen', command=self.delete_pressed)
            delete_button.grid(row=1, column=3)
        cancel_button = Button(frame, text='Abbrechen', command=lambda: self.editing_finished())
        cancel_button.grid(row=1, column=5)
        submit_button = Button(frame, text='Sichern', command=lambda: self.editing_finished(True))
        submit_button.grid(row=1, column=7)
        # Constraints setzen
        frame.columnconfigure(4, minsize=10)
        frame.columnconfigure(6, minsize=10)
        frame.columnconfigure(8, minsize=10)
        frame.columnconfigure(0, minsize=10)
        frame.columnconfigure(8, minsize=10)
        frame.rowconfigure(0, minsize=3)
        frame.rowconfigure(2, minsize=3)

    def build_form(self, frame):
        """GUI-Elemente für Adressformular erstellen"""
        frame.columnconfigure(0, minsize=15)
        frame.columnconfigure(2, minsize=15)

        label_entry = Entry(frame, textvariable=self.label)
        label_entry.grid(row=1, column=1, columnspan=3, pady=3)

        street_entry = Entry(frame, textvariable=self.street)
        street_entry.grid(row=2, column=1, columnspan=3, pady=3)

        house_number_entry = Entry(frame, width=5, textvariable=self.house_number)
        house_number_entry.grid(row=2, column=5, sticky=E)

        zip_code_entry = Entry(frame, width=10, textvariable=self.zip_code)
        zip_code_entry.grid(row=3, column=1, sticky=W, pady=3)

        town_entry = Entry(frame, width=18, textvariable=self.town)
        town_entry.grid(row=3, column=3, columnspan=3, pady=3)

    def editing_finished(self, save_pressed=None):
        """Aktualisieren der Adressfelder, wenn save_pressed == True"""
        if save_pressed:
            self.address.label = self.label.get()
            self.address.street = self.street.get()
            self.address.house_number = self.house_number.get()
            self.address.town = self.town.get()
            self.address.zip_code = self.zip_code.get()
            if not self.editing_mode:
                self.parent.person.add(self.address)
            self.parent.update_address_entries()
        self.root.destroy()

    def delete_pressed(self):
        """Löschen der gegebenen Adresse aus der Person"""
        if type(self.address) == AddressVO:
            self.parent.person.remove(self.address)
            self.parent.update_address_entries()
        self.root.destroy()

    def center_window(self):
        """Fenster mittig zentrieren relativ zum root-Fenster"""
        window_x = int(self.parent.root.winfo_x() + self.parent.root.winfo_width() / 2 - 150)
        window_y = int(self.parent.root.winfo_y() + self.parent.root.winfo_height() / 2 - 50)
        self.root.geometry(f'+{window_x}+{window_y}')


class CellNumberFieldWindow:
    """Das Fenster zum Telefonnummer hinzufügen und bearbeiten"""

    def __init__(self, parent, cell_number_field: CellNumberFieldVO = None):
        """Definierung des Hauptfensters"""
        self.parent = parent
        self.editing_mode = bool(cell_number_field)
        self.cell_number_field = (
                cell_number_field or CellNumberFieldVO(label='Label', person=self.parent.person,
                                                       cell_number='Telefonnummer'))
        self.cell_number = StringVar(value=self.cell_number_field.cell_number)
        self.label = StringVar(value=self.cell_number_field.label)
        self.root = Toplevel(parent.root)
        self.root.resizable(width=False, height=False)
        self.header_frame = Frame(self.root, bg='lightgrey')
        if self.editing_mode:
            self.build_header(self.header_frame, title='Telefonnummer hinzufügen')
            self.root.title('Telefonnummer hinzufügen')
        else:
            self.build_header(self.header_frame, title='Telefonnummer bearbeiten')
            self.root.title('Telefonnummer bearbeiten')
        self.header_frame.pack(anchor=W, fill=X)
        self.form_frame = Frame(self.root)
        self.build_form(self.form_frame)
        self.form_frame.pack(anchor=W, padx=10, fill=X)
        self.center_window()
        self.root.mainloop()

    def build_header(self, frame, title):
        """Header des Telefonnummerfeld erstellen"""
        bg_color = frame['bg']
        title = Label(frame, text=title, bg=bg_color)
        title.grid(row=1, column=1, sticky=W)
        frame.columnconfigure(2, weight=1)
        if self.editing_mode:
            delete_button = Button(frame, text='Löschen', command=self.delete_pressed)
            delete_button.grid(row=1, column=3)
        cancel_button = Button(frame, text='Abbrechen', command=lambda: self.editing_finished())
        cancel_button.grid(row=1, column=5)
        submit_button = Button(frame, text='Sichern', command=lambda: self.editing_finished(True))
        submit_button.grid(row=1, column=7)
        frame.columnconfigure(4, minsize=10)
        frame.columnconfigure(6, minsize=10)
        frame.columnconfigure(8, minsize=10)
        frame.columnconfigure(0, minsize=10)
        frame.columnconfigure(8, minsize=10)
        frame.rowconfigure(0, minsize=3)
        frame.rowconfigure(2, minsize=3)

    def build_form(self, frame):
        """GUI-Elemente für Telefonnummerforumlar erstellen"""
        label_entry = Entry(frame, textvariable=self.label)
        label_entry.grid(row=0, column=1, pady=3)
        cell_entry = Entry(frame, textvariable=self.cell_number)
        cell_entry.grid(row=0, column=3, pady=3)
        frame.columnconfigure(2, minsize=15)

    def editing_finished(self, save_pressed=None):
        """Aktualisieren für Telefonnummerformular"""
        if save_pressed:
            self.cell_number_field.label = self.label.get()
            self.cell_number_field.cell_number = self.cell_number.get()
            if not self.editing_mode:
                self.parent.person.add(self.cell_number_field)
            self.parent.update_cell_number_field_entries()
        self.root.destroy()

    def delete_pressed(self):
        """Aktualisieren der Telefonnummerformular, wenn save_pressed == True"""
        if type(self.cell_number_field) == CellNumberFieldVO:
            self.parent.person.remove(self.cell_number_field)
            self.parent.update_cell_number_field_entries()
        self.root.destroy()

    def center_window(self):
        """Fenster mittig zentrieren relativ zum root-Fenster"""
        window_x = int(self.parent.root.winfo_x() + self.parent.root.winfo_width() / 2 - 210)
        window_y = int(self.parent.root.winfo_y() + self.parent.root.winfo_height() / 2 - 50)
        self.root.geometry(f'+{window_x}+{window_y}')


class CustomFieldWindow:
    """Das Fenster für Custom Fields"""

    def __init__(self, parent, custom_field: CustomFieldVO = None):
        """Definierung des Hauptfensters"""
        self.parent = parent
        self.editing_mode = bool(custom_field)
        self.custom_field = (
                custom_field or CustomFieldVO(label='Label', person=self.parent.person,
                                              field_value='Eigener Wert'))
        self.field_value = StringVar(value=self.custom_field.field_value)
        self.label = StringVar(value=self.custom_field.label)
        if custom_field is None:
            self.v_type = StringVar(value=None)
        else:
            self.v_type = StringVar(value=custom_field.v_type)
        self.custom_v_type = StringVar()
        self.root = Toplevel(parent.root)
        self.root.resizable(width=False, height=False)
        self.header_frame = Frame(self.root, bg='lightgrey')
        if self.editing_mode:
            self.build_header(self.header_frame, title='Eigenes Feld bearbeiten')
            self.root.title('Eigenes Feld bearbeiten')
        else:
            self.build_header(self.header_frame, title='Eigenes Feld hinzufügen')
            self.root.title('Eigenes Feld hinzufügen')
        self.header_frame.pack(anchor=W, fill=X)
        self.form_frame = Frame(self.root)
        self.build_form(self.form_frame)
        self.form_frame.pack(anchor=W, padx=10, fill=X)
        self.center_window()
        self.root.mainloop()

    def build_header(self, frame, title):
        """Header des Custom Field Window erstellen"""
        bg_color = frame['bg']
        title = Label(frame, text=title, bg=bg_color)
        title.grid(row=1, column=1, sticky=W)
        frame.columnconfigure(2, weight=1)
        if self.editing_mode:
            delete_button = Button(frame, text='Löschen', command=self.delete_pressed)
            delete_button.grid(row=1, column=3)
        cancel_button = Button(frame, text='Abbrechen', command=lambda: self.editing_finished())
        cancel_button.grid(row=1, column=5)
        submit_button = Button(frame, text='Sichern', command=lambda: self.editing_finished(True))
        submit_button.grid(row=1, column=7)
        frame.columnconfigure(4, minsize=10)
        frame.columnconfigure(6, minsize=10)
        frame.columnconfigure(8, minsize=10)
        frame.columnconfigure(0, minsize=10)
        frame.columnconfigure(8, minsize=10)
        frame.rowconfigure(0, minsize=3)
        frame.rowconfigure(2, minsize=3)

    def build_form(self, frame):
        """GUI-Elemente des CustomFieldWindow erstellen"""
        frame.columnconfigure(2, minsize=15)
        v_type_label = Label(frame, text='Typ: ')
        v_type_label.grid(row=1, column=1, sticky=W)
        v_type_entry = Entry(frame, textvariable=self.custom_v_type)
        v_type_options = ['Keiner', 'eMail', 'URL', 'Spitzname', 'Public Key', 'Geschlecht', 'Hobby', 'Titel', 'Firma']
        v_type_option_menu = OptionMenu(frame, self.v_type, [])
        self.setup_v_type_option_menu(v_type_option_menu, v_type_options, v_type_entry)
        v_type_option_menu.grid(row=1, column=2, sticky=W)
        v_type_entry.grid(row=1, column=4)
        label_entry = Entry(frame, textvariable=self.label)
        label_entry.grid(row=3, column=1, columnspan=2, pady=3)
        field_value_entry = Entry(frame, textvariable=self.field_value)
        field_value_entry.grid(row=3, column=4, pady=3)
        frame.columnconfigure(1, minsize=1)

    def setup_v_type_option_menu(self, option_menu, options, entry):
        """Das Optionsmenü wird definiert"""
        option_menu['menu'].delete(0, 'end')
        for v_type in options:
            if ((v_type == 'Titel'
                 and 'Titel' in [custom_field.v_type for custom_field in self.parent.person.custom_fields if
                                 custom_field.v_type == 'Titel']
                 and self.custom_field.v_type != 'Titel')
                    or (v_type == 'Geschlecht'
                        and 'Geschlecht' in [custom_field.v_type for custom_field in self.parent.person.custom_fields if
                                             custom_field.v_type == 'Geschlecht']
                        and self.custom_field.v_type != 'Geschlecht')):
                pass
            else:
                option_menu['menu'].add_command(label=v_type, command=lambda entry=entry,
                                                                             title=v_type: self.set_command_for_v_type_option(
                    entry, title))
        option_menu['menu'].add_command(label='Eigener Typ', command=lambda entry=entry,
                                                                            title='Eigener Typ': self.set_command_for_v_type_option(
            entry, title))
        if self.custom_field.v_type is None:
            self.set_command_for_v_type_option(entry, 'Keiner')
        elif self.custom_field.v_type in options:
            self.set_command_for_v_type_option(entry, self.custom_field.v_type)
        else:
            self.set_command_for_v_type_option(entry, 'Eigener Typ')
            self.custom_v_type.set(self.custom_field.v_type)

    def set_command_for_v_type_option(self, entry, title):
        """Definiert die commands für das Options Menu"""
        self.v_type.set(title)
        if title == 'Eigener Typ':
            entry.configure(state='normal')
        else:
            entry.delete(0, 'end')
            self.custom_v_type.set('')
            entry.configure(state='disabled')
            if title == 'Geschlecht':
                if self.custom_field.v_type is None:
                    self.field_value.set('weiblich / maennlich / divers')
                    self.label.set('Geschlecht')
            elif title == 'Hobby':
                if self.custom_field.v_type is None:
                    self.label.set('Hobby')

            elif title == 'Titel':
                if self.custom_field.v_type is None:
                    self.label.set('Titel')

            elif title == 'Firma':
                if self.custom_field.v_type is None:
                    self.label.set('Firma')

    def editing_finished(self, save_pressed=None):
        """Aktualisiert Optionen falls save_pressed=True"""
        if save_pressed:
            self.custom_field.label = self.label.get()
            self.custom_field.field_value = self.field_value.get()
            if self.v_type.get() == 'Keiner':
                self.custom_field.v_type = None
            elif self.v_type.get() == 'Eigener Typ':
                self.custom_field.v_type = self.custom_v_type.get()
            else:
                self.custom_field.v_type = self.v_type.get()
            if not self.editing_mode:
                self.parent.person.add(self.custom_field)
            self.parent.update_custom_field_entries()
        self.root.destroy()

    def delete_pressed(self):
        """Löschen des gegebenen Custom Field"""
        if type(self.custom_field) == CustomFieldVO:
            self.parent.person.remove(self.custom_field)
            self.parent.update_custom_field_entries()
        self.root.destroy()

    def center_window(self):
        """Fenster mittig zentrieren relativ zum root-Fenster"""
        window_x = int(self.parent.root.winfo_x() + self.parent.root.winfo_width() / 2 - 200)
        window_y = int(self.parent.root.winfo_y() + self.parent.root.winfo_height() / 2 - 50)
        self.root.geometry(f'+{window_x}+{window_y}')


class ContactListWindow:
    """Das Fenster für Kontaktlisten"""

    #
    def __init__(self):
        """Hauptfenster erstellen und nötige Funktionen aufrufen"""
        self.root = Tk()
        self.contact_groups = []
        self.contact_group_titles = []
        self.selected_contact_group = None
        self.selected_contact_group_title = StringVar()
        self.root.title('Kontaktbuch')
        self.contact_group_options_have_been_setup = False

        self.header_frame = Frame(self.root, bg='lightgrey')
        self.build_header(self.header_frame)
        self.header_frame.pack(fill=X)

        self.person_table_frame = Frame(self.root)
        self.build_table(self.person_table_frame)

        self.footer_frame = Frame(self.root, bg='lightgrey')
        self.build_footer(self.footer_frame)
        self.footer_frame.pack(side=BOTTOM, fill=X)
        self.footer_frame.pack(anchor=W, padx=2, pady=2, fill=X)

        self.selected_contact_group_title.trace('w', lambda *args: self.update_person_table())
        self.person_table_frame.pack(fill=BOTH, expand=True)
        self.center_window()
        self.root.mainloop()

    def build_header(self, frame):
        """Header erstellen"""
        contact_groups_option_menu = OptionMenu(frame, self.selected_contact_group_title,
                                                [])  # Dropdown-Menu für Gruppenauswahl
        contact_groups_option_menu.grid(row=1, column=1)
        delete_contact_group_button = Button(frame, text='Gruppe bearbeiten',
                                             command=lambda *args: ContactGroupWindow(self,
                                                                                      contact_group=self.selected_contact_group))
        delete_contact_group_button.grid(row=1, column=3)
        new_contact_button = Button(frame, text='Neuer Kontakt', command=lambda *args: PersonWindow(self))
        new_contact_button.grid(row=1, column=5)
        frame.columnconfigure(2, weight=1, minsize=15)
        frame.columnconfigure(4, minsize=15)
        frame.columnconfigure(3, minsize=len('Gruppe bearbeiten'))
        self.update_contact_group_option_menu()  # setzen der Gruppen-Optionen im Dropdown-Menu
        frame.columnconfigure(0, minsize=5)
        frame.columnconfigure(6, minsize=5)
        frame.rowconfigure(0, minsize=3)
        frame.rowconfigure(2, minsize=3)

    def build_table(self, frame):
        person_table = ttk.Treeview(frame, height=25, show='tree')
        person_table.bind('<Double-1>', lambda event: self.on_doubleclick())
        person_table.pack(fill=BOTH, expand=True)
        self.update_person_table()

    def build_footer(self, frame):

        import_button = Button(frame, text='VCF Importieren',
                               command=lambda: threading.Thread(target=self.import_button_pressed).start())
        import_button.grid(row=1, column=1, sticky=E)

        export_button = Button(frame, text='Kontakte Exportieren',
                               command=lambda: threading.Thread(target=self.export_button_pressed).start())
        export_button.grid(row=1, column=3, sticky=E)
        frame.columnconfigure(0, weight=1, minsize=15)
        frame.columnconfigure(2, minsize=5)
        frame.rowconfigure(0, minsize=3)
        frame.rowconfigure(2, minsize=3)
        frame.columnconfigure(4, minsize=5)

    def export_button_pressed(self):
        vcard.export_persons(fd.askdirectory(), self.selected_contact_group)

    def import_button_pressed(self):
        vcard.import_persons(fd.askopenfile(filetypes=[('VCF Files', '*.vcf')]))
        self.update()

    def update(self):
        self.update_contact_group_option_menu()
        self.update_person_table()

    def update_contact_group_option_menu(self):
        """Aktualisieren der Gruppen-Optionen im Dropdown-Menu"""
        # generische Gruppe mit allen Kontakten erstellen, lexikalisch sortiert nach Nachname + Vorname
        all_contacts_group = ContactGroupVO(title='Alle Kontakte',
                                            persons=sorted(contact_management.get_all_persons(),
                                                           key=lambda person: (
                                                                   person.last_name + person.first_name).replace(
                                                               ' ', ''), reverse=False))
        # generische Gruppe mit Kontakten der letzten 14 Tage erstellen, absteigend sortiert nach Änderungsdatum
        latest_contact_group = ContactGroupVO(title='Letzte 14 Tage',
                                              persons=[person for person in sorted(contact_management.get_all_persons(),
                                                                                   key=lambda
                                                                                       person: person.modification_date,
                                                                                   reverse=True) if
                                                       time.time() - person.modification_date < 86400 * 14])
        self.selected_contact_group = all_contacts_group  # standardmäßig ausgewählte Gruppe auf generisch erzeugte Gruppe "Alle Kontakte" setzen
        # Liste der auswählbaren Gruppen = Liste aller Gruppen in der Datenbank + alle generischen Gruppen
        self.contact_groups = [all_contacts_group, latest_contact_group] + contact_management.get_all_contact_groups()
        self.contact_group_titles = [contact_group.title for contact_group in self.contact_groups]
        self.selected_contact_group_title.set(
            self.contact_group_titles[0])  # Titel im Dropdown-Menu auf "Alle Kontakte" setzen

        # Breite des Dropdown-Menus auf die Zeichenlänge des längsten Gruppentitels setzen
        max_option_length = max((len(max(self.contact_group_titles, key=len)), len('Neue Gruppe erstellen')))
        # für jedes aktualisieren des Dropdown-Menus ein neues erstellen und das alte später verwerfen
        option_menu_widget = OptionMenu(self.header_frame, self.selected_contact_group_title,
                                        *self.contact_group_titles)
        self.header_frame.winfo_children()[0] = option_menu_widget  # neues Optionmenu setzen
        option_menu_widget.grid(row=1, column=1)
        menu: Menu = option_menu_widget["menu"]
        menu.delete(0, 'end')  # alle Optionen löschen, um sie gleich neu aufzubauen (mit Kommandos)
        option_count = 0
        for contact_group in self.contact_groups:
            if option_count == 2:
                menu.add_separator()  # nach den generischen Gruppen einen Separator einfügen
            # Für jeden Eintrag im Dropdown-Menu die entsprechende Aktion setzen und diesen Eintrag dann ins Dropdown-Menu einfügen
            menu.add_command(label=contact_group.title,
                             command=lambda value=contact_group: self.set_command_for_contact_group_option_menu_entry(
                                 value))
            option_count += 1
        menu.add_separator()  # Separator vor "Neue Gruppe erstellen" einfügen
        # Eintrag, der ein ContactGroupWindow aufruft, um eine neue Gruppe erstellen zu können
        menu.add_command(label='Neue Gruppe erstellen',
                         command=lambda parent=self: ContactGroupWindow(parent=parent))
        option_menu_widget.config(width=max_option_length)
        # Nach jedem Aufruf der Funtkion wird die Gruppe "Alle Kontakte" gesetzt.
        # Diese Gruppe existiert aber nicht wirklich in der Datenbank und kann daher nicht gelöscht werden
        self.change_contact_group_delete_button_visibility(False)

    def set_command_for_contact_group_option_menu_entry(self, contact_group):
        """Aktion für einen Eintrag im Dropdown-Menu bei dessen Auswahl."""
        self.selected_contact_group = contact_group  # Variable für die ausgewählte ContactGroup setzen
        self.selected_contact_group_title.set(contact_group.title)  # ausgewählte Option im Dropdown-Menu ändern

        if self.selected_contact_group_title.get() == self.contact_group_titles[
            0] or self.selected_contact_group_title.get() == self.contact_group_titles[1]:
            self.change_contact_group_delete_button_visibility(
                False)  # bei generischen Gruppen den delete-Button ausblenden
        else:
            self.change_contact_group_delete_button_visibility(True)

    def change_contact_group_delete_button_visibility(self, visible):
        """Sichtbarkeit des delete-Buttons bei Auswahl einer Gruppe aus dem Dropdown-Menu ändern."""
        delete_button = self.header_frame.winfo_children()[1]
        if not visible:
            delete_button.grid_forget()  # delete-Button ausblenden, wenn Sicherbarkeit auf False
            self.header_frame.columnconfigure(3, minsize=110)
        else:
            delete_button.grid(row=1, column=3)  # ansonsten delete-Button erneut einblenden

    def update_person_table(self):
        person_table = self.person_table_frame.winfo_children()[0]  # Tabelle aus dem Fenster erhalten
        for person in person_table.get_children(''):
            person_table.delete(person)  # Einträge löschen, um Tabelle später mit neuen Einträgen zu füllen

        for person in self.selected_contact_group.persons:
            # Ein Tabelleneintrag besteht aus Vorname + Nachname.
            # Position in der Tabelle ist die Postion der Person im Array der Personen der Gruppe.
            # Die ID des Tabelleneintrags ist die ID der person.
            person_table.insert('', self.selected_contact_group.persons.index(person),
                                text=f'{person.first_name} {person.last_name}',
                                iid=person.person_id, tags=(person.person_id,))

    def on_doubleclick(self):
        person_table = self.person_table_frame.winfo_children()[0]
        selected_persons = person_table.selection()
        for person_id in selected_persons:
            # Tabelleinträge haben in der iid die person_ids gespeichert
            person_id = int(person_id)
            person = contact_management.get_person_by_id(person_id)  # Person erhalten anhand der ID
            # Bei Doppelklick ein neues PersonWindow erstellen und die Person übergeben.
            PersonWindow(parent=self, person=person, editing_mode=True)

    def center_window(self):
        """Fenster auf dem Bildschirm mittig zentrieren anhand der Standardgröße"""
        window_x = int(self.root.winfo_screenwidth() / 2 - 230)
        window_y = int(self.root.winfo_screenheight() / 2 - 300)
        self.root.geometry(f'+{window_x}+{window_y}')


class ContactGroupWindow:
    """Das Gruppenfenster"""

    def __init__(self, parent, contact_group: ContactGroupVO = None):
        """Definierung des Hauptfensters"""
        self.parent = parent
        self.contact_group = (contact_group or ContactGroupVO(persons=[], title='Titel'))
        self.title = StringVar(value=self.contact_group.title)
        self.root = Toplevel(parent.root)
        self.root.resizable(width=False, height=False)
        self.header_frame = Frame(self.root, bg='lightgrey')
        if contact_group:
            self.build_header(self.header_frame, title='Gruppe bearbeiten')
            self.root.title('Gruppe bearbeiten')
        else:
            self.build_header(self.header_frame, title='Gruppe erstellen')
            self.root.title('Gruppe erstellen')
        self.header_frame.pack(anchor=W, fill=X)

        self.form_frame = Frame(self.root)
        self.build_form(self.form_frame)
        self.form_frame.pack(anchor=W, padx=10, fill=X)
        self.root.attributes('-topmost', True)
        self.center_window()
        self.root.mainloop()

    def build_header(self, frame, title):
        """Header Erstellen"""
        bg_color = frame['bg']
        title = Label(frame, text=title, bg=bg_color)
        title.grid(row=1, column=1, sticky=W)
        if self.contact_group.group_id:
            delete_button = Button(frame, text='Löschen', command=self.delete_contact_group_button_pressed)
            delete_button.grid(row=1, column=3)
        cancel_button = Button(frame, text='Abbrechen', command=self.editing_finished)
        cancel_button.grid(row=1, column=5)
        submit_button = Button(frame, text='Sichern', command=lambda: self.editing_finished(self.contact_group))
        submit_button.grid(row=1, column=7)
        frame.columnconfigure(0, minsize=10)
        frame.columnconfigure(2, weight=1)
        frame.columnconfigure(4, minsize=10)
        frame.columnconfigure(6, minsize=10)
        frame.columnconfigure(8, minsize=10)
        frame.rowconfigure(0, minsize=3)
        frame.rowconfigure(2, minsize=3)

    def build_form(self, frame):
        """Formular Erstellen"""
        title_entry = Entry(frame, textvariable=self.title)
        title_entry.grid(row=0, column=3, pady=3)
        frame.columnconfigure(2, minsize=15)

    def editing_finished(self, contact_group=None):
        """Aktualisieren wenn fertig mit bearbeiten"""
        if contact_group:
            self.contact_group.title = self.title.get()
            contact_management.save(self.contact_group)
            self.parent.update_contact_group_option_menu()
        self.root.destroy()

    def delete_contact_group_button_pressed(self):
        """Gruppe Löschen"""
        if messagebox.askokcancel(title='Gruppe wirklich löschen?',
                                  message='''Sie sind im Begriff die Gruppe zu löschen.\nMöchten Sie fortfahren?\nDie damit verknüpften Kontakte bleiben erhalten.'''):
            contact_management.delete(self.parent.selected_contact_group)
            self.parent.update_contact_group_option_menu()
            self.root.destroy()

    def center_window(self):
        """Fenster mittig zentrieren relativ zum root-Fenster"""
        window_x = int(self.parent.root.winfo_x() + self.parent.root.winfo_width() / 2 - 150)
        window_y = int(self.parent.root.winfo_y() + self.parent.root.winfo_height() / 2 - 50)
        self.root.geometry(f'+{window_x}+{window_y}')


class ContactGroupSelectionWindow:
    """Das Fenster das auf ausgewählte Gruppen reagiert"""

    def __init__(self, parent, contact_group: ContactGroupVO = None):
        self.parent = parent
        self.root = Toplevel(parent.root)
        self.orig_contact_group = contact_group
        self.selected_contact_group = (contact_group or None)
        self.selectable_contact_groups = self.calculate_contact_group_options()
        self.contact_group_titles = ['Keine'] + list(
            map(lambda contact_group: contact_group.title, self.selectable_contact_groups))
        self.selected_contact_group_title = StringVar()
        self.header_frame = Frame(self.root, bg='lightgrey')
        self.build_header(self.header_frame, title='Gruppe auswählen')
        self.form_frame = Frame(self.root)
        self.build_form(self.form_frame)
        self.header_frame.pack()
        self.form_frame.pack()
        self.center_window()
        self.root.mainloop()

    def build_header(self, frame, title):
        """Header für Gruppenselektionsfenster erstellen"""
        bg_color = frame['bg']
        title = Label(frame, text=title, bg=bg_color)
        title.grid(row=1, column=1, sticky=W)
        frame.columnconfigure(2, weight=1)
        remove_button = Button(frame, text='Entfernen', command=self.remove_pressed)
        remove_button.grid(row=1, column=3)
        if not self.selected_contact_group:
            self.change_remove_button_visibility(False)
        cancel_button = Button(frame, text='Abbrechen', command=lambda: self.editing_finished())
        cancel_button.grid(row=1, column=5)
        submit_button = Button(frame, text='Sichern', command=lambda: self.editing_finished(True))
        submit_button.grid(row=1, column=7)
        frame.columnconfigure(4, minsize=10)
        frame.columnconfigure(6, minsize=10)
        frame.columnconfigure(0, minsize=10)
        frame.columnconfigure(8, minsize=10)
        frame.rowconfigure(0, minsize=3)
        frame.rowconfigure(2, minsize=3)

    def build_form(self, frame):
        """GUI Elemente für Addressformular erstel"""
        contact_groups_option_menu = OptionMenu(frame, self.selected_contact_group_title, [])
        contact_groups_option_menu.pack(anchor=CENTER)
        self.update_option_menu()

    def calculate_contact_group_options(self):
        """Gibt mögliche Kontaktgruppen zurück"""
        all_contact_groups = contact_management.get_all_contact_groups()
        persons_contact_group_ids = list(map(lambda contact_group: contact_group.group_id, self.parent.person.groups))
        selectable_contact_group_options = list(
            filter(lambda contact_group: contact_group.group_id not in persons_contact_group_ids, all_contact_groups))
        if self.selected_contact_group:
            selectable_contact_group_options.append(self.selected_contact_group)
        return selectable_contact_group_options

    def change_remove_button_visibility(self, visible):
        """Verändert die sichtbarkeit des Entfernen Button"""
        remove_button = self.header_frame.winfo_children()[1]
        if not visible:
            remove_button.grid_forget()
            self.header_frame.columnconfigure(3, minsize=len('Entfernen'))
        else:
            remove_button.grid(row=1, column=3)

    def choose_contact_group_option(self, contact_group):
        """Lässt Benutzer eine Kontaktgruppe wählen"""
        if not contact_group:
            self.selected_contact_group_title.set('Keine')
        else:
            self.selected_contact_group_title.set(contact_group.title)
        self.selected_contact_group = contact_group
        self.change_remove_button_visibility(bool(contact_group))

    def update_option_menu(self):
        """Aktualisiert das Optionsmenü"""
        contact_groups_option_menu = self.form_frame.winfo_children()[0]
        menu = contact_groups_option_menu['menu']
        menu.delete(0, 'end')
        menu.add_command(label=self.contact_group_titles[0],
                         command=lambda: self.choose_contact_group_option(contact_group=None))
        for contact_group in self.selectable_contact_groups:
            menu.add_command(label=contact_group.title,
                             command=lambda value=contact_group: self.choose_contact_group_option(value))
        self.choose_contact_group_option(contact_group=self.selected_contact_group)

    def editing_finished(self, save_pressed=False):
        """Aktualisiert wenn save_pressed=True"""
        if save_pressed:
            if type(self.selected_contact_group) == ContactGroupVO:
                if self.orig_contact_group:
                    self.parent.person.remove(self.orig_contact_group)
                self.parent.person.add(self.selected_contact_group)
                self.parent.update_contact_group_entries()
            elif self.selected_contact_group is None:
                self.parent.person.remove(self.orig_contact_group)
                self.parent.update_contact_group_entries()
        self.root.destroy()

    def remove_pressed(self):
        if type(self.selected_contact_group) == ContactGroupVO:
            self.parent.person.remove(self.selected_contact_group)
            self.parent.update_contact_group_entries()
        self.root.destroy()

    def center_window(self):
        """Fenster mittig zentrieren relativ zum root-Fenster"""
        window_x = int(self.parent.root.winfo_x() + self.parent.root.winfo_width() / 2 - 150)
        window_y = int(self.parent.root.winfo_y() + self.parent.root.winfo_height() / 2 - 50)
        self.root.geometry(f'+{window_x}+{window_y}')


class PersonWindow:
    """Das Fenster das einen Überblick über Personen gibt"""

    def __init__(self, parent, person: PersonVO = None,
                 editing_mode=False):
        self.person = (person or PersonVO(last_name='Nachname', first_name='Vorname',
                                          birthdate=None,
                                          modification_date=int(datetime.now(timezone.utc).timestamp())))
        self.last_name = StringVar(value=self.person.last_name)
        self.first_name = StringVar(value=self.person.first_name)
        self.birthdate_entry = None
        self.parent = parent
        self.root = Toplevel(parent.root)
        self.root.resizable(width=False, height=False)
        self.header_frame = Frame(self.root, bg='lightgrey')
        if editing_mode:
            self.build_header(self.header_frame, 'Kontakt bearbeiten', editing_mode)
            self.root.title('Kontakt bearbeiten')
        else:
            self.build_header(self.header_frame, 'Kontakt hinzufügen', editing_mode)
            self.root.title('Kontakt hinzufügen')
        self.header_frame.pack(anchor=W, fill=X)
        self.main_rows = []
        self.form_frame = Frame(self.root)
        self.build_form(self.form_frame)
        self.form_frame.pack(anchor=W, padx=10, fill=X, pady=5)
        self.center_window()
        self.root.mainloop()

    def build_header(self, frame, title, editing_mode):
        bg_color = frame['bg']
        title = Label(frame, text=title, bg=bg_color)
        title.grid(row=1, column=1, sticky=W)
        frame.columnconfigure(2, weight=1)
        if editing_mode:
            delete_person_button = Button(frame, text='Kontakt löschen', command=self.delete_person_button_pressed)
            delete_person_button.grid(row=1, column=3)
        cancel_button = Button(frame, text='Abbrechen', command=lambda: self.editing_finished())
        cancel_button.grid(row=1, column=5)
        submit_button = Button(frame, text='Sichern', command=lambda: self.editing_finished(True))
        submit_button.grid(row=1, column=7)
        # Abstände zwischen den GUI-Elementen setzen
        frame.columnconfigure(4, minsize=10)
        frame.columnconfigure(6, minsize=10)
        frame.columnconfigure(3, minsize=len('Kontakt löschen'))
        frame.columnconfigure(0, minsize=10)
        frame.columnconfigure(8, minsize=10)
        frame.rowconfigure(0, minsize=3)
        frame.rowconfigure(2, minsize=3)

    def build_form(self, frame):
        frame.columnconfigure(2, minsize=15)
        first_name_entry = Entry(frame, textvariable=self.first_name)
        first_name_entry.grid(row=0, column=1, pady=3)
        last_name_entry = Entry(frame, textvariable=self.last_name)
        last_name_entry.grid(row=0, column=3, pady=3)
        # Tabellen zur Darstellung der mit der Person verbundenen Adressen, Gruppen, ... erstellen
        self.build_cell_number_fields_table(frame)
        self.build_addresses_table(frame)
        self.build_birthdate_field(frame)
        self.build_contact_groups_table(frame)
        self.build_custom_fields_table(frame)

    def build_cell_number_fields_table(self, frame):
        cell_number_fields_table = ttk.Treeview(frame, height=len(self.person.cell_number_fields))
        cell_number_fields_table.grid(row=3, column=0, columnspan=4, sticky=E + W)
        cell_number_fields_table.heading('#0', text='Telefonnummer hinzufügen')
        cell_number_fields_table.bind('<Double-1>',
                                      self.on_doubleclick_cell_number_field_table)  # Reagieren auf Doppelklick auf Eitnrag
        cell_number_fields_table.bind('<Button-1>',
                                      self.on_click_cell_number_field_table)  # Reagieren auf Einfachklick auf den Tabellen-Header
        self.update_cell_number_field_entries()

    def build_addresses_table(self, frame):
        addresses_table = ttk.Treeview(frame, height=len(self.person.addresses))
        addresses_table.grid(row=4, column=0, columnspan=4, sticky=E + W)
        addresses_table.heading('#0', text='Adresse hinzufügen')
        addresses_table.bind('<Double-1>', self.on_doubleclick_addresses_table)  # Reagieren auf Doppelklick auf Eitnrag
        addresses_table.bind('<Button-1>',
                             self.on_click_addresses_table)  # Reagieren auf Einfachklick auf den Tabellen-Header
        self.update_address_entries()

    def build_birthdate_field(self, frame):
        """Geburtsdatums-Feld konfigurieren"""
        # DateEntry zum Darstellen des Datums mit Kalenderoption
        birthdate_entry = tkcalendar.DateEntry(frame, date_pattern='dd.mm.yyyy', locale='de_DE', width=12,
                                               foreground='white', borderwidth=2, maxdate=datetime.utcnow().date())
        birthdate_entry.grid(row=5, column=1)
        self.birthdate_entry = birthdate_entry
        birthdate_entry._top_cal.overrideredirect(False)
        birthdate_entry.bind('<Return>', lambda
            *args: self.root.focus_set())  # bei Enter den Fokus wieder auf das PersonWindow setzen
        # Bei Veränderung des Statuses des DateEntries entscheiden, ob der clear-Button zugänglich sein soll oder nicht
        birthdate_entry.bind('<FocusIn>', lambda *args: self.dateentry_edited(birthdate_entry))
        birthdate_entry.bind('<FocusOut>', lambda *args: self.dateentry_edited(birthdate_entry))
        clear_button = Button(frame, text='Geburtsdatum löschen',
                              command=lambda *args: self.clear_birthdate_entry(clear_button))
        clear_button.grid(row=5, column=3)
        if self.person.birthdate or self.person.birthdate == 0:
            birthdate_entry.set_date(datetime.fromtimestamp(
                self.person.birthdate).date())  # Geburtsdatum der Person setzen, wenn das Attribut einen Wert enthält
            clear_button.configure(state='normal')  # clear-Button infolge dessen auch verfügbar machen
        else:
            birthdate_entry.delete(0, 'end')  # ansonsten DateEntry leeren (sonst mit Standardwert befüllt)
            clear_button.configure(state='disabled')  # clear-Button infolge dessen deaktivieren

    def dateentry_edited(self, dateentry: tkcalendar.DateEntry):
        if not dateentry.get():
            clear_button = self.form_frame.winfo_children()[5]
            clear_button.configure(state='disabled')  # wenn dateentry leer ist, clear-Button deaktivieren
        else:
            clear_button = self.form_frame.winfo_children()[5]
            clear_button.configure(state='normal')  # ansonsten clear-Button verfügbar machen

    def clear_birthdate_entry(self, button):
        birthdate_entry = self.form_frame.winfo_children()[4]
        birthdate_entry.delete(0, 'end')  # dateentry leeren
        button.configure(state='disabled')  # clear-Button deaktivieren
        self.root.focus_set()

    def build_contact_groups_table(self, frame):
        contact_groups_table = ttk.Treeview(frame, height=len(self.person.groups))
        contact_groups_table.grid(row=6, column=0, columnspan=4, sticky=E + W)
        contact_groups_table.heading('#0', text='Gruppe hinzufügen')
        contact_groups_table.bind('<Double-1>',
                                  self.on_doubleclick_contact_groups_table)  # Reagieren auf Doppelklick auf Eitnrag
        contact_groups_table.bind('<Button-1>',
                                  self.on_click_contact_groups_table)  # Reagieren auf Einfachklick auf den Tabellen-Header
        self.update_contact_group_entries()

    def build_custom_fields_table(self, frame):
        custom_fields_table = ttk.Treeview(frame, height=len(self.person.custom_fields))
        custom_fields_table.grid(row=7, column=0, columnspan=4, sticky=E + W)
        custom_fields_table.heading('#0', text='Eigenes Feld hinzufügen')
        custom_fields_table.bind('<Double-1>',
                                 self.on_doubleclick_custom_field_table)  # Reagieren auf Doppelklick auf Eitnrag
        custom_fields_table.bind('<Button-1>',
                                 self.on_click_custom_field_table)  # Reagieren auf Einfachklick auf den Tabellen-Header
        self.update_custom_field_entries()

    def update_address_entries(self):
        address_table = self.form_frame.winfo_children()[3]
        for address in address_table.get_children(''):
            address_table.delete(
                address)  # alle Adress-Einträge entfernen, um Tabelle mit neuen Adressen befüllen zu können

        address_index = 0
        for address in self.person.addresses:
            # Tabelleneintrag darstellen mit Label, Straße, Hausnr, ...
            address_text = f'{address.label}\t{address.street} {address.house_number}, {address.zip_code} {address.town}'
            # Tabelleneintrag einfügen. Position ist die im Array der Person.
            address_table.insert('', address_index, text=address_text,
                                 iid=address_index)
            address_index += 1
        address_table['height'] = len(self.person.addresses)

    def on_doubleclick_addresses_table(self, event):
        addresses_table = self.form_frame.winfo_children()[3]
        region = addresses_table.identify('region', event.x, event.y)
        # auf Doppelklick nur reagieren, wenn er sich auf die Tabelleneinträge bezieht
        if region == 'tree':
            for address_index in addresses_table.selection():
                address_index = int(address_index)
                address = self.person.addresses[
                    address_index]  # Adresse aus der Person holen (Index in der Tabelle = Index im Adress-Array der Person)
                AddressWindow(parent=self,
                              address=address)  # AddressWindow öffnen, um die Adresse bearbeiten zu können => Adresse mitgeben
                addresses_table.selection_remove(address_index)  # Se Slktion wieder aufheben

    def on_click_addresses_table(self, event):
        addresses_table = self.form_frame.winfo_children()[3]
        region = addresses_table.identify('region', event.x, event.y)
        # auf Einfachklick nur reagieren, wenn er sich auf den Tabellenkopf bezieht
        if region == 'heading':
            AddressWindow(parent=self)  # ... dann ein neues AdressWindow erstellen um eine neue Adresse zu erstellen

    def update_cell_number_field_entries(self):
        cell_number_fields_table = self.form_frame.winfo_children()[2]
        for cell_number_field in cell_number_fields_table.get_children(''):
            cell_number_fields_table.delete(
                cell_number_field)  # alle Telefonnummern entfernen, um Tabelle mit neuen Telefonnummern befüllen zu können

        cell_number_field_index = 0
        for cell_number_field in self.person.cell_number_fields:
            # Tabelleneintrag darstellen mit Label und Telefonnummer
            cell_number_text = f'{cell_number_field.label}\t{cell_number_field.cell_number}'
            # Tabelleneintrag einfügen. Position ist die im Array der Person.
            cell_number_fields_table.insert('', cell_number_field_index,
                                            text=cell_number_text,
                                            iid=cell_number_field_index)
            cell_number_field_index += 1
        cell_number_fields_table['height'] = len(self.person.cell_number_fields)

    def on_click_cell_number_field_table(self, event):
        cell_number_fields_table = self.form_frame.winfo_children()[2]
        region = cell_number_fields_table.identify('region', event.x, event.y)
        if region == 'heading':
            # auf Einfachklick nur reagieren, wenn er sich auf den Tabellenkopf bezieht
            CellNumberFieldWindow(
                parent=self)  # ... dann ein neues CellNumberWindow erstellen um eine neue Telefonnummer zu erstellen

    def on_doubleclick_cell_number_field_table(self, event):
        cell_number_fields_table = self.form_frame.winfo_children()[2]
        region = cell_number_fields_table.identify('region', event.x, event.y)
        if region == 'tree':
            # auf Doppelklick nur reagieren, wenn er sich auf die Tabelleneinträge bezieht
            for cell_number_field_index in cell_number_fields_table.selection():
                cell_number_field_index = int(
                    cell_number_field_index)  # ID des CellNumberFields holen (auslesen aus dem Tabelleneintrag)
                cell_number_field = self.person.cell_number_fields[
                    cell_number_field_index]  # Telefonnummern-Feld aus der Person holen (Index in der Tabelle = Index im CellNumberField-Array der Person)
                CellNumberFieldWindow(parent=self,
                                      cell_number_field=cell_number_field)  # CellNumberFieldWindow öffnen, um die Telefonnummer bearbeiten zu können => CellNumberField mitgeben
                cell_number_fields_table.selection_remove(cell_number_field_index)  # Selektion wieder aufheben

    def update_contact_group_entries(self):
        contact_groups_table = self.form_frame.winfo_children()[6]
        for contact_group in contact_groups_table.get_children(''):
            contact_groups_table.delete(
                contact_group)  # alle Gruppen entfernen, um Tabelle mit neuen Gruppen befüllen zu können

        contact_group_index = 0
        for contact_group in self.person.groups:
            # Tabelleneintrag einfügen. Position ist die im Array der Person.
            contact_groups_table.insert('', contact_group_index,
                                        text=contact_group.title,
                                        iid=contact_group_index)
            contact_group_index += 1
        contact_groups_table['height'] = len(self.person.groups)

    def on_doubleclick_contact_groups_table(self, event):
        contact_groups_table = self.form_frame.winfo_children()[6]
        region = contact_groups_table.identify('region', event.x, event.y)
        # auf Doppelklick nur reagieren, wenn er sich auf die Tabelleneinträge bezieht
        if region == 'tree':
            for contact_group_index in contact_groups_table.selection():
                contact_group_index = int(contact_group_index)  # ID der Gruppe holen (auslesen aus der Tabelleneintrag)
                contact_group = self.person.groups[
                    contact_group_index]  # Gruppen-Feld aus der Person holen (Index in der Tabelle = Index im groups-Array der Person)
                ContactGroupSelectionWindow(parent=self,
                                            contact_group=contact_group)  # ContactGroupSelectionWindow öffnen, um die Gruppe auswählen zu können => ContactGroupVO mitgeben
                contact_groups_table.selection_remove(contact_group_index)  # Selektion wieder aufheben

    def on_click_contact_groups_table(self, event):
        contact_groups_table = self.form_frame.winfo_children()[6]
        region = contact_groups_table.identify('region', event.x, event.y)
        if region == 'heading':
            # auf Einfachklick nur reagieren, wenn er sich auf den Tabellenkopf bezieht
            ContactGroupSelectionWindow(
                parent=self)  # ... dann ein neues ContactGroupSelectionWindow erstellen um eine neue Gruppe auszuwählen

    def update_custom_field_entries(self):
        custom_fields_table = self.form_frame.winfo_children()[7]
        for custom_field in custom_fields_table.get_children(''):
            custom_fields_table.delete(
                custom_field)  # alle Einträge für benutzerdefinierte Felder entfernen, um Tabelle mit neuen befüllen zu können

        custom_field_index = 0
        for custom_field in self.person.custom_fields:
            # Tabelleneintrag darstellen mit Label und Wert
            custom_field_text = f'{custom_field.label} \t{custom_field.field_value}'
            # Tabelleneintrag einfügen. Position ist die im Array der Person.
            custom_fields_table.insert('', custom_field_index,
                                       text=custom_field_text,
                                       iid=custom_field_index)
            custom_field_index += 1
        custom_fields_table['height'] = len(
            self.person.custom_fields)  # Höhe der Tabelle auf die Anzahl der benutzerdefinierten Felder setzen

    def on_doubleclick_custom_field_table(self, event):
        custom_fields_table = self.form_frame.winfo_children()[7]
        region = custom_fields_table.identify('region', event.x, event.y)
        if region == 'tree':
            # auf Doppelklick nur reagieren, wenn er sich auf die Tabelleneinträge bezieht
            for custom_field_index in custom_fields_table.selection():
                custom_field_index = int(
                    custom_field_index)  # ID des benutzerdefinierten Feldes holen (auslesen aus dem Tabelleneintrag)
                custom_field = self.person.custom_fields[
                    custom_field_index]  # benutzerdefiniertes Feld aus der Person holen (Index in der Tabelle = Index im custom_fields-Array der Person)
                CustomFieldWindow(parent=self,
                                  custom_field=custom_field)  # CustomFieldWindow öffnen, um das benutzerdefinierte Feld bearbeiten zu können => CustomFieldWindow mitgeben
                custom_fields_table.selection_remove(custom_field_index)  # Selektion wieder aufheben

    def on_click_custom_field_table(self, event):
        custom_fields_table = self.form_frame.winfo_children()[7]
        region = custom_fields_table.identify('region', event.x, event.y)
        if region == 'heading':
            # auf Einfachklick nur reagieren, wenn er sich auf den Tabellenkopf bezieht
            CustomFieldWindow(
                parent=self)  # ... dann ein neues CustomFieldWindow erstellen um ein neues benutzerdefiniertes Feld zu erstellen

    def editing_finished(self, save_pressed=None):
        """Aktualisieren der Felder wenn save_pressed=True"""
        if save_pressed:
            # Felder der Person neu setzen, wenn abspeichern gedrückt wurde
            self.person.first_name = self.first_name.get()
            self.person.last_name = self.last_name.get()
            if self.birthdate_entry.get():
                self.person.birthdate = int(
                    datetime.combine(self.birthdate_entry.get_date(),
                                     datetime.now().time()).timestamp())  # Datumsangabe normalisieren (Date -> int)
            else:
                self.person.birthdate = None
            contact_management.save(self.person)  # Person in der Datenbank absichern
            t = threading.Thread(target=self.parent.update)  # Tabelle im PersonWindow neu laden
            t.start()
        self.root.destroy()

    def delete_person_button_pressed(self):
        """Löschen der Person"""
        # nur löschen, wenn Nutzer explizite Zustimmung gibt
        if messagebox.askokcancel(title='Kontakt wirklich löschen?',
                                  message='Sie sind im Begriff den Kontakt zu löschen.\nMöchten Sie fortfahren?'):
            contact_management.delete(self.person)
            t = threading.Thread(
                target=self.parent.update)  # Aktualisieren der Tabelle in einem separaten Thread behandeln
            t.start()
            self.root.destroy()  # derweil das PersonWindow schließen

    def center_window(self):
        """Fenster mittig zentrieren relativ zum root-Fenster"""
        window_x = int(self.parent.root.winfo_x() + self.parent.root.winfo_width() / 2 - 210)
        window_y = int(self.parent.root.winfo_y() + self.parent.root.winfo_height() / 2 - 100)
        self.root.geometry(f'+{window_x}+{window_y}')


if __name__ == '__main__':
    root_window = ContactListWindow()
    fake = Faker('de_DE')
    fake.add_provider(phone_number)
    person = PersonVO(fake.name().split(' ')[0], fake.name().split(' ')[0],
                      fake.random.randint(0, int(time.time())), 1)
    # new_contact_window = NewAddressWindow(root_window, person)
    # new_cell_number_window = NewCellNumberWindow(root_window, person)
    # new_custom_field_window = NewCustomFieldWindow(root_window, person)
    #  print(person.custom_fields[0].field_value)

    # contact_group_friends_and_family = ContactGroupVO(title='Freunde und Familie')
    # contact_management.save(contact_group_friends_and_family)
    # contact_group_work = ContactGroupVO(title='Arbeit')
    # contact_management.save(contact_group_work)
    # contact_group_others = ContactGroupVO(title='Andere')
    # contact_management.save(contact_group_others)
