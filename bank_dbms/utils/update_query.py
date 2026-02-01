from db_connect import get_connection
from decimal import Decimal

def saving_interest_add(target_date: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT account_no, balance, interest_rate FROM ACCOUNT WHERE account_type = 'SAVING' AND status = 'ACTIVE' AND interest_rate IS NOT NULL AND interest_pay_day = DAY(%s) FOR UPDATE", (target_date,))
            accounts = cur.fetchall()
            if not accounts:
                print("해당 날짜에 이자 지급 대상 보통예금 계좌가 없습니다.")
                return

            for a in accounts:
                bal = a["balance"] or 0
                rate = a["interest_rate"] or 0
                interest = bal * rate / Decimal(100)
                if interest <= 0:
                    continue

                new_balance = bal + interest

                cur.execute("UPDATE ACCOUNT SET balance = %s WHERE account_no = %s", (new_balance, a["account_no"]))

                cur.execute("INSERT INTO PASSBOOK_TX (account_no, tx_type, amount, balance_after, tx_date) VALUES (%s, 'INTEREST_SAVING', %s, %s, %s)", (a["account_no"], interest, new_balance, target_date))

        conn.commit()
        print(f"{target_date} 기준 보통예금 이자 처리가 완료되었습니다.")
    except Exception as e:
        conn.rollback()
        print("보통예금 이자 배치 중 오류:", e)
    finally:
        conn.close()


def time_deposit_maturity(target_date: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT account_no, balance, interest_rate FROM ACCOUNT WHERE account_type = 'TIME' AND status = 'ACTIVE' AND maturity_date = %s FOR UPDATE", (target_date,))
            accounts = cur.fetchall()
            if not accounts:
                print("해당 날짜에 만기 처리할 정기예금 계좌가 없습니다.")
                return

            for a in accounts:
                bal = a["balance"] or 0
                rate = a["interest_rate"] or 0
                interest = bal * rate / Decimal(100)
                new_balance = bal + interest

                cur.execute("UPDATE ACCOUNT SET balance = %s, status = 'MATURED' WHERE account_no = %s", (new_balance, a["account_no"]))

                cur.execute("INSERT INTO PASSBOOK_TX (account_no, tx_type, amount, balance_after, tx_date) VALUES (%s, 'TIME_MATURITY', %s, %s, %s)", (a["account_no"], interest, new_balance, target_date))

        conn.commit()
        print(f"{target_date} 기준 정기예금 만기/이자 처리가 완료되었습니다.")
    except Exception as e:
        conn.rollback()
        print("정기예금 배치 처리 중 오류:", e)
    finally:
        conn.close()


def installment_maturity(target_date: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT account_no, balance, interest_rate FROM ACCOUNT WHERE account_type = 'INSTALLMENT' AND status = 'ACTIVE' AND maturity_date = %s FOR UPDATE", (target_date,))
            accounts = cur.fetchall()
            if not accounts:
                print("해당 날짜에 만기 처리할 적금 계좌가 없습니다.")
                return

            for a in accounts:
                bal = a["balance"] or 0
                rate = a["interest_rate"] or 0
                interest = bal * rate / Decimal(100)
                new_balance = bal + interest

                cur.execute("UPDATE ACCOUNT SET balance = %s, status = 'MATURED' WHERE account_no = %s", (new_balance, a["account_no"]))

                cur.execute("INSERT INTO PASSBOOK_TX (account_no, tx_type, amount, balance_after, tx_date) VALUES (%s, 'INSTALLMENT_MATURITY', %s, %s, %s)", (a["account_no"], interest, new_balance, target_date))

        conn.commit()
        print(f"{target_date} 기준 적금 만기/이자 처리가 완료되었습니다.")
    except Exception as e:
        conn.rollback()
        print("적금 배치 처리 중 오류:", e)
    finally:
        conn.close()


def auto_create_card_bill(target_date: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT card_no FROM CARD WHERE status = 'ACTIVE'")
            cards = cur.fetchall()
            if not cards:
                print("활성 카드가 없습니다.")
                return

            created_count = 0

            for c in cards:
                card_no = c["card_no"]

                cur.execute("SELECT IFNULL(SUM(amount), 0) AS total FROM CARD_TX WHERE card_no = %s AND DATE(tx_date) = %s", (card_no, target_date))
                row = cur.fetchone()
                total = row["total"] or 0

                if total <= 0:
                    continue

                cur.execute("INSERT INTO CARD_BILL (card_no, period_start, period_end, total_amount, due_date, status) VALUES (%s, %s, %s, %s, %s, 'UNPAID')", (card_no, target_date, target_date, total, target_date))
                created_count += 1

        conn.commit()
        print(f"{target_date} 기준 카드 청구서 {created_count}건이 생성되었습니다.")
    except Exception as e:
        conn.rollback()
        print("카드 청구서 배치 처리 중 오류:", e)
    finally:
        conn.close()


def loan_overdue_check(target_date: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT r.repay_id, r.loan_id, l.user_id FROM LOAN_REPAY r JOIN LOAN l ON r.loan_id = l.loan_id WHERE r.due_date = %s AND r.status IN ('SCHEDULED', 'PARTIAL')", (target_date,))
            rows = cur.fetchall()
            if not rows:
                print("해당 날짜에 연체로 변경할 상환 일정이 없습니다.")
            else:
                for r in rows:
                    cur.execute("UPDATE LOAN_REPAY SET status = 'OVERDUE' WHERE repay_id = %s", (r["repay_id"],))
                    cur.execute("UPDATE LOAN SET overdue_count = overdue_count + 1 WHERE loan_id = %s", (r["loan_id"],))
                    cur.execute("UPDATE USER SET delinquency_count = delinquency_count + 1, delinquent_status = 'DELINQUENT' WHERE user_id = %s", (r["user_id"],))

        conn.commit()
        print(f"{target_date} 기준 대출 연체 및 고객 상태 갱신이 완료되었습니다.")
    except Exception as e:
        conn.rollback()
        print("대출 연체 배치 처리 중 오류:", e)
    finally:
        conn.close()

def card_overdue_check(target_date: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT b.bill_id, b.card_no, a.user_id FROM CARD_BILL b JOIN CARD c ON b.card_no = c.card_no JOIN ACCOUNT a ON c.account_no = a.account_no WHERE b.due_date = %s AND b.status = 'UNPAID'", (target_date,))
            rows = cur.fetchall()

            if not rows:
                print("해당 날짜에 연체로 처리할 카드 청구서가 없습니다.")
                return

            for r in rows:
                bill_id = r["bill_id"]
                card_no = r["card_no"]
                user_id = r["user_id"]

                cur.execute("UPDATE CARD_BILL SET status = 'OVERDUE' WHERE bill_id = %s", (bill_id,))
                cur.execute("UPDATE CARD SET overdue_count = overdue_count + 1 WHERE card_no = %s", (card_no,))
                cur.execute("UPDATE USER SET delinquency_count = delinquency_count + 1, delinquent_status = 'DELINQUENT' WHERE user_id = %s", (user_id,))

        conn.commit()
        print(f"{target_date} 기준 카드 연체 처리 배치가 완료되었습니다.")
    except Exception as e:
        conn.rollback()
        print("카드 연체 배치 처리 중 오류:", e)
    finally:
        conn.close()

