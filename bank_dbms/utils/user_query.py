from db_connect import get_connection

def create_user(name, phone, address, emp_id, credit_grade="A"):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO USER (name, phone, address, credit_grade, emp_id) VALUES (%s, %s, %s, %s, %s)", (name, phone, address, credit_grade, emp_id))
        conn.commit()
        print("고객이 등록되었습니다.")
    except Exception as e:
        conn.rollback()
        print("고객 등록 중 오류:", e)
    finally:
        conn.close()


def get_user_by_id(user_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM USER WHERE user_id = %s", (user_id,))
            row = cur.fetchone()
        return row
    except Exception as e:
        print("고객 조회 중 오류:", e)
        return None
    finally:
        conn.close()


def update_user_info(user_id, name, phone, address):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE USER SET name = %s, phone = %s, address = %s WHERE user_id = %s", (name, phone, address, user_id))
        conn.commit()
        print("고객 정보가 수정되었습니다.")
    except Exception as e:
        conn.rollback()
        print("고객 정보 수정 중 오류:", e)
    finally:
        conn.close()


def recalc_credit_for_user(user_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT delinquency_count FROM USER WHERE user_id = %s", (user_id,))
            row = cur.fetchone()
            if not row:
                print("해당 고객이 존재하지 않습니다.")
                return
            d = row["delinquency_count"] or 0

            if d <= 1:
                grade = "A"
            elif d <= 3:
                grade = "B"
            else:
                grade = "C"

            cur.execute("UPDATE USER SET credit_grade = %s WHERE user_id = %s", (grade, user_id))
        conn.commit()
        print(f"신용등급이 재산정되었습니다. (새 등급: {grade})")
    except Exception as e:
        conn.rollback()
        print("신용등급 재산정 중 오류:", e)
    finally:
        conn.close()


def show_user_status_summary(user_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM USER WHERE user_id = %s", (user_id,))
            user = cur.fetchone()
            if not user:
                print("해당 고객이 존재하지 않습니다.")
                return

            print("\n--- 고객 기본 정보 ---")
            for k, v in user.items():
                print(f"{k}: {v}")

            print("\n--- 계좌 목록 ---")
            cur.execute("SELECT account_no, account_type, status, balance FROM ACCOUNT WHERE user_id = %s", (user_id,))
            accounts = cur.fetchall()
            if not accounts:
                print("보유 계좌 없음")
            else:
                for a in accounts:
                    print(a)

            print("\n--- 대출 목록 ---")
            cur.execute("SELECT loan_id, principal, interest_rate, status, overdue_count FROM LOAN WHERE user_id = %s", (user_id,))
            loans = cur.fetchall()
            if not loans:
                print("대출 없음")
            else:
                for l in loans:
                    print(l)

            print("\n--- 카드 목록 ---")
            cur.execute("SELECT c.card_no, c.status, c.overdue_count, a.account_no FROM CARD c JOIN ACCOUNT a ON c.account_no = a.account_no WHERE a.user_id = %s", (user_id,))
            cards = cur.fetchall()
            if not cards:
                print("발급된 카드 없음")
            else:
                for c in cards:
                    print(c)

    except Exception as e:
        print("고객 상태 조회 중 오류:", e)
    finally:
        conn.close()