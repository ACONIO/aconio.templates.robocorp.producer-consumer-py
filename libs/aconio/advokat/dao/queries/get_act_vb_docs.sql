-- Get act documents indicating a 'Vollzugsbericht' for a given act number.

select 
    Betreff                     as "name",
    CAST(Datum as DATE)         as "date"
  from Advokat_DB2_DATEN.dbo.Dokument d
 where ANr = {act_number}
   and (Betreff like 'VB %' or Betreff like 'VZB %')
;