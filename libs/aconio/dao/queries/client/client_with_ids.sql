SELECT
    per.PER_PERSONENID                              AS "bmd_id",
    per.PER_PERSONENNR                              AS "bmd_number",
    per.PER_FIRMENNR                                AS "bmd_company_id",
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
    BUERO.PER_PERSON per
    LEFT JOIN BUERO.KLI_KUNDE_LIEFERANT kli         ON per.PER_PERSONENID = kli.KLI_KLID
                                                    AND per.PER_FIRMENNR = kli.KLI_FIRMENNR
    LEFT JOIN BUERO.BAI_BANKINSTITUTIONSZU bai      ON per.PER_SENDER_BANKINSTLFDNR = bai.BAI_BANKINSTLFDNR
    LEFT JOIN BUERO.ADR_ADRESSE adr                 ON per.PER_ADRESSLFDNR = adr.ADR_ADRESSLFDNR
WHERE
    per.PER_PERSONENID = '{client_bmd_id}'
    AND per.PER_FIRMENNR = {client_bmd_company_id}
;