--- Get employee based on responsibility (e.g. 'Buchhaltung') ---
SELECT
    zus.ZUS_MITARBEITERID AS "bmd_id",
    per_emp.PER_PERSONENNR AS "bmd_number",
    per_emp.PER_FIRMENNR AS "bmd_company_id",
    per_emp.PER_DISPLAY_EMAIL AS "email"
FROM
    BUERO.ZUS_ZUSTAENDIGKEIT zus
    JOIN BUERO.PER_PERSON per_emp ON zus.ZUS_MITARBEITERID = per_emp.PER_PERSONENID
    AND zus.ZUS_MIT_FIRMENNR = per_emp.PER_FIRMENNR
    JOIN BUERO.ZBE_ZUSTAENDIGKEITBEREICH zbe ON zus.ZUS_ZUSTBEREICHLFDNR = zbe.ZBE_ZUSTBEREICHLFDNR
WHERE
    ZUS_PERSONENID = '{client_bmd_id}'
    AND zbe.ZBE_ZUSTBEREICHBEZ in ({responsible_areas})
    AND zus.ZUS_FIRMENNR = {client_bmd_company_id}
    AND zus.ZUS_KATEGORIELFDNR = 1;