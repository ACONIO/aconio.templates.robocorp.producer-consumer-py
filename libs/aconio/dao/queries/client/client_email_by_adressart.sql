----- Obtain the E-Mail and ID of a client and the given 'Adressart' -----
SELECT
    ema.EMA_EMAILADRESSE AS "email"
FROM
    BUERO.PER_PERSON per
    LEFT JOIN BUERO.EMA_EMAIL ema ON per.PER_PERSONENID = ema.EMA_PERSONENID
    AND per.PER_FIRMENNR = ema.EMA_FIRMENNR
    LEFT JOIN BUERO.EMT_EMAILART eat ON ema.EMA_EMAILARTNR = eat.EMT_EMAILARTNR
WHERE
    per.PER_PERSONENID like '{client_bmd_id}'
    AND eat.EMT_EMTBEZ like '{email_address_type}'
    AND per.PER_FIRMENNR = {client_bmd_company_id};