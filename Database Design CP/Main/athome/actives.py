import psycopg2
from athome import basics

problem = "Error. Please, check your internet connection and try again later"
notif_dict = {'join': ' joined your activity:', 'not': ' will not participate in your activity:',
              'comm': ' commented on your activity:'}


class Activity:
    def __init__(self, id, type, user_id, title, starts, ends, lat, long,
                 descr, joined, comments, img, access):
        self.id = id
        self.ty = type
        self.uid = user_id
        self.u = basics.get_username(user_id)
        self.t = title
        self.s = starts
        self.e = ends
        self.la = lat
        self.lo = long
        self.d = descr
        self.j = joined
        self.c = comments
        self.ph = img
        self.a = access


class Comment:
    def __init__(self, user_id, posted, text, act_id):
        self.u = basics.get_username(user_id)
        self.uid = user_id
        self.t = text
        self.d = posted
        self.a = act_id


class Notification:
    def __init__(self, text, date, id):
        self.t = text
        self.d = date
        self.id = id
        self.ti = basics.get_title(id)


##########################    SHOW ACTIVITIES     ##############################


def show_actives(id):
    #returns list of activities for current user (or error)

    dist = 3000 #have no filters so far - distance from home in meters

    conn = basics.condb()
    if not conn:
        return [None, problem]

    cur = conn.cursor()

    #checking
    try:
        cur.execute("""SELECT act_id, act_type_name, citizen_id, act_title, to_char(act_start_time, 'Dy,FX Mon DD, HH24:MI'),
                        to_char(act_end_time, 'Dy,FX Mon DD, HH24:MI'), ST_Y(act_loc::geometry) as latitude,
                        ST_X(act_loc::geometry) as longitude, act_descript, cit_joined, cit_comments, act_img, accessable
                        FROM activities WHERE ST_Distance((SELECT home FROM citizens WHERE citizen_id=%s), act_loc)<=%s
                        AND act_end_time>=current_timestamp
                        ORDER BY act_start_time;""", [id, dist])
        actives = cur.fetchall()
        conn.close()
        #if not actives:
        #    return [None, "Nothing happens @Home, try to increase the distance"]
        act_list=[]
        for (i, act) in enumerate(actives):
            item = Activity(id=act[0], type=act[1], user_id=act[2], title=act[3], starts=act[4],
                            ends=act[5], lat=act[6], long=act[7], descr=act[8], joined=act[9],
                            comments=act[10], img=act[11], access=act[12])
            act_list.append(item)
        return [act_list, None]
    except:
        conn.rollback()
        conn.close()
        print ("Activities: Can't get user home location or activities list from DB")
        return [None, problem]


def single_act(act_id):
    #returns Activity for a particular activity (or error)

    conn = basics.condb()
    if not conn:
        return [None, problem]

    cur = conn.cursor()

    try:
        cur.execute("""SELECT act_id, act_type_name, citizen_id, act_title, to_char(act_start_time, 'Dy,FX Mon DD, HH24:MI'),
                        to_char(act_end_time, 'Dy,FX Mon DD, HH24:MI'), ST_Y(act_loc::geometry) as latitude,
                        ST_X(act_loc::geometry) as longitude, act_descript, cit_joined, cit_comments, act_img, accessable
                        FROM activities WHERE act_id=%s
                        ORDER BY act_start_time;""", [act_id])
        [act] = cur.fetchall()
        conn.close()
        details = Activity(id=act[0], type=act[1], user_id=act[2], title=act[3], starts=act[4],
                           ends=act[5], lat=act[6], long=act[7], descr=act[8], joined=act[9],
                           comments=act[10], img=act[11], access=act[12])
        return [details, None]
    except:
        conn.rollback()
        conn.close()
        print("Actives: can't activity details from DB")
        return [None, problem]


def get_comments(act_id):
    # returns list of comments for a particular activity (or error)

    conn = basics.condb()
    if not conn:
        return [None, problem]

    cur = conn.cursor()

    try:
        cur.execute("""SELECT citizen_id, act_comment_text, to_char(posted, 'YYYY,FX Mon DD, HH24:MI'), act_id
                        FROM activities_comments WHERE act_id=%s
                        ORDER BY posted ASC;""", [act_id])
        comments = cur.fetchall()
        if not comments:
            return [None, 'No comments yet']
        conn.close()
        comments_list = []
        for (i, com) in enumerate(comments):
            item = Comment(user_id=com[0], text=com[1], posted=com[2], act_id=com[3])
            comments_list.append(item)
        return [comments_list, None]
    except:
        conn.rollback()
        conn.close()
        print("Actives: can't get comments from DB")
        return [None, 'Error loading comments']

##########################    NOTIFICATIONS     ##############################

def show_notifs(id):
    #returns list of notifications for current user (or error)

    conn = basics.condb()
    if not conn:
        return [None, problem]

    cur = conn.cursor()

    #checking
    try:
        cur.execute("""SELECT notif_text, to_char(notif_date, 'YYYY,FX Mon DD, HH24:MI'), act_id
                        FROM notifs WHERE citizen_id=%s
                        ORDER BY notif_date DESC;""", [id])
        notifs = cur.fetchall()
        conn.close()
        #if cur.rowcount < 1:
        #    return [None, "\nYour notifications will be displayed here"]
        notif_list=[]
        for (i, notif) in enumerate(notifs):
            item = Notification(notif[0], notif[1], notif[2])
            notif_list.append(item)
        return [notif_list, None]
    except:
        conn.rollback()
        conn.close()
        print ("Notifications: Can't get notifications from DB")
        return [None, problem]


def build_notif(guest_id, action_key, act_id):
    #creates a row in notifications table and returns true/false
    # inner, so no error messages in return

    guest = basics.get_username(guest_id)
    [activ, whatever] = single_act(act_id)
    host_id = activ.uid
    act_id = activ.id
    text = guest + notif_dict.get(action_key)

    conn = basics.condb()
    if not conn or not guest:  #or not host_id:
        print("Actives: can't create notification (can't connect to DB)")
        return [False]

    cur = conn.cursor()

    try:
        cur.execute("""INSERT INTO notifs (notif_id, act_id, citizen_id, notif_text, notif_date)
                        VALUES (DEFAULT, %s, %s, %s, current_timestamp);""", [act_id, host_id, text])
        #comments = cur.fetchall()
        conn.commit()
        conn.close()
        return [True]

    except:
        conn.rollback()
        conn.close()
        print("Notifs: can't create notification")
        return [False]

##########################    ADD ACTIVITY     ##############################

def add_act(a):
    #gets Activity and creates a row in activities, returns new id (or error)
    conn = basics.condb()
    if not conn:
        return [None, problem]

    cur = conn.cursor()
    print([a.ty, a.uid, a.t, a.s, a.e, a.d,
            a.ph, a.j, a.c, a.la, a.lo, a.a]
           )
    try:
        cur.execute("""INSERT INTO activities
                        VALUES (DEFAULT, %s, %s, %s, to_timestamp(%s, 'YYYY-MM-DD HР24:MI'),
                        to_timestamp(%s, 'YYYY-MM-DD HР24:MI'), %s, %s, %s, %s, (ST_MakePoint(%s,%s)),
                        %s) RETURNING act_id;""", [a.ty, a.uid, a.t, a.s, a.e, a.d,
                                                  a.ph, a.j, a.c, a.la, a.lo, a.a])
        [(a.id,)] = cur.fetchall()
        conn.commit()
        conn.close()
        return [a.id, None]
    except:
        conn.rollback()
        conn.close()
        print("Actives: can't add activity to DB")
        return [False, problem]

##########################    JOINS AND COMMENTS     ##############################

def joined (act_id, who_id):
    # lets us now do a user participates in activity
    #returns 'yes'/'no' (or error)

    conn = basics.condb()
    if not conn:
        return [None, problem]

    cur = conn.cursor()

    cur.execute("""SELECT citizen_id FROM activities_participants
                    WHERE act_id=%s AND citizen_id=%s;""", [act_id, who_id])
    joined = cur.fetchall()
    if joined:
        return [True, None]
    else:
        return [False, None]

def join_act(act_id, who_id):
    # gets activity id and guest id, returns True/False (or error)

    conn = basics.condb()
    if not conn:
        return [None, problem]

    cur = conn.cursor()

    try:
        print(act_id, who_id)
        # row to participants
        cur.execute("""INSERT INTO activities_participants
                        VALUES (DEFAULT, %s, %s);""", [who_id, act_id])

        # upd column "joined" in activities
        cur.execute("""UPDATE activities SET (cit_joined) = (cit_joined+1) WHERE act_id=%s;""", [act_id])
        conn.commit()
        conn.close()

        # create notification
        notified = build_notif(who_id, 'join', act_id)
        if not notified:
            print("Activities: joined, but notification wasn't created")
        return [True, None]
    except:
        conn.rollback()
        conn.close()
        print("Actives: can't insert participant to DB or update count")
        return [False, problem]

def comm_act(act_id, who_id, text):
    # gets activity id, guest id and text, returns True/False (or error)

    conn = basics.condb()
    if not conn:
        return [None, problem]

    cur = conn.cursor()
    try:
        print(act_id, who_id, text)
        # row to comments
        cur.execute("""INSERT INTO activities_comments
                        VALUES (DEFAULT, %s, %s, %s, current_timestamp)""", [act_id, who_id, text])

        # upd comments count in activities
        cur.execute("""UPDATE activities SET (cit_comments) = (cit_comments+1) WHERE act_id=%s;""", [act_id])
        conn.commit()
        conn.close()

        # create notification
        try:
            build_notif(who_id, 'comm', act_id)
        except:
            print("Activities: commented, but notification wasn't created")
        return [True, None]
    except:
        conn.rollback()
        conn.close()
        print("Actives: can't insert comment to DB or update count")
        return [False, problem]

def del_comm(act_id, comm_id):
    # upd column
    # delete
    # delete notification
    pass

def unjoin(act_id, who_id):
    # upd column
    #delete row from participants
    # update
    # create notification
    pass