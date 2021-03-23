#!/usr/bin/env python
#pip install pycryptodomex
import sqlite3
import traceback
from pathlib import Path
from pygments.lexers.sql import SqlLexer

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from prompt_toolkit import prompt

from .util import en, dec, en_real, dec_real,read_entry_file

sql_completer = WordCompleter(
    [
        "select kw",
        "insert_user site user",
        "update_password site user",
        "update_password_by_id rowid",
        "exit",
    ],
    ignore_case=True,

)

style = Style.from_dict(
    {
        "completion-menu.completion": "bg:#008888 #ffffff",
        "completion-menu.completion.current": "bg:#00aaaa #000000",
        "scrollbar.background": "bg:#88aaaa",
        "scrollbar.button": "bg:#222222",
    }
)

"""
cmd:
select    163  prg
save  mail.163.com   prgrmz07@163.com  pwd
update mail.163.com  prgrmz07@163.com newPWD
"""
def prompt_password():
    password: bytes = prompt("password:", is_password=True).encode("utf-8")
    password_encrypt = en(password, gconf.k.aes_key)
    return password_encrypt


from random import randint
def mask(plain_text:bytes)->str:
    if plain_text is None: return None
    length=len(plain_text)
    mask_cnt=length//3
    mask_idx=[randint(0,length-1) for i in range(mask_cnt)]
    plain_ch_ls=list(plain_text.decode("utf-8"))
    for msk in mask_idx:
        plain_ch_ls[msk] = '#'
    return "".join(plain_ch_ls)
    # return "%s%s"%(begin*"#",plain_text[begin:].decode("utf-8"))
def select_by_like_site_or_username(site_or_username_like:str,connection:sqlite3.Connection):
    with connection:
        try:
            row_ls: sqlite3.Cursor = connection.execute("select id,site,username,password from pass ")
        except Exception as e:
            print(repr(e))
        else:
            plain_text_ls=[(
                row[0],
                dec(row[1],gconf.k.aes_key).decode("utf-8") ,
                dec(row[2],gconf.k.aes_key).decode("utf-8"),
                mask(dec(row[3],gconf.k.aes_key) )
                ) for row in row_ls]
            return [row for row in plain_text_ls
                    if
                    row[1].__contains__(site_or_username_like)
                    or row[2].__contains__(site_or_username_like)
                    ]
    return None

def db_2_csv_enc(connection:sqlite3.Connection)->bool:
    with connection:
        try:
            row_ls: sqlite3.Cursor = connection.execute("select id,site,username,password from pass ")
        except Exception as e:
            print(repr(e))
            return False
        else:
            #sql查询结果
            plain_text_ls=[row for row in row_ls]

            import csv

            #表转csv文件
            with open(gconf.p.plain_csv, 'w', newline='') as csvfile:
                print(f" {gconf.p.plain_db} -> {gconf.p.plain_csv}")
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(["id","site","username","password"])
                csvwriter.writerows(plain_text_ls)

            #csv文件转csv加密文件
            print(f" {gconf.p.plain_csv}.csv -> {gconf.p.plain_csv_enc}")
            plain_: bytes = read_entry_file(gconf.p.plain_csv)
            encrypt_: bytes = en_real(plain_, gconf.k.aes_key)
            with open(gconf.p.plain_csv_enc, "wb") as f:
                f.write(encrypt_)

            #删除csv文件
            gconf.p.plain_csv_path.unlink(missing_ok=True)

            return True
    return False

def csv_enc_2_csv()->None:
    print(f" {gconf.p.plain_csv_enc} -> {gconf.p.plain_csv}")
    encrypt_:bytes=read_entry_file(gconf.p.plain_csv_enc)
    plain_:bytes=dec_real(encrypt_,gconf.k.aes_key)
    with open(gconf.p.plain_csv, "wb") as f:
        f.write(plain_)


def csv_2_db()->None:
    connection:sqlite3.Connection = sqlite3.connect(gconf.p.plain_db)
    print(f" {gconf.p.plain_csv} -> {gconf.p.plain_db}"  )
    import pandas as pd
    df=pd .read_csv(gconf.p.plain_csv,delimiter=",")
    row_cnt:int=df.shape[0]
    if row_cnt==0:
        return
    df = df.where(pd.notnull(df), "")
    def gen_sql(r):
        return f"""insert into pass(id,site,username,password) values ({r['id']},'{r['site']}','{r['username']}','{r['password'] }' )""" \
            if r['password'] != "" \
            else f"""insert into pass(id,site,username) values ({r['id']},'{r['site']}','{r['username']}' )"""
    sql_ls=df.apply(lambda r:gen_sql(r),axis=1).tolist()
    # print(sql_ls)
    # print("\n".join(sql_ls))
    list(map(lambda sql:update_sql(sql,connection),sql_ls))

def update_sql(sql:str,connection:sqlite3.Connection):
    with connection:
        try:
             result=connection.execute(sql)
        except Exception as e:
            print(repr(e))
        else:
            # print("result:",result.rowcount)
            return (result.rowcount,result.lastrowid)
    return None

def csv_enc_2_db():
    csv_enc_2_csv()
    gconf.p.plain_db_path.unlink(missing_ok=True)
    init_plain_db()
    csv_2_db(  )

def save_(connection:sqlite3.Connection):
    try:
        db_2_csv_enc(connection)
    finally:
        if connection!=None :
            connection.close()


def clean_then_exit():
    print(f"remove {gconf.p.plain_db}")
    gconf.p.plain_db_path.unlink(missing_ok=True)
    print(f"remove {gconf.p.plain_csv}")
    gconf.p.plain_csv_path.unlink(missing_ok=True)
    global gExit
    gExit=True

def exec(cmd:str):
    connection:sqlite3.Connection = sqlite3.connect(gconf.p.plain_db)
    sql = None
    for i in range(100):
        cmd = cmd.replace("  "," ")
    cmd=cmd.split(" ")
    action=cmd[0].lower()
    if 'select'==action:
        search_word=cmd[1]
        row_ls=select_by_like_site_or_username(search_word,connection)
        [print(row) for row in row_ls]

    if 'insert_user'==action:
        site,username=cmd[1],cmd[2]
        site = en(site.encode("utf-8"), gconf.k.aes_key)
        username = en(username.encode("utf-8"), gconf.k.aes_key)
        sql = "insert into  pass(site,username) values ('{site}','{username}')".format(site=site,username=username)
        rowcount,lastrowid=update_sql(sql,connection)
        print("rowcount,lastrowid:",rowcount,lastrowid)
        save_(connection);connection=None

    if 'update_password'==action:
        site,username=cmd[1],cmd[2]
        password_encrypt=prompt_password()
        sql = "update pass set password='{password}' where site='{site}' and username='{username}'".format(site=site,username=username,password=password_encrypt)
        rowcount,lastrowid=update_sql(sql, connection)
        print("rowcount,lastrowid:",rowcount,lastrowid)
        save_(connection);connection=None

    if 'update_password_by_id'==action:
        id=cmd[1]
        password_encrypt=prompt_password()
        sql = "update pass set password='{password}' where  id='{id}'".format(id=id,password=password_encrypt)
        rowcount,lastrowid=update_sql(sql, connection)
        print("rowcount,lastrowid:",rowcount,lastrowid)
        save_(connection);connection=None

    if connection != None:
        connection.close()

    if 'exit'==action:
        clean_then_exit()



from .init_sql import init_db_sql
def init_plain_db():
    print(f"init_plain_db:{gconf.p.plain_db},using create table sql")
    connection:sqlite3.Connection = sqlite3.connect(gconf.p.plain_db)
    update_sql(init_db_sql,connection)
    connection.close()



def prompt_aes_key()->bytes:
    aes_key:bytes = prompt('aes key: ', is_password=True).encode("utf-8")
    return aes_key

def init():
    gconf.p.home_path.mkdir(exist_ok=True)

    if not gconf.p.plain_db_path.exists() :
        if not gconf.p.plain_csv_enc_path.exists():
            # build empty csv_enc
            init_plain_db()
            connection: sqlite3.Connection = sqlite3.connect(gconf.p.plain_db)
            save_(connection)
          
        csv_enc_2_db()
    else:
        print(f"using:{gconf.p.plain_db}")


def main():
    # connection = sqlite3.connect(database)
    gconf.k.aes_key:bytes = prompt_aes_key()

    session = PromptSession(
        lexer=PygmentsLexer(SqlLexer), completer=sql_completer, style=style
    )


    init()

    while not gExit:
        try:
            cmd = session.prompt(f"^_^pass_pad@{gconf.p.plain_db}> ")
            exec(cmd)
        except KeyboardInterrupt : # Control-C pressed.
            clean_then_exit()
        except  EOFError:  #  Control-D pressed.
            clean_then_exit()
        except ValueError as e:
            traceback.print_exc()
            gconf.k.aes_key: bytes = prompt_aes_key()
            # print(traceback.extract_stack(e))
            # break
    print("end")

class Conf():
    def __init__(self,name:str="pass",db_suffix:str="db",encrypt_suffix:str="enc",aes_key:str=None):
        self.p: Conf.Path = None
        self.path: Conf.Path = None

        self.k:Conf.CryptKey = None
        self.crypt_key: Conf.CryptKey = None

        self.p=self.path=Conf.Path(name, db_suffix, encrypt_suffix)
        self.k=self.crypt_key=Conf.CryptKey(aes_key)
    class Path():
        def __init__(self,name="pass",db_suffix="db",encrypt_suffix="enc"):
            self.home:str=f"{Path.home()}/.pass_pad"
            # Path(self.home).mkdir(exist_ok=True)
            self.plain:str=None
            self.plain_db:str=None
            self.plain_db_enc:str=None
            self.plain_csv:str=None
            self.plain_csv_enc:str=None

            self.plain=name
            self.plain_db= f"{self.home}/{name}.{db_suffix}"
            self.plain_db_enc= f"{self.home}/{name}.{db_suffix}.{encrypt_suffix}"
            self.plain_csv = f"{self.home}/{name}.csv"
            self.plain_csv_enc = f"{self.home}/{name}.csv.{encrypt_suffix}"

            self.home_path=Path(self.home)
            self.plain_db_path=Path(self.plain_db)
            self.plain_db_enc_path=Path(self.plain_db_enc)
            self.plain_csv_path=Path(self.plain_csv)
            self.plain_csv_enc_path=Path(self.plain_csv_enc)
    class CryptKey():
        def __init__(self,aes_key:bytes):
            self.aes_key:str=None

            self.aes_key=aes_key

gconf=Conf()
gExit=False
if __name__ == "__main__":
    main()
