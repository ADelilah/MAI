-- tables
-- Table: activities
CREATE TABLE activities (
    act_id integer  NOT NULL,
    citizen_id integer  NOT NULL,
    act_type_name varchar2(20)  NOT NULL,
    act_title varchar2(140)  NOT NULL,
    act_lat number(3,6)  NOT NULL,
    act_long number(3,6)  NOT NULL,
    act_date date  NOT NULL,
    act_repeat date  NULL,
    act_accessable char(1)  DEFAULT 0 NOT NULL,
    act_descript varchar2(255)  NOT NULL,
    act_img bfile  NULL,
    cit_joined smallint  NOT NULL,
    cit_comments smallint  NOT NULL,
    CONSTRAINT activities_pk PRIMARY KEY (act_id)
) ;

-- Table: activities_comments
CREATE TABLE activities_comments (
    act_comment_id integer  NOT NULL,
    act_id integer  NOT NULL,
    citizen_id integer  NOT NULL,
    act_comment_text varchar2(255)  NOT NULL,
    CONSTRAINT activities_comments_pk PRIMARY KEY (act_comment_id)
) ;

-- Table: activities_participants
CREATE TABLE activities_participants (
    joined_id integer  NOT NULL,
    citizen_id integer  NOT NULL,
    act_id integer  NOT NULL,
    CONSTRAINT activities_participants_pk PRIMARY KEY (joined_id)
) ;

-- Table: activities_types
CREATE TABLE activities_types (
    act_type_name varchar2(20)  NOT NULL,
    act_type_def_img bfile  NOT NULL,
    CONSTRAINT activities_types_pk PRIMARY KEY (act_type_name)
) ;

-- Table: citizens
CREATE TABLE citizens (
    citizen_id integer  NOT NULL,
    citizen_name varchar2(255)  NOT NULL,
    login_name char(30)  NOT NULL,
    phone integer  NOT NULL,
    code_region smallint  NOT NULL,
    home_lat number(3,6)  NOT NULL,
    home_long number(3,6)  NOT NULL,
    password varchar2(255)  NULL,
    birthdate date  NULL,
    gender char(1)  NULL,
    photo bfile  NULL,
    fb_login varchar2(255)  NULL,
    fb_pswd varchar2(255)  NULL,
    report_anonym char(1)  DEFAULT 1 NOT NULL,
    share_routes char(1)  DEFAULT 0 NOT NULL,
    CONSTRAINT citizens_pk PRIMARY KEY (citizen_id)
) ;

-- Table: linked_trackers
CREATE TABLE linked_trackers (
    tracker_id integer  NOT NULL,
    citizen_citizen_id integer  NOT NULL,
    st_type_id varchar2(30)  NOT NULL,
    st_login varchar2(255)  NOT NULL,
    st_password varchar2(255)  NOT NULL,
    CONSTRAINT linked_trackers_pk PRIMARY KEY (tracker_id)
) ;

-- Table: supported_trackers
CREATE TABLE supported_trackers (
    st_type varchar2(30)  NOT NULL,
    CONSTRAINT supported_trackers_pk PRIMARY KEY (st_type)
) ;

-- foreign keys
-- Reference: Events_citizen (table: activities)
ALTER TABLE activities ADD CONSTRAINT Events_citizen
    FOREIGN KEY (citizen_id)
    REFERENCES citizens (citizen_id);

-- Reference: act_comments (table: activities_comments)
ALTER TABLE activities_comments ADD CONSTRAINT act_comments
    FOREIGN KEY (act_id)
    REFERENCES activities (act_id);

-- Reference: act_that_joined (table: activities_participants)
ALTER TABLE activities_participants ADD CONSTRAINT act_that_joined
    FOREIGN KEY (act_id)
    REFERENCES activities (act_id);

-- Reference: act_types (table: activities)
ALTER TABLE activities ADD CONSTRAINT act_types
    FOREIGN KEY (act_type_name)
    REFERENCES activities_types (act_type_name);

-- Reference: cit_commented (table: activities_comments)
ALTER TABLE activities_comments ADD CONSTRAINT cit_commented
    FOREIGN KEY (citizen_id)
    REFERENCES citizens (citizen_id);

-- Reference: cit_who_joined (table: activities_participants)
ALTER TABLE activities_participants ADD CONSTRAINT cit_who_joined
    FOREIGN KEY (citizen_id)
    REFERENCES citizens (citizen_id);

-- Reference: linked_trackers (table: linked_trackers)
ALTER TABLE linked_trackers ADD CONSTRAINT linked_trackers
    FOREIGN KEY (citizen_citizen_id)
    REFERENCES citizens (citizen_id);

-- Reference: tracker_type (table: linked_trackers)
ALTER TABLE linked_trackers ADD CONSTRAINT tracker_type
    FOREIGN KEY (st_type_id)
    REFERENCES supported_trackers (st_type);

-- End of file.
