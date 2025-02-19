----- Obtain BMD 'Fristen' relevant for EVZ/KVZ -----
SELECT
    per.PER_PERSONENID                              AS "bmd_id",
    per.PER_PERSONENNR                              AS "bmd_number",
    fst.FST_PER_FIRMENNR                            AS "bmd_company_id",
    kli.KLI_QUOTEN_FIRMENNR                         AS "bmd_tax_company_id",
    per.PER_VORNAME                                 AS "first_name",
    per.PER_NAME                                    AS "name",
    adr.ADR_SPRACHNR                                AS "language",
    per.PER_FSTEUERNR                               AS "tax_number",
    bai.BAI_IBAN                                    AS "iban",
    bai.BAI_SWIFTCODE                               AS "bic",
    per.PER_DISPLAY_EMAIL                           AS "display_email",
    per.PER_ZUSATZNAME                              AS "additional_name"
FROM
    BUERO.FST_FRIST fst
    LEFT JOIN BUERO.PER_PERSON per                  ON fst.FST_PERSONENID = per.PER_PERSONENID
                                                    AND fst.FST_PER_FIRMENNR = per.PER_FIRMENNR
    LEFT JOIN BUERO.KLI_KUNDE_LIEFERANT kli         ON per.PER_PERSONENID = kli.KLI_KLID
                                                    AND per.PER_FIRMENNR = kli.KLI_FIRMENNR
    LEFT JOIN BUERO.ADR_ADRESSE adr                 ON per.PER_ADRESSLFDNR = adr.ADR_ADRESSLFDNR
    LEFT JOIN BUERO.BAI_BANKINSTITUTIONSZU bai      ON per.PER_SENDER_BANKINSTLFDNR = bai.BAI_BANKINSTLFDNR
WHERE
    fst.FST_FRISTLFDNR = {bmd_frist_id};