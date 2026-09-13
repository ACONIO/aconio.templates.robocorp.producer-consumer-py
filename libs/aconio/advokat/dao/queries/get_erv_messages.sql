-- Get all ERV entries with the given "Schriftsatz" type that are not yet completed.
-- These entries correspond to acts that need to be processed.

select {limit_clause}
    nr.ENr                          as "erv_id",
    a.ANr                           as "act_number",
    CAST(nr.Datum as DATE)          as "date",
    CAST(nr.ErledigtDatum as DATE)  as "completed_date",
    (nr.RACode + '\' + nr.RelName)  as "erv_data_zip"
  from Advokat_DB2_AdvoErv.dbo.Nachrichten nr
  join Advokat_DB2_DATEN.dbo.Akten a on a.AKurz = nr.AKurz
 where nr.SSTyp like '{ss_type}'
   and nr.SSTyp2 like '{ss_type_detailed}'
   and ('{act_short_name}' = 'None' OR a.AKurz = '{act_short_name}')                -- Optional filter, ommitted if "act_short_name" is 'None'
   and ('{date}' = 'None' OR CAST(nr.Datum as DATE) = TRY_CAST('{date}' as DATE))   -- Optional filter, ommitted if "date" is 'None'
   and ErledigtDatum is null
   order by nr.Datum desc
;