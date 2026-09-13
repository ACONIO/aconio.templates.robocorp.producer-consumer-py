-- Get act documents starting with 'VVZ' for a given act number.

select
    Betreff             as "subject",
    VonSB               as "employee",
    CAST(Datum as DATE) as "date"
  from Advokat_DB2_DATEN.dbo.Dokument d
 where ANr = {act_number}
   and Betreff like 'VVZ%'
;