--- Obtain the E-Mail and ID of the 'Sachbearbeiter' from a given client ---
SELECT
    per_emp.PER_PERSONENID AS "bmd_id",
    per_emp.PER_PERSONENNR AS "bmd_number",
    per_emp.PER_FIRMENNR AS "bmd_company_id",
    per_emp.PER_DISPLAY_EMAIL AS "email"
FROM
    BUERO.PER_PERSON per
    JOIN BUERO.PER_PERSON per_emp ON per.PER_SACHB_MITARBEITERID = per_emp.PER_PERSONENID
    AND per.PER_SACHB_FIRMENNR = per_emp.PER_FIRMENNR
WHERE
    per.PER_PERSONENID like '{client_bmd_id}'
    AND per.PER_FIRMENNR = {client_bmd_company_id};