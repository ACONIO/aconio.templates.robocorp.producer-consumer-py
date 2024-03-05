import datetime

from robocorp import workitems

from bot.core import tools
from bot.core import context

@tools.run_function
def run(ctx: context.RunContextReporter, inputs: list[workitems.Input]):
    content = generate_report(
        ctx=ctx,
        items=inputs,
        salutation=ctx.cfg.REPORT_SALUTATION,
        contact_person=ctx.cfg.CONTACT_PERSON
    )

    ctx.outlook.send_email(
        recipients=ctx.cfg.REPORT_RECIPIENTS,
        subject=f"EVZ/KVZ Versand Report {datetime.datetime.today().strftime('%d.%m.%Y')}",
        body=content,
        html_body=True,
        save_as_draft=ctx.cfg.SAVE_AS_DRAFT
    )


def generate_report(ctx: context.RunContextReporter,
                    items: list[workitems.Input],
                    salutation: str,
                    contact_person: str):
    """
    Creates a report for the employee informing them about failed work items and what
    steps need to be done to resolve the issues.
    """

    template = ctx.jinja_env.get_template(ctx.cfg.REPORT_TEMPLATE_FILE)

    infos = {
        i.payload["failed_wi_payload"]["client_id"]: ctx.cfg.CODES[i.payload["failed_wi_code"]]
        for i in items
    }

    return template.render(
        employee_salutation=salutation,
        infos=infos,
        contact_person=contact_person
    )
