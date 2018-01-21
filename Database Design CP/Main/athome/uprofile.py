import psycopg2
from athome import basics

problem = "Error. Please, check your internet connection and try again later"


class UserData:
    def __init__(self, fullname, nickname, code, phone, lat, long, photo):
        self.f = fullname
        self.n = nickname
        self.c = code
        self.p = phone
        self.la = lat
        self.lo = long
        self.ph = photo


def show_profile(id):
    # returns user data (or error)
    conn = basics.condb()
    if not conn:
        return [None, problem]

    cur = conn.cursor()
    try:
        cur.execute("""SELECT citizen_name as fullname, display_name as nickname,
                        code_region as code, phone, ST_Y(home::geometry) as latitude,
                        ST_X(home::geometry) As longitude, photo as photo
                        FROM citizens WHERE citizen_id=%s;""", [id])
        res=cur.fetchall()
        conn.close()
        [tup]=res
        userdata = UserData(tup[0], tup[1], tup[2], tup[3], tup[4], tup[5], tup[6])
        return [userdata, None]
    except:
        conn.rollback()
        conn.close()
        print("Uprofile: can't show user data")
        return [None, problem]


def edit_profile(userdata, newdata, id, pc, dnc): #pc = phone changed, dnc = display name changed
    # returns true/false (and/or 1/2 errors)

    conn = basics.condb()
    if not conn:
        return [False, False, problem]

    cur = conn.cursor()

    progress = ""

    if pc:
        try: #check for another user with the number we wanna add
            cur.execute("""SELECT citizen_id FROM citizens
                            WHERE phone=%s AND code_region =%s AND citizen_id !=%s;""", [newdata.p, newdata.c, id])
            res=cur.fetchall()

            if res:     #keeping old phone
                newdata.p = userdata.p
                newdata.c = userdata.c
                progress = progress + "Phone number belongs to another user.\nIf it's your's, please, login as that user.\n"
        except:
            conn.rollback()
            conn.close()
            print ("Uprofile: can't check if phone is occupied")
            return [False, False, problem]

    if dnc:
        try: #check if display name is free
            cur.execute("""SELECT citizen_id FROM citizens
                            WHERE display_name=%s AND citizen_id!=%s;""", [newdata.n, id])
            res = cur.fetchall()

            if res:
                newdata.n = userdata.n #keeping old display name
                progress = progress + "Display name is taken, please, choose another one"

        except:
            conn.rollback()
            conn.close()
            print("Uprofile: can't check if display name is occupied")
            return [False, False, problem]

    #finally, updating user data
    try:
        cur.execute("""UPDATE citizens SET (citizen_name, display_name, phone, code_region,
                        home, photo)=(%s,%s,%s,%s,(ST_MakePoint(%s,%s)),%s)
                        WHERE citizen_id=%s;""", [newdata.f, newdata.n, newdata.p, newdata.c,
                                                  newdata.lo, newdata.la, newdata.ph, id])

        conn.commit()
        conn.close()
        return [True, newdata, progress]
    except:
        conn.rollback()
        conn.close()
        print("Uprofile: can't update user's record")
        return [False, False, problem]
