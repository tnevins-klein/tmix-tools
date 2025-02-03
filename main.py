import sqlite3
import pathlib
import csv


def setup_table(con: sqlite3.Connection):
    cur = con.cursor()
    table_setup_statements = [
        "CREATE TABLE IF NOT EXISTS `actorGroups` (`id`	INTEGER PRIMARY KEY AUTOINCREMENT,`name`	TEXT,`data`	TEXT)",
        "CREATE TABLE IF NOT EXISTS `actorProfiles` (`actor`	INTEGER,`profile`	INTEGER,`data`	TEXT)",
        "CREATE TABLE IF NOT EXISTS `actors` (`id`	INTEGER PRIMARY KEY AUTOINCREMENT,`channel`	INTEGER,`name`	TEXT,`order`	INTEGER DEFAULT 0,`active`	INTEGER DEFAULT 0)",
        "CREATE TABLE IF NOT EXISTS `config` (`param`	TEXT,`value`	TEXT,PRIMARY KEY(param))",
        "CREATE TABLE IF NOT EXISTS `cues` (`number`	INTEGER NOT NULL DEFAULT 999,`point`	INTEGER NOT NULL DEFAULT 0,`name`	TEXT,`dca01Channels`	TEXT,`dca02Channels`	TEXT,`dca03Channels`	TEXT,`dca04Channels`	TEXT,`dca05Channels`	TEXT,`dca06Channels`	TEXT,`dca07Channels`	TEXT,`dca08Channels`	TEXT,`dca01Label`	TEXT,`dca02Label`	TEXT,`dca03Label`	TEXT,`dca04Label`	TEXT,`dca05Label`	TEXT,`dca06Label`	TEXT,`dca07Label`	TEXT,`dca08Label`	TEXT,`channelPositions`	TEXT,`channelProfiles`	TEXT,`fxMutes`	TEXT, `channelFX` TEXT, `snippets` TEXT, `qLabCue` TEXT, `channelLevels` TEXT, `scenes` TEXT, `colour` INTEGER, `dca09Channels` TEXT, `dca09Label` TEXT, `dca10Channels` TEXT, `dca10Label` TEXT, `dca11Channels` TEXT, `dca11Label` TEXT, `dca12Channels` TEXT, `dca12Label` TEXT)",
        "CREATE TABLE IF NOT EXISTS `ensembles` (`id`	INTEGER PRIMARY KEY AUTOINCREMENT,`name`	TEXT,`channels`	TEXT`channelProfiles`	TEXT, `channelProfiles` TEXT)",
        "CREATE TABLE IF NOT EXISTS `fxCache` (`fx`	INTEGER PRIMARY KEY,`name`	TEXT)",
        "CREATE TABLE IF NOT EXISTS `positions` (`id`	INTEGER PRIMARY KEY AUTOINCREMENT,`name`	TEXT,`shortName`	TEXT,`delay`	NUMERIC,`pan`	NUMERIC, `buses` TEXT)",
        "CREATE TABLE IF NOT EXISTS `profiles` (`id`	INTEGER PRIMARY KEY AUTOINCREMENT,`channel`	INTEGER,`name`	TEXT,`default`	INTEGER DEFAULT 0,`data`	TEXT)",
        "CREATE TABLE IF NOT EXISTS `sceneCache` (`scene`	INTEGER PRIMARY KEY,`name`	TEXT)",
        "CREATE TABLE IF NOT EXISTS `snippetCache` (`snippet`	INTEGER PRIMARY KEY,`name`	TEXT)",
        "CREATE UNIQUE INDEX IF NOT EXISTS `actorProfileID` ON `actorProfiles` (`actor`, `profile`)",
        "CREATE UNIQUE INDEX IF NOT EXISTS `cueID` ON `cues` (`number`, `point`)"]
    for statment in table_setup_statements:
        cur.execute(statment)


def setup_config(con: sqlite3.Connection):
    cur = con.cursor()
    with open("config.csv", "r") as f:
        for line in csv.reader(f):
            cur.execute(
                'INSERT OR REPLACE INTO config(param,value) VALUES(?,?)', line)
    cur.execute(
        'INSERT OR REPLACE INTO positions(id,name,shortName,delay,pan,buses) VALUES (0, "Centre Stage", "CS", 0, 0,"NULL")')


def add_cues(con: sqlite3.Connection):
    cur = con.cursor()
    actor = 'INSERT OR REPLACE INTO profiles(id,channel,name,`default`,data) VALUES(?,?,?,1,"")'
    cue = 'INSERT OR REPLACE INTO cues(rowid,number,name,dca01Channels,dca02Channels,dca03Channels,dca04Channels,dca05Channels,dca06Channels,dca07Channels,dca08Channels,dca01Label,dca02Label,dca03Label,dca04Label,dca05Label,dca06Label,dca07Label,dca08Label) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
    with open("Sound and Mics.csv") as f:
        data = [x[1:4] + x[4:-1:5] for x in csv.reader(f)][2:]
        cur.execute('UPDATE config SET value=? WHERE param=?',
                    (','.join([row[1] for row in data[1:]]), 'channels'))
        for row in data[1:]:
            cur.execute(actor, (row[1], row[1], row[2]))
        cols = [[x[y] for x in data] for y in range(len(data[0]))]
        for (index, col) in enumerate(cols[2:]):
            actors = [(cols[1][i+1] + ",", cols[2][i+1].split(" ")[0], cols[0][i+1]) if x !=
                      "" else ("", "", cols[0][i+1]) for (i, x) in enumerate(col[1:])]
            dcas = split_actors(actors)
            cur.execute(cue, [index, index, col[0], *dcas])


def split_actors(actors):
    # returns list of len 16 format
    # [#,#,#,#,#,#,#,#,STR,STR,STR,STR,STR,STR,STR,STR]
    SATB_names = ["Soprano", "Alto", "Tennor",  "Bass"]
    SATB_ports = dict(zip("SATB", [""]*4))
    for actor in actors:
        SATB_ports[actor[2]] += actor[0]
    port_groups = ["".join([group[0] for group in actors[3:]][3*x:3*x+3])
                   for x in range(5)]
    name_groups = [" ".join([group[1] for group in actors[3:]][3*x:3*x+3])
                   for x in range(5)]
    return [actors[0][0], actors[1][0], actors[2][0], "", *SATB_ports.values(), actors[0][1], actors[1][1], actors[2][1], "", *SATB_names]


def main():

    pathlib.Path("test.tmix").unlink(
        missing_ok=True
    )

    con = sqlite3.connect("test.tmix")
    setup_table(con)
    setup_config(con)
    add_cues(con)
    con.commit()


main()
