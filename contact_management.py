from value_objects import *
from exceptions import *
import database
import time


def save(entity):
    """Speichern oder Aktualisieren eines PersonVO- oder ContactGroupVO-Objekts in der Datenbank."""
    if type(entity) == PersonVO:
        db = database.get_db()  # Datenbankverbindung holen, um SQL-Anfragen auf der Datenbank auszuführen.
        try:
            entity.modification_date = int(
                time.time())  # Zeitstempel für letzte Änderung aktualisieren  # TODO: das in update_person() integrieren
            database.update_person(db, entity)  # wirft eine NoSuchEntityException,
            # wenn Person noch nicht in der Datenbank existiert.
        except NoSuchEntityException:
            person_id = database.insert_person(db, entity)  # Existiert die Person noch nicht in der Datenbank,
            # wird sie erstmalig eingefügt.
            return person_id
        finally:
            db.close()

    elif type(entity) == ContactGroupVO:
        db = database.get_db()  # Datenbankverbindung holen, um SQL-Anfragen auf der Datenbank auszuführen.
        try:
            database.update_contact_group(db, entity)  # wirft eine NoSuchEntityException,
            # wenn ContactGroup noch nicht in der Datenbank existiert.
        except NoSuchEntityException:
            group_id = database.insert_contact_group(db, entity)  # Existiert die ContactGroup noch nicht in der
            # Datenbank, wird sie erstmalig eingefügt.
            return group_id

        finally:
            db.close()  # in jedem Fall Datenbankverbindung wieder schließen
    else:
        # Exception werfen, wenn Typ des Objekts in der Parameterliste nicht unterstützt wird
        raise IllegalEntityTypeException('The entity must be of one of the following types: PersonVO or ' +
                                         'ContactGroupVO')


def delete(entity):
    """Löschen einer Person oder einer ContactGroup aus der Datenbank bewirken."""
    if type(entity) == PersonVO:
        db = database.get_db()
        database.delete_person(db, entity)  # löschen der Person in der Datenbank
        db.close()
    elif type(entity) == ContactGroupVO:
        db = database.get_db()
        database.delete_contact_group(db, entity)  # löschen der ContactGroup in der Datenbank
        db.close()
    else:
        # Exception werfen, wenn der Typ des Objekts in der Parameterliste nicht unterstützt wird
        raise IllegalEntityTypeException('The entity must be of one of the following types: PersonVO or ' +
                                         'ContactGroupVO')


def get_all_persons():
    """Holen aller Personen aus der Datenbank."""
    db = database.get_db()
    all_persons = database.get_all_persons(db)  # Alle Personen aus der Datenbank erhalten
    db.close()
    return all_persons


def get_persons_by_contact_group(contact_group: ContactGroupVO):
    """Holen aller Personen einer ContactGroup aus der Datenbank."""
    db = database.get_db()
    if not contact_group.group_id:  # Sicherstellen, dass group_id für die spätere SQL-Anfrage gesetzt ist
        raise NoSuchEntityException('Please specify an existing contact_group')
    contact_group = database.get_contact_group_by_group_id(contact_group.group_id)  # entsprechende ContactGroup aus
    # der Datenbank holen
    persons = contact_group.persons  # Personen aus der ContactGroup extrahieren
    db.close()
    return persons


def get_all_contact_groups():
    """Holen aller ContactGroups aus der Datenbank."""
    db = database.get_db()
    all_contact_groups = database.get_all_contact_groups(db)  # passende Funktion auf database aufrufen
    db.close()
    return all_contact_groups


def get_person_by_id(person_id):
    """Holen der Person aus der Datenbank."""
    db = database.get_db()
    person = database.get_person_by_id(db, person_id)  # passende Funktion auf database aufrufen
    db.close()
    return person


if __name__ == '__main__':
    # Es folgen Anweisunge
    db = database.get_db()
    group = ContactGroupVO(title='Friends & Family')
    person = PersonVO(last_name='Meier', first_name='Friedrich', birthdate=int(time.time()), groups=[group],
                      addresses=[], cell_number_fields=[], custom_fields=[])
    address = AddressVO(label='Home', street='Musterstr.', house_number='123', zip_code='12345',
                        town='Musterstadt', person=person)
    custom_field = CustomFieldVO(label='Company', field_value='Mustercompany', person=person)
    cell_number_field = CellNumberFieldVO(label='Mobile', cell_number='+43 123456789', person=person)
    # save(person)
    # save(group)
    # person.add(address)
    # person.add(custom_field)
    # person.add(cell_number_field)
    # save(person)
    person = database.get_person_by_id(db, 69)
    # address2 = AddressVO(label='work', person=person, street='workstreet', house_number='1',
    #                                  zip_code='12345', town='Musterstadt')
    # custom_field2 = CustomFieldVO(label='nick name', field_value='nick', person=person)
    # cell_number_field2 = CellNumberFieldVO(label='work', cell_number='+12 9876543', person=person)
    # person.add(address2)
    # person.add(custom_field2)
    # person.add(cell_number_field2)
    # group2 = ContactGroupVO(title='Work')
    # save(group2)
    # person.add(group2)
    # save(person)
    # group2 = database.get_contact_group_by_group_id(db, 5)
    # person.remove(group2)
    # save(person)
    # person = database.get_person_by_id(db, 69)
    # group2.add(person)
    # save(group2)
    # group2 = database.get_contact_group_by_group_id(db, 5)
    # group2.add(person)
    # group2.remove(person)
    # save(group2)
    # group2 = database.get_contact_group_by_group_id(db, 5)
    # address = database.get_addresses_by_person(db, person)
    # person.add(address)
    # save(person)
    # person = database.get_person_by_id(db, 69)
    # person.remove(address)
    # save(person)
    person = database.get_person_by_id(db, 69)
    delete(person)
    print('objects have been initialised')
