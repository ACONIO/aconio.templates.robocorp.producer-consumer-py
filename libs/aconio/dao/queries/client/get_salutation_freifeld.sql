select per.{salutation_bmd_freifeld} as "salutation"
  from BUERO.PER_PERSON per
 where per.PER_PERSONENID like '{client_bmd_id}'
   and per.PER_FIRMENNR = {client_bmd_company_id}