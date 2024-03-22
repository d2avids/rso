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
    Таска для расчета рейтинга Q7 - Q12.

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
    model_tandem_ranking.objects.filter(competition_id=competition_id).delete()
    model_tandem_ranking.objects.bulk_create(to_create_entries)

    logger.info("Тандем рейтинг создан")


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
    ).all()  # добавить select_related('junior_detachment__members', 'detachment__members')

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


def calculate_q19_place(competition_id):
    today = date.today()
    cutoff_date = date(2024, 10, 15)

    if today >= cutoff_date:  # если уже прошло 15 октября
        return

    participants = CompetitionParticipants.objects.filter(
        competition_id=competition_id
    ).all()

    if not participants:
        logger.info('Нет участников')
        return

    tandem_ids: list[tuple[int, int]] = []
    start_ids: list[int] = []

    for entry in participants:
        if entry.detachment is None:
            start_ids.append(entry.junior_detachment.id)
        else:
            tandem_ids.append(
                (entry.junior_detachment.id, entry.detachment.id)
            )

    to_create_entries = []

    for tandem in tandem_ids:
        report_main = Q19Report.objects.filter(
            competition_id=competition_id,
            detachment_id=tandem[0]
        ).first()
        report_junior = Q19Report.objects.filter(
            competition_id=competition_id,
            detachment_id=tandem[1]
        ).first()
        # если у обоих есть отчеты и нет нарушений
        if (
            report_main and report_junior and
            report_main.is_verified and report_junior.is_verified and
            report_main.safety_violations == Q19Report.SafetyViolationsChoices.NONE.value and
            report_junior.safety_violations == Q19Report.SafetyViolationsChoices.NONE.value
        ):
            to_create_entries.append(
                Q19TandemRanking(
                    competition_id=competition_id,
                    junior_detachment_id=tandem[0],
                    detachment_id=tandem[1],
                    place=1
                )
            )
        # если у обоих есть нет отчетов
        elif report_main is None and report_junior is None:
            to_create_entries.append(
                Q19TandemRanking(
                    competition_id=competition_id,
                    junior_detachment_id=tandem[0],
                    detachment_id=tandem[1],
                    place=3
                )
            )
        # во всех остальных случаях - 2 место
        else:
            to_create_entries.append(
                Q19TandemRanking(
                    competition_id=competition_id,
                    junior_detachment_id=tandem[0],
                    detachment_id=tandem[1],
                    place=2
                )
            )

    Q19TandemRanking.objects.filter(competition_id=competition_id).delete()
    Q19TandemRanking.objects.bulk_create(to_create_entries)

    to_create_entries_start = []
    for start_id in start_ids:
        report = Q19Report.objects.filter(
            competition_id=competition_id,
            detachment_id=start_id
        ).first()
        # если есть отчет и нет нарушений
        if (
            report and report.is_verified and
            report.safety_violations == Q19Report.SafetyViolationsChoices.NONE.value
        ):
            to_create_entries_start.append(
                Q19Ranking(
                    competition_id=competition_id,
                    detachment_id=start_id,
                    place=1
                )
            )
        # если есть отчет, он верифицирован, но есть нарушения
        elif (
            report and report.is_verified and
            report.safety_violations != Q19Report.SafetyViolationsChoices.NONE.value
        ):
            to_create_entries_start.append(
                Q19Ranking.objects.create(
                    competition_id=competition_id,
                    detachment_id=start_id,
                    place=2
                )
            )
        else:
            to_create_entries_start.append(
                Q19Ranking.objects.create(
                    competition_id=competition_id,
                    detachment_id=start_id,
                    place=3
                )
            )

    Q19Ranking.objects.filter(competition_id=competition_id).delete()
    Q19Ranking.objects.bulk_create(to_create_entries_start)
