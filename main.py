import click

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
    for statement in table_setup_statements:
        cur.execute(statement)


def setup_config(con: sqlite3.Connection, config_file):
    cur = con.cursor()
    with open(config_file, "r") as f:
        for line in csv.reader(f):
            cur.execute(
                'INSERT OR REPLACE INTO config(param,value) VALUES(?,?)', line)
    cur.execute(
        'INSERT OR REPLACE INTO positions(id,name,shortName,delay,pan,buses) VALUES (0, "Centre Stage", "CS", 0, 0,"NULL")')


def add_cues(con: sqlite3.Connection, scenes):
    cur = con.cursor()
    actor = 'INSERT OR REPLACE INTO profiles(id,channel,name,`default`,data) VALUES(?,?,?,1,"")'
    cue = 'INSERT OR REPLACE INTO cues(rowid,number,name,dca01Channels,dca02Channels,dca04Channels,dca05Channels,dca06Channels,dca07Channels,dca08Channels,dca01Label,dca02Label,dca04Label,dca05Label,dca06Label,dca07Label,dca08Label) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
    with open(scenes, "r") as f:
        data = [x for x in csv.reader(f)][2:]
        cur.execute('UPDATE config SET value=? WHERE param=?',
                    (','.join([row[2] for row in data[1:]]), 'channels'))
        for row in data[1:]:
            cur.execute(actor, (row[2], row[2], row[1]))
        cols = [[x[y] for x in data] for y in range(len(data[0]))]
        # cols[0] is charator names
        # cols[1] is actor names
        # cols[2] is mic numbers
        # cols[3] is voice part
        for (index, col) in enumerate(cols[2:]):
            actors = [(cols[2][i+1] + ",", cols[1][i+1], cols[3][i+1]) if x !=
                      '' else ("", "", cols[3][i+1]) for (i, x) in enumerate(col[1:])]
            dcas = split_actors(actors)
            cur.execute(cue, [index, index, col[0], *dcas])


def split_actors(actors):
    # returns list of len 16 format
    # [#,#,#,#,#,#,#,STR,STR,STR,STR,STR,STR,STR]
    SATB_names = ["Soprano", "Alto", "Tenor",  "Bass"]
    SATB_ports = dict(zip("SATB", [""]*4))
    backup_names = []
    lead_names = []
    lead_ports = []
    actor_count = 0
    for actor in actors:
        if actor[1] == '':
            continue
        actor_count += 1
        if len(lead_ports) == 3 :
            try:
                SATB_ports[actor[2][0]] += actor[0]
                break
            except:
                SATB_ports["S"] += actor[0]
            backup_names.append(actor[1])
        else:
            lead_names.append(actor[1])
            lead_ports.append(actor[0])
    if  actor_count < 7:
        for value,name in zip(SATB_ports.values(),backup_names):
            if value == '':
                continue
            lead_names.append(name)
            lead_ports.append(value)
        for _ in range(7-len(lead_names)):
            lead_names.append('')
            lead_ports.append('')
        return_values = [*lead_ports,  *lead_names]
        return(return_values)
    else:
        for _ in range(3 - len(lead_names)):
            lead_names.append('')
            lead_ports.append('')
        return_values = [*lead_ports, *SATB_ports.values(), *lead_names, *SATB_names]
        return(return_values)


@click.command()
@click.option(
    "--scenes",
    type=click.Path(),
    default="tracking.csv",
    help="Specifies the scenes file"
)
@click.option(
    "--config_file",
    type=click.Path(),
    default="config.csv",
    help="specifies the internal tmix config schema. Can be extracted using a SQLite db viewer"
)
@click.argument(
    "out_file",
    type=click.Path(),
)
def convert(scenes, config_file, out_file):
    pathlib.Path(out_file).unlink(
        missing_ok=True
    )

    con = sqlite3.connect(out_file)
    setup_table(con)
    setup_config(con, config_file)
    add_cues(con, scenes)
    con.commit()


convert()
