from db_connect import get_connection

def create_account(user_id, account_no, account_type, init_balance=0, interest_pay_day=0, maturity_date=0):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO ACCOUNT (account_no, user_id, account_type, status, balance, interest_pay_day, maturity_date) VALUES (%s, %s, %s, 'ACTIVE', %s, %s, %s)", (account_no, user_id, account_type, init_balance, interest_pay_day, maturity_date))
        conn.commit()
        print("계좌가 개설되었습니다.")
    except Exception as e:
        conn.rollback()
        print("계좌 개설 중 오류:", e)
    finally:
        conn.close()


def delete_account(account_no):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM ACCOUNT WHERE account_no = %s", (account_no,))
            if cur.rowcount == 0:
                print("해당 계좌가 없습니다.")
            else:
                print("계좌가 삭제되었습니다.")
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("계좌 삭제 중 오류:", e)
    finally:
        conn.close()


def show_account_info(account_no):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM ACCOUNT WHERE account_no = %s", (account_no,))
            row = cur.fetchone()
            if not row:
                print("해당 계좌를 찾을 수 없습니다.")
                return
            print("\n--- 계좌 정보 ---")
            for k, v in row.items():
                print(f"{k}: {v}")
    except Exception as e:
        print("계좌 정보 조회 중 오류:", e)
    finally:
        conn.close()


def list_accounts_by_user(user_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT account_no, account_type, status, balance FROM ACCOUNT WHERE user_id = %s", (user_id,))
            rows = cur.fetchall()
            if not rows:
                print("해당 고객의 계좌가 없습니다.")
                return
            print("\n--- 계좌 목록 ---")
            for r in rows:
                print(r)
    except Exception as e:
        print("계좌 목록 조회 중 오류:", e)
    finally:
        conn.close()


def change_account_status(account_no, new_status):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE ACCOUNT SET status = %s WHERE account_no = %s", (new_status, account_no))
            if cur.rowcount == 0:
                print("해당 계좌가 없습니다.")
            else:
                print("계좌 상태가 변경되었습니다.")
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("계좌 상태 변경 중 오류:", e)
    finally:
        conn.close()