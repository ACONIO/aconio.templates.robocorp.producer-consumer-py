-- Get all payment dates from the "Schuldner" (debtor) for a given act number.
select
    CAST(NewDate as DATE) as "date"
  from Advokat_DB2_DATEN.dbo.ZahlungSchuldner 
 where ANr = {act_number}
;