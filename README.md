# 1. 프로젝트 개요
### 1-1. 목표
- Python, MySQL을 활용한 은행 관리 서비스 DBMS 개발

### 1-2. 제약 사항
- 다음과 같은 **기본 entity와 요구 사항**을 반드시 포함해야 함
  - 기본 entity: 관리자, 사용자, 계좌
  - 요구사항:
    1. 관리자는 각 사용자의 계좌 입출금 내역을 관리
    2. 사용자는 자신의 계좌를 개설하거나 삭제할 수 있다
    3. 사용자는 자신의 계좌에 돈을 입금할 수 있다
    4. 사용자는 자신의 계좌에서 돈을 출금할 수 있다

- 위 사항들 외 다른 개체와 요구사항 추가 가능

- 설정한 entity와 요구사항을 바탕으로 ER Diagram, Relational Diagram을 설계하고 SQL을 이용하여 데이터베이스 스키마를 생성, 그 후 Python으로 DBMS 응용 프로그램을 개발

- 개발하는 응용 프로그램은 **insert, delete, select, update 기능**을 반드시 포함해야 함

- 모든 function들은 **CLI에서 수행**되어야 함
---
# 2. 프로젝트 설계
### 2-1. 기능 요구사항 설정
1. 직원은 각 사용자의 계좌 입출금 내역이 데이터로서 통장에 저장되도록 하고, 사용자가 열람할 수 있도록 한다.
2. 사용자는 자신의 계좌를 개설하거나 삭제할 수 있다.
3. 사용자는 자신의 계좌에 돈을 입/출금 할 수 있다.
4. 직원은 사용자의 정보를 바탕으로 사용자의 신용등급을 결정한다.
5. 계좌는 보통예금, 정기예금, 적금계좌 등이 있다.
6. 보통예금계좌는 자유롭게 입출금이 가능하며, 일정 기간마다 이자가 지급된다. 이 계좌에는 신용카드를 등록할 수 있으며, 카드로 소비한 총 금액을 기간마다 계좌에서 카드사로 송금한다. 계좌에 해당 금액이 없을 시 고객의 연체 횟수가 증가한다.
7. 정기예금계좌는 입출금이 불가능하며, 만기 시 정해진 이자를 지급한다.
8. 적금계좌는 만기 일자까지 출금이 불가능하며, 일정 기간마다 입금을 해야 하고, 일정 기간마다 이자가 지급된다. 납입이 늦어도 유예기간 안에만 입금하면 괜찮으며, 유예기간이 지나면 연체 횟수가 증가한다. 연체 횟수가 일정 수준을 넘어가면 적금이 자동 해지된다.
9. 해지된 적금/정기예금은 보통예금의 이자율을 따른다.
10. 사용자는 은행으로부터 대출을 받을 수 있으며, 담보가 필요하다.
11. 담보에는 신용, 예금/적금, 부동산 등이 있다. 신용등급이 낮을 경우 신용 대출은 불가능하다.
12. 대출이 연체될 경우 신용등급이 하락하고, 사용자를 연체자로 분류한다. 이 동안에는 새로 대출을 받거나 카드를 발급하는 것이 금지된다. 장기 연체자에게는 직원이 담보권을 사용할 수 있다.
13. 직원은 사용자의 요청 또는 이상거래가 발생했을 때 계좌를 동결 상태로 만들 수 있다.
14. 주기적으로 발생하는 이자 등에 대해서는 자동적으로 처리한다.

### 2-2. Entity/Attribute 설정
1. 직원: 직원id (PK), 이름, 연락처, 주소
2. 사용자: 사용자id (PK), 이름, 연락처, 주소, 신용 등급, 연체 횟수, 연체 상태
3. 계좌: 계좌번호 (PK), 사용자id (FK), 계좌 종류, 계좌 상태, 잔액, 이자율, 이자 지급일, 이자 지급 주기, 만기일, 유예기간, 연체 횟수
4. 통장: 거래id (PK), 거래 날짜, 거래 종류, 거래 금액, 계좌번호 (FK), 거래 후 잔액
5. 카드: 카드번호 (PK), 계좌번호 (FK), 상태, 연체 횟수
6. 카드 내역: 카드거래id (PK), 카드번호 (FK), 금액, 거래일자, 가맹점명
7. 카드 청구: 카드청구id (PK), 카드번호 (FK), 집계시작일, 집계종료일, 총액, 납부기한, 상태, 납부금액, 납부일자
8. 대출: 대출id (PK), 사용자id (FK), 원금, 이자율, 상태, 연체 횟수
9. 대출 상환: 상환id (PK), 대출id (FK), 상환액, 상환일자, 상태
10. 담보: 담보id (PK), 대출id (FK), 종류, 담보 자체 id, 가치

### 2-3. ER Diagram
<img width="800" height="450" alt="image" src="https://github.com/user-attachments/assets/83d98ddf-aedc-48ee-8f68-a26e1582420c" />

### 2-4. Relational Diagram
<img width="800" height="450" alt="image" src="https://github.com/user-attachments/assets/f257ca62-c800-4e9e-80cb-a6a14083086d" />

---
# 3. 응용 프로그램 구현
- 실제 은행의 운영 방식이 최대한 반영되도록 구현하려 하였고, 정확한 산정 방식을 모르는 것들(신용등급 등)이나 정밀한 수치(이자율)등 동일하게 구현하기 힘들다고 판단한 것들은 간소화하였다.
### 3-1. Dump 파일
- 데이터베이스 초기화를 용이하게 하기 위해 SQL DDL로 작성한 초기 DB 구조 설정 파일.
- database, table등을 처음부터 다시 생성하고, 각 attribute에 필요한 속성들(Primary key, Default, Constraint 등)을 설정해 준다.
- source dump.sql로 실행 가능.

### 3-2. Main.py
- CLI에서 DB를 관리할 수 있도록 조작 메뉴를 출력하고 입력에 따라 메뉴 이동 및 데이터 갱신을 진행.
- 0번을 상위 메뉴로 돌아가는 것으로 고정하고, 처리할 작업들을 카테고리화하여 하위 메뉴를 생성함.
<img width="400" height="320" alt="image" src="https://github.com/user-attachments/assets/1c87382a-8825-4a1b-83eb-002161e73de6" />

### 3-3. 기능 구현
- Employee_query.py
  1. Create_employee: INSERT INTO를 사용하여 직원 tuple을 생성.
  2. List_employees: SELECT FROM을 사용하여 직원 정보 목록 출력.
  3. Freeze_account: UPDATE SET WHERE를 사용하여 계좌를 동결.
  4. Unfreeze_account: UPDATE SET WHERE를 사용하여 계좌를 활성화.
  5. List_freeze_deliq: SELECT FROM WHERE를 사용하여 동결/연체 목록 출력.
- User_query.py
  1. Create_user: INSERT INTO를 사용하여 고객 tuple을 생성.
  2. Get_user_by_id: SELECT FROM WHERE를 사용하여 고객 정보를 열람.
  3. Update_user_info: UPDATE SET WHERE를 사용하여 고객의 정보를 수정.
  4. Recalc_credit_for_user: SELECT FROM WHERE, UPDATE SET WHERE를 사용하여 고객의 신용 등급을 갱신. (연체 횟수가 2 이상이면 B, 4 이상이면 C로 단순화)
  5. Show_user_status_summary: SELECT FROM (JOIN ON) WHERE를 사용하여 고객의 계좌/카드/대출 정보를 한번에 열람.
- Account_query.py
  1. Create_account: INSERT INTO를 사용하여 계좌 tuple을 생성.
  2. Delete_account: DELETE FROM WHERE를 사용하여 계좌 tuple을 삭제. FK로 연관된 tuple들도 on delete cascade로 자동 삭제.
  3. Show_account_info: SELECT FROM WHERE를 사용하여 계좌 정보를 확인.
  4. List_accounts_by_user: SELECT FROM WHERE를 사용하여 고객의 계좌 목록을 나열.
  5. Change_account_status: UPDATE SET WHERE를 사용하여 계좌의 상태를 변경.
- Card_query.py
  1. Create_card: SELECT FROM (JOIN ON) WHERE, INSERT INTO를 사용하여 카드 tuple을 생성. 계좌 하나당 카드 하나만 생성 가능하며, 카드 번호는 계좌번호와 동일.
  2. Show_card_info: SELECT FROM JOIN ON WHERE를 사용하여 카드의 정보를 열람.
  3. Add_card_tx: SELECT FROM WHERE, INSERT INTO를 사용하여 카드 결제 내역 tuple을 생성.
  4. Generate_card_bill: SELECT FROM WHERE, INSERT INTO를 사용하여 해당 기간의 카드 청구서 tuple을 생성.
  5. Show_card_bills: SELECT FROM WHERE ORDER BY를 사용하여 카드 청구서 목록을 조회할 수 있도록 하였습니다.
  6. Pay_card_bill: SELECT FROM (JOIN ON) WHERE, UPDATE SET WHERE를 사용하여 카드 청구를 납부. 계좌에 잔액이 부족하면 연체 처리.
  7. Change_card_status: UPDATE SET WHERE를 사용하여 카드 상태를 변경.
  8. Show_card_overdues: SELECT FROM JOIN ON WHERE를 사용하여 카드 연체 내역을 조회.
- Passbook_query.py
  1. Deposit: SELECT FROM WHERE, UPDATE SET WHERE, INSERT INTO를 사용하여 계좌에 입금을 하고 통장에 기록.
  2. Withdraw: SELECT FROM WHERE, UPDATE SET WHERE, INSERT INTO를 사용하여 계좌에서 출금을 하고 통장에 기록.
  3. Show_passbook_by_account: SELECT FROM WHERE ORDER BY를 사용하여 통장 거래 내역을 조회.
- Loan_query.py
  1. Create_loan: SELECT FROM WHERE, INSERT INTO를 사용하여 대출 tuple과 필요시 담보 tuple도 생성.
  2. Show_loan_info: SELECT FROM (JOIN ON) WHERE를 사용하여 해당 대출에 대한 정보를 열람.
  3. Create_repay_schedule: INSERT INTO를 사용하여 상환 일정 tuple을 생성.
  4. Pay_loan_repay: SELECT FROM WHERE, UPDATE SET WHEN THEN ELSE WHERE를 사용하여 상환 일정에 상환 진행.
  5. Show_loan_overdues: SELECT FROM JOIN ON WHERE를 사용하여 대출 연체 내역을 조회.
  6. Exercise_collateral: SELECT FROM WHERE, UPDATE SET WHERE를 사용하여 담보권 행사.
- Update_query.py
  1. Saving_interest_add: SELECT FROM WHERE, UPDATE SET WHERE, INSERT INTO를 사용하여 보통예금 계좌에 이자를 정산.
  2. 
