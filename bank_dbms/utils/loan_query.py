from db_connect import get_connection

def create_loan(user_id, principal, interest_rate, collateral_type, collateral_object_id, collateral_value):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT credit_grade, delinquent_status FROM USER WHERE user_id = %s", (user_id,))
            user = cur.fetchone()
            if not user:
                print("고객을 찾을 수 없습니다.")
                return

            if user["delinquent_status"] != "NORMAL":
                print("연체자는 신규 대출을 받을 수 없습니다.")
                return

            if collateral_type == "CREDIT" and user["credit_grade"] == "C":
                print("신용등급 C는 신용대출을 받을 수 없습니다.")
                return

            cur.execute("INSERT INTO LOAN (user_id, principal, interest_rate, status, overdue_count) VALUES (%s, %s, %s, 'ACTIVE', 0)", (user_id, principal, interest_rate))
            loan_id = cur.lastrowid

            cur.execute("INSERT INTO COLLATERAL (loan_id, collateral_type, object_id, value) VALUES (%s, %s, %s, %s)", (loan_id, collateral_type, collateral_object_id, collateral_value))

        conn.commit()
        print(f"대출이 생성되었습니다. loan_id={loan_id}")
    except Exception as e:
        conn.rollback()
        print("대출 생성 중 오류:", e)
    finally:
        conn.close()


def show_loan_info(loan_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT l.*, u.name AS user_name FROM LOAN l JOIN USER u ON l.user_id = u.user_id WHERE l.loan_id = %s", (loan_id,))
            loan = cur.fetchone()
            if not loan:
                print("대출을 찾을 수 없습니다.")
                return

            print("\n--- 대출 정보 ---")
            for k, v in loan.items():
                print(f"{k}: {v}")

            cur.execute("SELECT * FROM LOAN_REPAY WHERE loan_id = %s ORDER BY due_date", (loan_id,))
            repays = cur.fetchall()
            print("\n--- 상환 일정 ---")
            if not repays:
                print("등록된 상환 일정이 없습니다.")
            else:
                for r in repays:
                    print(r)

            cur.execute("SELECT * FROM COLLATERAL WHERE loan_id = %s", (loan_id,))
            col = cur.fetchone()
            print("\n--- 담보 정보 ---")
            if not col:
                print("등록된 담보가 없습니다.")
            else:
                for k, v in col.items():
                    print(f"{k}: {v}")

    except Exception as e:
        print("대출 정보 조회 중 오류:", e)
    finally:
        conn.close()


def create_repay_schedule(loan_id, num_terms, term_amount):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for i in range(num_terms):
                cur.execute("INSERT INTO LOAN_REPAY (loan_id, due_date, due_amount, paid_amount, status) VALUES (%s, DATE_ADD(CURDATE(), INTERVAL %s DAY), %s, 0, 'SCHEDULED')", (loan_id, 30 * i, term_amount))
        conn.commit()
        print("대출 상환 일정이 생성되었습니다.")
    except Exception as e:
        conn.rollback()
        print("상환 일정 생성 중 오류:", e)
    finally:
        conn.close()


def pay_loan_repay(repay_id, pay_amount):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM LOAN_REPAY WHERE repay_id = %s", (repay_id,))
            repay = cur.fetchone()
            if not repay:
                print("상환 일정을 찾을 수 없습니다.")
                return

            if repay["status"] == "PAID":
                print("이미 완납된 상환입니다.")
                return

            cur.execute("UPDATE LOAN_REPAY SET paid_amount = %s, paid_date = CURDATE(), status = CASE WHEN %s >= due_amount THEN 'PAID' ELSE 'PARTIAL' END WHERE repay_id = %s", (pay_amount, pay_amount, repay_id))
        conn.commit()
        print("상환 처리가 완료되었습니다.")
    except Exception as e:
        conn.rollback()
        print("대출 상환 처리 중 오류:", e)
    finally:
        conn.close()


def show_loan_overdues(user_id=None):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if user_id is None:
                cur.execute("SELECT r.*, l.user_id FROM LOAN_REPAY r JOIN LOAN l ON r.loan_id = l.loan_id WHERE r.status = 'OVERDUE'")
            else:
                cur.execute("SELECT r.*, l.user_id FROM LOAN_REPAY r JOIN LOAN l ON r.loan_id = l.loan_id WHERE r.status = 'OVERDUE' AND l.user_id = %s", (user_id,))
            rows = cur.fetchall()
            if not rows:
                print("연체된 상환이 없습니다.")
                return
            print("\n--- 대출 연체 내역 ---")
            for r in rows:
                print(r)
    except Exception as e:
        print("대출 연체 조회 중 오류:", e)
    finally:
        conn.close()


def exercise_collateral(loan_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM COLLATERAL WHERE loan_id = %s", (loan_id,))
            col = cur.fetchone()
            if not col:
                print("이 대출에는 담보가 등록되어 있지 않습니다.")
                return

            cur.execute("UPDATE LOAN SET status = 'CLOSED_BY_COLLATERAL' WHERE loan_id = %s", (loan_id,))
        conn.commit()
        print("담보권 행사 처리가 완료되었습니다.")
    except Exception as e:
        conn.rollback()
        print("담보권 행사 처리 중 오류:", e)
    finally:
        conn.close()
