from db_connect import get_connection

def create_card(account_no):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT a.account_no, a.account_type, a.status, u.user_id, u.delinquent_status FROM ACCOUNT a JOIN USER u ON a.user_id = u.user_id WHERE a.account_no = %s", (account_no,))
            row = cur.fetchone()
            if not row:
                print("계좌를 찾을 수 없습니다.")
                return

            if row["account_type"] != "SAVING":
                print("보통예금(SAVING) 계좌에만 카드를 발급할 수 있습니다.")
                return

            if row["status"] != "ACTIVE":
                print("활성 계좌가 아닙니다.")
                return

            if row["delinquent_status"] != "NORMAL":
                print("연체자는 카드를 발급받을 수 없습니다.")
                return

            card_no = row["account_no"]

            cur.execute("SELECT * FROM CARD WHERE account_no = %s", (account_no,))
            exist = cur.fetchone()
            if exist:
                print("이 계좌에는 이미 카드가 발급되어 있습니다.")
                return

            cur.execute("INSERT INTO CARD (card_no, account_no, status, overdue_count) VALUES (%s, %s, 'ACTIVE', 0)", (card_no, account_no))

        conn.commit()
        print(f"카드가 발급되었습니다. 카드 번호: {card_no}")
    except Exception as e:
        conn.rollback()
        print("카드 발급 중 오류:", e)
    finally:
        conn.close()


def show_card_info(card_no):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT c.*, a.user_id FROM CARD c JOIN ACCOUNT a ON c.account_no = a.account_no WHERE c.card_no = %s", (card_no,))
            row = cur.fetchone()
            if not row:
                print("카드를 찾을 수 없습니다.")
                return
            print("\n--- 카드 정보 ---")
            for k, v in row.items():
                print(f"{k}: {v}")
    except Exception as e:
        print("카드 정보 조회 중 오류:", e)
    finally:
        conn.close()


def add_card_tx(card_no, amount, merchant):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT status FROM CARD WHERE card_no = %s", (card_no,))
            card = cur.fetchone()
            if not card:
                print("카드를 찾을 수 없습니다.")
                return
            if card["status"] != "ACTIVE":
                print("활성 카드가 아닙니다.")
                return

            cur.execute("INSERT INTO CARD_TX (card_no, amount, tx_date, merchant) VALUES (%s, %s, NOW(), %s)", (card_no, amount, merchant))

        conn.commit()
        print("카드 사용 내역이 등록되었습니다.")
    except Exception as e:
        conn.rollback()
        print("카드 사용 내역 등록 중 오류:", e)
    finally:
        conn.close()


def generate_card_bill(card_no, period_start, period_end):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT IFNULL(SUM(amount), 0) AS total FROM CARD_TX WHERE card_no = %s AND tx_date >= %s AND tx_date < DATE_ADD(%s, INTERVAL 1 DAY)", (card_no, period_start, period_end))
            row = cur.fetchone()
            total = row["total"] or 0

            cur.execute("INSERT INTO CARD_BILL (card_no, period_start, period_end, total_amount, due_date, status) VALUES (%s, %s, %s, %s, DATE_ADD(%s, INTERVAL 7 DAY), 'UNPAID')", (card_no, period_start, period_end, total, period_end))
        conn.commit()
        print(f"카드 청구서가 생성되었습니다. 청구 금액: {total}")
    except Exception as e:
        conn.rollback()
        print("카드 청구서 생성 중 오류:", e)
    finally:
        conn.close()


def show_card_bills(card_no):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM CARD_BILL WHERE card_no = %s ORDER BY period_start DESC", (card_no,))
            rows = cur.fetchall()
            if not rows:
                print("해당 카드의 청구서가 없습니다.")
                return
            print("\n--- 카드 청구서 목록 ---")
            for r in rows:
                print(r)
    except Exception as e:
        print("카드 청구서 조회 중 오류:", e)
    finally:
        conn.close()


def pay_card_bill(bill_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM CARD_BILL WHERE bill_id = %s", (bill_id,))
            bill = cur.fetchone()
            if not bill:
                print("청구서를 찾을 수 없습니다.")
                return

            if bill["status"] == "PAID":
                print("이미 납부된 청구서입니다.")
                return

            card_no = bill["card_no"]
            total_amount = bill["total_amount"]

            cur.execute("SELECT a.account_no, a.balance, a.status, a.account_type, u.user_id, u.delinquency_count, u.delinquent_status FROM CARD c JOIN ACCOUNT a ON c.account_no = a.account_no JOIN USER u ON a.user_id = u.user_id WHERE c.card_no = %s FOR UPDATE", (card_no,))
            info = cur.fetchone()
            if not info:
                print("카드에 연결된 계좌/고객 정보를 찾을 수 없습니다.")
                return

            if info["status"] != "ACTIVE":
                print("연결된 계좌가 활성 상태가 아닙니다.")
                return

            if info["account_type"] != "SAVING":
                print("카드 청구는 보통예금 계좌에서만 납부할 수 있습니다.")
                return

            balance = info["balance"] or 0
            user_id = info["user_id"]

            if balance >= total_amount:
                new_balance = balance - total_amount
                cur.execute("UPDATE ACCOUNT SET balance = %s WHERE account_no = %s", (new_balance, info["account_no"]))
                cur.execute("UPDATE CARD_BILL SET status = 'PAID', paid_amount = %s, paid_date = CURDATE() WHERE bill_id = %s", (total_amount, bill_id))
                print("청구서가 정상 납부되었습니다.")
            else:
                print("잔액 부족으로 청구 금액을 납부하지 못했습니다. 연체 처리합니다.")
                cur.execute("UPDATE CARD SET overdue_count = overdue_count + 1 WHERE card_no = %s", (card_no,))
                cur.execute("UPDATE USER SET delinquency_count = delinquency_count + 1, delinquent_status = 'DELINQUENT' WHERE user_id = %s", (user_id,))
                cur.execute("UPDATE CARD_BILL SET status = 'OVERDUE' WHERE bill_id = %s", (bill_id,))

        conn.commit()
    except Exception as e:
        conn.rollback()
        print("청구서 납부/연체 처리 중 오류:", e)
    finally:
        conn.close()


def change_card_status(card_no, new_status):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE CARD SET status = %s WHERE card_no = %s", (new_status, card_no))
            if cur.rowcount == 0:
                print("카드를 찾을 수 없습니다.")
            else:
                print("카드 상태가 변경되었습니다.")
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("카드 상태 변경 중 오류:", e)
    finally:
        conn.close()


def show_card_overdues(card_no=None):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if card_no is None:
                cur.execute("SELECT c.card_no, c.account_no, c.status, c.overdue_count, u.user_id, u.name, u.delinquent_status FROM CARD c JOIN ACCOUNT a ON c.account_no = a.account_no JOIN USER u ON a.user_id = u.user_id WHERE c.overdue_count > 0")
            else:
                cur.execute("SELECT c.card_no, c.account_no, c.status, c.overdue_count, u.user_id, u.name, u.delinquent_status FROM CARD c JOIN ACCOUNT a ON c.account_no = a.account_no JOIN USER u ON a.user_id = u.user_id WHERE c.card_no = %s", (card_no,))
            rows = cur.fetchall()
            if not rows:
                print("연체 카드가 없습니다.")
                return
            print("\n--- 카드 연체 내역 ---")
            for r in rows:
                print(r)
    except Exception as e:
        print("카드 연체 조회 중 오류:", e)
    finally:
        conn.close()
