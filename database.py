import sqlite3
from value_objects import *
from exceptions import *
from faker import Faker
from faker.providers import phone_number
import time


# TODO: Datentypen hinzufügen? => Prof. Preuss fragen...
# TODO: Beziehungen hinzufügen! => nochmal überprüfen...

def setup(db_name='contact_book_db.sqlite'):
    """Datenbanktabellen erstellen, wenn nicht schon geschehen und Rückgabe der Datenbankverbindung."""
    db = sqlite3.connect(db_name)
    db.execute('PRAGMA foreign_keys = ON;')  # cascadierendes löschen ermöglichen
    db.commit()
    # Tabellen erstellen
    create_person_table(db)
    create_contact_group_table(db)
    create_belongs_to_table(db)
    create_address_table(db)
    create_cell_number_field_table(db)
    create_custom_field_table(db)
    return db


def get_db():
    """Datenbanktabellen erstellen, wenn nicht schon geschehen und Rückgabe der Datenbankverbindung."""
    return setup()


def create_person_table(db):
    """Datenbanktabelle für den Entitätstyp Person erstellen."""
    cursor = db.cursor()
    # Erstellung nur, wenn nicht bereits geschehen
    cursor.execute('''CREATE TABLE IF NOT EXISTS person (
        person_id INTEGER PRIMARY KEY NOT NULL,
        last_name TEXT,
        first_name TEXT,
        modification_date INTEGER NOT NULL,
        birthdate INTEGER
    );''')
    db.commit()


def create_contact_group_table(db):
    """Datenbanktabelle für den Entitätstyp ContactGroup erstellen."""
    cursor = db.cursor()
    # Erstellung nur, wenn nicht bereits geschehen
    cursor.execute('''CREATE TABLE IF NOT EXISTS contact_group (
        group_id INTEGER PRIMARY KEY NOT NULL,
        title TEXT NOT NULL
    );''')
    db.commit()


def create_custom_field_table(db):
    """Datenbanktabelle für den Entitätstyp CustomField erstellen."""
    cursor = db.cursor()
    # Erstellung nur, wenn nicht bereits geschehen
    cursor.execute('''CREATE TABLE IF NOT EXISTS custom_field (
        field_id INTEGER PRIMARY KEY NOT NULL,
        label TEXT NOT NULL, /* 'value' is already a keyword */
        field_value TEXT NOT NULL,
        v_type TEXT,
        person_id INTEGER NOT NULL,
        -- CustomField löschen, wenn verknüpfte Person gelöscht wird
        FOREIGN KEY (person_id) REFERENCES person (person_id) ON DELETE CASCADE

    );''')
    db.commit()


def create_cell_number_field_table(db):
    """Datenbanktabelle für den Entitätstyp CellNumberField erstellen."""
    cursor = db.cursor()
    # Erstellung nur, wenn nicht bereits geschehen
    cursor.execute('''CREATE TABLE IF NOT EXISTS cell_number_field (
        cell_number_id INTEGER PRIMARY KEY NOT NULL,
        label TEXT NOT NULL,
        cell_number TEXT NOT NULL,
        person_id INTEGER NOT NULL,
        -- CellNumberField löschen, wenn verknüpfte Person gelöscht wird
        FOREIGN KEY (person_id) REFERENCES person (person_id) ON DELETE CASCADE
    );''')
    db.commit()


def create_address_table(db):
    """Datenbanktabelle für den Entitätstyp Address erstellen."""
    cursor = db.cursor()
    # Erstellung nur, wenn nicht bereits geschehen
    cursor.execute('''CREATE TABLE IF NOT EXISTS address (
        address_id INTEGER PRIMARY KEY NOT NULL,
        label TEXT NOT NULL,
        town TEXT,
        zip_code TEXT,
        street TEXT,
        house_number TEXT,
        person_id INTEGER NOT NULL,
        -- Adresse löschen, wenn Person gelöscht wird
        FOREIGN KEY (person_id) REFERENCES person (person_id) ON DELETE CASCADE
    );''')
    db.commit()


def create_belongs_to_table(db):
    """Datenbanktabelle für die m:n-Relation zwischen Person und ContactGroup erstellen."""
    cursor = db.cursor()
    # Erstellung nur, wenn nicht bereits geschehen
    cursor.execute('''CREATE TABLE IF NOT EXISTS belongs_to (
        group_id INTEGER,
        person_id INTEGER,
        -- Eintrag löschen, wenn ContactGroup gelöscht wird
        FOREIGN KEY (group_id) REFERENCES contact_group (group_id) ON DELETE CASCADE,
        -- Eintrag löschen, wenn Person gelöscht wird  
        FOREIGN KEY (person_id) REFERENCES person (person_id) ON DELETE CASCADE,  
        PRIMARY KEY (group_id, person_id)
    );''')
    db.commit()


def insert_person(db,
                  person: PersonVO):  # Datentyp für Autovervollständigung und besserer Lesbarkeit des Codes angegeben
    """PersonVO-Objekt in die Datenbank einpflegen, sollte es noch nicht in der Datenbank existieren."""
    if check_entity_existence(db, person):
        # Exception werfen, wenn die Person bereits exisitiert
        raise EntityAlreadyExistsException('The specified entity already exists in the database')
    modification_date = int(time.time())  # Änderung dann dokumentieren, wenn Daten gesetzt werden
    cursor = db.cursor()
    # INSERT durchführen
    cursor.execute('''INSERT INTO person (modification_date, last_name, first_name, birthdate) VALUES (?, ?, ?, ?);''',
                   (modification_date, person.last_name, person.first_name, person.birthdate))
    person_id = cursor.lastrowid
    person.person_id = person_id  # ID auch in das PersonVO-Objekt eintragen
    if person.groups:
        for group in person.groups:
            if group.group_id and check_entity_existence(db, group):
                # m:n-Relation eintragen zwischen Person und ihren Gruppen
                cursor.execute('''INSERT INTO belongs_to (group_id, person_id) VALUES (?, ?)''',
                               (group.group_id, person.person_id))
    if person.addresses:
        for address in person.addresses:
            # Person der Adresse eine eindeutige Kennung geben und Adresse in die Datenbank einpflegen
            address.person.person_id = person_id
            insert_address(db, address)
    if person.cell_number_fields:
        for cell_number_field in person.cell_number_fields:
            # Person des CellNumberFields einen eindeutige Kennung geben und CellNumberField in die Datenbank einpflegen
            cell_number_field.person.person_id = person_id
            insert_cell_number_field(db, cell_number_field)
    if person.custom_fields:
        for custom_field in person.custom_fields:
            # Person des CustomFields einen eindeutige Kennung geben und CustomField in die Datenbank einpflegen
            custom_field.person.person_id = person_id
            insert_custom_field(db, custom_field)
    db.commit()
    return person_id


def insert_address(db,
                   address: AddressVO):  # Datentyp für Autovervollständigung und besserer Lesbarkeit des Codes angegeben
    """AddressVO-Objekt in die Datenbank einpflegen, sollte es noch nicht in der Datenbank existieren."""
    if check_entity_existence(db, address):
        # Exception werfen, wenn die Adresse bereits exisitiert
        raise EntityAlreadyExistsException('The specified entity already exists in the database')
    cursor = db.cursor()
    # INSERT durchführen
    cursor.execute(
        '''INSERT INTO address (label, street, house_number, zip_code, town, person_id) VALUES (?, ?, ?, ?, ?, ?);''',
        (address.label, address.street, address.house_number, address.zip_code, address.town, address.person.person_id))
    db.commit()
    address_id = cursor.lastrowid  # ID auch in das AddressVO-Objekt eintragen
    address.address_id = address_id
    return address_id


def insert_contact_group(db,
                         contact_group: ContactGroupVO):  # Datentyp für Autovervollständigung und besserer Lesbarkeit des Codes angegeben
    """ContactGroupVO-Objekt in die Datenbank einpflegen, sollte es noch nicht in der Datenbank existieren."""
    if check_entity_existence(db, contact_group):
        # Exception werfen, wenn die ContactGroup bereits exisitiert
        raise EntityAlreadyExistsException('The specified entity already exists in the database')
    cursor = db.cursor()
    # INSERT durchführen
    cursor.execute('''INSERT INTO contact_group (title) VALUES (?);''', (contact_group.title,))
    db.commit()
    group_id = cursor.lastrowid
    contact_group.group_id = group_id  # ID auch in das ContactGroupVO-Objekt eintragen
    if contact_group.persons:
        for person in contact_group.persons:
            if person.person_id and check_entity_existence(db, person):
                # m:n-Relation eintragen zwischen ContactGroup und ihren Personen
                cursor.execute('''INSERT INTO belongs_to (group_id, person_id) VALUES (?, ?);''',
                               (contact_group.group_id, person.person_id))
    db.commit()
    return group_id


def insert_custom_field(db,
                        custom_field: CustomFieldVO):  # Datentyp für Autovervollständigung und besserer Lesbarkeit des Codes angegeben
    """CustomFieldVO-Objekt in die Datenbank einpflegen, sollte es noch nicht in der Datenbank existieren."""
    if check_entity_existence(db, custom_field):
        # Exception werfen, wenn die ContactGroup bereits exisitiert
        raise EntityAlreadyExistsException('The specified entity already exists in the database')
    cursor = db.cursor()
    # INSERT durchführen
    cursor.execute('''INSERT INTO custom_field (label, field_value, v_type, person_id) VALUES (?, ?, ?, ?);''',
                   (custom_field.label, custom_field.field_value, custom_field.v_type, custom_field.person.person_id))
    db.commit()
    field_id = cursor.lastrowid
    custom_field.field_id = field_id  # ID auch in das CustomFieldVO-Objekt eintragen
    return field_id


def insert_cell_number_field(db,
                             cell_number_field: CellNumberFieldVO):  # Datentyp für Autovervollständigung und besserer Lesbarkeit des Codes angegeben
    """CellNumberFieldVO-Objekt in die Datenbank einpflegen, sollte es noch nicht in der Datenbank existieren."""
    if check_entity_existence(db, cell_number_field):
        # Exception werfen, wenn die ContactGroup bereits exisitiert
        raise EntityAlreadyExistsException('The specified entity already exists in the database')
    cursor = db.cursor()
    # INSERT durchführen
    cursor.execute('''INSERT INTO cell_number_field (label, cell_number, person_id) VALUES (?, ?, ?)''',
                   (cell_number_field.label, cell_number_field.cell_number, cell_number_field.person.person_id))
    db.commit()
    cell_number_id = cursor.lastrowid
    cell_number_field.cell_number_id = cell_number_id  # ID auch in das CellNumberFieldVO-Objekt eintragen
    return cell_number_id


def get_all_persons(db) -> [PersonVO]:
    """Holen aller in der Datenbank abgespeicherten PersonVO-Objekten."""
    cursor = db.cursor()
    persons = []
    # alle IDs aus der Datenbank holen
    cursor.execute('''SELECT person_id FROM person;''')
    person_data_sets = cursor.fetchall()
    for person_data in person_data_sets:
        # Für jede ID ein PersonVO-Objekt erzeugen und an Liste aller Personen anhängen
        persons.append(get_person_by_id(db, person_data[0]))
    return persons


def get_all_contact_groups(db) -> [ContactGroupVO]:
    """Holen aller in der Datenbank abgespeicherten ContactGroupVO-Objekten."""
    cursor = db.cursor()
    contact_groups = []
    # alle IDs aus der Datenbank holen
    cursor.execute('''SELECT group_id FROM contact_group;''')
    contact_group_data_sets = cursor.fetchall()
    for contact_group_data in contact_group_data_sets:
        # Für jede ID ein ContactGroupVO-Objekt erzeugen und an Liste aller ContactGroups anhängen
        contact_groups.append(get_contact_group_by_group_id(db, contact_group_data[0]))
    return contact_groups


def get_person_by_id(db, person_id):
    """Erzeugen eines PersonVO-Objektes aus den Daten in der Datenbank."""
    cursor = db.cursor()
    # Alle Attribute für zugehörige Person aus der Datenbank holen
    cursor.execute(
        '''SELECT person_id, last_name, first_name, birthdate, modification_date FROM person WHERE person_id = ?;''',
        (person_id,))
    person_data_set = cursor.fetchall()
    if person_data_set:
        person_data_set = person_data_set[0]  # Personen-Daten-Tupel aus der einelementigen Liste extrahieren
        # Holen aller IDs der Person zugehörigen ContactGroupVOs
        cursor.execute('''SELECT group_id FROM belongs_to WHERE person_id = ?;''', (person_id,))
        group_ids = cursor.fetchall()
        contact_groups = []
        for group_id in group_ids:
            group_id = group_id[0]  # ID aus der einelementigen Liste extrahieren
            cursor.execute('''SELECT group_id, title FROM contact_group WHERE group_id = ?;''', (group_id,))
            contact_group_data = cursor.fetchall()[
                0]  # ContactGroup-Daten-Tupel aus der einelementigen Liste extrahieren
            # ContactGroupVO-Objekt aus Daten zusammenstellen
            contact_group = ContactGroupVO(group_id=contact_group_data[0], title=contact_group_data[1])
            contact_groups.append(contact_group)  # ContactGroup zur Liste der ContactGroups der Person hinzufügen

        # PersonVO-Objekt aus gewonnenen Daten erzeugen
        # Adress-, Telefonnummer-, und benutzerdefinierte Felder werden erst später hinzugefügt,
        # da für deren Erzeugen ein existierendes PersonVO-Objekt bestehen muss
        person = PersonVO(person_id=person_data_set[0], last_name=person_data_set[1],
                          first_name=person_data_set[2],
                          birthdate=person_data_set[3], modification_date=person_data_set[4],
                          groups=contact_groups,
                          addresses=[], cell_number_fields=[],
                          custom_fields=[])
        addresses = get_addresses_by_person(db, person)
        cell_number_fields = get_cell_number_fields_by_person(db, person)
        custom_fields = get_custom_fields_by_person(db, person)
        # Hinzufügen der gerade erzeugten Listen aus Adressen, Telefonnummern und benutzerdefinierten Feldern
        person.addresses = addresses
        person.cell_number_fields = cell_number_fields
        person.custom_fields = custom_fields
        return person
    else:
        # Exception werfen, wenn Eintrag mit gegebener ID nicht existiert
        raise NoSuchEntityException('There is no person entity with the specified person_id')


def get_contact_group_by_group_id(db, group_id):
    """Erzeugen eines ContactGroupVO-Objektes aus den Daten in der Datenbank."""
    cursor = db.cursor()
    # Alle Attribute für zugehörige ContactGroup aus der Datenbank holen
    cursor.execute('''SELECT group_id, title FROM contact_group WHERE group_id = ?;''', (group_id,))
    group_data_set = cursor.fetchall()

    if group_data_set:
        group_data_set = group_data_set[0]  # ContactGroup-Daten-Tupel aus der einelementigen Liste extrahieren
        # Holen aller IDs der ContactGroup zugehörigen PersonVOs
        cursor.execute('''SELECT person_id FROM belongs_to WHERE group_id = ?;''',
                       (group_id,))
        person_ids = cursor.fetchall()
        persons = []
        for person_id in person_ids:
            person_id = person_id[0]  # ID aus der einelementigen Liste extrahieren
            cursor.execute(
                '''SELECT person_id, last_name, first_name, birthdate, modification_date FROM person WHERE person_id = ?;''',
                (person_id,))
            person_data = cursor.fetchall()[0]  # Person-Daten-Tupel aus der einelementigen Liste extrahieren

            # PersonVO-Objekt aus Daten zusammenstellen
            # Adress-, Telefonnummer-, und benutzerdefinierte Felder werden erst später hinzugefügt,
            # da für deren Erzeugen ein existierendes PersonVO-Objekt bestehen muss
            person = PersonVO(person_id=person_data[0], last_name=person_data[1], first_name=person_data[2],
                              birthdate=person_data[3], modification_date=person_data[4],
                              addresses=[], cell_number_fields=[],
                              custom_fields=[])
            addresses = get_addresses_by_person(db, person)
            cell_number_fields = get_cell_number_fields_by_person(db, person)
            custom_fields = get_custom_fields_by_person(db, person)
            # Hinzufügen der gerade erzeugten Listen aus Adressen, Telefonnummern und benutzerdefinierten Feldern
            # Das groups-Feld bleibt leer, da ein Aufruf zum Holen der ContactGroups in einer sich immer wieder
            # aufrufenden Schleife enden würde (diese Funktion würde wiederum eine weitere Funktion aufrufen,
            # die wieder nach den Personen dieser ContactGroups fragen würde).
            person.addresses = addresses
            person.cell_number_fields = cell_number_fields
            person.custom_fields = custom_fields
            persons.append(person)  # Person zur Liste der Personen der ContactGroup hinzufügen

        # ContactGroupVO-Objekt mit den gewonnenen Personen erzeugen
        contact_group = ContactGroupVO(group_id=group_data_set[0], title=group_data_set[1], persons=persons)
        return contact_group
    else:
        # Exception werfen, wenn Eintrag mit gegebener ID nicht existiert
        raise NoSuchEntityException('There is no contact_group entity with the specified group_id')


# def get_contact_groups_by_person_id(db, person_id) -> [ContactGroupVO]:
#     cursor = db.cursor()
#     if check_entity_existence(get_person_by_id(db, person_id)):
#         contact_groups = []
#         cursor.execute('''SELECT group_id FROM belongs_to WHERE person_id = ?''', (person_id,))
#         contact_group_ids = cursor.fetchall()
#         for group_id in contact_group_ids:
#             contact_groups.append(get_contact_group_by_group_id(group_id))
#         return contact_groups


def get_addresses_by_person(db, person) -> [AddressVO]:
    """Holen der Person zugehörigen Adressen aus der Datenbank."""
    if not person.person_id:
        # Es muss bereits eine Person in der Datenbank existieren, wenn die Adresse in der Datenbank existieren soll
        # nicht abgespeicherte Personen besitzen keine ID
        raise NoSuchEntityException('person_id must be set')
    cursor = db.cursor()
    addresses = []
    # Attribute der zur Person gehörenden Adressen anfragen
    cursor.execute(
        '''SELECT address_id, label, street, house_number, zip_code, town FROM address WHERE person_id=?;''',
        (person.person_id,))
    address_data_sets = cursor.fetchall()
    for address_data in address_data_sets:
        # Für jedes Adress-Datentupel ein AddressVO-Objekt erstellen
        addresses.append(
            AddressVO(address_id=address_data[0], label=address_data[1], street=address_data[2],
                      house_number=address_data[3],
                      zip_code=address_data[4], town=address_data[5], person=person))
    return addresses  # erstellte Liste der Adressen zurückgeben


def get_cell_number_fields_by_person(db, person) -> [CellNumberFieldVO]:
    """Holen der Person zugehörigen Telefonnummern-Felder aus der Datenbank."""
    if not person.person_id:
        raise NoSuchEntityException('person_id must be set')
    cursor = db.cursor()
    cell_number_fields = []
    # Attribute der zur Person gehörenden Telefonnummern anfragen
    cursor.execute('''SELECT cell_number_id, label, cell_number FROM cell_number_field WHERE person_id = ?''',
                   (person.person_id,))
    cell_number_fields_data_sets = cursor.fetchall()
    for cell_number_field_data in cell_number_fields_data_sets:
        # Für jedes Telefonnummern-Datentupel ein CellNumberFieldVO-Objekt erstellen
        cell_number_fields.append(CellNumberFieldVO(cell_number_id=cell_number_field_data[0],
                                                    label=cell_number_field_data[1],
                                                    cell_number=cell_number_field_data[2], person=person))
    return cell_number_fields  # erstellte Liste der Telefonnummern-Felder zurückgeben


def get_custom_fields_by_person(db, person) -> [CustomFieldVO]:
    """Holen der Person zugehörigen benutzterdefinierten Felder aus der Datenbank."""
    if not person.person_id:
        raise NoSuchEntityException('person_id must be set')
    cursor = db.cursor()
    custom_fields = []
    # Attribute der zur Person gehörenden benutzerdefinierten Felder anfragen
    cursor.execute('''SELECT field_id, label, field_value, v_type FROM custom_field WHERE person_id = ?''',
                   (person.person_id,))
    custom_fields_data_sets = cursor.fetchall()
    for custom_field_data in custom_fields_data_sets:
        # Für jedes Datentupel eines benutzerdefinierte Feldes ein CustomFieldVO-Objekt erstellen
        custom_fields.append(
            CustomFieldVO(field_id=custom_field_data[0], label=custom_field_data[1],
                          field_value=custom_field_data[2], v_type=custom_field_data[3],
                          person=person))
    return custom_fields  # erstellte Liste der benutzerdefinierten Felder zurückgeben


def check_entity_existence(db, entity):
    """Existenz eines ValueObjects als Entität in der Datenbank überprüfen anhand der ID."""
    cursor = db.cursor()
    if type(entity) == PersonVO:
        cursor.execute('SELECT person_id FROM person WHERE person_id = ?', (entity.person_id,))
        return bool(len(cursor.fetchall()))
    elif type(entity) == ContactGroupVO:
        cursor.execute('SELECT group_id FROM contact_group WHERE group_id = ?', (entity.group_id,))
        return bool(len(cursor.fetchall()))
    elif type(entity) == AddressVO:
        cursor.execute('SELECT address_id FROM address WHERE address_id = ?', (entity.address_id,))
        return bool(len(cursor.fetchall()))
    elif type(entity) == CellNumberFieldVO:
        cursor.execute('SELECT cell_number_id FROM cell_number_field WHERE cell_number_id = ?',
                       (entity.cell_number_id,))
        return bool(len(cursor.fetchall()))
    elif type(entity) == CustomFieldVO:
        cursor.execute('SELECT field_id FROM custom_field WHERE field_id = ?', (entity.field_id,))
        return bool(len(cursor.fetchall()))
    else:
        # Exception werfen, wenn der gegebene Typ des Objektes nicht auf einen Entitätstyp in der Datenbank abgebildet
        # vorliegt
        raise NoSuchEntityTypeException(f'There is no such entity type {type(entity)} existing in the database.')


def delete_address(db,
                   address: AddressVO):  # Datentyp für Autovervollständigung und besserer Lesbarkeit des Codes angegeben
    """Löschen der zum AddressVO-Objekt gehörenden Entität aus der Datenbank."""
    if check_entity_existence(db, address):
        cursor = db.cursor()
        # DELETE durchführen
        cursor.execute('''DELETE FROM address WHERE address_id = ?''', (address.address_id,))
        db.commit()
    else:
        # Exception werfen, wenn keine zugehörige Entität existiert
        raise NoSuchEntityException('The specifed entity does not exist in the database')


def delete_custom_field(db,
                        custom_field: CustomFieldVO):  # Datentyp für Autovervollständigung und besserer Lesbarkeit des Codes angegeben
    """Löschen der zum CustomFieldVO-Objekt gehörenden Entität aus der Datenbank."""
    if check_entity_existence(db, custom_field):
        cursor = db.cursor()
        # DELETE durchführen
        cursor.execute('''DELETE FROM custom_field WHERE field_id = ?''', (custom_field.field_id,))
        db.commit()
    else:
        # Exception werfen, wenn keine zugehörige Entität existiert
        raise NoSuchEntityException('The specifed entity does not exist in the database')


def delete_cell_number_field(db,
                             cell_number_field: CellNumberFieldVO):  # Datentyp für Autovervollständigung und besserer Lesbarkeit des Codes angegeben
    """Löschen der zum CellNumberFieldVO-Objekt gehörenden Entität aus der Datenbank."""
    if check_entity_existence(db, cell_number_field):
        cursor = db.cursor()
        # DELETE durchführen
        cursor.execute('''DELETE FROM cell_number_field WHERE cell_number_id = ?''',
                       (cell_number_field.cell_number_id,))
        db.commit()
    else:
        # Exception werfen, wenn keine zugehörige Entität existiert
        raise NoSuchEntityException('The specifed entity does not exist in the database')


def delete_person(db,
                  person: PersonVO):  # Datentyp für Autovervollständigung und besserer Lesbarkeit des Codes angegeben
    """Löschen der zum PersonVO-Objekt gehörenden Entität aus der Datenbank."""
    if check_entity_existence(db, person):
        cursor = db.cursor()
        # DELETE durchführen
        cursor.execute('''DELETE FROM person WHERE person_id = ?''', (person.person_id,))
        # cursor.execute('''DELETE FROM belongs_to WHERE person_id = ?''', (person.person_id,))
        db.commit()
    else:
        # Exception werfen, wenn keine zugehörige Entität existiert
        raise NoSuchEntityException('The specifed entity does not exist in the database')


def delete_contact_group(db,
                         contact_group: ContactGroupVO):  # Datentyp für Autovervollständigung und besserer Lesbarkeit des Codes angegeben
    """Löschen der zum ContactGroupVO-Objekt gehörenden Entität aus der Datenbank."""
    if check_entity_existence(db, contact_group):
        cursor = db.cursor()
        # DELETE durchführen
        cursor.execute('''DELETE FROM contact_group WHERE group_id = ?''', (contact_group.group_id,))
        # cursor.execute('''DELETE FROM belongs_to WHERE group_id = ?''', (contact_group.group_id,))
        db.commit()
    else:
        # Exception werfen, wenn keine zugehörige Entität existiert
        raise NoSuchEntityException('The specifed entity does not exist in the database')


def update_address(db,
                   address: AddressVO):  # Datentyp für Autovervollständigung und besserer Lesbarkeit des Codes angegeben
    """Aktualisieren der Attributwerte der zum AddressVO-Objekt gehörenden Entität"""
    if check_entity_existence(db, address):
        cursor = db.cursor()
        # Alle Felder neu setzen
        cursor.execute('''UPDATE address
        SET label = ?,
            street = ?,
            house_number = ?,
            zip_code = ?,
            town = ?
        WHERE address_id = ?;''', (
            address.label, address.street, address.house_number, address.zip_code, address.town, address.address_id))
        db.commit()  # Änderungen bestätigen
    else:
        # Exception werfen, wenn keine zum AddressVO-Objekt gehörende Entität existiert.
        raise NoSuchEntityException('The specifed entity does not exist in the database')


def update_custom_field(db,
                        custom_field: CustomFieldVO):  # Datentyp für Autovervollständigung und besserer Lesbarkeit des Codes angegeben
    """Aktualisieren der Attributwerte der zum CustomFieldVO-Objekt gehörenden Entität"""
    if check_entity_existence(db, custom_field):
        cursor = db.cursor()
        # Alle Felder neu setzen
        cursor.execute('''UPDATE custom_field
        SET label = ?,
            field_value = ?,
            v_type = ?,
        WHERE field_id = ?;''',
                       (custom_field.label, custom_field.field_value, custom_field.v_type, custom_field.field_id))
        db.commit()  # Änderungen bestätigen
    else:
        # Exception werfen, wenn keine zum CustomFieldVO-Objekt gehörende Entität existiert.
        raise NoSuchEntityException('The specifed entity does not exist in the database')


def update_cell_number_field(db,
                             cell_number_field: CellNumberFieldVO):  # Datentyp für Autovervollständigung und besserer Lesbarkeit des Codes angegeben
    """Aktualisieren der Attributwerte der zum CellNumberFieldVO-Objekt gehörenden Entität"""
    if check_entity_existence(db, cell_number_field):
        cursor = db.cursor()
        # Alle Felder neu setzen
        cursor.execute('''UPDATE cell_number_field
        SET label = ?,
            cell_number = ?
        WHERE cell_number_id = ?''',
                       (cell_number_field.label, cell_number_field.cell_number, cell_number_field.cell_number_id))
        db.commit()  # Änderungen bestätigen
    else:
        # Exception werfen, wenn keine zum CellNumberField-Objekt gehörende Entität existiert.
        raise NoSuchEntityException('The specifed entity does not exist in the database')


def update_person(db,
                  person: PersonVO):  # Datentyp für Autovervollständigung und besserer Lesbarkeit des Codes angegeben
    """Aktualisieren der Attributwerte der zum PersonVO-Objekt gehörenden Entität"""
    if check_entity_existence(db, person):
        cursor = db.cursor()
        # Attributwerte der Person-Entität neu setzen
        cursor.execute('''UPDATE person
        SET modification_date = ?,
            last_name = ?,
            first_name = ?,
            birthdate = ?
        WHERE person_id = ?''', (
            person.modification_date, person.last_name, person.first_name, person.birthdate, person.person_id))

        # IDs der in der Datenbank abgespeicherten ContactGroups erhalten um sie mit denen der Person zu vergleichen
        cursor.execute('''SELECT group_id FROM belongs_to WHERE person_id = ?''', (person.person_id,))
        group_ids_in_db = [group_id_tuple[0] for group_id_tuple in cursor.fetchall()]
        if person.groups:
            person_group_ids = [group.group_id for group in person.groups]
        else:
            person_group_ids = []
        for db_group_id in group_ids_in_db:
            if db_group_id not in person_group_ids:
                # Beziehungen in der Datenbank löschen, die im PersonVO-Objekt gelöscht wurden
                cursor.execute('''DELETE FROM belongs_to WHERE group_id = ? and person_id = ?;''',
                               (db_group_id, person.person_id))
        for person_group_id in person_group_ids:
            if person_group_id not in group_ids_in_db:
                # Beziehungen zur Datenbank hinzufügen, die im PersonVO-Objekt neu hinzugekommen sind
                cursor.execute('''INSERT INTO belongs_to (group_id, person_id) VALUES (?, ?);''',
                               (person_group_id, person.person_id))

        # update addresses
        # IDs der in der Datenbank abgespeicherten Adressen erhalten um sie mit den Adressen der Person zu vergleichen
        cursor.execute('''SELECT address_id FROM address WHERE person_id = ?''', (person.person_id,))
        address_ids_in_db = [address_id_tuple[0] for address_id_tuple in cursor.fetchall()]
        if person.addresses:
            person_addresses = [address for address in person.addresses]
            person_address_ids = [address.address_id for address in person_addresses]
        else:
            person_addresses = []
            person_address_ids = []
        for db_address_id in address_ids_in_db:
            if db_address_id not in person_address_ids:
                # Adressen aus der Datenbank löschen, die aus dem PersonVO-Objekt entfernt wurden
                cursor.execute('''DELETE FROM address WHERE address_id = ?''', (db_address_id,))
        for person_address in person_addresses:
            # für jedes Aktualisieren der Person auch die Adressen aktualisieren (neu einfügen oder aktualisieren)
            try:
                insert_address(db, person_address)
            except EntityAlreadyExistsException:
                update_address(db, person_address)

        # update cell_number_fields
        # IDs der in der Datenbank abgespeicherten Telefonnummern erhalten um sie mit den Telefonnummern der Person zu vergleichen
        cursor.execute('''SELECT cell_number_id FROM cell_number_field WHERE person_id = ?''', (person.person_id,))
        cell_number_ids_in_db = [cell_number_id_tuple[0] for cell_number_id_tuple in cursor.fetchall()]
        if person.cell_number_fields:
            person_cell_number_fields = [cell_number_field for cell_number_field in person.cell_number_fields]
            person_cell_number_ids = [cell_number_field.cell_number_id for cell_number_field in
                                      person_cell_number_fields]
        else:
            person_cell_number_fields = []
            person_cell_number_ids = []
        for db_cell_number_id in cell_number_ids_in_db:
            if db_cell_number_id not in person_cell_number_ids:
                # Telefonnummern aus der Datenbank löschen, die aus dem PersonVO-Objekt entfernt wurden
                cursor.execute('''DELETE FROM cell_number_field WHERE cell_number_id = ?''', (db_cell_number_id,))
        for person_cell_number_field in person_cell_number_fields:
            # für jedes Aktualisieren der Person auch die Telefonnummern aktualisieren (neu einfügen oder aktualisieren)
            try:
                insert_cell_number_field(db, person_cell_number_field)
            except EntityAlreadyExistsException:
                update_cell_number_field(db, person_cell_number_field)

        # update custom_fields
        # IDs der in der Datenbank abgespeicherten benutzerdefinierten Felder erhalten um sie mit denen der Person zu vergleichen
        cursor.execute('''SELECT field_id FROM custom_field WHERE person_id = ?''', (person.person_id,))
        field_ids_in_db = [field_id_tuple[0] for field_id_tuple in cursor.fetchall()]
        if person.custom_fields:
            person_custom_fields = [custom_field for custom_field in person.custom_fields]
            person_custom_field_ids = []
        else:
            person_custom_fields = []
            person_custom_field_ids = []
        for db_custom_field_id in field_ids_in_db:
            # benutzerdefinierte Felder aus der Datenbank löschen, die aus dem PersonVO-Objekt entfernt wurden
            if db_custom_field_id not in person_custom_field_ids:
                cursor.execute('''DELETE FROM custom_field WHERE field_id = ?''', (db_custom_field_id,))

        for person_custom_field in person_custom_fields:
            # für jedes Aktualisieren der Person auch die benutzerdefinierten Felder aktualisieren (neu einfügen oder aktualisieren)
            try:
                insert_custom_field(db, person_custom_field)
            except EntityAlreadyExistsException:
                update_custom_field(db, person_custom_field)

        db.commit()
    else:
        # Exception werfen, wenn keine zum PersonVO-Objekt gehörende Entität existiert.
        raise NoSuchEntityException('The specifed entity does not exist in the database')


def update_contact_group(db,
                         contact_group: ContactGroupVO):  # Datentyp für Autovervollständigung und besserer Lesbarkeit des Codes angegeben
    """Aktualisieren der Attributwerte der zum ContactGroupVO-Objekt gehörenden Entität"""
    if check_entity_existence(db, contact_group):
        cursor = db.cursor()
        # Attributwerte der ContactGroup neu setzen
        cursor.execute('''UPDATE contact_group
        SET title = ? 
        WHERE group_id = ?''', (contact_group.title, contact_group.group_id))

        # IDs der in der Datenbank abgespeicherten Personen erhalten um sie mit denen der ContactGroup zu vergleichen
        cursor.execute('''SELECT person_id FROM belongs_to WHERE group_id = ?''', (contact_group.group_id,))
        person_ids_in_db = [person_id_tuple[0] for person_id_tuple in cursor.fetchall()]
        if contact_group.persons:
            group_person_ids = [person.person_id for person in contact_group.persons]
        else:
            group_person_ids = []
        for group_person_id in group_person_ids:
            if group_person_id not in person_ids_in_db:
                # Beziehungen zur Datenbank hinzufügen, die im ContactGroup-Objekt neu hinzugekommen sind
                cursor.execute('''INSERT INTO belongs_to (group_id, person_id) VALUES (?, ?)''',
                               (contact_group.group_id, group_person_id))
        for db_person_id in person_ids_in_db:
            if db_person_id not in group_person_ids:
                # Beziehungen in der Datenbank löschen, die im ContactGroup-Objekt gelöscht wurden
                cursor.execute('''DELETE FROM belongs_to WHERE person_id = ? and group_id = ?''',
                               (db_person_id, contact_group.group_id))
        db.commit()
    else:
        # Exception werfen, wenn keine zum ContactGroupVO-Objekt gehörende Entität existiert.
        raise NoSuchEntityException('The specifed entity does not exist in the database')


if __name__ == '__main__':
    db = setup()
    fake = Faker('de_DE')
    fake.add_provider(phone_number)
    person = PersonVO(fake.name().split(' ')[0], fake.name().split(' ')[0],
                      fake.random.randint(0, int(time.time())), 1)
    # for _ in range(0, 20):
    #     insert_person(db, person)
    #     # get_all_persons(db)
    #     # get_contact_group_by_id(db, 1)
    #     # get_person_by_id(db, 2)
    #     # print(len(get_all_persons(db)))
    #     # print(len(get_all_contact_groups(db)))
    #     fake_address = fake.address()
    #     fake_address = [line.split(' ') for line in fake_address.splitlines()]
    #     random_person_id = fake.random.randint(1, len(get_all_persons(db)))
    #     random_person = get_person_by_id(db, random_person_id)
    #     insert_address(db, Address(label='Home', person=random_person, street=fake_address[0][0],
    #                                house_number=fake_address[0][1], zip_code=fake_address[1][0],
    #                                town=fake_address[1][1]))
    #     get_addresses_by_person_id(db, random_person.person_id)
    #     phone_number = fake.phone_number()
    #     random_person_id = fake.random.randint(1, len(get_all_persons(db)))
    #     random_person = get_person_by_id(db, random_person_id)
    #     insert_cell_number_field(db, CellNumberField(label='Home', cell_number=phone_number, person=random_person))
    #
    #     fake_label = fake.text()[0:10].split(' ')[0]
    #     fake_value = fake.text()[0:32]
    #     random_person_id = fake.random.randint(1, len(get_all_persons(db)))
    #     random_person = get_person_by_id(db, random_person_id)
    #     insert_custom_field(db, CustomField(label=fake_label, field_value=fake_value, person=random_person))
    # delete_person(db, get_person_by_id(db, 1))
    # delete_contact_group(db, get_contact_group_by_group_id(db, 3))
    # delete_address(db, get_addresses_by_person_id(db, 2)[0])
    # delete_custom_field(db, get_custom_fields_by_person_id(db, 3)[0])
    # delete_cell_number_field(db, get_cell_number_fields_by_person_id(db, 4)[0])
    # person = Person(person_id=11, modification_date=123, first_name='Peter')
    # update_person(db, person)
    # contact_group = ContactGroup(group_id=1, title='Andere', persons=[])
    # update_contact_group(db, contact_group)
    # print(get_addresses_by_person_id(db, person_id=5000))
    # print(get_cell_number_fields_by_person_id(db, person_id=5000))
    # person_1 = get_person_by_id(db, person_id=1)
    # print(person.person_id)
    # fake_address = fake.address()
    # fake_address = [line.split(' ') for line in fake_address.splitlines()]
    # random_person_id = fake.random.randint(1, len(get_all_persons(db)))
    # random_person = get_person_by_id(db, random_person_id)
    # address = AddressVO(label='Home', person=person, street='fake_address[0][0]',
    #                                    house_number="fake_address[0][1]", zip_code='fake_address[1][0]',
    #                                    town='fake_address[1][1]')
    # phone_number = fake.phone_number()
    # random_person_id = fake.random.randint(1, len(get_all_persons(db)))
    # random_person = get_person_by_id(db, random_person_id)
    # cell_number_field = CellNumberFieldVO(label='Home', cell_number='phone_number', person=person)
    #
    # fake_label = fake.text()[0:10].split(' ')[0]
    # fake_value = fake.text()[0:32]
    # random_person_id = fake.random.randint(1, len(get_all_persons(db)))
    # random_person = get_person_by_id(db, random_person_id)
    # custom_field = CustomFieldVO(label='fake_label', field_value='fake_value', person=person)
    # person = PersonVO(fake.name().split(' ')[0], fake.name().split(' ')[0], fake.random.randint(0, int(time.time())), 1, None, [address,], [cell_number_field,], [custom_field,])
    # person_id = insert_person(db, person)

    # person.addresses = [address, AddressVO(label='MyHome', person=person, street='Musterstr 5', house_number='67', zip_code='12345', town='Klm.')]
    # address.label = 'work'
    # person.addresses = [address,]
    # person.cell_number_fields = [cell_number_field, CellNumberFieldVO(label='mobile', cell_number='+46 123 457987', person=person)]
    # person.cell_number_fields = []
    # person.custom_fields = [custom_field,]
    # cell_number_field.label = 'work'
    # person.custom_fields = [custom_field, CustomFieldVO(label='work', field_value='+46 12345765', person=person)]
    # person.custom_fields = []
    # custom_field.label = 'fax'
    # update_person(db, person)
    # person_info = get_person_by_id(db, person_id=person.person_id)
    get_contact_group_by_group_id(db, 2)
    get_person_by_id(db, 1)
