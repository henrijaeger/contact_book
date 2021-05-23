from value_objects import *
import vobject
import contact_management
from datetime import datetime
import time


def get_serialized_person(person: PersonVO):
    v_card = vobject.vCard()  # vCard-Objekt instanziieren zur Datenhaltung
    v_card.add('fn')  # fn-Feld zur vCard hinzufügen
    v_card.fn.value = person.first_name + ' ' + person.last_name  # fn-Wert setzen (Vorname + Nachname)
    persons_organization = None

    for cell_number_field in person.cell_number_fields:
        v_card.add('tel').value = cell_number_field.cell_number  # Telefonnummer zur vCard hinzufügen
        v_card.tel_list[-1].type_param = cell_number_field.label  # tel-TYPE mit der Bezeichnung (label) versehen

    for address in person.addresses:
        v_card.add('adr').value = vobject.vcard.Address(street=address.street + ' ' + address.house_number,
                                                        city=address.town,
                                                        code=address.zip_code)  # Adresse zur vCard hinzufügen
        v_card.adr_list[-1].type_param = address.label  # adr-TYPE mit der Bezeichnung (label) versehen

    for custom_field in person.custom_fields:
        if custom_field.v_type == 'eMail':
            v_card.add('email').value = custom_field.field_value  # eMail zur vCard hinzufügen
            v_card.email_list[-1].type_param = custom_field.label  # email-TYPE mit der Bezeichnung (label) versehen

        elif custom_field.v_type == 'URL':
            v_card.add('url').value = custom_field.field_value  # Website der Person zur vCard hinzufügen
            v_card.url_list[-1].type_param = custom_field.label  # url-TYPE mit der Bezeichnung (label) versehen

        elif custom_field.v_type == 'Spitzname':
            v_card.add('nickname').value = custom_field.field_value  # Spitznamen zur vCard hinzufügen
            v_card.nickname_list[
                -1].type_param = custom_field.label  # nickname-TYPE mit der Bezeichnung (label) versehen

        elif custom_field.v_type == 'Public Key':
            v_card.add('key').value = custom_field.field_value  # Public Key zur vCard hinzufügen
            v_card.key_list[-1].type_param = custom_field.label  # key-TYPE mit der Bezeichnung (label) versehen

        elif custom_field.v_type == 'Geschlecht':
            # Geschlecht in den vCard-Standard konvertieren
            if custom_field.field_value.strip() == 'maennlich':
                v_card.add('gender').value = 'M'
            elif custom_field.field_value.strip() == 'weiblich':
                v_card.add('gender').value = 'F'
            else:
                v_card.add('gender').value = 'O'

        elif custom_field.v_type == 'Hobby':
            v_card.add('hobby').value = custom_field.field_value  # Hobby in die vCard eintragen

        elif custom_field.v_type == 'Titel':
            # vollständigen Namen mit Titel in die vCard eintragen, falls das Feld gesetzt ist
            v_card.add('n').value = vobject.vcard.Name(family=person.last_name, given=person.first_name,
                                                       prefix=custom_field.field_value)

        elif custom_field.v_type == 'Firma':
            # Unternehmens-String für den manuellen Eintrag in die serialisierte vCard vorbereiten
            persons_organization = custom_field.field_value + ';;'

        else:
            # Andere Typen in die vCard eintragen und Wert entsprechend setzen
            v_card.add((custom_field.v_type.replace(' ', '_') or 'Keiner').lower()).value = custom_field.field_value
            type_key = (custom_field.v_type.replace(' ', '_') or 'Keiner').lower()
            v_card.contents[type_key][
                -1].type_param = custom_field.label  # für benutzerdefinierten Typ im TYPE-Feld die Bezeichnung angeben

    for contact_group in person.groups:
        if contact_group.group_id:
            v_card.add('categories').value = [contact_group.title]  # Gruppen-Name der vCard hinzufügen

    if v_card.contents.get('n', None) is None:
        # sollte kein Titel existieren, den vollständigen Namen nochmal ohne Präfix setzen
        v_card.add('n').value = vobject.vcard.Name(family=person.last_name, given=person.first_name)

    serialized_v_card = v_card.serialize()  # vCard in einen String umwandeln (vcf-Standard)

    if person.birthdate:
        serialized_v_card_splitted = serialized_v_card.split('\n')
        # Geburtsdatum angeben in Zeile 3, wenn es spezifiziert wurde (umwandeln von int in Date)
        serialized_v_card_splitted.insert(3, f'BDAY:{datetime.fromtimestamp(person.birthdate).date()}\r')
        serialized_v_card = '\n'.join(serialized_v_card_splitted)

    if persons_organization:
        serialized_v_card_splitted = serialized_v_card.split('\n')
        # Firma angeben in Zeile 3, wenn sie angegeben wurde
        serialized_v_card_splitted.insert(3, f'ORG:{persons_organization}\r')
        serialized_v_card = '\n'.join(serialized_v_card_splitted)

    return serialized_v_card  # serialisierte vCard für den Inhalt einer vcf-Datei zurückgeben


def export_persons(file_path, contact_group):
    """Exportiert alle Kontakte in einen gewählten Ordner"""
    now = datetime.now()  # setzt die Zeit für automatische bennenung des Files
    format = '%Y%m%d'
    time1 = now.strftime(format)

    filepath_and_name = file_path + '/contacts' + time1 + '.vcf'  # der übergebene Filepath wird mit den automatisch
    # erstellten Angaben vervollständigt

    to_be_saved_file = open(filepath_and_name, 'w')  # erstellt ein Dokument am angegebenen Filepath

    for person in contact_group.persons:  # iteriert durch alle Personen und schreibt sie in die Datei
        to_be_saved_file.write(get_serialized_person(person))

    to_be_saved_file.close()


def import_persons(file):
    """importiert vcf files mit beliebig vielen Kontakten"""
    dataraw = file.read()  # öffnet die übergebene Datei

    data = dataraw.rsplit('END:VCARD')  # unterteilt die Datei bei dem Endpunkt von einer vcard Datei: END:VCARD

    for i in data:  # fügt die unterteilten Kontakte unserer Datenbank hinzu
        card = i + 'END:VCARD'  # fügt das vcard File-Ende wieder an
        if len(i) > 20:  # überprüft, dass wir keine falschen Eingaben wie z. B.: nur END:VCARD übergeben
            import_person(card)  # ruft die Importfunktion für jede vCard auf


def import_person(v_card_serialized: str):
    v_card_serialized.replace('\n', '\r\n')  # Ohne diese Ersetzung schlägt readOne-Funktion fehl
    v_card = vobject.readOne(v_card_serialized)  # serialisierte vCard einlesen
    person = PersonVO()  # Person zum Auffüllen der vCard-Werte instanziieren
    addresses = []
    cell_number_fields = []
    custom_fields = []
    all_contact_groups = contact_management.get_all_contact_groups()
    # alle ContactGroup-Titel extrahieren, um beim import zu überprüfen, ob schon eine geeignete Gruppe existiert,
    # in die der Kontakt importiert werden könnte
    all_contact_group_titles = [contact_group.title for contact_group in all_contact_groups]

    # Durch die Felder der vCard iterieren, um sie in die Person einzupflegen
    for v_card_key, v_card_value in v_card.contents.items():
        if v_card_key == 'adr':
            for adr in v_card_value:
                # Standardwerte für die Adresse setzen
                street = ''
                house_number = ''
                zip_code = ''
                town = ''
                label = 'Adresse'
                if hasattr(adr.value, 'street'):
                    street = adr.value.street
                    if len(street.split(' ')) > 1 and street.strip().split(' ')[-1].isdecimal():
                        # Falls eine Hausnummer angegeben ist, Straße und Hausnummer nochmal neu berechnen
                        house_number = street.split(' ')[-1]
                        splitted_street = street.strip().split(' ')[0:-1]
                        street = ' '.join(splitted_street)
                if hasattr(adr.value, 'code'):
                    zip_code = adr.value.code  # PLZ einfügen
                if hasattr(adr.value, 'city'):
                    town = adr.value.city  # Stadt einfügen
                if hasattr(adr.value, 'type_param'):
                    label = adr.value.type_param  # label mit TYPE-Feld versehen
                # kapseln der Daten in ein AddressVO-Objekt, das später zur Person hinzugefügt wird
                addresses.append(
                    AddressVO(person=person, label=label, street=street, house_number=house_number,
                              town=town, zip_code=zip_code))

        elif v_card_key == 'tel':
            for tel in v_card_value:
                # Standardwerte setzen
                cell_number = '[Keine Angabe]'
                label = 'Telefon'
                if hasattr(tel, 'value'):
                    cell_number = tel.value
                if hasattr(tel, 'type_param'):
                    label = tel.type_param
                # kapseln der Daten in ein CellNumberFieldVO-Objekt, das später zur Person hinzugefügt wird
                cell_number_fields.append(
                    CellNumberFieldVO(label=label, cell_number=cell_number, person=person))

        elif v_card_key == 'email':
            for email in v_card_value:
                # Standardwerte für eMail-Feld setzen
                email_address = '[Keine Angabe]'
                label = 'eMail'
                # Angaben aus vCard extrahieren, falls angegeben
                if hasattr(email, 'value'):
                    email_address = email.value
                if hasattr(email, 'type_param'):
                    label = email.type_param
                # kapseln der Daten in ein CustomFieldVO-Objekt, das später zur Person hinzugefügt wird
                custom_fields.append(
                    CustomFieldVO(label=label, field_value=email_address, v_type='eMail', person=person))

        elif v_card_key == 'url':
            for url in v_card_value:
                # Standardwerte für das CustomFieldVO setzen
                url_address = '[Keine Angabe]'
                label = 'URL'
                # Angaben aus vCard extrahieren, falls angegeben
                if hasattr(url, 'value'):
                    url_address = url.value
                if hasattr(url, 'type_param'):
                    label = url.type_param
                # kapseln der Daten in ein CustomFieldVO-Objekt, das später zur Person hinzugefügt wird
                custom_fields.append(
                    CustomFieldVO(label=label, field_value=url_address, v_type='URL', person=person))

        elif v_card_key == 'nickname':
            for nickname in v_card_value:
                # Standardwerte für das CustomFieldVO setzen
                name = '[Keine Angabe]'
                label = 'Spitzname'
                # Angaben aus vCard extrahieren, falls angegeben
                if hasattr(nickname, 'value'):
                    name = nickname.value
                if hasattr(nickname, 'type_param'):
                    label = nickname.type_param
                # kapseln der Daten in ein CustomFieldVO-Objekt, das später zur Person hinzugefügt wird
                custom_fields.append(
                    CustomFieldVO(label=label, field_value=name, v_type='Spitzname', person=person))

        elif v_card_key == 'key':
            for key in v_card_value:
                # Standardwerte für das CustomFieldVO setzen
                key_value = '[Keine Angabe]'
                label = 'Key'
                # Angaben aus vCard extrahieren, falls angegeben
                if hasattr(key, 'value'):
                    key_value = key.value
                if hasattr(key, 'type_param'):
                    label = key.type_param
                # kapseln der Daten in ein CustomFieldVO-Objekt, das später zur Person hinzugefügt wird
                custom_fields.append(
                    CustomFieldVO(label=label, field_value=key_value, v_type='Public Key', person=person))

        elif v_card_key == 'gender':
            for gender in v_card_value:
                # Standardwerte für das CustomFieldVO setzen
                gender_value = '[Keine Angabe]'
                label = 'Geschlecht'

                # Angaben aus vCard extrahieren, falls angegeben
                # Geschlecht aus vCard-Standard in die interne Darstellung konvertieren
                if hasattr(gender, 'value'):
                    if gender.value == 'M':
                        gender_value = 'maennlich'
                    elif gender.value == 'F':
                        gender_value = 'weiblich'
                    elif gender.value == 'O':
                        gender_value = 'divers'
                    else:
                        gender_value = gender.value

                # kapseln der Daten in ein CustomFieldVO-Objekt, das später zur Person hinzugefügt wird
                custom_fields.append(
                    CustomFieldVO(label=label, field_value=gender_value, v_type='Geschlecht',
                                  person=person))

        elif v_card_key == 'hobby':
            for hobby in v_card_value:
                # Standardwerte für das CustomFieldVO setzen
                hobby_value = '[Keine Angabe]'
                label = 'Hobby'

                # Angaben aus vCard extrahieren, falls angegeben
                if hasattr(hobby, 'value'):
                    hobby_value = hobby.value
            # kapseln der Daten in ein CustomFieldVO-Objekt, das später zur Person hinzugefügt wird
            custom_fields.append(
                CustomFieldVO(label=label, field_value=hobby_value, v_type='Hobby', person=person))

        elif v_card_key == 'n':
            for name in v_card_value:

                # Angaben aus vCard extrahieren, falls angegeben
                if hasattr(name.value, 'prefix') and name.value.prefix:
                    # Titel in ein CustomField konvertieren
                    custom_fields.append(
                        CustomFieldVO(label='Titel', field_value=name.value.prefix, v_type='Titel',
                                      person=person))
                if hasattr(name.value, 'family'):
                    person.last_name = name.value.family
                if hasattr(name.value, 'given'):
                    person.first_name = name.value.given

        elif v_card_key == 'org':
            for org in v_card_value:
                org_name = '[Keine Angabe]'

                # Angaben aus vCard extrahieren, falls angegeben
                if hasattr(org, 'value'):
                    if type(org.value) == str:
                        org_name = org.value.replace(';', ', ')  # vCard-Angabe in eine benutzerfreundliche umwandeln
                    elif type(org.value) == list and len(org.value) > 0:
                        org_name = org.value[0]
                # kapseln der Daten in ein CustomFieldVO-Objekt, das später zur Person hinzugefügt wird
                custom_fields.append(
                    CustomFieldVO(label='Firma', field_value=org_name, v_type='Firma', person=person))

        elif v_card_key == 'keiner':
            for no_type in v_card_value:
                field_value = '[Keine Angabe]'
                label = '[Keine Angabe]'

                # Angaben aus vCard extrahieren, falls angegeben
                if hasattr(no_type, 'value'):
                    field_value = no_type.value
                if hasattr(no_type, 'type_param'):
                    label = no_type.type_param
                # kapseln der Daten in ein CustomFieldVO-Objekt, das später zur Person hinzugefügt wird
                custom_fields.append(
                    CustomFieldVO(label=label, field_value=field_value, v_type=None, person=person))

        elif v_card_key == 'bday':
            for bday in v_card_value:
                if bday.value.isdecimal():
                    # Falls Geburtsdatum in Zahlenformat angegeben ist, den Wert einfach übernehmen (str -> int)
                    person.birthdate = int(bday.value)
                else:
                    try:
                        # Falls nicht, ausgeschriebene Datumsangabe in einen Zeitstempel (int) konvertieren
                        person.birthdate = int(datetime.strptime(bday.value, '%Y-%m-%d').timestamp())
                    except ValueError as err:
                        print('Birthdate could not be converted into datetime respectively into int' + str(err))

        elif v_card_key == 'categories':
            for category in v_card_value:
                if hasattr(category, 'value') and type(category.value) == list and bool(category.value):
                    for title in category.value:
                        if title not in all_contact_group_titles and title:
                            # sollte die Gruppe noch nicht existieren, erst eine neue erstellen
                            # und Variablen, die die Gruppenangaben enthalten aktualisieren
                            contact_management.save(ContactGroupVO(title=title))
                            all_contact_groups = contact_management.get_all_contact_groups()
                            all_contact_group_titles = [contact_group.title for contact_group in all_contact_groups]

                        # Der Person der ContactGroup zuordnen, auf die der Titel passt (auch wenn diese gleichnamig sind)
                        for contact_group in all_contact_groups:
                            if contact_group.title == title:
                                person.add(contact_group)

        elif v_card_key == 'version' or v_card_key == 'fn':
            pass  # Version und fn Felder ignorieren

        else:
            for value in v_card_value:
                # Weitere vCard-Felder einfügen, die das Programm nicht in eigene Typen umsetzen kann
                if type(v_card_value) == str:
                    label = 'Label'
                    field_value = 'Eigener Wert'
                    if hasattr(value, 'value'):
                        field_value = value.value
                    if hasattr(value, 'type_param'):
                        label = value.type_param

                    custom_fields.append(CustomFieldVO(label=label, field_value=field_value,
                                                       v_type=v_card_key.replace('-', ' '), person=person))

    # Person mit den gesammelten Daten versehen
    person.addresses = addresses
    person.cell_number_fields = cell_number_fields
    person.custom_fields = custom_fields
    contact_management.save(person)


if __name__ == '__main__':
    # v_card = get_serialized_person(contact_management.get_all_persons()[0])
    import_person('')
