--- Obtain the contact person of a client based on the "Personenkennzeichen" ---
SELECT
    SUBSTRING(pkz.PKZ_PERSONENID, 7, 11) AS "client_id",
    per.PER_NAME AS "last_name",
    per.PER_VORNAME AS "first_name",
    per.PER_TITEL AS "title_prefix",
    per.PER_TITEL_HINTEN AS "title_suffix",
    per.PER_DISPLAY_EMAIL AS "email",
    anr_pers.ANR_ANREDEBEZ AS "salutation_personal",
    anr_prof.ANR_ANREDEBEZ AS "salutation_professional",
    psz.PSZ_PERSONKZBEZ AS "identifier"
FROM
    BUERO.PKZ_PERSONKONTAKTZU pkz
    LEFT JOIN BUERO.PER_PERSON per ON pkz.PKZ_KONTAKT_PERSONENID = per.PER_PERSONENID
    AND pkz.PKZ_KONTAKT_FIRMENNR = per.PER_FIRMENNR
    LEFT JOIN BUERO.PSZ_PERSONENKZ psz ON pkz.PKZ_PERSONKZNR = psz.PSZ_PERSONKZNR
    AND pkz.PKZ_PERSONENART = psz.PSZ_PERSONENART
    LEFT JOIN BUERO.ADR_ADRESSE adr ON per.PER_ADRESSLFDNR = adr.ADR_ADRESSLFDNR
    LEFT JOIN BUERO.ANR_ANREDE anr_pers ON adr.ADR_PERSOENLICH_ANREDENR = anr_pers.ANR_ANREDENR
    LEFT JOIN BUERO.ANR_ANREDE anr_prof ON adr.ADR_GESCHAEFTLICH_ANREDENR = anr_prof.ANR_ANREDENR
WHERE
    pkz.PKZ_PERSONENID like '{client_bmd_id}'
    AND pkz.PKZ_FIRMENNR = {client_bmd_company_id}
    AND psz.PSZ_PERSONKZBEZ like '{identifier}';