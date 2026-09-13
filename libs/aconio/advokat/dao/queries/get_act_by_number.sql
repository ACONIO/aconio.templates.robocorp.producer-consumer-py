-- Get act information by act number.
select
    a.ANr                               as "act_number",
    a.AKurz                             as "act_short_name",
    a.GZ                                as "case_number",
    a.Status                            as "status",
    CAST(a.ErledDat as DATE)            as "completion_date"
  from Advokat_DB2_DATEN.dbo.Akten a
 where a.ANr = {act_number}
;