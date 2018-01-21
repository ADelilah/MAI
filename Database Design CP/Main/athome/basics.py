import psycopg2

def condb():
    #connects to DB returning cursor and message

    try:
        conn = psycopg2.connect("dbname='athome' user='Delilah' host='localhost' password='desophie'")
        return conn
    except:
        print ("Basics: can't connect to DB")
        return [None]

def get_username(id):
    #getting user's display name

    conn=condb()
    if not conn:
        return None
    cur = conn.cursor()

    try:
        cur.execute("""SELECT display_name FROM citizens WHERE citizen_id=%s;""", [id])
        [(dname,)]= cur.fetchall()
        conn.close()
        return dname
    except:
        conn.rollback()
        conn.close()
        print("Basics: can't get display name from DB")
        return None

def get_title(act_id):
    #getting user's display name

    conn=condb()
    if not conn:
        return None
    cur = conn.cursor()

    try:
        cur.execute("""SELECT act_title FROM activities WHERE act_id=%s;""", [act_id])
        [(title,)]= cur.fetchall()
        conn.close()
        return title
    except:
        conn.rollback()
        conn.close()
        print("Basics: can't get activity title from DB")
        return None


def phone_validation(phone):
    #returns clean 10-digit number (or error)

    phone = phone.replace(" ", "")
    phone = phone.replace(".", "")
    phone = phone.replace("-", "")
    phone = phone.replace("+", "")
    phone = phone.replace(")", "")
    phone = phone.replace("(", "")
    try:
        x = int(phone)  # check if it's numbers
        if 999999999 < x < 10000000000:
            return phone
    except:
        return None




#def errors_adjust(form):
#    errors = 'Please, enter correct'
#    for fieldName, errorMessages in form.errors.items():
#        for err in errorMessages:
#            err = err.replace(" ", "")
#            err = err.replace("Invalid", "")
#            errors = errors + ", " + err
#        errors = errors.replace("correct,", "correct")

