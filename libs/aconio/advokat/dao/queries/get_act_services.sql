select
    Kommentar               as "name",
    CAST(NewDate as DATE)   as "date",
    Leistung                as "type"
  from Advokat_DB2_DATEN.dbo.Leistung l
 where ANr = {act_number}
;