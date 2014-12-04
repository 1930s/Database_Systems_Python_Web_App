from flask import Response

__author__ = 'RR1'

import bcrypt
import easypg

def compare_unpw(username, pw_challenge):
    """
    Compares the password given to the hashed version in the database
    :param username: The username for which to authenticate against.
    :param pw_challenge: The password to challenge authentication.
    :return:
    """

    with easypg.cursor() as cur:
        cur.execute('''
            SELECT password
            FROM users
            WHERE username = %s
        ''', (username, ))

        # See this page for more information http://www.tutorialspoint.com/python/python_tuples.htm
        user_info = cur.fetchone()
        if user_info is None:
            return False
        else:
            #for row in user_info:
             #   print row
            pw = user_info[0]

            if bcrypt.hashpw(pw_challenge, pw) == pw:
                return True
            else:
                return False


def encrypt_password(password):
    return bcrypt.hashpw(password, bcrypt.gensalt())


def add_user(cur, username, password, email):
    """
    Add the user to the database.
    :param username: Username to add.
    :param password: Password to add.
    :param email: Email address to add.
    :param dob: Date of Birth to add.
    :return:
    """
    cur.execute('''
        INSERT INTO users (username, password, email, dob, user_role, start_date, last_login, end_date)
        VALUES (%s, %s, %s, current_date, 1 , current_date, current_timestamp, null);
        COMMIT;
    ''', (username, encrypt_password(password), email))
    return None


def get_all_user_list(cur, page, user_id):
    """
    Get all lists user_id has stored in database .
    :param cur: the database cursor
    :return: a list of dictionaries of article IDs and titles
    """

    cur.execute('''
        SELECT list_title
        FROM lists
        WHERE created_by = user_id %s
    ''', ((page - 1) * 50,))
    user_list = []
    for list_title in cur:
         user_list.append({'lists_tile': list_title })
    return  user_list


def search_books_title(cur, query):
    cur.execute('''
        SELECT title_id, title
        FROM titles
        WHERE title @@ plainto_tsquery(%s)
        ORDER BY title DESC, title
    ''', (query, ))

    article_info = []
    for title_id, title in cur:
        article_info.append({'id': title_id, 'title': title})

    return article_info


def search_books_author(cur, query):
    cur.execute('''
        SELECT titles.title_id, titles.title
        FROM titles
        JOIN editions ON (editions.title_id = titles.title_id)
        JOIN editions_authors ON (editions_authors.edition_id = editions.edition_id)
        JOIN authors ON (authors.author_id = editions_authors.author_id)
        WHERE author_name @@ plainto_tsquery(%s)
        ORDER BY titles.title DESC, titles.title
    ''', (query, ))

    article_info = []
    for title_id, title in cur:
        article_info.append({'id': title_id, 'title': title})

    return article_info
