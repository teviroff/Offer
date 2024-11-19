## Opportunity Card Overview
**Name:** {{opp.name}}<br>
**URL:** {{opp.link}}<br>
{% if 'form_link' in opp %}**Form URL:** {{opp.form_link}}<br> {% endif %}

**Desc:** {{opp.description}}<br>

{% if 'short_description' in opp %}**Short_desc:** {{opp.short_description}}<br> {% endif %}

**Provider:** {{opp.provider}}<br>

{% if 'logo' in opp %}**Logo:** {{opp.logo}}<br> {% endif %}

{% if 'requirements' in opp %}
### Requirements
{% if opp.requirements|length == 1 %}
{{opp.requirements[0]}}<br>
{% else %}
{% for req in opp.requirements %}
- {{ req }}
{% endfor %}
{% endif %}
{% endif %}

{% if 'advantages' in opp %}
### Advantages
{% if opp.advantages|length == 1 %}
{{opp.advantages[0]}}<br>
{% else %}
{% for adv in opp.advantages %}
- {{ adv }}
{% endfor %}
{% endif %}
{% endif %}

{% if 'target' in opp %}
### Target
{% if opp.target|length == 1 %}
{{opp.target[0]}}<br>
{% else %}
{% for trg in opp.target %}
- {{ trg }}
{% endfor %}
{% endif %}
{% endif %}

{% if 'discipline' in opp %}
### Discipline
{% if opp.discipline|length == 1 %}
{{opp.discipline[0]}}<br>
{% else %}
{% for dis in opp.discipline %}
- {{ dis }}
{% endfor %}
{% endif %}
{% endif %}

{% if 'place' in opp %}
{% if opp.place|length == 1 %}
**Place:** {{opp.place[0]}}<br>
{% else %}
### Places
{% for plc in opp.place %}
- {{ plc }}
{% endfor %}
{% endif %}
{% endif %}

**Period of internship:** {{opp.period_of_internship}}<br>

{% if 'selection_stages' in opp %}
### Selection Stages
{% for ss in opp.selection_stages %}
1. {{ ss.name }} ({{ss.period}})
{% for ss_obj in ss.objectives %}
    - {{ss_obj}}
{% endfor %}
{% endfor %}
{% endif %}

{% if 'allowance' in opp %}**Allowance:** {{opp.allowance}}<br> {% endif %}
{% if 'expenses' in opp %}**Expenses:** {{opp.expenses}}<br> {% endif %}

{% for adt in opp.additional %}
### {{adt.title}}
{{adt.description}}
{% endfor %}
