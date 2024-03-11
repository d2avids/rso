from datetime import date
from competitions.models import Q13EventOrganization, Q18Record, \
    Q18DetachmentReport, CompetitionParticipants, Q18TandemRecord


def calculate_q13_place(objects: list[Q13EventOrganization]) -> int:
    """
    Спортивных мероприятий указано 1 и более - 1 балл, если не указано ни
    одно спортивное мероприятие - 0 баллов.
    Интеллектуальных мероприятий указано 1 и более - 1 балл, если не указано
    ни одно интеллектуальное мероприятие - 0 баллов.
    Творческих мероприятий указано 1 и более - 1 балл, если не указано ни одно
    творческое мероприятие - 0 баллов.
    Волонтерских мероприятий указано 5 и более - 1 балл, от 0 до 4 - 0 баллов.
    Внутренних мероприятий указано 15 и более - 1 балл, от 0 до 14 - 0 баллов.
    Далее баллы по всем (5 шт) видам мероприятий суммируются
    и определяется место.

    Итоговое место:
    5 баллов - 1 место
    4 балла - 2 место
    3 балла - 3 место
    2 балла - 4 место
    1 балл - 5 место
    0 баллов (если указали только 2 волонтерских и 12 внутренних) - 6 место.
    """
    place = 6
    calculations = {
        'Спортивное': 0,
        'Интеллектуальное': 0,
        'Творческое': 0,
        'Волонтерское': 0,
        'Внутреннее': 0
    }
    for obj in objects:
        event_type = obj.event_type
        calculations[event_type] += 1
    if calculations['Спортивное'] > 0:
        place -= 1
    if calculations['Интеллектуальное'] > 0:
        place -= 1
    if calculations['Творческое'] > 0:
        place -= 1
    if calculations['Волонтерское'] > 4:
        place -= 1
    if calculations['Волонтерское'] > 14:
        place -= 1
    return place


def calculate_q18_place():
    today = date.today()
    cutoff_date = date(2024, 6, 15)

    verified_entries = Q18DetachmentReport.objects.filter(is_verified=True)
    solo_entries = []
    tandem_entries = []

    for entry in verified_entries:
        participants_entry = CompetitionParticipants.objects.filter(
            junior_detachment=entry.detachment
        ).first()

        if participants_entry and not participants_entry.detachment:
            category = solo_entries
        else:
            category = tandem_entries
            if participants_entry:
                partner_entry = Q18DetachmentReport.objects.filter(
                    detachment=participants_entry.detachment,
                    is_verified=True
                ).first()
                if partner_entry:
                    entry.participants_number += partner_entry.participants_number
                    if today <= cutoff_date:
                        entry.june_15_detachment_members += partner_entry.june_15_detachment_members
                        entry.save()

        if today <= cutoff_date:
            entry.june_15_detachment_members = entry.detachment.members.count()
            entry.save()

        ratio = entry.participants_number / float(entry.june_15_detachment_members)
        category.append((entry, ratio))

    process_and_save_entries(solo_entries, is_tandem=False)

    process_and_save_entries(tandem_entries, is_tandem=True)


def process_and_save_entries(entries_with_ratio, is_tandem):
    sorted_entries_with_ratio = sorted(entries_with_ratio, key=lambda x: x[1], reverse=True)

    if is_tandem:
        Q18TandemRecord.objects.all().delete()
    else:
        Q18Record.objects.all().delete()

    current_place = 1
    last_ratio = None

    # 500 - 1 место
    # 495, 495 - 2 место
    # 490 - 3 место

    for index, (entry, ratio) in enumerate(sorted_entries_with_ratio):
        if ratio != last_ratio:
            if index != 0:
                current_place = index + 1
        last_ratio = ratio

        if is_tandem:
            participants_entry = CompetitionParticipants.objects.filter(
                junior_detachment=entry.detachment
            ).first()
            if participants_entry:
                Q18TandemRecord.objects.create(
                    detachment=participants_entry.detachment,
                    junior_detachment=entry.detachment,
                    place=current_place
                )
        else:
            Q18Record.objects.create(
                place=current_place,
                detachment=entry.detachment
            )
