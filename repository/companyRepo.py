from abc import ABC, abstractmethod
from typing import Optional, List

from domain.company import Company
from repository.baseRepo import Repository, DbRepository


class CompanyRepo(Repository[Company], ABC) :
    @abstractmethod
    def get_by_ticker(self, ticker: str) -> Optional[Company]: ...

    @abstractmethod
    def get_by_market_id(self, market_id: str) -> List[Company]: ...

    @abstractmethod
    def update(self, company: Company) -> None: ...

class DbCompanyRepo(CompanyRepo, DbRepository[Company]):
    def add(self, company: Company) -> None:
        sql = """
        INSERT INTO companies (
            id, market_id, name, ticker,
            issued_shares, issued_price,
            current_price, logo_src, par_value, created_at, age,
            remaining_shares
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        company.id,
                        company.market_id,
                        company.name,
                        company.ticker,
                        company.issued_shares,
                        company.issued_price,
                        company.current_price,
                        company.logo_src,
                        company.par_value,
                        company.created_at,
                        company.age,
                        company.remaining_shares,
                    ),
                )

    def adds(self, *companies: Company) -> None:
        for _company in companies:
            self.add(_company)


    def get_by_id(self, company_id: str) -> Optional[Company]:
        sql = """
        SELECT id, market_id, name, ticker,
               issued_shares, issued_price,
               current_price, logo_src, par_value, age,
               remaining_shares
        FROM companies WHERE id = %s
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (company_id,))
                row = cur.fetchone()
        if not row:
            return None
        return Company(
            id=row["id"],
            market_id=row["market_id"],
            name=row["name"],
            age=row["age"],
            issued_shares=row["issued_shares"],
            issued_price=row["issued_price"],
            logo_src=row["logo_src"],
            ticker=row["ticker"],
            par_value=row["par_value"],
            current_price=row["current_price"],
            remaining_shares=row["remaining_shares"],
        )

    def get_by_ticker(self, ticker: str) -> Optional[Company]:
        sql = """
        SELECT id, market_id, name, ticker,
               issued_shares, issued_price,
               current_price, logo_src, par_value, age,
               remaining_shares
        FROM companies WHERE ticker = %s
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (ticker,))
                row = cur.fetchone()
        if not row:
            return None
        return Company(
            id=row["id"],
            market_id=row["market_id"],
            name=row["name"],
            age=row["age"],
            issued_shares=row["issued_shares"],
            issued_price=row["issued_price"],
            logo_src=row["logo_src"],
            ticker=row["ticker"],
            par_value=row["par_value"],
            current_price=row["current_price"],
            remaining_shares=row["remaining_shares"],
        )

    def list_all(self) -> List[Company]:
        sql = """
        SELECT id, market_id, name, ticker,
               issued_shares, issued_price,
               current_price, logo_src, par_value, age,
               remaining_shares
        FROM companies
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
        return [
            Company(
                id=row["id"],
                market_id=row["market_id"],
                name=row["name"],
                age=row["age"],
                issued_shares=row["issued_shares"],
                issued_price=row["issued_price"],
                logo_src=row["logo_src"],
                ticker=row["ticker"],
                par_value=row["par_value"],
                current_price=row["current_price"],
                remaining_shares=row["remaining_shares"],
            )
            for row in rows
        ]

    def get_by_market_id(self, market_id: str) -> List[Company]:
        sql = """
        SELECT id, market_id, name, ticker,
               issued_shares, issued_price,
               current_price, logo_src, par_value, age,
               remaining_shares
        FROM companies
        WHERE market_id = %s
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (market_id,))
                rows = cur.fetchall()
        return [
            Company(
                id=row["id"],
                market_id=row["market_id"],
                name=row["name"],
                age=row["age"],
                issued_shares=row["issued_shares"],
                issued_price=row["issued_price"],
                logo_src=row["logo_src"],
                ticker=row["ticker"],
                par_value=row["par_value"],
                current_price=row["current_price"],
                remaining_shares=row["remaining_shares"],
            )
            for row in rows
        ]

    def remove(self, company_id: str) -> None:
        sql = "DELETE FROM companies WHERE id = %s"
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (company_id,))

    def update(self, company: Company) -> None:
        sql = """
        UPDATE companies
        SET market_id = %s,
            name = %s,
            ticker = %s,
            issued_shares = %s,
            issued_price = %s,
            current_price = %s,
            logo_src = %s,
            par_value = %s,
            age = %s,
            remaining_shares = %s
        WHERE id = %s
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        company.market_id,
                        company.name,
                        company.ticker,
                        company.issued_shares,
                        company.issued_price,
                        company.current_price,
                        company.logo_src,
                        company.par_value,
                        company.age,
                        company.remaining_shares,
                        company.id,
                    ),
                )
