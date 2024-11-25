select per.PER_DISPLAY_EMAIL as "display_email"
  from BUERO.PER_PERSON per
where per.PER_PERSONENID like '{client_bmd_id}'
  and per.PER_FIRMENNR = {client_bmd_company_id}