from utils.user_query import (
    create_user,
    get_user_by_id,
    update_user_info,
    recalc_credit_for_user,
    show_user_status_summary
)

from utils.account_query import (
    create_account,
    delete_account,
    show_account_info,
    list_accounts_by_user,
    change_account_status
)

from utils.passbook_query import (
    deposit,
    withdraw,
    show_passbook_by_account
)

from utils.card_query import (
    create_card,
    add_card_tx,
    generate_card_bill,
    pay_card_bill,
    show_card_info,
    show_card_bills,
    change_card_status,
    show_card_overdues
)

from utils.loan_query import (
    create_loan,
    show_loan_info,
    create_repay_schedule,
    pay_loan_repay,
    show_loan_overdues,
    exercise_collateral
)

from utils.employee_query import (
    create_employee,
    list_employees,
    freeze_account,
    unfreeze_account,
    list_freeze_deliq
)

from utils.update_query import (
    saving_interest_add,
    time_deposit_maturity,
    installment_maturity,
    auto_create_card_bill,
    loan_overdue_check,
    card_overdue_check
)

def input_int(prompt: str) -> int:
    while True:
        s = input(prompt).strip()
        try:
            return int(s)
        except ValueError:
            print("정수를 입력해주세요.")

def customer_menu():
    while True:
        print("\n[고객 관리 메뉴]")
        print("0. 이전 메뉴로")
        print("1. 고객 등록")
        print("2. 고객 정보 조회")
        print("3. 고객 정보 수정")
        print("4. 고객 신용등급 산정/갱신")
        print("5. 고객 연체/대출/카드 상태 요약 조회")

        choice = input("선택: ").strip()

        if choice == "0":
            break

        elif choice == "1":
            print("\n[고객 등록]")
            name = input("이름: ").strip()
            phone = input("연락처: ").strip()
            address = input("주소: ").strip()
            emp_id = input_int("담당 직원 ID: ")
            create_user(name, phone, address, emp_id)

        elif choice == "2":
            print("\n[고객 정보 조회]")
            user_id = input_int("고객 ID: ")
            user = get_user_by_id(user_id)
            if not user:
                print("해당 고객이 존재하지 않습니다.")
            else:
                print("--- 고객 정보 ---")
                for k, v in user.items():
                    print(f"{k}: {v}")

        elif choice == "3":
            print("\n[고객 정보 수정]")
            user_id = input_int("고객 ID: ")
            print("수정하지 않을 항목은 그냥 Enter를 누르세요.")
            name = input("이름(변경 시 입력): ").strip()
            phone = input("연락처(변경 시 입력): ").strip()
            address = input("주소(변경 시 입력): ").strip()

            update_user_info(user_id, name, phone, address)

        elif choice == "4":
            print("\n[고객 신용등급 산정/갱신]")
            user_id = input_int("고객 ID: ")
            recalc_credit_for_user(user_id)

        elif choice == "5":
            print("\n[고객 상태 요약 조회]")
            user_id = input_int("고객 ID: ")
            show_user_status_summary(user_id)

        else:
            print("잘못된 입력입니다.")

def account_menu():
    while True:
        print("\n[계좌 관리 메뉴]")
        print("0. 이전 메뉴로")
        print("1. 계좌 개설")
        print("2. 계좌 해지")
        print("3. 계좌 정보 조회")
        print("4. 계좌 상태 변경 (ACTIVE/FROZEN/CLOSED 등)")
        print("5. 특정 고객의 계좌 목록 조회")

        choice = input("선택: ").strip()

        if choice == "0":
            break

        elif choice == "1":
            print("\n[계좌 개설]")
            user_id = input_int("고객 ID: ")
            account_no = input_int("계좌 번호(숫자): ")
            print("계좌 유형 예시: SAVING(보통예금), TIME(정기예금), INSTALLMENT(적금)")
            account_type = input("계좌 유형: ").strip().upper()
            init_balance = input_int("초기 입금액: ")
            interest_pay_day = None
            maturity_date = None
            if account_type == "SAVING":
                interest_pay_day = input_int("이자 지급일: ")
            elif account_type in ("TIME", "INSTALLMENT"):
                maturity_date = input("만기일 (YYYY-MM-DD): ").strip()
            else:
                print("알 수 없는 계좌 유형입니다. (SAVING / TIME / INSTALLMENT 중 하나)")
                continue
            create_account(user_id, account_no, account_type, init_balance, interest_pay_day, maturity_date)

        elif choice == "2":
            print("\n[계좌 해지]")
            account_no = input_int("계좌 번호: ")
            delete_account(account_no)

        elif choice == "3":
            print("\n[계좌 정보 조회]")
            account_no = input_int("계좌 번호: ")
            show_account_info(account_no)

        elif choice == "4":
            print("\n[계좌 상태 변경]")
            account_no = input_int("계좌 번호: ")
            new_status = input("새 상태 (예: ACTIVE/FROZEN/CLOSED): ").strip().upper()
            change_account_status(account_no, new_status)

        elif choice == "5":
            print("\n[고객의 계좌 목록 조회]")
            user_id = input_int("고객 ID: ")
            list_accounts_by_user(user_id)

        else:
            print("잘못된 입력입니다.")

def card_menu():
    while True:
        print("\n[카드 관리 메뉴]")
        print("0. 이전 메뉴로")
        print("1. 카드 발급 (보통예금 계좌에 연동)")
        print("2. 카드 정보 조회")
        print("3. 카드 사용 내역 등록 (결제)")
        print("4. 카드 청구서 생성 (기간 지정)")
        print("5. 카드 청구서 목록 조회")
        print("6. 카드 청구서 납부")
        print("7. 카드 상태 변경 (정지/해지 등)")
        print("8. 카드 연체 내역 조회 (전체/특정 카드)")

        choice = input("선택: ").strip()

        if choice == "0":
            break

        elif choice == "1":
            print("\n[카드 발급]")
            account_no = input_int("연동할 보통예금 계좌번호: ")
            create_card(account_no)

        elif choice == "2":
            print("\n[카드 정보 조회]")
            card_no = input_int("카드 번호: ")
            show_card_info(card_no)

        elif choice == "3":
            print("\n[카드 사용 내역 등록]")
            card_no = input_int("카드 번호: ")
            amount = input_int("결제 금액: ")
            merchant = input("가맹점 이름: ").strip()
            add_card_tx(card_no, amount, merchant)

        elif choice == "4":
            print("\n[카드 청구서 생성]")
            card_no = input_int("카드 번호: ")
            period_start = input("청구 기간 시작일 (YYYY-MM-DD): ").strip()
            period_end = input("청구 기간 종료일 (YYYY-MM-DD): ").strip()
            generate_card_bill(card_no, period_start, period_end)

        elif choice == "5":
            print("\n[카드 청구서 목록 조회]")
            card_no = input_int("카드 번호: ")
            show_card_bills(card_no)

        elif choice == "6":
            print("\n[카드 청구서 납부]")
            bill_id = input_int("납부할 청구서 ID: ")
            pay_card_bill(bill_id)

        elif choice == "7":
            print("\n[카드 상태 변경]")
            card_no = input_int("카드 번호: ")
            new_status = input("새 상태 (예: ACTIVE/STOPPED/CLOSED): ").strip().upper()
            change_card_status(card_no, new_status)

        elif choice == "8":
            print("\n[카드 연체 내역 조회]")
            print("1. 전체 카드 연체 내역")
            print("2. 특정 카드 연체 내역")
            sub = input("선택: ").strip()
            if sub == "1":
                show_card_overdues(None)
            elif sub == "2":
                card_no = input_int("카드 번호: ")
                show_card_overdues(card_no)
            else:
                print("잘못된 입력입니다.")

        else:
            print("잘못된 입력입니다.")


def passbook_menu():
    while True:
        print("\n[통장 / 입출금 메뉴]")
        print("0. 이전 메뉴로")
        print("1. 입금")
        print("2. 출금")
        print("3. 계좌별 통장 내역 조회")

        choice = input("선택: ").strip()

        if choice == "0":
            break

        elif choice == "1":
            print("\n[입금]")
            account_no = input_int("계좌 번호: ")
            amount = input_int("입금액: ")
            deposit(account_no, amount)

        elif choice == "2":
            print("\n[출금]")
            account_no = input_int("계좌 번호: ")
            amount = input_int("출금액: ")
            withdraw(account_no, amount)

        elif choice == "3":
            print("\n[통장 내역 조회]")
            account_no = input_int("계좌 번호: ")
            show_passbook_by_account(account_no)

        else:
            print("잘못된 입력입니다.")

def loan_menu():
    while True:
        print("\n[대출 / 담보 관리 메뉴]")
        print("0. 이전 메뉴로")
        print("1. 대출 신청")
        print("2. 대출 정보 조회")
        print("3. 대출 상환 일정 생성")
        print("4. 대출 상환 처리 (납부)")
        print("5. 대출 연체 현황 조회")
        print("6. 담보권 행사 처리")

        choice = input("선택: ").strip()

        if choice == "0":
            break

        elif choice == "1":
            print("\n[대출 신청]")
            user_id = input_int("고객 ID: ")
            principal = input_int("대출 원금: ")
            interest_rate = input_int("이자율(예: 3): ")
            print("담보 유형 예시: CREDIT / DEPOSIT / REAL_ESTATE")
            collateral_type = input("담보 유형: ").strip().upper()
            collateral_object_id = None
            collateral_value = None
            if(collateral_type != "CREDIT"):
                collateral_object_id = input("담보 식별자(예: 계좌번호/부동산ID 등): ").strip()
                collateral_value = input_int("담보 평가 금액: ")
            create_loan(
                user_id,
                principal,
                interest_rate,
                collateral_type,
                collateral_object_id,
                collateral_value
            )

        elif choice == "2":
            print("\n[대출 정보 조회]")
            loan_id = input_int("대출 ID: ")
            show_loan_info(loan_id)

        elif choice == "3":
            print("\n[대출 상환 일정 생성]")
            loan_id = input_int("대출 ID: ")
            num_terms = input_int("상환 회차 수: ")
            term_amount = input_int("회차별 상환 금액: ")
            create_repay_schedule(loan_id, num_terms, term_amount)

        elif choice == "4":
            print("\n[대출 상환 처리]")
            repay_id = input_int("상환 일정 ID: ")
            pay_amount = input_int("납부 금액: ")
            pay_loan_repay(repay_id, pay_amount)

        elif choice == "5":
            print("\n[대출 연체 현황 조회]")
            print("1. 전체 대출 연체")
            print("2. 특정 고객의 대출 연체")
            sub = input("선택: ").strip()
            if sub == "1":
                show_loan_overdues(None)
            elif sub == "2":
                user_id = input_int("고객 ID: ")
                show_loan_overdues(user_id)
            else:
                print("잘못된 입력입니다.")

        elif choice == "6":
            print("\n[담보권 행사 처리]")
            loan_id = input_int("대출 ID: ")
            exercise_collateral(loan_id)

        else:
            print("잘못된 입력입니다.")

def employee_menu():
    while True:
        print("\n[직원 / 관리 기능 메뉴]")
        print("0. 이전 메뉴로")
        print("1. 직원 등록")
        print("2. 직원 목록 조회")
        print("3. 계좌 동결")
        print("4. 계좌 동결 해제")
        print("5. 동결 / 연체 계좌 목록 조회")

        choice = input("선택: ").strip()

        if choice == "0":
            break

        elif choice == "1":
            print("\n[직원 등록]")
            name = input("이름: ").strip()
            phone = input("연락처: ").strip()
            address = input("주소: ").strip()
            create_employee(name, phone, address)

        elif choice == "2":
            print("\n[직원 목록 조회]")
            list_employees()

        elif choice == "3":
            print("\n[계좌 동결]")
            account_no = input_int("계좌 번호: ")
            freeze_account(account_no)

        elif choice == "4":
            print("\n[계좌 동결 해제]")
            account_no = input_int("계좌 번호: ")
            unfreeze_account(account_no)

        elif choice == "5":
            print("\n[동결 / 연체 계좌 목록 조회]")
            list_freeze_deliq()

        else:
            print("잘못된 입력입니다.")

def batch_menu():
    while True:
        print("\n[일괄 처리 메뉴]")
        print("0. 이전 메뉴로")
        print("1. 보통예금 이자 처리")
        print("2. 정기예금 만기 처리")
        print("3. 적금 만기 처리")
        print("4. 카드 청구서 자동 생성 (해당 날짜의 사용 내역 기준)")
        print("5. 대출 연체 및 고객 상태 갱신 (해당 날짜가 상환일인 건만)")
        print("6. 카드 연체 처리 (해당 날짜가 납부 기한인 청구서)")

        choice = input("선택: ").strip()

        if choice == "0":
            break

        elif choice == "1":
            print("\n[보통예금 이자 처리]")
            target_date = input("이자를 처리할 날짜 (YYYY-MM-DD): ").strip()
            saving_interest_add(target_date)

        elif choice == "2":
            print("\n[정기예금 만기 처리]")
            target_date = input("만기/이자 처리 날짜 (YYYY-MM-DD): ").strip()
            time_deposit_maturity(target_date)

        elif choice == "3":
            print("\n[적금 만기 처리]")
            target_date = input("적금 처리 날짜 (YYYY-MM-DD): ").strip()
            installment_maturity(target_date)

        elif choice == "4":
            print("\n[카드 청구서 자동 생성]")
            target_date = input("청구 기준 날짜 (YYYY-MM-DD): ").strip()
            auto_create_card_bill(target_date)

        elif choice == "5":
            print("\n[대출 연체 및 고객 상태 갱신]")
            target_date = input("연체 여부를 판단할 상환일 (YYYY-MM-DD): ").strip()
            loan_overdue_check(target_date)
        
        elif choice == "6":
            print("\n[카드 연체 처리]")
            target_date = input("연체 여부를 판단할 납부 기한일 (YYYY-MM-DD): ").strip()
            card_overdue_check(target_date)

        else:
            print("잘못된 입력입니다.")

def main_menu():
    while True:
        print("\n=== 은행 관리 시스템 ===")
        print("0. 종료")
        print("1. 고객 관리")
        print("2. 계좌 관리")
        print("3. 카드 관리")
        print("4. 통장 / 입출금 관리")
        print("5. 대출 / 담보 관리")
        print("6. 직원 / 관리 기능")
        print("7. 일괄 처리(이자/연체/자동해지 등)")

        choice = input("메뉴 선택: ").strip()

        if choice == "0":
            print("프로그램을 종료합니다.")
            break
        elif choice == "1":
            customer_menu()
        elif choice == "2":
            account_menu()
        elif choice == "3":
            card_menu()
        elif choice == "4":
            passbook_menu()
        elif choice == "5":
            loan_menu()
        elif choice == "6":
            employee_menu()
        elif choice == "7":
            batch_menu()
        else:
            print("잘못된 입력입니다. 다시 선택해주세요.")


if __name__ == "__main__":
    main_menu()
