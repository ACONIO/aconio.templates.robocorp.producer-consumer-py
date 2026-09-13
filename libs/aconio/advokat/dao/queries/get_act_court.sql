-- Get the associated court data for a given act number.
select
    CONCAT(n.Name1, n.Name2, n.Name3, n.Name4)  as "name",
    n."Straße"                                  as "address",
    n.Ort                                       as "city",
    n.Plz                                       as "zip_code"
  from Advokat_DB2_DATEN.dbo.Akten a
  join Advokat_DB2_DATEN.dbo.Namen n on a.Gericht1 = n.NNr
 where ANr = {act_number}
;