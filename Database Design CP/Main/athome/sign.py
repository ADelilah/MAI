import psycopg2
from athome import basics

problem = "Error. Please, check your internet connection and try again later"

def login_check(code, phone, password):
    # returns current user id (or error)

    conn = basics.condb()
    if not conn:
        return [None, problem]

    cur = conn.cursor()

    # checking
    try:
        cur.execute("""SELECT citizen_id FROM citizens
                      WHERE phone=%s AND code_region=%s AND password=%s;""", [phone, code, password])
        result = cur.fetchall()
        # if failed, checking if user exist
        if not result:
            try:
                cur.execute("""SELECT citizen_id FROM citizens
                                WHERE phone=%s AND code_region=%s;""", [phone, code])
                result2 = cur.fetchall()
                if not result2:
                    conn.rollback()
                    conn.close()
                    return [None, "Phone number doesn't exist. Please, sign up"]
                else:
                    conn.rollback()
                    conn.close()
                    return [None, "Incorrect password"]
            except:
                conn.rollback()
                conn.close()
                print("Sign: can't check if the user exist")
                return [None, problem]
        [(uid,)] = result
        conn.close()
        return [uid, None]
    except:
        conn.rollback()
        conn.close()
        print("Sign: can't check login data")
        return [None, problem]


def add_user(user_row):
    # gets a list [name, phone, code, password] and returns new id (or error)
    #using current location for now
    #so that's the only case we need to import stuff to get current location
    from urllib.request import urlopen
    import json

    # Automatically geolocate the connecting IP
    f = urlopen('http://freegeoip.net/json/')
    json_string = str(f.read())
    f.close()
    json_string = json_string.replace("b'", "")
    json_string = json_string.replace("\\n'", "")
    location = json.loads(json_string)
    lat = location['latitude']
    long = location['longitude']
    print(lat, long)

    #adding current location them to list of user data
    user_row.insert(3, long)
    user_row.insert(4, lat)
    # copying name to display name (hoping it's free)
    user_row.insert(1, user_row[0])

    conn = basics.condb()
    if not conn:
        return [None, problem]
    cur = conn.cursor()

    N = 1  # increment for display name builder below


    # trying to INSERT and return id
    while True:

        try:
            cur.execute("""INSERT INTO citizens(citizen_id, citizen_name, display_name, phone,
                        code_region, home, password)
                        VALUES (DEFAULT,%s,%s,%s,%s,(ST_MakePoint(%s,%s)),%s)
                        RETURNING citizen_id;""", user_row)

            [(uid,)] = cur.fetchall()
            conn.commit()
            return [uid, None]

        except psycopg2.IntegrityError as e:
            conn.rollback()
            conn.close()
            if e.diag.message_detail.startswith('Key (phone)'):
                return [None, "Phone number already exists. Please, sign in"]

            # if display name isn't unique, creating it
            elif e.diag.message_detail.startswith('Key (display_name)'):
                next_nickname = user_row[0] + str(' ') + str(N)
                user_row[1] = next_nickname
                N += 1
            else:
                conn.rollback()
                conn.close()
                print ("Sign: unknown integrity error - trying to insert")
                return [None, problem]
        except:
            conn.rollback()
            conn.close()
            print("Sign: can't add new user to DB :(")
            return [None, problem]
