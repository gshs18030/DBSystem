DROP DATABASE IF EXISTS bank;
CREATE DATABASE IF NOT EXISTS bank;
USE bank;

-- 1. 직원
DROP TABLE IF EXISTS EMPLOYEE;
CREATE TABLE IF NOT EXISTS EMPLOYEE (
    emp_id int(11) AUTO_INCREMENT,
    name varchar(50),
    phone varchar(20),
    address varchar(200),
    PRIMARY KEY (emp_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 2. 고객
DROP TABLE IF EXISTS USER;
CREATE TABLE IF NOT EXISTS USER (
    user_id int(11) AUTO_INCREMENT,
    name varchar(50),
    phone varchar(20),
    address varchar(200),
    credit_grade varchar(10) DEFAULT 'A',      -- 예: A/B/C 등급
    delinquency_count int DEFAULT 0,
    delinquent_status varchar(20) DEFAULT 'NORMAL',
    emp_id int(11) NOT NULL,
    PRIMARY KEY (user_id),
    CONSTRAINT fk_user_employee FOREIGN KEY (emp_id) REFERENCES EMPLOYEE(emp_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 3. 계좌
DROP TABLE IF EXISTS ACCOUNT;
CREATE TABLE IF NOT EXISTS ACCOUNT (
    account_no int(15),
    user_id  int(11) NOT NULL,
    account_type varchar(20) NOT NULL,   -- SAVING / TIME / INSTALLMENT 등
    status varchar(20) NOT NULL DEFAULT 'ACTIVE',
    balance int(15) NOT NULL DEFAULT 0,
    interest_rate decimal(5,2) DEFAULT 5,
    interest_pay_day int(5),        -- 매월 며칠
    maturity_date date,
    grace_period_days int(5) DEFAULT 7,
    overdue_count int(5) DEFAULT 0,
    PRIMARY KEY (account_no),
    CONSTRAINT fk_account_user FOREIGN KEY (user_id) REFERENCES USER(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 4. 통장 거래
DROP TABLE IF EXISTS PASSBOOK_TX;
CREATE TABLE IF NOT EXISTS PASSBOOK_TX (
    tx_id int(15) AUTO_INCREMENT,
    account_no int(15) NOT NULL,
    tx_date datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tx_type varchar(20) NOT NULL,  -- DEPOSIT / WITHDRAW
    amount int(15) NOT NULL,
    balance_after int(15) NOT NULL,
    PRIMARY KEY (tx_id),
    CONSTRAINT fk_passbook_account FOREIGN KEY (account_no) REFERENCES ACCOUNT(account_no) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 5. 카드
DROP TABLE IF EXISTS CARD;
CREATE TABLE IF NOT EXISTS CARD (
    card_no int(20),
    account_no int(15) NOT NULL UNIQUE,
    status varchar(20) NOT NULL DEFAULT 'ACTIVE',
    overdue_count int(5) DEFAULT 0,
    PRIMARY KEY (card_no),
    CONSTRAINT fk_card_account FOREIGN KEY (account_no) REFERENCES ACCOUNT(account_no) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 6. 카드 거래 내역
DROP TABLE IF EXISTS CARD_TX;
CREATE TABLE IF NOT EXISTS CARD_TX (
    card_tx_id int(20) AUTO_INCREMENT,
    card_no int(20) NOT NULL,
    amount int(15) NOT NULL,
    tx_date datetime NOT NULL,
    merchant varchar(100),
    PRIMARY KEY (card_tx_id),
    CONSTRAINT fk_cardtx_card FOREIGN KEY (card_no) REFERENCES CARD(card_no) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 7. 카드 청구
DROP TABLE IF EXISTS CARD_BILL;
CREATE TABLE IF NOT EXISTS CARD_BILL (
    bill_id int(15) AUTO_INCREMENT,
    card_no int(20) NOT NULL,
    period_start date NOT NULL,
    period_end date NOT NULL,
    total_amount int(15) NOT NULL,
    due_date date NOT NULL,
    status varchar(20) NOT NULL DEFAULT 'UNPAID',
    paid_amount int(15),
    paid_date date,
    PRIMARY KEY (bill_id),
    CONSTRAINT fk_cardbill_card FOREIGN KEY (card_no) REFERENCES CARD(card_no) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 8. 대출
DROP TABLE IF EXISTS LOAN;
CREATE TABLE IF NOT EXISTS LOAN (
    loan_id int(15) AUTO_INCREMENT,
    user_id int(15) NOT NULL,
    principal int(15) NOT NULL,
    interest_rate decimal(5,2) NOT NULL,
    status varchar(20) NOT NULL DEFAULT 'ACTIVE',
    overdue_count int(5) DEFAULT 0,
    PRIMARY KEY (loan_id),
    CONSTRAINT fk_loan_user FOREIGN KEY (user_id) REFERENCES USER(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 9. 대출 상환
DROP TABLE IF EXISTS LOAN_REPAY;
CREATE TABLE IF NOT EXISTS LOAN_REPAY (
    repay_id int(5) AUTO_INCREMENT,
    loan_id int(15) NOT NULL,
    due_date date NOT NULL,
    due_amount int(15) NOT NULL,
    paid_amount int(15),
    paid_date date,
    status varchar(20) NOT NULL DEFAULT 'SCHEDULED',
    PRIMARY KEY (repay_id),
    CONSTRAINT fk_repay_loan FOREIGN KEY (loan_id) REFERENCES LOAN(loan_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 10. 담보
DROP TABLE IF EXISTS COLLATERAL;
CREATE TABLE IF NOT EXISTS COLLATERAL (
    collateral_id int(5) AUTO_INCREMENT,
    loan_id int(15) NOT NULL UNIQUE,    -- 1:1 관계
    collateral_type varchar(20) NOT NULL,      -- CREDIT / DEPOSIT / REAL_ESTATE 등
    object_id varchar(50),
    value int(15),
    PRIMARY KEY (collateral_id),
    CONSTRAINT fk_collateral_loan FOREIGN KEY (loan_id) REFERENCES LOAN(loan_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
