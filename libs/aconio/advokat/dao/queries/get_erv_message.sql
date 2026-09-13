-- Get ERV message by ID
select
    nr.ENr                          as "erv_id",
    a.ANr                           as "act_number",
    CAST(nr.Datum as DATE)          as "date",
    CAST(nr.ErledigtDatum as DATE)  as "completed_date",
    (nr.RACode + '\' + nr.RelName)  as "erv_data_zip"
  from Advokat_DB2_AdvoErv.dbo.Nachrichten nr
  join Advokat_DB2_DATEN.dbo.Akten a on a.AKurz = nr.AKurz
 where nr.ENr = {erv_id}
   order by nr.Datum desc
;