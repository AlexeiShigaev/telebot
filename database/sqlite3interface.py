import json
import sqlite3
import sys
from config import database_name
from logs import logger


def save(user_id: str, state: json, query_res: json) -> None:
    logger.debug('На входе user_id:{}, state:{}'.format(user_id, state))
    try:
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()
        sql_q = "CREATE TABLE IF NOT EXISTS '" + user_id + \
                "'(id INTEGER PRIMARY KEY AUTOINCREMENT, state json, query_res json)"
        cursor.execute(sql_q)

        cursor.execute(
            "INSERT INTO '" + user_id + "'(state, query_res) VALUES(?,?)",
            (state, query_res)
        )
        conn.commit()
    except sqlite3.OperationalError as ex:
        tb = sys.exc_info()[2]
        logger.error('\nПроизошло исключение\n{}'.format(str(ex.with_traceback(tb))))


def get_states(user_id: str) -> list:
    logger.debug('На входе user_id:{}'.format(user_id))
    try:
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, state FROM '{}'".format(user_id))
    except sqlite3.OperationalError as ex:
        tb = sys.exc_info()[2]
        logger.error('\nПроизошло исключение\n{}'.format(str(ex.with_traceback(tb))))
        return []
    return cursor.fetchall()


def delete_row(user_id: str, row_id: int) -> bool:
    logger.debug('На входе user_id:{}, row_id:{}'.format(user_id, row_id))
    try:
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM '{}' WHERE id={}".format(user_id, row_id))
        conn.commit()
    except sqlite3.OperationalError as ex:
        tb = sys.exc_info()[2]
        logger.error('\nПроизошло исключение\n{}'.format(str(ex.with_traceback(tb))))
        return False
    return True


def get_query_res(user_id: str, row_id: int) -> list:
    try:
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()
        cursor.execute("SELECT state, query_res FROM '{}' WHERE id={}".format(user_id, row_id))
    except sqlite3.OperationalError as ex:
        tb = sys.exc_info()[2]
        logger.error('\nПроизошло исключение\n{}'.format(str(ex.with_traceback(tb))))
        return []
    return cursor.fetchall()
