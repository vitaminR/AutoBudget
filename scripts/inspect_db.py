import sqlite3, pathlib
p = pathlib.Path('/mnt/c/Users/nymil/Codepro/AutoBudget/autobudget.db').resolve()
print('DB path:', p)
try:
    con = sqlite3.connect(str(p))
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print('Tables:', cur.fetchall())
    for t in ['pay_periods','bills']:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            print(t, 'count:', cur.fetchone()[0])
        except Exception as e:
            print('error reading', t, e)
    con.close()
except Exception as e:
    print('db connect error', e)
