from datetime import date
import logging
from competitions.models import Q13EventOrganization, Q18Ranking, \
    Q18DetachmentReport, CompetitionParticipants, Q18TandemRanking, Q7Ranking, Q7Report, Q7TandemRanking


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
        Q18TandemRanking.objects.all().delete()
    else:
        Q18Ranking.objects.all().delete()

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
                Q18TandemRanking.objects.create(
                    detachment=participants_entry.detachment,
                    junior_detachment=entry.detachment,
                    place=current_place
                )
        else:
            Q18Ranking.objects.create(
                place=current_place,
                detachment=entry.detachment
            )

def calculate_place(
        competition_id, model_report, model_ranking, model_tandem_ranking,
        reverse=True
):
    """
    Таска для расчета рейтинга Q7.

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

    logger.info(f'Расчет рейтинга Q7. competition_id: {competition_id}')

    if today >= cutoff_date:  # если уже прошло 15 октября
        return

    participants = CompetitionParticipants.objects.filter(
        competition_id=competition_id
    ).all()

    if not participants:
        logger.info('Нет участников')
        return

    logger.info(f'Участники: {participants}')
    tandem_ids: list[tuple[int, int]] = []  # список пар id отрядов(junior_detachment и detachment)
    start_ids: list[int] = []

    logger.info(f'Все участники: {participants}')
    for entry in participants:  # сортируем отряды по типу заявки
        if entry.detachment is None:
            start_ids.append(entry.junior_detachment.id) # сохраняем их айдишники в список
        else:
            tandem_ids.append((entry.junior_detachment.id, entry.detachment.id))
    logger.info(f'ID отчетов старт: {start_ids}')

    logger.info(f'ID отчетов тандем: {tandem_ids}')
    reports_start = model_report.objects.filter(  # получаем отчеты по типу заявки
        competition_id=competition_id,
        detachment_id__in=start_ids
    )
    logger.info(f'Отчеты старт получили: {reports_start}')

    sorted_by_score_start_reports = sorted(  # сортируем отчеты старт по очкам
        reports_start, key=lambda x: x.score, reverse=True
    )

    logger.info('Отчеты старт отсортированы')

    model_ranking.objects.filter(competition_id=competition_id).delete()  # удаляем старые данные
    to_create_entries = []
    for index, report in enumerate(sorted_by_score_start_reports):
        to_create_entries.append(
            model_ranking(competition=report.competition,
                          detachment=report.detachment,
                          place=index + 1)
        )

    model_ranking.objects.bulk_create(to_create_entries)  # создаем новый рейтинг старт

    logger.info("Старт рейтинг создан")

    # Начинаем считать тандем
    tandem_reports = []

    for ids in tandem_ids:  # получаем отчеты тандем попарно объектами
        tandem = []   # Если один или оба еще не подали отчет, тут будет (None, None)
        for id in ids:
            tandem.append(model_report.objects.filter(
                competition_id=competition_id,
                detachment_id=id
            ).first())

        tandem_reports.append(tandem)
    logger.info("Тандем заявка начало")

    # сортируем отчеты тандем по очкам если они есть
    # если их нет хоть у одного - сортируем только по партнеру
    # если их нет ни у одного - они будут в конце списка
    sorted_by_score_tandem_reports = sorted(
        tandem_reports,
        key=lambda x: ((x[0].score + x[1].score) if (x[0] and x[1])
                       else (x[0].score if x[0] is not None
                             else (x[1].score if x[1] is not None
                                   else (0 if reverse else len(tandem_ids))))),  # Вес ноль когда чем больше-тем лучше и вес максимальный когда чем меньше-тем лучше
        reverse=reverse
    )
    logger.info(f"Тандем заявка сортировка окончена {sorted_by_score_tandem_reports}")

    model_tandem_ranking.objects.filter(competition_id=competition_id).delete()
    to_create_entries = []
    for index, report in enumerate(sorted_by_score_tandem_reports):
        if report[0] is None and report[1] is None:
            continue
            # не попадают в рейтинг.
            # при формировании итогового нужно взять последнее место + 1

        if report[0] is not None and report[1] is not None:
            to_create_entries.append(
                model_tandem_ranking(competition=report[0].competition,
                                     junior_detachment=report[0].detachment,
                                     detachment=report[1].detachment,
                                     place=index + 1)
            )
            logger.info(f"Тандем заявка конец {index, report[0], report[1]}")

        elif report[0] is not None:  # если junior_detachment не None
            detachment = CompetitionParticipants.objects.get(
                junior_detachment=report[0].detachment,
                competition=report[0].competition
            ).detachment
            logger.info(f"Тандем заявка конец {index, report[0], report[1]}")
            to_create_entries.append(
                model_tandem_ranking(competition=report[0].competition,
                                     junior_detachment=report[0].detachment,
                                     detachment=detachment,
                                     place=index + 1)
            )

        elif report[1] is not None:  # если detachment не None
            junior_detachment = CompetitionParticipants.objects.get(
                detachment=report[1].detachment,
                competition=report[1].competition
            ).junior_detachment
            logger.info("Тандем заявка конец")
            to_create_entries.append(
                model_tandem_ranking(competition=report[1].competition,
                                     junior_detachment=junior_detachment,
                                     detachment=report[1].detachment,
                                     place=index + 1)
            )

    model_tandem_ranking.objects.bulk_create(to_create_entries)  # создаем новый рейтинг тандем

    logger.info("Тандем рейтинг создан")
