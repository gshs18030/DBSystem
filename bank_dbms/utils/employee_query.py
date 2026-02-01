from db_connect import get_connection

def create_employee(name, phone, address):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO EMPLOYEE (name, phone, address) VALUES (%s, %s, %s)", (name, phone, address))
        conn.commit()
        print("직원이 등록되었습니다.")
    except Exception as e:
        conn.rollback()
        print("직원 등록 중 오류:", e)
    finally:
        conn.close()


def list_employees():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM EMPLOYEE")
            rows = cur.fetchall()
            if not rows:
                print("등록된 직원이 없습니다.")
                return
            print("\n--- 직원 목록 ---")
            for r in rows:
                print(r)
    except Exception as e:
        print("직원 목록 조회 중 오류:", e)
    finally:
        conn.close()


def freeze_account(account_no):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE ACCOUNT SET status = 'FROZEN' WHERE account_no = %s", (account_no,))
            if cur.rowcount == 0:
                print("해당 계좌가 없습니다.")
            else:
                print("계좌가 동결되었습니다.")
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("계좌 동결 중 오류:", e)
    finally:
        conn.close()


def unfreeze_account(account_no):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE ACCOUNT SET status = 'ACTIVE' WHERE account_no = %s", (account_no,))
            if cur.rowcount == 0:
                print("해당 계좌가 없습니다.")
            else:
                print("계좌 동결이 해제되었습니다.")
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("계좌 동결 해제 중 오류:", e)
    finally:
        conn.close()


def list_freeze_deliq():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            print("\n--- 동결된 계좌 목록 ---")
            cur.execute("SELECT * FROM ACCOUNT WHERE status = 'FROZEN'")
            frozen = cur.fetchall()
            if not frozen:
                print("동결 계좌 없음")
            else:
                for r in frozen:
                    print(r)

            print("\n--- 연체 고객 목록 (delinquency_count > 0) ---")
            cur.execute("SELECT * FROM USER WHERE delinquency_count > 0")
            del_users = cur.fetchall()
            if not del_users:
                print("연체 고객 없음")
            else:
                for u in del_users:
                    print(u)

            print("\n--- 카드 연체 카드 목록 ---")
            cur.execute("SELECT * FROM CARD WHERE overdue_count > 0")
            cards = cur.fetchall()
            if not cards:
                print("카드 연체 없음")
            else:
                for c in cards:
                    print(c)

    except Exception as e:
        print("이상 거래/연체 계좌 조회 중 오류:", e)
    finally:
        conn.close()
