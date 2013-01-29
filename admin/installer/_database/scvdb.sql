CREATE DATABASE '%(NAME)s.fdb';
DEFAULT CHARACTER SET UTF8;
/********************* ROLES **********************/

CREATE ROLE RDB$ADMIN;
/********************* UDFS ***********************/

/****************** GENERATORS ********************/

CREATE GENERATOR ACT_GEN;
CREATE GENERATOR ATL_GEN;
CREATE GENERATOR CSS_GEN;
CREATE GENERATOR GEN_OPERATIONS_ID;
CREATE GENERATOR MDT_GEN;
CREATE GENERATOR MNI_GEN;
CREATE GENERATOR MNU_GEN;
CREATE GENERATOR MOD_GEN;
CREATE GENERATOR OPE_GEN;
CREATE GENERATOR REP_GEN;
CREATE GENERATOR RIG_GEN;
CREATE GENERATOR ROL_GEN;
CREATE GENERATOR SIT_GEN;
CREATE GENERATOR USR_GEN;
CREATE GENERATOR WGT_GEN;
/******************** DOMAINS *********************/

CREATE DOMAIN BOOL
 AS Smallint
 NOT NULL
 check (value = 0 or value = 1)
;

/******************** TABLES **********************/

CREATE TABLE ACTIONLISTS
(
  ATL_ID Integer NOT NULL,
  ATL_NAME Varchar(64),
  CONSTRAINT ATL_PK PRIMARY KEY (ATL_ID)
);
CREATE TABLE ACTIONS
(
  ACT_ID Integer NOT NULL,
  ACT_NAME Varchar(64),
  ACT_ATL_ID Integer,
  ACT_SIT_ID Integer,
  ACT_SPACE Integer,
  ACT_WGT_ID Integer,
  ACT_URL Varchar(1024),
  ACT_ORDER Integer NOT NULL,
  CONSTRAINT ACT_PK PRIMARY KEY (ACT_ID),
  CONSTRAINT ACI_UNI_ORDER UNIQUE (ACT_ATL_ID,ACT_ORDER)
);
CREATE TABLE CONFIG
(
  PARAM Varchar(32) NOT NULL,
  VAL Varchar(1024) NOT NULL,
  PRIMARY KEY (PARAM)
);
CREATE TABLE CSS
(
  CSS_ID Integer NOT NULL,
  CSS_SELECTOR Varchar(15) NOT NULL,
  CSS_MOD_ID Integer,
  CSS_WGT_ID Integer,
  CSS_SESSION Varchar(32),
  CSS_TAG Varchar(20) NOT NULL,
  CSS_VALUE Varchar(50) NOT NULL,
  CONSTRAINT CSS_PK PRIMARY KEY (CSS_ID),
  CONSTRAINT CSS_UNI_SELECTOR UNIQUE (CSS_SELECTOR,CSS_MOD_ID,CSS_WGT_ID,CSS_SESSION,CSS_TAG)
);
CREATE TABLE CSSSESSION
(
  CSE_SESSION Varchar(32) NOT NULL,
  CSE_FILE Varchar(50) NOT NULL,
  CSE_OUTDATED BOOL,
  CONSTRAINT PK_CSSSESSION PRIMARY KEY (CSE_SESSION,CSE_FILE)
);
CREATE TABLE MENUITEMS
(
  MNI_ID Integer NOT NULL,
  MNI_NAME Varchar(64),
  MNI_MNU_ID Integer,
  MNI_MNI_ID Integer,
  MNI_ATL_ID Integer,
  MNI_ORDER Integer NOT NULL,
  CONSTRAINT MNI_PK PRIMARY KEY (MNI_ID)
);
CREATE TABLE MENUS
(
  MNU_ID Integer NOT NULL,
  MNU_NAME Varchar(64),
  MNU_SIT_ID Integer DEFAULT NULL,
  CONSTRAINT MNU_PK PRIMARY KEY (MNU_ID)
);
CREATE TABLE MODULES
(
  MOD_ID Integer NOT NULL,
  MOD_NAME Varchar(64),
  MOD_DISPLAYNAME Varchar(64),
  MOD_VERSIONMAJOR Integer,
  MOD_VERSIONMINOR Integer,
  MOD_VERSIONREV Integer,
  MOD_MD5 Varchar(32),
  MOD_REP_ID Integer,
  CONSTRAINT MOD_PK PRIMARY KEY (MOD_ID),
  CONSTRAINT MOD_UNI_NAME UNIQUE (MOD_NAME,MOD_VERSIONMAJOR,MOD_VERSIONMINOR,MOD_VERSIONREV)
);
CREATE TABLE MODULETABLES
(
  MDT_ID Integer NOT NULL,
  MDT_NAME Varchar(64),
  MDT_MOD_ID Integer,
  CONSTRAINT MDT_PK PRIMARY KEY (MDT_ID),
  CONSTRAINT MDT_UNI_NAME UNIQUE (MDT_NAME)
);
CREATE TABLE OPERATIONDATA
(
  OPD_OPE_ID Integer NOT NULL,
  OPD_KEY Varchar(64) NOT NULL,
  OPD_VALUE Varchar(512) NOT NULL,
  OPD_TYPE Varchar(16) NOT NULL,
  CONSTRAINT PK_OPERATIONDATA PRIMARY KEY (OPD_OPE_ID,OPD_KEY)
);
CREATE TABLE OPERATIONS
(
  OPE_ID Integer NOT NULL,
  OPE_OPE_PARENT Integer,
  OPE_INVOKED Timestamp NOT NULL,
  OPE_TYPE Varchar(64) NOT NULL,
  OPE_STATUS Integer DEFAULT 0 NOT NULL,
  CONSTRAINT PK_OPERATIONS PRIMARY KEY (OPE_ID)
);
CREATE TABLE REPOSITORIES
(
  REP_ID Integer NOT NULL,
  REP_NAME Varchar(64),
  REP_IP Varchar(32),
  REP_PORT Integer DEFAULT 80,
  REP_LASTUPDATE Timestamp,
  REP_PUBLICKEY Varchar(1024) NOT NULL,
  CONSTRAINT REP_PK PRIMARY KEY (REP_ID),
  CONSTRAINT REP_UNI_IPPORT UNIQUE (REP_ID,REP_PORT)
);
CREATE TABLE RIGHTS
(
  RIG_ID Integer NOT NULL,
  RIG_NAME Varchar(64),
  CONSTRAINT RIG_PK PRIMARY KEY (RIG_ID),
  CONSTRAINT RIG_UNI_NAME UNIQUE (RIG_NAME)
);
CREATE TABLE ROLERIGHTS
(
  RRI_ROL_ID Integer NOT NULL,
  RRI_RIG_ID Integer NOT NULL,
  CONSTRAINT RRI_PK PRIMARY KEY (RRI_ROL_ID,RRI_RIG_ID)
);
CREATE TABLE ROLES
(
  ROL_ID Integer NOT NULL,
  ROL_NAME Varchar(64),
  CONSTRAINT ROL_PK PRIMARY KEY (ROL_ID),
  CONSTRAINT ROL_UNI_NAME UNIQUE (ROL_NAME)
);
CREATE TABLE SITES
(
  SIT_ID Integer NOT NULL,
  SIT_NAME Varchar(64),
  SIT_MNU_ID Integer,
  SIT_HTML Blob sub_type 1,
  SIT_DESCRIPTION Varchar(500),
  SIT_SPACES Integer,
  SIT_FILENAME Varchar(255),
  SIT_DEFAULT BOOL,
  CONSTRAINT SIT_PK PRIMARY KEY (SIT_ID),
  CONSTRAINT SIT_UNI_NAME UNIQUE (SIT_NAME)
);
CREATE TABLE USERRIGHTS
(
  URI_USR_ID Integer NOT NULL,
  URI_RIG_ID Integer NOT NULL,
  CONSTRAINT URI_PK PRIMARY KEY (URI_USR_ID,URI_RIG_ID)
);
CREATE TABLE USERROLES
(
  URO_USR_ID Integer NOT NULL,
  URO_ROL_ID Integer NOT NULL,
  CONSTRAINT URO_PK PRIMARY KEY (URO_USR_ID,URO_ROL_ID)
);
CREATE TABLE USERS
(
  USR_ID Integer NOT NULL,
  USR_NAME Varchar(64),
  USR_PASSWORD Varchar(128) NOT NULL,
  USR_SALT Varchar(128) NOT NULL,
  CONSTRAINT USR_PK PRIMARY KEY (USR_ID),
  CONSTRAINT USR_UNI_NAME UNIQUE (USR_NAME)
);
CREATE TABLE WIDGETS
(
  WGT_ID Integer NOT NULL,
  WGT_NAME Varchar(64),
  WGT_SIT_ID Integer,
  WGT_MOD_ID Integer,
  WGT_SPACE Integer,
  CONSTRAINT WGT_PK PRIMARY KEY (WGT_ID)
);
/********************* VIEWS **********************/

/******************* EXCEPTIONS *******************/

/******************** TRIGGERS ********************/

SET TERM ^ ;
CREATE TRIGGER CSS_AUTOINCREMENT FOR CSS ACTIVE
BEFORE INSERT POSITION 0
as
declare variable tmp decimal(18,0);
begin
  if (new.css_id is null) then
    new.css_id = gen_id(css_gen, 1);
  else
  begin
    tmp = gen_id(css_gen, 0);
    if (tmp < new.css_id) then
      tmp = gen_id(css_gen, new.css_id-tmp);
  end
end^
SET TERM ; ^
SET TERM ^ ;
CREATE TRIGGER OPERATIONS_BI FOR OPERATIONS ACTIVE
BEFORE INSERT POSITION 0
AS
DECLARE VARIABLE tmp DECIMAL(18,0);
BEGIN
  IF (NEW.OPE_ID IS NULL) THEN
    NEW.OPE_ID = GEN_ID(GEN_OPERATIONS_ID, 1);
  ELSE
  BEGIN
    tmp = GEN_ID(GEN_OPERATIONS_ID, 0);
    if (tmp < new.OPE_ID) then
      tmp = GEN_ID(GEN_OPERATIONS_ID, new.OPE_ID-tmp);
  END
END^
SET TERM ; ^

ALTER TABLE ACTIONS ADD CONSTRAINT ACT_FK_ATL
  FOREIGN KEY (ACT_ATL_ID) REFERENCES ACTIONLISTS (ATL_ID) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ACTIONS ADD CONSTRAINT ACT_FK_SIT
  FOREIGN KEY (ACT_SIT_ID) REFERENCES SITES (SIT_ID) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ACTIONS ADD CONSTRAINT ACT_FK_WGT
  FOREIGN KEY (ACT_WGT_ID) REFERENCES WIDGETS (WGT_ID) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE CSS ADD CONSTRAINT CSS_FK_MOD
  FOREIGN KEY (CSS_MOD_ID) REFERENCES MODULES (MOD_ID) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE CSS ADD CONSTRAINT CSS_FK_WGT
  FOREIGN KEY (CSS_WGT_ID) REFERENCES WIDGETS (WGT_ID) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE MENUITEMS ADD CONSTRAINT MNI_FK_ATL
  FOREIGN KEY (MNI_ATL_ID) REFERENCES ACTIONLISTS (ATL_ID) ON UPDATE CASCADE ON DELETE SET NULL;
ALTER TABLE MENUITEMS ADD CONSTRAINT MNI_FK_MNI
  FOREIGN KEY (MNI_MNI_ID) REFERENCES MENUITEMS (MNI_ID) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE MENUITEMS ADD CONSTRAINT MNI_FK_MNU
  FOREIGN KEY (MNI_MNU_ID) REFERENCES MENUS (MNU_ID) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE MODULES ADD CONSTRAINT MOD_FK_REP
  FOREIGN KEY (MOD_REP_ID) REFERENCES REPOSITORIES (REP_ID) ON UPDATE CASCADE ON DELETE SET NULL;
ALTER TABLE MODULETABLES ADD CONSTRAINT MDT_FK_MOD
  FOREIGN KEY (MDT_MOD_ID) REFERENCES MODULES (MOD_ID) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE OPERATIONDATA ADD CONSTRAINT FK_OPERATIONDATA_1
  FOREIGN KEY (OPD_OPE_ID) REFERENCES OPERATIONS (OPE_ID) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ROLERIGHTS ADD CONSTRAINT RRI_FK_RIG
  FOREIGN KEY (RRI_RIG_ID) REFERENCES RIGHTS (RIG_ID) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ROLERIGHTS ADD CONSTRAINT RRI_FK_ROL
  FOREIGN KEY (RRI_ROL_ID) REFERENCES ROLES (ROL_ID) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE SITES ADD CONSTRAINT SIT_FK_MNU
  FOREIGN KEY (SIT_MNU_ID) REFERENCES MENUS (MNU_ID) ON UPDATE CASCADE ON DELETE SET NULL;
ALTER TABLE USERRIGHTS ADD CONSTRAINT URI_PK_RIG
  FOREIGN KEY (URI_RIG_ID) REFERENCES RIGHTS (RIG_ID) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE USERRIGHTS ADD CONSTRAINT URI_PK_USR
  FOREIGN KEY (URI_USR_ID) REFERENCES USERS (USR_ID) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE USERROLES ADD CONSTRAINT URO_FK_ROL
  FOREIGN KEY (URO_ROL_ID) REFERENCES ROLES (ROL_ID) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE USERROLES ADD CONSTRAINT URO_FK_USR
  FOREIGN KEY (URO_USR_ID) REFERENCES USERS (USR_ID) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE WIDGETS ADD CONSTRAINT WGT_FK_MOD
  FOREIGN KEY (WGT_MOD_ID) REFERENCES MODULES (MOD_ID) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE WIDGETS ADD CONSTRAINT WGT_FK_SIT
  FOREIGN KEY (WGT_SIT_ID) REFERENCES SITES (SIT_ID) ON UPDATE CASCADE ON DELETE CASCADE;


GRANT DELETE, INSERT, REFERENCES, SELECT, UPDATE
 ON ACTIONLISTS TO  %(USER)s WITH GRANT OPTION;

GRANT DELETE, INSERT, REFERENCES, SELECT, UPDATE
 ON ACTIONS TO  %(USER)s WITH GRANT OPTION;

GRANT DELETE, INSERT, REFERENCES, SELECT, UPDATE
 ON CONFIG TO  %(USER)s WITH GRANT OPTION;

GRANT DELETE, INSERT, REFERENCES, SELECT, UPDATE
 ON CSS TO  %(USER)s WITH GRANT OPTION;

GRANT DELETE, INSERT, REFERENCES, SELECT, UPDATE
 ON CSSSESSION TO  %(USER)s WITH GRANT OPTION;

GRANT DELETE, INSERT, REFERENCES, SELECT, UPDATE
 ON MENUITEMS TO  %(USER)s WITH GRANT OPTION;

GRANT DELETE, INSERT, REFERENCES, SELECT, UPDATE
 ON MENUS TO  %(USER)s WITH GRANT OPTION;

GRANT DELETE, INSERT, REFERENCES, SELECT, UPDATE
 ON MODULES TO  %(USER)s WITH GRANT OPTION;

GRANT DELETE, INSERT, REFERENCES, SELECT, UPDATE
 ON MODULETABLES TO  %(USER)s WITH GRANT OPTION;

GRANT DELETE, INSERT, REFERENCES, SELECT, UPDATE
 ON OPERATIONDATA TO  %(USER)s WITH GRANT OPTION;

GRANT DELETE, INSERT, REFERENCES, SELECT, UPDATE
 ON OPERATIONS TO  %(USER)s WITH GRANT OPTION;

GRANT DELETE, INSERT, REFERENCES, SELECT, UPDATE
 ON REPOSITORIES TO  %(USER)s WITH GRANT OPTION;

GRANT DELETE, INSERT, REFERENCES, SELECT, UPDATE
 ON RIGHTS TO  %(USER)s WITH GRANT OPTION;

GRANT DELETE, INSERT, REFERENCES, SELECT, UPDATE
 ON ROLERIGHTS TO  %(USER)s WITH GRANT OPTION;

GRANT DELETE, INSERT, REFERENCES, SELECT, UPDATE
 ON ROLES TO  %(USER)s WITH GRANT OPTION;

GRANT DELETE, INSERT, REFERENCES, SELECT, UPDATE
 ON SITES TO  %(USER)s WITH GRANT OPTION;

GRANT DELETE, INSERT, REFERENCES, SELECT, UPDATE
 ON USERRIGHTS TO  %(USER)s WITH GRANT OPTION;

GRANT DELETE, INSERT, REFERENCES, SELECT, UPDATE
 ON USERROLES TO  %(USER)s WITH GRANT OPTION;

GRANT DELETE, INSERT, REFERENCES, SELECT, UPDATE
 ON USERS TO  %(USER)s WITH GRANT OPTION;

GRANT DELETE, INSERT, REFERENCES, SELECT, UPDATE
 ON WIDGETS TO  %(USER)s WITH GRANT OPTION;

INSERT INTO USERS (USR_ID, USR_NAME, USR_PASSWORD, USR_SALT)
 VALUES (1, 'root', '%(PASSWORD)s', '%(SALT)s');

INSERT INTO RIGHTS (RIG_ID, RIG_NAME) VALUES (1, 'scoville.manageserverdata');
INSERT INTO RIGHTS (RIG_ID, RIG_NAME) VALUES (2, 'scoville.users.create');
INSERT INTO RIGHTS (RIG_ID, RIG_NAME) VALUES (3, 'scoville.users.delete');
INSERT INTO RIGHTS (RIG_ID, RIG_NAME) VALUES (4, 'scoville.users.modify');
INSERT INTO RIGHTS (RIG_ID, RIG_NAME) VALUES (5, 'scoville.users.grant_revoke');
INSERT INTO RIGHTS (RIG_ID, RIG_NAME) VALUES (6, 'scoville.roles.create');
INSERT INTO RIGHTS (RIG_ID, RIG_NAME) VALUES (7, 'scoville.roles.delete');
INSERT INTO RIGHTS (RIG_ID, RIG_NAME) VALUES (8, 'scoville.roles.modify');
INSERT INTO RIGHTS (RIG_ID, RIG_NAME) VALUES (9, 'scoville.modules.install');
INSERT INTO RIGHTS (RIG_ID, RIG_NAME) VALUES (10, 'scoville.modules.uninstall');
INSERT INTO RIGHTS (RIG_ID, RIG_NAME) VALUES (11, 'scoville.modules.enter_repo');
INSERT INTO RIGHTS (RIG_ID, RIG_NAME) VALUES (12, 'scoville.modules.erase_repo');
INSERT INTO RIGHTS (RIG_ID, RIG_NAME) VALUES (13, 'scoville.sites.create');
INSERT INTO RIGHTS (RIG_ID, RIG_NAME) VALUES (14, 'scoville.sites.delete');
INSERT INTO RIGHTS (RIG_ID, RIG_NAME) VALUES (15, 'scoville.sites.modify');
INSERT INTO RIGHTS (RIG_ID, RIG_NAME) VALUES (16, 'scoville.widget.create');
INSERT INTO RIGHTS (RIG_ID, RIG_NAME) VALUES (17, 'scoville.widget.delete');
INSERT INTO RIGHTS (RIG_ID, RIG_NAME) VALUES (18, 'scoville.widget.modify');
INSERT INTO RIGHTS (RIG_ID, RIG_NAME) VALUES (19, 'scoville.users.view');
INSERT INTO RIGHTS (RIG_ID, RIG_NAME) VALUES (20, 'scoville.roles.view');
INSERT INTO RIGHTS (RIG_ID, RIG_NAME) VALUES (21, 'scoville.css.edit');

INSERT INTO ROLES (ROL_ID, ROL_NAME) VALUES (1,'admin');

INSERT INTO ROLERIGHTS (RRI_ROL_ID, RRI_RIG_ID) VALUES (1,1);
INSERT INTO ROLERIGHTS (RRI_ROL_ID, RRI_RIG_ID) VALUES (1,2);
INSERT INTO ROLERIGHTS (RRI_ROL_ID, RRI_RIG_ID) VALUES (1,3);
INSERT INTO ROLERIGHTS (RRI_ROL_ID, RRI_RIG_ID) VALUES (1,4);
INSERT INTO ROLERIGHTS (RRI_ROL_ID, RRI_RIG_ID) VALUES (1,5);
INSERT INTO ROLERIGHTS (RRI_ROL_ID, RRI_RIG_ID) VALUES (1,6);
INSERT INTO ROLERIGHTS (RRI_ROL_ID, RRI_RIG_ID) VALUES (1,7);
INSERT INTO ROLERIGHTS (RRI_ROL_ID, RRI_RIG_ID) VALUES (1,8);
INSERT INTO ROLERIGHTS (RRI_ROL_ID, RRI_RIG_ID) VALUES (1,9);
INSERT INTO ROLERIGHTS (RRI_ROL_ID, RRI_RIG_ID) VALUES (1,10);
INSERT INTO ROLERIGHTS (RRI_ROL_ID, RRI_RIG_ID) VALUES (1,11);
INSERT INTO ROLERIGHTS (RRI_ROL_ID, RRI_RIG_ID) VALUES (1,12);
INSERT INTO ROLERIGHTS (RRI_ROL_ID, RRI_RIG_ID) VALUES (1,13);
INSERT INTO ROLERIGHTS (RRI_ROL_ID, RRI_RIG_ID) VALUES (1,14);
INSERT INTO ROLERIGHTS (RRI_ROL_ID, RRI_RIG_ID) VALUES (1,15);
INSERT INTO ROLERIGHTS (RRI_ROL_ID, RRI_RIG_ID) VALUES (1,16);
INSERT INTO ROLERIGHTS (RRI_ROL_ID, RRI_RIG_ID) VALUES (1,17);
INSERT INTO ROLERIGHTS (RRI_ROL_ID, RRI_RIG_ID) VALUES (1,18);
INSERT INTO ROLERIGHTS (RRI_ROL_ID, RRI_RIG_ID) VALUES (1,19);
INSERT INTO ROLERIGHTS (RRI_ROL_ID, RRI_RIG_ID) VALUES (1,20);
INSERT INTO ROLERIGHTS (RRI_ROL_ID, RRI_RIG_ID) VALUES (1,21);

INSERT INTO USERROLES (URO_ROL_ID, URO_USR_ID) VALUES (1,1);

INSERT INTO REPOSITORIES VALUES (1,'%(REPO)s','%(REPO)s',80,NULL,'');

INSERT INTO SITES VALUES (1, 'Mainsite', NULL, '<div id=\"h1\"><div id=\"s1\"></div></div><div id=\"h2\"><div id=\"s2\"><div id=\"v1\"></div><div id=\"s3\"></div></div><div id=\"v2\"><div id=\"s4\"></div></div><div id=\"v3\"><div id=\"s5\"></div></div></div><div id=\"h3\"><div id=\"template_bottom\"><span>This Site is using Scoville </span> <span style=\"color:#f00;\">&lt;</span><span style=\"color:#0f0;\">}-</span><span> a CMS by masterprogs &copy; 2011</span></div></div>', 'Mainsite for Content', 5, 'mainsite.html', 1);

SET GENERATOR REP_GEN TO 1;
SET GENERATOR SIT_GEN TO 1;
SET GENERATOR USR_GEN TO 1;
SET GENERATOR ROL_GEN TO 1;
SET GENERATOR RIG_GEN TO 21;
