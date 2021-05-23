from exceptions import *


class PersonVO:
    """Value Object zum Kapseln der Daten einer Person wie sie in der Datenbank existieren."""

    def __init__(self, last_name: str = None, first_name: str = None, birthdate: int = None,
                 modification_date: int = None, groups=None, addresses=None, cell_number_fields=None,
                 custom_fields=None,
                 person_id: int = None):
        if ((type(last_name) == str or last_name is None)
                and (type(first_name) == str or first_name is None)
                and (type(birthdate) == int or birthdate is None)
                and (type(modification_date) == int or modification_date is None)
                and (groups == [] or groups is None or (
                        type(groups) == list and all(type(group) == ContactGroupVO for group in groups)))
                and (addresses == [] or addresses is None or (
                        type(addresses) == list and all(type(address) == AddressVO for address in addresses)))
                and (cell_number_fields == [] or cell_number_fields is None or (
                        type(cell_number_fields) == list and all(
                    type(cell_number_field) == CellNumberFieldVO for cell_number_field in cell_number_fields)))
                and (custom_fields == [] or custom_fields is None or (type(custom_fields) == list and all(
                    type(custom_field) == CustomFieldVO for custom_field in custom_fields)))
                and (type(person_id) == int or person_id is None)):
            self.person_id = person_id
            self.last_name = last_name
            self.first_name = first_name
            self.birthdate = birthdate
            self.modification_date = modification_date
            self.groups = (groups or [])
            self.addresses = (addresses or [])
            self.cell_number_fields = (cell_number_fields or [])
            self.custom_fields = (custom_fields or [])

            for address in self.addresses:
                if not address.person:
                    address.person = self

            for cell_number_field in self.cell_number_fields:
                if not cell_number_field.person:
                    cell_number_field.person = self

            for custom_field in self.custom_fields:
                if not custom_field.person:
                    custom_field.person = self

            for group in self.groups:
                if self not in group.persons:
                    group.persons.append(self)

        else:
            raise TypeError('Please initialize with matching data types')

    def add(self, entity):
        """Hinzufügen einer Entität (AddressVO, CellNumberFieldVO, ContactGroupVO oder CustomFieldVO) zur Person."""
        if type(entity) == AddressVO:
            if entity.address_id is None or not self.entity_already_added(entity):
                # nur hinzufügen, wenn Adresse nicht bereits hinzugefügt wurde oder es sich um eine neue Adresse handelt (ID noch nicht gesetzt).
                self.addresses.append(entity)
            entity.person = self
        elif type(entity) == CellNumberFieldVO:
            if entity.cell_number_id is None or not self.entity_already_added(entity):
                # nur hinzufügen, wenn Telefonnummer nicht bereits hinzugefügt wurde oder es sich um eine neue Telefonnummer handelt (ID noch nicht gesetzt).
                self.cell_number_fields.append(entity)
            entity.person = self
        elif type(entity) == CustomFieldVO:
            if entity.field_id is None or not self.entity_already_added(entity):
                # nur hinzufügen, wenn benutzerdefiniertes Feld nicht bereits hinzugefügt wurde oder es sich um ein neues benutzerdefiniertes Feld handelt (ID noch nicht gesetzt).
                self.custom_fields.append(entity)
            entity.person = self
        elif type(entity) == ContactGroupVO:
            if entity.group_id is None or not self.entity_already_added(entity):
                # nur hinzufügen, wenn ContactGroup nicht bereits hinzugefügt wurde oder es sich um eine neue Gruppe handelt (ID noch nicht gesetzt).
                self.groups.append(entity)
            entity.persons.append(self)
        else:
            # Exception werfen, wenn Typ des Objekts in der Parameterliste nicht existiert
            raise NoSuchEntityTypeException(
                'The entity must be of one of the following types: AddressVO, ' +
                'CellNumberFieldVO, CustomFieldVO or ContactGroupVO')

    def remove(self, entity):
        """Entfernen einer Entität (AddressVO, CellNumberFieldVO, ContactGroupVO oder CustomFieldVO) der Person."""
        if type(entity) == AddressVO:
            try:
                for address in self.addresses:
                    if address.address_id == entity.address_id or (address is entity):
                        # löschen, wenn IDs übereinstimmen oder Adresse zwar schon unter den Adressen aufgelistet ist, aber noch nicht abgespeichert wurde (dann keine ID vorhanden)
                        self.addresses.remove(address)  # jedes Vorkommen unter den Adressen der Person löschen
            except ValueError as err:
                raise NoSuchEntityException(err)
        elif type(entity) == CellNumberFieldVO:
            try:
                for cell_number_field in self.cell_number_fields:
                    if cell_number_field.cell_number_id == entity.cell_number_id or (cell_number_field is entity):
                        # löschen, wenn IDs übereinstimmen oder CellNumberField zwar schon unter den cell_number_fields aufgelistet ist,
                        # aber noch nicht abgespeichert wurde (dann keine ID vorhanden)
                        self.cell_number_fields.remove(
                            entity)  # jedes Vorkommen unter den Telefonnummern der Person löschen
            except ValueError as err:
                raise NoSuchEntityException(err)
        elif type(entity) == CustomFieldVO:
            try:
                for custom_field in self.custom_fields:
                    if custom_field.field_id == entity.field_id or (custom_field is entity):
                        # löschen, wenn IDs übereinstimmen oder CustomField zwar schon unter den custom_fields aufgelistet ist,
                        # aber noch nicht abgespeichert wurde (dann keine ID vorhanden)
                        self.custom_fields.remove(
                            entity)  # jedes Vorkommen unter den benutzerdefinierten Feldern der Person löschen
            except ValueError as err:
                raise NoSuchEntityException(err)
        elif type(entity) == ContactGroupVO:
            try:
                for group in self.groups:
                    if group.group_id == entity.group_id or (group is entity):
                        # löschen, wenn IDs übereinstimmen oder ContactGroup zwar schon unter den groups aufgelistet ist,
                        # aber noch nicht abgespeichert wurde (dann keine ID vorhanden)
                        self.groups.remove(group)  # Gruppe aus den eigenen ContactGroups löschen

                for person in entity.persons:
                    if person.person_id == self.person_id:
                        entity.persons.remove(
                            person)  # umgekehrt auch entfernen der Person aus der angegebenen ContactGroup
            except ValueError as err:
                raise NoSuchEntityException(err)
        else:
            # Exception werfen, wenn Entitätstyp des Objekts in der Parameterliste nicht existiert
            raise NoSuchEntityTypeException(
                'The entity must be of one of the following types: AddressVO, ' +
                'CellNumberFieldVO, CustomFieldVO or ContactGroupVO')

    def entity_already_added(self, entity):
        entity_exists = False
        if type(entity) == AddressVO:
            for address in self.addresses:
                if address.address_id == entity.address_id:  # Evaluation der Existenz allein anhand der IDs
                    entity_exists = True  # Entität existiert, sobald eine übereinstimmende ID gefunden wurde

        elif type(entity) == CellNumberFieldVO:
            for cell_number_field in self.cell_number_fields:
                if cell_number_field.cell_number_id == entity.cell_number_id:
                    entity_exists = True

        elif type(entity) == CustomFieldVO:
            for custom_field in self.custom_fields:
                if custom_field.field_id == entity.field_id:
                    entity_exists = True

        elif type(entity) == ContactGroupVO:
            for contact_group in self.groups:
                if contact_group.group_id == entity.group_id:
                    entity_exists = True
        else:
            # Exception werfen, wenn Entitätstyp des Objekts in der Parameterliste nicht existiert
            raise NoSuchEntityTypeException(
                'The entity must be of one of the following types: AddressVO, ' +
                'CellNumberFieldVO, CustomFieldVO or ContactGroupVO')
        return entity_exists


class CellNumberFieldVO:
    def __init__(self, label: str, cell_number: str, person: PersonVO, cell_number_id: int = None):
        if (type(label) == str and type(cell_number) == str and type(person) == PersonVO
                and (type(cell_number_id) == int or cell_number_id is None)):
            if label and cell_number and person:
                self.cell_number_id = cell_number_id
                self.label = label
                self.cell_number = cell_number
                self.person = person
            else:
                # Exception werfen, sollte ein benötigter Parameter leer sein
                raise ValueError('All attributes must not be empty')
        else:
            # Exception werfen, sollte ein Parameter einen falschen Typ haben
            raise TypeError('All attributes have to be of type str')


class AddressVO:
    def __init__(self, label: str, person: PersonVO, street: str = None, house_number: str = None,
                 zip_code: str = None,
                 town: str = None, address_id: int = None):
        if (type(label) == str
                and (type(street) == str or street is None)
                and (type(house_number) == str or house_number is None)
                and (type(zip_code) == str or zip_code is None)
                and (type(town) == str or town is None)
                and (type(address_id) == int or address_id is None)
                and (type(person) == PersonVO)):
            if label and person:
                self.address_id = address_id
                self.label = label
                self.town = town
                self.zip_code = zip_code
                self.street = street
                self.house_number = house_number
                self.person = person
            else:
                # Exception werfen, sollte ein benötigter Parameter leer sein
                raise ValueError('Label must not be empty')
        else:
            # Exception werfen, sollte ein Parameter einen falschen Typ haben
            raise TypeError('All attributes have to be of type str')


class CustomFieldVO:
    def __init__(self, label: str, field_value: str, person: PersonVO, field_id: int = None,
                 v_type: str = None):
        if (type(label) == str and type(field_value) == str and type(person) == PersonVO
                and (type(field_id) == int or field_id is None)
                and (type(
                    v_type) == str or v_type is None)):
            if label and field_value and person:
                self.field_id = field_id
                self.label = label
                self.field_value = field_value
                self.v_type = v_type
                self.person = person
            else:
                # Exception werfen, sollte ein benötigter Parameter leer sein
                raise ValueError('All attributes must not be empty')
        else:
            # Exception werfen, sollte ein Parameter einen falschen Typ haben
            raise TypeError('All attributes have to be of type str')


class ContactGroupVO:
    def __init__(self, title: str, persons: [PersonVO] = None, group_id: int = None):
        if (type(title) == str
                and (persons == [] or persons is None or (
                        type(persons) == list and all(type(person) == PersonVO for person in persons)))
                and (type(group_id) == int or group_id is None)):
            if title:
                self.title = title
                self.group_id = group_id
                self.persons = (persons or [])

                for person in self.persons:  # sicherstellen, dass alle Personen in der Gruppe auch selber die Gruppe enthalten
                    if self not in person.groups:
                        person.groups.append(self)
            else:
                # Exception werfen, sollte ein benötigter Parameter leer sein
                raise ValueError('Title must not be empty')
        else:
            # Exception werfen, sollte ein Parameter einen falschen Typ haben
            raise TypeError('All parameter datatypes have to match')

    def add(self, entity: PersonVO):
        if type(entity) == PersonVO:
            if not self.entity_already_added(entity):
                self.persons.append(entity)
            if self not in entity.groups:
                entity.groups.append(self)
        else:
            # Exception werfen, wenn ein anderer (Entitäts-)Typ als PersonVO angegeben wird
            raise IllegalEntityTypeException('The entity must be of type PersonVO')

    def remove(self, entity: PersonVO):
        if type(entity) == PersonVO:
            try:
                for person in self.persons:
                    if person.person_id == entity.person_id:
                        self.persons.remove(person)  # Person aus den eigenen Personen löschen
                for group in entity.groups:
                    if group.group_id == self.group_id:
                        entity.groups.remove(group)  # umgekehrt auch entfernen der Gruppe aus der angegebenen Person
            except ValueError as err:
                raise NoSuchEntityException(
                    'The given entity does not exist in the list of group members (persons)' + err)
        else:
            # Exception werfen, wenn ein anderer (Entitäts-)Typ als PersonVO angegeben wird
            raise IllegalEntityTypeException('The entity must be of type PersonVO')

    def entity_already_added(self, entity):
        existence = False
        if type(entity) == AddressVO:
            for address in self.addresses:
                if address.address_id == entity.address_id:  # Evaluation der Existenz allein anhand der IDs
                    existence = True  # Entität existiert, sobald eine übereinstimmende ID gefunden wurde
        else:
            raise NoSuchEntityTypeException(
                'The entity must be of one of the following types: PersonVO')
        return existence
