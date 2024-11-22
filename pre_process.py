import pandas as pd
import numpy as np 
import openpyxl

def preprocess_data(student_file, host_file):
    # Determine file format and load data
    if student_file.name.endswith('.csv'):
        students = pd.read_csv(student_file)
    elif student_file.name.endswith(('.xls', '.xlsx')):
        students = pd.read_excel(student_file)

    if host_file.name.endswith('.csv'):
        hosts = pd.read_csv(host_file)
    elif host_file.name.endswith(('.xls', '.xlsx')):
        hosts = pd.read_excel(host_file)

# hosts = pd.read_excel(r"C:\Users\akobe\OneDrive\SVE-Matching-Problem\SVE-matching-internationaux-fetes\data\hosts_anonymnous.xlsx")
# students = pd.read_excel(r"C:\Users\akobe\OneDrive\SVE-Matching-Problem\SVE-matching-internationaux-fetes\data\students_anonymnous.xlsx")
    if student_file.name.endswith('.csv') and host_file.name.endswith('.csv'):
        students.columns = students.columns.str.strip()
        hosts.columns = hosts.columns.str.strip()

        # Simplified column names for student dataframe
        student_renamed_columns = {
            'ID_stud': 'student_id',
            'Langue': 'language',
            "À quel genre vous identifiez-vous?": 'gender',
            "Dans quelle faculté étudiez-vous?": 'faculty',
            "Quel est votre programme d'études?": 'program',
            "Quel campus de l’UdeM fréquentez-vous le plus souvent?": 'main_campus',
            "Avez-vous une ou des préférences quant au type d'activité que vous souhaitez expérimenter dans le cadre du Jumelage?": 'activity_preferences',
            "À quelle(s) date(s) voudriez-vous profiter du jumelage? (Vous pouvez cocher plus d\'une date, mais vous devez alors vous engager à être disponible à toutes les journées sélectionnées).": 'preferred_dates',
            "Avez-vous accès à une voiture pour vous déplacer à l\'extérieur de Montréal?": 'car_access',
            "Quelle(s) langue(s) parlez-vous couramment?": 'languages_spoken',
            "Avez-vous des allergies et/ou un régime alimentaire particulier?": 'dietary_restrictions',
            "Si vous avez une allergie, précisez:": 'specific_allergies',
            "Avez-vous peur ou êtes-vous allergique aux animaux de compagnie?": 'pet_allergies',
            "Êtes-vous disponible pour\xa0notre évènement de rencontre «Hôtes-jumelé(s)»\xa0qui se déroulera le jeudi 5 décembre de 17h à 19h?": 'event_availability',
            "Avez-vous des demandes ou des attentes spécifiques?\xa0N\'hésitez pas à nous faire part de toute information que nous devrions prendre en considération. Ces renseignements seront traités en toute confiden": 'specific_requests',
            "Colonne1": 'column1',
            "Prefer only woman group": 'woman_group_preference',
            "ID_stud.1": 'student_id_duplicate',
            "Friends ids": 'friends_ids'
        }

        # Simplified column names for host dataframe
        host_renamed_columns = {
            'ID_host': 'host_id',
            'Heure de la dernière modification': 'last_modified_time',
            "À quel genre vous identifiez-vous?": 'gender',
            "Pour quel service/faculté/unité travaillez-vous?": 'service_faculty',
            "Veuillez préciser si vous avez sélectionné « Autre ».": 'other_specify',
            "Avez-vous participé au Jumelage du temps des Fêtes l\'année dernière (2023)?": 'past_participation',
            "Combien de personnes étudiantes internationales aimeriez-vous accueillir (minimum 2, maximum 5)?": 'num_students',
            "Que souhaitez-vous offrir comme expérience aux personnes étudiantes avec qui vous serez jumelé(e)?\xa0\n(Merci de privilégier des activités sans frais pour les personnes étudiantes)": 'offered_experience',
            "Pouvez-vous nous donner quelques détails sur l’activité que vous souhaitez proposer aux personnes étudiantes avec qui vous serez jumelé(e)?": 'activity_details',
            'À quelle(s) date(s) souhaiteriez-vous accueillir vos jumelé(e)s? (Vous pouvez cocher plus d\'une date, mais vous devez alors vous engager à être disponible toutes les journées sélectionnées.)': 'preferred_dates',
            "Quel campus de l’UdeM fréquentez-vous le plus souvent?": 'main_campus',
            "L’activité que vous proposez aura-t-elle lieu dans la grande région de Montréal, à un endroit facilement accessible en transports en commun?": 'accessible_by_transit',
            "Si non, vous engagez-vous à accompagner vos jumelé(e)s pour leurs déplacements?\u202f\xa0\n(Par exemple, en allant les chercher et les reconduire à leur domicile, au métro ou à tout autre point convenu ent...": 'transport_commitment',
            "Quelle(s) langue(s) parlez-vous couramment?": 'languages_spoken',
            "Pour certaines personnes de la communauté étudiante internationale, l\'anglais est la langue d\'usage. Êtes-vous à l\'aise de communiquer uniquement en anglais avec vos jumelé(e)s?\xa0En répondant oui, ...": 'comfortable_in_english',
            "Dans le cas où l’activité que vous proposez se passe chez vous, avez-vous un animal de compagnie à la maison?": 'pets_at_home',
            "Vous engagez-vous à respecter et à accommoder vos jumelé(e)s dans le cas où l\'activité implique de la nourriture? (Allergies, restrictions alimentaires, régime particulier)": 'food_restriction_commitment',
            "Êtes-vous disponible pour notre évènement de rencontre «hôtes-jumelé(s)» qui se déroulera le jeudi 5 décembre de 17 h à 19 h? Cet évènement sera le moment idéal pour faire connaissance.": 'event_availability',
            "Avez-vous des demandes ou des attentes spécifiques?": 'specific_requests',
            "Prefer only woman group": 'woman_group_preference'
        }

        # Rename columns in student dataframe
        students.rename(columns=student_renamed_columns, inplace=True)

        # Rename columns in host dataframe
        hosts.rename(columns=host_renamed_columns, inplace=True)

        students_clean = students[['student_id', 'language', 'gender', 'activity_preferences', 'preferred_dates', 'car_access',
            'languages_spoken', 'dietary_restrictions', 'specific_allergies',
            'pet_allergies','woman_group_preference', 'friends_ids']]
        hosts_clean = hosts[["host_id","gender", "preferred_dates","num_students","offered_experience","activity_details", "languages_spoken","accessible_by_transit", "transport_commitment","comfortable_in_english", "food_restriction_commitment","woman_group_preference", "pets_at_home"]]


        # Normalize and split lists from semicolon-separated fields
        hosts_clean['preferred_dates'] = hosts_clean['preferred_dates'].str.split(';').apply(lambda x: [i.strip() for i in x if i.strip()])
        hosts_clean['languages_spoken'] = hosts_clean['languages_spoken'].str.split(';').apply(lambda x: [i.strip() for i in x if i.strip()])
        hosts_clean['pets_at_home'] = hosts_clean['pets_at_home'].fillna("").str.split(';').apply(lambda x: [i.strip() for i in x if i.strip()])
        hosts_clean['offered_activities'] = hosts_clean['offered_experience'].str.split(';').apply(lambda x: [i.strip() for i in x if i.strip()])

        students_clean['preferred_dates'] = students_clean['preferred_dates'].str.split(';').apply(lambda x: [i.strip() for i in x if i.strip()])
        students_clean['languages_spoken'] = students_clean['languages_spoken'].str.split(';').apply(lambda x: [i.strip() for i in x if i.strip()])
        students_clean['dietary_restrictions'] = students_clean['dietary_restrictions'].fillna("").str.split(';').apply(lambda x: [i.strip() for i in x if i.strip()])
        students_clean['pet_allergies'] = students_clean['pet_allergies'].fillna("").str.split(';').apply(lambda x: [i.strip() for i in x if i.strip()])
        students_clean['preferred_activities'] = students_clean['activity_preferences'].str.split(';').apply(lambda x: [i.strip() for i in x if i.strip()])

        # students_clean.to_csv(r"C:\Users\akobe\OneDrive\SVE-Matching-Problem\SVE-matching-internationaux-fetes\data\students_clean.csv", index=False)
        # hosts_clean.to_csv(r"C:\Users\akobe\OneDrive\SVE-Matching-Problem\SVE-matching-internationaux-fetes\data\hosts_clean.csv", index=False)
        return students_clean, hosts_clean
    else:
        students.columns = students.columns.str.strip()
        hosts.columns = hosts.columns.str.strip()

        student_renamed_columns = {
        'ID_stud': 'student_id',
        'Langue': 'language',
        "À quel genre vous identifiez-vous?": 'gender',
        "Avez-vous une ou des préférences quant au type d'activité que vous souhaitez expérimenter dans le cadre du Jumelage?": 'activity_preferences',
        "À quelle(s) date(s) voudriez-vous profiter du jumelage? (Vous pouvez cocher plus d'une date, mais vous devez alors vous engager à être disponible à toutes les journées sélectionnées).": 'preferred_dates',
        "Quelle(s) langue(s) parlez-vous couramment?": 'languages_spoken',
        "Avez-vous des allergies et/ou un régime alimentaire particulier?": 'dietary_restrictions',
        "Avez-vous peur ou êtes-vous allergique aux animaux de compagnie?": 'pet_allergies',
        "Prefer only woman group": 'woman_group_preference',
        "Friends ids": 'friends_ids'
        }
        students.rename(columns=student_renamed_columns, inplace=True)

        # Clean and rename host columns
        host_renamed_columns = {
            'ID_host': 'host_id',
            "À quel genre vous identifiez-vous?": 'gender',
            "Combien de personnes étudiantes internationales aimeriez-vous accueillir (minimum 2, maximum 5)?": 'num_students',
            "Que souhaitez-vous offrir comme expérience aux personnes étudiantes avec qui vous serez jumelé(e)?\xa0\n(Merci de privilégier des activités sans frais pour les personnes étudiantes)": 'offered_experience',
            "À quelle(s) date(s) souhaiteriez-vous accueillir vos jumelé(e)s? (Vous pouvez cocher plus d'une date, mais vous devez alors vous engager à être disponible toutes les journées sélectionnées.)": 'preferred_dates',
            "Quelle(s) langue(s) parlez-vous couramment?": 'languages_spoken',
            "Pour certaines personnes de la communauté étudiante internationale, l\'anglais est la langue d\'usage. Êtes-vous à l\'aise de communiquer uniquement en anglais avec vos jumelé(e)s?\xa0En répondant oui, ...": 'comfortable_in_english',
            "Dans le cas où l’activité que vous proposez se passe chez vous, avez-vous un animal de compagnie à la maison?": 'pets_at_home',
            "Vous engagez-vous à respecter et à accommoder vos jumelé(e)s dans le cas où l\'activité implique de la nourriture? (Allergies, restrictions alimentaires, régime particulier)": 'food_restriction_commitment',
            "Prefer only woman group": 'woman_group_preference'
        }
        hosts.rename(columns=host_renamed_columns, inplace=True)

        # Select relevant columns
        students_clean = students[['student_id', 'language', 'gender', 'activity_preferences', 'preferred_dates', 'languages_spoken',
                                    'dietary_restrictions', 'pet_allergies', 'woman_group_preference', 'friends_ids']]
        hosts_clean = hosts[['host_id', 'gender','num_students', 'offered_experience', 'preferred_dates', 'languages_spoken',
                            'comfortable_in_english', 'food_restriction_commitment', 'woman_group_preference', 'pets_at_home']]

        # Normalize and split lists from semicolon-separated fields
        hosts_clean['preferred_dates'] = hosts_clean['preferred_dates'].str.split(';').apply(lambda x: [i.strip() for i in x if i.strip()])
        hosts_clean['languages_spoken'] = hosts_clean['languages_spoken'].str.split(';').apply(lambda x: [i.strip() for i in x if i.strip()])
        hosts_clean['pets_at_home'] = hosts_clean['pets_at_home'].fillna("").str.split(';').apply(lambda x: [i.strip() for i in x if i.strip()])
        hosts_clean['offered_activities'] = hosts_clean['offered_experience'].str.split(';').apply(lambda x: [i.strip() for i in x if i.strip()])

        students_clean['preferred_dates'] = students_clean['preferred_dates'].str.split(';').apply(lambda x: [i.strip() for i in x if i.strip()])
        students_clean['languages_spoken'] = students_clean['languages_spoken'].str.split(';').apply(lambda x: [i.strip() for i in x if i.strip()])
        students_clean['dietary_restrictions'] = students_clean['dietary_restrictions'].fillna("").str.split(';').apply(lambda x: [i.strip() for i in x if i.strip()])
        students_clean['pet_allergies'] = students_clean['pet_allergies'].fillna("").str.split(';').apply(lambda x: [i.strip() for i in x if i.strip()])
        students_clean['preferred_activities'] = students_clean['activity_preferences'].str.split(';').apply(lambda x: [i.strip() for i in x if i.strip()])

        return students_clean, hosts_clean
