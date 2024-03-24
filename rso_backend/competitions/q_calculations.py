from datetime import date
import logging
from competitions.models import Q13EventOrganization, Q18Ranking, \
    Q18DetachmentReport, CompetitionParticipants, Q18TandemRanking, Q19Ranking, Q19Report, Q19TandemRanking, Q1Report, Q7Ranking, Q7Report, Q7TandemRanking


logger = logging.getLogger('tasks')


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


def calculate_q18_place(competition_id):
    today = date.today()
    cutoff_date = date(2024, 6, 15)

    logger.info(f'Сегодняшняя дата: {cutoff_date}')

    verified_entries = Q18DetachmentReport.objects.filter(is_verified=True)
    logger.info(f'Получили верифицированные отчеты: {verified_entries.count()}')

    solo_entries = []
    tandem_entries = []

    for entry in verified_entries:
        participants_entry = CompetitionParticipants.objects.filter(
            junior_detachment=entry.detachment
        ).first()
        partner_entry = None
        if participants_entry and not participants_entry.detachment:
            category = solo_entries
            logger.info(f'Отчет {entry} - соло участник')
        elif participants_entry:
            logger.info(f'Отчет {entry} - тандем участник')
            category = tandem_entries
            if participants_entry:
                partner_entry = Q18DetachmentReport.objects.filter(
                    detachment=participants_entry.detachment,
                    is_verified=True
                ).first()
                if partner_entry:
                    logger.info(
                        f'Для отчета {entry} найден '
                        f'партнерский отчет: {partner_entry}'
                    )
        elif not participants_entry:
            participants_entry = CompetitionParticipants.objects.filter(
                detachment=entry.detachment
            ).first()
            partner_entry = entry
            if participants_entry:
                category = tandem_entries
                entry = Q18DetachmentReport.objects.filter(
                    detachment=participants_entry.junior_detachment,
                    is_verified=True
                ).first()
                if entry:
                    logger.info(
                        f'Для отчета {partner_entry} найден '
                        f'партнерский отчет: {entry}'
                    )
        if today <= cutoff_date:
            logger.info(
                f'Сегодняшняя дата {today} меньше '
                f'cutoff date: {cutoff_date}. '
                f'Обновляем кол-во участников.'
            )
            calculate_detachment_members(entry, partner_entry)

        entry.score = entry.participants_number / entry.june_15_detachment_members
        entry.save()

        if partner_entry:
            partner_entry.score = partner_entry.participants_number / partner_entry.june_15_detachment_members
            partner_entry.save()
            tuple_to_append = (entry, partner_entry, entry.score + partner_entry.score)
            if tuple_to_append not in category:
                category.append(tuple_to_append)
        else:
            category.append((entry, entry.score))

    if solo_entries:
        logger.info('Есть записи для соло-участников. Удаляем записи из таблицы Q18 Ranking')
        Q18Ranking.objects.all().delete()
        solo_entries.sort(key=lambda entry: entry[1])
        place = len(solo_entries)
        for entry in solo_entries:
            logger.info(
                f'Отчет {entry[0]} занимает {place} место'
            )
            Q18Ranking.objects.create(
                detachment=entry[0].detachment,
                place=place,
                competition_id=competition_id
            )
            place -= 1

    if tandem_entries:
        logger.info('Есть записи для тандем-участников. Удаляем записи из таблицы Q18 TandemRanking')
        Q18TandemRanking.objects.all().delete()
        tandem_entries.sort(key=lambda entry: entry[2])
        place = len(tandem_entries)
        for entry in tandem_entries:
            logger.info(
                f'Отчеты {entry[0]} и {entry[1]} занимают {place} место'
            )
            Q18TandemRanking.objects.create(
                junior_detachment=entry[0].detachment,
                detachment=entry[1].detachment,
                place=place,
                competition_id=competition_id
            )
            place -= 1


def calculate_detachment_members(entry, partner_entry=None):
    entry.june_15_detachment_members = entry.detachment.members.count() + 1
    entry.save()
    if partner_entry:
        partner_entry.june_15_detachment_members = partner_entry.detachment.members.count() + 1
        partner_entry.save()


def calculate_place(
        competition_id, model_report, model_ranking, model_tandem_ranking,
        reverse=True
):
    """
    Таска для расчета рейтингов Q7 - Q12 и Q20.

    Для celery-beat, считает вплоть до 15 октября 2024 года.
    :param competition_id: id конкурса
    :param model_report: модель отчета
    :param model_ranking: модель рейтинга старт
    :param model_tandem_ranking: модель тандем рейтинга
    :param reverse: True - чем больше очков, чем выше место в рейтинге,
                    False - чем меньше очков, тем выше место.
    """
    today = date.today()
    cutoff_date = date(2024, 10, 15)

    if today >= cutoff_date:
        return

    participants = CompetitionParticipants.objects.filter(  # первый запрос к бд
        competition_id=competition_id
    ).select_related('junior_detachment', 'detachment')

    if not participants:
        return

    start_ids = list(participants.filter(detachment__isnull=True)
                     .values_list('junior_detachment__id', flat=True))

    tandem_ids = list(participants.filter(detachment__isnull=False)
                      .values_list('junior_detachment__id', 'detachment__id'))

    reports_start = model_report.objects.filter(  # второй запрос к бд
        competition_id=competition_id,
        detachment_id__in=start_ids
    )

    sorted_by_score_start_reports = sorted(
        reports_start, key=lambda x: x.score, reverse=reverse
    )

    to_create_entries = []
    for index, report in enumerate(sorted_by_score_start_reports):
        to_create_entries.append(
            model_ranking(competition=report.competition,
                          detachment=report.detachment,
                          place=index + 1)
        )

    model_ranking.objects.filter(competition_id=competition_id).delete()  # третий запрос к бд
    model_ranking.objects.bulk_create(to_create_entries)  # четвертый запрос к бд

    reports = model_report.objects.filter(  # пятый запрос к бд
        competition_id=competition_id
    ).select_related('detachment').all()

    tandem_reports = [
        [reports.filter(detachment_id=id).first() for id in ids]
        for ids in tandem_ids
    ]

    sorted_by_score_tandem_reports = sorted(
        tandem_reports,
        key=lambda x: ((x[0].score + x[1].score) if (x[0] and x[1])
                       else (x[0].score if x[0] is not None
                             else (x[1].score if x[1] is not None
                                   else (0 if reverse else len(tandem_ids))))),
        reverse=reverse
    )

    logger.info(f'Отчеты: {sorted_by_score_tandem_reports}')

    to_create_entries = []
    for index, report in enumerate(sorted_by_score_tandem_reports):
        if report[0] is None and report[1] is None:
            continue

        if report[0] is not None and report[1] is not None:
            to_create_entries.append(
                model_tandem_ranking(competition=report[0].competition,
                                     junior_detachment=report[0].detachment,
                                     detachment=report[1].detachment,
                                     place=index + 1)
            )

        elif report[0] is not None:
            detachment = participants.get(
                junior_detachment=report[0].detachment,
            ).detachment
            to_create_entries.append(
                model_tandem_ranking(competition=report[0].competition,
                                     junior_detachment=report[0].detachment,
                                     detachment=detachment,
                                     place=index + 1)
            )

        elif report[1] is not None:
            junior_detachment = participants.get(
                detachment=report[1].detachment,
            ).junior_detachment
            to_create_entries.append(
                model_tandem_ranking(competition=report[1].competition,
                                     junior_detachment=junior_detachment,
                                     detachment=report[1].detachment,
                                     place=index + 1)
            )
    model_tandem_ranking.objects.filter(competition_id=competition_id).delete()  # шестой запрос к бд
    model_tandem_ranking.objects.bulk_create(to_create_entries)  # седьмой запрос к бд


def calculate_q1_score(competition_id):
    """
    Функция для расчета очков по 1 показателю.

    Выполняется только 15.04.2024.
    """
    today = date.today()
    start_date = date(2024, 4, 15)

    if today != start_date:
        return

    participants = CompetitionParticipants.objects.filter(
        competition_id=competition_id
    ).all()  # мб добавить select_related('junior_detachment__members', 'detachment__members')

    if not participants:
        logger.info('Нет участников')
        return

    detachments_data = []

    # Собираем список списков, где
    #       первый элемент - id отряда-участника,
    #       второй - количество участников в отряде,
    #       третий - количество участников с оплаченным членским взносом
    # Добавляем везде единичку, т.к. командира нет в members
    for entry in participants:
        detachments_data.append([
            entry.junior_detachment_id,
            entry.junior_detachment.members.count() + 1,
            entry.junior_detachment.members.filter(
                user__membership_fee=True
            ).count() + 1 if entry.junior_detachment.commander.membership_fee else 0
        ])
        if entry.detachment:
            detachments_data.append([
                entry.detachment_id,
                entry.detachment.members.count() + 1,
                entry.detachment.members.filter(
                    user__membership_fee=True
                ).count() + 1 if entry.detachment.commander.membership_fee else 0
            ])

    # Создаем отчеты каждому отряду с посчитанными score
    #       10 человек в отряде  – за каждого уплатившего 1 балл
    #       11-20 человек – за каждого уплатившего 0.75 балла
    #       21 и более человек – за каждого уплатившего 0.5 балла

    to_create_entries = []

    # score по дефолту 1, иначе в таске как False проходит, не считается
    for data in detachments_data:
        score = 1  # TODO: Если в отряде меньше 10 человек - то score = 1 УТОЧНИТЬ
        if data[1] == 10:
            score = data[2] * 1 + 1
        elif data[1] > 10 and data[1] <= 20:
            score = data[2] * 0.75 + 1
        elif data[1] > 20:
            score = data[2] * 0.5 + 1
        to_create_entries.append(
            Q1Report(competition_id=competition_id,
                     detachment_id=data[0],
                     score=score)
        )

    Q1Report.objects.filter(competition_id=competition_id).delete()
    Q1Report.objects.bulk_create(to_create_entries)


def calculate_q19_place(report: Q19Report) -> int:
    if report.safety_violations == 'Имеются':
        return 2
    return 1
