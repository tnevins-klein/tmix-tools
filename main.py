import sqlite3
import pathlib
import os


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
        for line in f:
            cur.execute(
                'INSERT OR REPLACE INTO config(param,value) VALUES(?,?)', line.split(",", 1))
    cur.execute(
        'INSERT OR REPLACE INTO positions(id,name,shortName,delay,pan,buses) VALUES (0, "Centre Stage", "CS", 0, 0,"NULL")')


def add_cues(con: sqlite3.Connection):
    cur = con.cursor()
    sql = 'INSERT OR REPLACE INTO profiles(id,channel,name,default,data) VAlUES(?,?,?,1,"NULL")'
    with open("Sound and Mics.csv") as f:
        data = list(map(lambda a: a.split(",")[
                    1:3] + a.split(",")[3:-1:5], f.readlines()))[2:22]
        print(data[0], data[-1])


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
