----- Get employee for frist with id. -----
SELECT    
    per_ma.PER_PERSONENID                           AS "bmd_id",
    per_ma.PER_PERSONENNR                           AS "bmd_number",
    fst.FST_MIT_FIRMENNR                            AS "bmd_company_id",
    per_ma.PER_DISPLAY_EMAIL                        AS "email"
FROM
    BUERO.FST_FRIST fst
    LEFT JOIN BUERO.PER_PERSON per_ma               ON fst.FST_MITARBEITERID = per_ma.PER_PERSONENID
                                                    AND fst.FST_MIT_FIRMENNR = per_ma.PER_FIRMENNR
WHERE
    fst.FST_FRISTLFDNR = {bmd_frist_id};