from db_connect import get_connection

def deposit(account_no, amount):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT balance, account_type, status FROM ACCOUNT WHERE account_no = %s FOR UPDATE", (account_no,))
            row = cur.fetchone()
            if not row:
                print("계좌를 찾을 수 없습니다.")
                return
            if row["status"] != "ACTIVE":
                print("활성 계좌가 아닙니다.")
                return

            new_balance = (row["balance"] or 0) + amount

            cur.execute("UPDATE ACCOUNT SET balance = %s WHERE account_no = %s", (new_balance, account_no))
            cur.execute("INSERT INTO PASSBOOK_TX (account_no, tx_type, amount, balance_after) VALUES (%s, %s, %s, %s)", (account_no, "DEPOSIT", amount, new_balance))

        conn.commit()
        print(f"{amount}원이 입금되었습니다. 현재 잔액: {new_balance}")
    except Exception as e:
        conn.rollback()
        print("입금 중 오류:", e)
    finally:
        conn.close()


def withdraw(account_no, amount):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT balance, account_type, status FROM ACCOUNT WHERE account_no = %s FOR UPDATE", (account_no,))
            row = cur.fetchone()
            if not row:
                print("계좌를 찾을 수 없습니다.")
                return

            if row["status"] != "ACTIVE":
                print("활성 계좌가 아닙니다.")
                return

            acc_type = row["account_type"]
            if acc_type in ("TIME", "INSTALLMENT"):
                print("정기예금/적금 계좌는 일반 출금이 불가능합니다.")
                return

            current_balance = row["balance"] or 0
            if current_balance < amount:
                print("잔액이 부족합니다.")
                return

            new_balance = current_balance - amount

            cur.execute("UPDATE ACCOUNT SET balance = %s WHERE account_no = %s", (new_balance, account_no))
            cur.execute("INSERT INTO PASSBOOK_TX (account_no, tx_type, amount, balance_after) VALUES (%s, %s, %s, %s)", (account_no, "WITHDRAW", amount, new_balance))

        conn.commit()
        print(f"{amount}원이 출금되었습니다. 현재 잔액: {new_balance}")
    except Exception as e:
        conn.rollback()
        print("출금 중 오류:", e)
    finally:
        conn.close()


def show_passbook_by_account(account_no):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM PASSBOOK_TX WHERE account_no = %s ORDER BY tx_date, tx_id", (account_no,))
            rows = cur.fetchall()
            if not rows:
                print("해당 계좌의 거래 내역이 없습니다.")
                return
            print("\n--- 통장 거래 내역 ---")
            for r in rows:
                print(r)
    except Exception as e:
        print("통장 조회 중 오류:", e)
    finally:
        conn.close()
