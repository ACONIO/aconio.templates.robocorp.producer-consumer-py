-- Get opponent information for a specific act.
select
    n.Vorname                       as "first_name",
    n.Name1                         as "last_name",
    CAST(n.geboren as DATE)         as "dob",
    n."Straße"                      as "address",
    n.Ort                           as "city",
    n.Plz                           as "zip_code",
    case 
        when na.Reihung = 1
            then 1
        else 0
    end as "is_primary"
  from Advokat_DB2_DATEN.dbo.NamAkt na
  join Advokat_DB2_DATEN.dbo.Namen n on na.NNr = n.NNr
 where ANr = {act_number}
   and na.Funktion like 'Gegner'
;
